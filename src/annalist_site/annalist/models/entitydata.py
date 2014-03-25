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

    _entitytype = ANNAL.CURIE.EntityData
    _entitypath = layout.TYPEDATA_ENTITY_PATH
    _entityfile = layout.ENTITY_DATA_FILE
    _entityref  = layout.DATA_ENTITY_REF

    def __init__(self, parent, entity_id):
        """
        Initialize a new Entity Data object, without metadata.

        parent      is the parent collection (RecordType) from which the entity is descended.
        entity_id   the local identifier (slug) for the data record
        """
        super(EntityData, self).__init__(parent, entity_id)
        return

# End.
