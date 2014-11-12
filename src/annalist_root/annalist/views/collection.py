"""
Annalist collection views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf import settings
from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import resolve, reverse

from annalist                   import message
from annalist.exceptions        import Annalist_Error

from annalist.models.site       import Site
from annalist.models.collection import Collection
from annalist.models.recordtype import RecordType
from annalist.models.recordview import RecordView
from annalist.models.recordlist import RecordList

from annalist.views.uri_builder import uri_with_params
from annalist.views.displayinfo import DisplayInfo
from annalist.views.generic     import AnnalistGenericView
from annalist.views.confirm     import ConfirmView


class CollectionView(AnnalistGenericView):
    """
    View class to handle requests to display an Annalist collection.

    Redirects to default list view.
    """
    def __init__(self):
        super(CollectionView, self).__init__()
        return

    def get(self, request, coll_id):
        """
        Form for displaying the current collection 
        """
        return HttpResponseRedirect(self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id))


class CollectionEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection edit URI
    """
    def __init__(self):
        super(CollectionEditView, self).__init__()
        return

    def collection_view_setup(self, coll_id, action):
        """
        Assemble display information for collection view request handler
        """
        viewinfo = DisplayInfo(self, action)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.check_authorization(action)
        return viewinfo

    # GET

    def get(self, request, coll_id):
        """
        Form for editing (customizing) the current collection 
        """
        def resultdata(viewinfo):
            coll = viewinfo.collection
            context = (
                { 'continuation_url':   continuation_next.get('continuation_url', "")
                , 'types':              sorted( [t.get_id() for t in coll.types(include_alt=False)] )
                , 'lists':              sorted( [l.get_id() for l in coll.lists(include_alt=False)] )
                , 'views':              sorted( [v.get_id() for v in coll.views(include_alt=False)] )
                , 'select_rows':        "6"
                })
            context.update(viewinfo.context_data())
            return context
        viewinfo = self.collection_view_setup(coll_id, "view")
        if viewinfo.http_response:
            return viewinfo.http_response
        continuation_next, continuation_here = self.continuation_urls(
            request.GET,
            None  # self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id)
            )
        return (
            self.render_html(resultdata(viewinfo), 'annalist_collection_edit.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id):
        """
        Update some aspect of the current collection
        """
        # Note: in many cases, this function redirects to a URI that displays a form
        #       to gather further details of values to update.  Values returned by
        #       POST to this view are then passed as URI segments in the GET request
        #       that renders the form.  Maybe there's an easier way than all this 
        #       URI-wrangling?
        redirect_uri  = None
        http_response = None
        continuation_next, continuation_here = self.continuation_urls(
            request.POST,
            None  # self.view_uri("AnnalistSiteView")
            )
        if "close" in request.POST:
            redirect_uri = continuation_next.get('continuation_url', self.view_uri("AnnalistSiteView"))
        # Check "config" authorization
        viewinfo = self.collection_view_setup(coll_id, "config")
        if viewinfo.http_response:
            return viewinfo.http_response
        # Record types
        type_id = request.POST.get('typelist', None)
        if "type_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_type", "Type_view", 
                continuation_here
                )
        if "type_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_type", "Type_view", type_id, 
                message.NO_TYPE_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "type_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_type", "Type_view", type_id, 
                message.NO_TYPE_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "type_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, type_id, 
                message.NO_TYPE_FOR_DELETE, 
                message.REMOVE_RECORD_TYPE, 
                "AnnalistRecordTypeDeleteView",
                continuation_next)
        # List views
        list_id = request.POST.get('listlist', None)
        if "list_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_list", "List_view", 
                continuation_here
                )
        if "list_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_list", "List_view", list_id, 
                message.NO_LIST_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "list_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_list", "List_view", list_id, 
                message.NO_LIST_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "list_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, list_id, 
                message.NO_LIST_FOR_DELETE, 
                message.REMOVE_RECORD_LIST, 
                "AnnalistRecordListDeleteView",
                continuation_next)
        # Record views
        view_id = request.POST.get('viewlist', None)
        if "view_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_view", "View_view", 
                continuation_here
                )
        if "view_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_view", "View_view", view_id, 
                message.NO_VIEW_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "view_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_view", "View_view", view_id, 
                message.NO_VIEW_FOR_COPY, 
                continuation_here, continuation_next
                )
        if "view_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, view_id, 
                message.NO_VIEW_FOR_DELETE, 
                message.REMOVE_RECORD_VIEW, 
                "AnnalistRecordViewDeleteView",
                continuation_next)
        # Invoke selected view and/or render status response
        if redirect_uri:
            http_response = http_response or HttpResponseRedirect(redirect_uri)
        if http_response:
            return http_response
        raise Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())

    # POST helper methods

    def item_new_uri(self, coll_id, type_id, view_id, continuation_here):
        redirect_uri = uri_with_params(
            self.view_uri("AnnalistEntityNewView", 
                coll_id=coll_id, view_id=view_id, type_id=type_id, action="new"
                ),
            continuation_here
            )
        return redirect_uri

    def item_edit_copy_uri(self,
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_next, action):
        redirect_uri = (
            self.check_value_supplied(entity_id, no_entity_msg, continuation_next)
            or
            uri_with_params(
                self.view_uri("AnnalistEntityEditView", action=action, 
                    coll_id=coll_id, view_id=view_id, type_id=type_id, entity_id=entity_id
                    ),
                continuation_here
                )
            )
        return redirect_uri

    def item_copy_uri(self, 
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_next):
        redirect_uri = self.item_edit_copy_uri(
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_next,
            "copy")
        return redirect_uri

    def item_edit_uri(self,
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_next):
        redirect_uri = self.item_edit_copy_uri(
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_next,
            "edit")
        return redirect_uri

    def item_delete_response(self, 
            coll_id, entity_id, 
            no_entity_msg, 
            confirm_msg, 
            complete_action_view,
            continuation_next):
        redirect_uri  = None
        http_response = None
        if entity_id:
            # Get user to confirm action before actually doing it
            confirmed_action_uri = self.view_uri(
                complete_action_view, coll_id=coll_id
                )
            message_vals = {'id': entity_id, 'coll_id': coll_id}
            http_response = (
                ConfirmView.render_form(self.request,
                    action_description=     confirm_msg%message_vals,
                    confirmed_action_uri=   confirmed_action_uri,
                    action_params=          self.request.POST,
                    cancel_action_uri=      self.get_request_path(),
                    title=                  self.site_data()["title"]
                    )
                )
        else:
            redirect_uri = (
                self.check_value_supplied(
                    entity_id, no_entity_msg,
                    continuation_next
                    )
                )
        return redirect_uri, http_response

# End.
