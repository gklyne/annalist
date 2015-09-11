"""
Annalist record field description
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
from annalist.identifiers       import ANNAL
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordField(EntityData):

    _entitytype     = ANNAL.CURIE.Field
    _entitytypeid   = "_field"
    _entityview     = layout.COLL_FIELD_VIEW
    _entitypath     = layout.COLL_FIELD_PATH
    _entityaltpath  = layout.SITE_FIELD_PATH
    _entityfile     = layout.FIELD_META_FILE
    _entityref      = layout.META_FIELD_REF

    def __init__(self, parent, field_id, altparent=None):
        """
        Initialize a new RecordField object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        field_id    the local identifier for the record view
        altparent   is a site object to search for this new entity,
                    allowing site-wide RecordField values to be found.
        """
        log.debug("RecordField %s"%(field_id))
        # assert altparent, "RecordField instantiated with no altparent"
        super(RecordField, self).__init__(parent, field_id, altparent=altparent)
        return

    def _migrate_values(self, entitydata):
        """
        Field description entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exctly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        migration_map = (
            [ (ANNAL.CURIE.options_typeref,  ANNAL.CURIE.field_ref_type       )
            , (ANNAL.CURIE.restrict_values,  ANNAL.CURIE.field_ref_restriction)
            , (ANNAL.CURIE.target_field,     ANNAL.CURIE.field_ref_field      )
            ])
        for old_key, new_key in migration_map:
            if old_key in entitydata:
                entitydata[new_key] = entitydata.pop(old_key)
        # Default render type to "Text"
        if ANNAL.CURIE.field_render_type not in entitydata:
            entitydata[ANNAL.CURIE.field_render_type] = "Text"
        # Calculate mode from other fields if not defined
        val_render = entitydata[ANNAL.CURIE.field_render_type]
        val_type  = entitydata.get(ANNAL.CURIE.field_value_type, None)
        ref_type  = entitydata.get(ANNAL.CURIE.field_ref_type, None)
        ref_field = entitydata.get(ANNAL.CURIE.field_ref_field, None)
        if ANNAL.CURIE.field_value_mode in entitydata:
            val_mode = entitydata[ANNAL.CURIE.field_value_mode]
        else:
            val_mode  = "Value_direct"
            if ref_type and ref_field:
                val_mode = "Value_field"
            elif val_render == "RefMultifield":
                val_mode = "Value_entity"
            elif val_type == ANNAL.CURIE.Import or val_render == "URIImport":
                val_mode = "Value_import"
            elif val_type == ANNAL.CURIE.Upload or val_render == "FileUpload":
                val_mode = "Value_upload"
            entitydata[ANNAL.CURIE.field_value_mode] = val_mode
        # Consistency checks
        if val_mode == "Value_field":
            if ( not (ref_type and ref_field) ):
               log.warning(
                    "RecordField %s: Value_field mode requires values for %s and %s"%( 
                        entitydata[ANNAL.CURIE.id], 
                        ANNAL.CURIE.field_ref_type, 
                        ANNAL.CURIE.field_ref_field
                        )
                    )
        elif val_mode == "Value_entity":
            if not ref_type:
               log.warning(
                    "RecordField %s: Value_entity val_mode requires value for %s"%( 
                        entitydata[ANNAL.CURIE.id], 
                        ANNAL.CURIE.field_ref_type, 
                        )
                    )
            if ref_field:
               log.warning(
                    "RecordField %s: Value_entity mode should not define value for %s"%( 
                        entitydata[ANNAL.CURIE.id], 
                        ANNAL.CURIE.field_ref_field
                        )
                    )
        # Return result
        return entitydata

# End.
