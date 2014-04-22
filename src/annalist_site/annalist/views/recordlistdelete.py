"""
Annalist record list delete confirmation response handler
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
from annalist.models.recordlist     import RecordList

from annalist.views.generic         import AnnalistGenericView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

class RecordListDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed record view deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordListDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record view from a collection
        """
        log.debug("RecordListDeleteConfirmedView.post: %r"%(request.POST))
        if "list_delete" in request.POST:
            http_response = (
                self.get_coll_data(coll_id, self.get_request_host()) or
                self.form_edit_auth("delete", self.collection.get_uri())
                )
            if http_response:
                return http_response
            list_id   = request.POST['listlist']
            message_vals = {'id': list_id, 'coll_id': coll_id}
            messages  = (
                { 'entity_removed': message.RECORD_LIST_REMOVED%message_vals
                })
            continuation_uri = self.list_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.confirm_form_respose(
                request, list_id, 
                self.collection.remove_list, messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
