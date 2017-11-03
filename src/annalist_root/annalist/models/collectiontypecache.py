"""
This module is used to cache per-collection type information.

@@NOTE: the current implementation is type-specific, but the intent is that in due 
course it will be factored into a general value-cache and type-specific logic.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL

from annalist.models.closurecache   import ClosureCache
from annalist.models.recordtype     import RecordType

#   ---------------------------------------------------------------------------
# 
#   Local helper functions
# 
#   ---------------------------------------------------------------------------


#   ---------------------------------------------------------------------------
# 
#   Error class
# 
#   ---------------------------------------------------------------------------

class Cache_Error(Annalist_Error):
    """
    Class for errors raised by closure calculations.
    """
    def __init__(self, value=None, msg="Cache_error"):
        super(Cache_Error, self).__init__(value, msg)
        return

#   ---------------------------------------------------------------------------
# 
#   Type-cache object class
# 
#   ---------------------------------------------------------------------------

class CollectionTypeCacheObject(object):
    """
    This class is a type cache for a specified collection.

    NOTE: Type entities are instantiated with respect to a specified collection,
    but the collection objects are transient (regenerated for each request), so
    the cache stores the type values but not the instantiated type entity.
    """
    def __init__(self, coll_id):
        """
        Initialize a cache object for a specified collection.

        coll_id         Collection id with which the type cache is associated.
        """
        super(CollectionTypeCacheObject, self).__init__()
        self._coll_id           = coll_id
        self._types_by_id       = {}
        self._type_ids_by_uri   = {}
        self._supertype_closure = ClosureCache(coll_id, ANNAL.CURIE.supertype_uri)
        return

    def get_coll_id(self):
        return self._coll_id

    def is_not_empty(self):
        return self._types_by_id != {}

    def set_type(self, type_entity):
        """
        Save a new or updated type definition.
        """
        type_id     = type_entity.get_id()
        type_uri    = type_entity.get_uri()
        type_values = type_entity.get_values()
        add_type    = False
        if type_id not in self._types_by_id:
            self._types_by_id[type_id]      = type_values
            self._type_ids_by_uri[type_uri] = type_id
            self._supertype_closure.removeVal(type_uri)
            for st_obj in type_values[ANNAL.CURIE.supertype_uri]:
                st_uri = st_obj['@id']
                self._supertype_closure.addRel(type_uri, st_uri)
            add_type = True
        return add_type

    def remove_type(self, coll, type_id):
        """
        Remove type from collection type cache.

        Returns the type entity removed, or None if not found.
        """
        type_values = self._types_by_id.get(type_id, None)
        type_entity = self._make_type(coll, type_id, type_values)
        if type_entity:
            type_uri = type_entity.get_uri()
            del self._types_by_id[type_id]
            del self._type_ids_by_uri[type_uri]
            self._supertype_closure.removeVal(type_uri)
        return type_entity

    def get_type(self, coll, type_id):
        """
        Retrieve type description entity for a given type Id.

        Returns a type entity for the supplied type Id, or None 
        if not defined in the current cache object.
        """
        type_values = self._types_by_id.get(type_id, None)
        return self._make_type(coll, type_id, type_values)

    def get_type_from_uri(self, coll, type_uri):
        """
        Retrieve a type description for a given type URI.

        Returns a type object for the specified collecion and type URI,
        or None if the type URI does not exist
        """
        type_id = self._type_ids_by_uri.get(type_uri, None)
        return self.get_type(coll, type_id)

    def get_all_types(self, coll):
        """
        Returns all types currently defined for a collection.
        """
        for type_id, type_values in self._types_by_id.items():
            yield self._make_type(coll, type_id, type_values)
        return

    def get_type_uri_supertype_uris(self, type_uri):
        """
        Returns all supertype URIs for a specieid type URI.
        """
        return self._supertype_closure.fwdClosure(type_uri)

    def get_type_uri_subtype_uris(self, type_uri):
        """
        Returns all subtype URIs for a specieid type URI.
        """
        return self._supertype_closure.revClosure(type_uri)

    def get_type_uri_supertypes(self, coll, type_uri):
        """
        Returns all supertypes for a specieid type URI.
        """
        for st_uri in self.get_type_uri_supertype_uris(type_uri):
            st = self.get_type_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def get_type_uri_subtypes(self, coll, type_uri):
        """
        Returns all subtypes for a specieid type URI.
        """
        for st_uri in self.get_type_uri_subtype_uris(type_uri):
            st = self.get_type_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def _make_type(self, coll, type_id, type_values):
        """
        Local helper method to construct a type entity gioven its Id and values.

        Returns None if either Id or values evaluate as Boolean False (i.e. are None or empty).
        """
        type_entity = None
        if type_id and type_values:
            type_entity = RecordType._child_init(coll, type_id)
            type_entity.set_values(type_values)
        return type_entity

#   ---------------------------------------------------------------------------
# 
#   Collection type-cache class
# 
#   ---------------------------------------------------------------------------

class CollectionTypeCache(object):
    """
    This class manages multiple-collection cache objects
    """
    def __init__(self):
        """
        Initialize.

        Initializes a value cache cache with no per-collection data.
        """
        super(CollectionTypeCache, self).__init__()
        self._caches = {}
        return

    # @@TODO: these are candidates for a common base class
    # Generic collection cache alllocation and access methods

    def _get_cache(self, coll, cache_cls):
        """
        Local helper returns a cache object for a specified collection.

        Creates a new cache object if needed.

        coll        is a collection object for which a cache object is obtained
        cache_cls   is a class object for the cache object to be returned.  The class 
                    constructor is called with the collection id as parameter.
        """
        coll_id = coll.get_id()
        if coll_id not in self._caches.keys():
            # Create and save new cache object
            self._caches[coll_id] = cache_cls(coll_id)
        return self._caches[coll_id]

    def flush_cache(self, coll):
        """
        Remove all cached data for a specified collection.

        Returns True if the cache object was defined, otherwise False.

        coll        is a collection object for which a cache is removed.
        """
        coll_id = coll.get_id()
        cache = self._caches.pop(coll_id, None)
        return (cache is not None) and cache.is_not_empty()

    def collection_has_cache(self, coll):
        """
        Tests whether a cache object exists for the specified collection.

        Note: some access operations create an empty cache object, so this 
        is considered to be equivalent to no-cache.
        """
        coll_id = coll.get_id()
        cache   = self._caches.get(coll_id, None)
        return (cache is not None) and cache.is_not_empty()

    # Collection type cache alllocation and access methods

    def set_type(self, coll, type_entity):
        """
        Save a new or updated type definition
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.set_type(type_entity)

    def remove_type(self, coll, type_id):
        """
        Remove type from collection type cache.

        Returns the type entity removed if found, or None if not defined.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.remove_type(coll, type_id)

    def get_type(self, coll, type_id):
        """
        Retrieve a type description for a given type Id.

        Returns a type object for the specified collecion and type Id.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_type(coll, type_id)

    def get_type_from_uri(self, coll, type_uri):
        """
        Retrieve a type description for a given type URI.

        Returns a type object for the specified collecion and type URI.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_type_from_uri(coll, type_uri)

    def get_all_types(self, coll):
        """
        Returns all types currently defined for a collection.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_all_types(coll)

    def get_type_uri_supertypes(self, coll, type_uri):
        """
        Returns all supertypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_type_uri_supertypes(coll, type_uri)

    def get_type_uri_subtypes(self, coll, type_uri):
        """
        Returns all subtypes for a specieid type URI.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_type_uri_subtypes(coll, type_uri)

# End.
