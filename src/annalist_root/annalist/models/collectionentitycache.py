from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
This module is used to cache per-collection information about entities of some
designated type.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import layout
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.objectcache    import get_cache, remove_cache # , remove_matching_caches

#   ---------------------------------------------------------------------------
# 
#   Local helper functions
# 
#   ---------------------------------------------------------------------------

def make_cache_key(cache_type, entity_type_id, coll_id):
    return (cache_type, entity_type_id, coll_id)

def match_cache_key_unused_(cache_types, entity_cls):
    def match_fn(cachekey):
        return (cachekey[0] in cache_types) and (cachekey[1] == entity_cls._entitytypeid)
    return match_fn

#   ---------------------------------------------------------------------------
# 
#   Error class
# 
#   ---------------------------------------------------------------------------

class Cache_Error(Annalist_Error):
    """
    Class for errors raised by closure calculations.
    """
    def __init__(self, value=None, msg="Cache_error (collectionentityache)"):
        super(Cache_Error, self).__init__(value, msg)
        return

#   ---------------------------------------------------------------------------
# 
#   Entity-cache object class
# 
#   ---------------------------------------------------------------------------

class CollectionEntityCacheObject(object):
    """
    This class is an entity cache for a specified collection and entity type.

    NOTE: entities are instantiated with respect to a specified collection,
    but the collection objects are transient (regenerated for each request), so
    the cache stores the entity values but not the instantiated entities.

    Two kinds of information are cached:

    1.  entity cache: details of all entities that are visible in
        this class, indexed by entity id and entity URI
    2.  scope cache: lists of entity ids that are visible in different scopes: used 
        when returning entity enumerations (see method "get_all_entities").

    The scope cache is populated by calls to "get_all_entities".  When a entity is 
    added to or removed from the entity cache, lacking information about the scopes 
    where it is visible, the scope cache is cleared.

    Scope values currently include "user", "all", "site"; None => "coll".
    Apart from treating None as collection local scope, the logic in this class
    treats scope names as opaque identifiers.  The scope logic is embedded mainly
    in the Entity and EntityRoot class methods "_children".
    """

    _cache_types = {"entities_by_id", "entity_ids_by_uri", "entity_ids_by_scope"}

    def __init__(self, coll_id, entity_cls):
        """
        Initialize a cache object for a specified collection.

        coll_id         Collection id with which the entity cache is associated.
        """
        super(CollectionEntityCacheObject, self).__init__()
        self._coll_id             = coll_id
        self._entity_cls          = entity_cls
        self._type_id             = entity_cls._entitytypeid
        self._entities_by_id      = None
        self._entity_ids_by_uri   = None
        self._entity_ids_by_scope = None
        self._site_cache          = None
        return

    def _make_cache_key(self, cache_type):
        return make_cache_key(cache_type, self._type_id, self._coll_id)

    def _make_entity(self, coll, entity_id, entity_values):
        """
        Internal helper method to construct an entity given its Id and values.

        coll            is collection entity to which the new identity will belong
        entity_id       is the new entity id
        entity_values   is a dictionary containing:
                        ["parent_id"] is the id of the parent entity
                        ["data"] is a dictionary of values for the new entity

        Returns None if either Id or values evaluate as Boolean False (i.e. are None or empty).
        """
        entity = None
        if entity_id and entity_values:
            parent_id = entity_values["parent_id"]
            parent    = coll
            if coll.get_id() != parent_id:
                for parent in coll.get_alt_entities(altscope="all"):
                    if parent.get_id() == parent_id:
                        break
                else:
                    msg = (
                        "Saved parent id %s not found for entity %s/%s in collection %s"%
                        (parent_id, self._type_id, entity_id, coll.get_id())
                        )
                    log.error(msg)
                    raise ValueError(msg)
            entity = self._entity_cls._child_init(parent, entity_id)
            entity.set_values(entity_values["data"])
        return entity

    def _load_entity(self, coll, entity, entity_uri=None):
        """
        Internal helper method saves entity data to cache.
        This function does not actually read entity data.

        Returns True if new entity data is added, otherwise False.
        """
        entity_id     = entity.get_id()
        if not entity_uri:
            entity_uri    = entity.get_uri()
        entity_parent = entity.get_parent().get_id()
        entity_data   = entity.get_save_values()
        #@@TODO: remove this
        # def _load_entity_data(old_value):
        #     # Update other caches while _entities_by_id lock is acquired
        #     self._entity_ids_by_uri.set(entity_uri, entity_id)
        #     self._entity_ids_by_scope.flush()
        #     return {"parent_id": entity_parent, "data": entity_data}
        # add_entity, _ = self._entities_by_id.find(entity_id, _load_entity_data, None)
        #@@
        add_entity = False
        with self._entities_by_id.access(entity_id) as es:
            if entity_id not in es:
                # Update cache via context handler
                es[entity_id] = {"parent_id": entity_parent, "data": entity_data}
                # Update other caches while _entities_by_id lock is acquired
                self._entity_ids_by_uri.set(entity_uri, entity_id)
                self._entity_ids_by_scope.flush()
                add_entity = True
        return add_entity

    def _load_entities(self, coll):
        """
        Initialize cache of entities, if not already done.

        NOTE: site level entitites are cached separately by the collection cache 
        manager, and merged separately.  Hence "nosite" scope here.

        From entity.py:
            "nosite" - collection-level only: used for listing entities from just
                collections.  Used when cacheing data, where site data is assumed 
                to be invariant, hence no need to re-load.
        """
        scope_name = "nosite" if self._site_cache else "all"
        if self._entities_by_id is None:
            self._entities_by_id      = get_cache(self._make_cache_key("entities_by_id"))
            self._entity_ids_by_uri   = get_cache(self._make_cache_key("entity_ids_by_uri"))
            self._entity_ids_by_scope = get_cache(self._make_cache_key("entity_ids_by_scope"))
            for entity_id in coll._children(self._entity_cls, altscope=scope_name):
                t = self._entity_cls.load(coll, entity_id, altscope=scope_name)
                self._load_entity(coll, t)
        return

    def _drop_entity(self, coll, entity_id):
        """
        Drop entity from collection cache.

        Returns the entity removed, or None if not found.
        """
        entity_values = self._entities_by_id.get(entity_id, None)
        entity        = self._make_entity(coll, entity_id, entity_values)
        if entity:
            entity_uri = entity.get_uri()
            self._entities_by_id.pop(entity_id, None)
            self._entity_ids_by_uri.pop(entity_uri, None)
            self._entity_ids_by_scope.flush()
        return entity

    def set_site_cache(self, site_cache):
        self._site_cache = site_cache
        return

    def get_coll_id(self):
        return self._coll_id

    def set_entity(self, coll, entity):
        """
        Save a new or updated entity definition.
        """
        self._load_entities(coll)
        self._load_entity(coll, entity)
        return

    def remove_entity(self, coll, entity_id):
        """
        Remove entity from collection cache.

        Returns the entity removed, or None if not found.
        """
        self._load_entities(coll)       # @@TODO: is this needed?
        return self._drop_entity(coll, entity_id)

    def get_entity(self, coll, entity_id):
        """
        Retrieve the entity for a given entity id.

        Returns an entity for the supplied entity Id, or None 
        if not defined for the current collection.
        """
        self._load_entities(coll)
        entity_values = self._entities_by_id.get(entity_id, None)
        if entity_values:
            return self._make_entity(coll, entity_id, entity_values)
        # If not in collection cache, look for value in site cache:
        if self._site_cache:
            return self._site_cache.get_entity(coll.get_site_data(), entity_id)
        return None

    def get_entity_from_uri(self, coll, entity_uri):
        """
        Retrieve an entity for a given entity URI.

        Returns an entity for the specified collecion and entuty URI,
        or None if the entity URI does not exist
        """
        self._load_entities(coll)
        entity_id = self._entity_ids_by_uri.get(entity_uri, None)
        if entity_id:
            entity    = self.get_entity(coll, entity_id)
            return entity
        # If not in collection cache, look for value in site cache:
        if self._site_cache:
            return self._site_cache.get_entity_from_uri(
                coll.get_site_data(), entity_uri
                )
        return None

    def get_all_entity_ids(self, coll, altscope=None):
        """
        Returns an iterator over all entity ids currently defined for a collection, 
        which may be qualified by a specified scope.

        NOTE: this method returns only those entity ids for which a record has
        been saved to the collection data storage.
        """
        #@@TODO: remove this
        # def get_scope_ids(scope_entity_ids=[]):
        #     # Collect entity ids for named scope
        #     for entity_id in coll._children(self._entity_cls, altscope=altscope):
        #         if entity_id != layout.INITIAL_VALUES_ID:
        #             scope_entity_ids.append(entity_id)
        #     return scope_entity_ids
        # self._load_entities(coll)
        # scope_name = altscope or "coll"     # 'None' designates collection-local scope
        # _, entity_ids = self._entity_ids_by_scope.find(scope_name, get_scope_ids, [])
        #@@
        self._load_entities(coll)
        scope_name = altscope or "coll"     # 'None' designates collection-local scope
        scope_entity_ids = []
        with self._entity_ids_by_scope.access(scope_name) as eids:
            if scope_name in eids:
                scope_entity_ids = eids[scope_name]
            else:
                # Collect entity ids for named scope
                for entity_id in coll._children(self._entity_cls, altscope=altscope):
                    if entity_id != layout.INITIAL_VALUES_ID:
                        scope_entity_ids.append(entity_id)
                # Update cache via context manager
                eids[scope_name] = scope_entity_ids
        return scope_entity_ids

    def get_all_entities(self, coll, altscope=None):
        """
        Returns a generator of all entities currently defined for a collection, which
        may be qualified by a specified scope.

        NOTE: this method returns only those records that have actually been saved to
        the collection data storage.
        """
        scope_entity_ids = self.get_all_entity_ids(coll, altscope=altscope)
        for entity_id in scope_entity_ids:
            t = self.get_entity(coll, entity_id)
            if t:
                yield t
        return

    def remove_cache(self):
        """
        Close down and release all entity cache data
        """
        if self._entities_by_id:
            remove_cache(self._entities_by_id.cache_key())
            self._entities_by_id = None
        if self._entity_ids_by_uri:
            remove_cache(self._entity_ids_by_uri.cache_key())
            self._entity_ids_by_uri = None
        if self._entity_ids_by_scope:
            remove_cache(self._entity_ids_by_scope.cache_key())
            self._entity_ids_by_scope = None
        return

#   ---------------------------------------------------------------------------
# 
#   Collection entity-cache class
# 
#   ---------------------------------------------------------------------------

coll_cache_by_type_id_coll_id = {}

class CollectionEntityCache(object):
    """
    This class manages multiple-collection cache objects
    """
    def __init__(self, cache_cls, entity_cls):
        """
        Initializes a value cache with no per-collection data.

        cache_cls   is a class object for the collaction cache objects to be used.
                    The constructor is called with collection id and entity class
                    as parameters (see method `_get_cache`).
        entity_cls  is a class object for the type of entity to be cached.
        """
        super(CollectionEntityCache, self).__init__()
        self._cache_cls  = cache_cls
        self._entity_cls = entity_cls
        self._type_id    = entity_cls._entitytypeid
        coll_cache_by_type_id_coll_id[self._type_id] = {}
        return

    # Generic collection cache alllocation and access methods

    def _get_site_cache(self):
        """
        Local helper returns a cache object for the site-wide entities
        """
        if layout.SITEDATA_ID not in coll_cache_by_type_id_coll_id[self._type_id]:
            # log.info(
            #     "CollectionEntityCache: creating %s cache for collection %s"%
            #     (self._type_id, layout.SITEDATA_ID)
            #     )
            # Create and save new cache object
            site_cache = self._cache_cls(layout.SITEDATA_ID, self._entity_cls)
            coll_cache_by_type_id_coll_id[self._type_id][layout.SITEDATA_ID] = site_cache
        return coll_cache_by_type_id_coll_id[self._type_id][layout.SITEDATA_ID]

    def _get_cache(self, coll):
        """
        Local helper returns a cache object for a specified collection.

        Creates a new cache object if needed.

        coll        is a collection object for which a cache object is obtained
        """
        coll_id = coll.get_id()
        # log.info(
        #     "CollectionEntityCache: get %s cache for collection %s"%
        #     (self._type_id, coll_id)
        #     )
        if coll_id not in coll_cache_by_type_id_coll_id[self._type_id]:
            # log.debug(
            #     "CollectionEntityCache: creating %s cache for collection %s"%
            #     (self._type_id, coll_id)
            #     )
            # Create and save new cache object
            coll_cache = self._cache_cls(coll_id, self._entity_cls)
            coll_cache.set_site_cache(self._get_site_cache())
            coll_cache_by_type_id_coll_id[self._type_id][coll_id] = coll_cache
        return coll_cache_by_type_id_coll_id[self._type_id][coll_id]

    def flush_cache(self, coll):
        """
        Remove all cached data for a specified collection.

        Returns True if the cache object was defined, otherwise False.

        coll        is a collection object for which a cache is removed.
        """
        coll_id = coll.get_id()
        cache   = coll_cache_by_type_id_coll_id[self._type_id].pop(coll_id, None)
        if cache:
            cache.remove_cache()
            # log.info(
            #     "CollectionEntityCache: flushed %s cache for collection %s"%
            #     (self._type_id, coll_id)
            #     )
            return True
        return False

    def flush_all(self):
        """
        Remove all cached data for all collections.
        """
        # remove_cache_types = CollectionEntityCacheObject._cache_types
        # find_matching_caches(
        #     match_cache_key(remove_cache_types, entity_cls),
        #     lambda cache: cache.close()
        #     )
        caches = coll_cache_by_type_id_coll_id[self._type_id]
        coll_cache_by_type_id_coll_id[self._type_id] = {}
        # log.info(
        #     "CollectionEntityCache: flushing %s cache for collections %r"%
        #     (self._type_id, caches.keys())
        #     )
        for coll_id in caches:
            caches[coll_id].remove_cache()
        return

    # Collection cache allocation and access methods

    def set_entity(self, coll, entity):
        """
        Save a new or updated type definition
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.set_entity(coll, entity)

    def remove_entity(self, coll, entity_id):
        """
        Remove entity from collection cache.

        Returns the entity removed if found, or None if not defined.
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.remove_entity(coll, entity_id)

    def get_entity(self, coll, entity_id):
        """
        Retrieve an entity for a given entity id.

        Returns an entity object for the specified collection and entity id.
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.get_entity(coll, entity_id)

    def get_entity_from_uri(self, coll, entity_uri):
        """
        Retrieve en entity for a given collection and entity URI.

        Returns an entity object for the specified collection and entity URI.
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.get_entity_from_uri(coll, entity_uri)

    def get_all_entity_ids(self, coll, altscope=None):
        """
        Returns all entities currently available for a collection in the indicated scope.
        Default scope is entities defined directly in the indicated collection.
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.get_all_entity_ids(coll, altscope=altscope)

    def get_all_entities(self, coll, altscope=None):
        """
        Returns all entities currently available for a collection in the indicated scope.
        Default scope is entities defined directly in the indicated collection.
        """
        entity_cache = self._get_cache(coll)
        return entity_cache.get_all_entities(coll, altscope=altscope)

# End.
