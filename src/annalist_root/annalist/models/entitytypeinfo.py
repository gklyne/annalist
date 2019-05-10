from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Gather information about an entity/record type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import traceback
import logging
log = logging.getLogger(__name__)

import copy

from annalist                       import message
from annalist                       import layout
from annalist.util                  import valid_id, extract_entity_id

from annalist.identifiers           import ANNAL, RDF, RDFS

from annalist.models.collection     import Collection
from annalist.models.annalistuser   import AnnalistUser, site_default_user_id, default_user_id, unknown_user_id
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordgroup    import RecordGroup, RecordGroup_migration
from annalist.models.recordfield    import RecordField
from annalist.models.recordvocab    import RecordVocab
from annalist.models.recordinfo     import RecordInfo
from annalist.models.recordenum     import RecordEnumFactory
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

COLL_ID     = layout.COLL_TYPEID
USER_ID     = layout.USER_TYPEID
TYPE_ID     = layout.TYPE_TYPEID
LIST_ID     = layout.LIST_TYPEID
VIEW_ID     = layout.VIEW_TYPEID
GROUP_ID    = layout.GROUP_TYPEID
FIELD_ID    = layout.FIELD_TYPEID
VOCAB_ID    = layout.VOCAB_TYPEID
INFO_ID     = layout.INFO_TYPEID
TASK_ID     = layout.TASK_TYPEID

COLL_MESSAGES = (
    { 'parent_heading':         "(@@ COLL_MESSAGES.parent_heading - unused message @@)"
    , 'parent_missing':         "(@@ COLL_MESSAGES.parent_missing - unused message @@)"
    , 'entity_heading':         message.COLLECTION_ID
    , 'entity_invalid_id':      message.COLLECTION_ID_INVALID
    , 'entity_exists':          message.COLLECTION_EXISTS
    , 'entity_not_exists':      message.COLLECTION_NOT_EXISTS
    , 'entity_removed':         message.COLLECTION_REMOVED
    , 'entity_type_heading':    "(@@ COLL_MESSAGES.entity_type_heading - unused message @@)"
    , 'entity_type_invalid':    "(@@ COLL_MESSAGES.entity_type_invalid - unused message @@)"
    })

ENTITY_MESSAGES = (
    { 'parent_heading':         message.RECORD_TYPE_ID
    , 'parent_missing':         message.RECORD_TYPE_NOT_EXISTS
    , 'entity_heading':         message.ENTITY_DATA_ID
    , 'entity_invalid_id':      message.ENTITY_DATA_ID_INVALID
    , 'entity_exists':          message.ENTITY_DATA_EXISTS
    , 'entity_not_exists':      message.ENTITY_DATA_NOT_EXISTS
    , 'entity_removed':         message.ENTITY_DATA_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

USER_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.ANNALIST_USER_ID
    , 'entity_invalid_id':      message.ANNALIST_USER_ID_INVALID
    , 'entity_exists':          message.ANNALIST_USER_EXISTS
    , 'entity_not_exists':      message.ANNALIST_USER_NOT_EXISTS
    , 'entity_removed':         message.ANNALIST_USER_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

TYPE_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_TYPE_ID
    , 'entity_invalid_id':      message.RECORD_TYPE_ID_INVALID
    , 'entity_exists':          message.RECORD_TYPE_EXISTS
    , 'entity_not_exists':      message.RECORD_TYPE_NOT_EXISTS
    , 'entity_removed':         message.RECORD_TYPE_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

LIST_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_LIST_ID
    , 'entity_invalid_id':      message.RECORD_LIST_ID_INVALID
    , 'entity_exists':          message.RECORD_LIST_EXISTS
    , 'entity_not_exists':      message.RECORD_LIST_NOT_EXISTS
    , 'entity_removed':         message.RECORD_LIST_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

VIEW_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_VIEW_ID
    , 'entity_invalid_id':      message.RECORD_VIEW_ID_INVALID
    , 'entity_exists':          message.RECORD_VIEW_EXISTS
    , 'entity_not_exists':      message.RECORD_VIEW_NOT_EXISTS
    , 'entity_removed':         message.RECORD_VIEW_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

GROUP_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_GROUP_ID
    , 'entity_invalid_id':      message.RECORD_GROUP_ID_INVALID
    , 'entity_exists':          message.RECORD_GROUP_EXISTS
    , 'entity_not_exists':      message.RECORD_GROUP_NOT_EXISTS
    , 'entity_removed':         message.RECORD_GROUP_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

FIELD_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_FIELD_ID
    , 'entity_invalid_id':      message.RECORD_FIELD_ID_INVALID
    , 'entity_exists':          message.RECORD_FIELD_EXISTS
    , 'entity_not_exists':      message.RECORD_FIELD_NOT_EXISTS
    , 'entity_removed':         message.RECORD_FIELD_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

VOCAB_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_VOCAB_ID
    , 'entity_invalid_id':      message.RECORD_VOCAB_ID_INVALID
    , 'entity_exists':          message.RECORD_VOCAB_EXISTS
    , 'entity_not_exists':      message.RECORD_VOCAB_NOT_EXISTS
    , 'entity_removed':         message.RECORD_VOCAB_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

INFO_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_INFO_ID
    , 'entity_invalid_id':      message.RECORD_INFO_ID_INVALID
    , 'entity_exists':          message.RECORD_INFO_EXISTS
    , 'entity_not_exists':      message.RECORD_INFO_NOT_EXISTS
    , 'entity_removed':         message.RECORD_INFO_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

ENUM_MESSAGES = (
    { 'parent_heading':         message.COLLECTION_ID
    , 'parent_missing':         message.COLLECTION_NOT_EXISTS
    , 'entity_heading':         message.RECORD_ENUM_ID
    , 'entity_invalid_id':      message.RECORD_ENUM_ID_INVALID
    , 'entity_exists':          message.RECORD_ENUM_EXISTS
    , 'entity_not_exists':      message.RECORD_ENUM_NOT_EXISTS
    , 'entity_removed':         message.RECORD_ENUM_REMOVED
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    })

SITE_PERMISSIONS = (
    { "view":   "VIEW"      # View site config data
    , "list":   "VIEW"      # ..
    , "search": "VIEW"      # ..
    , "new":    "FORBIDDEN" # Create collection record
    , "copy":   "FORBIDDEN" # ..
    , "edit":   "FORBIDDEN" # Update collection record
    , "delete": "FORBIDDEN" # Delete collection record
    , "config": "FORBIDDEN" # Change collection configuration
    , "admin":  "ADMIN"     # Change users or permissions
    })

ADMIN_PERMISSIONS = (
    { "view":   "ADMIN"     # View user record
    , "list":   "ADMIN"     # ..
    , "search": "ADMIN"     # ..
    , "new":    "ADMIN"     # Create user record
    , "copy":   "ADMIN"     # ..
    , "edit":   "ADMIN"     # Update user record
    , "delete": "ADMIN"     # Delete user record
    , "config": "CONFIG"    # Change collection configuration
    , "admin":  "ADMIN"     # Change users or permissions
    })

ADMIN_VIEW_PERMISSIONS = (
    { "view":   "VIEW"     # View site record
    , "list":   "VIEW"     # ..
    , "search": "VIEW"     # ..
    , "new":    "ADMIN"     # Create site record
    , "copy":   "ADMIN"     # ..
    , "edit":   "ADMIN"     # Update site record
    , "delete": "ADMIN"     # Delete site record
    , "config": "CONFIG"    # Change collection configuration
    , "admin":  "ADMIN"     # Change users or permissions
    })

CONFIG_PERMISSIONS = (
    { "view":   "VIEW"      # View config record
    , "list":   "VIEW"      # ..
    , "search": "VIEW"      # ..
    , "new":    "CONFIG"    # Create config record
    , "copy":   "CONFIG"    # ..
    , "edit":   "CONFIG"    # Update config record
    , "delete": "CONFIG"    # Delete config record
    , "config": "CONFIG"    # Change collection configuration
    , "admin":  "ADMIN"     # Change users or permissions
    })

ENTITY_PERMISSIONS = (
    { "view":   "VIEW"      # View data record
    , "list":   "VIEW"      # ..
    , "search": "VIEW"      # ..
    , "new":    "CREATE"    # Create data record
    , "copy":   "CREATE"    # ..
    , "edit":   "UPDATE"    # Update data record
    , "delete": "DELETE"    # Delete data record
    , "config": "CONFIG"    # Change collection configuration
    , "admin":  "ADMIN"     # Change users or permissions
    })

TYPE_CLASS_MAP = (
    { COLL_ID:                  Collection
    , USER_ID:                  AnnalistUser
    , TYPE_ID:                  RecordType
    , LIST_ID:                  RecordList
    , VIEW_ID:                  RecordView
    , GROUP_ID:                 RecordGroup_migration
    , FIELD_ID:                 RecordField
    , VOCAB_ID:                 RecordVocab
    , INFO_ID:                  RecordInfo
    , '_enum_field_placement':  RecordEnumFactory('_enum_field_placement',  '_enum_field_placement')
    , '_enum_list_type':        RecordEnumFactory('_enum_list_type',        '_enum_list_type')
    , '_enum_render_type':      RecordEnumFactory('_enum_render_type',      '_enum_render_type')
    , '_enum_value_mode':       RecordEnumFactory('_enum_value_mode',       '_enum_value_mode')
    , '_enum_value_type':       RecordEnumFactory('_enum_value_type',       '_enum_value_type')
    })

TYPE_MESSAGE_MAP = (
    { COLL_ID:                  COLL_MESSAGES
    , USER_ID:                  USER_MESSAGES
    , TYPE_ID:                  TYPE_MESSAGES
    , LIST_ID:                  LIST_MESSAGES
    , VIEW_ID:                  VIEW_MESSAGES
    , GROUP_ID:                 GROUP_MESSAGES
    , FIELD_ID:                 FIELD_MESSAGES
    , VOCAB_ID:                 VOCAB_MESSAGES
    , INFO_ID:                  INFO_MESSAGES
    , '_enum_field_placement':  ENUM_MESSAGES  
    , '_enum_list_type':        ENUM_MESSAGES
    , '_enum_render_type':      ENUM_MESSAGES
    , '_enum_value_mode':       ENUM_MESSAGES
    , '_enum_value_type':       ENUM_MESSAGES
    })

SITE_PERMISSIONS_MAP = (
    { COLL_ID:                  SITE_PERMISSIONS
    , USER_ID:                  ADMIN_PERMISSIONS
    , TYPE_ID:                  SITE_PERMISSIONS
    , LIST_ID:                  SITE_PERMISSIONS
    , VIEW_ID:                  SITE_PERMISSIONS
    , GROUP_ID:                 SITE_PERMISSIONS
    , FIELD_ID:                 SITE_PERMISSIONS
    , VOCAB_ID:                 SITE_PERMISSIONS
    , INFO_ID:                  ADMIN_VIEW_PERMISSIONS
    , '_enum_field_placement':  SITE_PERMISSIONS  
    , '_enum_list_type':        SITE_PERMISSIONS
    , '_enum_render_type':      SITE_PERMISSIONS
    , '_enum_value_mode':       SITE_PERMISSIONS
    , '_enum_value_type':       SITE_PERMISSIONS
    , 'EntityData':             SITE_PERMISSIONS
    })

TYPE_PERMISSIONS_MAP = (
    { COLL_ID:                  CONFIG_PERMISSIONS
    , USER_ID:                  ADMIN_PERMISSIONS
    , TYPE_ID:                  CONFIG_PERMISSIONS
    , LIST_ID:                  CONFIG_PERMISSIONS
    , VIEW_ID:                  CONFIG_PERMISSIONS
    , GROUP_ID:                 CONFIG_PERMISSIONS
    , FIELD_ID:                 CONFIG_PERMISSIONS
    , VOCAB_ID:                 CONFIG_PERMISSIONS
    , INFO_ID:                  CONFIG_PERMISSIONS
    , '_enum_field_placement':  SITE_PERMISSIONS  
    , '_enum_list_type':        SITE_PERMISSIONS
    , '_enum_render_type':      SITE_PERMISSIONS
    , '_enum_value_mode':       SITE_PERMISSIONS
    , '_enum_value_type':       SITE_PERMISSIONS
    , 'EntityData':             ENTITY_PERMISSIONS
    })

def get_built_in_type_ids():
    """
    Returns an interator over the built-in types
    """
    return iter(TYPE_CLASS_MAP)

class EntityTypeInfo(object):
    """
    Check a supplied type identifier, and access values for:
        Entity class
        Entity parent
        Entity alternative parent for site-wide values
        Type-dependent messages
    """

    def __init__(self, coll, type_id, create_typedata=False):
        """
        Set up type attribute values.

        coll            collection object in which type is used
        type_id         entity type id, which is a collection-defined value,
                        or one of a number of special site-wide built-in types.
        create_typedata if true, requests that a RecordTypeData entity be created
                        and saved on disk for user-defined types if it does not 
                        already exist.  (Creating a RecordTypeData entity ensures
                        that the corresponding data storage location is available 
                        for saving entity data.)

        Attributes of type information object are:

        recordtype      type object describing the identified type
        entityparent    Parent entity for entities of this type, or None if 
                        the type is not defined for the collection
        entityaltparent Alternative (site-wide) parent entity for built-in types, 
                        or None
        entityclass     Python class object for entity
        entitymessages  a table of message strings for diagnostics relating to 
                        operations on this type.

        and other values as initialized here.
        """
        self.entitycoll      = coll
        self.recordtype      = None
        self.entityparent    = None
        self.coll_id         = coll.get_id()
        self.type_id         = type_id
        self.permissions_map = None
        if type_id == layout.COLL_TYPEID: # "_coll"
            # NOTE: 
            #
            # This setup defaults to using site permissions for collection operations.
            # But there is some special-case code in views.displayinfo that uses the 
            # collection itself if it exists.
            #
            # (See use of attribute DisplayInfo.coll_perms.)
            #
            self.recordtype      = coll.get_site().site_data_collection().get_type(type_id)
            self.entityparent    = coll.get_site()
            self.entityaltparent = None
            self.entityclass     = Collection
            self.entitymessages  = COLL_MESSAGES
            self.permissions_map = CONFIG_PERMISSIONS # unless entity is layout.SITEDATA_ID?
        elif type_id in TYPE_CLASS_MAP:
            self.recordtype      = coll.get_type(type_id)
            self.entityparent    = coll
            self.entityaltparent = coll.get_site()
            self.entityclass     = TYPE_CLASS_MAP[type_id]
            self.entitymessages  = TYPE_MESSAGE_MAP[type_id]
            if self.coll_id == layout.SITEDATA_ID:
                self.permissions_map = SITE_PERMISSIONS_MAP[type_id]
            else:
                self.permissions_map = TYPE_PERMISSIONS_MAP[type_id]
        else:
            if not valid_id(type_id):
                raise ValueError("EntityTypeInfo invalid type_id (%s)"%(type_id,))
            if RecordType.exists(coll, type_id, altscope="all"):
                # log.info("@@ EntityTypeInfo: Type %s exists"%type_id)
                self.recordtype     = coll.get_type(type_id)
            else:
                # log.info("@@ EntityTypeInfo: Type %s does not exist for collection %s"%(type_id,coll.get_id()))
                pass
            if create_typedata and not RecordTypeData.exists(coll, type_id):
                self.entityparent   = RecordTypeData.create(coll, type_id, {})
            else:
                self.entityparent   = RecordTypeData(coll, type_id)
            self.entityaltparent = None
            self.entityclass     = EntityData
            self.entitymessages  = ENTITY_MESSAGES
            self.permissions_map = ENTITY_PERMISSIONS
        if not self.recordtype:
            # .recordtype is used by views.displayinfo to locate the default
            # view and/or list id for examining records of a particular type.
            # Also used in entityedit for getting @type URI/CURIE values.
            # Used in bound_field to get link to type record
            log.warning("EntityTypeInfo.__init__: RecordType %s not found"%type_id)
            # log.info("".join(traceback.format_stack()))
            # raise ValueError("Trace")
        return

    def get_type_id(self):
        """
        Return id for current type
        """
        if self.recordtype:
            return self.recordtype[ANNAL.CURIE.id]
        return None

    def get_type_uri(self):
        """
        Return identiftying URI for the current type
        """
        typeuri = None
        if self.recordtype:
            if ANNAL.CURIE.uri in self.recordtype:
                typeuri = self.recordtype[ANNAL.CURIE.uri]
            if not typeuri:
                typeuri = self.recordtype[ANNAL.CURIE.url]
        return typeuri

    def get_all_type_uris(self):
        """
        Return list of all type URIs for this type
        """
        type_uris = None
        type_uri  = self.get_type_uri()
        if type_uri:
            type_uris = [type_uri] + list(self.entitycoll.cache_get_supertype_uris(type_uri))
        return type_uris

    def set_type_uris(self, entity_values):
        """
        Set URIs of current type in supplied entity values

        Previous type URIs are overridden.
        """
        entity_values[ANNAL.CURIE.type] = self.get_type_uri()
        entity_values['@type']          = self.get_all_type_uris()
        return

    def make_entity_uri(self, entity_id):
        """
        Return a candidate entity URI for an instance of the current type,
        based on a namespace prefix declared in the type definition.

        Returns None if no entity namespace prefix is declared for the type.
        """
        if ANNAL.CURIE.ns_prefix in self.recordtype:
            ns_pref = self.recordtype[ANNAL.CURIE.ns_prefix]
            if ns_pref != "":
                if not valid_id(ns_pref):
                    raise ValueError(
                        "EntityTypeInfo invalid ns_prefix %s for type %s"%
                          (ns_pref, self.type_id)
                        )
                return ns_pref + ":" + entity_id
        return None

    def set_entity_uri(self, entity_id, entity_values):
        """
        Update entity URI in supplied entity values, if value is not already set.

        If current value is blank or same as URL then that value is discarded.
        """
        if ANNAL.CURIE.uri in entity_values:
            if entity_values[ANNAL.CURIE.uri] in {"", entity_values.get(ANNAL.CURIE.url, "")}:
                entity_values.pop(ANNAL.CURIE.uri)
        if ANNAL.CURIE.uri not in entity_values:
            entity_uri = self.make_entity_uri(entity_id)
            if entity_uri:
                entity_values[ANNAL.CURIE.uri] = entity_uri
        return

    def get_default_view_id(self):
        """
        Returns the default view id for the current record type
        """
        view_id = None
        if self.recordtype:
            view_id = extract_entity_id(self.recordtype.get(ANNAL.CURIE.type_view, None))
        else:
            log.warning("EntityTypeInfo.get_default_view_id: no type data for %s"%(self.type_id))
        return view_id or "Default_view"

    # Entity-specific methods

    def get_entity_permissions_map(self, entity_id=None):
        """
        Returns an entity-specific permission map that takes account of special 
        access permissions applied to specific individual entities.

        Thge permission maop is a map from an action name ("view", "new", etc) to 
        a permission token that must be granted to a requester for the action 
        to be allowed.

        If `entity_id` is not specified, or is None, returns a default permission map 
        applicable to entities of the current type in the absence of more specific 
        permission requirements.
        """
        entity_perms_map = self.permissions_map
        # Check for entity-specific permissions
        #
        # The logic here is currently ad-hoc, but in due course could be replaced
        # by something more generic
        # log.info(
        #     "@@ get_entity_permissions_map: type_id %s, entity_id %s"%(self.type_id, entity_id)
        #     )
        if self.type_id == USER_ID:
            # Relax view access requirements for default and unknown user id
            # (Real users require admin rights to view)
            if entity_id in [site_default_user_id, default_user_id, unknown_user_id]:
                entity_perms_map = dict(entity_perms_map)
                entity_perms_map["view"] = CONFIG_PERMISSIONS["view"]
        return entity_perms_map

    def _new_entity(self, entity_id):
        """
        Returns a new, entity object of the current type with the given id
        """
        return self.entityclass(self.entityparent, entity_id)

    def parent_exists(self):
        """
        Test for existence of parent entity for the current type.
        """
        return self.entityparent._exists()

    def entity_exists(self, entity_id, altscope=None):
        """
        Test for existence of identified entity of the current type.
        """
        return self.entityclass.exists(self.entityparent, entity_id, altscope=altscope)

    def create_entity(self, entity_id, entity_values):
        """
        Creates and returns an entity for the current type, with the supplied values.
        """
        log.debug("create_entity: id %s, parent id %s"%(entity_id, self.entityparent.get_id()))
        # log.debug("create_entity: values %r"%(entity_values,))
        # Set type URI for entity; previous types are not carried forwards
        self.set_type_uris(entity_values)
        self.set_entity_uri(entity_id, entity_values)
        return self.entityclass.create(self.entityparent, entity_id, entity_values)

    def remove_entity(self, entity_id):
        """
        Remove identified entity for the current type.
        """
        log.debug(
            "remove_entity id %s, parent %s"%
            (entity_id, self.entityparent)
            )
        if self.type_id == COLL_ID:
            raise ValueError("EntitytypeInfo.remove_entity: Attempt to remove collection")
        return self.entityclass.remove(self.entityparent, entity_id)

    def get_entity(self, entity_id, action="view"):
        """
        Loads and returns an entity for the current type, or 
        returns None if the entity does not exist.

        If `action` is "new" then a new entity is initialized (but not saved).
        """
        # log.debug(
        #     "EntityTypeInfo.get_entity id %s, parent %s, altparent %s, action %s"%
        #     (entity_id, self.entityparent, self.entityaltparent, action)
        #     )
        entity = None
        entity_id = extract_entity_id(entity_id)
        if valid_id(entity_id, reserved_ok=True):
            if action == "new":
                entity = self._new_entity(entity_id)
                entity_initial_values = self.get_initial_entity_values(entity_id)
                entity.set_values(entity_initial_values)
            elif self.entityclass.exists(self.entityparent, entity_id, altscope="all"):
                entity = self.entityclass.load(self.entityparent, entity_id, altscope="all")
            else:
                log.debug(
                    "EntityTypeInfo.get_entity %s/%s at %s not found"%
                    (self.type_id, entity_id, self.entityparent._entitydir)
                    )
        return entity

    def get_create_entity(self, entity_id):
        """
        Read or create an entity with the indicated entity_id.

        If the identified entity does not already exist, a new entity is created 
        and returned, but not (yet) saved.
        """
        entity = self.get_entity(entity_id)
        if entity is None:
            entity = self.get_entity(entity_id, action="new")
        return entity

    def get_copy_entity(self, entity_id, copy_entity_id):
        """
        Read or create an entity with the indicated entity_id.

        If the identified entity does not already exist, a new entity is created 
        but not (yet) saved.

        The newly created entity is a copy of 'copy_entity_id'.        
        """
        entity_id = extract_entity_id(entity_id)
        entity    = self.get_entity(entity_id)
        if entity is None:
            entity = self._new_entity(entity_id)
            entity.set_values(
                self.get_initial_entity_values(entity_id, copy_entity_id=copy_entity_id)
                )
        return entity

    def get_entity_implied_values(self, entity):
        """
        Adds implied values to the supplied entity value (e.g. aliases),
        and returns a new value with the additional values

        Implied values are determined by the type of the entity, and if type
        information is not present this function generates a failure.
        """
        if not self.recordtype: 
            raise AssertionError(
                "EntityTypeInfo.get_entity_implied_values called with no type information available.  "+
                "entity_id %s/%s, type_id %s"%(entity.get_type_id(), entity.get_id(), self.type_id)
                )
        implied_entity = entity
        if implied_entity and ANNAL.CURIE.field_aliases in self.recordtype:
            implied_entity = copy.deepcopy(entity)
            for alias in self.recordtype[ANNAL.CURIE.field_aliases]:
                tgt = alias[ANNAL.CURIE.alias_target]
                src = alias[ANNAL.CURIE.alias_source]
                if implied_entity.get(tgt, None) in [None, ""]:
                    implied_entity[tgt] = implied_entity.get(src, "")
        return implied_entity

    def rename_entity(self, new_entity_id, old_typeinfo, old_entity_id):
        """
        Copy associated data files from specified entity to new.
        The calling program is expected to update data associated with the new entity.

        Subdirectories are copied as entire subtrees.
        """
        if old_typeinfo.entity_exists(old_entity_id):
            new_entity = self._new_entity(new_entity_id)
            old_entity = old_typeinfo._new_entity(old_entity_id)
            p_new      = new_entity._rename_files(old_entity)
            if not p_new:
                log.warning(
                    "EntityTypeInfo.rename_entity: error renaming entity %s from %s to %s"%
                    (old_entity.get_url(), old_entity_id, new_entity_id)
                    )
        else:
            log.warning(
                "EntityTypeInfo.rename_entity: source entity not found %s/%s"%
                (old_typeinfo.type_id, old_entity_id)
                )
        return

    def enum_entity_ids(self, altscope=None):
        """
        Iterate over entity identifiers in collection with current type.
        """
        if self.entityparent:
            for eid in self.entityparent.child_entity_ids(
                    self.entityclass, 
                    altscope=altscope):
                yield eid
        else:
            log.warning("EntityTypeInfo.enum_entity_ids: missing entityparent; type_id %s"%(self.type_id))
        return

    def enum_entities(self, user_perms=None, altscope=None):
        """
        Iterate over entities in collection with current type.
        """
        if (not user_perms or 
            self.permissions_map['list'] in user_perms[ANNAL.CURIE.user_permission]):
            if not self.entityparent:
                log.warning("EntityTypeInfo.enum_entities: missing entityparent; type_id %s"%(self.type_id))
            else:
                for eid in self.entityparent.child_entity_ids(
                        self.entityclass, 
                        altscope=altscope):
                    yield self.get_entity(eid)
        return

    def enum_entities_with_implied_values(self, user_perms=None, altscope=None):
        """
        Iterate over entities in collection with current type.
        Returns entities with alias and inferred fields instantiated.

        If user_perms is supplied and not None, checks that they contain permission to
        list values of the appropriate type. 
        """
        #@@
        # log.info(
        #     "@@ EntityTypeInfo.enum_entities_with_implied_values: parent %s, altscope %s"%
        #     (self.entityparent.get_id(), altscope)
        #     )
        #@@
        if (not user_perms or 
            self.permissions_map['list'] in user_perms[ANNAL.CURIE.user_permission]):
            if not self.entityparent:
                log.warning(
                    "EntityTypeInfo.enum_entities_with_implied_values: missing entityparent; type_id %s"%
                    (self.type_id)
                    )
            elif not self.recordtype:
                log.warning(
                    "EntityTypeInfo.enum_entities_with_implied_values: missing recordtype; type_id %s"%
                    (self.type_id)
                    )
                # No record type info: return base entity without implied values
                for eid in self.entityparent.child_entity_ids(
                        self.entityclass, 
                        altscope=altscope):
                    yield self.get_entity(eid)
            else:
                #@@
                # log.info(
                #     "@@ enum_entities_with_implied_values: parent %s, altscope %s"%
                #     (self.entityparent.get_id(), altscope)
                #     )
                #@@
                for eid in self.entityparent.child_entity_ids(
                        self.entityclass, 
                        altscope=altscope):
                    yield self.get_entity_implied_values(self.get_entity(eid))
        return

    def get_initial_entity_values(self, entity_id, copy_entity_id=layout.INITIAL_VALUES_ID):
        """
        Returns an initial value dictionary for the indicated entity.

        Attempts to read initial values from the type parent directory.
        Failing that, returns system-wide default values.
        """
        values = (
            { '@type':              [ANNAL.CURIE.EntityData]
            , ANNAL.CURIE.type_id:  self.type_id
            , RDFS.CURIE.label:     ""
            , RDFS.CURIE.comment:   ""
            })
        init_entity = self.get_entity(copy_entity_id)
        if init_entity:
            values = init_entity.get_values()
            values.pop("@id",              None)
            values.pop(ANNAL.CURIE.id,     None)
            values.pop(ANNAL.CURIE.url,    None)
        values[ANNAL.CURIE.id]      = entity_id
        values[RDFS.CURIE.label]    = ""
        values[RDFS.CURIE.comment]  = ""
        return values

    def get_fileobj(self, entity_id, name, typeuri, mimetype, mode):
        """
        Returns a file object to access a file stored with the named entity 
        with the designated type URI (typically obtained from a field description).  
        The `mode` string value is interpreted like the `mode` parameter to the 
        Python `open` function, to the extent applicable.
        """
        fileobj = None
        if self.entityparent:
            fileobj = self.entityclass.fileobj(
                self.entityparent, entity_id, name, typeuri, mimetype, mode
                )
        else:
            log.warning("EntityTypeInfo.get_fileobj: missing entityparent; type_id %s"%(self.type_id))
        return fileobj

    def get_ancestor_id(self, entity):
        """
        Returns the ancestor collection id for the supplied entity
        (which is assumed to be of the current type).
        """
        if self.type_id == COLL_ID:
            return layout.SITEDATA_ID
        return entity._parent._ancestorid

# End.
