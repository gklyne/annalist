"""
Annalist record view

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

class RecordView(Entity):

    _entitytype = ANNAL.CURIE.RecordView
    _entitypath = layout.COLL_VIEW_PATH
    _entityfile = layout.VIEW_META_FILE
    _entityref  = layout.META_VIEW_REF

    def __init__(self, parent, view_id):
        """
        Initialize a new RecordView object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        view_id     the local identifier for the record view
        """
        super(RecordView, self).__init__(parent, view_id)
        return

# End.
