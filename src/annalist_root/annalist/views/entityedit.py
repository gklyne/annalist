"""
Generic entity edit view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import logging
log = logging.getLogger(__name__)

from itertools import izip_longest

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

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='coll_id',          e=None,                    f=None               )
        , SimpleValueMap(c='type_id',          e=None,                    f=None               )
        , SimpleValueMap(c='view_choices',     e=None,                    f=None               )
        , SimpleValueMap(c='edit_view_button', e=None,                    f=None               )
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

    The view to be displayed can be specified through the constructor
    (for predefined views) or through the HTTP request URI parameters
    (for any view).
    """

    _entityedittemplate = 'annalist_entity_edit.html'
    _entityviewtemplate = 'annalist_entity_view.html'

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
        self.get_view_template(action, type_id, entity_id)
        action   = action or "view"
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
        log.info("  form data %r"%(request.POST))
        self.get_view_template(action, type_id, entity_id)
        action_uri = action
        action     = request.POST.get('action', action)
        viewinfo   = self.view_setup(action, coll_id, type_id, view_id, entity_id)
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
            , 'edit_view_button': viewinfo.recordview.get(ANNAL.CURIE.open_view, "yes")
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

    def get_view_template(self, action, type_id, entity_id):
        """
        Returns name of template to use for the current view.

        The `action` parameter must be that provided via the URI used to invoke the view,
        and not taken from a submitted form.  This ensures that the template used is
        consistently based on the URI used, and not subject to any vagaries of submiteted
        form data.
        """
        # @@TODO: clean up this code to use URI values saved in viewinfo rather than `self`
        if action in ["new", "copy", "edit"]:
            self.formtemplate = self._entityedittemplate
            self.uri_action  = "edit"
        else:
            self.formtemplate = self._entityviewtemplate
            self.uri_action  = "view"
        self.uri_type_id   = type_id
        self.uri_entity_id = entity_id
        return self.formtemplate

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
        entityvals = { field_description.get_field_property_uri(): viewinfo.view_id }
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
        # log.info(
        #     "get_entity id %s, parent %s, action %s, altparent %s"%
        #     (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
        #     )
        entity = typeinfo.get_entity_with_aliases(entity_id, action)
        if entity is None:
            parent_id    = typeinfo.entityparent.get_id()
            altparent_id = typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent else "(none)"
            log.debug(
                "Entity not found: parent %s, altparent %s, entity_id %s"%
                (parent_id, altparent_id, entity_id)
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
            { 'edit_view_button':   viewinfo.recordview.get(ANNAL.CURIE.open_view, "yes")
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
            self.render_html(viewcontext, self.formtemplate) or 
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
            self.render_html(form_context, self.formtemplate) or 
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
        if ('cancel' in form_data) or ('close' in form_data):
            return HttpResponseRedirect(continuation_url)

        typeinfo       = viewinfo.entitytypeinfo
        orig_entity    = self.get_entity(orig_entity_id, typeinfo, viewinfo.action)
        # log.info("orig_entity %r"%(orig_entity.get_values(),))
        entityvaluemap = self.get_view_entityvaluemap(viewinfo, orig_entity)

        # # Check response has valid id and type
        # if not util.valid_id(entity_id):
        #     log.debug("form_response: entity_id not util.valid_id('%s')"%entity_id)
        #     return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
        #         error_head=messages['entity_heading'],
        #         error_message=messages['entity_invalid_id']
        #         )
        # if not util.valid_id(entity_type_id):
        #     log.debug("form_response: entity_type_id not util.valid_id('%s')"%entity_type_id)
        #     return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
        #         error_head=messages['entity_type_heading'],
        #         error_message=messages['entity_type_invalid']
        #         )

        # Save updated details
        if 'save' in form_data:
            # log.info(
            #     "save: entity_id %s, orig_entity_id %s, type_id %s, orig_type_id %s"%
            #     (entity_id, orig_entity_id, entity_type_id, orig_entity_type_id)
            #     )
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type_id,
                orig_entity_id, orig_entity_type_id,
                viewinfo, context_extra_values, messages)
            return http_response or HttpResponseRedirect(continuation_url)

        # Update or define new view or type (invoked from generic entity editing view)
        # Save current entity and redirect to view edit with new field added, and
        # current page as continuation.
        if 'use_view' in form_data:
            # Save entity, then redirect to selected view
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id,
                viewinfo, context_extra_values, messages)
            if http_response:
                return http_response
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entity_type_id
                , 'view_id':    form_data['view_choice']
                , 'entity_id':  entity_id
                , 'action':     self.uri_action
                })
            redirect_uri = (
                uri_with_params(
                    self.view_uri("AnnalistEntityEditView", **view_uri_params),
                    { 'continuation_url': continuation_url }
                    )
                )
            return HttpResponseRedirect(redirect_uri)

        # If "Edit" or "Copy" button invoked, initiate new view of current entity
        edit_action = (
            "edit" if 'edit' in form_data else
            "copy" if 'copy' in form_data else None
            )
        if edit_action is not None:
            view_edit_uri_base = self.view_uri("AnnalistEntityEditView",
                coll_id=viewinfo.coll_id,
                type_id=self.uri_type_id,       # entity_type_id,
                view_id=viewinfo.view_id,
                entity_id=self.uri_entity_id,   # entity_id,
                action=edit_action
                )
            return self.save_invoke_edit_entity(
                entityvaluemap, form_data,
                self.uri_entity_id, self.uri_type_id,   # from URI, not form data
                # entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id, # orig_entity,
                viewinfo, context_extra_values, messages,
                view_edit_uri_base, edit_action,
                {}, continuation_url
                )

        # New entity buttons
        #
        # These may use explicit button ids per the table below, or may be part of
        # an enumered-value field used to create a new enumerated value instance.
        #
        # In all cases, the current entity is saved and the browser is redirected 
        # to a new page to enter details of a new entity of the appropriate type.
        #
        new_button_map = (
            { 'new_type':  
                { 'type_id':  "_type"
                , 'view_id':  "Type_view"
                }
            , 'new_view':
                { 'type_id':  "_view"
                , 'view_id':  "View_view"
                }
            , 'new_field':
                { 'type_id':  "_field"
                , 'view_id':  "Field_view"
                }
            , 'new_group':
                { 'type_id':  "_group"
                , 'view_id':  "Field_group_view"
                }
            })
        new_type_id = None
        for button_id in new_button_map.keys():
            if button_id in form_data:
                new_type_id = new_button_map[button_id]['type_id']
                new_view_id = new_button_map[button_id]['view_id']
                break

        new_enum = self.find_new_enum(entityvaluemap, form_data)
        if new_enum:
            new_type_id  = new_enum['field_options_typeref']
            new_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, new_type_id
                )
            new_view_id  = new_typeinfo.get_default_view_id()

        if new_type_id is not None:
            new_edit_uri_base = self.view_uri("AnnalistEntityNewView",
                coll_id=viewinfo.coll_id, 
                view_id=new_view_id, type_id=new_type_id, 
                action="new"
                )
            return self.save_invoke_edit_entity(
                entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id, # orig_entity,
                viewinfo, context_extra_values, messages,
                new_edit_uri_base, "new",
                {}, continuation_url
                )

        # Add field from entity view (as opposed to view description view)
        # See below call of 'find_add_field' for adding field in view description
        # @@TODO: remove references to add_view_field option; 
        #         lose parameter to save_invoke_edit_entity (?)
        if ('add_view_field' in form_data) or ('open_view' in form_data) :
            view_edit_uri_base = self.view_uri("AnnalistEntityEditView",
                coll_id=viewinfo.coll_id,
                view_id="View_view",
                type_id="_view",
                entity_id=viewinfo.view_id,
                action=self.uri_action
                )
            add_field_param = (
                {"add_field": "View_fields"} if ('add_view_field' in form_data) else {}
                )
            log.info("Open view: continuation_url: %s"%continuation_url)
            log.info("Open view: entity_id: %s"%entity_id)
            return self.save_invoke_edit_entity(
                entityvaluemap, form_data,
                entity_id, entity_type_id, 
                orig_entity_id, orig_entity_type_id, # orig_entity,
                viewinfo, context_extra_values, messages,
                view_edit_uri_base, "config",
                add_field_param, continuation_url
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
            orig_entity_id, orig_entity_type_id, 
            viewinfo, context_extra_values, messages):
        """
        This method contains logic to save entity data modified through a form
        interface.  If an entity is being edited (as opposed to created or copied)
        and the entity id or type have been changed, then new entity data is written 
        and the original entity data is removed.  If an entity was being viewed,
        no data is saved.

        Returns None if the save completes successfully, otherwise an 
        HTTP response object that reports the nature of the problem.
        """
        # log.info(
        #     "save_entity: save, action %s, entity_id %s, orig_entity_id %s, entity_type_id %s, orig_entity_type_id %s"
        #     %(form_data['action'], entity_id, orig_entity_id, entity_type_id, orig_entity_type_id)
        #     )
        action   = form_data['action']
        typeinfo = viewinfo.entitytypeinfo
        if self.uri_action == "view":
            # This is view operation: nothing to save
            return None
        if not action in ["new", "copy", "edit"]:
            log.warning("'Save' operation for action '%s'"%(action))
            # Check "edit" authorization to continue
            if viewinfo.check_authorization("edit"):
                return viewinfo.http_response
        entity_renamed = (
            ( action == "edit" ) and
            ( (entity_id != orig_entity_id) or (entity_type_id != orig_entity_type_id) )
            )

        # Check for valid id and type to be saved
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

        # Check for valid entity nid and type id
        # @@TODO: factor out repeated re-rendering logic
        if not util.valid_id(entity_id):
            log.warning("save_entity: invalid entity_id (%s)"%(entity_id))
            return self.form_re_render(
                viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=message.ENTITY_DATA_ID,
                error_message=message.ENTITY_DATA_ID_INVALID
                )
        if not util.valid_id(entity_type_id):
            log.warning("save_entity: invalid entity_type_id (%s)"%(entity_type_id))
            return self.form_re_render(
                viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=message.ENTITY_TYPE_ID,
                error_message=message.ENTITY_TYPE_ID_INVALID
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
        if (action in ["new", "copy"]) or entity_renamed:
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
                log.warning("Expected %s/%s not found; action %s, entity_renamed %r"%
                      (entity_type_id, entity_id, action, entity_renamed)
                    )
                return self.form_re_render(viewinfo, entityvaluemap, form_data, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_not_exists']
                    )

        # Assemble updated values for storage
        #
        # Note: form data is applied as update to original entity data so that
        # values not in view are preserved.  Use original entity values without 
        # field aliases as basis for new value.
        orig_entity   = typeinfo.get_entity(entity_id, action)
        orig_values   = orig_entity.get_values() if orig_entity else {}
        entity_values = orig_values.copy()
        # log.info("orig entity_values %r"%(entity_values,))
        if action == "copy":
            entity_values.pop(ANNAL.CURIE.uri, None)      # Force new URI on copy
        entity_values.update(entityvaluemap.map_form_data_to_values(form_data))
        entity_values[ANNAL.CURIE.type_id] = entity_type_id
        entity_values[ANNAL.CURIE.type]    = new_typeinfo.entityclass._entitytype
        # log.info("save entity_values%r"%(entity_values))

        # Create/update stored data now
        if not entity_renamed:
            # Normal (non-type) entity create or update, no renaming
            err_vals = self.create_update_entity(new_typeinfo, entity_id, entity_values)
        elif "_type" not in [entity_type_id, orig_entity_type_id]:
            # Non-type record rename
            err_vals = self.rename_entity(
                typeinfo, orig_entity_id, new_typeinfo, entity_id, entity_values
                )
        else:
            err_vals = self.rename_entity_type(
                viewinfo, 
                typeinfo, orig_entity_id, 
                new_typeinfo, entity_id, entity_values
                )
        if err_vals:
            return self.form_re_render(
                viewinfo, entityvaluemap, form_data, context_extra_values,
                error_head=err_vals[0],
                error_message=err_vals[1]
                )

        return None

    def rename_entity_type(self,
            viewinfo,
            old_typeinfo, old_type_id, 
            new_typeinfo, new_type_id, type_data
            ):
        """
        Save a renamed type entity.

        This involves renaming all of the instances of the type to
        the new type (with new type id and in new location).

        Returns None if the operation succeeds, or error message
        details to be displayed as a pair of values for the message 
        heading and the message body.
        """
        # NOTE: old RecordData instance is not removed.

        # Don't allow type-rename to or from a type value
        if old_typeinfo.type_id != new_typeinfo.type_id:
            log.warning(
                "EntityEdit.rename_entity_type: attempt to change type of type record"
                )
            return (message.INVALID_OPERATION_ATTEMPTED, message.INVALID_TYPE_CHANGE)
        # Don't allow renaming built-in type
        builtin_types = get_built_in_type_ids()
        if (new_type_id in builtin_types) or (old_type_id in builtin_types):
            log.warning(
                "EntityEdit.rename_entity_type: attempt to rename or define a built-in type"
                )
            return (message.INVALID_OPERATION_ATTEMPTED, message.INVALID_TYPE_RENAME)

        # Create new type record
        new_typeinfo.create_entity(new_type_id, type_data)

        # Update instances of type
        src_typeinfo = EntityTypeInfo(
            viewinfo.site, viewinfo.collection, old_type_id
            )
        dst_typeinfo = EntityTypeInfo(
            viewinfo.site, viewinfo.collection, new_type_id, 
            create_typedata=True
            )
        if new_typeinfo.entity_exists(new_type_id):
            # Enumerate type instance records and move to new type
            remove_OK = True
            for d in src_typeinfo.enum_entities():
                data_id   = d.get_id()
                data_vals = d.get_values()
                data_vals[ANNAL.CURIE.type_id] = new_type_id
                data_vals[ANNAL.CURIE.type]    = dst_typeinfo.entityclass._entitytype
                if self.rename_entity(
                    src_typeinfo, data_id, 
                    dst_typeinfo, data_id, data_vals
                    ):
                    remove_OK = False
            # Finally, remove old type record:
            if remove_OK:       # Precautionary
                new_typeinfo.remove_entity(old_type_id)
                RecordTypeData.remove(new_typeinfo.entitycoll, old_type_id)
        else:
            log.warning(
                "Failed to rename type %s to type %s"%
                (old_type_id, new_type_id)
                )
            return (
                message.SYSTEM_ERROR, 
                message.RENAME_TYPE_FAILED%(old_type_id, new_type_id)
                )
        return None

    def rename_entity(self,
            old_typeinfo, old_entity_id, 
            new_typeinfo, new_entity_id, entity_values
            ):
        """
        Save a renamed entity.

        Renaming may involve changing the type (hence location) of the entity,
        and/or the entity_id

        The new entity is saved and checked before the original entity is deleted.

        Returns None if the operation succeeds, or error message
        details to be displayed as a pair of values for the message 
        heading and the message body.
        """
        new_typeinfo.create_entity(new_entity_id, entity_values)
        if new_typeinfo.entity_exists(new_entity_id):    # Precautionary
            old_typeinfo.remove_entity(old_entity_id)
        else:
            log.warning(
                "EntityEdit.rename_entity: Failed to rename entity %s/%s to %s/%s"%
                    (old_typeinfo.type_id, old_entity_id, 
                     new_typeinfo.type_id, new_entity_id)
                )
            return (
                message.SYSTEM_ERROR, 
                message.RENAME_ENTITY_FAILED%
                    (old_typeinfo.type_id, old_entity_id, 
                     new_typeinfo.type_id, new_entity_id)
                )
        return None

    def create_update_entity(self, typeinfo, entity_id, entity_values):
        """
        Create or update an entity.

        Returns None if the operation succeeds, or error message
        details to be displayed as a pair of values for the message 
        heading and the message body.
        """
        typeinfo.create_entity(entity_id, entity_values)
        if not typeinfo.entity_exists(entity_id):
            log.warning(
                "EntityEdit.create_update_entity: Failed to create/update entity %s/%s"%
                    (typeinfo.type_id, entity_id)
                )
            return (
                message.SYSTEM_ERROR, 
                message.CREATE_ENTITY_FAILED%
                    (typeinfo.type_id, entity_id)
                )
        return None

    def save_invoke_edit_entity(self, 
            entityvaluemap, form_data,
            entity_id, entity_type_id, 
            orig_entity_id, orig_entity_type_id, # orig_entity,
            viewinfo, context_extra_values, messages,
            config_edit_url, config_edit_perm,
            url_params, continuation_url):
        """
        Common logic for invoking a resource edit while editing
        some other resource:
          - the entity currently being edited is saved
          - authorization to perform the requested edit is checked
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
            orig_entity_id, orig_entity_type_id,
            viewinfo, context_extra_values, messages)
        return (
            http_response or
            self.invoke_edit_entity(
                viewinfo, config_edit_perm,
                config_edit_url, url_params, 
                entity_id or orig_entity_id, entity_type_id, 
                form_data, continuation_url
                )
            )

        #@@
        # # @@TODO: get permission required from typeinfo of entity to be created
        # if viewinfo.check_authorization(config_edit_perm):
        #     return viewinfo.http_response
        # (continuation_next, continuation_here) = self.continuation_urls(
        #     form_data, continuation_url, 
        #     base_here=viewinfo.get_save_continuation_url(entity_type_id, entity_id, self.uri_action)
        #     # base_here=viewinfo.get_edit_continuation_url(entity_type_id, entity_id)
        #     )
        # return HttpResponseRedirect(
        #     uri_with_params(config_edit_url, url_params, continuation_here)
        #     )
        #@@

    def invoke_edit_entity(self, 
            viewinfo, edit_perm,
            edit_url, url_params, 
            entity_id, entity_type_id, 
            param_data, continuation_url
            ):
        """
        Common logic for invoking a resource edit while editing
        or viewing some other resource:
          - authorization to perform the requested edit is checked
          - a continuaton URL is calculated which is the URL for the current view,
            except that the continuation action is always "edit"
          - a URL for the config edit view is assembled from the supplied base URL
            and parameters, and the calculated continuaton URL
          - an HTTP redirect response to the config edit view is returned.

        If there is a problem with any ofthese steps, an error response is returned
        and displayed in the current view.

        viewinfo            current view information.
        edit_perm           action for which permission is required to invoke the indicated
                            edit (e.g. "new", "edit" or "config").
        edit_url            base URL for edit view to be invoked.
        url_params          additional parameters to be added to the edit view base url.
        entity_id           entity_id of entity currently presented.
        entity_type_id      type_id of entity currently being presented.
        param_data          dictionary with additional parameters of the current view (e.g. search).
        continuation_url    continuation URL from the current view.
        """
        if viewinfo.check_authorization(edit_perm):
            return viewinfo.http_response
        log.info("invoke_edit_entity: entity_id %s"%entity_id)
        (continuation_next, continuation_here) = self.continuation_urls(
            request_dict=param_data,
            default_cont=continuation_url, 
            base_here=viewinfo.get_save_continuation_url(
                entity_type_id, entity_id, self.uri_action
                )
            )
        return HttpResponseRedirect(
            uri_with_params(edit_url, url_params, continuation_here)
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
        Locate remove field option in form data and, if present, return a description of 
        the field to be removed, with the list of member indexes to be removed added as 
        element 'remove_fields'.
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

    def find_new_enum(self, entityvaluemap, form_data):
        """
        Locate add enumerated value option in form data and, if present, return a 
        description of the enumerated field for which a new value is to be created.

        Field 'field_options_typeref' of the returned value is the type_id of the 
        enumerated value type.
        """
        def is_new_f(fd):
            # Using FieldDescription method directly doesn't work
            return fd.has_new_button()
        for enum_desc in self.find_fields(entityvaluemap, is_new_f):
            enum_new = self.form_data_contains(form_data, enum_desc, "new")
            if enum_new:
                return enum_desc
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
            self.render_html(form_context, self.formtemplate) or 
            self.error(self.error406values())
            )

    def find_repeat_fields(self, entityvaluemap):
        """
        Iterate over repeat field groups in the current view.

        Each value found is returned as a field description dictionary 
        (cf. FieldDescription).
        """
        def is_repeat_f(fd):
            return fd.is_repeat_group()
        return self.find_fields(entityvaluemap, is_repeat_f)

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

    def find_fields(self, entityvaluemap, filter_f):
        """
        Iterate over fields that satisfy the supplied predicate

        entityvaluemap  is the list of entity-value map entries for the current view
        filter_f        is a predicate that is applied to field description values, 
                        and returns True for those that are to be returned.

        returns a generator of FieldDescription values from the supplied entity 
        value map that satisfy the supplied predicate.
        """
        # Recursive helper function walks through list of field descriptions, 
        # including those that are nested in field group descriptions.
        def _find_fields(fieldmap, group_list):
            if fieldmap is None:
                log.warning("entityedit.find_fields: fieldmap is None")
                return
            # Always called with list of field descriptions
            for field_desc in fieldmap:
                log.debug("find_fields: field_desc %r"%(field_desc))
                if filter_f(field_desc):
                    field_desc['group_list'] = group_list
                    log.info(
                        "entityedit.find_fields: field name %s, prefixes %r"%
                        (field_desc.get_field_name(), group_list)
                        )
                    yield field_desc
                if field_desc.has_field_group_ref():
                    groupref = field_desc.group_ref()
                    if not util.valid_id(groupref):
                        # this is for resilience in the face of bad data
                        log.warning(
                            "entityedit.find_fields: invalid group_ref %s in field description for %s"%
                            (groupref, field_desc['field_id'])
                            )
                    else:
                        log.info(
                            "entityedit.find_fields: Group field desc %s: %s"%
                            (groupref, field_desc['field_id'])
                            )
                        group_fields   = field_desc['group_field_descs']
                        new_group_list = group_list + [field_desc['group_id']]
                        for fd in _find_fields(group_fields, new_group_list):
                            yield fd
            return
        # Entry point: locate list of fields and return generator
        for evmapitem in entityvaluemap:
            # Data entry fields are always presented within a top-level FieldListValueMap
            # cf. self.get_view_entityvaluemap.
            itemdesc = evmapitem.get_structure_description()
            if itemdesc['field_type'] == "FieldListValueMap":
                return _find_fields(itemdesc['field_list'], [])
        return

    def form_data_contains(self, form_data, field_desc, postfix):
        """
        Tests to see if the form data contains a result field corresponding to 
        the supplied field descriptor (as returned by 'find_fields') with a 
        postfix value as supplied.

        Returns the full name of the field found, or None.
        """
        log.info("form_data_contains: field_desc %r"%field_desc)
        field_name         = field_desc.get_field_name()
        field_name_postfix = "new"
        def _scan_groups(prefix, group_list):
            """
            return (stop, result)
            where:
              'stop'   is True if there are no more possible results to try.
              'result' is the final result to return if `more` is false.
            """
            stop_all   = True
            if group_list == []:
                try_field = prefix + field_name
                log.info("form_data_contains: try_field %s"%try_field)
                if try_field in form_data:
                    try_postfix = try_field + "__" + field_name_postfix
                    return (try_postfix in form_data, try_postfix)
            else:
                group_head = group_list[0]
                group_tail = group_list[1:]
                index      = 0
                while True:
                    next_prefix = "%s%s__%d__"%(prefix, group_head, index)
                    (stop, result) = _scan_groups(next_prefix, group_tail)
                    if stop:
                        if result:
                            return (True, result)
                        else:
                            break
                    stop_all = False
                    index   += 1
            return (stop_all, None)
        matched, result = _scan_groups("", field_desc["group_list"])
        return result if matched else None

# End.
