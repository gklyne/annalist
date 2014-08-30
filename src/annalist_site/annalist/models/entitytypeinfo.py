"""
Gather information about an entity/record type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import message

from annalist.identifiers           import ANNAL, RDF, RDFS

from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
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
    , 'entity_type_heading':    message.ENTITY_TYPE_ID
    , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
    , 'entity_removed':         message.ENTITY_DATA_REMOVED
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

TYPE_CLASS_MAP = (
    { '_type':              RecordType
    , '_list':              RecordList
    , '_view':              RecordView
    , '_field':             RecordField
    , 'Enum_list_type':     RecordEnumFactory('Enum_list_type',  'Enum_list_type')
    , 'Enum_field_type':    RecordEnumFactory('Enum_field_type', 'Enum_field_type')
    })

TYPE_MESSAGE_MAP = (
    { '_type':              TYPE_MESSAGES
    , '_list':              LIST_MESSAGES
    , '_view':              VIEW_MESSAGES
    , '_field':             FIELD_MESSAGES
    , 'Enum_list_type':     ENUM_MESSAGES
    , 'Enum_field_type':    ENUM_MESSAGES
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
        self.entitysite     = site
        self.entitycoll     = coll
        self.recordtype     = None
        self.entityparent   = None
        self.coll_id        = coll.get_id()
        self.type_id        = type_id
        if type_id in TYPE_CLASS_MAP:
            self.recordtype      = RecordType.load(coll, type_id, site)
            self.entityparent    = coll
            self.entityaltparent = site
            self.entityclass     = TYPE_CLASS_MAP[type_id]
            self.entitymessages  = TYPE_MESSAGE_MAP[type_id]
        else:
            if RecordType.exists(coll, type_id, site):
                self.recordtype     = RecordType.load(coll, type_id, site)
                if create_typedata and not RecordTypeData.exists(coll, type_id):
                    self.entityparent   = RecordTypeData.create(coll, type_id, {})
                else:
                    self.entityparent   = RecordTypeData(coll, type_id)
            self.entityaltparent = None
            self.entityclass     = EntityData
            self.entitymessages  = ENTITY_MESSAGES
        if not self.recordtype:
            #@@
            # .recordtype is used by views.displayinfo to locate the default
            # view and/or list id for examining records of a particular type.
            #
            # Also used in entityedit for getting @type URI/CURIE values.
            #
            # Used in render_utils to get link to type record
            #@@
            log.warning("EntityTypeInfo: RecordType %s not found"%type_id)
        return

    def get_entity(self, entity_id):
        """
        Loads and returns an entity for the current type, or 
        returns None if the entity does not exist.
        """
        log.debug(
            "get_entity id %s, parent %s, altparent %s"%
            (entity_id, self.entityparent, self.entityaltparent)
            )
        if self.entityclass.exists(self.entityparent, entity_id, altparent=self.entityaltparent):
            return self.entityclass.load(self.entityparent, entity_id, altparent=self.entityaltparent)
        return None

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
            log.warning("EntityTypeInfo missing entityparent; type_id %s"%(self.type_id))
        return

    def enum_entities(self, usealtparent=False):
        """
        Iterate over entities in collection with current type.

        usealtparent    is True if site-wide entities are to be included.
        """
        altparent = self.entityaltparent if usealtparent else None
        if self.entityparent:
            for e in self.entityparent.child_entities(
                    self.entityclass, 
                    altparent=altparent):
                yield e
        else:
            log.warning("EntityTypeInfo missing entityparent; type_id %s"%(self.type_id))
        return

    def get_initial_entity_values(self, entity_id):
        """
        Returns an initial value dictionary for the indicated entity.

        Attempts to read initial values from the type parent directory.
        Failing that, returns system-wide default values.
        """
        values = (
            { '@type':              ["annal:EntityData"]
            , ANNAL.CURIE.type_id:  self.type_id
            , RDFS.CURIE.label:     "%s/%s/%s"%
                                    (self.coll_id, self.type_id, entity_id)
            , RDFS.CURIE.comment:   "Entity '%s' of type '%s' in collection '%s'"%
                                    (entity_id, self.type_id, self.coll_id)
            })
        init_entity = self.get_entity("_initial_values")
        if init_entity:
            values = init_entity.get_values()
            values.pop("@id", None)
            values.pop(ANNAL.CURIE.id,  None)
            values.pop(ANNAL.CURIE.url, None)
            values.pop(ANNAL.CURIE.uri, None)
        values[ANNAL.CURIE.id] = entity_id
        return values

# End.
