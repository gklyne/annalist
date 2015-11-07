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
import shutil
import json
import errno
import traceback
import logging
log = logging.getLogger(__name__)

from django.conf                import settings

from annalist                   import util
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
    """

    _entitytype     = ANNAL.CURIE.Entity
    _entitytypeid   = None
    _entityview     = "%(id)s/"     # Placeholder for testing
    _entitypath     = None          # Relative path from parent to entity (template)
    _entityfile     = None          # Relative reference to body file from entity
    _entityref      = None          # Relative reference to entity from body file
    _last_id        = None          # Last ID allocated

    def __init__(self, parent, entityid, altparent=None, idcheck=True, use_altpath=False):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see ._save() method.

        parent      is the parent entity from which the new entity is descended.
        entityid    the collection identifier for the collection
        altparent   is an alternative parent entity to search for this entity, using 
                    the alternative path for the entity type: this is used to augment 
                    explicitly created entities in a collection with site-wide 
                    installed metadata entites (i.e. types, views, etc.)
        idcheck     is set False to skip the valid-identifier check; used when initializing 
                    (unidentified) site data element
                    @@TODO: when collection-inheritance is introduced, this should go.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.  This is used by test code to force
                    an entity to be located on the alternative parent path.  In normal
                    use, this value is left unspecified (i.e. False).
                    @@TODO: when collection-inheritance is introduced, this should go.
        """
        if idcheck and not util.valid_id(entityid):
            raise ValueError("Invalid entity identifier: %s"%(entityid))
        relpath = self.relpath(entityid)
        if use_altpath:
            relpath = self.altpath(entityid)
        # log.debug(
        #     "  _ Entity.__init__: id %s, parenturl %s, parentdir %s, relpath %s"%
        #     (entityid, parent._entityurl, parent._entitydir, relpath)
        #     )
        entity_url  = urlparse.urljoin(parent._entityurl, relpath) 
        entity_dir  = os.path.normpath(os.path.join(parent._entitydir, relpath))
        entity_base = parent._entitydir   # Used as safety check when removing data
        if not entity_dir.startswith(entity_base):
            entity_base = parent._entitybasedir
        # log.debug(
        #     "  _ Entity.__init__: entity_url %s, entity_dir %s"%
        #     (entity_url, entity_dir)
        #     )
        super(Entity, self).__init__(entity_url, entity_dir, entity_base)
        self._entityviewurl = urlparse.urljoin(
            parent._entityurl,
            self._entityview%{'id': entityid, 'type_id': self._entitytypeid}
            )
        self._parent        = parent
        self._altparent     = altparent     # Alternative to current entity to search
        self._entityalturl  = None
        self._entityaltdir  = None
        if altparent:
            altpath = self.altpath(entityid)
            self._entityalturl = altparent._entityurl+altpath
            self._entityaltdir = altparent._entitydir+altpath
            self._entityuseurl = None       # URI not known until entity is created or accessed
            log.debug(
                "Entity.__init__: entity alt URI %s, entity alt dir %s"%
                (self._entityalturl, self._entityaltdir)
                )
        self._entityid = entityid
        log.debug("Entity.__init__: entity_id %s, type_id %s"%(self._entityid, self.get_type_id()))
        return

    def get_view_url(self, baseurl=""):
        """
        Return URI used to view entity data.  For metadata entities, this may be 
        different from the URI at which the resource is located, per get_uri().
        The intent is to provide a URI that works regardless of whether the metadata
        is stored as site-wide or collection-specific data.
        """
        # log.debug(
        #     "Entity.get_view_url: baseurl %s, _entityviewurl %s"%
        #     (baseurl, self._entityviewurl)
        #     )
        return urlparse.urljoin(baseurl, self._entityviewurl)

    def get_alt_ancestry(self, altscope=None):
        """
        Returns a list of alternative entities to the current entity to search for possible 
        child entities.  Thne supplied altscope parameter indicates the scope to be searched.

        Currently, only one alternative may be declared, but a list is returned to 
        facilitate future developments supporting multiple inheritance paths.

        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  Currently defined values are:
                    "none" or None - search current entity only
                    "all" - search current entity and all alternative parent entities,
                    including their parents and alternatives.
        """
        if altscope is not None:
            if not isinstance(altscope, (unicode, str)):
                log.error("altscope must be string (%r supplied)"%(altscope))
                log.error("".join(traceback.format_stack()))
                raise ValueError("altscope must be string (%r supplied)"%(altscope))
        log.debug("Entity.get_alt_ancestry: %s/%s"%(self.get_type_id(), self.get_id()))
        return [self._altparent] if (altscope == "all" and self._altparent) else []

    def try_alt_ancestry(self, func, test=test_is_true, altscope=None):
        """
        Try applying the supplied function to the superclass object of current entity and 
        then any alternative ancestry of the current entity, until a result is obtained 
        that satisfies the supplied test.

        By default, looks for a result that evaluates as Boolan True

        If no satisfying value is found, returns the result from the last function
        executed (i.e. with the default test, returns None).
        """
        log.debug("Entity.try_alt_ancestry: %s/%s"%(self.get_type_id(), self.get_id()))
        # if altscope is not None:
        #     if not isinstance(altscope, (unicode, str)):
        #         log.error("altscope must be string (%r supplied)"%(altscope))
        #         log.error("".join(traceback.format_stack()))
        #         raise ValueError("altscope must be string (%r supplied)"%(altscope))
        v = func(super(Entity, self))
        if test(v):
            return v
        alt_parents = self._parent.get_alt_ancestry(altscope=altscope)
        for altparent in alt_parents:
            log.debug("Entity.try_alt_ancestry: alt %s/%s"%(altparent.get_type_id(), altparent.get_id()))
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
        """
        # log.debug(
        #     "Entity.try_alt_parentage: %s/%s with parent %r"%
        #     (cls._entitytypeid, entityid, parent)
        #     )
        e = cls._child_init(parent, entityid)
        #@@ TODO: review this: currently force URL returned to be that of original parent, not alt
        #         This is done to minimize disruption to tests while changing logic.
        #         If choose to stay with this, the logic should probably be pushed to get_view_url(),
        #         with actual view URL specified whenparent entity ()i.e. Collection) is initialized
        ub = e._entityurl       #@@
        uv = e._entityviewurl   #@@
        # log.warning("@@try_alt_parentage: ub %s, uv %s"%(ub, uv))
        # log.debug("Entity.try_alt_parentage: _child_init "+repr(e))
        v = func(e)
        if test(v):
            return (e, v)
        alt_parents = parent.get_alt_ancestry(altscope=altscope)
        # log.debug(
        #     "Entity.try_alt_parentage: alt_parents %r"%(alt_parents,)
        #     )
        for altparent in alt_parents:
            e = cls._child_init(altparent, entityid)
            e._entityurl = ub       #@@
            e._entityviewurl = uv   #@@
            v = func(e)
            if test(v):
                return (e, v)
        # Failed: log details
        log.debug(
            " __ no entity found for %s/%s with parent %s"%
            (cls._entitytypeid, entityid, parent)
            )
        log.debug("    alt parents tried: %r"%(alt_parents,))
        return (None, v)

    # Class helper methods

    @classmethod
    def allocate_new_id(cls, parent):
        if cls._last_id is None:
            cls._last_id = 1
        while True:
            newid = "%08d"%cls._last_id
            if not cls.exists(parent, newid):
                break
            cls._last_id += 1
        return newid

    @classmethod
    def relpath(cls, entityid):
        """
        Returns parent-relative path string for an identified entity of the given class.

        cls         is the class of the entity whose relative path is returned.
        entityid    is the local identifier (slug) for the entity.
        """
        # log.debug("Entity.relpath: entitytype %s, entityid %s"%(cls._entitytype, entityid))
        relpath = (cls._entitypath or "%(id)s")%{'id': entityid, 'type_id': cls._entitytypeid}
        # log.debug("Entity.relpath: %s"%(relpath))
        return relpath

    @classmethod
    def altpath(cls, entityid):
        """
        Returns alternative-parent-relative path string for an identified entity 
        of the given class.

        cls         is the class of the entity whose alternative relative path is returned.
        entityid    is the local identifier (slug) for the entity.
        """
        # log.debug("Entity.altpath: entitytype %s, entityid %s"%(cls._entitytype, entityid))
        altpath = (cls._entityaltpath or "%(id)s")%{'id': entityid, 'type_id': cls._entitytypeid}
        # log.debug("Entity.altpath: %s"%(altpath))
        return altpath

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
        p = util.entity_path(parent._entitydir, [cls.relpath(entityid)], cls._entityfile)
        log.debug("Entity.path: %s"%(p))
        return p

    # I/O helper functions (moved/copied from EntityRoot)

    def _alt_dir_path(self):
        """
        Return alternate directory and path for current entity body file
        """
        if not self._entityfile:
            raise ValueError("Entity._alt_dir_path without defined entity file path")
        if self._entityaltdir:
            # log.info("    _ Entity._alt_dir_path _entityaltdir %s"%(self._entityaltdir,))
            # log.info("    _ Entity._alt_dir_path _entityfile   %s"%(self._entityfile,))
            (basedir, filepath) = util.entity_dir_path(self._entityaltdir, [], self._entityfile)
            return (basedir, filepath)
        return (None, None)

    def _alt_dir_path_uri(self):
        (d, p) = self._alt_dir_path()
        return (d, p, self._entityalturl)

    def _children(self, cls, altscope=None):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        """
        coll_entity_ids = list(self._base_children(cls))
        site_entity_ids = list(itertools.chain.from_iterable(
            (alt._children(cls, altscope=altscope) for alt in self.get_alt_ancestry(altscope=altscope))
            ))
        # if altscope == "all" and self._altparent:
        #     site_entity_ids = self._altparent._children(cls, altscope=altscope)
        for entity_id in [f for f in site_entity_ids if f not in coll_entity_ids] + coll_entity_ids:
            if util.valid_id(entity_id):
                yield entity_id
        return

    def resource_file(self, resource_ref):
        """
        Returns a file object value for a resource associated with the current
        entity, or with a corresponding entity with the samem id descended from an 
        alternative parent, or None if the resource is not present.
        """
        file_obj = self.try_alt_ancestry(lambda e: e.resource_file(resource_ref), altscope="all")
        return file_obj

    # Create and access functions

    def child_entity_ids(self, cls, altscope=None):
        """
        Iterates over child entity identifiers of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        """
        for i in self._children(cls, altscope=altscope):
            if cls.exists(self, i, altscope=altscope):
                yield i
        return

    def child_entities(self, cls, altscope=None):
        """
        Iterates over child entities of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned, 
        and to instantiate and load data for the entities found.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        """
        for i in self._children(cls, altscope=altscope):
            e = cls.load(self, i, altscope=altscope)
            if e:
                yield e
        return

    @classmethod
    def _child_init(cls, parent, entityid, altscope=None, use_altpath=False):
        """
        Instantiate a child entity (e.g. for create and load methods) of a specified
        parent entity.

        parent      is the parent entity for which a child is instantiated.
        entityid    is the entity id of the child to be instantiated.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        """
        if use_altpath:
            # log.info(" __ Entity._child_init: (use_altpath) "+entityid)
            e = cls(parent, entityid, use_altpath=use_altpath)
        elif altscope:
            # log.info(" __ Entity._child_init: (altscope) "+entityid)
            e = cls(parent, entityid, altscope=altscope)
        else:
            # log.info(" __ Entity._child_init: (no altscope) "+entityid)
            e = cls(parent, entityid)
        return e

    @classmethod
    def create(cls, parent, entityid, entitybody, use_altpath=False):
        """
        Method creates a new entity or rewrites an existing entity.

        cls         is a class value used to construct the new entity value
        parent      is the parent entity from which the new entity is descended.
        entityid    is the local identifier (slug) for the new entity - this is 
                    required to be unique among descendents of a common parent.
        entitybody  is a dictionary of values that are stored for the created entity.
        use_altpath is set True if the entity is to be situated at the alternative
                    path relative to its parent.

        Returns the created entity as an instance of the supplied class object.
        """
        log.debug("Entity.create: entityid %s"%(entityid))
        e = cls._child_init(parent, entityid, use_altpath=use_altpath)
        e.set_values(entitybody)
        e._save()
        return e

    @classmethod
    def remove(cls, parent, entityid, use_altpath=False):
        """
        Method removes an entity, deleting its details, data and descendents from Annalist storage.

        cls         is the class of the entity to be removed
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns None on success, or a status value indicating a reason for value.
        """
        log.debug("Entity.remove: id %s"%(entityid))
        e = cls.load(parent, entityid, use_altpath=use_altpath)
        if e:
            e._remove(cls._entitytype)
        else:
            return Annalist_Error("Entity %s not found"%(entityid))
        return None

    @classmethod
    def load(cls, parent, entityid, altscope=None, use_altpath=False):
        """
        Return an entity with given identifier belonging to some given parent,
        or None if there is not such identity.

        cls         is the class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns an instance of the indicated class with data loaded from the
        corresponding Annalist storage, or None if there is no such entity.
        """
        log.debug("Entity.load: entity %s/%s, altscope %s"%
            (cls._entitytype, entityid, altscope)
            )
        # if altscope is not None:
        #     if not isinstance(altscope, (unicode, str)):
        #         log.error("altscope must be string (%r supplied)"%(altscope))
        #         log.error("".join(traceback.format_stack()))
        #         raise ValueError("altscope must be string (%r supplied)"%(altscope))
        entity = None
        if util.valid_id(entityid):
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
        # log.warning("@@Entity.load ub %r"%(entity._entityurl))
        # log.warning("@@Entity.load uv %r"%(entity._entityviewurl))
        # log.warning("@@Entity.load e  %r"%(entity))
        # log.warning("@@Entity.load v  %r"%(v))
        return entity

    @classmethod
    def exists(cls, parent, entityid, altscope=None, use_altpath=False):
        """
        Method tests for existence of identified entity descended from given parent.

        cls         is the class of the entity to be tested
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_ancestry` for more details.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns True if the entity exists, as determined by existence of the 
        entity description metadata file.
        """
        log.debug("Entity.exists: entitytype %s, parentdir %s, entityid %s"%
            (cls._entitytype, parent._entitydir, entityid)
            )
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
    def fileobj(cls, parent, entityid, filename, filetypeuri, mimetype, mode, altscope=None, use_altpath=False):
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
                    search for children.  See method `get_alt_ancestry` for more details.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

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
