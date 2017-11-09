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

from annalist                       import layout
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL, RDFS

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

    Two kinds of information are cached:

    1.  type cache: details of all types that are visible to
        this class, indexed by type id and type URI
    2.  scope cache: lists of type Ids that are visible in different scopes: used 
        when returning type enumerations (see method "get_all_types").

    The scope cache is populated by calls to "get_all_types".  When a type is 
    added to or removed from the type cache, lacking information about the scopes 
    where it is visible, the scope cache is cleared.

    Scope cvalues currently include "user", "all", "site"; None => "coll".
    Apart from treating None as collection local scope, the logic in this class
    treats scope names as opaque identifiers.  The scope logic is embedded mainly
    in the Entity and EntityRoot class methods "_children".
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
        self._type_ids_by_scope = {}
        self._supertype_closure = ClosureCache(coll_id, ANNAL.CURIE.supertype_uri)
        return

    def _make_type(self, coll, type_id, type_values):
        """
        Internal helper method to construct a type entity given its Id and values.

        Returns None if either Id or values evaluate as Boolean False (i.e. are None or empty).
        """
        type_entity = None
        if type_id and type_values:
            parent_id = type_values["parent_id"]
            parent    = coll
            if coll.get_id() != parent_id:
                for parent in coll.get_alt_entities(altscope="all"):
                    if parent.get_id() == parent_id:
                        break
                else:
                    msg = (
                        "Saved parent id %s not found for type %s in collection %s"%
                        (parent_id, type_id, coll.get_id())
                        )
                    log.error(msg)
                    raise ValueError(msg)
            type_entity = RecordType._child_init(parent, type_id)
            type_entity.set_values(type_values["data"])
        return type_entity

    def _load_type(self, coll, type_entity):
        """
        Internal helper method loads type data to cache.

        Returns True if new type was added.
        """
        type_id     = type_entity.get_id()
        type_uri    = type_entity.get_uri()
        type_parent = type_entity.get_parent().get_id()
        type_data   = type_entity.get_save_values()
        add_type    = False
        if type_id not in self._types_by_id:
            self._types_by_id[type_id]      = {"parent_id": type_parent, "data": type_data}
            self._type_ids_by_uri[type_uri] = type_id
            self._supertype_closure.remove_val(type_uri)
            # Add relations for supertype references from the new type URI
            for st_obj in type_data.get(ANNAL.CURIE.supertype_uri, []):
                st_uri = st_obj["@id"]
                self._supertype_closure.add_rel(type_uri, st_uri)
            # Also add relations for references *to* the new type URI
            for sub_id in self._types_by_id:
                sub_values  = self._types_by_id[sub_id]
                sub_st_objs = sub_values["data"].get(ANNAL.CURIE.supertype_uri, [])
                sub_st_uris = [ sub_st_obj["@id"] for sub_st_obj in sub_st_objs ]
                if type_uri in sub_st_uris:
                    sub_uri = sub_values["data"].get(ANNAL.CURIE.uri, None)
                    if sub_uri:
                        self._supertype_closure.add_rel(sub_uri, type_uri)
            # Finish up, flush scope cache
            add_type = True
            self._type_ids_by_scope = {}
        return add_type

    def _load_types(self, coll):
        """
        Initialize cache of RecordType entities, if not already done
        """
        if self._types_by_id == {}:
            for type_id in coll._children(RecordType, altscope="all"):
                t = RecordType.load(coll, type_id, altscope="all")
                self._load_type(coll, t)
        return

    def get_coll_id(self):
        return self._coll_id

    def __is_not_empty(self):
        return self._types_by_id != {}

    def set_type(self, coll, type_entity):
        """
        Save a new or updated type definition.
        """
        self._load_types(coll)
        return self._load_type(coll, type_entity)

    def remove_type(self, coll, type_id):
        """
        Remove type from collection type cache.

        Returns the type entity removed, or None if not found.
        """
        self._load_types(coll)
        type_values = self._types_by_id.get(type_id, None)
        type_entity = self._make_type(coll, type_id, type_values)
        if type_entity:
            type_uri = type_entity.get_uri()
            del self._types_by_id[type_id]
            del self._type_ids_by_uri[type_uri]
            self._supertype_closure.remove_val(type_uri)
            self._type_ids_by_scope = {}
        return type_entity

    def get_type(self, coll, type_id):
        """
        Retrieve type description entity for a given type Id.

        Returns a type entity for the supplied type Id, or None 
        if not defined in the current cache object.
        """
        self._load_types(coll)
        type_values = self._types_by_id.get(type_id, None)
        return self._make_type(coll, type_id, type_values)

    def get_type_from_uri(self, coll, type_uri):
        """
        Retrieve a type description for a given type URI.

        Returns a type object for the specified collecion and type URI,
        or None if the type URI does not exist
        """
        self._load_types(coll)
        type_id     = self._type_ids_by_uri.get(type_uri, None)
        type_entity = self.get_type(coll, type_id)
        return type_entity

    def get_all_types(self, coll, altscope=None):
        """
        Returns a generator of all types currently defined for a collection, which may be 
        qualified by a specified scope.  See discussion at top of this class.

        NOTE: this method returns only those records that have actually been saved to
        the collection data storage.
        """
        self._load_types(coll)
        scope_name = altscope or "coll"     # 'None' designates collection-local scope
        if scope_name in self._type_ids_by_scope:
            scope_type_ids = self._type_ids_by_scope[scope_name]
        else:
            # Generate scope cache for named scope
            scope_type_ids = []
            for type_id in coll._children(RecordType, altscope=altscope):
                if type_id != layout.INITIAL_VALUES_ID:
                    scope_type_ids.append(type_id)
            self._type_ids_by_scope[scope_name] = scope_type_ids
        # Return type generator based on cache (using local copy as generator source)
        for type_id in scope_type_ids:
            t = self.get_type(coll, type_id)
            if t:
                yield t
        return

    def _get_type_uri_supertype_uris(self, type_uri):
        """
        Returns all supertype URIs for a specified type URI.
        """
        return self._supertype_closure.fwd_closure(type_uri)

    def _get_type_uri_subtype_uris(self, type_uri):
        """
        Returns all subtype URIs for a specified type URI.
        """
        return self._supertype_closure.rev_closure(type_uri)

    def get_type_uri_supertypes(self, coll, type_uri):
        """
        Returns all supertypes for a specieid type URI.
        """
        self._load_types(coll)
        for st_uri in self._get_type_uri_supertype_uris(type_uri):
            st = self.get_type_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def get_type_uri_subtypes(self, coll, type_uri):
        """
        Returns all subtypes for a specieid type URI.
        """
        self._load_types(coll)
        for st_uri in self._get_type_uri_subtype_uris(type_uri):
            st = self.get_type_from_uri(coll, st_uri)
            if st:
                yield st
        return

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
        cache   = self._caches.pop(coll_id, None)
        return (cache is not None)

    def flush_all(self):
        """
        Remove all cached data for all collections.
        """
        self._caches = {}
        return

    # def collection_has_cache(self, coll):
    #     """
    #     Tests whether a cache object exists for the specified collection.

    #     Note: some access operations create an empty cache object, so this 
    #     is considered to be equivalent to no-cache.
    #     """
    #     coll_id = coll.get_id()
    #     cache   = self._caches.get(coll_id, None)
    #     return (cache is not None) and cache.is_not_empty()

    # Collection type cache alllocation and access methods

    def set_type(self, coll, type_entity):
        """
        Save a new or updated type definition
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.set_type(coll, type_entity)

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

    def get_all_types(self, coll, altscope=None):
        """
        Returns all types currently available for a collection in the indicated scope.
        Default scope is types defined directly in the indicated collection.
        """
        type_cache = self._get_cache(coll, CollectionTypeCacheObject)
        return type_cache.get_all_types(coll, altscope=altscope)

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
