"""
Generic entity edit view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import urlparse
import traceback
import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist.identifiers               import RDFS, ANNAL
from annalist.exceptions                import Annalist_Error
from annalist                           import message
from annalist                           import layout
from annalist.util                      import (
    valid_id, split_type_entity_id, extract_entity_id,
    label_from_id,
    open_url, copy_resource_to_fileobj
    )

import annalist.models.entitytypeinfo as entitytypeinfo
from annalist.models.entitytypeinfo     import EntityTypeInfo, get_built_in_type_ids, CONFIG_PERMISSIONS
from annalist.models.recordview         import RecordView
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitydata         import EntityData

from annalist.views.uri_builder         import uri_base, uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.responseinfo        import ResponseInfo
from annalist.views.generic             import AnnalistGenericView
from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap

from annalist.views.fields.field_description    import FieldDescription, field_description_from_view_field
from annalist.views.fields.bound_field          import bound_field, get_entity_values

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='url_type_id',           e=None,                    f=None               )
        , SimpleValueMap(c='view_choices',          e=None,                    f=None               )
        , SimpleValueMap(c='edit_view_button',      e=None,                    f=None               )
        , SimpleValueMap(c='edit_view_enable',      e=None,                    f=None               )
        , SimpleValueMap(c='default_view_enable',   e=None,                    f=None               )
        , SimpleValueMap(c='customize_view_enable', e=None,                    f=None               )
        , StableValueMap(c='entity_id',             e=ANNAL.CURIE.id,          f='entity_id'        )
        , SimpleValueMap(c='entity_uri',            e=ANNAL.CURIE.uri,         f='entity_uri'       )
        # The "record_type" value (in context and form data) is intended to reflect the actual
        # type of the displayed entity.  Currently, it is not used:
        , SimpleValueMap(c='record_type',           e=ANNAL.CURIE.type,        f='record_type'      )
        , SimpleValueMap(c='view_id',               e=None,                    f='view_id'          )
        , SimpleValueMap(c='orig_id',               e=None,                    f='orig_id'          )
        , SimpleValueMap(c='orig_type',             e=None,                    f='orig_type'        )
        , SimpleValueMap(c='orig_coll',             e=None,                    f='orig_coll'        )
        , SimpleValueMap(c='action',                e=None,                    f='action'           )
        , SimpleValueMap(c='continuation_url',      e=None,                    f='continuation_url' )
        , SimpleValueMap(c='continuation_param',    e=None,                    f=None               )
        # + Field data: added separately during processing of the form description
        # + Form and interaction control (hidden fields)
        ])

#   -------------------------------------------------------------------------------------------
#
#   Entity edit view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class GenericEntityEditView(AnnalistGenericView):
    """
    View class for generic entity edit view
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
        log.log(settings.TRACE_FIELD_VALUE, "  %s"%(self.get_request_path()))
        self.get_view_template(action, type_id, entity_id)
        action           = action or "view"
        viewinfo         = self.view_setup(
            action, coll_id, type_id, view_id, entity_id, request.GET.dict()
            )
        # viewinfo.check_authorization(action)
        if viewinfo.http_response:
            return viewinfo.http_response

        # Create local entity object or load values from existing
        typeinfo = viewinfo.curr_typeinfo
        entity   = self.get_entity(
            viewinfo.src_entity_id or viewinfo.use_entity_id, typeinfo, action
            )
        # log.debug("@@ GenericEntityEditView.get %r"%(entity,))
        if entity is None:
            entity_label = (message.ENTITY_MESSAGE_LABEL%
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    viewinfo.type_id
                , 'entity_id':  viewinfo.src_entity_id
                })
            return self.error(
                dict(self.error404values(),
                    message=message.ENTITY_DOES_NOT_EXIST%
                        { 'type_id': viewinfo.type_id
                        , 'id':      viewinfo.src_entity_id
                        , 'label':   entity_label
                        }
                    )
                )
        # log.info("@@ EntityEdit.get: ancestry %s/%s/%s"%(entity._parent._ancestorid, type_id, entity_id))
        orig_entity_coll_id = viewinfo.orig_typeinfo.get_ancestor_id(entity)
        viewinfo.set_orig_coll_id(orig_coll_id=orig_entity_coll_id)
        if viewinfo.check_authorization(action):
            return viewinfo.http_response

        # Set up values for rendered form response
        self.help_markdown = viewinfo.recordview.get(RDFS.CURIE.comment, None)
        entityvals  = get_entity_values(
            viewinfo.curr_typeinfo, entity,
            entity_id=viewinfo.use_entity_id,
            action=viewinfo.action
            )
        context_extra_values = (
            { 'request_url':            self.get_request_path()
            , 'url_type_id':            type_id
            , 'orig_id':                viewinfo.src_entity_id
            , 'orig_type':              type_id
            , 'orig_coll':              orig_entity_coll_id
            , 'edit_view_enable':       'disabled="disabled"'
            , 'default_view_enable':    'disabled="disabled"'
            , 'customize_view_enable':  'disabled="disabled"'
            , 'continuation_param':     viewinfo.get_continuation_param()
            })
        if viewinfo.authorizations['auth_config']:
            context_extra_values['edit_view_enable']      = ""
            context_extra_values['default_view_enable']   = ""
            context_extra_values['customize_view_enable'] = ""
        add_field = request.GET.get('add_field', None) #@@ redundant?
        try:
            response = self.form_render(
                viewinfo, entity, entityvals, context_extra_values, 
                add_field #@@ remove param
                )
        except Exception as e:
            # -- This should be redundant, but...
            log.error("Exception in GenericEntityEditView.get (%r)"%(e))
            log.error("".join(traceback.format_stack()))
            # --
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
        log.log(settings.TRACE_FIELD_VALUE, "  %s"%(self.get_request_path()))
        # log.log(settings.TRACE_FIELD_VALUE,
        #     "  form data %r"%(request.POST)
        #     )
        if request.FILES:
            for f in request.FILES:
                log.info(
                    "  file upload %s: %s (%d bytes) %s"%
                    (f, request.FILES[f].name, request.FILES[f].size, 
                        request.FILES[f].content_type
                        )
                    )
        self.get_view_template(action, type_id, entity_id)
        action              = request.POST.get('action', action)
        view_id             = request.POST.get('view_id', view_id)
        viewinfo            = self.view_setup(
            action, coll_id, type_id, view_id, entity_id, request.POST.dict()
            )
        # Get key form data values
        # Except for entity_id, use values from URI when form does not supply a value
        # (entity_id may be autogenerated later)
        orig_entity_id      = request.POST.get('orig_id', entity_id)
        orig_entity_type_id = request.POST.get('orig_type', type_id)
        orig_entity_coll_id = request.POST.get('orig_coll', coll_id)
        curr_entity_type_id = extract_entity_id(request.POST.get('entity_type', type_id))
        curr_entity_id      = request.POST.get('entity_id', None)
        viewinfo.set_coll_type_entity_id(
            orig_coll_id=orig_entity_coll_id,
            orig_type_id=orig_entity_type_id, orig_entity_id=orig_entity_id,
            curr_type_id=curr_entity_type_id, curr_entity_id=curr_entity_id
            )
        viewinfo.check_authorization(action)
        if viewinfo.http_response:
            return viewinfo.http_response
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        typeinfo        = viewinfo.curr_typeinfo
        context_extra_values = (
            { 'request_url':        self.get_request_path()
            , 'url_type_id':        type_id
            , 'orig_id':            orig_entity_id
            , 'orig_type':          orig_entity_type_id
            , 'orig_coll':          orig_entity_coll_id
            , 'save_id':            viewinfo.curr_entity_id
            , 'save_type':          viewinfo.curr_type_id
            , 'save_coll':          viewinfo.coll_id
            , 'continuation_param': viewinfo.get_continuation_param()
            })
        message_vals = dict(context_extra_values, id=entity_id, type_id=type_id, coll_id=coll_id)
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
        #@@TODO: this should be redundant - create as-needed, not before
        #         as of 2014-11-07, removing this causes test failures
        if not typeinfo.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(viewinfo.collection, typeinfo.entityparent.get_id(), {})
        #@@
        try:
            response = self.form_response(viewinfo, context_extra_values)
        except Exception as e:
            # -- This should be redundant, but...
            log.error("Exception in GenericEntityEditView.post (%r)"%(e))
            log.error("".join(traceback.format_stack()))
            # --
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
        #@@ self.collection_view_url      = self.get_collection_view_url(coll_id)
        self.default_continuation_url = self.view_uri(
            "AnnalistEntityDefaultListType", coll_id=coll_id, type_id=type_id
            )
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_request_type_info(type_id)
        viewinfo.get_view_info(viewinfo.get_view_id(type_id, view_id))
        viewinfo.get_entity_info(action, entity_id)
        # viewinfo.get_entity_data()
        # viewinfo.check_authorization(action)
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

        'params', if supplied, is a dictionary of additional query parameters to be added
        to the resulting URI.

        If the entity has been renamed on the submitted form, this is taken into account
        when re-displaying.
        """
        view_uri_params = (
            { 'coll_id':    viewinfo.coll_id
            , 'type_id':    viewinfo.curr_type_id
            , 'entity_id':  viewinfo.curr_entity_id or viewinfo.orig_entity_id
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
        entitymap = EntityValueMap(baseentityvaluemap)
        # log.debug(
        #     "GenericEntityEditView.get_view_entityvaluemap entityview: %r"%
        #     viewinfo.recordview.get_values()
        #     )
        view_fields  = viewinfo.recordview.get_values()[ANNAL.CURIE.view_fields]
        fieldlistmap = FieldListValueMap('fields',
            viewinfo.collection, view_fields,
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
        context_extra_values.update(
            { 'continuation_url':   viewinfo.get_continuation_url() or ""
            , 'view_choices':       self.get_view_choices_field(viewinfo)
            })
        entityvals   = viewinfo.curr_typeinfo.get_entity_implied_values(entityvals)
        form_context = entityvaluemap.map_value_to_context(entityvals, **context_extra_values)
        form_context.update(viewinfo.context_data(entity_label=entityvals.get(RDFS.CURIE.label, None)))
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
            if entityformvals[k] is not None:
                if not is_previous_upload(orig_entityvals, k):
                    upd_entityvals[k] = entityformvals[k]
        # log.info("orig entity_values %r"%(entity_values,))
        return upd_entityvals

    def form_render(self, viewinfo, entity, entityvals, context_extra_values, add_field):
        #@@ remove add_field?
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
        #   There is a test case that depends on this logic:
        #     annalist.tests.test_recordview.RecordViewEditViewTest.test_get_recordview_edit_add_field
        if add_field:
            add_field_desc = self.find_repeat_id(entityvaluemap, add_field)
            if add_field_desc:
                # Add empty fields per named repeat group
                self.add_entity_field(add_field_desc, entity)
        #@@
        viewcontext = self.get_form_display_context(
            viewinfo, entityvaluemap, entityvals, **context_extra_values
            )
        # log.info("form_render.viewcontext['fields'] %r"%(viewcontext['fields'],))        
        # Generate and return form data
        entity_baseurl = (
            viewinfo.reqhost + 
            viewinfo.get_src_entity_resource_url("")
            )
        entity_json_url   = urlparse.urljoin(entity_baseurl, viewinfo.get_entity_data_ref())
        entity_turtle_url = urlparse.urljoin(entity_baseurl, viewinfo.get_entity_turtle_ref())
        entity_links = [
            { "rel": "canonical"
            , "ref": entity_baseurl
            }]
        return (
            self.render_html(viewcontext, self.formtemplate, links=entity_links)
            or 
            self.redirect_json(entity_json_url, links=entity_links)
            or
            self.redirect_turtle(entity_turtle_url, links=entity_links)
            or
            self.error(self.error406values())
            )

    def form_re_render(self, responseinfo,
            viewinfo, entityvaluemap, entityvals, context_extra_values={}, 
            error_head=None, error_message=None):
        """
        Returns response info object with HTTP response that is a re-rendering of the current form 
        with current values and error message displayed.
        """
        #@@ viewinfo.reset_info_messages()
        form_context = self.get_form_display_context(
            viewinfo, entityvaluemap, entityvals, **context_extra_values
            )
        # log.info("********\nform_context %r"%form_context)
        form_context['info_head']     = None
        form_context['info_message']  = None
        form_context['error_head']    = error_head
        form_context['error_message'] = error_message
        if error_message:
            responseinfo.set_response_error(error_head, error_message)
        responseinfo.set_http_response(
            self.render_html(form_context, self.formtemplate)
            )
        if not responseinfo.has_http_response():
            errorvalues   = self.error406values()
            http_response = self.error(errorvalues)
            responseinfo.set_response_error(
                "%(status)03d: %(reason)s"%errorvalues,
                errorvalues.message
                )
        return responseinfo

        # @@@@@@@@
        # responseinfo.set_http_response(
        #     self.render_html(form_context, self.formtemplate) or 
        #     self.error(self.error406values())
        #     )
        # @@@@@@@@
        # return (
        #     self.render_html(form_context, self.formtemplate) or 
        #     self.error(self.error406values())
        #     )

    # @@TODO: refactor form_response to separate methods for each action
    #         form_response should handle initial checking and dispatching.
    #         The refactoring should attempt to separate methods that use the
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
        typeinfo     = viewinfo.curr_typeinfo
        messages     = viewinfo.type_messages
        orig_entity  = self.get_entity(viewinfo.orig_entity_id, typeinfo, viewinfo.action)
        # log.info("orig_entity %r"%(orig_entity.get_values(),))
        try:
            #@@TODO:  when current display is "view" (not edit), there are no form values
            #         to be saved.  Is this redundant?  Currently, it works because logic
            #         uses existing values where new ones are not provided.  But there
            #         are some unexpected warnings generated by 'decode' for fields not 
            #         present (e.g., user permisisons/TokenSet).
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
            # log.info("save: continuation_url '%s'"%(viewinfo.get_continuation_next()))
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
                    , 'entity_id':  viewinfo.curr_entity_id or viewinfo.orig_entity_id
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

        # Make the current view default for the current collection.
        if "default_view" in form_data:
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            if not responseinfo.has_http_response():
                #@@
                # auth_check = self.form_action_auth("config", viewinfo.collection, CONFIG_PERMISSIONS)
                #@@
                auth_check = viewinfo.check_authorization("config")
                if auth_check:
                    return auth_check
                viewinfo.collection.set_default_view(
                    view_id=viewinfo.view_id, type_id=viewinfo.orig_type_id, entity_id=viewinfo.orig_entity_id
                    )
                action = "list"
                msg    = (message.DEFAULT_VIEW_UPDATED%
                    { 'coll_id':   viewinfo.coll_id
                    , 'view_id':   viewinfo.view_id
                    , 'type_id':   viewinfo.orig_type_id
                    , 'entity_id': viewinfo.orig_entity_id
                    })
                redirect_uri = (
                    uri_with_params(
                        self.get_request_path(), 
                        self.info_params(msg),
                        viewinfo.get_continuation_url_dict()
                        )
                    )
                responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))
            return responseinfo.get_http_response()

        # Display "customize" page (collection edit view)
        if "customize" in form_data:
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            if not responseinfo.has_http_response():
                responseinfo.set_http_response(
                    viewinfo.check_authorization("config")
                    #@@
                    # self.form_action_auth("config", viewinfo.collection, CONFIG_PERMISSIONS)
                    #@@
                    )
            if not responseinfo.has_http_response():
                cont_here = viewinfo.get_continuation_here(
                    base_here=self.view_uri(
                        "AnnalistEntityEditView", 
                        coll_id=viewinfo.coll_id,
                        view_id=viewinfo.view_id,
                        type_id=viewinfo.curr_type_id,
                        entity_id=viewinfo.curr_entity_id or viewinfo.orig_entity_id,
                        action=self.uri_action
                        )
                    )
                redirect_uri = (
                    uri_with_params(
                        self.view_uri(
                            "AnnalistCollectionEditView", 
                            coll_id=viewinfo.coll_id
                            ),
                        {'continuation_url': cont_here}
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
                { 'type_id':  entitytypeinfo.TYPE_ID
                , 'view_id':  "Type_view"
                }
            , 'new_view':
                { 'type_id':  entitytypeinfo.VIEW_ID
                , 'view_id':  "View_view"
                }
            , 'new_field':
                { 'type_id':  entitytypeinfo.FIELD_ID
                , 'view_id':  "Field_view"
                }
            , 'new_group':
                { 'type_id':  entitytypeinfo.GROUP_ID
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
            if not valid_id(new_type_id):
                # Report problem with field definition...
                err_msg = message.NO_REFER_TO_TYPE%new_enum
                log.info(err_msg)
                self.form_re_render(responseinfo,
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=message.CREATE_FIELD_ENTITY_ERROR,
                    error_message=err_msg
                    )
                return responseinfo.get_http_response()
            new_typeinfo = EntityTypeInfo(
                viewinfo.collection, new_type_id
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
                    viewinfo.collection, edit_type_id
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
                type_id=entitytypeinfo.VIEW_ID,
                entity_id=viewinfo.view_id,
                action=self.uri_action
                )
            add_field_param = (
                {"add_field": "View_fields"} if ('add_view_field' in form_data) else {}
                )
            # log.info("Open view: entity_id: %s"%viewinfo.curr_entity_id)
            auth_req = "view" if viewinfo.action == "view" else "config"
            responseinfo = self.save_invoke_edit_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                view_edit_uri_base, auth_req,
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
                self.form_re_render(responseinfo,
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['remove_field_error'],
                    error_message=messages['no_field_selected']
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
                self.form_re_render(responseinfo,
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['move_field_error'],
                    error_message=messages['no_field_selected']
                    )
            return self.form_refresh_on_success(viewinfo, responseinfo)

        # Task buttons
        #
        # These are buttons on selected displays that are used to invoke a complex 
        # task using information from the current view.
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


        Decision table:

        Action  | coll_id | type_id | entity_id | Target  | Result
                | same?   | same?   | same?     | exists? |
        ------------------------------------------------------------
        View    |    --   |    --   |     --    |    --   | Do nothing
                |         |         |           |         |
        New     |    --   |    --   |     --    |     Y   | Error
                |    --   |    --   |     --    |     N   | Save_new
                |         |         |           |         |
        Copy    |     Y   |     Y   |      Y    |    --   | Error
                |    --   |    --   |     --    |     Y   | Error
                |    --   |    --   |     --    |     N   | Save_copy
                |         |         |           |         |
                |         |         |           |         |
        Edit    |     Y   |     Y   |      Y    |     N   | Error
                |     Y   |     Y   |      Y    |     Y   | Save_update
                |         |         |           |         |
                |     Y   |     Y   |      N    |     Y   | Error
                |     Y   |     Y   |      N    |     N   | Save_rename *1
                |         |         |           |         |
                |     Y   |     N   |     --    |     Y   | Error
                |     Y   |     N   |     --    |     N   | Save_rename_type
                |         |         |           |         |
                |     N   |    --   |     --    |     Y   | Error (shouldn't happen)
                |     N   |    --   |     --    |     N   | Save_copy

        *1 special case when type is '_type' or '_coll'


        viewinfo        contains display context for the form which is being processed
        entityvaluemap  a list of field descriptions that are used to map values between
                        the edited entity and the form display, including references to
                        field descriptions that control how values are rendered.
        entityformvals  a dictionary of entity values extracted from the submitted form; 
                        these are used either for redisplaying the form if there is an 
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
        value if the save completes successfully, otherwise an HTTP response object 
        that reports the nature of the problem.
        """
        if responseinfo is None:
            raise ValueError("entityedit.save_entity expects ResponseInfo object")
        if responseinfo.has_http_response():
            return responseinfo
        save_entity_id = viewinfo.curr_entity_id
        save_type_id   = viewinfo.curr_type_id
        save_coll_id   = viewinfo.coll_id
        orig_entity_id = viewinfo.orig_entity_id
        orig_type_id   = viewinfo.orig_type_id
        orig_coll_id   = viewinfo.orig_coll_id
        action         = viewinfo.action
        # log.info("save_entity: formvals: %r, import_field %r"%(entityformvals, import_field))
        # log.info(
        #     "save_entity_id %s, save_type_id %s, orig_entity_id %s, orig_type_id %s, action %s"%
        #     (save_entity_id, save_type_id, orig_entity_id, orig_type_id, action)
        #     )
        orig_typeinfo  = viewinfo.orig_typeinfo
        save_typeinfo  = viewinfo.curr_typeinfo
        messages       = viewinfo.type_messages
        if self.uri_action == "view":
            # This is a view operation: nothing to save
            return responseinfo
        if not action in ["new", "copy", "edit"]:
            log.warning("'Save' operation for action '%s'"%(action))
            # Check "edit" authorization to continue
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
        # If no id field in form, use original or allocated id
        # Assumes Id value of None corresponds to no form field
        if save_entity_id is None:
            save_entity_id = orig_entity_id
        entity_renamed = (
            ( action == "edit" ) and
            ( (save_entity_id != orig_entity_id) or 
              (save_type_id   != orig_type_id  ) or
              (save_coll_id   != orig_coll_id  ) )
            )
        # log.info("@@ Renamed: %s"%entity_renamed)

        # @@TODO: factor out repeated re-rendering logic

        # Check for valid id and type to be saved
        if not valid_id(save_entity_id):
            log.debug("form_response: save_entity_id not valid ('%s')"%save_entity_id)
            return self.form_re_render(responseinfo,
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        if not valid_id(save_type_id):
            log.debug("form_response: save_type_id not valid_id('%s')"%save_type_id)
            return self.form_re_render(responseinfo,
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                error_head=messages['entity_type_heading'],
                error_message=messages['entity_type_invalid']
                )

        # Check original parent exists (still)
        if (action != "new") and (not orig_typeinfo.parent_exists()):
            log.warning("save_entity: original entity parent does not exist")
            return self.form_re_render(responseinfo,
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )

        #@@@@ TO BE REMOVED
        # Check existence of entity to save according to action performed
        if (action in ["new", "copy"]) or entity_renamed:
            if not viewinfo.saved():
                # First save - check for existence
                if save_typeinfo.entity_exists(save_entity_id):
                    log.warning(
                        "Entity exists: action %s %s/%s, orig %s/%s"%
                            (action, save_type_id, save_entity_id, orig_type_id, orig_entity_id)
                        )
                    return self.form_re_render(responseinfo,
                        viewinfo, entityvaluemap, entityformvals, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_exists']
                        )
        else:
            if not orig_typeinfo.entity_exists(save_entity_id, altscope="all"):
                # This shouldn't happen, but just in case...
                log.warning("Expected %s/%s not found; action %s, entity_renamed %r"%
                      (save_type_id, save_entity_id, action, entity_renamed)
                    )
                return self.form_re_render(responseinfo,
                    viewinfo, entityvaluemap, entityformvals, context_extra_values,
                    error_head=messages['entity_heading'],
                    error_message=messages['entity_not_exists']
                    )
        #@@@@

        if action == "new":
            err_vals, entity_values = self.save_new(viewinfo, 
                save_typeinfo, save_entity_id, entityformvals
                )            
        elif action == "copy":
            #@@TODO merge values and force new URI - see above
            err_vals, entity_values = self.save_copy(viewinfo, 
                save_typeinfo, save_entity_id, 
                orig_typeinfo, orig_entity_id, entityformvals
                )
        else: # action == "edit":
            if save_coll_id != orig_coll_id:
                err_vals, entity_values = self.save_copy(viewinfo, 
                    save_typeinfo, save_entity_id, 
                    orig_typeinfo, orig_entity_id, entityformvals
                    )
            elif save_type_id != orig_type_id:
                if entitytypeinfo.TYPE_ID in [save_type_id, orig_type_id]:
                    log.warning(
                        "EntityEdit.rename_entity_type: attempt to change type of type record"
                        )
                    err_vals      = (message.INVALID_OPERATION_ATTEMPTED, message.INVALID_TYPE_CHANGE)
                    entity_values = None
                else:
                    # Entity renamed to new type
                    err_vals, entity_values = self.save_rename(viewinfo, 
                        save_typeinfo, save_entity_id, 
                        orig_typeinfo, orig_entity_id, entityformvals
                        )
            elif save_entity_id != orig_entity_id:
                # Non -collection or -type record rename
                err_vals, entity_values = self.save_rename(viewinfo, 
                    save_typeinfo, save_entity_id, 
                    orig_typeinfo, orig_entity_id, 
                    entityformvals
                    )
            else:
                err_vals, entity_values = self.save_update(viewinfo, 
                    save_typeinfo, save_entity_id, entityformvals
                    )

        # Save any imported resource or uploaded files
        if not err_vals:
            responseinfo = self.save_uploaded_files(
                save_entity_id, save_typeinfo,
                entityvaluemap, entity_values,
                self.request.FILES,
                responseinfo
                )
        if not err_vals and import_field is not None:
            responseinfo = self.save_linked_resource(
                save_entity_id, save_typeinfo,
                entityvaluemap, entity_values,
                import_field,
                responseinfo
                )
            # log.info("save_linked_resource: responseinfo %r"%responseinfo)
            # log.info("save_linked_resource: entity_values %r"%entity_values)
        if responseinfo.is_updated():
            err_vals = self.create_update_entity(save_typeinfo, save_entity_id, entity_values)

        # Finish up
        if err_vals:
            log.warning("err_vals %r"%(err_vals,))
            return self.form_re_render(responseinfo,
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                error_head=err_vals[0],
                error_message=err_vals[1]
                )
        log.info("Saved %s/%s"%(save_type_id, save_entity_id))
        viewinfo.saved(is_saved=True)
        viewinfo.update_coll_version()
        return responseinfo

    def save_assemble_values(self, action, viewinfo, 
        save_typeinfo, save_entity_id, 
        orig_typeinfo, orig_entity_id, entityformvals
        ):
        """
        Assemble updated values for storage
        
        Note: form data is applied as update to original entity data so that
        values not in view are preserved.  Use original entity values without 
        field aliases as basis for new value.

        Returns the merged entity values.
        """
        #@@TODO: eliminate action parameter
        if orig_typeinfo and orig_entity_id:
            orig_entity   = orig_typeinfo.get_entity(orig_entity_id, action)
            orig_values   = orig_entity.get_values() if orig_entity else {}
        else:
            orig_values = {}
        entity_values = self.merge_entity_form_values(orig_values, entityformvals)
        if action == "copy":
            # Force new URI on copy
            orig_uri = orig_values.get(ANNAL.CURIE.uri, None) 
            new_uri  = entity_values.get(ANNAL.CURIE.uri, None) 
            if new_uri == orig_uri:
                entity_values.pop(ANNAL.CURIE.uri, None)
        entity_values[ANNAL.CURIE.type_id] = save_typeinfo.get_type_id()
        entity_values[ANNAL.CURIE.type]    = save_typeinfo.get_type_uri()
        # Supply values for label and comment if not already provided or aliased
        entity_implied_vals = save_typeinfo.get_entity_implied_values(entity_values)
        entity_label        = entity_implied_vals.get(RDFS.CURIE.label, None)
        if not entity_label:
            entity_label = label_from_id(save_entity_id)
            entity_values[RDFS.CURIE.label] = entity_label
        if not entity_implied_vals.get(RDFS.CURIE.comment, None):
            entity_values[RDFS.CURIE.comment] = entity_label
        return entity_values

    def save_new(self, viewinfo, save_typeinfo, save_entity_id, entityformvals):
        """
        Save new entity

        Returns a pair (err_vals, entity_values), where:
            err_vals is None if the operation succeeds, or error details
                a pair of strings for the error message heading and body.
            entity_values is a copy of the data values that were saved.
        """
        # messages = viewinfo.type_messages
        err_vals = None
        if not viewinfo.saved():
            # First save - check for existence
            if save_typeinfo.entity_exists(save_entity_id):
                log.warning(
                    "Entity exists (new): %s/%s"%
                        (save_typeinfo.type_id, save_entity_id)
                    )
                err_vals = (
                    viewinfo.type_messages['entity_heading'],
                    viewinfo.type_messages['entity_exists']
                    )
        if not err_vals:
            entity_values = self.save_assemble_values("new", viewinfo, 
                save_typeinfo, save_entity_id, 
                None, None, entityformvals
                )
            err_vals = self.create_update_entity(save_typeinfo, save_entity_id, entity_values)
        return (err_vals, entityformvals)

    def save_copy(self, viewinfo, 
        save_typeinfo, save_entity_id, 
        orig_typeinfo, orig_entity_id, entityformvals
        ):
        """
        Save copy of entity.

        As well as saving the entity data, attachments are copied from the original
        to the new entity directory or container.

        Returns a pair (err_vals, entity_values), where:
            err_vals is None if the operation succeeds, or error details
                a pair of strings for the error message heading and body.
            entity_values is a copy of the data values that were saved.
        """
        err_vals      = None
        entity_values = None
        if not viewinfo.saved():
            # First save - check for existence
            if save_typeinfo.entity_exists(save_entity_id):
                log.warning(
                    "Entity exists (copy): %s/%s, orig %s/%s"%
                        (save_typeinfo.type_id, save_entity_id, orig_typeinfo.type_id, orig_entity_id)
                    )
                err_vals = (
                    viewinfo.type_messages['entity_heading'],
                    viewinfo.type_messages['entity_exists']
                    )
        if not err_vals:
            entity_values = self.save_assemble_values("copy", viewinfo, 
                save_typeinfo, save_entity_id, 
                orig_typeinfo, orig_entity_id, entityformvals
                )
            err_vals = self.copy_entity(
                orig_typeinfo, orig_entity_id, 
                save_typeinfo, save_entity_id, 
                entity_values
                )
        return (err_vals, entity_values)

    def save_rename(self, viewinfo, save_typeinfo, save_entity_id, orig_typeinfo, orig_entity_id, entityformvals):
        """
        Save renamed entity.

        Returns a pair (err_vals, entity_values), where:
            err_vals is None if the operation succeeds, or error details
                a pair of strings for the error message heading and body.
            entity_values is a copy of the data values that were saved.
        """
        err_vals      = None
        entity_values = None
        if not viewinfo.saved():
            # First save - check for existence
            if save_typeinfo.entity_exists(save_entity_id):
                log.warning(
                    "Entity exists (rename): %s/%s, orig %s/%s"%
                        (save_typeinfo.type_id, save_entity_id, orig_typeinfo.type_id, orig_entity_id)
                    )
                err_vals = (
                    viewinfo.type_messages['entity_heading'],
                    viewinfo.type_messages['entity_exists']
                    )
        if not err_vals:
            save_type_id  = viewinfo.curr_type_id
            orig_type_id  = viewinfo.orig_type_id
            entity_values = self.save_assemble_values("edit", viewinfo, 
                save_typeinfo, save_entity_id, 
                orig_typeinfo, orig_entity_id, entityformvals
                )
            if entitytypeinfo.TYPE_ID in [save_type_id, orig_type_id]:
                # Type renamed
                # log.info(
                #     "@@ rename_entity_type %s/%s to %s/%s"%
                #     ( save_typeinfo.get_type_id(), orig_entity_id, 
                #       save_typeinfo.get_type_id(), save_entity_id) 
                #     )
                err_vals = self.rename_entity_type(
                    viewinfo, 
                    orig_typeinfo, orig_entity_id, 
                    save_typeinfo, save_entity_id, entity_values
                    )
            elif entitytypeinfo.COLL_ID in [save_type_id, orig_type_id]:
                # Collection renamed
                err_vals = self.rename_collection(
                    orig_typeinfo, orig_entity_id, 
                    save_typeinfo, save_entity_id, entity_values
                    )
            else:
                err_vals = self.rename_entity(
                    orig_typeinfo, orig_entity_id, 
                    save_typeinfo, save_entity_id, 
                    entity_values
                    )
        if not err_vals:
            # Update references to renamed entity in continuation URL
            viewinfo.update_continuation_url(
                old_type_id=orig_type_id, old_entity_id=orig_entity_id,
                new_type_id=save_type_id, new_entity_id=save_entity_id
                )
        return (err_vals, entity_values)

    def save_update(self, viewinfo, save_typeinfo, save_entity_id, entityformvals):
        """
        Save updated entity.

        Returns a pair (err_vals, entity_values), where:
            err_vals is None if the operation succeeds, or error details
                a pair of strings for the error message heading and body.
            entity_values is a copy of the data values that were saved.
        """
        err_vals      = None
        entity_values = None
        if not save_typeinfo.entity_exists(save_entity_id, altscope=None):
            # This shouldn't happen, but just in case (e.g. bad URL hacking) ...
            log.warning("save_update: expected entity %s/%s not found"%
                  (save_typeinfo.type_id, save_entity_id)
                )
            err_vals = (
                viewinfo.type_messages['entity_heading'],
                viewinfo.type_messages['entity_not_exists']
                )
        if not err_vals:
            entity_values = self.save_assemble_values("edit", viewinfo, 
                save_typeinfo, save_entity_id, 
                save_typeinfo, save_entity_id, entityformvals
                )
            err_vals = self.create_update_entity(save_typeinfo, save_entity_id, entity_values)
        return (err_vals, entity_values)

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
            value_type    = field_desc.get('field_value_type', ANNAL.CURIE.Unknown_type)
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

        # log.info("@@ save_uploaded_files, entityvals: %r"%(entityvals,))
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
                value_type    = import_field.get('field_value_type', ANNAL.CURIE.Unknown_type)
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

        # log.info("@@ save_linked_resource, entityvals: %r"%(entityvals,))
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

        Returns None if the operation succeeds, or error details in the form of 
        a pair of values for the error message heading and the error message body.
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

        Returns None if the operation succeeds, or error details in the form of 
        a pair of values for the error message heading and the error message body.
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
            viewinfo.collection, old_type_id
            )
        dst_typeinfo = EntityTypeInfo(
            viewinfo.collection, new_type_id, 
            create_typedata=True
            )
        if new_typeinfo.entity_exists(new_type_id):
            # Enumerate type instance records and move to new type
            remove_OK = True
            for d in src_typeinfo.enum_entities():
                data_id   = d.get_id()
                data_vals = d.get_values()
                data_vals[ANNAL.CURIE.type_id] = new_type_id
                data_vals[ANNAL.CURIE.type]    = dst_typeinfo.get_type_uri()
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

    def rename_collection(self,
            old_typeinfo, old_entity_id, 
            new_typeinfo, new_entity_id, entity_values
            ):
        """
        Save a renamed collection.

        This involves renaming the collection directory and updating 
        the collection metadata.

        Returns None if the operation succeeds, or error message
        details to be displayed as a pair of values for the message 
        heading and the message body.
        """
        log.info("rename_collection old: %s, new: %s, vals: %r"%(old_entity_id, new_entity_id, entity_values))
        new_typeinfo.rename_entity(new_entity_id, old_typeinfo, old_entity_id)
        new_typeinfo.create_entity(new_entity_id, entity_values)
        if not new_typeinfo.entity_exists(new_entity_id):    # Precautionary
            log.warning(
                "EntityEdit.rename_collection: Failed to rename collection %s/%s to %s/%s"%
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
        # log.info(
        #     "rename_entity old: %s/%s, new: %s/%s, vals: %r"%
        #       ( old_typeinfo.type_id, old_entity_id, 
        #         new_typeinfo.type_id, new_entity_id, 
        #         entity_values
        #       )
        #     )
        # _new_entity just constructs a new object of the appropriate class
        old_entity = old_typeinfo._new_entity(old_entity_id)
        new_entity = new_typeinfo.create_entity(new_entity_id, entity_values)
        msg        = new_entity._copy_entity_files(old_entity)
        if msg:
            return (message.SYSTEM_ERROR,  msg)
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
                  ( old_typeinfo.type_id, old_entity_id, 
                    new_typeinfo.type_id, new_entity_id
                  )
                )
        return None

    def copy_entity(self,
            old_typeinfo, old_entity_id, 
            new_typeinfo, new_entity_id, entity_values
            ):
        """
        Copy an entity, including any attachments.

        (Unlike rename, entities are just copied without affecting any existing
        entities of that type.

        Returns None if the operation succeeds, or error details in the form of 
        a pair of values for the error message heading and the error message body.
        """
        log.info(
            "copy_entity old: %s/%s, new: %s/%s"%
              ( old_typeinfo.type_id, old_entity_id, 
                new_typeinfo.type_id, new_entity_id
              )
            )
        # log.debug("copy_entity vals: %r"%(entity_values,))
        # _new_entity just constructs a new object of the appropriate class
        old_entity = old_typeinfo._new_entity(old_entity_id)
        new_entity = new_typeinfo.create_entity(new_entity_id, entity_values)
        msg        = new_entity._copy_entity_files(old_entity)
        if msg:
            return (message.SYSTEM_ERROR,  msg)
        if not new_typeinfo.entity_exists(new_entity_id):
            log.warning(
                "EntityEdit.copy_entity: failed to copy entity %s/%s to %s/%s"%
                  ( old_typeinfo.type_id, old_entity_id, 
                    new_typeinfo.type_id, new_entity_id
                  )
                )
            return (
                message.SYSTEM_ERROR, 
                message.COPY_ENTITY_FAILED%
                  ( old_typeinfo.type_id, old_entity_id, 
                    new_typeinfo.type_id, new_entity_id
                  )
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
                        these are used either for redisplaying the form if there is an 
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
        # NOTE: see also find_task_button and annal:edit_task_buttons in correspnding view data

        # Tasks invoked without saving current entity
        # If no response generated yet, save entity
        responseinfo = self.save_entity(
            viewinfo, entityvaluemap, entityformvals, context_extra_values,
            responseinfo=responseinfo
            )
        if responseinfo.is_response_error():
            return responseinfo

        # Tasks invoked after current entity has been saved (if required)

        #@@------------------------------------------------------
        #@@TODO: drive this logic from a stored _task description
        #@@------------------------------------------------------

        if task_id == entitytypeinfo.TASK_ID+"/Define_view_list":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals
            base_id        = entityformvals[ANNAL.CURIE.id]
            type_entity_id = entitytypeinfo.TYPE_ID+"/"+base_id
            type_label     = entityformvals[RDFS.CURIE.label]
            type_uri       = entityformvals.get(ANNAL.CURIE.uri, None)
            prev_view_id   = entityformvals.get(ANNAL.CURIE.type_view, None)
            prev_list_id   = entityformvals.get(ANNAL.CURIE.type_list, None)
            view_entity_id = entitytypeinfo.VIEW_ID+"/"+base_id+layout.SUFFIX_VIEW
            list_entity_id = entitytypeinfo.LIST_ID+"/"+base_id+layout.SUFFIX_LIST
            list_selector  = "'%s' in [@type]"%(type_uri) if type_uri else "ALL"
            if not (prev_view_id or prev_list_id):
                error_params = self.error_params(
                    message.NO_VIEW_OR_LIST_SELECTED
                    )
                return responseinfo.set_http_response(
                    HttpResponseRedirect(self.get_form_refresh_uri(viewinfo, params=error_params))
                    )
            # log.debug("task/Define_view_list prev_view_id %s"%(prev_view_id,))
            # log.debug("task/Define_view_list prev_list_id %s"%(prev_list_id,))
            # Set up view details (other defaults from sitedata '_initial_values')
            type_values = { "type_id": base_id, "type_label": type_label }
            if prev_view_id:
                view_typeinfo = EntityTypeInfo(
                    viewinfo.collection, entitytypeinfo.VIEW_ID
                    )
                view_entity   = view_typeinfo.get_copy_entity(view_entity_id, prev_view_id)
                view_entity.setdefault(RDFS.CURIE.label,   
                    message.TYPE_VIEW_LABEL%type_values
                    )
                view_entity.setdefault(RDFS.CURIE.comment, 
                    message.TYPE_VIEW_COMMENT%type_values
                    )
                view_entity[ANNAL.CURIE.view_entity_type] = type_uri
                view_entity._save()
            # Set up list details (other defaults from sitedata '_initial_values')
            if prev_list_id:
                list_typeinfo = EntityTypeInfo(
                    viewinfo.collection, entitytypeinfo.LIST_ID
                    )
                list_entity   = list_typeinfo.get_copy_entity(list_entity_id, prev_list_id)
                list_entity.setdefault(RDFS.CURIE.label,   
                    message.TYPE_LIST_LABEL%type_values
                    )
                list_entity.setdefault(RDFS.CURIE.comment, 
                    message.TYPE_LIST_COMMENT%type_values
                    )
                list_entity[ANNAL.CURIE.display_type] = "List"
                list_entity[ANNAL.CURIE.default_view] = view_entity_id
                list_entity[ANNAL.CURIE.default_type] = type_entity_id
                list_entity[ANNAL.CURIE.list_entity_type]     = type_uri
                list_entity[ANNAL.CURIE.list_entity_selector] = list_selector
                list_entity._save()
            # Update view, list values in type record, and save again
            if prev_view_id:
                entityformvals[ANNAL.CURIE.type_view] = view_entity_id
            if prev_list_id:
                entityformvals[ANNAL.CURIE.type_list] = list_entity_id
            responseinfo = self.save_entity(
                viewinfo, entityvaluemap, entityformvals, context_extra_values,
                responseinfo=responseinfo
                )
            info_values = self.info_params(
                message.TASK_CREATE_VIEW_LIST%{'id': base_id, 'label': type_label}
                )
            redirect_uri = self.get_form_refresh_uri(viewinfo, params=info_values)
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))

        elif task_id == entitytypeinfo.TASK_ID+"/Define_subtype":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals
            type_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.TYPE_ID
                )
            base_type_id        = entityformvals[ANNAL.CURIE.id] or viewinfo.use_entity_id
            base_type_entity    = type_typeinfo.get_entity(base_type_id)
            base_type_label     = base_type_entity.get(RDFS.CURIE.label, base_type_id)
            base_type_uri       = base_type_entity.get(ANNAL.CURIE.uri,  "_coll:"+base_type_id)
            base_view_entity_id = base_type_entity.get(ANNAL.CURIE.type_view, "Default_view")
            base_list_entity_id = base_type_entity.get(ANNAL.CURIE.type_list, "Default_list")
            # Set up subtype details
            sub_type_id         = base_type_id+layout.SUFFIX_SUBTYPE
            sub_type_entity_id  = entitytypeinfo.TYPE_ID+"/"+sub_type_id
            sub_type_uri        = base_type_uri and base_type_uri + layout.SUFFIX_SUBTYPE
            sub_type_label      = "@@subtype of " + base_type_label
            sub_type_values     = (
                { "type_id":          sub_type_id
                , "type_uri":           sub_type_uri
                , "type_label":         sub_type_label
                , "type_ref":           sub_type_entity_id
                , "type_view_id":       base_view_entity_id
                , "type_list_id":       base_list_entity_id
                , "base_type_id":       base_type_id
                , "base_type_label":    base_type_label
                })
            sub_type_comment    = message.SUBTYPE_COMMENT%sub_type_values
            sub_type_supertypes = [{ "@id": base_type_uri }]
            # Create subtype record, and save
            type_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.TYPE_ID
                )
            sub_type_entity = type_typeinfo.get_create_entity(sub_type_entity_id)
            sub_type_entity[RDFS.CURIE.label]           = sub_type_label
            sub_type_entity[RDFS.CURIE.comment]         = sub_type_comment
            sub_type_entity[ANNAL.CURIE.uri]            = sub_type_uri
            sub_type_entity[ANNAL.CURIE.supertype_uri]  = sub_type_supertypes           
            sub_type_entity[ANNAL.CURIE.type_view]      = base_view_entity_id
            sub_type_entity[ANNAL.CURIE.type_list]      = base_list_entity_id
            sub_type_entity._save()
            # Construct response that redirects to view new type entity with message
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entitytypeinfo.TYPE_ID
                , 'view_id':    "Type_view"
                , 'entity_id':  sub_type_id
                , 'action':     "edit"
                })
            info_values = self.info_params(
                message.TASK_CREATE_SUBTYPE%{'id': sub_type_id, 'label': sub_type_label}
                )
            more_uri_params = viewinfo.get_continuation_url_dict()
            more_uri_params.update(info_values)
            redirect_uri = (
                uri_with_params(
                    self.view_uri("AnnalistEntityEditView", **view_uri_params),
                    more_uri_params
                    )
                )
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))

        elif task_id == entitytypeinfo.TASK_ID+"/Define_subproperty_field":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals
            field_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.FIELD_ID
                )
            base_field_id        = entityformvals[ANNAL.CURIE.id] or viewinfo.use_entity_id
            base_field_entity    = field_typeinfo.get_entity(base_field_id)
            base_field_label     = base_field_entity.get(RDFS.CURIE.label, base_field_id)
            base_field_prop_uri  = base_field_entity.get(ANNAL.CURIE.property_uri,  "_coll:"+base_field_id)
            # Set up subtype details
            sub_field_id         = base_field_id+layout.SUFFIX_SUBPROPERTY
            sub_field_entity_id  = entitytypeinfo.FIELD_ID+"/"+sub_field_id
            sub_field_prop_uri   = base_field_prop_uri + layout.SUFFIX_SUBPROPERTY
            sub_field_values     = (
                { "field_id":          sub_field_id
                , "field_prop_uri":    sub_field_prop_uri
                , "field_ref":         sub_field_entity_id
                , "base_field_id":     base_field_id
                , "base_field_label":  base_field_label
                })
            sub_field_label                 = message.SUBFIELD_LABEL%sub_field_values
            sub_field_values["field_label"] = sub_field_label
            sub_field_comment               = message.SUBFIELD_COMMENT%sub_field_values
            sub_field_superprop_uris        = [{ "@id": base_field_prop_uri }]
            # Create subfield record, and save
            field_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.FIELD_ID
                )
            subfield_copy_fields = (
                [ ANNAL.CURIE.type_id
                , ANNAL.CURIE.field_render_type
                , ANNAL.CURIE.field_value_mode
                , ANNAL.CURIE.field_ref_type
                , ANNAL.CURIE.field_value_type
                , ANNAL.CURIE.field_entity_type
                , ANNAL.CURIE.field_placement
                , ANNAL.CURIE.default_value
                , ANNAL.CURIE.placeholder
                , ANNAL.CURIE.tooltip
                ])
            sub_field_entity = field_typeinfo.get_create_entity(sub_field_entity_id)
            for f in subfield_copy_fields:
                if f in base_field_entity:
                    sub_field_entity[f] = base_field_entity[f]
            sub_field_entity[RDFS.CURIE.label]              = sub_field_label
            sub_field_entity[RDFS.CURIE.comment]            = sub_field_comment
            sub_field_entity[ANNAL.CURIE.property_uri]      = sub_field_prop_uri
            sub_field_entity[ANNAL.CURIE.superproperty_uri] = sub_field_superprop_uris
            sub_field_entity._save()
            # Construct response that redirects to view new field entity with message
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entitytypeinfo.FIELD_ID
                , 'view_id':    "Field_view"
                , 'entity_id':  sub_field_id
                , 'action':     "edit"
                })
            info_values = self.info_params(
                message.TASK_CREATE_SUBFIELD%
                  { 'id':       sub_field_id
                  , 'label':    sub_field_label
                  , 'base_uri': base_field_prop_uri
                  }
                )
            more_uri_params = viewinfo.get_continuation_url_dict()
            more_uri_params.update(info_values)
            redirect_uri = (
                uri_with_params(
                    self.view_uri("AnnalistEntityEditView", **view_uri_params),
                    more_uri_params
                    )
                )
            responseinfo.set_http_response(HttpResponseRedirect(redirect_uri))

        elif task_id == entitytypeinfo.TASK_ID+"/Define_many_field":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals (form is a field description)
            field_entity_id          = entityformvals[ANNAL.CURIE.id]
            field_label              = entityformvals[RDFS.CURIE.label]
            field_entity_type        = entityformvals[ANNAL.CURIE.field_entity_type] # domain
            field_property_uri       = entityformvals[ANNAL.CURIE.property_uri]
            field_value_type         = entityformvals[ANNAL.CURIE.field_value_type]  # range
            repeat_field_id          = field_entity_id    + layout.SUFFIX_REPEAT
            repeat_property_uri      = field_property_uri
            repeat_entity_type       = (
                field_entity_type if field_entity_type != ANNAL.CURIE.Field_list 
                else ""
                )
            repeat_value_type        = repeat_entity_type
            field_params = { "field_id": field_entity_id, "field_label": field_label }
            repeat_field_label       = message.MANY_FIELD_LABEL%field_params
            repeat_field_comment     = message.MANY_FIELD_COMMENT%field_params
            repeat_field_placeholder = message.MANY_FIELD_PLACEHOLDER%field_params
            repeat_field_add         = message.MANY_FIELD_ADD%field_params
            repeat_field_delete      = message.MANY_FIELD_DELETE%field_params
            # Create repeat-field referencing original field
            field_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.FIELD_ID
                )
            repeat_field_entity   = field_typeinfo.get_create_entity(repeat_field_id)
            repeat_field_entity[ANNAL.CURIE.field_render_type] = "Group_Set_Row"
            repeat_field_entity[ANNAL.CURIE.field_value_mode]  = "Value_direct"
            if not repeat_field_entity.get(ANNAL.CURIE.field_fields, None):
                repeat_field_entity[ANNAL.CURIE.field_fields] = (
                    [ { ANNAL.CURIE.field_id:           entitytypeinfo.FIELD_ID+"/"+field_entity_id
                      , ANNAL.CURIE.property_uri:       "@id"
                      , ANNAL.CURIE.field_placement:    "small:0,12"
                      }
                    ])
            repeat_field_entity.setdefault(RDFS.CURIE.label,                 repeat_field_label)
            repeat_field_entity.setdefault(RDFS.CURIE.comment,               repeat_field_comment)
            repeat_field_entity.setdefault(ANNAL.CURIE.placeholder,          repeat_field_placeholder)
            repeat_field_entity.setdefault(ANNAL.CURIE.property_uri,         repeat_property_uri)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_entity_type,    repeat_entity_type)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_value_type,     repeat_value_type)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_placement,      "small:0,12")
            repeat_field_entity.setdefault(ANNAL.CURIE.repeat_label_add,     repeat_field_add)
            repeat_field_entity.setdefault(ANNAL.CURIE.repeat_label_delete,  repeat_field_delete)
            repeat_field_entity._save()

            # Redisplay field view with message
            info_values = self.info_params(
                message.TASK_CREATE_MANY_VALUE_FIELD%
                  {'field_id': repeat_field_id, 'label': field_label}
                )
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entitytypeinfo.FIELD_ID
                , 'entity_id':  repeat_field_id
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

        elif task_id in [entitytypeinfo.TASK_ID+"/Define_repeat_field", entitytypeinfo.TASK_ID+"/Define_list_field"]:
        # elif task_id == entitytypeinfo.TASK_ID+"/Define_list_field":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals (form is a field description)
            field_entity_id          = entityformvals[ANNAL.CURIE.id]
            field_label              = entityformvals[RDFS.CURIE.label]
            field_entity_type        = entityformvals[ANNAL.CURIE.field_entity_type] # domain
            field_property_uri       = entityformvals[ANNAL.CURIE.property_uri]
            field_value_type         = entityformvals[ANNAL.CURIE.field_value_type]  # range
            repeat_field_id          = field_entity_id    + layout.SUFFIX_SEQUENCE
            repeat_property_uri      = field_property_uri + layout.SUFFIX_SEQUENCE_P
            repeat_entity_type       = (
                field_entity_type if field_entity_type != ANNAL.CURIE.Field_list 
                else ""
                )
            field_params = { "field_id": field_entity_id, "field_label": field_label }
            repeat_field_label       = message.LIST_FIELD_LABEL%field_params
            repeat_field_comment     = message.LIST_FIELD_COMMENT%field_params
            repeat_field_placeholder = message.LIST_FIELD_PLACEHOLDER%field_params
            repeat_field_add         = message.LIST_FIELD_ADD%field_params
            repeat_field_delete      = message.LIST_FIELD_DELETE%field_params
            # Create repeat-field referencing original
            field_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.FIELD_ID
                )
            repeat_field_entity   = field_typeinfo.get_create_entity(repeat_field_id)
            repeat_field_entity[ANNAL.CURIE.field_render_type] = "Group_Seq_Row"
            repeat_field_entity[ANNAL.CURIE.field_value_mode]  = "Value_direct"
            if not repeat_field_entity.get(ANNAL.CURIE.field_fields, None):
                repeat_field_entity[ANNAL.CURIE.field_fields] = (
                    [ { ANNAL.CURIE.field_id:           entitytypeinfo.FIELD_ID+"/"+field_entity_id
                      , ANNAL.CURIE.property_uri:       field_property_uri
                      , ANNAL.CURIE.field_placement:    "small:0,12"
                      }
                    ])
            repeat_field_entity.setdefault(RDFS.CURIE.label,                 repeat_field_label)
            repeat_field_entity.setdefault(RDFS.CURIE.comment,               repeat_field_comment)
            repeat_field_entity.setdefault(ANNAL.CURIE.placeholder,          repeat_field_placeholder)
            repeat_field_entity.setdefault(ANNAL.CURIE.property_uri,         repeat_property_uri)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_entity_type,    repeat_entity_type)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_value_type,     ANNAL.CURIE.Field_list)
            repeat_field_entity.setdefault(ANNAL.CURIE.field_placement,      "small:0,12")
            repeat_field_entity.setdefault(ANNAL.CURIE.repeat_label_add,     repeat_field_add)
            repeat_field_entity.setdefault(ANNAL.CURIE.repeat_label_delete,  repeat_field_delete)
            repeat_field_entity._save()

            # Redisplay field view with message
            info_values = self.info_params(
                message.TASK_CREATE_LIST_VALUE_FIELD%
                  {'field_id': repeat_field_id, 'label': field_label}
                )
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entitytypeinfo.FIELD_ID
                , 'entity_id':  repeat_field_id
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

        elif task_id == entitytypeinfo.TASK_ID+"/Define_field_ref":
            if viewinfo.check_authorization("edit"):
                return responseinfo.set_http_response(viewinfo.http_response)
            # Extract info from entityformvals (form is a field description)
            field_entity_id       = entityformvals[ANNAL.CURIE.id]
            field_label           = entityformvals[RDFS.CURIE.label]
            field_entity_type     = entityformvals[ANNAL.CURIE.field_entity_type]
            field_property_uri    = entityformvals[ANNAL.CURIE.property_uri]
            field_value_type      = entityformvals[ANNAL.CURIE.field_value_type]
            ref_field_id          = field_entity_id    + layout.SUFFIX_MULTI
            ref_group_id          = field_entity_id    + layout.SUFFIX_MULTI_G
            ref_property_uri      = field_property_uri + layout.SUFFIX_MULTI_P
            ref_entity_type       = (
                field_entity_type if field_entity_type != ANNAL.CURIE.Field_list else 
                ""
                )
            field_params = { "field_id": field_entity_id, "field_label": field_label }
            ref_field_label       = message.FIELD_REF_LABEL%field_params
            ref_field_comment     = message.FIELD_REF_COMMENT%field_params
            ref_field_placeholder = message.FIELD_REF_PLACEHOLDER%field_params
            # Create field referencing field
            field_typeinfo = EntityTypeInfo(
                viewinfo.collection, entitytypeinfo.FIELD_ID
                )
            ref_field_entity   = field_typeinfo.get_create_entity(ref_field_id)
            ref_field_entity[ANNAL.CURIE.field_render_type] = "RefMultifield"
            ref_field_entity[ANNAL.CURIE.field_value_mode]  = "Value_entity"
            if not ref_field_entity.get(ANNAL.CURIE.field_fields, None):
                ref_field_entity[ANNAL.CURIE.field_fields] = (
                    [ { ANNAL.CURIE.field_id:           entitytypeinfo.FIELD_ID+"/"+field_entity_id
                      , ANNAL.CURIE.field_placement:    "small:0,12"
                      }
                    ])
            ref_field_entity.setdefault(RDFS.CURIE.label,               ref_field_label)
            ref_field_entity.setdefault(RDFS.CURIE.comment,             ref_field_comment)
            ref_field_entity.setdefault(ANNAL.CURIE.placeholder,        ref_field_placeholder)
            ref_field_entity.setdefault(ANNAL.CURIE.field_entity_type,  ref_entity_type)
            ref_field_entity.setdefault(ANNAL.CURIE.field_value_type,   ANNAL.CURIE.Field_list)
            ref_field_entity.setdefault(ANNAL.CURIE.property_uri,       ref_property_uri)
            ref_field_entity.setdefault(ANNAL.CURIE.field_placement,    "small:0,12")
            ref_field_entity.setdefault(ANNAL.CURIE.field_ref_type,     "Default_type")
            ref_field_entity._save()
            # Display new reference field view with message; continuation same as current view
            info_values = self.info_params(
                message.TASK_CREATE_REFERENCE_FIELD%
                  {'field_id': field_entity_id, 'group_id': ref_group_id, 'label': field_label}
                )
            view_uri_params = (
                { 'coll_id':    viewinfo.coll_id
                , 'type_id':    entitytypeinfo.FIELD_ID
                , 'entity_id':  ref_field_id
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

        elif task_id == entitytypeinfo.TASK_ID+"/Show_list":
            list_entity_id = viewinfo.use_entity_id or viewinfo.orig_entity_id
            list_uri = self.view_uri(
                "AnnalistEntityGenericList", 
                coll_id=viewinfo.coll_id,
                list_id=list_entity_id
                )
            cont_here = viewinfo.get_continuation_here(
                base_here=self.view_uri(
                    "AnnalistEntityEditView", 
                    coll_id=viewinfo.coll_id,
                    view_id=viewinfo.view_id,
                    type_id=viewinfo.curr_type_id,
                    entity_id=viewinfo.curr_entity_id or viewinfo.orig_entity_id,
                    action=self.uri_action
                    )
                )
            redirect_uri = uri_with_params(
                list_uri, {'continuation_url': cont_here}
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
            # log.info("@@ find_new_enum is_new_f fd %r"%(fd,))
            return fd.has_new_button()
        for enum_desc in self.find_fields(entityvaluemap, is_new_f):
            # log.info("@@ find_new_enum enum_desc %r"%(enum_desc,))
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
            # log.info("***** Move up: %r"%(new_index_list,))
        elif move_field_desc['move_direction'] == 'down':
            new_index_list = reverselist(move_up(reverselist(old_index_list)))
            # log.info("***** Move down: %r"%(new_index_list,))
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
        # Implementation deferred until save logioc can be refactored
        #     [ entitytypeinfo.TASK_ID+"/Copy_type_view_list"
        task_ids = (
            [ entitytypeinfo.TASK_ID+"/Define_view_list"
            , entitytypeinfo.TASK_ID+"/Define_subtype"
            , entitytypeinfo.TASK_ID+"/Define_subproperty_field"
            # , entitytypeinfo.TASK_ID+"/Define_subtype_view_list"
            , entitytypeinfo.TASK_ID+"/Define_repeat_field" 
            , entitytypeinfo.TASK_ID+"/Define_list_field" 
            , entitytypeinfo.TASK_ID+"/Define_many_field" 
            , entitytypeinfo.TASK_ID+"/Define_field_ref" 
            , entitytypeinfo.TASK_ID+"/Show_list" 
            ])
        for t in task_ids:
            if extract_entity_id(t) in form_data:
                return t
        return None

    # The next two methods are used to locate form fields, which may be in repeat
    # groups, that contain activated additional controls (buttons).
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
                # log.debug("find_fields: field_desc %r"%(field_desc))
                if filter_f(field_desc):
                    field_desc['group_list'] = group_list
                    # log.debug(
                    #     "entityedit.find_fields: field name %s, prefixes %r"%
                    #     (field_desc.get_field_name(), group_list)
                    #     )
                    yield field_desc
                if field_desc.has_field_list():
                    if not field_desc.group_field_descs():
                        # this is for resilience in the face of bad data
                        groupref = field_desc.group_ref()
                        if groupref and not valid_id(groupref):
                            log.warning(
                                "entityedit.find_fields: invalid group_ref %s in field description for %s"%
                                   (groupref, field_desc['field_id'])
                                )
                        else:
                            log.warning(
                                "entityedit.find_fields: no field list or group ref in field description for %s"%
                                   (field_desc['field_id'])
                                )
                    elif 'group_id' not in field_desc:
                        log.error(
                            "entityedit.find_fields: groupref %s, missing 'group_id' in field description for %s"%
                               (groupref, field_desc['field_id'])
                            )
                    else:
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
        # log.debug("form_data_contains: field_desc %r"%field_desc)
        # log.debug("form_data_contains: group_list %r"%field_desc['group_list'])
        # log.debug("form_data_contains: form_data %r"%form_data)
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
