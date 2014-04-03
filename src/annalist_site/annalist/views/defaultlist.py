"""
Default record list view
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

from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

from annalist.views.confirm         import ConfirmView, dict_querydict
# from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView
from annalist.views.entitylist      import GenericEntityListView

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDefaultListView(GenericEntityListView):
    """
    View class for default record list view
    """

    def __init__(self):
        super(EntityDefaultListView, self).__init__(list_id=None)
        return

    # Helper functions

    def list_setup(self, coll_id, type_id):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection
            self.recordtype
            self.recordtypedata
            self._entityclass

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        reqhost = self.get_request_host()
        if type_id:
            http_response = self.get_coll_type_data(coll_id, type_id, host=reqhost)
            self._list_id = "Default_list"
        else:
            http_response = self.get_coll_data(coll_id, host=reqhost)
            self._list_id = "Default_list_all"
        return http_response

    def get_new_view_uri(self, coll_id, type_id):
        """
        Get URI for entity new view
        """
        return self.view_uri(
            "AnnalistEntityDefaultNewView", 
            coll_id=coll_id, type_id=type_id,
            action="new"
            )

    def get_edit_view_uri(self, coll_id, type_id, entity_id, action):
        """
        Get URI for entity edit or copy view
        """
        return self.view_uri(
                "AnnalistEntityDefaultEditView", 
                coll_id=coll_id, type_id=type_id, entity_id=entity_id,
                action=action
                )

# End.
