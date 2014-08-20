"""
Entity list view
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
from annalist.exceptions                import Annalist_Error

from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitytypeinfo     import EntityTypeInfo
from annalist.models.entityfinder       import EntityFinder

from annalist.views.uri_builder         import uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.grouprepeatmap      import GroupRepeatMap
from annalist.views.confirm             import ConfirmView, dict_querydict
from annalist.views.generic             import AnnalistGenericView

from annalist.views.fields.render_utils import get_entity_values

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated entity-value map for list displays
listentityvaluemap  = (
        [ SimpleValueMap(c='title',                 e=None,                  f=None               )
        , SimpleValueMap(c='coll_id',               e=None,                  f=None               )
        , SimpleValueMap(c='type_id',               e=None,                  f=None               )
        , SimpleValueMap(c='list_id',               e=None,                  f=None               )
        , SimpleValueMap(c='list_ids',              e=None,                  f=None               )
        , SimpleValueMap(c='list_selected',         e=None,                  f=None               )
        , SimpleValueMap(c='collection_view',       e=None,                  f=None               )
        , SimpleValueMap(c='default_view_id',       e=None,                  f=None               )
        , SimpleValueMap(c='default_view_enable',   e=None,                  f=None               )
        , SimpleValueMap(c='search_for',            e=None,                  f='search_for'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='continuation_url',      e=None,                  f='continuation_url' )
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
        return

    # Helper functions

    def list_setup(self, coll_id, type_id, list_id):
        """
        Assemble display information for list view request handler
        """
        listinfo = DisplayInfo(self, "list")
        listinfo.get_site_info(self.get_request_host())
        listinfo.get_coll_info(coll_id)
        listinfo.get_type_info(type_id)
        listinfo.get_list_info(listinfo.get_list_id(listinfo.type_id, list_id))
        listinfo.check_authorization("list")
        return listinfo

    def get_list_entityvaluemap(self, listinfo):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated list display.
        """
        # @@TODO: can this be subsumed by repeat value logic in get_fields_entityvaluemap?
        # Locate and read view description
        entitymap  = EntityValueMap(listentityvaluemap)
        log.debug("entitylist %r"%listinfo.recordlist.get_values())
        fieldlistmap = FieldListValueMap(
            listinfo.collection, 
            listinfo.recordlist.get_values()['annal:list_fields']
            )
        entitymap.add_map_entry(fieldlistmap)  # one-off for access to field headings
        entitymap.add_map_entry(
            GroupRepeatMap(c='entities', e='annal:list_entities', g=[fieldlistmap])
            )
        return entitymap

    #@@
    # def get_entityvals(self, entity_list):
    #     for e in entity_list:
    #         v = e.get_values()
    #         v[...]
    #@@

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("entitylist.get: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        listinfo = self.list_setup(coll_id, type_id, list_id)
        if listinfo.http_response:
            return listinfo.http_response
        log.debug("list_id %s"%listinfo.list_id)
        # Prepare list and entity IDs for rendering form
        list_ids    = [ l.get_id() for l in listinfo.collection.lists() ]
        selector    = listinfo.recordlist.get_values().get('annal:list_entity_selector', "")
        search_for  = request.GET.get('search', "")
        entity_list = (
            EntityFinder(listinfo.collection)
                .get_entities(type_id, selector=selector, search=search_for)
            )
        entityval = { 'annal:list_entities': [ get_entity_values(e) for e in entity_list ] }
        # Set up initial view context
        entityvaluemap = self.get_list_entityvaluemap(listinfo)
        viewcontext = entityvaluemap.map_value_to_context(entityval,
            title               = self.site_data()["title"],
            continuation_url    = request.GET.get('continuation_url', ""),
            request_url         = self.get_request_path(),
            ### heading             = entity_initial_values['rdfs:label'],
            coll_id             = coll_id,
            type_id             = type_id,
            list_id             = listinfo.list_id,
            search_for          = search_for,
            list_ids            = list_ids,
            list_selected       = listinfo.list_id,
            collection_view     = self.view_uri("AnnalistCollectionView", coll_id=coll_id),
            default_view_id     = listinfo.recordlist['annal:default_view'],
            default_view_enable = ("" if list_id else 'disabled="disabled"')
            )
        # log.debug("EntityGenericListView.get viewcontext %r"%(viewcontext))
        # Generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Handle response from dynamically generated list display form.
        """
        log.debug("entitylist.post: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        # log.info("  %s"%(self.get_request_path()))
        # log.info("  form data %r"%(request.POST))
        continuation_next, continuation_here = self.continuation_urls(
            request.POST,
            None
            # self.view_uri("AnnalistSiteView")
            # self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            )
        if 'close' in request.POST:
            return HttpResponseRedirect(
                continuation_next.get('continuation_url', self.view_uri("AnnalistSiteView"))
                )
        # Not "Close": set up list parameters
        listinfo = self.list_setup(coll_id, type_id, list_id)
        if listinfo.http_response:
            return http_response
        # Process requested action
        redirect_uri = None
        entity_ids   = request.POST.getlist('entity_select')
        log.debug("entity_ids %r"%(entity_ids))
        if len(entity_ids) > 1:
            action = ""
            redirect_uri = self.check_value_supplied(None, message.TOO_MANY_ENTITIES_SEL)
        else:
            (entity_type, entity_id) = (
                entity_ids[0].split("/") if len(entity_ids) == 1 else (None, None)
                )
            entity_type = entity_type or type_id or listinfo.get_list_type_id()
            if "new" in request.POST:
                action = "new"
                redirect_uri = uri_with_params(
                    listinfo.get_new_view_uri(coll_id, entity_type), 
                    continuation_here
                    )
            if "copy" in request.POST:
                action = "copy"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_COPY, 
                        continuation_url=continuation_next
                        )
                    or
                    uri_with_params(
                        listinfo.get_edit_view_uri(
                            coll_id, entity_type, entity_id, action
                            ),
                        continuation_here
                        )
                    )
            if "edit" in request.POST:
                action = "edit"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_EDIT,
                        continuation_url=continuation_next
                        )
                    or
                    uri_with_params(
                        listinfo.get_edit_view_uri(
                            coll_id, entity_type, entity_id, action
                            ),
                        continuation_here
                        )
                    )
            if "delete" in request.POST:
                action = "delete"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_DELETE,
                        continuation_url=continuation_next
                        )
                    or
                    listinfo.check_collection_entity(entity_id, entity_type,
                        message.SITE_ENTITY_FOR_DELETE%{'id': entity_id},
                        continuation_url=continuation_next
                        )
                    )
                if not redirect_uri:
                    # Get user to confirm action before actually doing it
                    complete_action_uri = self.view_uri(
                        "AnnalistEntityDataDeleteView", 
                        coll_id=coll_id, type_id=entity_type
                        )
                    # log.info("coll_id %s, type_id %s, complete_action_uri %s"%(coll_id, entity_type, complete_action_uri))
                    delete_params = dict_querydict(
                        { "entity_delete":      ["Delete"]
                        , "entity_id":          [entity_id]
                        , "continuation_url":   [self.get_request_path()]
                        })
                    message_vals = {'id': entity_id, 'type_id': entity_type, 'coll_id': coll_id}
                    return (
                        self.form_action_auth("delete", listinfo.collection.get_url()) or
                        ConfirmView.render_form(request,
                            action_description=     message.REMOVE_ENTITY_DATA%message_vals,
                            complete_action_uri=    complete_action_uri,
                            action_params=          delete_params,
                            cancel_action_uri=      self.get_request_path(),
                            title=                  self.site_data()["title"]
                            )
                        )
            if "default_view" in request.POST:
                auth_check = self.form_action_auth("config", listinfo.collection.get_url())
                if auth_check:
                    return auth_check
                listinfo.collection.set_default_list(list_id)
                action = "list"
                msg    = message.DEFAULT_VIEW_UPDATED%{'coll_id': coll_id, 'list_id': list_id}         
                redirect_uri = (
                    uri_with_params(
                        self.get_request_path(), 
                        self.info_params(msg),
                        continuation_next
                        )
                    )
            if "view" in request.POST:
                action = "list"         
                search = request.POST['search_for']
                params = continuation_next
                if search:
                    params = dict(params, search=search)
                list_uri_params = (
                    { 'coll_id': coll_id
                    , 'list_id': request.POST['list_id']
                    })
                if type_id:
                    list_uri_params.update({'type_id': type_id})
                redirect_uri = (
                    uri_with_params(
                        self.view_uri("AnnalistEntityGenericList", **list_uri_params),
                        params
                        )
                    )
            if "customize" in request.POST:
                action       = "config"
                redirect_uri = (
                    uri_with_params(
                        self.view_uri(
                            "AnnalistCollectionEditView", 
                            coll_id=coll_id
                            ),
                        continuation_here
                        )
                    )
        if redirect_uri:
            return (
                listinfo.check_authorization(action) or
                HttpResponseRedirect(redirect_uri)
                )
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        log.error("Unexpected form data posted to %s: %r"%(request.get_full_path(), request.POST))
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        redirect_uri = uri_with_params(continuation_next['continuation_url'], err_values)
        return HttpResponseRedirect(redirect_uri)

# End.
