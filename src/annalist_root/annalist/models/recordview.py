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
    _entityfile     = layout.VIEW_META_FILE
    _entityref      = layout.META_VIEW_REF

    def __init__(self, parent, view_id):
        """
        Initialize a new RecordView object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        view_id     the local identifier for the record view
        """
        super(RecordView, self).__init__(parent, view_id)
        self._parent = parent
        log.debug("RecordView %s: dir %s"%(view_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _post_update_processing(self, entitydata):
        """
        Default post-update processing.

        This method is called when a RecordView entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the entity belongs.
        """
        self._parent.generate_coll_jsonld_context()
        return entitydata

# End.
