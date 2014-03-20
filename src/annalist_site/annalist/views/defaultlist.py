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
# from annalist.exceptions            import Annalist_Error
# from annalist.identifiers           import RDF, RDFS, ANNAL
# from annalist                       import util

# from annalist.site                  import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView


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

    # GET

    def get(self, request, coll_id=None, type_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("defaultedit.get: coll_id %s, type_id %s"%(coll_id, type_id))
        reqhost = self.get_request_host()
        if type_id:
            http_response = self.get_coll_type_data(coll_id, type_id, host=reqhost)
            self._list_id = "Default_list"
        else:
            http_response = self.get_coll_data(coll_id, host=reqhost)
            self._list_id       = "Default_list_all"
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
        log.debug("views.defaultlist.post %s"%(self.get_request_path()))
        # log.debug("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.debug("  form data %r"%(request.POST))
        reqhost = self.get_request_host()
        if type_id:
            http_response = self.get_coll_type_data(coll_id, type_id, host=reqhost)
        else:
            http_response = self.get_coll_data(coll_id, host=reqhost)
        if not http_response:
            http_response = self.form_edit_auth("list", self.collection._entityuri)
        if http_response:
            return http_response
        # Get key POST values
        continuation_uri     = request.POST.get('continuation_uri', 
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'continuation_uri': continuation_uri
            })
        messages = (
            { 
            })


        # Process form response and respond accordingly
        self._entityvaluemap = self.get_form_entityvaluemap(self._view_id)
        return self.form_response(
            request, action, self.recordtypedata, entity_id, orig_entity_id, 
            messages, context_extra_values
            )

    # Helper - handle list response
    def form_response(self, request, action, parent, entityid, orig_entityid, messages, context_extra_values):
        """
        Handle POST response from entity edit form.
        """
        log.debug("form_response: action %s"%(request.POST['action']))
        continuation_uri = context_extra_values['continuation_uri']
        if 'cancel' in request.POST:
            # log.debug("form_response: cancel")
            return HttpResponseRedirect(continuation_uri)
        # Check authorization
        auth_required = self.form_edit_auth(action, parent._entityuri)
        if auth_required:
            # log.debug("form_response: auth_required")            
            return auth_required
        # Check parent exists (still)
        if not parent._exists():
            # log.debug("form_response: not parent._exists()")
            return self.form_re_render(request, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )
        # Check response has valid type id
        if not util.valid_id(entityid):
            # log.debug("form_response: not util.valid_id('%s')"%entityid)
            return self.form_re_render(request, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        # Process response
        entityid_changed = (request.POST['action'] == "edit") and (entityid != orig_entityid)
        if 'save' in request.POST:
            log.debug(
                "form_response: save, action %s, entity_id %s, orig_entityid %s"
                %(request.POST['action'], entityid, orig_entityid)
                )
            # Check existence of type to save according to action performed
            if (request.POST['action'] in ["new", "copy"]) or entityid_changed:
                if self._entityclass.exists(parent, entityid):
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_exists']
                        )
            else:
                if not self._entityclass.exists(parent, entityid):
                    # This shouldn't happen, but just incase...
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_not_exists']
                        )
            # Create/update data now
            entity_initial_values = self.map_form_data_to_values(request.POST)
            self._entityclass.create(parent, entityid, entity_initial_values)
            # Remove old type if rename
            if entityid_changed:
                if self._entityclass.exists(parent, entityid):    # Precautionary
                    self._entityclass.remove(parent, orig_entityid)
            return HttpResponseRedirect(continuation_uri)
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(continuation_uri+err_values)




# End.
