"""
Entity list view
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

# from annalist.models.collection     import Collection
# from annalist.models.recordtype     import RecordType
# from annalist.models.recordtypedata import RecordTypeData

from annalist.views.confirm         import ConfirmView, dict_querydict
from annalist.views.entityeditbase  import EntityDeleteConfirmedBaseView

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
            http_response = (
                get_coll_data(coll_id, self.get_request_host()) or
                get_type_data(type_id)
                )
            # .................

            entity_id  = request.POST['entity_id']
            coll       = self.collection(coll_id)
            recordtype = self.recordtype(coll_id, type_id)
            recorddata = self.recordtypedata(coll_id, type_id)
            messages  = (
                { 'entity_removed': message.ENTITY_DATA_REMOVED%(entity_id, type_id, coll_id)
                })
            continuation_uri = (
                request.POST.get('continuation_uri', None) or
                self.view_uri("AnnalistEntityDefaultListAll", coll_id=coll_id)
                )
            return self.confirm_form_respose(
                request, recorddata, entity_id, recorddata.remove_entity, 
                messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
