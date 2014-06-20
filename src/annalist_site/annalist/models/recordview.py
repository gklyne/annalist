"""
Annalist record view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordView(EntityData):

    _entitytype     = ANNAL.CURIE.View
    _entitytypeid   = "_view"
    _entityview     = layout.COLL_VIEW_VIEW
    _entitypath     = layout.COLL_VIEW_PATH
    _entityaltpath  = layout.SITE_VIEW_PATH
    _entityfile     = layout.VIEW_META_FILE
    _entityref      = layout.META_VIEW_REF

    def __init__(self, parent, view_id, altparent=None):
        """
        Initialize a new RecordView object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        view_id     the local identifier for the record view
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordView values to be found.
        """
        super(RecordView, self).__init__(parent, view_id, altparent)
        log.debug("RecordView %s: dir %s, alt %s"%(view_id, self._entitydir, self._entityaltdir))
        return

# End.
