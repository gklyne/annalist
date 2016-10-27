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
from annalist.models.entitydata import EntityData

class RecordTypeData(Entity):

    _entitytype     = ANNAL.CURIE.Type_Data
    _entitytypeid   = layout.TYPEDATA_TYPEID
    _entityview     = layout.COLL_TYPEDATA_VIEW
    _entitypath     = layout.COLL_TYPEDATA_PATH
    _entityfile     = layout.TYPEDATA_META_FILE
    _baseref        = layout.TYPEDATA_COLL_BASE_REF
    _contextref     = layout.TYPEDATA_CONTEXT_FILE

    def __init__(self, parent, type_id):
        """
        Initialize a new RecordTypeData object, without metadata.

        parent      is the parent collection from which the type data is descended.
        type_id     the local identifier (slug) for the record type
        """
        # @@
        # log.info(
        #     "@@ RecordTypeData.__init__ id %s, _entitytypeid %s, parent_id %s"%
        #     (type_id, self._entitytypeid, parent.get_id())
        #     )
        # @@
        self._entityref = layout.COLL_BASE_TYPEDATA_REF%{'id': type_id}
        super(RecordTypeData, self).__init__(parent, type_id)
        return

    # @@TODO remove this method and re-test (now redundant, handled through Entity class)
    def entities(self):
        """
        Generator enumerates and returns records of given type
        """
        for f in self._children(EntityData):
            log.debug("RecordTypeData.entities: f %s"%f)            
            e = EntityData.load(self, f)
            if e:
                yield e
        return

    def remove_entity(self, entity_id):
        t = EntityData.remove(self, entity_id)
        return t

    def _local_find_alt_parents(self):
        """
        Returns a list of alternative parents for the current inheritance branch only;
        i.e. does not attempt to follow altparent chains in referenced trees.
        (That is handled by `_find_alt_parents`.)

        This method overrides the method in Entity to take account of the need to
        look beyond the immediate RecordTypeData instance to follow links to collections
        from which data is inherited.
        """
        type_id  = self.get_id()
        altcolls = self._parent._local_find_alt_parents()
        # log.info("@@ RecordTypeData._local_find_alt_parents altcolls %r"%(altcolls))
        altdatas = [ alt for alt in [ RecordTypeData.load(c, type_id) for c in altcolls ] if alt ]
        # log.info("@@ RecordTypeData._local_find_alt_parents %r"%([p.get_id for p in altdatas]))
        return altdatas

# End.
