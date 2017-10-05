"""
This module is used to cache information about relations for which transitive
closure computations are frequently required (e.g. rdfs:superClassOf, 
rdfs:superpropertyOf, etc.).  It is intended to concentrate transitive 
closure computations (and optimizations) that would otherwise be scattered 
across the codebase.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.exceptions    import Annalist_Error

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
        del rel[v1]     # Maintains consistency of getValues() method
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
        super(Annalist_Error, self).__init__(value, msg)
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

    In the following descriptions, the relatrion is taken to be defined 
    over some set values vals from a domain Val.

    Core methods:

        addRel      :: Val, Val -> Bool | error
        removeRel   :: Val, Val -> Bool
        fwdClosure  :: Val      -> Val*
        revClosure  :: Val      -> Val*

    Invariants:

    FORALL v, v1, v2 in vals:

    D (directed relation graph):

        D1: v not in fwdClosure(v)
        D2: v not in revClosure(v)
        D3: v1 not in fwdClosure(v) or v1 not in revClosure(v)

    S (symmetry):

        v2 in fwdClosure(v1) <=> v1 in revClosure(v2)

    T (transitivity):

        v2 in fwdClosure(v1) and v3 in fwdClosure(v2) => v3 in fwdClosure(v1)
    """
    def __init__(self, coll, rel):
        """
        Initialize.

        coll    is collection in which closure is calculated
        rel     is URI of relation over which closure is calculated

        The parameters are priovided for information about the scope of the closure, 
        and do not of themselves affect the actual closure calculations.

        The set of values over which the relation is defined is represented by 
        dictionaries of direct forward and reverse mappings from members of the set.
        Initializes these to empty dictionaries, corresponding to an empty set of
        values.

        The invariants are all trivially true for an emty value set.
        """
        super(ClosureCache, self).__init__()
        self._coll      = coll
        self._rel       = rel
        self._fwd_rel   = {}   # Dictonary of direct forward relations in vals: Val -> Val*
        self._rev_rel   = {}   # Dictonary of direct reverse relations in vals: Val -> Val*
        return

    def getCollection(self):
        return self._coll

    def getCollectionId(self):
        return self._coll.get_id()

    def getRelationURI(self):
        return self._rel

    def addRel(self, v1, v2):
        """
        Add a forward relation between v1 and v2.

        Returns True if a new relation is added, False if the relation is already defined
        or raises an error and leaves the ClosureCache unchangfed if the new relation would 
        violate one of the invariants.
        """
        if v1 == v2:
            # Preserve invariant D1 (hence D2 by symmetry)
            raise Closure_Error(value=v1, msg="Attempt to define relation with itself")
        if v2 in self.revClosure(v1):
            # Preserve invariant D3
            raise Closure_Error(value=(v1,v2), msg="Attempt to define forward relation for which closure contains reverse ralation")
        if (v1 in self._fwd_rel) and (v2 in self._fwd_rel[v1]):
            # Already defined - no change hence invariants preserved
            return False
        # Add new relation: these assignments occur together, so symmetry of direct relations is preserved
        add_direct_rel(self._fwd_rel, v1, v2)
        add_direct_rel(self._rev_rel, v2, v1)
        return True

    def removeVal(self, v):
        """
        Remove value from set over which relation is defined.

        Operates by removing all direct relations that mention the value.
        """
        updated = False
        if v in self._fwd_rel:
            for v2 in self._fwd_rel[v]:
                # Remove reverse relations referencing this value (which must exist by symmetry)
                remove_direct_rel(self._rev_rel, v2, v)
            # Restore symmetry
            del self._fwd_rel[v]
            updated = True
        if v in self._rev_rel:
            for v1 in self._rev_rel[v]:
                # Remove forward relations referencing this value (which must exist by symmetry)
                remove_direct_rel(self._fwd_rel, v1, v)
            # Restore symmetry
            del self._rev_rel[v]
            updated = True
        return updated

    def fwdClosure(self, v):
        """
        Return transitive closure of values v1 for which "v rel v1"
        """
        return get_closure(self._fwd_rel, v)

    def revClosure(self, v):
        return get_closure(self._rev_rel, v)

    def getValues(self):
        """
        Returns the set of values over which the closure is currently defined.

        Also performs some consistency checks.

        (Defined mainly for testing.)
        """
        vf1s = frozenset(self._fwd_rel.keys())    # Forward relation first values (v1: v1 rel v2)
        vr1s = frozenset(self._rev_rel.keys())    # Reverse relation first values (v2: v1 rel v2)
        vf2s = frozenset().union(*[ self._fwd_rel[vf1] for vf1 in vf1s ])
        vr2s = frozenset().union(*[ self._rev_rel[vr1] for vr1 in vr1s ])
        assert vf1s == vr2s
        assert vr1s == vf2s
        return vf1s | vr1s

# End.
