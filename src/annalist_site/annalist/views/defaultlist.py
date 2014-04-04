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

    def get_list_id(self, type_id, list_id):
        return (
            super(EntityDefaultListView, self).get_list_id(type_id, list_id) or
            ("Default_list" if type_id else "Default_list_all")
            )

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
