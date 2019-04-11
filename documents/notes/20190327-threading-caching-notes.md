# Thread-safe cache management

This file contains notes about thread-safe cache management for Annalist.

The challenge is this bug:

- [ ] BUG: Retrieving turtle data in production server fails.  Works OK in dev server.
    - (no data returned; apparent server resarts?; session data corrupted?)
    - gunicorn (version 19.9.0)
    - curl: (52) Empty reply from server after about 30 seconds.  gunicorn worker reboots about same time??
    - suspect deadlock on single-worker-thread as Turtle output needs to access context via HTTP.
        - TEST: raise work thread count to 2, and see if problem persists.  If so, bring forward use of memcached?
        - YES: raising the worker count to 2 fixes the problem, which (pretty much) confirms the deadlock hypothesis

The reason for restricting Annalist to a single process is so that there are not multiple copies of type, field and vocabulary caches, and transitive closures for sub/supertypes and sub/superproperties.

Thus, to solove this deadlock problem, we need to re-think this caching in Annalist.

May also need to re-think other concurrent access possibilities (e.g. record change while editing? Interlock on file system operations?)

## Cache code references

(Based on search for "cache")

- src/annalist_root/annalist/models/closurecache.py
    - add_direct_rel
    - remove_direct_rel
    - not referenced outside "models" and "tests" modules.
    - used by "collectionfieldcache" and "collectiontypecache"
    - NOTE: renewing object effectively invalidates the cache
- src/annalist_root/annalist/models/collectionentitycache.py
    - this is pretty central
    - caches organized by entity type, collection and scope
    - supports by-id and by-uri retrieval
    - not referenced outside "models" module.
- src/annalist_root/annalist/models/collection.py
    - maintains type/field/vocab caches
        - flush_collection_caches
        - flush_all_caches
        - many other methods
- src/annalist_root/annalist/models/collectiondata.py
    - calls tgt_coll.flush_all_caches at initialization
    - not used in live system?
- src/annalist_root/annalist/models/collectionfieldcache.py
    - subclass of collectionentitycache
    - adds sub/superproperty closure cache based on closurecache
    - overrides some methods to manage closure cache
- src/annalist_root/annalist/models/collectiontypecache.py
    - subclass of collectionentitycache
    - adds sub/supertype closure cache based on closurecache
    - overrides some methods to manage closure cache
- src/annalist_root/annalist/models/collectionvocabcache.py
    - subclass of collectionentitycache
- src/annalist_root/annalist/models/entityfinder.py
    - calls collection type cache methods
- src/annalist_root/annalist/models/entityroot.py
    - get_save_values: used to get values to be cached
- src/annalist_root/annalist/models/entitytypeinfo.py
    - calls collection type cache methods
- src/annalist_root/annalist/models/recordfield.py
    - calls collection cache management method(s)
- src/annalist_root/annalist/models/recordtype.py
    - calls collection cache management method(s)
- src/annalist_root/annalist/models/recordvocab.py
    - calls collection cache management method(s)

Thus, it appears that all cache management is handled within 2 modules:

    - src/annalist_root/annalist/models/closurecache.py
    - src/annalist_root/annalist/models/collectionentitycache.py


## Caching options:

- no cache: rely on faster data access
- local cache with invalidation signals between threads
- local cache with multi-thread in single address space, +interlock (hmmm)
- always use memcached (complicates local/dev installation)
- detect memcached and use if avcailable (reliable?)
- use settings to select local or memcached; e.g. setting for memcached access, if missing use local storage.
- ...
- need to make all invalidations explicit (not just throwing away reference)
- isolate low-level (memcached-like?) cach interface to single module
- check out memcached API again...

### Proposed strategy

(with a view to using memcached in "production" deployments)

1. Isolate all caching logic to a single module, using an API that maps easily to memcached.
2. Use a Python Lock object to interlock access to each cache object.  The only lock references needed should be within the cache management module.
3. Run gunicorn with multiple threads in a single worker process.

This should be sufficient to fix the immediate problem.

4. Plan how to use memcached as an alternative to interlocked local data; use `settings` to switch mechanism used.
5. Implement memcached interface.
6. Deploy with memcached, and test.
7. Using memcached, test with multiple gunicorn workers.
8. Document procedure for memcached deployment.
9. Think about testing a production service configuration.



## Form of cached data

### collectionentitycache.CollectionEntityCacheObject

3 dictionaries:

    self._entities_by_id      = {} 
        :: entity_id -> {"parent_id": entity_parent, "data": entity_data}

        `entity_data` is itself a dictionary.
        Updated atomically (i.e., both fields together, with no selective updates)

    self._entity_ids_by_uri   = {}
        :: entity_uri -> entity_id

    self._entity_ids_by_scope = {}
        :: scope_name -> [ entity_id ]
        Updated atomically.

### collectionentitycache.CollectionEntityCache

Static reference instantiated at load time for each cached entity type (i.e. currently Types, Fields and Vocabs).

Static dictionary:

    site_cache_by_type_id
        :: type_id -> (cache object)

        Entry added for each `CollectionEntityCache` created.
        Never invalidated, so can stick with local storage.


Per-collection dictionary for cached entity type:

    self._caches     = {}
        :: coll_id -> (cache object, subtype of CollectionEntityCacheObject)

        Has `flush_cache(coll_id)` method, called by collection.py and tests.
        Has `flush_all()` method, called by collection.py and test initialization.

I judge that this mapping object can be maintained locally, all value caching is handled in `CollectionEntityCacheObject`.  If value caching is across processes, the `CollectionEntityCache` object can safely be replicated per-process.

What is needed is is to ensure that the `flush_*` mathods do actually call a corresponding method on the object cache, and not just rely on the cachje going away.  (Use a finalizer to detect when this is not done?)


### closurecache.ClosureCache

Create separate instance for each combination of collection and relation.

2 dictionaries:

    self._fwd_rel   = {}   # Dictonary of direct forward relations in vals: Val -> Val*
    self._rev_rel   = {}   # Dictonary of direct reverse relations in vals: Val -> Val*

NOTE: the values are treated as sets rather than lists.

New values are added incrementally to each set, but the code could do a read/modify/write if a suitable interlock can be arranged.  (NOTE memcached has CAS "check and set", also "APPEND")

Will need to add a method for flushing a cache.


## Memcached notes

Flat key space.  Assume (and require) memcached instance is dedicated to Annalist.

Key construction; max 250 chars,

`CollectionEntityCacheObject`:

    ENT:/coll_id/type_id/entity_id (or use entity URL path?)

`ClosureCache`:

    FWD:/coll_id/property_uri/node_uri
    REV:/coll_id/property_uri/node_uri

Hmmm: do we need to hash the key to prevent overlength?



## Redis notes

Redis may be a better option.  Fewer concerns over key length, format, etc.  Also can handle storage of non-string values. (sets, lists, hashes, ...)

See:

SET, MSET, HMSET, HGET, HGETALL, LADD, LPUSH, etc.

https://redis.io/topics/quickstart
https://memcached.org/
https://github.com/memcached/memcached/blob/master/doc/protocol.txt
 https://pymemcache.readthedocs.io/en/latest/apidoc/pymemcache.client.base.html
 

...

