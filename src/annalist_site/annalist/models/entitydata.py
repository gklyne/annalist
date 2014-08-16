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

    def __init__(self, parent, entity_id, altparent=None):
        """
        Initialize a new Entity Data object, without metadata.

        parent      is the parent collection (RecordType) from which the entity is descended.
        entity_id   the local identifier (slug) for the data record
        altparent   is an alternative parent entity to search for this entity, using 
                    the alternative path for the entity type: this is used to augment 
                    explicitly created entities in a collection with site-wide 
                    installed metadata entites (i.e. types, views, etc.)
        """
        super(EntityData, self).__init__(parent, entity_id, altparent=altparent)
        self._entitytypeid  = self._entitytypeid or parent.get_id()
        self._entityviewuri = parent._entityuri+self._entityview%{'id': entity_id}
        log.debug("EntityData: _entityviewuri %s"%(self._entityviewuri))
        return

    # def get_view_uri(self, baseuri=""):
    #     """
    #     Return URI used to view entity data.  For metadata entities, this may be 
    #     different from the URI at which the resource is located, per get_uri().
    #     The intent is to provide a URI that works regardless of whether the metadata
    #     is stored as site-wide or collection-specific data.
    #     """
    #     return urlparse.urljoin(baseuri, self._entityviewuri)

# End.
