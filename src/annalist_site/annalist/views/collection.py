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

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

from annalist.views.generic     import AnnalistGenericView
from annalist.views.confirm     import ConfirmView

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
        Create a rendering of the current collection.
        """
        def resultdata():
            coll = self.collection(coll_id)
            context = (
                { 'title':          self.site_data()["title"]
                , 'coll_id':        coll_id
                , 'types':          sorted( [t.get_id() for t in coll.types()] )
                , 'lists':          sorted( [l.get_id() for l in coll.lists()] )
                , 'views':          sorted( [v.get_id() for v in coll.views()] )
                , 'select_rows':    "6"
                })
            return context
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message=message.COLLECTION_NOT_EXISTS%(coll_id)))
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
        continuation = "?continuation_uri=%s"%(self.get_request_uri())
        type_id = request.POST.get('typelist', None)
        if "type_new" in request.POST:
            redirect_uri = self.view_uri(
                "AnnalistRecordTypeNewView", coll_id=coll_id, action="new"
                ) + continuation
        if "type_copy" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_COPY) or
                ( self.view_uri(
                    "AnnalistRecordTypeCopyView", coll_id=coll_id, type_id=type_id, action="copy"
                    ) + continuation)
                )
        if "type_edit" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_EDIT) or
                ( self.view_uri(
                    "AnnalistRecordTypeEditView", coll_id=coll_id, type_id=type_id, action="edit"
                    ) + continuation)
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
            redirect_uri = self.view_uri("AnnalistSiteView")
        if redirect_uri:
            return HttpResponseRedirect(redirect_uri)
        raise Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())

# End.
