"""
Annalist record view
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
from annalist.util              import extract_entity_id


class RecordView(EntityData):

    _entitytype     = ANNAL.CURIE.View
    _entitytypeid   = layout.VIEW_TYPEID
    _entityview     = layout.COLL_VIEW_VIEW
    _entitypath     = layout.COLL_VIEW_PATH
    _entityfile     = layout.VIEW_META_FILE

    def __init__(self, parent, view_id):
        """
        Initialize a new RecordView object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        view_id     the local identifier for the record view
        """
        super(RecordView, self).__init__(parent, view_id)
        self._parent = parent
        # log.debug("RecordView %s: dir %s"%(view_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _migrate_values(self, entitydata):
        """
        View description entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exactly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        for f in entitydata[ANNAL.CURIE.view_fields]:
            field_id = extract_entity_id(f[ANNAL.CURIE.field_id])
            if field_id == "Field_render":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_render_type"
            if field_id == "Field_type":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_value_type"
        # Return result
        return entitydata

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Default post-update processing.

        This method is called when a RecordView entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the entity belongs.
        """
        self._parent.generate_coll_jsonld_context(flags=post_update_flags)
        return entitydata

# End.
