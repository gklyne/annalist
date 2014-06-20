"""
Annalist record list

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
from annalist.models.entitydata import EntityData

class RecordList(EntityData):

    _entitytype     = ANNAL.CURIE.List
    _entitytypeid   = "_list"
    _entityview     = layout.COLL_LIST_VIEW
    _entitypath     = layout.COLL_LIST_PATH
    _entityaltpath  = layout.SITE_LIST_PATH
    _entityfile     = layout.LIST_META_FILE
    _entityref      = layout.META_LIST_REF

    def __init__(self, parent, list_id, altparent=None):
        """
        Initialize a new RecordList object, without metadta (yet).

        parent      is the parent entity from which the list is descended.
        list_id     the local identifier for the record list
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordType values to be found.
        """
        super(RecordList, self).__init__(parent, list_id, altparent)
        log.debug("RecordList %s: dir %s, alt %s"%(list_id, self._entitydir, self._entityaltdir))
        return

# End.
