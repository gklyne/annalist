"""
Annalist record field description
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
from annalist.identifiers       import ANNAL
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordField(EntityData):

    _entitytype     = ANNAL.CURIE.Field
    _entitytypeid   = "_field"
    _entityview     = layout.COLL_FIELD_VIEW
    _entitypath     = layout.COLL_FIELD_PATH
    _entityaltpath  = layout.SITE_FIELD_PATH
    _entityfile     = layout.FIELD_META_FILE
    _entityref      = layout.META_FIELD_REF

    def __init__(self, parent, field_id, altparent=None):
        """
        Initialize a new RecordField object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        field_id    the local identifier for the record view
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordField values to be found.
        """
        log.debug("RecordField %s"%(field_id))
        # assert altparent, "RecordField instantiated with no altparent"
        super(RecordField, self).__init__(parent, field_id, altparent=altparent)
        return

# End.
