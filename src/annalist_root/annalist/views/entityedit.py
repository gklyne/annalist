"""
Generic entity edit view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist.identifiers               import RDFS, ANNAL
from annalist.exceptions                import Annalist_Error
from annalist                           import message
from annalist.util                      import (
    valid_id, split_type_entity_id, extract_entity_id,
    open_url, copy_resource_to_fileobj
    )

from annalist.models.entitytypeinfo     import EntityTypeInfo, get_built_in_type_ids
from annalist.models.recordtype         import RecordType
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitydata         import EntityData

from annalist.views.uri_builder         import uri_base, uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.responseinfo        import ResponseInfo
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
        action           = action or "view"
        viewinfo         = self.view_setup(
            action, coll_id, type_id, view_id, entity_id, request.GET.dict()
            )
        if viewinfo.http_response:
            return viewinfo.http_response

        # Create local entity object or load values from existing
        typeinfo = viewinfo.entitytypeinfo
        entity   = self.get_entity(viewinfo.entity_id, typeinfo, action)
        # log.debug("GenericEntityEditView.get %r"%(entity,))
        if entity is None:
            entity_label = (message.ENTITY_MESSAGE_LABEL%
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    viewinfo.type_id
                , 'entity_id':  viewinfo.entity_id
                })
            return self.error(
                dict(self.error404values(),
                    message=message.ENTITY_DOES_NOT_EXIST%{'id': entity_label}
                    )
                )
        # @@TODO: build context_extra_values here and pass into form_render.
        #         eventually, form_render will ideally be used for both GET and POST 
        #         handlers that respond with a rendered form.
        add_field = request.GET.get('add_field', None)
        try:
            response = self.form_render(viewinfo, entity, add_field)
        except Exception as e:
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        return response

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
        log.log(settings.TRACE_FIELD_VALUE,
            "  form data %r"%(request.POST)
            )
        if request.FILES:
            for f in request.FILES:
                log.info(
                    "  file upload %s: %s(%d bytes) %s"%
                    (f, request.FILES[f].name, request.FILES[f].size, 
                        request.FILES[f].content_type
                        )
                    )
        self.get_view_template(action, type_id, entity_id)
        action      = request.POST.get('action', action)
        viewinfo    = self.view_setup(
            action, coll_id, type_id, view_id, entity_id, request.POST.dict()
            )
        if viewinfo.http_response:
            return viewinfo.http_response
        # Get key form data values
        # Except for entity_id, use values from URI when form does not supply a value
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type_id       = extract_entity_id(request.POST.get('entity_type', type_id))
        orig_entity_type_id  = request.POST.get('orig_type', type_id)
        view_id              = request.POST.get('view_id', view_id)
        viewinfo.set_type_entity_id(
            orig_type_id=orig_entity_type_id, orig_entity_id=orig_entity_id,
            curr_type_id=entity_type_id, curr_entity_id=entity_id
            )
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        typeinfo        = viewinfo.entitytypeinfo
        context_extra_values = (
            { 'site_title':       viewinfo.sitedata["title"]
            , 'title':            viewinfo.collection[RDFS.CURIE.label]
            , 'action':           action
            , 'edit_view_button': viewinfo.recordview.get(ANNAL.CURIE.open_view, "yes")
            , 'continuation_url': viewinfo.get_continuation_url() or ""
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
            , 'move_field_error':       message.MOVE_FIELD_ERROR
            , 'no_field_selected':      message.NO_FIELD_SELECTED
            })
        viewinfo.set_messages(messages)
        # Process form response and respond accordingly
        #@@ TODO: this should be redundant - create as-needed, not before
        #         as of 2014-11-07, removing this causes test failures
        if not typeinfo.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(viewinfo.collection, typeinfo.entityparent.get_id(), {})
        #@@
        try:
            response = self.form_response(viewinfo, context_extra_values)
        except Exception as e:
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        return response


    # Helper functions

    def view_setup(self, action, coll_id, type_id, view_id, entity_id, request_dict):
        """
        Assemble display information for entity view request handler
        """
        #@@ self.site_view_url        = self.view_uri("AnnalistSiteView")
        self.collection_view_url  = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        self.default_continuation_url = self.view_uri(
            "AnnalistEntityDefaultListType", coll_id=coll_id, type_id=type_id
            )
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
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
        consistently based on the URI used, and not subject to any vagaries of submitted
        form data.
        """
        # @@TODO: clean up this code to save and use values in viewinfo rather than `self`
        #         i.e. 'formtemplate' and 'uri_action'; rename for greater clarity?
        if action in ["new", "copy", "edit"]:
            self.formtemplate = self._entityedittemplate
            self.uri_action   = "edit"
        else:
            self.formtemplate = self._entityviewtemplate
            self.uri_action   = "view"
        self.uri_type_id   = type_id
        self.uri_entity_id = entity_id
        return self.formtemplate

    def get_form_refresh_uri(self, viewinfo, view_id=None, action=None, params=None):
        """
        Return a URI to refresh the current form display, with options to override the
        view identifier and/or action to use.  The defaults just refresh the current
        display, except that a "new" action becomes "edit" on the assumption that
        the new entity is saved before the refresh occurs.

        'params', if supplied, is a dioctionary of additional query parameters to be added
        to the resulting URI.

        If the entity has been renamed on the submitted form, this is taken into account
        when re-displaying.
        """
        view_uri_params = (
            { 'coll_id':    viewinfo.coll_id
            , 'type_id':    viewinfo.curr_type_id
            , 'entity_id':  viewinfo.curr_entity_id or viewinfo.entity_id
            , 'view_id':    view_id or viewinfo.view_id     # form_data['view_choice']
            , 'action':     action  or self.uri_action
            })
        more_uri_params = viewinfo.get_continuation_url_dict()
        if params:
            more_uri_params.update(params)
        refresh_uri = (
            uri_with_params(
                self.view_uri("AnnalistEntityEditView", **view_uri_params),
                more_uri_params
                )
            )
        return refresh_uri

    def form_refresh_on_success(self, viewinfo, responseinfo, params=None):
        """
        Helper function returns HttpResponse value that refreshes the current
        page (via redirect) if the supplied `responseinfo` indicates success, 
        otherwise returns the indicated error response.
        """
        if not responseinfo.has_http_response():
            responseinfo.set_http_response(
                HttpResponseRedirect(self.get_form_refresh_uri(viewinfo, params=params))
                )
        return responseinfo.get_http_response()

    def get_view_entityvaluemap(self, viewinfo, entity_values):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated view.
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

    def get_form_display_context(self, viewinfo, entityvaluemap, entityvals, **context_extra_values):
        """
        Return a form display context with data from the supplied entity values, 
        augmented with inferred values and other context data.
        """
        # log.info("get_form_display_context, entityvals: %r"%(entityvals,))
        entityvals   = viewinfo.entitytypeinfo.get_entity_inferred_values(entityvals)
        form_context = entityvaluemap.map_value_to_context(entityvals, **context_extra_values)
        form_context.update(viewinfo.context_data())
        return form_context

    def merge_entity_form_values(self, orig_entityvals, entityformvals):
        """
        Logic that merges updated values from a form response into a set of 
        stored entity values.

        Values that correspond to an uploaded or imported file are not updated.

        (This is a bit ad hoc, needed to overcome the fact that previously uploaded 
        file information is not part of the form data being merged.)
        """
        # @@TODO: consider more positive method for detecting previous upload; e.g. @type value
        def is_previous_upload(ov, k):
            return (
                (k in ov) and
                isinstance(ov[k], dict) and
                ("resource_name" in ov[k])
                )
        # log.info("merge_entity_form_values orig_entityvals: %r"%(orig_entityvals,))
        # log.info("merge_entity_form_values entityformvals:  %r"%(entityformvals,))
        upd_entityvals = orig_entityvals.copy()
        for k in entityformvals:
            if not is_previous_upload(orig_entityvals, k):
                upd_entityvals[k] = entityformvals[k]
        # log.info("orig entity_values %r"%(entity_values,))
        return upd_entityvals

    def form_render(self, viewinfo, entity, add_field):
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
        try:
            entityvaluemap = self.get_view_entityvaluemap(viewinfo, entity)
        except Annalist_Error as e:
            return viewinfo.report_error(str(e))
        #@@ TODO: remove this?
        #   This logic is currently unused - it was provided for add field button 
        #   on entity edit, now using view/edit view description buttons instead.
        if add_field:
            add_field_desc = self.find_repeat_id(entityvaluemap, add_field)
            if add_field_desc:
                # Add empty fields per named repeat group
                self.add_entity_field(add_field_desc, entity)
        #@@
        entityvals  = get_entity_values(viewinfo.entitytypeinfo, entity, entity_id)
        # log.info("form_render.entityvals %r"%(entityvals,))        
        if viewinfo.action == "copy":
            entityvals.pop(ANNAL.CURIE.uri, None)
        context_extra_values = (
            { 'edit_view_button':   viewinfo.recordview.get(ANNAL.CURIE.open_view, "yes")
            , 'continuation_url':   viewinfo.get_continuation_url() or ""
            , 'request_url':        self.get_request_path()
            , 'coll_id':            coll_id
            , 'type_id':            type_id
            , 'view_choices':       self.get_view_choices_field(viewinfo)
            , 'orig_id':            entity_id
            , 'orig_type':          type_id
            , 'view_id':            viewinfo.view_id
            })
        viewcontext = self.get_form_display_context(
            viewinfo, entityvaluemap, entityvals, **context_extra_values
            )
        # log.info("form_render.viewcontext['fields'] %r"%(viewcontext['fields'],))        
        # Generate and return form data
        return (
            self.render_html(viewcontext, self.formtemplate) or 
            self.error(self.error406values())
            )

    def form_re_render(self, 
            viewinfo, entityvaluemap, entityvals, context_extra_values={}, 
            error_head=None, error_message=None):
        """
        Returns re-rendering of form with current values and error message displayed.
        """
        form_context = self.get_form_display_context(
            viewinfo, entityvaluemap, entityvals, **context_extra_values
            )
        # log.info("********\nform_context %r"%form_context)
        form_context['error_head']    = error_head
        form_context['error_message'] = error_message
        return (
            self.render_html(form_context, self.formtemplate) or 
            self.error(self.error406values())
            )

    # @@TODO: refactor form_response to separate methods for each action
    #         form_response should handle initial checking and dispatching.
    #         The refactoring shopuld attempt to separate methods that use the
    #         form data to analyse the response received from methods that process
    #         update trhe entity data, or display a new form based on entity data.
    #         The `entityformvals` local variable which contains entity data updated
    #         with values extracted from the form response should be used as the 
    #         link between these facets of response processing.
    def form_response(self, viewinfo, context_extra_values):
        """
        Handle POST response from entity edit form.
        """
        log.log(settings.TRACE_FIELD_VALUE,
            "form_response entity_id %s, orig_entity_id %s, type_id %s, orig_type_id %s"%
            (viewinfo.curr_entity_id, viewinfo.orig_entity_id, viewinfo.curr_type_id, viewinfo.orig_type_id)
            )
        form_data = self.request.POST
        if ('cancel' in form_data) or ('close' in form_data):
            return HttpResponseRedirect(viewinfo.get_continuation_next())

        responseinfo = ResponseInfo()
        typeinfo     = viewinfo.entitytypeinfo
        messages     = viewinfo.type_messages
        orig_entity  = self.get_entity(viewinfo.orig_entity_id, typeinfo, viewinfo.action)
        # log.info("orig_entity %r"%(orig_entity.get_values(),))
        try:
            entityvaluemap = self.get_view_entityvaluemap(viewinfo, orig_entity)
            entityformvals = entityvaluemap.map_form_data_to_values(form_data, orig_entity)
        except Annalist_Error as e:
            return viewinfo.report_error(str(e))

        # Save updated details
        if 'save' in form_data:
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            log.info("save: continuation_url '%s'"%(viewinfo.get_continuation_next()))
            return responseinfo.http_redirect(self, viewinfo.get_continuation_next())

        # Import data described by a field with an activated "Import" button
        import_field = self.find_import(entityvaluemap, form_data)
        if import_field:
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                import_field=import_field,
                responseinfo=responseinfo
                )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Update or define new view or type (invoked from generic entity editing view)
        # Save current entity and redirect to view edit with new field added, and
        # current page as continuation.
        if 'use_view' in form_data:
            # Save entity, then redirect to selected view
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            if not responseinfo.has_http_response():
                view_uri_params = (
                    { 'coll_id':    viewinfo.coll_id
                    , 'type_id':    viewinfo.curr_type_id
                    , 'view_id':    extract_entity_id(form_data['view_choice'])
                    , 'entity_id':  viewinfo.curr_entity_id or viewinfo.entity_id
                    , 'action':     self.uri_action
                    })
                redirect_uri = (
                    uri_with_params(
                        self.view_uri("AnnalistEntityEditView", **view_uri_params),
                        viewinfo.get_continuation_url_dict()
                        )
                    )
                responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
            return responseinfo.get_http_response()

        # If "Edit" or "Copy" button invoked, initiate new view of current entity
        edit_action = (
            "edit" if 'edit' in form_data else
            "copy" if 'copy' in form_data else
            "view" if 'view' in form_data else None
            )
        if edit_action is not None:
            view_edit_uri_base = self.view_uri("AnnalistEntityEditView",
                coll_id=viewinfo.coll_id,
                type_id=self.uri_type_id,       # entity_type_id,
                view_id=viewinfo.view_id,
                entity_id=self.uri_entity_id,   # entity_id,
                action=edit_action
                )
            responseinfo = self.save_invoke_edit_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                view_edit_uri_base, edit_action,
                {},
                responseinfo=responseinfo
                )
            return responseinfo.get_http_response()

        # New entity buttons
        #
        # These may use explicit button ids per the table below, or may be part of
        # an enumerated-value field used to create a new referenced entity instance.
        #
        # In all cases, the current entity is saved and the browser is redirected 
        # to a new page to enter details of a new/updated entity of the appropriate 
        # type.
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
            new_type_id    = extract_entity_id(new_enum['field_ref_type'])
            new_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, new_type_id
                )
            new_view_id  = new_typeinfo.get_default_view_id()

        if new_type_id:
            edit_entity_id = None
            edit_type_id, edit_entity_id = split_type_entity_id(
                new_enum and new_enum.get('enum_value', None), 
                default_type_id=new_type_id)
            edit_action    = "new"
            edit_url_id    = "AnnalistEntityNewView"
            if edit_entity_id:
                # Entity selected: edit (use type from selected entity)
                edit_typeinfo = EntityTypeInfo(
                    viewinfo.site, viewinfo.collection, edit_type_id
                    )
                edit_view_id  = edit_typeinfo.get_default_view_id()
                edit_action   = "edit"
                new_edit_url_base = self.view_uri("AnnalistEntityEditView",
                    coll_id=viewinfo.coll_id, 
                    view_id=edit_view_id, 
                    type_id=edit_type_id, 
                    entity_id=edit_entity_id,
                    action=edit_action
                    )
            else:
                # No entity selected: create new
                new_edit_url_base = self.view_uri("AnnalistEntityNewView",
                    coll_id=viewinfo.coll_id, 
                    view_id=new_view_id, 
                    type_id=new_type_id, 
                    action=edit_action
                    )
            responseinfo = self.save_invoke_edit_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                new_edit_url_base, edit_action,
                {},
                responseinfo=responseinfo
                )
            return responseinfo.get_http_response()

        # Add field from entity view (as opposed to view description view)
        # See below call of 'find_add_field' for adding field in view description
        # @@TODO: remove references to add_view_field option (use just 'open_view')
        if ('add_view_field' in form_data) or ('open_view' in form_data):
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
            log.info("Open view: entity_id: %s"%viewinfo.curr_entity_id)
            responseinfo = self.save_invoke_edit_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                view_edit_uri_base, "config",
                add_field_param,
                responseinfo=responseinfo
                )
            return responseinfo.get_http_response()

        # Add new instance of repeating field, and redisplay
        add_field = self.find_add_field(entityvaluemap, form_data)
        # log.info("*** Add field: "+repr(add_field))
        if add_field:
            responseinfo.set_http_response(
                self.update_repeat_field_group(
                    viewinfo, add_field, entityvaluemap, entityformvals, 
                    **context_extra_values
                    )
                )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Remove Field(s), and redisplay
        remove_field = self.find_remove_field(entityvaluemap, form_data)
        if remove_field:
            if remove_field['remove_fields']:
                responseinfo.set_http_response(
                    self.update_repeat_field_group(
                        viewinfo, remove_field, entityvaluemap, entityformvals, 
                        **context_extra_values
                        )
                    )
            else:
                log.debug("form_response: No field(s) selected for remove_field")
                responseinfo.set_http_response(
                    self.form_re_render(
                        viewinfo, entityvaluemap, entityformvals, context_extra_values,
                        error_head=messages['remove_field_error'],
                        error_message=messages['no_field_selected']
                        )
                    )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Move field and redisplay
        move_field = self.find_move_field(entityvaluemap, form_data)
        if move_field:
            if move_field['move_fields']:
                http_response = self.update_repeat_field_group(
                    viewinfo, move_field, entityvaluemap, entityformvals, **context_extra_values
                    )
            else:
                log.debug("form_response: No field selected for move up/down")
                responseinfo.set_http_response(
                    self.form_re_render(
                        viewinfo, entityvaluemap, entityformvals, context_extra_values,
                        error_head=messages['move_field_error'],
                        error_message=messages['no_field_selected']
                        )
                    )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Task buttons
        #
        # These are buttons on selected displays that are used to invoke a complex 
        # task using information from the current view.
        #@@ ..........
        task_id = self.find_task_button(entityvaluemap, form_data)
        if task_id:
            responseinfo = self.save_invoke_task(
                viewinfo, entityvaluemap, entityformvals, 
                context_extra_values,
                task_id=task_id,
                responseinfo=responseinfo
                )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(form_data), 
            message.SYSTEM_ERROR
            )
        log.warning("Unexpected form data %s"%(err_values))
        log.warning("Continue to %s"%(viewinfo.get_continuation_next()))
        for k, v in form_data.items():
            log.info("  form[%s] = %r"%(k,v))
        redirect_uri = uri_with_params(viewinfo.get_continuation_next(), err_values)
        responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        return responseinfo.get_http_response()

    def save_entity(
            self, viewinfo, entityvaluemap, entityformvals, context_extra_values,
            import_field=None, responseinfo=None
            ):
        """
        This method contains logic to save entity data modified through a form
        interface.  If an entity is being edited (as opposed to created or copied)
        and the entity id or type have been changed, then new entity data is written 
        and the original entity data is removed.  If an entity was being viewed,
        no data is saved.

        viewinfo        contains display context for the form which is being processed
        entityvaluemap  a list of field descriptions that are used to map valuyes between
                        the edited entyity and the form display, including references to
                        field descriptions that control hopw values are rendered.  This
                        is used to find form 
        entityformvals  a dictionary of entity values extracted from the submitted form; 
                        these are used either for redisplayiongthe form if there is an 
                        error, or to update the saved entity data.
        context_extra_values
                        a dictionary of additional values that may be used if the
                        form needs to be redisplayed.
        import_field    if specified, is a field description for which a resource 
                        import is requested.  cf. method `save_linked_resource`.
        responseinfo    a `ResponseInfo` object that is used to collect diagnostic 
                        information about form processing.  It may contain an HTTP 
                        response object if the form or an error page needs to be 
                        displayed, a flag indicating whether the entity data was
                        updated, and any additional messages to be included with
                        any other response.

        Returns the supplied ResponseInfo object, with `None` for the HTTPResponse 
        valuer of the save completes successfully, otherwise an HTTP response object 
        that reports the nature of the problem.
        """
        if responseinfo is None:
            raise ValueError("entityedit.save_entity expects ResponseInfo object")
        if responseinfo.has_http_response():
            return responseinfo
        # log.info("save_entity: formvals: %r, import_field %r"%(entityformvals, import_field))
        entity_id      = viewinfo.curr_entity_id
        entity_type_id = viewinfo.curr_type_id
        orig_entity_id = viewinfo.orig_entity_id
        orig_type_id   = viewinfo.orig_type_id
        action         = viewinfo.action
        typeinfo       = viewinfo.entitytypeinfo
        messages       = viewinfo.type_messages
        if self.uri_action == "view":
            # This is a view operation: nothing to save
            return responseinfo
        if not action in ["new", "copy", "edit"]:
            log.warning("'Save' operation for action '%s'"%(action))
            # Check "edit" authorization to continue
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
        entity_renamed = (
            ( action == "edit" ) and
            ( (entity_id      != orig_entity_id) or 
              (entity_type_id != orig_type_id  ) )
            )

        # @@TODO: factor out repeated re-rendering logic

        # Check for valid id and type to be saved
        if not valid_id(entity_id):
            log.debug("form_response: entity_id not valid_id('%s')"%entity_id)
            return responseinfo.set_http_response(
                self.form_re_render(
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_invalid_id']
                    )
                )
        if not valid_id(entity_type_id):
            log.info("form_response: entity_type_id not valid_id('%s')"%entity_type_id)
            return responseinfo.set_http_response(
                self.form_re_render(
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['entity_type_heading'],
                    error_message=messages['entity_type_invalid']
                    )
                )

        # Check original parent exists (still)
        #@@ TODO: unless this is a "new" action?
        if not typeinfo.parent_exists():
            log.warning("save_entity: original entity parent does not exist")
            return responseinfo.set_http_response(
                self.form_re_render(
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['parent_heading'],
                    error_message=messages['parent_missing']
                    )
                )

        # Determine type information for saved entity
        if entity_type_id != orig_type_id:
            # log.info("new_typeinfo: entity_type_id %s"%(entity_type_id))
            new_typeinfo = EntityTypeInfo(
                viewinfo.site, viewinfo.collection, entity_type_id, 
                create_typedata=True
                )
        else:
            new_typeinfo = typeinfo

        # Check existence of entity to save according to action performed
        if (action in ["new", "copy"]) or entity_renamed:
            if not viewinfo.saved():
                # First save - check for existence
                if new_typeinfo.entity_exists(entity_id):
                    log.warning(
                        "Entity exists: action %s %s/%s, orig %s/%s"%
                            (action, entity_type_id, entity_id, orig_type_id, orig_entity_id)
                        )
                    return responseinfo.set_http_response(
                        self.form_re_render(
                            viewinfo, entityvaluemap, entityformvals, context_extra_values,
                            error_head=messages['entity_heading'],
                            error_message=messages['entity_exists']
                            )
                        )
        else:
            if not typeinfo.entity_exists(entity_id, use_altparent=True):
                # This shouldn't happen, but just in case...
                log.warning("Expected %s/%s not found; action %s, entity_renamed %r"%
                      (entity_type_id, entity_id, action, entity_renamed)
                    )
                return responseinfo.set_http_response(
                    self.form_re_render(
                        viewinfo, entityvaluemap, entityformvals, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_not_exists']
                        )
                    )

        # Assemble updated values for storage
        #
        # Note: form data is applied as update to original entity data so that
        # values not in view are preserved.  Use original entity values without 
        # field aliases as basis for new value.
        orig_entity   = typeinfo.get_entity(orig_entity_id, action)
        orig_values   = orig_entity.get_values() if orig_entity else {}
        entity_values = self.merge_entity_form_values(orig_values, entityformvals)
        if action == "copy":
            entity_values.pop(ANNAL.CURIE.uri, None)      # Force new URI on copy
        entity_values[ANNAL.CURIE.type_id] = entity_type_id
        entity_values[ANNAL.CURIE.type]    = new_typeinfo.entityclass._entitytype
        # log.info("save entity_values%r"%(entity_values))

        # Create/update stored data now
        if not entity_renamed:
            # Normal (non-type) entity create or update, no renaming
            err_vals = self.create_update_entity(new_typeinfo, entity_id, entity_values)
        else:
            if "_type" not in [entity_type_id, orig_type_id]:
                # Non-type record rename
                err_vals = self.rename_entity(
                    typeinfo, orig_entity_id, new_typeinfo, entity_id, entity_values
                    )
            else:
                # Type renamed
                err_vals = self.rename_entity_type(
                    viewinfo, 
                    typeinfo, orig_entity_id, 
                    new_typeinfo, entity_id, entity_values
                    )
            if not err_vals:
                viewinfo.update_continuation_url(
                    old_type_id=orig_type_id,   old_entity_id=orig_entity_id,
                    new_type_id=entity_type_id, new_entity_id=entity_id
                    )

        # Save any imported resource or uploaded files
        if not err_vals:
            responseinfo = self.save_uploaded_files(
                entity_id, new_typeinfo,
                entityvaluemap, entity_values,
                self.request.FILES,
                responseinfo
                )
        if not err_vals and import_field is not None:
            responseinfo = self.save_linked_resource(
                entity_id, new_typeinfo,
                entityvaluemap, entity_values,
                import_field,
                responseinfo
                )
            # log.info("save_linked_resource: responseinfo %r"%responseinfo)
            # log.info("save_linked_resource: entity_values %r"%entity_values)
        if responseinfo.is_updated():
            err_vals = self.create_update_entity(new_typeinfo, entity_id, entity_values)

        # Finish up
        if err_vals:
            log.warning("err_vals %r"%(err_vals,))
            return responseinfo.set_http_response(
                self.form_re_render(
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=err_vals[0],
                    error_message=err_vals[1]
                    )
                )
        log.info("Saved %s/%s"%(entity_type_id, entity_id))
        viewinfo.saved(is_saved=True)
        viewinfo.update_coll_version()
        return responseinfo

    def import_resource(self,
            field_desc, field_name,
            type_id, entity_id, entityvals,
            init_field_vals, read_resource,
            responseinfo
            ):
        """
        Common logic for saving uploaded files or linked resources.

        field_desc      Field descriptor for import/upload field
        field_name      is the name of the field instance for which a 
                        resource is imported.
        type_id         Id of type of entity to which uploaded resource is attached
        entity_id       Id of entity
        entityvals      Entity values dictionary
        init_field_vals is a function that is called to set up a field values
                        dictionary. Called as:
                            init_field_vals(field_vals, field_name, field_string)
        read_resource   opens and saves a resource.  Also updates the supplied 
                        field_vals with details of the accessed resource.  Called as:
                            read_resource(field_desc, field_name, field_vals)
        responseinfo    receives information about any read_resource error.
                        The structure is provided with message templates for reporting.

        returns `import_vals`, which is a copy of the field values augmented with 
        some additional information to assist diagnostic generation.
        """
        log.info("Importing resource for %s"%field_name)
        property_uri = field_desc['field_property_uri']
        fv           = entityvals[property_uri]
        if isinstance(fv, dict):
            field_vals   = fv.copy()
            field_string = None
        elif isinstance(fv, (str, unicode)):
            field_vals   = {}
            field_string = fv
        else:
            field_vals = {}
        init_field_vals(field_vals, field_name, field_string)
        import_vals  = field_vals.copy()    # Used for reporting..
        import_vals.update(
            { 'id':         entity_id
            , 'type_id':    type_id
            })
        log.debug("import_vals: %r"%(import_vals))
        try:
            read_resource(field_desc, field_name, field_vals)
            # Import completed: update field in entity value dictionary
            entityvals[property_uri] = field_vals
            import_vals.update(field_vals)
            import_done = responseinfo.get_message('import_done')
            import_msg  = responseinfo.get_formatted('import_done_info', import_vals)
            responseinfo.set_updated()
            responseinfo.set_response_confirmation(import_done, import_msg)
        except Exception as e:
            import_err = responseinfo.get_message('import_err')
            import_msg = responseinfo.get_formatted(
                'import_err_info', dict(import_vals, import_exc=str(e))
                )
            log.warning("%s: %s"%(import_err, import_msg))
            log.debug(str(e), exc_info=True)
            responseinfo.set_response_error(import_err, import_msg)
        return import_vals

    def save_uploaded_files(self,
        entity_id, typeinfo,
        entityvaluemap, entityvals,
        uploaded_files,
        responseinfo
        ):
        """
        Process uploaded files: files are saved to the entity directory, and 
        the supplied entity values are updated accordingly

        This functon operates by scanning through fields that may generate a file
        upload and looking for a corresponding uploaded files.  Uploaded files not
        corresponding to view fields are ignored.

        uploaded_files  is the Django uploaded files information from the request
                        bveing processed.

        Updates and returns the supplied responseinfo object.
        """
        def is_upload_f(fd):
            return fd.is_upload_field()
        def init_field_vals(field_vals, field_name, field_string):
            field_vals['upload_name']   = field_name
            field_vals['uploaded_file'] = field_vals.get('uploaded_file', field_string)
            return
        def read_resource(field_desc, field_name, field_vals):
            value_type    = field_desc.get('field_target_type', ANNAL.CURIE.unknown_type)
            uploaded_file = uploaded_files[field_name]
            resource_type = uploaded_file.content_type
            with typeinfo.get_fileobj(
                    entity_id, field_name, value_type, resource_type, "wb"
                    ) as local_fileobj:
                resource_name = os.path.basename(local_fileobj.name)
                field_vals.update(
                    { 'resource_name':  resource_name
                    , 'resource_type':  resource_type
                    , 'uploaded_file':  uploaded_file.name
                    , 'uploaded_size':  uploaded_file.size
                    })
                for chunk in uploaded_files[upload_name].chunks():
                    local_fileobj.write(chunk)
            return

        # log.info("save_uploaded_files, entityvals: %r"%(entityvals,))  #@@
        if responseinfo.is_response_error():
            return responseinfo     # Error already seen - return now
        responseinfo.set_message_templates(
            { 'import_err':         message.UPLOAD_ERROR
            , 'import_err_info':    message.UPLOAD_ERROR_REASON
            , 'import_done':        message.UPLOAD_DONE
            , 'import_done_info':   message.UPLOAD_DONE_DETAIL
            })
        for fd in self.find_fields(entityvaluemap, is_upload_f):
            upload_name  = fd.get_field_instance_name()
            if upload_name in uploaded_files:
                self.import_resource(
                    fd, upload_name,
                    typeinfo.type_id, entity_id, entityvals,
                    init_field_vals, read_resource,
                    responseinfo
                    )
                # end if
            # end for
        return responseinfo

    def save_linked_resource(self, 
            entity_id, typeinfo,
            entityvaluemap, entityvals,
            import_field,
            responseinfo
            ):
        """
        Imports a resource described by a supplied field description, updates the 
        saved entity with information about the imported resource, and redisplays 
        the current form.

        import_field    is field description of import field that has been triggered.

        Updates and returns the supplied responseinfo object.
        """
        def init_field_vals(field_vals, field_name, field_string):
            field_vals['import_name'] = field_name
            field_vals['import_url']  = field_vals.get('import_url', field_string)
            return
        def read_resource(field_desc, field_name, field_vals):
            import_url = field_vals['import_url']
            resource_fileobj, resource_url, resource_type = open_url(import_url)
            log.debug(
                "import_field: import_url %s, resource_url %s, resource_type %s"%
                (import_url, resource_url, resource_type)
                )
            try:
                value_type    = import_field.get('field_target_type', ANNAL.CURIE.unknown_type)
                with typeinfo.get_fileobj(
                        entity_id, field_name, value_type, resource_type, "wb"
                        ) as local_fileobj:
                    resource_name = os.path.basename(local_fileobj.name)
                    field_vals.update(
                        { 'resource_url' :  resource_url
                        , 'resource_name':  resource_name
                        , 'resource_type':  resource_type
                        })
                    #@@TODO: timeout / size limit?  (Potential DoS?)
                    copy_resource_to_fileobj(resource_fileobj, local_fileobj)
            finally:
                resource_fileobj.close()
            return

        # log.info("save_linked_resource, entityvals: %r"%(entityvals,))  #@@
        if responseinfo.is_response_error():
            return responseinfo     # Error already seen - return now
        responseinfo.set_message_templates(
            { 'import_err':         message.IMPORT_ERROR
            , 'import_err_info':    message.IMPORT_ERROR_REASON
            , 'import_done':        message.IMPORT_DONE
            , 'import_done_info':   message.IMPORT_DONE_DETAIL
            })
        import_name = import_field.get_field_instance_name()
        self.import_resource(
            import_field, import_name,
            typeinfo.type_id, entity_id, entityvals,
            init_field_vals, read_resource,
            responseinfo
            )
        return responseinfo

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
        log.info("rename_entity old: %s, new: %s, vals: %r"%(old_entity_id, new_entity_id, entity_values))
        new_typeinfo.create_entity(new_entity_id, entity_values)
        new_typeinfo.copy_data_files(new_entity_id, old_typeinfo, old_entity_id)
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

    def save_invoke_edit_entity(self, 
            viewinfo, entityvaluemap, entityvals, context_extra_values,
            config_edit_url, edit_perm,
            url_params,
            responseinfo=None):
        """
        Common logic for invoking a resource edit while editing
        some other resource:
          - the entity currently being edited is saved
          - the invoke_edit_entity method (below) is called

        If there is a problem, an error response is returned for display 
        in the current view.
        """
        responseinfo = self.save_entity(
            viewinfo, entityvaluemap, entityvals, context_extra_values,
            responseinfo=responseinfo
            )
        if not responseinfo.has_http_response():
            responseinfo.set_http_response(
                self.invoke_edit_entity(
                    viewinfo, edit_perm,
                    config_edit_url, url_params, 
                    viewinfo.curr_type_id,
                    viewinfo.curr_entity_id or viewinfo.orig_entity_id
                    )
                )
        return responseinfo

    def invoke_edit_entity(self, 
            viewinfo, edit_perm,
            edit_url, url_params, 
            entity_type_id, entity_id
            ):
        """
        Common logic for invoking a resource edit while editing
        or viewing some other resource:
          - authorization to perform the requested edit is checked
          - a continuaton URL is calculated which is the URL for the current view
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
        entity_type_id      type_id of entity currently being presented.
        entity_id           entity_id of entity currently presented.
        """
        if viewinfo.check_authorization(edit_perm):
            return viewinfo.http_response
        log.info("invoke_edit_entity: entity_id %s"%entity_id)
        cont_here = viewinfo.get_continuation_here(
            base_here=self.view_uri(
                "AnnalistEntityEditView", 
                coll_id=viewinfo.coll_id,
                view_id=viewinfo.view_id,
                type_id=entity_type_id,
                entity_id=entity_id,
                action=self.uri_action
                )
            )
        return HttpResponseRedirect(
            uri_with_params(edit_url, url_params, {'continuation_url': cont_here})
            )

    def save_invoke_task(self, 
            viewinfo, entityvaluemap, entityformvals,
            context_extra_values,
            task_id=None,
            responseinfo=None
            ):
        """
        Save current entity and invoke identified task using current entity values

        viewinfo        contains display context for the form which is being processed
        entityvaluemap  a list of field descriptions that are used to map valuyes between
                        the edited entyity and the form display, including references to
                        field descriptions that control hopw values are rendered.  This
                        is used to find form 
        entityformvals  a dictionary of entity values extracted from the submitted form; 
                        these are used either for redisplayiongthe form if there is an 
                        error, or to update the saved entity data.
        context_extra_values
                        a dictionary of additional values that may be used if the
                        form needs to be redisplayed.
        task_id         if to task to be performed.
        responseinfo    a `ResponseInfo` object that is used to collect diagnostic 
                        information about form processing.  It may contain an HTTP 
                        response object if the form or an error page needs to be 
                        displayed, a flag indicating whether the entity data was
                        updated, and any additional messages to be included with
                        any other response.

        Returns the updated responseinfo value.
        """
        responseinfo = self.save_entity(
            viewinfo, entityvaluemap, entityformvals, context_extra_values,
            responseinfo=responseinfo
            )
        if responseinfo.is_response_error():
            return responseinfo
        if task_id == "_task/Define_view_list":
            #@@.................
            #@@TODO: drive this logic from a stored _task descriuption
            # Extract info from entityformvals
            type_entity_id = "_type/"+entityformvals[ANNAL.CURIE.id]
            type_label     = entityformvals[RDFS.CURIE.label]
            type_uri       = entityformvals.get(ANNAL.CURIE.uri, None)
            view_entity_id = "_view/"+entityformvals[ANNAL.CURIE.id]
            list_entity_id = "_list/"+entityformvals[ANNAL.CURIE.id]
            list_selector  = "'%s' in [@type]"%(type_uri) if type_uri else "ALL"
            # Set up view details (other defaults from sitedata '_initial_values')
            view_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_view")
            view_entity   = view_typeinfo.get_create_entity(view_entity_id)
            view_entity[ANNAL.CURIE.record_type] = type_uri
            view_entity.setdefault(RDFS.CURIE.label,        "View of "+type_label)
            view_entity.setdefault(RDFS.CURIE.comment,      "View of "+type_label)
            view_entity._save()
            # Set up list details (other defaults from sitedata '_initial_values')
            list_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_list")
            list_entity   = list_typeinfo.get_create_entity(list_entity_id)
            list_entity.setdefault(RDFS.CURIE.label,         "List of "+type_label)
            list_entity.setdefault(RDFS.CURIE.comment,       "List of "+type_label)
            list_entity[ANNAL.CURIE.default_view] = view_entity_id
            list_entity[ANNAL.CURIE.default_type] = type_entity_id
            list_entity[ANNAL.CURIE.record_type]  = type_uri
            list_entity[ANNAL.CURIE.display_type] = "List"
            list_entity[ANNAL.CURIE.list_entity_selector] = list_selector
            list_entity._save()
            # Update view, list values in type record, and save again
            entityformvals[ANNAL.CURIE.type_view] = view_entity_id
            entityformvals[ANNAL.CURIE.type_list] = list_entity_id
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            info_values = self.info_params(
                message.TASK_CREATE_VIEW_LIST%{'label': type_label}
                )
            redirect_uri = self.get_form_refresh_uri(viewinfo, params=info_values)
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        elif task_id == "_task/Define_repeat_field":
            # Extract info from entityformvals (form is a field description)
            field_entity_id     = entityformvals[ANNAL.CURIE.id]
            field_label         = entityformvals[RDFS.CURIE.label]
            field_entity_type   = entityformvals[ANNAL.CURIE.field_entity_type]
            field_property_uri  = entityformvals[ANNAL.CURIE.property_uri]
            repeat_entity_id    = field_entity_id + "_repeat"
            repeat_property_uri = field_property_uri + "_repeat"
            repeat_field_label  = "Repeat field '%s'"%field_label
            # Create repeat-field group (defaults from sitedata '_group/_initial_values')
            group_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_group")
            group_entity   = group_typeinfo.get_create_entity(repeat_entity_id)
            group_entity.setdefault(RDFS.CURIE.label,           repeat_field_label)
            group_entity.setdefault(RDFS.CURIE.comment,         repeat_field_label)
            group_entity.setdefault(ANNAL.CURIE.record_type,    field_entity_type)
            if not group_entity.get(ANNAL.CURIE.group_fields,   None):
                group_entity[ANNAL.CURIE.group_fields] = (
                    [ { ANNAL.CURIE.field_id:           "_field/"+field_entity_id
                      , ANNAL.CURIE.property_uri:       field_property_uri
                      , ANNAL.CURIE.field_placement:    "small:0,12"
                      }
                    ])
            group_entity._save()
            # Create repeat-field referencing group
            field_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_field")
            field_entity   = field_typeinfo.get_create_entity(repeat_entity_id)
            field_entity[ANNAL.CURIE.field_render_type] = "RepeatGroupRow"
            field_entity[ANNAL.CURIE.field_value_mode]  = "Value_direct"
            field_entity[ANNAL.CURIE.field_value_type]  = "annal:Field_group"
            field_entity[ANNAL.CURIE.group_ref]         = "_group/"+repeat_entity_id
            field_entity[ANNAL.CURIE.field_entity_type] = field_entity_type
            field_entity.setdefault(RDFS.CURIE.label,                 repeat_field_label)
            field_entity.setdefault(RDFS.CURIE.comment,               repeat_field_label)
            field_entity.setdefault(ANNAL.CURIE.placeholder,          "(Repeat field "+field_label+")")
            field_entity.setdefault(ANNAL.CURIE.property_uri,         repeat_property_uri)
            field_entity.setdefault(ANNAL.CURIE.field_placement,      "small:0,12")
            field_entity.setdefault(ANNAL.CURIE.repeat_label_add,     "Add "+field_label)
            field_entity.setdefault(ANNAL.CURIE.repeat_label_delete,  "Remove "+field_label)
            field_entity._save()
            # Redisplay field view with message
            info_values = self.info_params(
                message.TASK_CREATE_REPEAT_FIELD%
                  {'field_id': repeat_entity_id, 'group_id': repeat_entity_id, 'label': field_label}
                )
            redirect_uri = self.get_form_refresh_uri(viewinfo, params=info_values)
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        elif task_id == "_task/Define_field_ref":
            # Extract info from entityformvals (form is a field description)
            field_entity_id     = entityformvals[ANNAL.CURIE.id]
            field_label         = entityformvals[RDFS.CURIE.label]
            field_property_uri  = entityformvals[ANNAL.CURIE.property_uri]
            field_entity_type   = entityformvals[ANNAL.CURIE.field_entity_type]
            ref_entity_id       = field_entity_id + "_ref"
            ref_property_uri    = field_property_uri + "_ref"
            ref_field_label     = "Reference field '%s'"%field_label
            # Create field-reference group (defaults from sitedata '_group/_initial_values')
            group_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_group")
            group_entity   = group_typeinfo.get_create_entity(ref_entity_id)
            group_entity.setdefault(RDFS.CURIE.label,         ref_field_label)
            group_entity.setdefault(RDFS.CURIE.comment,       ref_field_label)
            group_entity.setdefault(ANNAL.CURIE.record_type,  field_entity_type)
            if not group_entity.get(ANNAL.CURIE.group_fields, None):
                group_entity[ANNAL.CURIE.group_fields] = (
                    [ { ANNAL.CURIE.field_id:           "_field/"+field_entity_id
                      , ANNAL.CURIE.field_placement:    "small:0,12"
                      }
                    ])
            group_entity._save()
            # Create field group reference
            field_typeinfo = EntityTypeInfo(viewinfo.site, viewinfo.collection, "_field")
            field_entity   = field_typeinfo.get_create_entity(ref_entity_id)
            field_entity[ANNAL.CURIE.field_render_type] = "RefMultifield"
            field_entity[ANNAL.CURIE.field_value_mode]  = "Value_entity"
            field_entity[ANNAL.CURIE.field_value_type]  = "annal:Slug"
            field_entity[ANNAL.CURIE.group_ref]         = "_group/"+ref_entity_id
            field_entity[ANNAL.CURIE.field_entity_type] = field_entity_type
            field_entity.setdefault(RDFS.CURIE.label,             ref_field_label)
            field_entity.setdefault(RDFS.CURIE.comment,           ref_field_label)
            field_entity.setdefault(ANNAL.CURIE.placeholder,      "(Reference field "+field_label+")")
            field_entity.setdefault(ANNAL.CURIE.property_uri,     ref_property_uri)
            field_entity.setdefault(ANNAL.CURIE.field_placement,  "small:0,12")
            field_entity.setdefault(ANNAL.CURIE.field_ref_type,   "Default_type")
            field_entity._save()
            # Display new reference field view with message; continuation same as current view
            info_values = self.info_params(
                message.TASK_CREATE_REFERENCE_FIELD%
                  {'field_id': ref_entity_id, 'group_id': ref_entity_id, 'label': field_label}
                )
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    "_field"
                , 'entity_id':  ref_entity_id
                , 'view_id':    "Field_view"
                , 'action':     "edit"
                })
            more_uri_params = viewinfo.get_continuation_url_dict()
            more_uri_params.update(info_values)
            redirect_uri = (
                uri_with_params(
                    self.view_uri("AnnalistEntityEditView", **view_uri_params),
                    more_uri_params
                    )
                )
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        else:
            log.error("EntityEdit.save_invoketask: Unknown task_id %s"%(task_id,))
            err_values = self.error_params(
                message.UNKNOWN_TASK_ID%{'task_id': task_id}, 
                message.SYSTEM_ERROR
                )
            redirect_uri = self.get_form_refresh_uri(viewinfo, params=err_values)
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        return responseinfo

    def _do_something_placeholder(self, 
            viewinfo, entityvaluemap, entityformvals,
            context_extra_values,
            some_param=None, 
            responseinfo=None
            ):
        """
        @@ <placeholder function skeleton>

        Save current entity and <do something> using current entity values

        viewinfo        contains display context for the form which is being processed
        entityvaluemap  a list of field descriptions that are used to map valuyes between
                        the edited entyity and the form display, including references to
                        field descriptions that control hopw values are rendered.  This
                        is used to find form 
        entityformvals  a dictionary of entity values extracted from the submitted form; 
                        these are used either for redisplayiongthe form if there is an 
                        error, or to update the saved entity data.
        context_extra_values
                        a dictionary of additional values that may be used if the
                        form needs to be redisplayed.
        some_param      ...
        responseinfo    a `ResponseInfo` object that is used to collect diagnostic 
                        information about form processing.  It may contain an HTTP 
                        response object if the form or an error page needs to be 
                        displayed, a flag indicating whether the entity data was
                        updated, and any additional messages to be included with
                        any other response.
        """
        responseinfo = self.save_entity(
            viewinfo, entityvaluemap, entityformvals, context_extra_values,
            responseinfo=responseinfo
            )
        if responseinfo.is_response_error():
            return responseinfo
        info_values = self.error_params(
            "@@TODO: implement 'do_something'", 
            message.SYSTEM_ERROR
            )
        redirect_uri = self.get_form_refresh_uri(viewinfo, params=info_values)
        responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
        return responseinfo

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
                    repeat_desc['remove_fields'] = form_data.getlist(remove_fields_key)
                else:
                    repeat_desc['remove_fields'] = []
                return repeat_desc
        return None

    def find_move_field(self, entityvaluemap, form_data):
        """
        Locate move field option in form data and, if present, return a description 
        of the field to be moved, with the member index to be moved added as  element 
        'remove_fields', and the direction of movement as element 'move_direction'.
        """
        for repeat_desc in self.find_repeat_fields(entityvaluemap):
            # log.info("find_remove_field: %r"%repeat_desc)
            move_direction = None            
            if repeat_desc['group_id']+"__up" in form_data:
                move_direction = "up"
            elif repeat_desc['group_id']+"__down" in form_data:
                move_direction = "down"
            if move_direction is not None:
                repeat_desc['move_direction'] = move_direction
                move_fields_key = repeat_desc['group_id']+"__select_fields"
                if move_fields_key in form_data:
                    repeat_desc['move_fields'] = form_data.getlist(move_fields_key)
                else:
                    repeat_desc['move_fields'] = []
                return repeat_desc
        return None

    def find_new_enum(self, entityvaluemap, form_data):
        """
        Locate add enumerated value option in form data and, if present, return a 
        description of the enumerated field for which a new value is to be created.

        Field 'field_ref_type' of the returned value is the type_id of the 
        enumerated value type.
        """
        def is_new_f(fd):
            # Using FieldDescription method directly doesn't work
            # log.info("find_new_enum is_new_f fd %r"%(fd,))  #@@
            return fd.has_new_button()
        for enum_desc in self.find_fields(entityvaluemap, is_new_f):
            # log.info("find_new_enum enum_desc %r"%(enum_desc,))  #@@
            enum_new_edit = self.form_data_contains(form_data, enum_desc, "new_edit")
            if enum_new_edit:
                enum_desc['enum_value'] = form_data[enum_new_edit]
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

    def update_repeat_field_group(self, 
            viewinfo, field_desc, entityvaluemap, entityformvals, **context_extra_values
            ):
        """
        Saves an entity instance data with a repeated field or field group added,
        moved or removed, then redisplays the current form.

        viewinfo    DisplayInfo object describing the current view.
        field_desc  is a field description for a field or field group to be added
                    or removed.  Fields are removed if the description contains a
                    'remove_fields' field, which contains a list of the repeat index
                    values to be removed, otherwise a field is added.
        entityvaluemap
                    an EntityValueMap object for the entity being presented.
        entityformvals  
                    is a dictionary of entity values to which the field is added.
        context_extra_values
                    is a dictionary of default and additional values not provided by the
                    entity itself, that may be needed to render the updated form. 

        returns None if the entity is updated and saved, or an HttpResponse object to 
        display an error message.
        """
        # log.info("field_desc: %r: %r"%(field_desc,))
        if 'remove_fields' in field_desc:
            self.remove_entity_field(field_desc, entityformvals)
        elif 'move_fields' in field_desc:
            self.move_entity_field(field_desc, entityformvals)           
        else:
            self.add_entity_field(field_desc, entityformvals)
        # log.info("entityvals: %r"%(entityvals,))
        responseinfo = ResponseInfo()
        http_response = self.save_entity(
            viewinfo, entityvaluemap, entityformvals, context_extra_values,
            responseinfo=responseinfo
            )
        return responseinfo.get_http_response()

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

    def move_entity_field(self, move_field_desc, entity):
        def reverselist(l):
            return list(reversed(l))
        def move_up(vals):
            """
            Local function to move selected elements towards the head of a list.
            Operates on a list of (valuye,flag) pairs
            Based on spike/rearrange-list/move_up.lhs:

            > move_up p []  = []
            > move_up p [v] = [v]
            > move_up p (v:vtail)
            >    | p v      = v:(move_up p vtail)
            > move_up p (v1:v2:vtail)
            >    | not (p v1) && (p v2) 
            >               = v2:(move_up p (v1:vtail))
            >    | not (p v1) && not (p v2) 
            >               = v1:(move_up p (v2:vtail))
            """
            if len(vals) <= 1:
                return vals
            v1 = vals[0]
            v2 = vals[1]
            if v1[1]:
                return [v1] + move_up(vals[1:])
            if v2[1]:
                return [v2] + move_up([v1]+vals[2:])
            else:
                return [v1] + move_up([v2]+vals[2:])
            raise RuntimeError("move_entity_field/move_up cases exhausted without match")
        # Shuffle selected items up or down
        repeatvals_key = move_field_desc['field_property_uri']
        old_repeatvals = entity[repeatvals_key]
        old_index_list = (
            [ (i, str(i) in move_field_desc['move_fields']) 
            for i in range(len(old_repeatvals))
            ])
        if move_field_desc['move_direction'] == 'up':
            new_index_list = move_up(old_index_list)
            log.info("***** Move up: %r"%(new_index_list,))
        elif move_field_desc['move_direction'] == 'down':
            new_index_list = reverselist(move_up(reverselist(old_index_list)))
            log.info("***** Move down: %r"%(new_index_list,))
        else:
            raise RuntimeError("move_entity_field - 'move_direction' must be 'up' or 'down'")
        new_repeatvals = (
            [ old_repeatvals[new_index_list[i][0]]
            for i in range(len(new_index_list))
            ])
        entity[repeatvals_key] = new_repeatvals
        return

    def find_import(self, entityvaluemap, form_data):
        """
        Locate any import option in form data and, if present, return a 
        description of the field describing the value to be imported.
        """
        def is_import_f(fd):
            return fd.is_import_field()
        for enum_desc in self.find_fields(entityvaluemap, is_import_f):
            enum_import = self.form_data_contains(form_data, enum_desc, "import")
            if enum_import:
                enum_desc.set_field_instance_name(enum_import)
                return enum_desc
        return None

    def find_task_button(self, entityvaluemap, form_data):
        """
        If form data indicates a task button has been triggered,
        return its Id, otherwise return None.
        """
        task_ids = (
            [ "_task/Define_view_list"
            , "_task/Define_repeat_field" 
            , "_task/Define_field_ref" 
            ])
        for t in task_ids:
            if extract_entity_id(t) in form_data:
                return t
        return None

    # The next two methods are used to locate form fields, which may be in repeat
    # groups, that contain asctivated additional controls (buttons).
    #
    # `find_fields` is a generator that locates candidate fields that *might* have 
    # a designated control, and
    # `form_data_contains` tests a field returned by `find_fields` to see if a 
    # designated control (identified by a name suffix) has been activated.

    def find_fields(self, entityvaluemap, filter_f):
        """
        Iterate over fields that satisfy the supplied predicate

        entityvaluemap  is the list of entity-value map entries for the current view
        filter_f        is a predicate that is applied to field description values, 
                        and returns True for those that are to be returned.

        Returns a generator of FieldDescription values from the supplied entity 
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
                    log.debug(
                        "entityedit.find_fields: field name %s, prefixes %r"%
                        (field_desc.get_field_name(), group_list)
                        )
                    yield field_desc
                if field_desc.has_field_group_ref():
                    groupref = field_desc.group_ref()
                    if not valid_id(groupref):
                        # this is for resilience in the face of bad data
                        log.warning(
                            "entityedit.find_fields: invalid group_ref %s in field description for %s"%
                               (groupref, field_desc['field_id'])
                            )
                    else:
                        log.debug(
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

    def form_data_contains(self, form_data, field_desc, field_name_postfix):
        """
        Tests to see if the form data contains a result field corresponding to 
        the supplied field descriptor (as returned by 'find_fields') with a 
        postfix value as supplied.

        Returns the full name of the field found (without the trailing suffix), 
        or None.
        """
        log.debug("form_data_contains: field_desc %r"%field_desc)
        log.debug("form_data_contains: group_list %r"%field_desc['group_list'])
        log.debug("form_data_contains: form_data %r"%form_data)
        field_name         = field_desc.get_field_name()
        def _scan_groups(prefix, group_list):
            """
            return (stop, result)
            where:
              'stop'   is True if there are no more possible results to try.
              'result' is the final result to return if `stop` is True.
            """
            stop_all   = True
            if group_list == []:
                try_field = prefix + field_name
                log.debug("form_data_contains: try_field %s__%s"%(try_field, field_name_postfix))
                if try_field in form_data:
                    try_postfix = try_field + "__" + field_name_postfix
                    return (try_postfix in form_data, try_field)
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
