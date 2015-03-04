"""
Annalist user delete confirmation response handler
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

class AnnalistUserDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed record type deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(AnnalistUserDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a user record from a collection
        """
        log.debug("AnnalistUserDeleteConfirmedView.post: %r"%(request.POST))
        if "type_delete" in request.POST:
            return self.complete_remove_entity(
                coll_id, "_user", request.POST['userlist'], 
                self.view_uri("AnnalistCollectionEditView", coll_id=coll_id),
                request.POST.dict()
                )
        return self.error(self.error400values())

# End.
