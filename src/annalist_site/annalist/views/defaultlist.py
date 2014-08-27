"""
Default record list view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.entitylist      import EntityGenericListView

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityDefaultListView(EntityGenericListView):
    """
    View class for default record list view

    Currently, this class is somewhat redundant, but future developments
    are expected to provide content negotiation on this URI.
    """

    def __init__(self):
        super(EntityDefaultListView, self).__init__()
        return

# End.
