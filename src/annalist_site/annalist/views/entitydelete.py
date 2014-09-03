"""
Entity list view
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

#   -------------------------------------------------------------------------------------------
#
#   Entity delete confirmation response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDataDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed entity data deletion,
    anticipated to be requested from a data list or record view.
    """
    def __init__(self):
        super(EntityDataDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id, type_id):
        """
        Process options to complete action to remove an entity data record.
        """
        log.debug("EntityDataDeleteConfirmedView.post: %r"%(request.POST))
        if "entity_delete" in request.POST:
            entity_id = request.POST['entity_id']
            continuation_url = (
                request.POST.get('completion_url', None) or
                self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id)
                )
            continuation_url_params = continuation_params(request.POST.dict())
            # log.info("continuation_params %r"%(continuation_params,))
            return self.complete_remove_entity(
                coll_id, type_id, entity_id, continuation_url, continuation_url_params
                )
        return self.error(self.error400values())

# End.
