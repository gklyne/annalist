from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
This module is used to cache information about relations for which transitive
closure computations are frequently required (e.g. rdfs:superClassOf, 
rdfs:superpropertyOf, etc.).  It is intended to concentrate transitive 
closure computations (and optimizations) that would otherwise be scattered 
across the codebase.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.exceptions            import Annalist_Error

from annalist.models.objectcache    import get_cache, remove_cache

#   ---------------------------------------------------------------------------
# 
#   Local helper functions
# 
#   ---------------------------------------------------------------------------

def make_cache_key(cache_type, coll_id, rel_id):
    return (cache_type, coll_id, rel_id)

#   ---------------------------------------------------------------------------
# 
#   Local helper functions to manage direct relations between values
# 
#   ---------------------------------------------------------------------------

def add_direct_rel(rel, v1, v2):
    """
    Local helper to add a direct relation
    """
    if v1 not in rel:
        rel[v1] = set()
    rel[v1].add(v2)
    return

def remove_direct_rel(rel, v1, v2):
    """
    Local helper to remove a direct relation
    """
    rel[v1].remove(v2)
    if rel[v1] == set():
        del rel[v1]     # Maintains consistency of get_values() method
    return

def get_closure(rel, v):
    """
    Return transitive closure of values v1 such that "v rel v1",
    given a dictionary of direct relations.

    Termination depends on directed relation; i.e.

        v1 in rel(v) => v not in get_closure(rel, v1)

    Thus the get_closure recursive call can never include v, as
    all values (v1) for which get_closure is called recursively are 
    values that have been added to the closure result (cv).
    """
    if v not in rel:
        return set()
    v1s = rel[v]
    cv  = v1s.union(*[get_closure(rel, v1) for v1 in v1s])
    return cv

#   ---------------------------------------------------------------------------
# 
#   Error class
# 
#   ---------------------------------------------------------------------------

class Closure_Error(Annalist_Error):
    """
    Class for errors raised by closure calculations.
    """
    def __init__(self, value=None, msg="Closure_error"):
        super(Closure_Error, self).__init__(value, msg)
        return

#   ---------------------------------------------------------------------------
# 
#   Closure cache class
# 
#   ---------------------------------------------------------------------------

class ClosureCache(object):
    """
    This class saves information used to calculate transitive closures of a 
    relation in a specified collection.

    In the following descriptions, the relation is taken to be defined 
    over some set values vals from a domain Val.

    Core methods:

        add_rel     :: Val, Val -> Bool | error
        remove_val  :: Val      -> Bool
        fwd_closure :: Val      -> Val*
        rev_closure :: Val      -> Val*

    Invariants:

    FORALL v, v1, v2 in vals:

    D (directed relation graph):

        D1: v not in fwd_closure(v)
        D2: v not in rev_closure(v)
        D3: v1 not in fwd_closure(v) or v1 not in rev_closure(v)

    S (symmetry):

        v2 in fwd_closure(v1) <=> v1 in rev_closure(v2)

    T (transitivity):

        v2 in fwd_closure(v1) and v3 in fwd_closure(v2) => v3 in fwd_closure(v1)
    """
    def __init__(self, coll_id, rel_uri):
        """
        Initialize.

        coll_id     Id of collection with which relation closure is scoped
        rel         URI of relation over which closure is calculated

        The parameters are provided for information about the scope of the closure, 
        and are used to access saved cache values, but do not of themselves affect the 
        actual closure calculations.

        The set of values over which the relation is defined is represented by 
        dictionaries of direct forward and reverse mappings from members of the set.
        Initializes these to empty dictionaries, corresponding to an empty set of
        values.

        The invariants are all trivially true for an emty value set.
        """
        super(ClosureCache, self).__init__()
        self._coll_id   = coll_id
        self._rel_uri   = rel_uri
        self._key       = make_cache_key("ClosureCache", coll_id, rel_uri)
        self._cache     = get_cache(self._key)
        self._cache.set("fwd", {})
        self._cache.set("rev", {})
        #@@@ self._rel       = { 'fwd': {}, 'rev': {} }
        return

    def remove_cache(self):
        self._cache = None
        remove_cache(self._key)
        return

    def get_collection_id(self):
        return self._coll_id

    def get_relation_uri(self):
        return self._rel_uri

    def add_rel(self, v1, v2):
        """
        Add a forward relation between v1 and v2.

        Returns True if a new relation is added, False if the relation is already defined
        or raises an error and leaves the ClosureCache unchanged if the new relation would 
        violate one of the invariants.
        """
        with self._cache.access("fwd", "rev") as rel:
            if v1 == v2:
                # Preserve invariant D1 (hence D2 by symmetry)
                msg = "Attempt to define relation with itself"
                raise Closure_Error(value=v1, msg=msg)
            if v2 in get_closure(rel["rev"], v1):
                # Preserve invariant D3
                msg="Attempt to define forward relation for which closure contains reverse relation"
                raise Closure_Error(value=(v1,v2), msg=msg)
            if (v1 in rel["fwd"]) and (v2 in rel["fwd"][v1]):
                # Already defined - no change hence invariants preserved
                return False
            # Add new relation: these assignments occur together, so symmetry of direct relations is preserved
            add_direct_rel(rel["fwd"], v1, v2)
            add_direct_rel(rel["rev"], v2, v1)
        return True

    def remove_val(self, v):
        """
        Remove value from set over which relation is defined.

        Operates by removing all direct relations that mention the value.
        """
        updated = False
        with self._cache.access("fwd", "rev") as rel:
            if v in rel["fwd"]:
                for v2 in rel["fwd"][v]:
                    # Remove reverse relations referencing this value (which must exist by symmetry)
                    remove_direct_rel(rel["rev"], v2, v)
                # Restore symmetry
                del rel["fwd"][v]
                updated = True
            if v in rel["rev"]:
                for v1 in rel["rev"][v]:
                    # Remove forward relations referencing this value (which must exist by symmetry)
                    remove_direct_rel(rel["fwd"], v1, v)
                # Restore symmetry
                del rel["rev"][v]
                updated = True
        return updated

    def fwd_closure(self, v):
        """
        Return transitive closure of values v1 for which "v rel v1"
        """
        with self._cache.access("fwd") as rel:
            return get_closure(rel["fwd"], v)

    def rev_closure(self, v):
        with self._cache.access("rev") as rel:
            return get_closure(rel["rev"], v)

    def get_values(self):
        """
        Returns the set of values over which the closure is currently defined.

        Also performs some consistency checks.

        (Defined mainly for testing.)
        """
        with self._cache.access("fwd", "rev") as rel:
            vf1s = frozenset(rel["fwd"].keys())    # Forward relation first values (v1: v1 rel v2)
            vr1s = frozenset(rel["rev"].keys())    # Reverse relation first values (v2: v1 rel v2)
            vf2s = frozenset().union(*[ rel["fwd"][vf1] for vf1 in vf1s ])
            vr2s = frozenset().union(*[ rel["rev"][vr1] for vr1 in vr1s ])
            assert vf1s == vr2s
            assert vr1s == vf2s
            return vf1s | vr1s

# End.
