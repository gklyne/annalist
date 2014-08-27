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

from annalist.views.entityedit      import GenericEntityEditView

#   -------------------------------------------------------------------------------------------
#
#   Entity edit default view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDefaultEditView(GenericEntityEditView):
    """
    View class for default record edit view

    Currently, this class is somewhat redundant, but future developments are 
    expected to provide content negotiation on this URI.
    """

    def __init__(self):
        super(EntityDefaultEditView, self).__init__()
        return

# End.
