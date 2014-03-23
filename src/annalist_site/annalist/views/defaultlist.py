"""
Default record view/edit
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

class EntityDefaultListView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can be generated dynamically per-instance...

    _entityformtemplate = 'annalist_entity_list.html'
    _entityclass        = None          # to be supplied dynamically

    def __init__(self):
        super(EntityDefaultListView, self).__init__()
        self._list_id       = "Default_list"
        self._entityclass   = None
        return

    # Helper functions

    def view_setup(self, coll_id, type_id):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection
            self.recordtype
            self.recordtypedata
            self._entityclass

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        reqhost = self.get_request_host()
        if type_id:
            http_response = self.get_coll_type_data(coll_id, type_id, host=reqhost)
            self._list_id = "Default_list"
        else:
            http_response = self.get_coll_data(coll_id, host=reqhost)
            self._list_id = "Default_list_all"
        return http_response

    # GET

    def get(self, request, coll_id=None, type_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("defaultedit.get: coll_id %s, type_id %s"%(coll_id, type_id))
        http_response = self.view_setup(coll_id, type_id)
        if not http_response:
            http_response = self.form_edit_auth("list", self.collection._entityuri)
        if http_response:
            return http_response
        # Prepare context for rendering form
        list_ids      = [ l.get_id() for l in self.collection.lists() ]
        list_selected = self.collection.get_values().get("default_list", self._list_id)
        # @@TODO: apply selector logic here?
        if type_id:
            entity_list   = self.recordtypedata.entities()
        else:
            entity_list = []
            for f in self.collection._children(RecordTypeData):
                t = RecordTypeData.load(self.collection, f)
                if t:
                    entity_list.extend(t.entities())
        entityval = { 'annal:list_entities': entity_list }
        # Set up initial view context
        self._entityvaluemap = self.get_list_entityvaluemap(self._list_id)
        log.debug("EntityDefaultListView.get _entityvaluemap %r"%(self._entityvaluemap))
        viewcontext = self.map_value_to_context(entityval,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            ### heading             = entity_initial_values['rdfs:label'],
            coll_id             = coll_id,
            type_id             = type_id,
            list_id             = self._list_id,
            list_ids            = list_ids,
            list_selected       = list_selected
            )
        log.debug("EntityDefaultListView.get viewcontext %r"%(viewcontext))
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None):
        """
        Handle response from dynamically generated list display form.
        """
        log.debug("defaultlist.post: coll_id %s, type_id %s"%(coll_id, type_id))
        # log.info("  %s"%(self.get_request_path()))
        # log.info("  form data %r"%(request.POST))
        continuation_uri = request.POST.get(
            "continuation_uri", 
            self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            )
        if 'close' in request.POST:
            return HttpResponseRedirect(continuation_uri)
        http_response = self.view_setup(coll_id, type_id)
        if http_response:
            return http_response
        # Process requested action
        redirect_uri = None
        continuation_path = self.get_request_path().split("?", 1)[0]
        continuation = "?continuation_uri=%s"%(continuation_path)
        entity_ids   = request.POST.getlist('entity_select')
        log.debug("entity_ids %r"%(entity_ids))
        if len(entity_ids) > 1:
            redirect_uri = self.check_value_supplied(None, message.TOO_MANY_ENTITIES_SEL)
        else:
            entity_id    = entity_ids[0] if len(entity_ids) == 1 else None
            if "new" in request.POST:
                redirect_uri = self.view_uri(
                    "AnnalistEntityDefaultNewView", 
                    coll_id=coll_id, type_id=type_id, action="new"
                    ) + continuation
            if "copy" in request.POST:
                redirect_uri = (
                    self.check_value_supplied(entity_id, message.NO_ENTITY_FOR_COPY) or
                    ( self.view_uri(
                        "AnnalistEntityDefaultEditView", 
                        coll_id=coll_id, type_id=type_id, entity_id=entity_id, action="copy"
                        ) + continuation)
                    )
            if "edit" in request.POST:
                redirect_uri = (
                    self.check_value_supplied(entity_id, message.NO_ENTITY_FOR_EDIT) or
                    ( self.view_uri(
                        "AnnalistEntityDefaultEditView", 
                        coll_id=coll_id, type_id=type_id, entity_id=entity_id, action="edit"
                       ) + continuation)
                    )
            if "delete" in request.POST:
                redirect_uri = (
                    self.check_value_supplied(entity_id, message.NO_ENTITY_FOR_DELETE)
                    )
                if not redirect_uri:
                    # Get user to confirm action before actually doing it
                    complete_action_uri = self.view_uri(
                        "AnnalistEntityDataDeleteView", 
                        coll_id=coll_id, type_id=type_id # , entity_id=entity_id
                        )
                    delete_params = dict_querydict(
                        { "entity_delete": ["Delete"]
                        , "entity_id":     [entity_id]
                        })
                    return (
                        self.authorize("DELETE") or
                        ConfirmView.render_form(request,
                            action_description=     message.REMOVE_ENTITY_DATA%(entity_id, type_id, coll_id),
                            complete_action_uri=    complete_action_uri,
                            action_params=          delete_params,
                            cancel_action_uri=      self.get_request_path(),
                            title=                  self.site_data()["title"]
                            )
                        )
            if "search" in request.POST:
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
            if "list_view" in request.POST:
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
            if "default_view" in request.POST:
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
            if "customize" in request.POST:
                raise Annalist_Error(request.POST, "@@TODO DefaultList unimplemented "+self.get_request_path())
        if redirect_uri:
            return HttpResponseRedirect(redirect_uri)
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(continuation_uri+err_values)

#   -------------------------------------------------------------------------------------------
#
#   Entity delete confirmation response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDataDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed entity data deletion,
    anticipated to be requested from a data list or record view.
    """
    def __init__(self):
        super(EntityDataDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id, type_id):
        """
        Process options to complete action to remove an entity data record.
        """
        log.debug("EntityDataDeleteConfirmedView.post: %r"%(request.POST))
        if "entity_delete" in request.POST:
            entity_id  = request.POST['entity_id']
            coll       = self.collection(coll_id)
            recordtype = self.recordtype(coll_id, type_id)
            recorddata = self.recordtypedata(coll_id, type_id)
            messages  = (
                { 'entity_removed': message.ENTITY_DATA_REMOVED%(entity_id, type_id, coll_id)
                })
            continuation_uri = (
                request.POST.get('continuation_uri', None) or
                self.view_uri("AnnalistEntityDefaultListType", coll_id=coll_id, type_id=type_id)
                )
            return self.confirm_form_respose(
                request, recorddata, entity_id, recorddata.remove_entity, 
                messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
