"""
Annalist record type

A record type is represented by:
- an ID (slug)
- a URI
- a name/label
- a description
- ...
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import os.path
import shutil

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordType(EntityData):

    _entitytype     = ANNAL.CURIE.Type
    _entitytypeid   = layout.TYPE_TYPEID
    _entityroot     = layout.COLL_TYPE_PATH
    _entityview     = layout.COLL_TYPE_VIEW
    _entityfile     = layout.TYPE_META_FILE

    def __init__(self, parent, type_id):
        """
        Initialize a new RecordType object, without metadta (yet).

        parent      is the parent collection in which the type is defined.
        type_id     the local identifier for the record type
        """
        super(RecordType, self).__init__(parent, type_id)
        self._parent = parent
        # log.debug("RecordType %s: dir %s"%(type_id, self._entitydir))
        # log.debug("RecordType %s: uri %s"%(type_id, self._entityurl))
        return

    def _migrate_values(self, entitydata):
        """
        Type definition entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exctly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        # Convert representation of supertype URIs to use repeated property instead of 
        # reference to an RDF list.
        if ANNAL.CURIE.supertype_uris in entitydata:
            if isinstance(entitydata[ANNAL.CURIE.supertype_uris], list):
                entitydata[ANNAL.CURIE.supertype_uri] = (
                    [ {'@id': st[ANNAL.CURIE.supertype_uri] } 
                      for st in entitydata[ANNAL.CURIE.supertype_uris]
                    ])
                del entitydata[ANNAL.CURIE.supertype_uris]
        # Return result
        return entitydata

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Post-update processing.

        This method is called when an entity has been created or updated.
        """
        self._parent.cache_add_type(self)
        return entitydata

    def _post_remove_processing(self, post_update_flags):
        """
        Post-remove processing.

        This method is called when an entity has been removed.  
        """
        self._parent.cache_remove_type(self.get_id())
        return

# End.
