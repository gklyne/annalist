"""
Annalist record view delete confirmation response handler
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
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import util

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView

from annalist.views.generic         import AnnalistGenericView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

class RecordViewDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed record view deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordViewDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record view from a collection
        """
        log.debug("RecordViewDeleteConfirmedView.post: %r"%(request.POST))
        if "view_delete" in request.POST:
            http_response = (
                self.get_coll_data(coll_id, self.get_request_host()) or
                self.form_edit_auth("delete", self.collection.get_uri())
                )
            if http_response:
                return http_response
            view_id   = request.POST['viewlist']
            message_vals = {'id': view_id, 'coll_id': coll_id}
            messages  = (
                { 'entity_removed': message.RECORD_VIEW_REMOVED%message_vals
                })
            continuation_uri = self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.confirm_form_respose(
                request, view_id, 
                self.collection.remove_view, messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
