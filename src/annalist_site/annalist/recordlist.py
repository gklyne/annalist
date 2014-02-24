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
from annalist.entity            import Entity

class RecordList(Entity):

    _entitytype = ANNAL.CURIE.RecordList
    _entitypath = layout.COLL_LIST_PATH
    _entityfile = layout.LIST_META_FILE
    _entityref  = layout.META_LIST_REF

    def __init__(self, parent, list_id):
        """
        Initialize a new RecordList object, without metadta (yet).

        parent      is the parent entity from which the list is descended.
        list_id     the local identifier for the record list
        """
        super(RecordList, self).__init__(parent, list_id)
        return

# End.
