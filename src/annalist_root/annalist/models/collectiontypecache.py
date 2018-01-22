"""
This module is used to cache per-collection type information.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import layout
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.collectionentitycache  import (
    Cache_Error, CollectionEntityCacheObject, CollectionEntityCache
    )
from annalist.models.closurecache           import ClosureCache
from annalist.models.recordtype             import RecordType

#   ---------------------------------------------------------------------------
# 
#   Type-cache object class
# 
#   ---------------------------------------------------------------------------

class CollectionTypeCacheObject(CollectionEntityCacheObject):
    """
    This class is a type cache for a specified collection.

    It extends class CollectionEntityCacheObject with type-specific logic; notably
    overriding method _load_entity with additional logic to maintain a supertype
    closure cache, and methods to access that cache.
    """
    def __init__(self, coll_id, entity_cls=RecordType):
        """
        Initialize a cache object for a specified collection.

        coll_id         Collection id with which the type cache is associated.
        """
        super(CollectionTypeCacheObject, self).__init__(coll_id, entity_cls)
        self._supertype_closure = ClosureCache(coll_id, ANNAL.CURIE.supertype_uri)
        return

    def _load_entity(self, coll, type_entity):
        """
        Internal helper method loads type data to cache.
        Also updates supertype closure cache.

        Returns True if new type was added.
        """
        type_id     = type_entity.get_id()
        type_uri    = type_entity.get_uri()
        type_parent = type_entity.get_parent().get_id()
        type_data   = type_entity.get_save_values()
        add_type    = super(CollectionTypeCacheObject, self)._load_entity(coll, type_entity)
        if add_type:
            # Add relations for supertype references from the new type URI
            for supertype_obj in type_data.get(ANNAL.CURIE.supertype_uri, []):
                supertype_uri = supertype_obj["@id"]
                self._supertype_closure.add_rel(type_uri, supertype_uri)
            # Also add relations for references *to* the new type URI
            for try_subtype in self.get_all_entities(coll):
                sub_st_objs = try_subtype.get(ANNAL.CURIE.supertype_uri, [])
                sub_st_uris = [ sub_st_obj["@id"] for sub_st_obj in sub_st_objs ]
                if type_uri in sub_st_uris:
                    subtype_uri = try_subtype.get(ANNAL.CURIE.uri, None)
                    if subtype_uri:
                        self._supertype_closure.add_rel(subtype_uri, type_uri)
        return add_type

    def _drop_entity(self, coll, type_id):
        """
        Override method that drops entity from cache, to also remove references
        from the supertype closure cache.

        Returns the type entity removed, or None if not found.
        """
        type_entity = super(CollectionTypeCacheObject, self)._drop_entity(coll, type_id)
        if type_entity:
            type_uri = type_entity.get_uri()
            self._supertype_closure.remove_val(type_uri)
        return type_entity

    def get_type_uri_supertype_uris(self, type_uri):
        """
        Returns all supertype URIs for a specified type URI.

        Returns all supertype URIs, even those for which there 
        is no defined type entity.
        """
        return self._supertype_closure.fwd_closure(type_uri)

    def get_type_uri_subtype_uris(self, type_uri):
        """
        Returns all subtype URIs for a specified type URI.

        Returns all subtype URIs, even those for which there 
        is no defined type entity.
        """
        return self._supertype_closure.rev_closure(type_uri)

    def get_type_uri_supertypes(self, coll, type_uri):
        """
        Returns all supertypes for a specified type URI.

        This method returns only those supertypes that are defined as entities.
        """
        self._load_entities(coll)
        for st_uri in self.get_type_uri_supertype_uris(type_uri):
            st = self.get_entity_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def get_type_uri_subtypes(self, coll, type_uri):
        """
        Returns all subtypes for a specified type URI.

        This method returns only those subtypes that are defined as entities.
        """
        self._load_entities(coll)
        for st_uri in self.get_type_uri_subtype_uris(type_uri):
            st = self.get_entity_from_uri(coll, st_uri)
            if st:
                yield st
        return

#   ---------------------------------------------------------------------------
# 
#   Collection type-cache class
# 
#   ---------------------------------------------------------------------------

class CollectionTypeCache(CollectionEntityCache):
    """
    This class manages type cache objects over multiple collections
    """
    def __init__(self):
        """
        Initialize.

        Initializes a value cache cache with no per-collection data.
        """
        super(CollectionTypeCache, self).__init__(CollectionTypeCacheObject, RecordType)
        return

    # Collection type cache allocation and access methods

    def set_type(self, coll, type_entity):
        """
        Save a new or updated type definition
        """
        return self.set_entity(coll, type_entity)

    def remove_type(self, coll, type_id):
        """
        Remove type from collection type cache.

        Returns the type entity removed if found, or None if not defined.
        """
        return self.remove_entity(coll, type_id)

    def get_type(self, coll, type_id):
        """
        Retrieve a type description for a given type Id.

        Returns a type object for the specified collection and type Id.
        """
        return self.get_entity(coll, type_id)

    def get_type_from_uri(self, coll, type_uri):
        """
        Retrieve a type description for a given type URI.

        Returns a type object for the specified collection and type URI.
        """
        return self.get_entity_from_uri(coll, type_uri)

    def get_all_type_ids(self, coll, altscope=None):
        """
        Returns all types currently available for a collection in the indicated scope.
        Default scope is types defined directly in the indicated collection.
        """
        return self.get_all_entity_ids(coll, altscope=altscope)

    def get_all_types(self, coll, altscope=None):
        """
        Returns all types currently available for a collection in the indicated scope.
        Default scope is types defined directly in the indicated collection.
        """
        return self.get_all_entities(coll, altscope=altscope)

    def get_type_uri_supertypes(self, coll, type_uri):
        """
        Returns all supertypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll)
        return type_cache.get_type_uri_supertypes(coll, type_uri)

    def get_type_uri_subtypes(self, coll, type_uri):
        """
        Returns all subtypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll)
        return type_cache.get_type_uri_subtypes(coll, type_uri)

    def get_type_uri_supertype_uris(self, coll, type_uri):
        """
        Returns all supertypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll)
        return type_cache.get_type_uri_supertype_uris(type_uri)

    def get_type_uri_subtype_uris(self, coll, type_uri):
        """
        Returns all subtypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll)
        return type_cache.get_type_uri_subtype_uris(type_uri)

# End.
