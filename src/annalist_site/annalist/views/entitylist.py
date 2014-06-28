"""
Entity list view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message
from annalist.exceptions            import Annalist_Error

from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.entityfinder   import EntityFinder

from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.grouprepeatmap      import GroupRepeatMap
from annalist.views.confirm         import ConfirmView, dict_querydict
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView


#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated entity-value map for list displays
listentityvaluemap  = (
        [ SimpleValueMap(c='title',            e=None,                  f=None               )
        , SimpleValueMap(c='coll_id',          e=None,                  f=None               )
        , SimpleValueMap(c='type_id',          e=None,                  f=None               )
        , SimpleValueMap(c='list_id',          e=None,                  f=None               )
        , SimpleValueMap(c='list_ids',         e=None,                  f=None               )
        , SimpleValueMap(c='list_selected',    e=None,                  f=None               )
        , SimpleValueMap(c='collection_view',  e=None,                  f=None               )
        , SimpleValueMap(c='default_view_id',  e=None,                  f=None               )
        , SimpleValueMap(c='search_for',       e=None,                  f='search_for'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='continuation_uri', e=None,                  f='continuation_uri' )
        ])


#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityGenericListView(EntityEditBaseView):
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
        Check collection and type identifiers and objects.

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        reqhost = self.get_request_host()
        http_response = (
            # http_response or 
            self.get_coll_data(coll_id, host=reqhost) or
            self.get_type_data(type_id) or
            self.get_list_data(self.get_list_id(type_id, list_id))
            )
        return http_response

    def get_list_id(self, type_id, list_id):
        return (
            list_id or 
            self.collection.get_values().get("Default_list", None)
            )

    def get_list_view_id(self):
        return self.recordlist.get('annal:default_view', None) or "Default_view"

    def get_list_type_id(self):
        return self.recordlist.get('annal:default_type', None) or "Default_type"

    def get_new_view_uri(self, coll_id, type_id):
        """
        Get URI for entity new view
        """
        return self.view_uri(
            "AnnalistEntityNewView", 
            coll_id=coll_id, 
            view_id=self.get_list_view_id(), 
            type_id=type_id,
            action="new"
            )

    def get_edit_view_uri(self, coll_id, type_id, entity_id, action):
        """
        Get URI for entity edit or copy view
        """
        return self.view_uri(
                "AnnalistEntityEditView", 
                coll_id=coll_id, 
                view_id=self.get_list_view_id(), 
                type_id=type_id,
                entity_id=entity_id,
                action=action
                )

    def get_list_entityvaluemap(self, list_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated list display.
        """
        # @@TODO: can this be subsumed by repeat value logic in get_fields_entityvaluemap?
        # Locate and read view description
        entitymap  = copy.copy(listentityvaluemap)
        log.debug("entitylist %r"%self.recordlist.get_values())
        groupmap = []
        self.get_fields_entityvaluemap(
            groupmap,
            self.recordlist.get_values()['annal:list_fields']
            )
        entitymap.extend(groupmap)  # one-off for access to field headings
        entitymap.append(
            GroupRepeatMap(c='entities', e='annal:list_entities', g=groupmap)
            )
        return entitymap

    def check_collection_entity(self, entity_id, entity_type, msg, continuation_uri=""):
        """
        Test a supplied entity_id is defined in the current collection,
        returning a URI to display a supplied error message if the test fails.

        NOTE: this function works with the generic base template base_generic.html, which
        is assumed to provide an underlay for the currently viewed page.

        entity_id           entity id that is required to be defined in the current collection.
        entity_type         specified type for entity to delete.
        msg                 message to display if the test fails.
        continuation_uri    URI of page to display when the redisplayed form is closed.

        returns a URI string for use with HttpResponseRedirect to redisplay the 
        current page with the supplied message, or None if entity id is OK.
        """
        # log.info("check_collection_entity: entity_id: %s"%(entity_id))
        # log.info("check_collection_entity: entityparent: %s"%(self.entityparent.get_id()))
        # log.info("check_collection_entity: entityclass: %s"%(self.entityclass))
        redirect_uri = None
        typeinfo     = self.entitytypeinfo or EntityTypeInfo(self.site(), self.collection, entity_type)
        if not typeinfo.entityclass.exists(typeinfo.entityparent, entity_id):
            redirect_uri = (
                self.get_request_path()+
                self.error_params(msg)
                ) + continuation_uri
        return redirect_uri

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("entitylist.get: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        http_response = (
            self.list_setup(coll_id, type_id, list_id) or
            self.form_edit_auth("list", self.collection._entityuri)
            )
        if http_response:
            return http_response
        # Prepare list and entity IDs for rendering form
        list_id     = self.get_list_id(type_id, list_id)
        list_ids    = [ l.get_id() for l in self.collection.lists() ]
        entity_list = (
            EntityFinder(self.collection)
                .get_entities(type_id, selector=None, search=None)
            )
        entityval = { 'annal:list_entities': list(entity_list) }
        # Set up initial view context
        self._entityvaluemap = self.get_list_entityvaluemap(list_id)
        log.debug("EntityGenericListView.get _entityvaluemap %r"%(self._entityvaluemap))
        viewcontext = self.map_value_to_context(entityval,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', ""),
            ### heading             = entity_initial_values['rdfs:label'],
            coll_id             = coll_id,
            type_id             = type_id,
            list_id             = list_id,
            list_ids            = list_ids,
            list_selected       = list_id,
            collection_view     = self.view_uri("AnnalistCollectionView", coll_id=coll_id),
            default_view_id     = self.recordlist['annal:default_view']
            )
        # log.debug("EntityGenericListView.get viewcontext %r"%(viewcontext))
        # generate and return form data
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
        continuation_uri, continuation_here, continuation_next = self.continuation_uris(
            request.POST,
            self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            )
        # log.info("continuation_here %s"%(continuation_here))
        # log.info("continuation_uri  %s"%(continuation_uri))
        if 'close' in request.POST:
            return HttpResponseRedirect(continuation_uri)
        # Not "Close": set up list parameters
        http_response = (
            self.list_setup(coll_id, type_id, list_id)
            )
        if http_response:
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
            entity_type = entity_type or type_id or self.get_list_type_id()
            cont_param  = "&continuation_uri="+continuation_uri
            if "new" in request.POST:
                action = "new"
                redirect_uri = self.get_new_view_uri(coll_id, entity_type) + continuation_here
            if "copy" in request.POST:
                action = "copy"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_COPY, 
                        continuation_uri=cont_param
                        ) or
                    self.get_edit_view_uri(
                        coll_id, entity_type, entity_id, action
                        ) + continuation_here
                    )
            if "edit" in request.POST:
                action = "edit"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_EDIT,
                        continuation_uri=cont_param
                        ) or
                    self.get_edit_view_uri(
                        coll_id, entity_type, entity_id, action
                        ) + continuation_here
                    )
            if "delete" in request.POST:
                action = "delete"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_DELETE,
                        continuation_uri=cont_param
                        ) or
                    self.check_collection_entity(entity_id, entity_type,
                        message.SITE_ENTITY_FOR_DELETE%{'id': entity_id},
                        continuation_uri=cont_param
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
                        , "continuation_uri":   [self.get_request_path()]
                        })
                    message_vals = {'id': entity_id, 'type_id': entity_type, 'coll_id': coll_id}
                    return (
                        self.form_edit_auth("delete", self.collection.get_uri()) or
                        ConfirmView.render_form(request,
                            action_description=     message.REMOVE_ENTITY_DATA%message_vals,
                            complete_action_uri=    complete_action_uri,
                            action_params=          delete_params,
                            cancel_action_uri=      self.get_request_path(),
                            title=                  self.site_data()["title"]
                            )
                        )
            if "search" in request.POST:
                action = "search"                
                raise Annalist_Error(request.POST, "@@TODO EntityGenericListView.post unimplemented "+self.get_request_path())
            if "list_view" in request.POST:
                action  = "list"
                redirect_uri = self.view_uri(
                    "AnnalistEntityGenericList", 
                    coll_id=coll_id, 
                    list_id=request.POST['list_id'], 
                    type_id=type_id or "",
                    ) + continuation_next
            if "default_view" in request.POST:
                # @@TODO:
                # Make currently selected list view default for collection
                # @@TODO: also, reinstate test case
                action = "config"
                raise Annalist_Error(request.POST, "@@TODO EntityGenericListView.post unimplemented "+self.get_request_path())
            if "customize" in request.POST:
                action       = "config"
                redirect_uri = self.view_uri(
                    "AnnalistCollectionEditView", 
                    coll_id=coll_id
                    ) + continuation_here
        if redirect_uri:
            return (
                self.form_edit_auth(action, self.collection.get_uri()) or
                HttpResponseRedirect(redirect_uri)
                )
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        log.error("Unexpected form data posted to %s: %r"(request.get_full_path(), request.POST))
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(continuation_uri+err_values)

# End.
