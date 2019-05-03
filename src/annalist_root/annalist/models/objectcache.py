from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
This module provides an object cacheing framework for arbitrary Python values.
The intent is thatall cacghe logic can be isolated, and may be re-implemented
using a network cache faclity such as MemCache or Redis.

The present implementation assumes a single-process, multi-threaded environment
and interlocks cache accesses to avoid possible cache-related race conditions.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2019, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import traceback
import threading
import contextlib

from annalist.exceptions            import Annalist_Error

#   ===================================================================
#
#   Error class
#
#   ===================================================================

class Cache_Error(Annalist_Error):
    """
    Class for errors raised by cache methods.
    """
    def __init__(self, value=None, msg="Cache_error (objectcache)"):
        super(Cache_Error, self).__init__(value, msg)
        return

#   ===================================================================
#
#   Cache creation and discovery
#
#   ===================================================================

globalcachelock  = threading.Lock() # Used to interlock creation/deletion of caches
objectcache_dict = {}               # Initial empty set of object caches
objectcache_tb   = {}

def get_cache(cachekey):
    """
    This function locates or creates an object cache.

    cachekey    is a hashable value that uniquely identifies the required cache
                (e.g. a string or URI).

    Returns the requested cache object, which may be created on-the-fly.
    """
    with globalcachelock:
        if cachekey not in objectcache_dict:
            objectcache_dict[cachekey] = ObjectCache(cachekey)
        objectcache = objectcache_dict[cachekey]    # Copy value while lock acquired
    return objectcache

def remove_cache(cachekey):
    """
    This function removes a cache from the set of object  caches

    cachekey    is a hashable value that uniquely identifies the required cache
                (e.g. a string or URI).
    """
    # log.debug("objectcache.remove_cache %r"%(cachekey,))
    objectcache = None
    with globalcachelock:
        if cachekey in objectcache_dict:
            objectcache = objectcache_dict[cachekey]
            del objectcache_dict[cachekey]
    # Defer operations that acquire the cache local lock until 
    # the global lock is released
    if objectcache:
        objectcache.close()
    return

# ===== @@@Unused functions follow; eventually, remove these? ====

def make_cache_unused_(cachekey):
    """
    This function creates an object cache.

    cachekey    is a hashable value that uniquely identifies the required cache
                (e.g. a string or URI).

    Returns the created cache object.
    """
    with globalcachelock:
        try:
            if cachekey in objectcache_dict:
                raise Cache_Error(cachekey, msg="Cache already exists")
            objectcache_dict[cachekey] = ObjectCache(cachekey)
            objectcache_tb[cachekey]   = traceback.extract_stack()
            objectcache = objectcache_dict[cachekey]    # Copy value while lock acquired
        except Exception as e:
            print("@@@@ Cache already exists", file=sys.stderr)
            print("".join(traceback.format_list(objectcache_tb[cachekey])), file=sys.stderr)
            print("@@@@", file=sys.stderr)
            raise
    return objectcache

def remove_all_caches_unused_():
    """
    This function removes all caches from the set of object caches
    """
    # log.debug("@@@@ remove_all_caches")
    objectcaches = []
    with globalcachelock:
        for cachekey in objectcache_dict.keys():
            # log.debug("@@@@ remove_all_caches %r"%(cachekey,))
            objectcaches.append(objectcache_dict[cachekey])
            del objectcache_dict[cachekey]
    # Defer operations that acquire the cache local lock until 
    # the global lock is released
    for objectcache in objectcaches:
        objectcache.close()
    return

def remove_matching_caches_unused_(match_fn):
    """
    This function removes all caches whose cache key is matched by the provided
    function from the set of object caches.

    match_fn    is a function that tests a supplied cache key, and returns
                True if the corresponding cache is to be removed.
    """
    objectcaches = []
    with globalcachelock:
        for cachekey in _find_matching_cache_keys(match_fn):
            objectcaches.append(objectcache_dict[cachekey])
            del objectcache_dict[cachekey]
    # Defer operations that acquire the cache local lock until 
    # the global lock is released
    for objectcache in objectcaches:
        objectcache.close()
    return

def _find_matching_cache_keys_unused_(match_fn):
    """
    A generator that returns all cache keys matching the supplied function.

    match_fn    is a function that tests a supplied cache key, and returns
                True if it mnatches some criterion.
    """
    for cachekey in objectcache_dict.keys():
        if match_fn(cachekey):
            yield cachekey
    return

#   ===================================================================
#
#   Object cache class
#
#   ===================================================================

class ObjectCache(object):
    """
    A class for caching objects of some type.

    The cache is identified by is cache key value that is used to distinguish 
    a particular object cache from all others (see also `getCache`)
    """

    def __init__(self, cachekey):
        # log.debug("ObjectCache.__init__: cachekey %r"%(cachekey,))
        self._cachekey  = cachekey
        self._cachelock = threading.Lock()  # Allocate a lock object for this cache
        self._cache     = {}                # Initial empty set of values
        self._opened    = traceback.extract_stack()
        self._closed    = None
        return

    def cache_key(self):
        """
        Return cache key (e.g. for use with 'remove_cache')
        """
        return self._cachekey

    def flush(self):
        """
        Remove all objects from cache.
        """
        # log.debug("ObjectCache.flush: cachekey %r"%(self._cachekey,))
        with self._cachelock:
            for key in self._cache.keys():
                del self._cache[key]
        return self

    def close(self):
        """
        Close down this cache object.  Once closed, it cannot be used again.
        """
        # log.debug("ObjectCache.close: cachekey %r"%(self._cachekey,))
        self.flush()
        self._cachelock = None              # Discard lock object
        self._closed    = traceback.extract_stack()
        return

    def set(self, key, value):
        """
        Save object value in cache (overwriting any existing value for the key).

        key     is a hashable value that uniquely identifies the required cache
                (e.g. a string or URI).
        value   is a (new) value that is to be associated with the key.
        """
        with self._cachelock:
            self._cache[key] = value
        return value

    def get(self, key, default=None):
        """
        Retrieve object value from cache, or return default value
        """
        if self._cachelock is None:
            msg = "Access after cache closed (%r, %s)"%(self._cachekey, key)
            log.error(msg)
            log.debug("---- closed at:")
            log.debug("".join(traceback.format_list(self._closed)))
            log.debug("----")
            raise Exception(msg)
        # print("@@@@ self._cachelock %r, self._cachekey %r"%(self._cachelock, self._cachekey))
        with self._cachelock:
            value = self._cache.get(key, default)
        return value

    def pop(self, key, default=None):
        """
        Remove object value from cache, return that or default value
        """
        with self._cachelock:
            value = self._cache.pop(key, default)
        return value

    @contextlib.contextmanager
    def access(self, *keys):
        """
        A context manager for interlocked access to a cached value.

        The value bound by the context manager (for a 'with ... as' assignment) is a
        dictionary that has entries for each of the valuyes in the supplied key values
        for which there is a previously cached value.

        On exit from the context manager, if the value under any of the given keys has 
        been changed, or if any new entries have been added, they are used to update the 
        cached values before the interlock is released.

        Use like this:

            with cacheobject.access("key1", "key2", ...) as value:
                # value is dict of cached values for given keys
                # interlocked processing code here
                # updates to value are written back to cache on leavinbg context

        See: https://docs.python.org/2/library/contextlib.html
        """
        with self._cachelock:
            value_dict = {}
            for key in keys:
                if key in self._cache:
                    value_dict[key] = self._cache[key]
            yield value_dict
            for key in value_dict:
                self._cache[key] = value_dict[key]
            # If needed: this logic removes keys deleted by yield code...
            # for key in keys:
            #     if key not in value_dict:
            #         del self._cache[key]
        return

    # ===== @@@ UNUSED - remove this in due course =====

    def find_unused_(self, key, load_fn, seed_value):
        """
        Returns cached value for key, or calls the supplied function to obtain a 
        value, and caches and returns that value.

        If a previously-cached value is present, the value returned is:

            (False, old-value)

        If a previously-cached value is not present, the function is called with 
        the supplied "seed_value" as a parameter, the resuling value is cached under
        the supplied key, and the return value is:

            (True, new-value)
        """
        # log.debug("ObjectCache.find: cachekey %r, key %r"%(self._cachekey, key))
        with self._cachelock:
            if key in self._cache:
                old_value = self._cache[key]
                result = (False, old_value)
            else:
                new_value = load_fn(seed_value)
                self._cache[key] = new_value
                result = (True, new_value)
        return result

# End.
