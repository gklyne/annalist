"""
Annalist record type delete confirmation response handler
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

from annalist.views.uri_builder         import continuation_params
from annalist.views.entitydeletebase    import EntityDeleteConfirmedBaseView

class RecordTypeDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed record type deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordTypeDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record type from a collection
        """
        log.debug("RecordTypeDeleteConfirmedView.post: %r"%(request.POST))
        if "type_delete" in request.POST:
            # @@
            # entity_id = request.POST['typelist']
            # continuation_url = (
            #     request.POST.get('continuation_url', None) or
            #     self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            #     )
            # continuation_url_params = continuation_params(request.POST.dict())
            # return self.complete_remove_entity(
            #     coll_id, "_type", entity_id, continuation_url, continuation_url_params
            #     )
            # @@
            return self.complete_remove_entity(
                coll_id, "_type", request.POST['typelist'], 
                self.view_uri("AnnalistCollectionEditView", coll_id=coll_id),
                request.POST.dict()
                )
        return self.error(self.error400values())

# End.
