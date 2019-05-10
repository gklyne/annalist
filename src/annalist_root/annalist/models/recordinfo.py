"""
Annalist general information entity (used for displaying arbitrary information)
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2019, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import os.path
import shutil

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL, RDFS, OWL
from annalist                   import util
from annalist.models.entitydata import EntityData

class RecordInfo(EntityData):

    _entitytype     = ANNAL.CURIE.Information
    _entitytypeid   = layout.INFO_TYPEID
    _entityroot     = layout.COLL_INFO_PATH
    _entityview     = layout.COLL_INFO_VIEW
    _entityfile     = layout.INFO_META_FILE

    def __init__(self, parent, info_id):
        """
        Initialize a new RecordInfo object, without metadata (yet).

        parent      is the parent collection in which the information is defined.
        info_id     the local identifier for the information.
        """
        super(RecordInfo, self).__init__(parent, info_id)
        self._parent = parent
        # log.debug("RecordInfo %s: dir %s"%(info_id, self._entitydir))
        return

# End.
