"""
Entity list view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message
from annalist.exceptions            import Annalist_Error

from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

from annalist.views.confirm         import ConfirmView, dict_querydict
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class GenericEntityListView(EntityEditBaseView):
    """
    View class for generic entity list view
    """

    _entityformtemplate = 'annalist_entity_list.html'
    _entityclass        = None          # to be supplied dynamically

    def __init__(self, list_id=None):
        super(GenericEntityListView, self).__init__()
        self._default_list_id = list_id
        return

    # Helper functions

    def list_setup(self, coll_id, type_id):
        """
        Check collection and type identifiers and objects.

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        reqhost = self.get_request_host()
        if type_id:
            http_response = (
                self.get_coll_data(coll_id, host=reqhost) or
                self.get_type_data(type_id)
                )
        else:
            http_response = self.get_coll_data(coll_id, host=reqhost)
        # if not http_response:
        #     http_response = self.get_list_data(list_id or self._list_id)
        return http_response

    def get_list_id(self, type_id, list_id):
        return (
            list_id or 
            self._default_list_id or 
            self.collection.get_values().get("Default_list", None)
            )

    def get_list_view_id(self):
        return self.recordlist.get('annal:default_view', None) or "Default_view"

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

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("entitylist.get: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        http_response = self.list_setup(coll_id, type_id)
        if not http_response:
            http_response = self.form_edit_auth("list", self.collection._entityuri)
        if http_response:
            return http_response
        # Prepare context for rendering form
        # @@TODO: apply selector logic here?
        list_id     = self.get_list_id(type_id, list_id)
        list_ids    = [ l.get_id() for l in self.collection.lists() ]
        if type_id:
            entity_list = self.recordtypedata.entities()
        else:
            entity_list = []
            for f in self.collection._children(RecordTypeData):
                t = RecordTypeData.load(self.collection, f)
                if t:
                    entity_list.extend(t.entities())
        entityval = { 'annal:list_entities': entity_list }
        # Set up initial view context
        self._entityvaluemap = self.get_list_entityvaluemap(list_id)
        log.debug("GenericEntityListView.get _entityvaluemap %r"%(self._entityvaluemap))
        viewcontext = self.map_value_to_context(entityval,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', ""),
            ### heading             = entity_initial_values['rdfs:label'],
            coll_id             = coll_id,
            type_id             = type_id,
            list_id             = list_id,
            list_ids            = list_ids,
            list_selected       = list_id
            )
        log.debug("GenericEntityListView.get viewcontext %r"%(viewcontext))
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
        continuation_here, continuation_uri = self.continuation_uris(request.POST,
            self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            )
        # log.info("continuation_here %s"%(continuation_here))
        # log.info("continuation_uri  %s"%(continuation_uri))
        if 'close' in request.POST:
            return HttpResponseRedirect(continuation_uri)
        # Not "Close": set up list parameters
        http_response = (
            self.list_setup(coll_id, type_id) or
            self.get_list_data(self.get_list_id(type_id, list_id))
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
            entity_type = entity_type or type_id or "Default_type"
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
                    self.get_edit_view_uri(coll_id, entity_type, entity_id, action) + continuation_here
                    )
            if "edit" in request.POST:
                action = "edit"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_EDIT,
                        continuation_uri=cont_param
                        ) or
                    self.get_edit_view_uri(coll_id, entity_type, entity_id, action) + continuation_here
                    )
            if "delete" in request.POST:
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_DELETE,
                        continuation_uri=cont_param
                        )
                    )
                if not redirect_uri:
                    # Get user to confirm action before actually doing it
                    complete_action_uri = self.view_uri(
                        "AnnalistEntityDataDeleteView", 
                        coll_id=coll_id, type_id=entity_type
                        )
                    delete_params = dict_querydict(
                        { "entity_delete":      ["Delete"]
                        , "entity_id":          [entity_id]
                        , "continuation_uri":   [self.get_request_path()]
                        })
                    return (
                        self.form_edit_auth("delete", self.collection.get_uri()) or
                        ConfirmView.render_form(request,
                            action_description=     message.REMOVE_ENTITY_DATA%(entity_id, entity_type, coll_id),
                            complete_action_uri=    complete_action_uri,
                            action_params=          delete_params,
                            cancel_action_uri=      self.get_request_path(),
                            title=                  self.site_data()["title"]
                            )
                        )
            if "search" in request.POST:
                action = "search"                
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
            if "list_view" in request.POST:
                action = "list"
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
            if "default_view" in request.POST:
                action = "config"
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
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
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(continuation_uri+err_values)

# End.
