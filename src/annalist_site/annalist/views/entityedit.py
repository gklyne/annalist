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

from annalist                           import message
from annalist                           import util

from annalist.models.recordtype         import RecordType
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitydata         import EntityData

from annalist.views.uri_builder         import uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.generic             import AnnalistGenericView

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='title',            e=None,                  f=None               )
        , SimpleValueMap(c='coll_id',          e=None,                  f=None               )
        , SimpleValueMap(c='type_id',          e=None,                  f=None               )
        , StableValueMap(c='entity_id',        e='annal:id',            f='entity_id'        )
        , SimpleValueMap(c='entity_uri',       e='annal:uri',           f='entity_uri'       )
        , SimpleValueMap(c='record_type',      e='annal:record_type',   f='record_type'      )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='view_id',          e=None,                  f='view_id'          )
        , SimpleValueMap(c='orig_id',          e=None,                  f='orig_id'          )
        , SimpleValueMap(c='orig_type',        e=None,                  f='orig_type'        )
        , SimpleValueMap(c='action',           e=None,                  f='action'           )
        , SimpleValueMap(c='continuation_uri', e=None,                  f='continuation_uri' )
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
        log.log(settings.TRACE_FIELD_VALUE,
            "views.entityedit.get %s"%(self.get_request_path())
            )
        log.log(settings.TRACE_FIELD_VALUE,
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response

        # Create local entity object or load values from existing
        # entity_initial_values = (
        #     { "rdfs:label":   "Entity '%s' of type '%s' in collection '%s'"%
        #                       (viewinfo.entity_id, type_id, coll_id)
        #     , "rdfs:comment": ""
        #     })
        typeinfo              = viewinfo.entitytypeinfo
        entity_initial_values = typeinfo.get_initial_entity_values(viewinfo.entity_id)
        entity = self.get_entity(viewinfo.entity_id, typeinfo, action, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%{'id': entity_initial_values['rdfs:label']}
                    )
                )
        # @@TODO: build context_extra_values here and pass into form_render.
        #         eventually, form_render will ideally be used for both GET and POST 
        #         handlers that respond with a rendered form.
        add_field        = request.GET.get('add_field', None)
        continuation_uri = request.GET.get('continuation_uri', "")
        return self.form_render(viewinfo, entity, add_field, continuation_uri)

    # POST

    def post(self, request,
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Handle response from generic entity editing form.
        """
        log.debug("views.entityedit.post %s"%(self.get_request_path()))
        log.debug(
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        # log.debug("  form data %r"%(request.POST))
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response
        # Get key form data values
        # Except for entity_id, use values from URI when form does not supply a value
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type          = request.POST.get('entity_type', type_id)
        orig_entity_type     = request.POST.get('orig_type', type_id)
        continuation_uri     = (request.POST.get('continuation_uri', None) or
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        view_id              = request.POST.get('view_id', view_id)
        action               = request.POST.get('action', action)
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        # log.info("continuation_uri %s, type_id %s"%(continuation_uri, type_id))
        typeinfo        = viewinfo.entitytypeinfo
        # @@TODO: handle enumeration of values more generically in fields/render_utils.
        type_ids        = [ t.get_id() for t in viewinfo.collection.types() ]
        context_extra_values = (
            { 'title':            viewinfo.sitedata["title"]
            , 'action':           action
            , 'continuation_uri': continuation_uri
            , 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'type_ids':         type_ids
            , 'orig_id':          orig_entity_id
            , 'orig_type':        orig_entity_type
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
        if not typeinfo.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(viewinfo.collection, typeinfo.entityparent.get_id(), {})
        return self.form_response(
            viewinfo,
            entity_id, orig_entity_id, 
            entity_type, orig_entity_type,
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
        viewinfo.check_authorization(action)
        return viewinfo

    def get_view_entityvaluemap(self, viewinfo):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated view.
        """
        # Locate and read view description
        entitymap = EntityValueMap(baseentityvaluemap)
        log.debug("entityview %r"%viewinfo.recordview.get_values())
        fieldlistmap = FieldListValueMap(
            viewinfo.collection, 
            viewinfo.recordview.get_values()['annal:view_fields']
            )
        entitymap.add_map_entry(fieldlistmap)
        return entitymap

    def get_entity(self, entity_id, typeinfo, action, entity_initial_values):
        """
        Create local entity object or load values from existing.

        entity_id       entity id to create or load
        typeinfo        EntityTypeInfo object for the entity
        action          is the requested action: new, edit, copy
        entity_initial_values
                        is a dictionary of initial values used when 
                        a new entity is created

        returns an object of the appropriate type.

        If an existing entity is accessed, values are read from storage, 
        otherwise a new entity object is created but not yet saved.
        """
        entityclass = typeinfo.entityclass
        log.debug(
            "get_entity id %s, parent %s, action %s, altparent %s"%
            (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
            )
        entity = None
        if action == "new":
            entity = entityclass(typeinfo.entityparent, entity_id)
            entity.set_values(entity_initial_values)
        elif entityclass.exists(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent):
            entity = entityclass.load(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent)
        if entity is None:
            parent_id = typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent else "(none)"
            log.debug(
                "Entity not found: parent %s, entity_id %s"%(parent_id, entity_id)
                )
        return entity

    def form_render(self, viewinfo, entity, add_field, continuation_uri):
        """
        Returns an HTTP response that renders a view of an entity, 
        using supplied entity data
        """
        assert entity, "No entity value provided"
        coll_id   = viewinfo.coll_id
        type_id   = viewinfo.type_id
        entity_id = entity.get_id()
        type_ids  = [ t.get_id() for t in viewinfo.collection.types() ]
        # Set up initial view context
        entityvaluemap = self.get_view_entityvaluemap(viewinfo)
        if add_field:
            add_field_desc = self.find_repeat_id(entityvaluemap, add_field)
            if add_field_desc:
                self.add_entity_field(add_field_desc, entity)
        viewcontext    = entityvaluemap.map_value_to_context(entity,
            title               = viewinfo.sitedata["title"],
            continuation_uri    = continuation_uri,
            action              = viewinfo.action,
            coll_id             = coll_id,
            type_id             = type_id,
            type_ids            = type_ids,
            orig_id             = entity_id,
            orig_type           = type_id,
            view_id             = viewinfo.view_id
            )
        # Generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def form_re_render(self, 
            entityvaluemap, form_data, context_extra_values={}, 
            error_head=None, error_message=None):
        """
        Returns re-rendering of form with current values and error message displayed.
        """
        form_context = entityvaluemap.map_form_data_to_context(form_data,
            **context_extra_values
            )
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
                entity_type, orig_entity_type, 
                messages, context_extra_values
            ):
        """
        Handle POST response from entity edit form.
        """
        form_data        = self.request.POST    
        continuation_uri = context_extra_values['continuation_uri']
        if 'cancel' in form_data:
            return HttpResponseRedirect(continuation_uri)
        typeinfo       = viewinfo.entitytypeinfo
        entityvaluemap = self.get_view_entityvaluemap(viewinfo)

        # Check response has valid id and type
        if not util.valid_id(entity_id):
            log.debug("form_response: entity_id not util.valid_id('%s')"%entity_id)
            return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        if not util.valid_id(entity_type):
            log.debug("form_response: entity_type not util.valid_id('%s')"%entity_type)
            return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                error_head=messages['entity_type_heading'],
                error_message=messages['entity_type_invalid']
                )

        # Save updated details
        if 'save' in form_data:
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type, orig_entity_id, orig_entity_type, 
                viewinfo.collection, typeinfo, context_extra_values, messages)
            return http_response or HttpResponseRedirect(continuation_uri)

        # Add field from entity view (as opposed to view description view)
        if 'add_view_field' in form_data:
            http_response = self.save_entity(entityvaluemap, form_data,
                entity_id, entity_type, orig_entity_id, orig_entity_type, 
                viewinfo.collection, typeinfo, context_extra_values, messages)
            if http_response:
                return http_response
            viewinfo.check_authorization("config")
            if viewinfo.http_response:
                return viewinfo.http_response
            (continuation_next, continuation_here) = self.continuation_uris(form_data, continuation_uri)
            view_edit_uri_base = self.view_uri("AnnalistEntityEditView",
                coll_id=viewinfo.coll_id,
                view_id="View_view",
                type_id="_view",
                entity_id=viewinfo.view_id,
                action="edit"
                )
            view_edit_uri = uri_with_params(view_edit_uri_base, {"add_field": "View_fields"}, continuation_here)
            return HttpResponseRedirect(view_edit_uri)

        # Add new instance of repeating field
        add_field = self.find_add_field(entityvaluemap, form_data)
        if add_field:
            entityvals = entityvaluemap.map_form_data_to_values(form_data)
            return self.update_view_fields(add_field, entityvals, entityvaluemap, **context_extra_values)

        # Remove Field(s)
        remove_field = self.find_remove_field(entityvaluemap, form_data)
        if remove_field:
            if not remove_field['remove_fields']:
                log.debug("form_response: No field(s) selected for remove_field")
                return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                    error_head=messages['remove_field_error'],
                    error_message=messages['no_field_selected']
                    )
            entityvals = entityvaluemap.map_form_data_to_values(form_data)
            return self.update_view_fields(remove_field, entityvals, entityvaluemap, **context_extra_values)

        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(form_data), 
            message.SYSTEM_ERROR
            )
        log.warning("Unexpected form data %s"%(err_values))
        log.warning("Continue to %s"%(continuation_uri))
        redirect_uri = view_edit_uri(continuation_uri, err_values)
        return HttpResponseRedirect(redirect_uri)

    def save_entity(self,
            entityvaluemap, form_data,
            entity_id, entity_type, orig_entity_id, orig_entity_type, 
            collection, typeinfo, context_extra_values, messages):
        """
        This method contains logic to save entity data modified through a form
        intrerface.  If an entity is being edited (as oppoosed to created or copied)
        and the entity id or type have been changed, then new entity data is written 
        and the original entity data is removed.

        Returns None if the save completes successfully, otherwise an 
        HTTP response object that reports the nature of the problem.
        """
        action      = form_data['action']
        orig_entity = self.get_entity(orig_entity_id, typeinfo, action, {})
        log.debug(
            "save_entity: save, action %s, entity_id %s, orig_entity_id %s"
            %(action, entity_id, orig_entity_id)
            )
        log.debug(
            "                     entity_type %s, orig_entity_type %s"
            %(entity_type, orig_entity_type)
            )
        entity_id_changed = (
            ( action == "edit" ) and
            ( (entity_id != orig_entity_id) or (entity_type != orig_entity_type) )
            )
        # Check original parent exists (still)
        orig_parent = typeinfo.entityparent
        if not orig_parent._exists():
            log.warning("save_entity: not orig_parent._exists()")
            return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )
        # Determine new parent for saved entity
        if entity_type != orig_entity_type:
            new_parent = RecordTypeData(collection, entity_type)
            if not new_parent._exists():
                # Create RecordTypeData if not already existing
                RecordTypeData.create(collection, entity_type, {})
        else:
            new_parent = orig_parent
        # Check existence of entity to save according to action performed
        if (action in ["new", "copy"]) or entity_id_changed:
            if typeinfo.entityclass.exists(new_parent, entity_id):
                return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_exists']
                    )
        else:
            if not typeinfo.entityclass.exists(orig_parent, entity_id, altparent=typeinfo.entityaltparent):
                # This shouldn't happen, but just in case...
                log.warning("Expected %s/%s not found; action %s, entity_id_changed %r"%
                      (entity_type, entity_id, action, entity_id_changed)
                    )
                return self.form_re_render(entityvaluemap, form_data, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_not_exists']
                    )
        # Create/update data now
        # Note: form data is applied as update to original entity data so that
        # values not in view are preserved.
        entity_values = orig_entity.get_values() if orig_entity else {}
        entity_values.pop('annal:uri', None)  # Force re-allocation of URI
        entity_values.update(entityvaluemap.map_form_data_to_values(form_data))
        typeinfo.entityclass.create(new_parent, entity_id, entity_values)
        # Remove old entity if rename
        if entity_id_changed:
            if typeinfo.entityclass.exists(new_parent, entity_id):    # Precautionary
                typeinfo.entityclass.remove(orig_parent, orig_entity_id)
        return None

    def find_repeat_fields(self, entityvaluemap):
        """
        Iterate over repeat field groups in the current view.

        Each value found is returned as a field structure description; e.g.

            { 'field_type': 'RepeatValuesMap'
            , 'repeat_entity_values': u 'annal:view_fields'
            , 'repeat_id': u 'View_fields'
            , 'repeat_btn_label': u 'field'
            , 'repeat_label': u 'Fields'
            , 'repeat_context_values': u 'repeat'
            , 'repeat_fields_description':
            , { 'field_type': 'FieldListValueMap'
              , 'field_list':
                [ { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
                  , 'field_id': u 'Field_sel'
                  }
                , { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
                  , 'field_id': u 'Field_placement'
                  }
                ]
              }
            }
        """
        def _find_repeat_fields(fieldmap):
            for kmap in fieldmap:
                field_desc = kmap.get_structure_description()
                if field_desc['field_type'] == "FieldListValueMap":
                    for fd in _find_repeat_fields(kmap.fs):
                        yield fd
                if field_desc['field_type'] == "RepeatValuesMap":
                    yield field_desc
        return _find_repeat_fields(entityvaluemap)

    def find_add_field(self, entityvaluemap, form_data):
        """
        Locate add field option in form data and,if present, return a description of the field to
        be added.
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_add_field: %r"%repeat_desc)
            if repeat_desc['repeat_id']+"__add" in form_data:
                return repeat_desc
        return None

    def find_remove_field(self, entityvaluemap, form_data):
        """
        Locate remove field option in form data and, if present, return a description of the field to
        be removed, with the list of member indexes to be removed added as element 'remove_fields'.
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_remove_field: %r"%repeat_desc)
            if repeat_desc['repeat_id']+"__remove" in form_data:
                remove_fields_key = repeat_desc['repeat_id']+"__select_fields"
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
            if repeat_desc['repeat_id'] == repeat_id:
                return repeat_desc
        return None

    def update_view_fields(self, field_desc, entityvals, entityvaluemap, **context_extra_values):
        """
        Renders a new form from supplied entity instance data with a repeateds field or 
        field group added or removed.

        The change is not saved to permanent storage, and is used to render a form display.
        The new field is saved by invoking 'save' from the displayed form (i.e. a corresponding 
        HTTP POST).

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
        return (
            self.render_html(form_context, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def add_entity_field(self, add_field_desc, entity):
        field_val = dict(
            [ (f['field_property_uri'], "")
              for f in add_field_desc['repeat_fields_description']['field_list']
            ])
        entity[add_field_desc['repeat_entity_values']].append(field_val)
        return

    def remove_entity_field(self, remove_field_desc, entity):
        repeatvals_key = remove_field_desc['repeat_entity_values']
        old_repeatvals = entity[repeatvals_key]
        new_repeatvals = []
        for i in range(len(old_repeatvals)):
            if str(i) not in remove_field_desc['remove_fields']:
                new_repeatvals.append(old_repeatvals[i])
        entity[repeatvals_key] = new_repeatvals
        return

# End.
