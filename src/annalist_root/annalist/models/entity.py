"""
Common base classes for Annalist stored entities (collections, data, metadata, etc.)

This module implements a common pattern whereby an entity is related to a parent,
with storage directories and URIs allocated by combining the parent entity and a
local identifier (slug) for the descendent.

This module also implements the logic used to locate entities on alternate search paths,
such as site data or data inherited from other collections.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import itertools
import json
import errno
import traceback
import logging
log = logging.getLogger(__name__)

from django.conf                import settings

from annalist                   import layout
from annalist                   import util
from annalist                   import message
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL

from annalist.models.entityroot import EntityRoot

#   -------------------------------------------------------------------------------------------
#
#   Helpers
#
#   -------------------------------------------------------------------------------------------

def test_not_none(v):
    """
    Helper function tests for a non-None value
    """
    return v is not None

def test_is_true(v):
    """
    Helper function tests for a value that evaluates to Boolean True
    """
    return bool(v)

#   -------------------------------------------------------------------------------------------
#
#   Entity
#
#   -------------------------------------------------------------------------------------------

class Entity(EntityRoot):
    """
    This is the base class for all entities managed by Annalist as 
    descendents of some other entity.

    ## Entity access paths

    There are several key reference positions in a hierarchical entity structure:

    root            is the root URL for the entity, without a trailing "/", also
                    used to identify the entity.
    view            is a URL used to view or retrieve default entity (meta-)data.
    base            is a base URL for resolving relative references in entity data,
                    and corresponds to the container where entity data is stored.
    name            is the URL of the entity metadata resource (filename)
    prov            is the URL of the entity provenance resource (filename)

    In many cases, the root and base URLs are the same, but they may differ (e.g. for collections).

    These various URLs are constructed from the base URL of the parent entity using the following
    class variables, which must be defined by all subclasses of "Entity".  Constant strings for
    the actual values or value formatting templates used are defined in module layout.py.

    _entityroot     is a relative reference from the parent entity base URL to the entity root URL.
    _entityview     is a relative reference from the parent entity base URL to the entity view
                    URL.  This is generally _entityroot with a trailing "/" added.
    _entitybase     is a relative reference from the entity root URL to the entity base URL.
                    This is an empty string if the root is also the base URI, otherwise it
                    indicates a sub-container (sub-directory) where entity data is stored.
    _entityfile     is the resource name (filename) that can be used as a relative reference
                    from the entity base URL to access the entity metadata file.
    _entityprov     is the resource name (filename) that can be used as a relative reference
                    from the entity base URL to access the entity provenance file.
    _entityref      is a reverse relative reference from the base URL to the entity root URL
    _contextbase    is a relative reference from the entity base URL to the corresponding
                    JSON-LD context base URL for the containing collection.
    _contextref     is a relative reference from the entity base URL to the corresponding
                    JSON-LD context file URL for the containing collection.

    Other resources attached to an entity identified by names inthe entity metadatra, which
    are resolved against the entity base URL.

    The following methods are provided to access various entity and content URLs:

    entity.get_root_url()       returns the root URL for 'entity'
    entity.get_base_url()       returns the base URL for 'entity'
    entity.get_data_url()       returns the URL for entity metadata as JSON-LD
    entity.get_data_url(resource_name)
                                returns the URL for specified resource data

    entityroot.get_view_url()   returns the view URL for 'entity'
    """

    _last_id        = None          # Last ID allocated

    _entitytype     = ANNAL.CURIE.Entity
    _entitytypeid   = None

    _entityroot     = "%(id)s"
    _entityview     = "%(id)s/"
    _entitybase     = ""
    _entityfile     = None
    _entityprov     = None

    _entityref      = None
    _contextbase    = None
    _contextref     = None

    # _entitypath     = None          # Relative path from parent to entity (template)
    # _entityview     = "%(id)s/"     # Placeholder for testing
    # _entityfile     = None          # Relative reference to body file from entity base

    def __init__(self, parent, entityid, altparent=None):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see ._save() method.

        parent      is the parent entity from which the new entity is descended.
        entityid    the collection identifier for the collection
        altparent   is an alternative parent entity to search for this entity, using 
                    the alternative path for the entity type: this is used to augment 
                    explicitly created entities in a collection with site-wide 
                    installed metadata entites (i.e. types, views, etc.)
        """
        if not util.valid_id(entityid):
            msg = "Invalid entity identifier: %s"%(entityid)
            raise ValueError(msg)
        relpath = self.relpath(entityid)
        # log.debug(
        #     "@@  _ Entity.__init__: id %s, parenturl %s, parentdir %s, relpath %s"%
        #     (entityid, parent._entityurl, parent._entitydir, relpath)
        #     )
        entity_url  = urlparse.urljoin(parent._entityurl, relpath) 
        entity_dir  = os.path.normpath(os.path.join(parent._entitydir, relpath))
        entity_base = parent._entitydir   # Used as safety check when removing data
        if not entity_dir.startswith(entity_base):
            entity_base = parent._entitybasedir
        # log.debug(
        #     "@@  _ Entity.__init__: entity_url %s, entity_dir %s"%
        #     (entity_url, entity_dir)
        #     )
        entityviewurl = urlparse.urljoin(
            parent._entityviewurl,
            self._entityview%{'id': entityid, 'type_id': self._entitytypeid}
            )
        super(Entity, self).__init__(entity_url, entityviewurl, entity_dir, entity_base)
        self._entityid   = entityid
        self._parent     = parent
        self._ancestorid = entityid    # May be changed by subclass _local_find_alt_parents
        self._altparent  = altparent   # Alternative to current entity to search
        # log.debug("Entity.__init__: entity_id %s, type_id %s"%(self._entityid, self.get_type_id()))
        return

    def _get_ref_url(self, baseurl, entityurl, urlref):
        """
        Assemble a URL from supplied base URL and reference.

        The entity type id and id may be interpolated as if the supplied reference
        includes '%(type_id)s' and/or '%(id)s' respectively.
        """
        # log.debug("Entity._get_ref_url: baseurl %s, urlref %s"%(baseurl, urlref))
        if urlref is None:
            return None
        rooturl = urlparse.urljoin(baseurl, entityurl)
        return urlparse.urljoin(
            rooturl,
            urlref%({"type_id": self._entitytypeid, "id": self._entityid})
            )

    def get_root_url(self, baseurl=""):
        """
        Return entity root URL.
        """
        # log.debug(
        #     "Entity.get_view_url: baseurl %s, _entityrooturl %s"%
        #     (baseurl, self._entityviewurl)
        #     )
        return self._get_ref_url(baseurl, self._parent._entityurl, self._entityroot)

    def get_base_url(self, baseurl=""):
        """
        Return entity base URL.
        """
        return self._get_ref_url(baseurl, self._entityurl, self._entitybase)

    def get_data_url(self, resource_ref=None, baseurl=""):
        """
        Return entity data URL.
        """
        dataref = resource_ref or self._entityfile
        return self._get_ref_url(baseurl, self.get_base_url(baseurl=baseurl), dataref)

    def get_parent(self):
        """
        Return parent entity
        """
        return self._parent

    def set_alt_entities(self, altparent):
        """
        Update the alternative parent for the current entity.

        Returns a list of parents accessible from the supplied altparent (including itself)
        """
        # Set new alternative parent
        self._altparent = altparent
        # Build list of accessible parents, check for recursion
        parents = [self] + self._find_alt_parents(altscope="all")
        # log.info(
        #     "@@ Entity.set_alt_entities: %r altparent %r, parents %r"%
        #     (self.get_id(), altparent.get_id(), [p.get_id() for p in parents])
        #     )
        return parents

    def _local_find_alt_parents(self):
        """
        Returns a list of alternative parents for the current inheritance branch only;
        i.e. does not attempt to follow altparent chains in referenced trees.
        (That is handled by `_find_alt_parents` below.)

        This method may be overridden by classes that need to look higher in the 
        class inheritance tree to find alternative parent branches.
        """
        return [self._altparent] if self._altparent else []

    def _find_alt_parents(self, altscope=None, parents_seen=[]):
        """
        Local helper function returns a list of entities, not including the current entity,
        that are potentially in scope for containing entities considered to belong to
        the current entity.

        This function also checks for recursive references and returns an error if
        recursion is detected.

        See spike/tree_scan/tree_scan.lhs for algorithm.

            > parentlist e@(Entity {altparents=alts}) = e:altpath -- req (a)
            >     where
            >         altpath = mergealts e [ parentlist p | p <- alts ]
            >
            > mergealts :: Entity -> [[Entity]] -> [Entity]
            > mergealts _ []            = []
            > mergealts parent [altpath]
            >   | parent `elem` altpath = error ("Entity "++(show parent)++" has recursive altparent path")
            >   | otherwise             = altpath
            > mergealts parent (alt1:alt2:morealts) = 
            >     mergealts parent ((mergealtpair alt1 alt2):morealts)

        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  Currently defined values are:
                    "none" or None - search current entity only
                    "all" - search current entity and all alternative parent entities,
                        including their parents and alternatives.
                    "select" - same as "all" - used for generating a list of options
                        for a select/choice field.
                    "user" - search current entity and site entity if it is on the 
                        alternatives list; skips intervening entities.  Used to avoid 
                        inheriting user permissions with other configuration data.
                    "site" - site-level only: used for listing collections; by default, 
                        collections are not included in enumerations of entities. 
                        (See EntityRoot. and Site._children method)
                    "nosite" - collection-level only: used for listing entities from just
                        collections.  Used when cacheing data, where site data is assumed 
                        to be invariant, hence no need to re-load.
        """
        altparents = self._local_find_alt_parents()     # Class-specific local alternative discovery
        #@@
        # log.info(
        #     "@@ Entity._find_alt_parents: self %r, _altparents %r"%
        #     (self.get_id(), [ p.get_id() for p in altparents if p ])
        #     )
        #@@
        altparent_lists = []
        if altscope:
            for p in altparents:
                altp = []
                if p:
                    if p in parents_seen:
                        msg = (
                            "Entity._find_alt_parents %r contains recursive altparent reference)"%
                            (self.get_id(),)
                            )
                        log.error(msg)
                        raise ValueError(msg)
                    elif ( (altscope == "all") or (altscope == "select") or
                           ((altscope == "user")   and (p.get_id() == layout.SITEDATA_ID)) or
                           ((altscope == "nosite") and (p.get_id() != layout.SITEDATA_ID))
                           ):
                           # (altscope == "user") and (self._altparent.get_id() == layout.SITEDATA_ID)):
                        altp.append(p)
                    altp.extend(p._find_alt_parents(altscope=altscope, parents_seen=parents_seen+[p]))
                    altparent_lists.append(altp)
        parents = []
        for alt_list in altparent_lists:
            if self in alt_list:
                # Is this test redundant??  Keeping it for safety.
                msg = (
                    "Entity._find_alt_parents %r generates recursive altparent reference)"%
                    (self.get_id(),)
                    )
                log.error(msg)
                raise ValueError(msg)
            parents = self._merge_alt_parent_lists(parents, alt_list)
        return parents

    def _merge_alt_parent_lists(self, list1, list2):
        """
        Merge a pair of allternative parent lists, preserving depth ordering and where 
        possible placing entries from the first list ahead of entries from the second list.

        See spike/tree_scan/tree_scan.lhs for algorithm.

            > mergealtpair :: [Entity] -> [Entity] -> [Entity]
            > mergealtpair [] alt2      = alt2
            > mergealtpair alt1 []      = alt1
            > mergealtpair alt1@(h1:t1) alt2@(h2:t2)
            >   | h1 == h2              = h1:mergealtpair t1 t2     -- req (b) (part)
            >   | h1 `notElem` t2       = h1:mergealtpair t1 alt2   -- req (d)
            >   | h2 `notElem` t1       = h2:mergealtpair alt1 t2   -- req (d)
            >   | otherwise             = error ("Cannot preserve depth ordering of "++(show h1)++" and "++(show h2))
        """
        if not list1:
            return list2
        if not list2:
            return list1
        if list1[0] == list2[0]:
            return [list1[0]] + self. _merge_alt_parent_lists(list1[1:], list2[1:])
        if list1[0] not in list2:
            return [list1[0]] + self. _merge_alt_parent_lists(list1[1:], list2)
        if list2[0] not in list1:
            return [list2[0]] + self. _merge_alt_parent_lists(list1, list2[1:])
        msg = (
            "Entity._merge_alt_parent_lists: Cannot preserve depth ordering of %r and %r"%
            (list1[0].get_id(), list2[0].get_id())
            )
        log.error(msg)
        raise ValueError(msg)

    def get_alt_entities(self, altscope=None):
        """
        Returns a list of alternative entities to the current entity to search for possible 
        child entities.  The supplied altscope parameter indicates the scope to be searched.

        Currently, only one alternative may be declared, but a list is returned that
        includes alternatives to the alternatives available, and to facilitate future 
        developments supporting multiple inheritance paths.

        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `_find_alt_parents` for more details.
        """
        if altscope is not None:
            if not isinstance(altscope, (unicode, str)):
                log.error("altscope must be string (%r supplied)"%(altscope))
                log.error("".join(traceback.format_stack()))
                raise ValueError("altscope must be string (%r supplied)"%(altscope))
        # log.debug("Entity.get_alt_entities: %s/%s"%(self.get_type_id(), self.get_id()))
        alt_parents = [self] + self._find_alt_parents(altscope=altscope)
        # log.info(
        #     "@@ Entity.get_alt_entities: %s/%s -> %r"%
        #     (self.get_type_id(), self.get_id(), [ p.get_id() for p in alt_parents ])
        #     )
        return alt_parents

    def try_alt_entities(self, func, test=test_is_true, altscope=None):
        """
        Try applying the supplied function to the current entity and then any alternatives
        of the current entity, until a result is obtained that satisfies the supplied test.

        By default, looks for a result that evaluates as Boolan True

        If no satisfying value is found, returns the result from the last function
        executed (i.e. with the default test, returns None).

        The supplied function should operate on a single supplied entity, without 
        attempting to evaluate alternatives: this function will enumerate the 
        alternatives and make additional calls as needed.
        """
        # log.debug("Entity.try_alt_entities: %s/%s"%(self.get_type_id(), self.get_id()))
        # if altscope is not None:
        #     if not isinstance(altscope, (unicode, str)):
        #         log.error("altscope must be string (%r supplied)"%(altscope))
        #         log.error("".join(traceback.format_stack()))
        #         raise ValueError("altscope must be string (%r supplied)"%(altscope))
        v = func(self)
        if test(v):
            return v
        alt_parents = self._parent.get_alt_entities(altscope=altscope)
        for altparent in alt_parents:
            # log.debug("Entity.try_alt_entities: alt %s/%s"%(altparent.get_type_id(), altparent.get_id()))
            v = func(altparent)
            if test(v):
                return v
        return v

    @classmethod
    def try_alt_parentage(cls, parent, entityid, func, test=test_is_true, altscope=None):
        """
        Try applying the supplied function to an entity descended from the supplied
        parent, then any alternative parents to that parent, until a result is obtained 
        that satisfies the supplied test.

        By default, looks for a result that evaluates as Boolan True

        Returns a pair consising of the satisfied entity and the corresponding value.

        If no satisfying value is found, returns the result for the last entity tried
        executed;  i.e., with the default test, returns (None,None).

        The supplied function should operate on a single supplied entity, without 
        attempting to evaluate alternatives: this function will enumerate the 
        alternatives and make additional calls as needed.
        """
        e  = cls._child_init(parent, entityid)
        uv = e._entityviewurl
        v  = func(e)
        if test(v):
            return (e, v)
        alt_parents = parent.get_alt_entities(altscope=altscope)
        for altparent in alt_parents:
            e = cls._child_init(altparent, entityid, entityviewurl=uv)
            v = func(e)
            if test(v):
                # log.info("@@ try_alt_parentage ancestorid %s, entityid %s"%(altparent._ancestorid, entityid))
                return (e, v)
        # Failed: log details
        #@@
        # log.debug(
        #     "Entity.try_alt_parentage: no entity found for %s/%s with parent %s, scope %s"%
        #     (cls._entitytypeid, entityid, parent.get_id(), altscope)
        #     )
        # for ap in alt_parents:
        #     log.debug(" -- alt parent tried: %r"%(ap.get_id(),))
        #@@
        return (None, v)

    # Class helper methods

    @classmethod
    def allocate_new_id(cls, parent, base_id=None):
        """
        Allocate and return an as-yet-unused entity id for a member of the 
        indicated entity class as an offsprintof the indicated parent.  

        If "base_id" is specified, it is used as part of the new Id allocated 
        (used when copying an entity).
        """
        if base_id and util.valid_id(base_id):
            last_id     = 0
            name_format = base_id+"_%02d"
        else:
            last_id     = cls._last_id or 0
            name_format = "%08d"
        while True:
            last_id += 1
            new_id   = name_format%last_id
            if not cls.exists(parent, new_id):
                break
        if not base_id:
            cls._last_id = last_id
        return new_id

    @classmethod
    def relpath(cls, entityid):
        """
        Returns parent-relative path string for an identified entity of the given class.

        cls         is the class of the entity whose relative path is returned.
        entityid    is the local identifier (slug) for the entity.
        """
        # log.debug("Entity.relpath: entitytype %s, entityid %s"%(cls._entitytype, entityid))
        relpath = (cls._entityroot or "%(id)s")%{'id': entityid, 'type_id': cls._entitytypeid}
        # log.debug("Entity.relpath: %s"%(relpath))
        return relpath

    @classmethod
    def path(cls, parent, entityid):
        """
        Returns path string for accessing the body of the indicated entity.

        cls         is the class of the entity whose path is returned.
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        """
        # log.debug("Entity.path: entitytype %s, parentdir %s, entityid %s"%
        #     (cls._entitytype, parent._entitydir, entityid)
        #     )
        assert cls._entityfile is not None
        p = util.entity_path(
            parent._entitydir, 
            [cls.relpath(entityid), cls._entitybase], 
            cls._entityfile
            )
        log.debug("Entity.path: %s"%(p))
        return p

    @classmethod
    def meta_resource_name(cls, name_ext=".jsonld"):
        """
        Returns a metadata resource (file) name.

        By default, returns the name for JSON-LD data, but if an alternative name extension
        is profided returns a name with that extension instead.
        """
        #@@TODO: type selection should use type identifier rather than extension string?
        resource_name = cls._entityfile
        assert resource_name.endswith(".jsonld")
        if resource_name.endswith(".jsonld") and name_ext != ".jsonld":
            resource_name = resource_name[0:-7]+name_ext
        return resource_name

    # I/O helper functions (copied from or overriding EntityRoot)

    def _children(self, cls, altscope=None):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.

        @@NOTE:  The logic in this method is intended to return inherited values before
        values defined in the current collection.  It should probably be re-worked to return 
        entries in order from all inherited definitions.  The logic here could possibly
        be simplified to extract all values in the "alt parents" loop, (though the ordering 
        might be tricky to preserve that way).
        """
        # log.info("@@ Entity._children: parent %s, altscope %s"%(self.get_id(), altscope))
        coll_entity_ids = list(super(Entity, self)._children(cls, altscope=None))
        alt_parents     = self.get_alt_entities(altscope=altscope)
        # parent_entity_ids = list(itertools.chain.from_iterable(
        #     ( super(Entity, alt)._children(cls, altscope=altscope) 
        #       for alt in alt_parents # self.get_alt_entities(altscope=altscope)
        #     )))     # See https://docs.python.org/2/library/itertools.html#itertools.chain
        parent_entity_ids = []
        for alt in alt_parents:
            for eid in super(Entity, alt)._children(cls, altscope=altscope):
                # Filter out duplicates
                if eid not in parent_entity_ids:
                    parent_entity_ids.append(eid)
        # log.info("@@ Entity._children: coll_entity_ids %r, parent_entity_ids %r"%(coll_entity_ids, parent_entity_ids))
        # if altscope == "all" and self._altparent:
        #     parent_entity_ids = self._altparent._children(cls, altscope=altscope)
        for entity_id in [f for f in parent_entity_ids if f not in coll_entity_ids] + coll_entity_ids:
            if util.valid_id(entity_id):
                yield entity_id
        return

    def resource_file(self, resource_ref):
        """
        Returns a file object value for a resource associated with the current
        entity, or with a corresponding entity with the same id descended from an 
        alternative parent, or None if the resource is not present.
        """
        file_obj = self.try_alt_entities(
            lambda e: super(Entity,e).resource_file(resource_ref), 
            altscope="all"
            )
        return file_obj

    # Create and access functions

    def child_entities(self, cls, altscope=None):
        """
        Iterates over child entities of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned, 
        and to instantiate and load data for the entities found.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See `_find_alt_parents` for more details.
        """
        for i in self._children(cls, altscope=altscope):
            e = cls.load(self, i, altscope=altscope)
            if e:
                yield e
        return

    @classmethod
    def _child_init(cls, parent, entityid, entityviewurl=None):
        """
        Instantiate a child entity (e.g. for create and load methods) of a 
        specified parent entity.

        parent          is the parent entity for which a child is instantiated.
        entityid        is the entity id of the child to be instantiated.
        entityviewurl   if supplied, indicates an alternative URL to be used as the
                        view URL for the initialized entitty.
        """
        # log.info(" __ Entity._child_init: "+entityid)
        e = cls(parent, entityid)
        if entityviewurl is not None:
            e._entityviewurl = entityviewurl
        return e

    @classmethod
    def create(cls, parent, entityid, entitybody):
        """
        Method creates a new entity or rewrites an existing entity.

        cls         is a class value used to construct the new entity value
        parent      is the parent entity from which the new entity is descended.
        entityid    is the local identifier (slug) for the new entity - this is 
                    required to be unique among descendents of a common parent.
        entitybody  is a dictionary of values that are stored for the created entity.

        Returns the created entity as an instance of the supplied class object.
        """
        log.debug("Entity.create: entityid %s, parentid %s"%(entityid, parent.get_id()))
        e = cls._child_init(parent, entityid)
        e.set_values(entitybody)
        e._save()
        return e

    @classmethod
    def remove(cls, parent, entityid):
        """
        Method removes an entity, deleting its details, data and descendents from Annalist storage.

        cls         is the class of the entity to be removed
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.

        Returns None on success, or a status value indicating a reason for value.
        """
        log.debug("Entity.remove: id %s"%(entityid))
        e = cls.load(parent, entityid)
        if e:
            if "@error" in e:
                return Annalist_Error(
                    message.ENTITY_LOAD_ERROR%(
                        { 'id':       entityid
                        , 'file':     e["@error"]
                        , 'message':  e["@message"]
                        })
                    )
            e._remove(cls._entitytype)
        else:
            return Annalist_Error("Entity %s not found"%(entityid))
        return None

    @classmethod
    def load(cls, parent, entityid, altscope=None, reserved_ok=False):
        """
        Return an entity with given identifier belonging to some given parent,
        or None if there is not such identity.

        cls         is the class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See `_find_alt_parents` for more details.

        Returns an instance of the indicated class with data loaded from the
        corresponding Annalist storage, or None if there is no such entity.
        """
        # log.debug("Entity.load: entity %s/%s, altscope %s"%
        #     (cls._entitytype, entityid, altscope)
        #     )
        # if altscope is not None:
        #     if not isinstance(altscope, (unicode, str)):
        #         log.error("altscope must be string (%r supplied)"%(altscope))
        #         log.error("".join(traceback.format_stack()))
        #         raise ValueError("altscope must be string (%r supplied)"%(altscope))
        entity = None
        if util.valid_id(entityid, reserved_ok=reserved_ok):
            (e, v) = cls.try_alt_parentage(
                parent, entityid, (lambda e: e._load_values()), 
                altscope=altscope
                )
            # log.info(" __ Entity.load: _load_values "+repr(v))
            # log.info("entity.load %r"%(v,))
            if v:
                v = e._migrate_values(v)
                e.set_values(v)
                entity = e
        else:
            log.debug("Entity.load: invalid id %s"%entityid)
        # log.warning("@@Entity.load ub %r"%(entity._entityurl))
        # log.warning("@@Entity.load uv %r"%(entity._entityviewurl))
        # log.warning("@@Entity.load e  %r"%(entity))
        # log.warning("@@Entity.load v  %r"%(v))
        return entity

    @classmethod
    def exists(cls, parent, entityid, altscope=None):
        """
        Method tests for existence of identified entity descended from given parent.

        cls         is the class of the entity to be tested
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See `_find_alt_parents` for more details.

        Returns True if the entity exists, as determined by existence of the 
        entity description metadata file.
        """
        # log.debug("Entity.exists: entitytype %s, parentdir %s, entityid %s"%
        #     (cls._entitytype, parent._entitydir, entityid)
        #     )
        # if altscope is not None:
        #     if not isinstance(altscope, (unicode, str)):
        #         log.error("altscope must be string (%r supplied)"%(altscope))
        #         log.error("".join(traceback.format_stack()))
        #         raise ValueError("altscope must be string (%r supplied)"%(altscope))
        (e, v) = cls.try_alt_parentage(
            parent, entityid, (lambda e: e._exists()), 
            altscope=altscope
            )
        return v

    @classmethod
    def fileobj(cls, parent, entityid, filename, filetypeuri, mimetype, mode, altscope=None):
        """
        Method returns a file object value (like `open`) for accessing an imported
        resource associated with an entity (e.g. image, binary blob, etc.)

        cls         is the class of the entity to be tested
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        filename    is the local name for the file object to ne created or accessed.
        filetypeuri is a URI or CURIE indicating the type of resource for which a file
                    object is created.  This is used to determine details such as file 
                    extension used when creating a new file.
        mimetype    is a MIME content-type string for the resource representation used.
        mode        indicates how the resource is to be opened, with the same options
                    that are used with the standard `open` method (as far as they are 
                    applicable).  E.g. "wb" to create a new resource, and "r" to read 
                    an existing one.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See `_find_alt_parents` for more details.

        Returns a file object value, or None.
        """
        log.debug("Entity.fileobj: entitytype %s, parentdir %s, entityid %s"%
            (cls._entitytype, parent._entitydir, entityid)
            )
        if altscope is not None:
            if not isinstance(altscope, (unicode, str)):
                log.error("altscope must be string (%r supplied)"%(altscope))
                log.error("".join(traceback.format_stack()))
                raise ValueError("altscope must be string (%r supplied)"%(altscope))
        (e, v) = cls.try_alt_parentage(
            parent, entityid, 
            (lambda e: e._fileobj(filename, filetypeuri, mimetype, mode)), 
            altscope=altscope
            )
        return v

# End.
