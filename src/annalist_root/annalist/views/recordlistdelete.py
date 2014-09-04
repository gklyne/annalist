"""
Annalist record list delete confirmation response handler
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

from annalist.views.entitydeletebase    import EntityDeleteConfirmedBaseView

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
        Complete removal of a record view from a collection
        """
        log.debug("RecordListDeleteConfirmedView.post: %r"%(request.POST))
        if "list_delete" in request.POST:
            return self.complete_remove_entity(
                coll_id, "_list", request.POST['listlist'], 
                self.view_uri("AnnalistCollectionEditView", coll_id=coll_id),
                request.POST.dict()
                )
        return self.error(self.error400values())

# End.
