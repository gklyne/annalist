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
        # @@TODO: later, read and redirect to the currently selected default view
        return HttpResponseRedirect(self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id))


class CollectionEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection edit URI
    """
    def __init__(self):
        super(CollectionEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id):
        """
        Form for editing (customizing) the current collection 
        """
        def resultdata():
            coll = self.collection
            context = (
                { 'title':              self.site_data()["title"]
                , 'continuation_uri':   continuation_uri
                , 'coll_id':            coll_id
                , 'types':              sorted( [t.get_id() for t in coll.types(include_alt=False)] )
                , 'lists':              sorted( [l.get_id() for l in coll.lists(include_alt=False)] )
                , 'views':              sorted( [v.get_id() for v in coll.views(include_alt=False)] )
                , 'select_rows':        "6"
                })
            return context
        http_response = self.get_coll_data(coll_id, self.get_request_host())
        if http_response:
            return http_response
        continuation_here, continuation_uri = self.continuation_uris(
            request.GET,
            self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id)
            )
        return (
            self.render_html(resultdata(), 'annalist_collection_edit.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id):
        """
        Update some aspect of the current collection
        """
        # Note: in many cases, this function redirects to a form that displays a form
        #       to gather further details of values to update.  Values returned by
        #       POST to this view are then passed as URI segments in the GET request
        #       that renders the form.  Maybe there's an easier way that all this 
        #       URI-wrangling?
        redirect_uri = None
        continuation_here, continuation_uri = self.continuation_uris(request.POST,
            # self.view_uri("AnnalistEntityListAllView", coll_id=coll_id)
            self.view_uri("AnnalistSiteView")
            )
        # continuation = "?continuation_uri=%s"%(self.get_request_uri())
        type_id = request.POST.get('typelist', None)
        if "type_new" in request.POST:
            redirect_uri = self.view_uri(
                "AnnalistRecordTypeNewView", coll_id=coll_id, action="new"
                ) + continuation_here
        if "type_copy" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_COPY) or
                ( self.view_uri(
                    "AnnalistRecordTypeCopyView", coll_id=coll_id, type_id=type_id, action="copy"
                    ) + continuation_here)
                )
        if "type_edit" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_EDIT) or
                ( self.view_uri(
                    "AnnalistRecordTypeEditView", coll_id=coll_id, type_id=type_id, action="edit"
                    ) + continuation_here)
                )
        if "type_delete" in request.POST:
            if type_id:
                # Get user to confirm action before actually doing it
                complete_action_uri = self.view_uri("AnnalistRecordTypeDeleteView", coll_id=coll_id)
                return (
                    self.authorize("DELETE") or
                    ConfirmView.render_form(request,
                        action_description=     message.REMOVE_RECORD_TYPE%(type_id, coll_id),
                        complete_action_uri=    complete_action_uri,
                        action_params=          request.POST,
                        cancel_action_uri=      self.get_request_path(),
                        title=                  self.site_data()["title"]
                        )
                    )
            else:
                redirect_uri = (
                    self.check_value_supplied(type_id, message.NO_TYPE_FOR_DELETE)
                    )
        if "close" in request.POST:
            redirect_uri = request.POST.get('continuation_uri',
                self.view_uri("AnnalistSiteView")
                )
        if redirect_uri:
            return HttpResponseRedirect(redirect_uri)
        raise Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())

# End.
