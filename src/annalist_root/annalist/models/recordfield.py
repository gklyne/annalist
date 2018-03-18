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

from annalist                       import layout
from annalist.identifiers           import ANNAL, RDFS
from annalist.models.entity         import Entity
from annalist.models.entitydata     import EntityData
from annalist.models.recordgroup    import RecordGroup, RecordGroup_migration
from annalist.util                  import (
    split_type_entity_id, extract_entity_id, make_type_entity_id
    )
from annalist.exceptions            import Annalist_Error

class RecordField(EntityData):

    _entitytype     = ANNAL.CURIE.Field
    _entitytypeid   = layout.FIELD_TYPEID
    _entityroot     = layout.COLL_FIELD_PATH
    _entityview     = layout.COLL_FIELD_VIEW
    _entityfile     = layout.FIELD_META_FILE

    def __init__(self, parent, field_id):
        """
        Initialize a new RecordField object, without metadta (yet).

        parent      is the parent collection to which the field belongs.
        field_id    the local identifier for the record field
        """
        # assert altparent, "RecordField instantiated with no altparent"
        super(RecordField, self).__init__(parent, field_id)
        self._parent = parent
        # log.debug("RecordField %s"%(field_id))
        return

    def get_property_uri(self):
        """
        Return field's property URI
        """
        return self.get(ANNAL.CURIE.property_uri, "@@undefined_property_uri@@")

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _map_entity_field_enum_val(self, entitydata, key, type_id, old_enum_val, new_enum_val):
        """
        Map enumerated value of specified type
        """
        if key in entitydata:
            type_id_here, enum_val_here = split_type_entity_id(entitydata[key])
            if type_id_here == type_id and enum_val_here == old_enum_val:
                entitydata[key] = make_type_entity_id(type_id, new_enum_val)
        return entitydata

    def _migrate_values(self, entitydata):
        """
        Field description entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exactly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        field_id = entitydata[ANNAL.CURIE.id]
        migration_map = (
            [ (ANNAL.CURIE.options_typeref,     ANNAL.CURIE.field_ref_type       )
            , (ANNAL.CURIE.restrict_values,     ANNAL.CURIE.field_ref_restriction)
            , (ANNAL.CURIE.target_field,        ANNAL.CURIE.field_ref_field      )
            , (ANNAL.CURIE.field_target_type,   ANNAL.CURIE.field_value_type     )
            ])
        entitydata = self._migrate_values_map_field_names(migration_map, entitydata)
        # Fix up enumerated values to use new enumeration type names
        field_enum_types = (
            [ (ANNAL.CURIE.field_render_type, "_enum_render_type")
            , (ANNAL.CURIE.field_value_mode,  "_enum_value_mode")
            ])
        for fkey, ftype in field_enum_types:
            if fkey in entitydata and entitydata[fkey]:
                entitydata[fkey] = make_type_entity_id(
                    ftype, extract_entity_id(entitydata[fkey])
                    )
        # If comment and no tooltip, create tooltip and update comment
        if (RDFS.CURIE.comment in entitydata) and (ANNAL.CURIE.tooltip not in entitydata):
            label   = entitydata.get(RDFS.CURIE.label, "Field '%s'"%field_id)
            comment = entitydata[RDFS.CURIE.comment]
            entitydata[ANNAL.CURIE.tooltip] = comment
            entitydata[RDFS.CURIE.comment]  = "# %s\r\n\r\n%s"%(label, comment)
        # If reference to field group, copy group field list inline
        if ANNAL.CURIE.group_ref in entitydata:
            group_type_id, group_id = split_type_entity_id(
                entitydata[ANNAL.CURIE.group_ref], default_type_id=layout.GROUP_TYPEID
                )
            if group_id != "":
                log.info("Migrating group reference %s in field %s"%(group_id, field_id))
                group_obj = RecordGroup_migration.load(self._parent, group_id)
                if not group_obj:
                    msg = (
                        "Failed to load group '%s' for field '%s' in collection '%s'"%
                        (group_id, field_id, self._parent.get_id())
                        )
                    log.warning(msg)
                    self.set_error(msg)
                    # raise Annalist_Error(msg)
                else:
                    field_value_type = entitydata[ANNAL.CURIE.field_value_type]
                    group_entity_type = group_obj[ANNAL.CURIE.group_entity_type]
                    if field_value_type and group_entity_type and field_value_type != group_entity_type:
                        log.warning(
                            "Group %s entity type %s differs from field %s value type %s"%
                            (group_id, group_entity_type, field_id, field_value_type)
                            )
                    entitydata[ANNAL.CURIE.field_fields] = group_obj[ANNAL.CURIE.group_fields]
            del entitydata[ANNAL.CURIE.group_ref]
        # Default render type to "Text"
        if ANNAL.CURIE.field_render_type not in entitydata:
            entitydata[ANNAL.CURIE.field_render_type] = "_enum_render_type/Text"
        # Migrate changed render type names
        entitydata = self._map_entity_field_enum_val(
            entitydata, ANNAL.CURIE.field_render_type, "_enum_render_type", 
            "RepeatGroup", "Group_Seq"
            )
        entitydata = self._map_entity_field_enum_val(
            entitydata, ANNAL.CURIE.field_render_type, "_enum_render_type", 
            "RepeatGroupRow", "Group_Seq_Row"
            )
        entitydata = self._map_entity_field_enum_val(
            entitydata, ANNAL.CURIE.field_render_type, "_enum_render_type", 
            "Slug", "EntityRef"
            )
        # Calculate mode from other fields if not defined
        val_render = entitydata[ANNAL.CURIE.field_render_type]
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
            elif val_render == "URIImport":
                val_mode = "Value_import"
            elif val_render == "FileUpload":
                val_mode = "Value_upload"
            entitydata[ANNAL.CURIE.field_value_mode] = val_mode
        # Consistency checks
        if val_mode == "Value_field":
            if ( not (ref_type and ref_field) ):
               log.warning(
                    "RecordField %s: val_mode 'Value_field' requires values for %s and %s"%
                        (field_id, ANNAL.CURIE.field_ref_type, ANNAL.CURIE.field_ref_field)
                    )
        elif val_mode == "Value_entity":
            if not ref_type:
               log.warning(
                    "RecordField %s: val_mode 'Value_entity' requires value for %s"%
                        (field_id, ANNAL.CURIE.field_ref_type)
                    )
            if ref_field:
               log.warning(
                    "RecordField %s: val_mode 'Value_entity' should not define value for %s"%
                        (field_id, ANNAL.CURIE.field_ref_field)
                    )
        # Return result
        return entitydata

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Post-update processing.

        This method is called when a RecordField entity has been created or updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the field belongs.
        """
        self._parent.cache_add_field(self)
        self._parent.generate_coll_jsonld_context(flags=post_update_flags)
        return entitydata

    def _post_remove_processing(self, post_update_flags):
        """
        Post-remove processing.

        This method is called when a RecordField entity has been removed.  
        """
        self._parent.cache_remove_field(self.get_id())
        return




# End.
