"""
Annalist record type

A record type is represented by:
- an ID (slug)
- a URI
- a name/label
- a description
- ...
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

class RecordType(Entity):

    _entitytype     = ANNAL.CURIE.RecordType
    _entitypath     = layout.COLL_TYPE_PATH
    _entityaltpath  = layout.SITE_TYPE_PATH
    _entityfile     = layout.TYPE_META_FILE
    _entityref      = layout.META_TYPE_REF

    def __init__(self, parent, type_id, altparent=None):
        """
        Initialize a new RecordType object, without metadta (yet).

        parent      is the parent entity from which the type is descended.
        type_id     the local identifier for the record type
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordType values to be found.
        """
        super(RecordType, self).__init__(parent, type_id, altparent)
        log.debug("RecordType %s: dir %s, alt %s"%(type_id, self._entitydir, self._entityaltdir))
        return

# End.
