"""
Gather information about an entity/record type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy

from annalist                       import message
from annalist.util                  import valid_id, extract_entity_id

from annalist.identifiers           import ANNAL, RDF, RDFS

from annalist.models.annalistuser   import AnnalistUser
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordfield    import RecordField
from annalist.models.recordenum     import RecordEnumFactory
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

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
    { '_user':              AnnalistUser
    , '_type':              RecordType
    , '_list':              RecordList
    , '_view':              RecordView
    , '_group':             RecordGroup
    , '_field':             RecordField
    , 'Enum_list_type':     RecordEnumFactory('Enum_list_type',   'Enum_list_type')
    , 'Enum_render_type':   RecordEnumFactory('Enum_render_type', 'Enum_render_type')
    , 'Enum_value_mode':    RecordEnumFactory('Enum_value_mode',  'Enum_value_mode')
    , 'Enum_bib_type':      RecordEnumFactory('Enum_bib_type',    'Enum_bib_type')
    })

TYPE_MESSAGE_MAP = (
    { '_user':              USER_MESSAGES
    , '_type':              TYPE_MESSAGES
    , '_list':              LIST_MESSAGES
    , '_view':              VIEW_MESSAGES
    , '_group':             GROUP_MESSAGES
    , '_field':             FIELD_MESSAGES
    , 'Enum_list_type':     ENUM_MESSAGES
    , 'Enum_render_type':   ENUM_MESSAGES
    , 'Enum_value_mode':    ENUM_MESSAGES
    , 'Enum_bib_type':      ENUM_MESSAGES
    })

TYPE_PERMISSIONS_MAP = (
    { '_user':              ADMIN_PERMISSIONS
    , '_type':              CONFIG_PERMISSIONS
    , '_list':              CONFIG_PERMISSIONS
    , '_view':              CONFIG_PERMISSIONS
    , '_group':             CONFIG_PERMISSIONS
    , '_field':             CONFIG_PERMISSIONS
    , 'Enum_list_type':     CONFIG_PERMISSIONS
    , 'Enum_render_type':   CONFIG_PERMISSIONS
    , 'Enum_value_mode':    CONFIG_PERMISSIONS
    , 'Enum_bib_type':      CONFIG_PERMISSIONS
    })

def get_built_in_type_ids():
    """
    Returns an interator over the built-in types
    """
    return TYPE_CLASS_MAP.iterkeys()

class EntityTypeInfo(object):
    """
    Check a supplied type identifier, and access values for:
        Entity class
        Entity parent
        Entity alternative parent for site-wide values
        Type-dependent messages
    """

    def __init__(self, site, coll, type_id, create_typedata=False):
        """
        Set up type attribute values.

        site            current site object
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
        entityparent    Parent enbtity for entities of this type, or None if 
                        the type is not defined for the collection
        entityaltparent Alternative (site-wide) parent entity for built-in types, 
                        or None
        entityclass     Python class object for entity
        entitymessages  a table of message strings for diagnostics relating to 
                        operations on this type.

        and other values as initialized here.
        """
        #@@TODO: remove site param and access through coll
        self.entitysite      = site
        self.entitycoll      = coll
        self.recordtype      = None
        self.entityparent    = None
        self.coll_id         = coll.get_id()
        self.type_id         = type_id
        self.permissions_map = None
        if type_id in TYPE_CLASS_MAP:
            self.recordtype      = coll.get_type(type_id)
            self.entityparent    = coll
            self.entityaltparent = site
            self.entityclass     = TYPE_CLASS_MAP[type_id]
            self.entitymessages  = TYPE_MESSAGE_MAP[type_id]
            self.permissions_map = TYPE_PERMISSIONS_MAP[type_id]
        else:
            if RecordType.exists(coll, type_id, site):
                self.recordtype     = coll.get_type(type_id)
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
            #
            # Also used in entityedit for getting @type URI/CURIE values.
            #
            # Used in render_utils to get link to type record
            log.warning("EntityTypeInfo.__init__: RecordType %s not found"%type_id)
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
        types = [self.get_type_uri()]
        if self.recordtype:
            supertypes = self.recordtype.get(ANNAL.CURIE.supertype_uris, None)
            if supertypes:
                for st in supertypes:
                    # supertype_uris is list of objects { 'annal:supertype_uri': uri }
                    t = st.get(ANNAL.CURIE.supertype_uri, None)
                    if t:
                        types.append(t)
        return types

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

    def entity_exists(self, entity_id, use_altparent=False):
        """
        Test for existence of identified entity of the current type.
        """
        altparent = self.entityaltparent if use_altparent else None
        return self.entityclass.exists(self.entityparent, entity_id, altparent=altparent)

    def create_entity(self, entity_id, entity_values):
        """
        Creates and returns an entity for the current type, with the supplied values.
        """
        log.debug(
            "create_entity id %s, parent %s, values %r"%
            (entity_id, self.entityparent, entity_values)
            )
        # Set type URI for entity; previous types are not carried forwards
        # Don't save entity URI if same as URL
        if entity_values.get(ANNAL.CURIE.uri) == entity_values.get(ANNAL.CURIE.url):
            entity_values.pop(ANNAL.CURIE.uri, None)
        entity_values['@type'] = self.get_all_type_uris() # NOTE: previous types not carried forward
        return self.entityclass.create(self.entityparent, entity_id, entity_values)

    def remove_entity(self, entity_id):
        """
        Remove identified entity for the current type.
        """
        log.debug(
            "remove_entity id %s, parent %s"%
            (entity_id, self.entityparent)
            )
        return self.entityclass.remove(self.entityparent, entity_id)

    def get_entity(self, entity_id, action="view"):
        """
        Loads and returns an entity for the current type, or 
        returns None if the entity does not exist.

        If `action` is "new" then a new entity is initialized (but not saved).
        """
        log.debug(
            "get_entity id %s, parent %s, altparent %s, action %s"%
            (entity_id, self.entityparent, self.entityaltparent, action)
            )
        entity = None
        entity_id = extract_entity_id(entity_id)
        if valid_id(entity_id):
            if action == "new":
                entity = self._new_entity(entity_id)
                entity_initial_values = self.get_initial_entity_values(entity_id)
                entity.set_values(entity_initial_values)
            elif self.entityclass.exists(
                    self.entityparent, entity_id, altparent=self.entityaltparent
                    ):
                entity = self.entityclass.load(
                    self.entityparent, entity_id, altparent=self.entityaltparent
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

    # @@TODO: rename inferred -> implied
    def get_entity_inferred_values(self, entity):
        """
        Adds inferrable values to the supplied entity value (e.g. aliases),
        and returns a new value with the additional values

        Inferred values are determined by the type of the entity, and if type
        information is not present this fundtion generates a failure.
        """
        if not self.recordtype: 
            raise AssertionError(
                "add_inferred_values_to_entity called with no type information available.  "+
                "entity_id %s/%s, type_id %s"%(entity.get_type_id(), entity.get_id(), self.type_id)
                )
        inferred_entity = entity
        if inferred_entity and ANNAL.CURIE.field_aliases in self.recordtype:
            inferred_entity = copy.deepcopy(entity)
            for alias in self.recordtype[ANNAL.CURIE.field_aliases]:
                tgt = alias[ANNAL.CURIE.alias_target]
                src = alias[ANNAL.CURIE.alias_source]
                if inferred_entity.get(tgt, None) in [None, ""]:
                    inferred_entity[tgt] = inferred_entity.get(src, "")
        return inferred_entity

    def copy_data_files(self, new_entity_id, old_typeinfo, old_entity_id):
        """
        Copy associated data files from specified entity to new.
        """
        if self.entity_exists(new_entity_id):
            if old_typeinfo.entity_exists(old_entity_id):
                new_entity = self._new_entity(new_entity_id)
                old_entity = old_typeinfo._new_entity(old_entity_id)
                for p, f in old_entity._entity_files():
                    if not new_entity._exists_file(f):
                        p_new = new_entity._copy_file(p, f)
                        if not p_new:
                            log.warning(
                                "EntityTypeInfo.copy_data_files: error copying file %s from %s to %s"%
                                (f, old_entity_id, new_entity_id)
                                )
            else:
                log.warning(
                    "EntityTypeInfo.copy_data_files: source entity not found %s/%s"%
                    (old_typeinfo.type_id, old_entity_id)
                    )
        else:
            log.warning(
                "EntityTypeInfo.copy_data_files: target entity not found %s/%s"
                %(self.type_id, entity_id)
                )
        return

    def enum_entity_ids(self, usealtparent=False):
        """
        Iterate over entity identifiers in collection with current type.

        usealtparent    is True if site-wide entities are to be included.
        """
        altparent = self.entityaltparent if usealtparent else None
        if self.entityparent:
            for eid in self.entityparent.child_entity_ids(
                    self.entityclass, 
                    altparent=altparent):
                yield eid
        else:
            log.warning("EntityTypeInfo.enum_entity_ids: missing entityparent; type_id %s"%(self.type_id))
        return

    def enum_entities(self, user_perms=None, usealtparent=False):
        """
        Iterate over entities in collection with current type.

        usealtparent    is True if site-wide entities are to be included.
        """
        if (not user_perms or 
            self.permissions_map['list'] in user_perms[ANNAL.CURIE.user_permissions]):
            altparent = self.entityaltparent if usealtparent else None
            if self.entityparent:
                for eid in self.entityparent.child_entity_ids(
                        self.entityclass, 
                        altparent=altparent):
                    yield self.get_entity(eid)
            else:
                log.warning("EntityTypeInfo.enum_entities: missing entityparent; type_id %s"%(self.type_id))
        return

    def enum_entities_with_inferred_values(self, user_perms=None, usealtparent=False):
        """
        Iterate over entities in collection with current type.
        Returns entities with alias and inferred fields instantiated.

        usealtparent    is True if site-wide entities are to be included.
        """
        if (not user_perms or 
            self.permissions_map['list'] in user_perms[ANNAL.CURIE.user_permissions]):
            altparent = self.entityaltparent if usealtparent else None
            if self.entityparent:
                for eid in self.entityparent.child_entity_ids(
                        self.entityclass, 
                        altparent=altparent):
                    yield self.get_entity_inferred_values(self.get_entity(eid))
            else:
                log.warning("EntityTypeInfo.enum_entities: missing entityparent; type_id %s"%(self.type_id))
        return

    def get_initial_entity_values(self, entity_id):
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
        init_entity = self.get_entity("_initial_values")
        if init_entity:
            values = init_entity.get_values()
            values.pop("@id", None)
            values.pop(ANNAL.CURIE.id,  None)
            values.pop(ANNAL.CURIE.url, None)
        values[ANNAL.CURIE.id] = entity_id
        return values

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

# End.
