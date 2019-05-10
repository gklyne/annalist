"""
Annalist field group group
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
import traceback

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData
from annalist.util              import extract_entity_id


class RecordGroup(EntityData):

    _entitytype     = ANNAL.CURIE.Field_group
    _entitytypeid   = layout.GROUP_TYPEID
    _entityroot     = layout.COLL_GROUP_PATH
    _entityview     = layout.COLL_GROUP_VIEW
    _entityfile     = layout.GROUP_META_FILE

    _deprecation_warning = True

    def __init__(self, parent, group_id):
        """
        Initialize a new RecordGroup object, without metadata (yet).

        parent      is the parent collection in which the group is defined.
        group_id    the local identifier for the field group
        """
        if self._deprecation_warning:
            log.warn("Instantiating _group/%s for collection %s"%(group_id, parent.get_id()))
            # log.debug("".join(traceback.format_stack()))
        super(RecordGroup, self).__init__(parent, group_id)
        self._parent = parent
        # log.debug("RecordGroup %s: dir %s"%(group_id, self._entitydir))
        return

    @classmethod
    def load(cls, parent, entityid, altscope=None, deprecation_warning=False):
        """
        Overloaded load method with default deprecation warning
        """
        if cls._deprecation_warning:
            log.warn("Loading _group/%s for collection %s"%(entityid, parent.get_id()))
            # log.debug("".join(traceback.format_stack()))
        return super(RecordGroup, cls).load(parent, entityid, altscope=altscope)

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _migrate_values(self, entitydata):
        """
        Group description entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exactly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        migration_map = (
            [ (ANNAL.CURIE.record_type, ANNAL.CURIE.group_entity_type)
            ])
        entitydata = self._migrate_values_map_field_names(migration_map, entitydata)
        for f in entitydata.get(ANNAL.CURIE.group_fields, []):
            field_id = extract_entity_id(f[ANNAL.CURIE.field_id])
            if field_id == "Field_render":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_render_type"
            if field_id == "Field_type":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/Field_value_type"
            if field_id == "View_target_type":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/View_entity_type"
            if field_id == "List_target_type":
                f[ANNAL.CURIE.field_id] = layout.FIELD_TYPEID+"/List_entity_type"
        # Return result
        return entitydata

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Post-update processing.

        This method is called when a RecordGroup entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the group belongs.
        """
        self._parent.generate_coll_jsonld_context(flags=post_update_flags)
        return entitydata

class RecordGroup_migration(RecordGroup):
    """
    Variation of RecordGroup with suppressed instantiation warning,
    used for migrating old data.
    """
    _deprecation_warning = False

    def __init__(self, parent, group_id):
        super(RecordGroup_migration, self).__init__(parent, group_id)
        return

# End.
