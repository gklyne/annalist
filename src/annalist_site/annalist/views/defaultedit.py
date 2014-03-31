"""
Default record view/edit
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import copy

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings

from annalist.models.entitydata     import EntityData

from annalist.views.entityedit      import GenericEntityEditView

#   -------------------------------------------------------------------------------------------
#
#   Entity edit default view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDefaultEditView(GenericEntityEditView):
    """
    View class for default record edit view
    """

    def __init__(self):
        super(EntityDefaultEditView, self).__init__(
            view_id="Default_view", entity_class=EntityData
            )
        return

# End.
