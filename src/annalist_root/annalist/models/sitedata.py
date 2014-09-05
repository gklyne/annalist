"""
Annalist site data

Site data is an alternative location for generic Annalist metatadata 
(e.g. type and view definitions, etc.) that are common across all 
collections (and even installations).
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
from annalist.models.recordtype import RecordType
from annalist.models.recordview import RecordView
from annalist.models.recordlist import RecordList

class SiteData(Entity):

    _entitytype     = ANNAL.CURIE.SiteData
    _entitytypeid   = "_sitedata"
    _entityview     = layout.SITEDATA_VIEW
    _entitypath     = layout.SITEDATA_PATH
    _entityfile     = layout.SITEDATA_META_FILE
    _entityref      = layout.META_SITEDATA_REF

    def __init__(self, parent):
        """
        Initialize a new SiteData object, without metadta (yet).

        parent      is the parent site from which the new collection is descended.
        """
        super(SiteData, self).__init__(parent, layout.SITEDATA_DIR, idcheck=False)
        return

    # Record types

    def types(self):
        """
        Generator enumerates and returns record types that may be stored
        """
        for f in self._children(RecordType):
            t = RecordType.load(self, f)
            if t:
                yield t
        return

    # Record views

    def views(self):
        """
        Generator enumerates and returns record views that may be stored
        """
        for f in self._children(RecordView):
            t = RecordView.load(self, f)
            if t:
                yield t
        return

    # Record lists

    def lists(self):
        """
        Generator enumerates and returns record lists that may be stored
        """
        for f in self._children(RecordList):
            t = RecordList.load(self, f)
            if t:
                yield t
        return

# End.
