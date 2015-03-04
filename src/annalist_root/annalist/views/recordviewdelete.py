"""
Annalist record view delete confirmation response handler
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
            return self.complete_remove_entity(
                coll_id, "_view", request.POST['viewlist'], 
                self.view_uri("AnnalistCollectionEditView", coll_id=coll_id),
                request.POST.dict()
                )
        return self.error(self.error400values())

# End.
