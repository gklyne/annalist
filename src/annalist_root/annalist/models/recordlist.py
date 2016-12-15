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
from annalist.util              import extract_entity_id, make_type_entity_id

class RecordList(EntityData):

    _entitytype     = ANNAL.CURIE.List
    _entitytypeid   = layout.LIST_TYPEID
    _entityview     = layout.COLL_LIST_VIEW
    _entitypath     = layout.COLL_LIST_PATH
    _entityfile     = layout.LIST_META_FILE

    def __init__(self, parent, list_id):
        """
        Initialize a new RecordList object, without metadta (yet).

        parent      is the parent entity from which the list is descended.
        list_id     the local identifier for the record list
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordType values to be found.
        """
        super(RecordList, self).__init__(parent, list_id)
        self._parent = parent
        # log.debug("RecordList %s: dir %s"%(list_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _migrate_values(self, entitydata):
        """
        List description entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exactly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        for fkey, ftype in [(ANNAL.CURIE.display_type, "_enum_list_type")]:
            entitydata[fkey] = make_type_entity_id(
                ftype, extract_entity_id(entitydata[fkey])
                )
        for f in entitydata[ANNAL.CURIE.list_fields]:
            field_id = extract_entity_id(f[ANNAL.CURIE.field_id])
            if field_id == "Field_render":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_render_type"
            if field_id == "Field_type":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_value_type"
        # Return result
        return entitydata

# End.
