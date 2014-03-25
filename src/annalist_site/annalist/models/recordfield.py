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
# from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
# from annalist                   import util
from annalist.models.entity     import Entity

class RecordField(Entity):

    _entitytype = ANNAL.CURIE.RecordField
    _entitypath = layout.COLL_FIELD_PATH
    _entityfile = layout.FIELD_META_FILE
    _entityref  = layout.META_FIELD_REF

    def __init__(self, parent, field_id, altparent=None):
        """
        Initialize a new RecordField object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        field_id     the local identifier for the record view
        """
        log.debug("RecordField %s"%(field_id))
        assert altparent, "RecordField instantiated with no altparent"
        super(RecordField, self).__init__(parent, field_id, altparent=altparent)
        return

# End.
