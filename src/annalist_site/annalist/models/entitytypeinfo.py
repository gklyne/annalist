"""
Gather information about an entity/record type
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import message
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
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

TYPE_CLASS_MAP = (
    { '_type':  RecordType
    , '_list':  RecordList
    , '_view':  RecordView
    , '_field': RecordField
    })

TYPE_MESSAGE_MAP = (
    { '_type':  TYPE_MESSAGES
    , '_list':  LIST_MESSAGES
    , '_view':  VIEW_MESSAGES
    , '_field': FIELD_MESSAGES
    })

class EntityTypeInfo(object):
    """
    Check a supplied type identifier, and access values for:
        Entity class
        Entity parent
        Entity alternative parent for site-wide values
        Type-dependent messages
    """

    def __init__(self, site, coll, type_id):
        """
        Set up type attribute values.

        site            current site object
        coll            collection object in which type is used
        type_id         entity type id, which is a collection-defined value,
                        or one of a number of special site-wide built-in types.

        Attributes of type information object are:

        recordtype      type object describing the identified type
        entityparent    Parent enbtity for entities of this type, or None if 
                        the type is not defined for the collection
        entityaltparent Alternative (site-wide) parent entity for built-in types, 
                        or None
        entityclass     Python class object for entity
        entitymessages  a table of message strings for diagnostics relating to 
                        operations on this type.
        """
        if type_id in TYPE_CLASS_MAP:
            self.recordtype      = RecordType.load(coll, type_id, site)
            self.entityparent    = coll
            self.entityaltparent = site
            self.entityclass     = TYPE_CLASS_MAP[type_id]
            self.entitymessages  = TYPE_MESSAGE_MAP[type_id]
        else:
            if RecordType.exists(coll, type_id, site):
                self.recordtype     = RecordType.load(coll, type_id)
                self.entityparent   = RecordTypeData(coll, type_id)
            else:                
                log.warning("EntityTypeInfo: RecordType %s not found"%type_id)
                self.recordtype     = None
                self.entityparent   = None
            self.entityaltparent = None
            self.entityclass     = EntityData
            self.entitymessages  = ENTITY_MESSAGES
        return

# End.
