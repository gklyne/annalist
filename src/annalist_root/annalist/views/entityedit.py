"""
Generic entity edit view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist.identifiers               import RDFS, ANNAL
from annalist                           import message
from annalist                           import util

from annalist.models.entitytypeinfo     import EntityTypeInfo, get_built_in_type_ids
from annalist.models.recordtype         import RecordType
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitydata         import EntityData

from annalist.views.uri_builder         import uri_base, uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field
from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap

from annalist.views.fields.bound_field  import bound_field, get_entity_values

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# View mapping table structure
#
# EntityValueMap                          GenericEntityEditView.get_view_entityvaluemap
#   FieldListValueMap                     
#       FieldDescription*                 FieldListValueMap.__init__
#       FieldValueMap*
#       FieldValueMap* or
#       (RepeatValuesMap + FieldListValueMap)*
#
# FieldDescription references renderer
#
# FieldValueMap.map_entity_to_context returns bound_field object
#
# FieldValueMap.map_form_to_entity uses FieldDescription['field_value_mapper'].decode(formval)
#
# GenericEntityEditView.get_view_entityvaluemap is called from form_render and form_response)
#

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='coll_id',          e=None,                    f=None               )
        , SimpleValueMap(c='type_id',          e=None,                    f=None               )
        , SimpleValueMap(c='view_choices',     e=None,                    f=None               )
        , SimpleValueMap(c='edit_add_field',   e=None,                    f=None               )
        , StableValueMap(c='entity_id',        e=ANNAL.CURIE.id,          f='entity_id'        )
        , SimpleValueMap(c='entity_url',       e=ANNAL.CURIE.url,         f='entity_url'       )
        , SimpleValueMap(c='entity_uri',       e=ANNAL.CURIE.uri,         f='entity_uri'       )
        , SimpleValueMap(c='record_type',      e=ANNAL.CURIE.record_type, f='record_type'      )
        , SimpleValueMap(c='view_id',          e=None,                    f='view_id'          )
        , SimpleValueMap(c='orig_id',          e=None,                    f='orig_id'          )
        , SimpleValueMap(c='orig_type',        e=None,                    f='orig_type'        )
        , SimpleValueMap(c='action',           e=None,                    f='action'           )
        , SimpleValueMap(c='continuation_url', e=None,                    f='continuation_url' )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        ])

#   -------------------------------------------------------------------------------------------
#
#   Entity edit view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class GenericEntityEditView(AnnalistGenericView):
    """
    View class for generic entity edit view

    The view to be displayted can be specified through the constructor
    (for predefined views) or through the HTTP request URTI parameters
    (for any view).
    """

    _entityformtemplate = 'annalist_entity_edit.html'

    def __init__(self):
        super(GenericEntityEditView, self).__init__()
        return

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.info(
            "views.entityedit.get:  coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        # log.log(settings.TRACE_FIELD_VALUE,
        #     "views.entityedit.get %s"%(self.get_request_path())
        #     )
        # log.log(settings.TRACE_FIELD_VALUE,
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        action   = action or "edit"     # Default action (@@TODO: 'view' when read-only views defined)
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response

        # Create local entity object or load values from existing
        typeinfo = viewinfo.entitytypeinfo
        entity   = self.get_entity(viewinfo.entity_id, typeinfo, action)
        if entity is None:
            entity_label = (message.ENTITY_MESSAGE_LABEL%
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    viewinfo.type_id
                , 'entity_id':  viewinfo.entity_id
                })
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%{'id': entity_label}
                    )
                )
        # @@TODO: build context_extra_values here and pass into form_render.
        #         eventually, form_render will ideally be used for both GET and POST 
        #         handlers that respond with a rendered form.
        add_field        = request.GET.get('add_field', None)
        continuation_url = request.GET.get('continuation_url', "")
        return self.form_render(viewinfo, entity, add_field, continuation_url)

    # POST

    def post(self, request,
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Handle response from generic entity editing form.
        """
        log.info(
            "views.entityedit.post: coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        log.log(settings.TRACE_FIELD_VALUE,
            "views.entityedit.post %s"%(self.get_request_path())
            )
        log.log(settings.TRACE_FIELD_VALUE,
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        log.debug("  form data %r"%(request.POST))
        action               = request.POST.get('action', action)
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response
        # Get key form data values
        # Except for entity_id, use values from URI when form does not supply a value
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type_id       = request.POST.get('entity_type', type_id)
        orig_entity_type_id  = request.POST.get('orig_type', type_id)
        continuation_url     = (request.POST.get('continuation_url', None) or
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        view_id              = request.POST.get('view_id', view_id)
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        # log.info("continuation_url %s, type_id %s"%(continuation_url, type_id))
        typeinfo        = viewinfo.entitytypeinfo
        context_extra_values = (
            { 'site_title':       viewinfo.sitedata["title"]
            , 'title':            viewinfo.collection[RDFS.CURIE.label]
            , 'action':           action
            , 'edit_add_field':   viewinfo.recordview.get(ANNAL.CURIE.add_field, "yes")
            , 'continuation_url': continuation_url
            , 'request_url':      self.get_request_path()
            , 'coll_id':          coll_id
            , 'coll_label':       viewinfo.collection[RDFS.CURIE.label]
            , 'type_id':          type_id
            , 'view_choices':     self.get_view_choices_field(viewinfo)
            , 'orig_id':          orig_entity_id
            , 'orig_type':        orig_entity_type_id
            , 'view_id':          view_id
            })
        message_vals = {'id': entity_id, 'type_id': type_id, 'coll_id': coll_id}
        messages = (
            { 'parent_heading':         typeinfo.entitymessages['parent_heading']%message_vals
            , 'parent_missing':         typeinfo.entitymessages['parent_missing']%message_vals
            , 'entity_heading':         typeinfo.entitymessages['entity_heading']%message_vals
            , 'entity_invalid_id':      typeinfo.entitymessages['entity_invalid_id']%message_vals
            , 'entity_exists':          typeinfo.entitymessages['entity_exists']%message_vals
            , 'entity_not_exists':      typeinfo.entitymessages['entity_not_exists']%message_vals
            , 'entity_type_heading':    typeinfo.entitymessages['entity_type_heading']%message_vals
            , 'entity_type_invalid':    typeinfo.entitymessages['entity_type_invalid']%message_vals
            , 'remove_field_error':     message.REMOVE_FIELD_ERROR
            , 'no_field_selected':      message.NO_FIELD_SELECTED
            })
        # Process form response and respond accordingly
        #@@ TODO: this should be redundant - create as-needed, not before
        #         as of 2014-11-07, removing this causes test failures
        if not typeinfo.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(viewinfo.collection, typeinfo.entityparent.get_id(), {})
        #@@
        return self.form_response(
            viewinfo,
            entity_id, orig_entity_id, 
            entity_type_id, orig_entity_type_id,
            messages, context_extra_values
            )

    # Helper functions

    def view_setup(self, action, coll_id, type_id, view_id, entity_id):
        """
        Assemble display information for entity view request handler
        """
        viewinfo = DisplayInfo(self, action)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.get_view_info(viewinfo.get_view_id(type_id, view_id))
        viewinfo.get_entity_info(action, entity_id)
        # viewinfo.get_entity_data()
        viewinfo.check_authorization(action)
        return viewinfo

    def get_view_entityvaluemap(self, viewinfo, entity_values):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated view.

        The 3rd parameter to `FieldListValueMap` is used for EntityFinder
        invocations used to populate enumerated field options.
        """
        # Locate and read view description
        entitymap = EntityValueMap(baseentityvaluemap)
        log.debug("entityview: %r"%viewinfo.recordview.get_values())
        fieldlistmap = FieldListValueMap('fields',
            viewinfo.collection, 
            viewinfo.recordview.get_values()[ANNAL.CURIE.view_fields],
            {'view': viewinfo.recordview, 'entity': entity_values}
            )
        entitymap.add_map_entry(fieldlistmap)
        return entitymap

    def get_view_choices_field(self, viewinfo):
        """
        Returns a bound_field object that displays as a view-choice selection drop-down.
        """
        # @@TODO: Possibly create FieldValueMap and return map_entity_to_context value? 
        #         or extract this logic and share?
        field_description = field_description_from_view_field(
            viewinfo.collection, 
            { ANNAL.CURIE.field_id: "View_choice" }, 
            None
            )
        entityvals        = { field_description['field_property_uri']: viewinfo.view_id }
        return bound_field(field_description, entityvals)

    def get_entity(self, entity_id, typeinfo, action):
        """
        Create local entity object or load values from existing.

        entity_id       entity id to create or load
        typeinfo        EntityTypeInfo object for the entity
        action          is the requested action: new, edit, copy

        returns an object of the appropriate type.

        If an existing entity is accessed, values are read from storage, 
        otherwise a new entity object is created but not yet saved.
        """
        entityclass = typeinfo.entityclass
        # log.info(
        #     "get_entity id %s, parent %s, action %s, altparent %s"%
        #     (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
        #     )
        entity = None
        if util.valid_id(entity_id):
            if action == "new":
                entity = entityclass(typeinfo.entityparent, entity_id)
                entity_initial_values = typeinfo.get_initial_entity_values(entity_id)
                entity.set_values(entity_initial_values)
            elif entityclass.exists(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent):
                entity = entityclass.load(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent)
        if entity is None:
            parent_id = typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent else "(none)"
            log.debug(
                "Entity not found: parent %s, entity_id %s"%(parent_id, entity_id)
                )
        return entity

    def form_render(self, viewinfo, entity, add_field, continuation_url):
        """
        Returns an HTTP response that renders a view of an entity, 
        using supplied entity data
        """
        assert entity, "No entity value provided"
        coll_id   = viewinfo.coll_id
        type_id   = viewinfo.type_id
        entity_id = entity.get_id()
        coll      = viewinfo.collection
        # Set up initial view context
        # @@TODO: entity needed here?
        entityvaluemap = self.get_view_entityvaluemap(viewinfo, entity)
        if add_field:
            add_field_desc = self.find_repeat_id(entityvaluemap, add_field)
            if add_field_desc:
                # Add empty fields per named repeat group
                self.add_entity_field(add_field_desc, entity)
        entityvals  = get_entity_values(viewinfo, entity, entity_id)
        if viewinfo.action == "copy":
            entityvals.pop(ANNAL.CURIE.uri, None)
        context_extra_values = (
            { 'edit_add_field':     viewinfo.recordview.get(ANNAL.CURIE.add_field, "yes")
            , 'continuation_url':   continuation_url
            , 'request_url':        self.get_request_path()
            , 'coll_id':            coll_id
            , 'type_id':            type_id
            , 'view_choices':       self.get_view_choices_field(viewinfo)
            , 'orig_id':            entity_id
            , 'orig_type':          type_id
            , 'view_id':            viewinfo.view_id
            })
        viewcontext = entityvaluemap.map_value_to_context(entityvals, 
            **context_extra_values
            )
        # log.info("form_render: viewcontext %r"%(viewcontext,)) #@@
        viewcontext.update(viewinfo.context_data())
        # Generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def form_re_render(self, 
            viewinfo, entityvaluemap, form_data, context_extra_values={}, 
            error_head=None, error_message=None):
        """
        Returns re-rendering of form with current values and error message displayed.
        """
        # log.info("********\nform_data %r"%form_data)
        form_context = entityvaluemap.map_form_data_to_context(form_data,
            **context_extra_values
            )
        form_context.update(viewinfo.context_data())
        # log.info("********\nform_context %r"%form_context)
        form_context['error_head']    = error_head
        form_context['error_message'] = error_message
        return (
            self.render_html(form_context, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # @@TODO: refactor form_response to separate methods for each action
    #         form_response should handle initial checking and dispatching.
    def form_response(self, viewinfo,
                entity_id, orig_entity_id, 
                entity_type_id, orig_entity_type_id, 
                messages, context_extra_values
            ):
        """
        Handle POST response from entity edit form.
        """
        log.info("form_response entity_id %s, orig_entity_id %s, entity_type_id %s, orig_entity_type_id %s"%
            (entity_id, orig_entity_id, entity_type_id, orig_entity_type_id)
            )
        form_data        = self.request.POST    
        continuation_url = context_extra_values['continuation_url']
        if 'cancel' in form_data:
            return HttpResponseRedirect(continuation_url)

        typeinfo       = viewinfo.entitytypeinfo
        orig_entity    = self.get_entity(orig_entity_id, typeinfo, viewinfo.action)
        # log.info("orig_entity %r"%(orig_entity.get_values(),))
        entityvaluemap = self.get_view_entityvaluemap(viewinfo, orig_entity)

        # Check response has valid id and type
        if not util.valid_id(entity_id):
            log.debug("form_response: entity_id not util.valid_id('%s')"%entity_id)
            return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        if not util.valid_id(entity_type_id):
            log.debug("form_response: entity_type_id not util.valid_id('%s')"%entity_type_id)
            return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=messages['entity_type_heading'],
                error_message=messages['entity_type_invalid']
                )

        # Save updated details
        if 'save' in form_data:
            # log.info(
            #     "save: entity_id %s, orig_entity_id %s, type_id %s, orig_type_id %s"%
            #     (entity_id, orig_entity_id, entity_type_id, orig_entity_type_id)
            #     )
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type_id,
                orig_entity_id, orig_entity_type_id, orig_entity,
                viewinfo, context_extra_values, messages)
            return http_response or HttpResponseRedirect(continuation_url)

        # Add field from entity view (as opposed to view description view)
        # See below call of 'find_add_field' for adding field in view description
        if 'add_view_field' in form_data:
            view_edit_uri_base = self.view_uri("AnnalistEntityEditView",
                coll_id=viewinfo.coll_id,
                view_id="View_view",
                type_id="_view",
                entity_id=viewinfo.view_id,
                action="edit"
                )
            return self.invoke_config_edit_view(
                entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id,  orig_entity,
                viewinfo, context_extra_values, messages,
                view_edit_uri_base, {"add_field": "View_fields"}, continuation_url
                )

        # Update or define new view or type (invoked from generic entity editing view)
        if 'use_view' in form_data:
            # Save entity, then redirect to selected view
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id, orig_entity,
                viewinfo, context_extra_values, messages)
            if http_response:
                return http_response
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entity_type_id
                , 'view_id':    form_data['view_choice']
                , 'entity_id':  entity_id
                , 'action':     "edit"
                })
            redirect_uri = (
                uri_with_params(
                    self.view_uri("AnnalistEntityEditView", **view_uri_params),
                    { 'continuation_url': continuation_url }
                    )
                )
            return HttpResponseRedirect(redirect_uri)

        if 'new_view' in form_data:
            view_edit_uri_base = self.view_uri("AnnalistEntityNewView",
                coll_id=viewinfo.coll_id, view_id="View_view", type_id="_view", action="new"
                )
            return self.invoke_config_edit_view(
                entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id, orig_entity,
                viewinfo, context_extra_values, messages,
                view_edit_uri_base, {}, continuation_url
                )

        if 'new_field' in form_data:
            view_edit_uri_base = self.view_uri("AnnalistEntityNewView",
                coll_id=viewinfo.coll_id, view_id="Field_view", type_id="_field", action="new"
                )
            return self.invoke_config_edit_view(
                entityvaluemap, form_data,
                entity_id, entity_type_id,
                orig_entity_id, orig_entity_type_id, orig_entity,
                viewinfo, context_extra_values, messages,
                view_edit_uri_base, {}, continuation_url
                )

        if 'new_type' in form_data:
            type_edit_uri_base = self.view_uri("AnnalistEntityNewView",
                coll_id=viewinfo.coll_id, view_id="Type_view", type_id="_type", action="new"
                )
            return self.invoke_config_edit_view(
                entityvaluemap, form_data,
                entity_id, entity_type_id,
                orig_entity_id, orig_entity_type_id, orig_entity,
                viewinfo, context_extra_values, messages,
                type_edit_uri_base, {}, continuation_url
                )

        # Add new instance of repeating field, and redisplay
        add_field = self.find_add_field(entityvaluemap, form_data)
        # log.info("*** Add field: "+repr(add_field))
        if add_field:
            entityvals = entityvaluemap.map_form_data_to_values(form_data)
            return self.update_view_fields(viewinfo, add_field, entityvals, entityvaluemap, **context_extra_values)

        # Remove Field(s), and redisplay
        remove_field = self.find_remove_field(entityvaluemap, form_data)
        if remove_field:
            if not remove_field['remove_fields']:
                log.debug("form_response: No field(s) selected for remove_field")
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=messages['remove_field_error'],
                    error_message=messages['no_field_selected']
                    )
            entityvals = entityvaluemap.map_form_data_to_values(form_data)
            return self.update_view_fields(viewinfo, remove_field, entityvals, entityvaluemap, **context_extra_values)

        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(form_data), 
            message.SYSTEM_ERROR
            )
        log.warning("Unexpected form data %s"%(err_values))
        log.warning("Continue to %s"%(continuation_url))
        for k, v in form_data.items():
            log.info("  form[%s] = %r"%(k,v))
        redirect_uri = uri_with_params(continuation_url, err_values)
        return HttpResponseRedirect(redirect_uri)

    def save_entity(self,
            entityvaluemap, form_data,
            entity_id, entity_type_id,
            orig_entity_id, orig_entity_type_id, orig_entity,
            viewinfo, context_extra_values, messages):
        """
        This method contains logic to save entity data modified through a form
        intrerface.  If an entity is being edited (as oppoosed to created or copied)
        and the entity id or type have been changed, then new entity data is written 
        and the original entity data is removed.

        Returns None if the save completes successfully, otherwise an 
        HTTP response object that reports the nature of the problem.
        """
        # log.info(
        #     "save_entity: save, action %s, entity_id %s, orig_entity_id %s, entity_type_id %s, orig_entity_type_id %s"
        #     %(form_data['action'], entity_id, orig_entity_id, entity_type_id, orig_entity_type_id)
        #     )
        # log.info(
        #     "           orig_entity %r"
        #     %(orig_entity)
        #     )
        action   = form_data['action']
        typeinfo = viewinfo.entitytypeinfo
        if not action in ["new", "copy", "edit"]:
            log.warning("'Save' operation for action '%s'"%(action))
            # Check "edit" authorization to continue
            if viewinfo.check_authorization("edit"):
                return viewinfo.http_response
        entity_id_changed = (
            ( action == "edit" ) and
            ( (entity_id != orig_entity_id) or (entity_type_id != orig_entity_type_id) )
            )

        # Check original parent exists (still)
        #@@ TODO: unless this is a "new" action?
        if not typeinfo.parent_exists():
            log.warning("save_entity: original entity parent does not exist")
            return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )

        # Determine type information for saved entity
        if entity_type_id != orig_entity_type_id:
            # log.info("new_typeinfo: entity_type_id %s"%(entity_type_id))
            new_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, entity_type_id, 
                create_typedata=True
                )
        else:
            new_typeinfo = typeinfo

        # Check existence of entity to save according to action performed
        if (action in ["new", "copy"]) or entity_id_changed:
            if new_typeinfo.entity_exists(entity_id):
                log.warning(
                    "Entity exists: action %s %s/%s, orig %s/%s"%
                        (action, entity_type_id, entity_id, orig_entity_type_id, orig_entity_id)
                    )
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_exists']
                    )
        else:
            if not typeinfo.entity_exists(entity_id, use_altparent=True):
                # This shouldn't happen, but just in case...
                log.warning("Expected %s/%s not found; action %s, entity_id_changed %r"%
                      (entity_type_id, entity_id, action, entity_id_changed)
                    )
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_not_exists']
                    )

        # Assemble updated values for storage
        # Note: form data is applied as update to original entity data so that
        # values not in view are preserved.
        entity_values  = orig_entity.get_values() if orig_entity else {}
        # log.info("orig entity_values %r"%(entity_values,))
        if action == "copy":
            entity_values.pop(ANNAL.CURIE.uri, None)      # Force new URI on copy
        entity_values.update(entityvaluemap.map_form_data_to_values(form_data))
        entity_values[ANNAL.CURIE.type_id] = entity_type_id
        entity_values[ANNAL.CURIE.type]    = new_typeinfo.entityclass._entitytype
        # log.info("save entity_values%r"%(entity_values))

        # If saving view description, ensure all property URIs are unique
        #
        # @@TODO: this is somehwat ad hoc - is there a better way?
        # The problem this avoids is that multiple fields with the same property URI would 
        # be handled confusingly by the view editing logic.
        if viewinfo.view_id == "View_view":
            properties = set()
            for view_field in entity_values[ANNAL.CURIE.view_fields]:
                field_id = view_field[ANNAL.CURIE.field_id]
                field    = RecordField.load(viewinfo.collection, field_id, altparent=viewinfo.site)
                property_uri = field[ANNAL.CURIE.property_uri]
                if property_uri in properties:
                    return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                        error_head=message.VIEW_DESCRIPTION_HEADING,
                        error_message=message.VIEW_PROPERTY_DUPLICATE%
                          { 'field_id':field_id, 'property_uri': property_uri}
                        )
                properties.add(property_uri)

        # Create/update stored data now
        #
        # @@TODO: refactor the following to
        #     (a) factor out core entity rename logic, 
        #     (b) separate view-level validation and error repporting from action logic

        if not ("_type" in [entity_type_id, orig_entity_type_id] and entity_id_changed):

            # Normal (non-type) record save
            new_typeinfo.create_entity(entity_id, entity_values)
            if entity_id_changed:
                # Rename entity other than a type: remove old entity
                if new_typeinfo.entity_exists(entity_id):    # Precautionary
                    typeinfo.remove_entity(orig_entity_id)
                else:
                    log.warning(
                        "Failed to rename entity %s/%s to %s/%s"%
                        (orig_type_id, orig_entity_id, entity_type_id, entity_id)
                        )

        else:

            # Special case for saving type information with new id (rename type)
            #
            # Need to update RecordTypeData and record data instances
            # Don't allow type-rename to or from a type value
            if entity_type_id != orig_entity_type_id:
                log.warning("save_entity: attempt to change type of type record")
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=message.INVALID_OPERATION_ATTEMPTED,
                    error_message=message.INVALID_TYPE_CHANGE
                    )
            # Don't allow renaming built-in type
            builtin_types = get_built_in_type_ids()
            if (entity_id in builtin_types) or (orig_entity_id in builtin_types):
                log.warning("save_entity: attempt to rename or define a built-in type")
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=message.INVALID_OPERATION_ATTEMPTED,
                    error_message=message.INVALID_TYPE_RENAME
                    )
            # Create new type record
            new_typeinfo.create_entity(entity_id, entity_values)
            # Update instances of type
            src_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, orig_entity_id
                )
            dst_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, entity_id, 
                create_typedata=True
                )
            if new_typeinfo.entity_exists(entity_id):
                # Enumerate type instance records and move to new type
                remove_OK = True
                for d in src_typeinfo.enum_entities():
                    data_id   = d.get_id()
                    data_vals = d.get_values()
                    data_vals[ANNAL.CURIE.type_id] = entity_id
                    data_vals[ANNAL.CURIE.type]    = dst_typeinfo.entityclass._entitytype
                    dst_typeinfo.create_entity(data_id, data_vals)
                    if dst_typeinfo.entity_exists(data_id):     # Precautionary
                        # NOTE: assumes that enum_entities is not affected by removal:
                        src_typeinfo.remove_entity(data_id)
                    else:
                        log.warning(
                            "Failed to rename type %s entity %s to type %s"%
                            (orig_entity_id, data_id, entity_id)
                            )
                        remove_OK = False
                # Finally, remove old type record:
                if remove_OK:       # Precautionary
                    typeinfo.remove_entity(orig_entity_id)
                    RecordTypeData.remove(typeinfo.entitycoll, orig_entity_id)
            else:
                log.warning(
                    "Failed to rename type %s to type %s"%
                    (orig_entity_id, entity_id)
                    )

        return None

    # def store_entity_type_uri(self, entity_values, entity_typeinfo):
    #     """
    #     Sort out entity URI and entity type URI(s), in preparation to save.

    #     The '@type' and 'annal:URI' fields in the supplied entity_values are updated

    #     entity_values   an entity values dictionary whose '@type' and 'annal:uri' 
    #                     fields may be updated.
    #     entity_typeinfo an EntityTypeInfo object describing the type with which the
    #                     entity is to be saved.
    #     """
    #     if entity_typeinfo.recordtype:
    #         typeuris = []
    #         if ANNAL.CURIE.uri in entity_typeinfo.recordtype:
    #             typeuris = [entity_typeinfo.recordtype[ANNAL.CURIE.uri]]
    #         else:
    #             typeuris = []
    #         entity_values['@type'] = typeuris   # NOTE: previous types not carried forward
    #     if ( (ANNAL.CURIE.uri in entity_values) and 
    #          (entity_values[ANNAL.CURIE.uri] == entity_values.get(ANNAL.CURIE.url, None) ) ):
    #         del entity_values[ANNAL.CURIE.uri]  # Don't save URI if same as URL
    #     return entity_values

    def invoke_config_edit_view(self, 
            entityvaluemap, form_data,
            entity_id, entity_type_id, 
            orig_entity_id, orig_entity_type_id, orig_entity,
            viewinfo, context_extra_values, messages,
            config_edit_url, url_params, continuation_url):
        """
        Common logic for invoking a configuration resource edit while editing
        some other resource:
          - the entity currently being edited is saved
          - authorization to perform configuration edits is checked
          - a continuaton URL is calculated which is the URL for the current view,
            except that the continuation action is always "edit"
          - a URL for the config edit view is assembled from the supplied base URL
            and parameters, and the calculated continuaton URL
          - an HTTP redirect response to the config edit view is returned.

        If there is a problem with any ofthese steps, an error response is returned
        and displayed in the current view.
        """
        http_response = self.save_entity(entityvaluemap, form_data,
            entity_id, entity_type_id, 
            orig_entity_id, orig_entity_type_id, orig_entity,
            viewinfo, context_extra_values, messages)
        if http_response:
            return http_response
        if viewinfo.check_authorization("config"):
            return viewinfo.http_response
        (continuation_next, continuation_here) = self.continuation_urls(
            form_data, continuation_url, 
            base_here=viewinfo.get_edit_continuation_url(entity_type_id, entity_id)
            )
        return HttpResponseRedirect(
            uri_with_params(config_edit_url, url_params, continuation_here)
            )

    def find_add_field(self, entityvaluemap, form_data):
        """
        Locate any add field option in form data and, if present, return a description of 
        the field to be added.
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_add_field: %r"%repeat_desc)
            # log.info("find_add_field - trying %s"%(repeat_desc['group_id']+"__add"))
            if repeat_desc['group_id']+"__add" in form_data:
                return repeat_desc
        return None

    def find_remove_field(self, entityvaluemap, form_data):
        """
        Locate remove field option in form data and, if present, return a description of the field to
        be removed, with the list of member indexes to be removed added as element 'remove_fields'.
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_remove_field: %r"%repeat_desc)
            if repeat_desc['group_id']+"__remove" in form_data:
                remove_fields_key = repeat_desc['group_id']+"__select_fields"
                if remove_fields_key in form_data:
                    repeat_desc['remove_fields'] = form_data[remove_fields_key]
                else:
                    repeat_desc['remove_fields'] = []
                return repeat_desc
        return None

    def find_repeat_id(self, entityvaluemap, repeat_id):
        """
        Locate a repeated field description by repeat_id.

        Returns the field description (see `find_repeat_fields` above), or None
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_add_field: %r"%repeat_desc)
            if repeat_desc['group_id'] == repeat_id:
                return repeat_desc
        return None

    def update_view_fields(self, viewinfo, field_desc, entityvals, entityvaluemap, **context_extra_values):
        """
        Renders a new form from supplied entity instance data with a repeated field or 
        field group added or removed.

        The change is not saved to permanent storage, and is used to render a form display.
        The new field is saved by invoking 'save' from the displayed form (i.e. a corresponding 
        HTTP POST).

        viewinfo    DisplayInfo object describing the current view.
        field_desc  is a field description for a field or field group to be added
                    or removed.  Fields are removed if the description contains a
                    'remove_fields' field, which contains a list of the repeat index
                    values to be removed, otherwise a field is added.
        entityvals  is a dictionary of entity values to which the field is added.
        entityvaluemap
                    an EntityValueMap object for the entity being presented.
        context_extra_values
                    is a dictionary of default and additional values not provided by the
                    entity itself, that may be needed to render the updated form. 

        returns an HttpResponse object to rendering the updated entity editing form,
        or to indicate an reason for failure.
        """
        # log.info("field_desc: %r: %r"%(field_desc,))
        if 'remove_fields' in field_desc:
            self.remove_entity_field(field_desc, entityvals)
        else:
            self.add_entity_field(field_desc, entityvals)
        # log.info("entityvals: %r"%(entityvals,))
        form_context = entityvaluemap.map_value_to_context(entityvals, **context_extra_values)
        form_context.update(viewinfo.context_data())
        return (
            self.render_html(form_context, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def find_repeat_fields(self, entityvaluemap):
        """
        Iterate over repeat field groups in the current view.

        Each value found is returned as a field description dictionary (cf. FieldDescription).
        """
        def _find_repeat_fields(fieldmap):
            if fieldmap is None:
                log.warning("entityedit.find_repeat_fields: fieldmap is None")
                return
            # Always called with list of field descriptions
            for field_desc in fieldmap:
                log.debug("find_repeat_fields: field_desc %r"%(field_desc))
                groupref    = field_desc.group_ref()
                if groupref is not None:
                    if not util.valid_id(groupref):
                        # this is for resilience in the face of bad data
                        log.warning(
                            "invalid group_ref %s in field description for %s"%
                            (groupref, field_desc['field_id'])
                            )
                    log.info("find_repeat_fields: groupref %s"%(groupref))
                    if field_desc.is_repeat_group():
                        yield field_desc
                    for fd in _find_repeat_fields(field_desc['group_field_descs']):
                        # log.info("find_repeat_field FieldListValueMap yield %r"%(fd))
                        yield fd
            return
        for evmapitem in entityvaluemap:
            # log.info("find_repeat_fields evmapitem %r"%(evmapitem,))
            itemdesc = evmapitem.get_structure_description()
            # log.info("**** find_repeat_fields itemdesc %r"%(itemdesc,))
            if itemdesc['field_type'] == "FieldListValueMap":
                return _find_repeat_fields(itemdesc['field_list'])
        return None

    def add_entity_field(self, add_field_desc, entity):
        """
        Add a described repeat field group to the supplied entity values.

        See 'find_repeat_fields' for information about the field description.
        """
        # log.info("*** add_field_desc %r"%(add_field_desc,))
        # log.info("*** entity %r"%(entity,))
        field_val = dict(
            [ (f['field_property_uri'], None)
              for f in add_field_desc['group_field_descs']
            ])
        entity[add_field_desc['field_property_uri']].append(field_val)
        return

    def remove_entity_field(self, remove_field_desc, entity):
        repeatvals_key = remove_field_desc['field_property_uri']
        old_repeatvals = entity[repeatvals_key]
        new_repeatvals = []
        for i in range(len(old_repeatvals)):
            if str(i) not in remove_field_desc['remove_fields']:
                new_repeatvals.append(old_repeatvals[i])
        entity[repeatvals_key] = new_repeatvals
        return

# End.
