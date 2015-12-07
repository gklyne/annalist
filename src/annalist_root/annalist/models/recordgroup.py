"""
Annalist field group group
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

class RecordGroup(EntityData):

    _entitytype     = ANNAL.CURIE.Field_group
    _entitytypeid   = "_group"
    _entityview     = layout.COLL_GROUP_VIEW
    _entitypath     = layout.COLL_GROUP_PATH
    _entityfile     = layout.GROUP_META_FILE
    _entityref      = layout.META_GROUP_REF

    def __init__(self, parent, group_id):
        """
        Initialize a new RecordGroup object, without metadta (yet).

        parent      is the parent entity from which the field group is descended.
        group_id    the local identifier for the field group
        """
        super(RecordGroup, self).__init__(parent, group_id)
        self._parent = parent
        log.debug("RecordGroup %s: dir %s"%(group_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _post_update_processing(self, entitydata):
        """
        Default post-update processing.

        This method is called when a RecordGroup entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the group belongs.
        """
        self._parent.generate_coll_jsonld_context()
        return entitydata

# End.
