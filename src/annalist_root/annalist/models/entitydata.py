"""
Collection of Annalist data records for a specified record type
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

class EntityData(Entity):

    _entitytype     = ANNAL.CURIE.EntityData
    _entitytypeid   = None
    _entityview     = layout.TYPEDATA_ENTITY_VIEW
    _entitypath     = layout.TYPEDATA_ENTITY_PATH
    _entityfile     = layout.ENTITY_DATA_FILE
    _entityref      = layout.DATA_ENTITY_REF
    _contextref     = layout.ENTITY_CONTEXT_FILE

    def __init__(self, parent, entity_id):
        """
        Initialize a new Entity Data object, without metadata.

        parent      is the parent collection (RecordType) from which the entity is descended.
        entity_id   the local identifier (slug) for the data record
        altparent   is an alternative parent entity to search for this entity, using 
                    the alternative path for the entity type: this is used to augment 
                    explicitly created entities in a collection with site-wide 
                    installed metadata entites (i.e. types, views, etc.)
        """
        super(EntityData, self).__init__(parent, entity_id)
        self._entitytypeid  = self._entitytypeid or parent.get_id()
        self._paramdict     = { 'type_id': self._entitytypeid, 'id': entity_id }
        self._entityviewuri = parent._entityurl+self._entityview%self._paramdict
        # self._entityref     = layout.CONTEXT_ENTITY_REF%self._paramdict
        # log.debug("EntityData: _entityviewuri %s"%(self._entityviewuri))
        return

    def _migrate_filenames(self):
        """
        Return filename migration list for entity data

        Returns a list of filenames used for the current entity type in previous
        versions of Annalist software.  If the expected filename is not found when 
        attempting to read a file, the _load_values() method calls this function to
        look for any of the filenames returned.  If found, the file is renamed
        to the current version filename.

        Default method returns an empty list.
        """
        return [layout.ENTITY_OLD_DATA_FILE]

# End.
