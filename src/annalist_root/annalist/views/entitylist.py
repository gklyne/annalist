"""
Entity list view
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist                           import layout
from annalist                           import message
from annalist.exceptions                import Annalist_Error
from annalist.identifiers               import RDFS, ANNAL
from annalist.util                      import (
    make_type_entity_id, split_type_entity_id, extract_entity_id,
    make_resource_url
    )

import annalist.models.entitytypeinfo as entitytypeinfo
from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitytypeinfo     import EntityTypeInfo, CONFIG_PERMISSIONS
from annalist.models.entityfinder       import EntityFinder

from annalist.views.uri_builder         import uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.confirm             import ConfirmView, dict_querydict
from annalist.views.generic             import AnnalistGenericView

from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.fieldvaluemap       import FieldValueMap
from annalist.views.repeatvaluesmap     import RepeatValuesMap

from annalist.views.fields.field_description    import FieldDescription, field_description_from_view_field
from annalist.views.fields.bound_field          import bound_field, get_entity_values

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated 
# entity-value map for list displays
listentityvaluemap  = (
        [ SimpleValueMap(c='help_filename',         e=None, f=None               )
        , SimpleValueMap(c='url_type_id',           e=None, f=None               )
        , SimpleValueMap(c='url_list_id',           e=None, f=None               )
        , SimpleValueMap(c='list_choices',          e=None, f=None               )
        , SimpleValueMap(c='collection_view',       e=None, f=None               )
        , SimpleValueMap(c='default_view_id',       e=None, f=None               )
        , SimpleValueMap(c='default_view_enable',   e=None, f=None               )
        , SimpleValueMap(c='customize_view_enable', e=None, f=None               )
        , SimpleValueMap(c='search_for',            e=None, f='search_for'       )
        , SimpleValueMap(c='scope',                 e=None, f='scope'            )
        , SimpleValueMap(c='continuation_url',      e=None, f='continuation_url' )
        , SimpleValueMap(c='continuation_param',    e=None, f=None               )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        ])

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityGenericListView(AnnalistGenericView):
    """
    View class for generic entity list view
    """

    _entityformtemplate = 'annalist_entity_list.html'

    def __init__(self):
        super(EntityGenericListView, self).__init__()
        self.help          = "entity-list-help"
        return

    # Helper functions

    def list_setup(self, coll_id, type_id, list_id, request_dict):
        """
        Assemble display information for list view request handlers
        """
        # log.info("list_setup coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        self.collection_view_url = self.get_collection_view_url(coll_id)
        listinfo = DisplayInfo(self, "list", request_dict, self.collection_view_url)
        listinfo.get_site_info(self.get_request_host())
        listinfo.get_coll_info(coll_id)
        listinfo.get_request_type_info(type_id)
        listinfo.get_list_info(listinfo.get_list_id(listinfo.type_id, list_id))
        listinfo.check_authorization("list")
        return listinfo

    def get_list_entityvaluemap(self, listinfo, context_extra_values):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated list display.
        """
        # Locate and read view description
        entitymap  = EntityValueMap(listentityvaluemap)
        # log.debug(
        #     "EntityGenericListView.get_list_entityvaluemap entitylist %r"%
        #     listinfo.recordlist.get_values()
        #     )
        #
        # Need to generate
        # 1. 'fields':  (context receives list of field descriptions used to generate row headers)
        # 2. 'entities': (context receives a bound field that displays entry for each entity)
        #
        # NOTE - supplied entity has single field ANNAL.CURIE.entity_list (see 'get' below)
        #        entitylist template uses 'fields' from context to display headings
        list_fields = listinfo.recordlist.get(ANNAL.CURIE.list_fields, [])
        fieldlistmap = FieldListValueMap('fields', listinfo.collection, list_fields, None)
        entitymap.add_map_entry(fieldlistmap)  # For access to field headings
        repeatrows_field_descr = (
            { ANNAL.CURIE.id:                   "List_rows"
            , RDFS.CURIE.label:                 "Fields"
            , RDFS.CURIE.comment:               
                "This resource describes the repeated field description used when "+
                "displaying and/or editing a record view description"
            , ANNAL.CURIE.field_name:           "List_rows"
            , ANNAL.CURIE.field_render_type:    "RepeatListRow"
            , ANNAL.CURIE.property_uri:         ANNAL.CURIE.entity_list
            })
        repeatrows_descr = FieldDescription(
            listinfo.collection, 
            repeatrows_field_descr,
            field_list=list_fields
            )
        entitymap.add_map_entry(FieldValueMap(c="List_rows", f=repeatrows_descr))
        return entitymap

    # Helper functions assemble and return data for list of entities

    def strip_context_values(self, listinfo, entity, base_url):
        """
        Return selected values from entity data, 
        with context reference removed and entity id updated.
        """
        # entityvals = entity.get_values()
        entityvals = get_entity_values(listinfo.curr_typeinfo, entity)
        entityvals.pop('@context', None)
        entityref = make_type_entity_id(
            entityvals[ANNAL.CURIE.type_id], entityvals[ANNAL.CURIE.id]
            )
        entityvals['@id'] = base_url+entityref
        return entityvals

    def assemble_list_data(self, listinfo, scope, search_for):
        """
        Assemble and return a dict structure of JSON data used to generate
        entity list responses.
        """
        # Prepare list and entity IDs for rendering form
        selector    = listinfo.recordlist.get_values().get(ANNAL.CURIE.list_entity_selector, "")
        user_perms  = self.get_permissions(listinfo.collection)
        entity_list = (
            EntityFinder(listinfo.collection, selector=selector)
                .get_entities_sorted(
                    user_perms, type_id=listinfo.type_id, altscope=scope,
                    context={'list': listinfo.recordlist}, search=search_for
                    )
            )
        #@@
        # log.info("assemble_list_data: %r"%([e.get_id() for e in entity_list],))
        #@@
        # typeinfo = listinfo.curr_typeinfo
        base_url = self.get_collection_base_url(listinfo.coll_id)
        list_url = self.get_list_url(
            listinfo.coll_id, listinfo.list_id,
            type_id=listinfo.type_id,
            scope=scope,
            search=search_for
            )
        entityvallist = [ self.strip_context_values(listinfo, e, base_url) for e in entity_list ]
        # print "@@@@ type_id %s"%(listinfo.type_id,)
        # print "@@@@ entity_list %r"%(entity_list,)
        # print "@@@@ entityvallist %r"%(entityvallist,)
        # log.debug("@@ listinfo.list_id %s, coll base_url %s"%(listinfo.list_id, base_url))
        # log.info(
        #     "EntityListDataView.assemble_list_data: list_url %s, base_url %s, context_url %s"%
        #     (list_url, base_url, base_url+layout.COLL_CONTEXT_FILE)
        #     )
        jsondata = (
            { '@id':            list_url
            , '@context': [
                { "@base":  base_url },
                base_url+layout.COLL_CONTEXT_FILE
                ]
            , ANNAL.CURIE.entity_list:  entityvallist
            })
        # print "@@@@ assemble_list_data: jsondata %r"%(jsondata,)
        return jsondata

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Create a form for listing entities.
        """
        scope      = request.GET.get('scope',  None)
        search_for = request.GET.get('search', "")
        log.info(
            "views.entitylist.get:  coll_id %s, type_id %s, list_id %s, scope %s, search '%s'"%
            (coll_id, type_id, list_id, scope, search_for)
            )
        log.log(settings.TRACE_FIELD_VALUE, "  %s"%(self.get_request_path()))
        listinfo    = self.list_setup(coll_id, type_id, list_id, request.GET.dict())
        if listinfo.http_response:
            return listinfo.http_response
        self.help_markdown = listinfo.recordlist.get(RDFS.CURIE.comment, None)
        log.debug("listinfo.list_id %s"%listinfo.list_id)
        # Prepare list and entity IDs for rendering form
        try:
            entityvallist = self.assemble_list_data(listinfo, scope, search_for)
            # Set up initial view context
            context_extra_values = (
                { 'continuation_url':       listinfo.get_continuation_url() or ""
                , 'continuation_param':     listinfo.get_continuation_param()
                , 'request_url':            self.get_request_path()
                , 'scope':                  scope
                , 'url_type_id':            type_id
                , 'url_list_id':            list_id
                , 'search_for':             search_for
                , 'list_choices':           self.get_list_choices_field(listinfo)
                , 'collection_view':        self.collection_view_url
                , 'default_view_id':        listinfo.recordlist[ANNAL.CURIE.default_view]
                , 'default_view_enable':    'disabled="disabled"'
                , 'customize_view_enable':  'disabled="disabled"'
                , 'collection':             listinfo.collection
                })
            if listinfo.authorizations['auth_config']:
                context_extra_values['customize_view_enable'] = ""
                if list_id:
                    context_extra_values['default_view_enable']   = ""
            entityvaluemap = self.get_list_entityvaluemap(listinfo, context_extra_values)
            listcontext = entityvaluemap.map_value_to_context(
                entityvallist,
                **context_extra_values
                )
            listcontext.update(listinfo.context_data())
        except Exception as e:
            log.exception(str(e))
            return self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        # log.info("EntityGenericListView.get listcontext %r"%(listcontext))
        # Generate and return form data
        json_redirect_url   = make_resource_url("", self.get_request_path(), layout.ENTITY_LIST_FILE)
        turtle_redirect_url = make_resource_url("", self.get_request_path(), layout.ENTITY_LIST_TURTLE)
        return (
            self.render_html(listcontext, self._entityformtemplate)
            or 
            self.redirect_json(json_redirect_url)
            or
            self.redirect_turtle(turtle_redirect_url)
            or
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Handle response from dynamically generated list display form.
        """
        log.info("views.entitylist.post: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        log.log(settings.TRACE_FIELD_VALUE, "  %s"%(self.get_request_path()))
        # log.log(settings.TRACE_FIELD_VALUE, "  form data %r"%(request.POST))
        listinfo = self.list_setup(coll_id, type_id, list_id, request.POST.dict())
        if listinfo.http_response:
            return listinfo.http_response
        if 'close' in request.POST:
            return HttpResponseRedirect(listinfo.get_continuation_url() or self.collection_view_url)

        # Process requested action
        action          = None
        redirect_path   = None
        redirect_cont   = listinfo.get_continuation_here()
        redirect_params = {}
        entity_ids      = request.POST.getlist('entity_select')
        log.debug("entity_ids %r"%(entity_ids))
        if len(entity_ids) > 1:
            listinfo.display_error_response(message.TOO_MANY_ENTITIES_SEL)
        else:
            entity_type = type_id or listinfo.get_list_type_id()
            entity_id   = None
            if len(entity_ids) == 1:
                (entity_type, entity_id) = split_type_entity_id(entity_ids[0], entity_type)
                log.info("EntityList.post entity_ids: entity_type %s, entity_id %s"%(entity_type, entity_id))
            if "new" in request.POST:
                action        = "new"
                redirect_path = listinfo.get_new_view_uri(coll_id, entity_type)
            if "copy" in request.POST:
                action = "copy"
                if not entity_id:
                    listinfo.display_error_response(message.NO_ENTITY_FOR_COPY)
                else:
                    redirect_path = listinfo.get_edit_view_uri(
                        coll_id, entity_type, entity_id, action
                        )
            if "edit" in request.POST:
                action = "edit"
                if not entity_id:
                    listinfo.display_error_response(message.NO_ENTITY_FOR_EDIT)
                else:
                    redirect_path = listinfo.get_edit_view_uri(
                        coll_id, entity_type, entity_id, action
                        )
            if "delete" in request.POST:
                action = "delete"
                confirmed_deletion_uri = self.view_uri(
                    "AnnalistEntityDataDeleteView", 
                    coll_id=coll_id, type_id=entity_type
                    )
                return listinfo.confirm_delete_entity_response(
                    entity_type, entity_id, 
                    confirmed_deletion_uri
                    )
            if "default_view" in request.POST:
                #@@
                # auth_check = self.form_action_auth("config", listinfo.collection, CONFIG_PERMISSIONS)
                #@@
                auth_check = listinfo.check_authorization("config")
                if auth_check:
                    return auth_check
                listinfo.collection.set_default_list(list_id)
                listinfo.add_info_message(
                    message.DEFAULT_LIST_UPDATED%{'coll_id': coll_id, 'list_id': list_id}         
                    )
                redirect_path, redirect_params = listinfo.redisplay_path_params()
                redirect_cont   = listinfo.get_continuation_next()
            if ( ("list_type" in request.POST) or ("list_all"  in request.POST) ):
                action          = "list"
                redirect_path   = self.get_list_url(
                    coll_id, extract_entity_id(request.POST['list_choice']),
                    type_id=None if "list_all" in request.POST else type_id
                    )
                redirect_params = dict(
                    scope="all" if "list_scope_all" in request.POST else None,
                    search=request.POST['search_for']
                    )
                redirect_cont   = listinfo.get_continuation_next()
                # redirect_cont   = None
            if "customize" in request.POST:
                action        = "config"
                redirect_path = self.view_uri(
                            "AnnalistCollectionEditView", 
                            coll_id=coll_id
                            )
        if redirect_path:
            if redirect_cont:
                redirect_params.update(
                    { "continuation_url": redirect_cont }
                    )
            listinfo.redirect_response(
                redirect_path, redirect_params=redirect_params, action=action
                )
            # return (
            #     listinfo.check_authorization(action) or
            #     HttpResponseRedirect(redirect_uri)
            #     )
        if listinfo.http_response:
            return listinfo.http_response


        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        log.error("Unexpected form data posted to %s: %r"%(request.get_full_path(), request.POST))
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        redirect_uri = uri_with_params(listinfo.get_continuation_next(), err_values)
        return HttpResponseRedirect(redirect_uri)

    def get_list_choices_field(self, listinfo):
        """
        Returns a bound_field object that displays as a list-choice selection drop-down.
        """
        # @@TODO: Possibly create FieldValueMap and return map_entity_to_context value? 
        #         or extract this logic and share?  See also entityedit view choices
        field_description = field_description_from_view_field(
            listinfo.collection, 
            { ANNAL.CURIE.field_id: "List_choice"
            , ANNAL.CURIE.field_placement: "small:0,12;medium:0,9" },
            {}
            )
        entityvals = { field_description['field_property_uri']: listinfo.list_id }
        return bound_field(field_description, entityvals)

    def get_list_url(self, coll_id, list_id, type_id=None, scope=None, search=None, query_params={}):
        """
        Return a URL for accessing the current list display
        """
        list_uri_params = (
            { 'coll_id': coll_id
            , 'list_id': list_id
            })
        if type_id:
            list_uri_params['type_id']  = type_id
        if scope:
            query_params = dict(query_params, scope=scope)
        if search:
            query_params = dict(query_params, search=search)
        list_url = (
            uri_with_params(
                self.view_uri("AnnalistEntityGenericList", **list_uri_params),
                query_params
                )
            )
        return list_url

# End.
