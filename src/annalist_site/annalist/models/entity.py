"""
Common base classes for Annalist stored entities (collections, data, metadata, etc.)

This module implements a common pattern whereby an entity is related to a parent,
with storage directories and URIs allocated by combining the parent entity and a
local identifier (slug) for the descendent.

Part of the purpose of this module is to abstract the underlying storage access
from the Annalist organization of presented entities.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil
import json
import errno

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist               import util
from annalist.exceptions    import Annalist_Error
from annalist.identifiers   import ANNAL

#   -------------------------------------------------------------------------------------------
#   EntityRoot
#   -------------------------------------------------------------------------------------------

class EntityRoot(object):
    """
    This is the base class for entities that do not have any parent entity
    (e.g. Annalist Site objects).

    An entity presents at least the following interface:
        cls._entitytype     type of entity (CURIE or URI)
        cls._entityfile     relative path to file where entity body is stored
        cls._entityref      relative reference to entity from body file
        self._entityid      ID of entity; may be None for "root" entities (e.g. site?)
        self._entityuri     URI at which entity is accessed
        self._entityurihost URI host at which entity is accessed (per HTTP host: header)
        self._entityuripath URI absolute path at which entity is accessed
        self._entitydir     directory where entity is stored
        self._values        dictionary of values in entity body
    """

    _entitytype = ANNAL.CURIE.EntityRoot
    _entityfile = None          # To be overriden by entity subclasses..
    _entityref  = None          # Relative reference to entity from body file

    def __init__(self, entityuri, entitydir):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see .save() method.

        entityuri   is the base URI at which the entity is accessed
        entitydir   is the base directory containing the entity
        """
        self._entityid      = None
        self._typeid        = None
        self._entityuri     = entityuri if entityuri.endswith("/") else entityuri + "/"
        self._entitydir     = entitydir if entitydir.endswith("/") else entitydir + "/"
        self._entityalturi  = None
        self._entityaltdir  = None
        self._values        = None
        self._entityurihost = util.entity_uri_host(self._entityuri, "")
        self._entityuripath = util.entity_uri_path(self._entityuri, "")
        log.debug("EntityRoot.__init__: entity URI %s, entity dir %s"%(self._entityuri, self._entitydir))
        return

    # General entity access methods

    def set_id(self, entityid):
        self._entityid = entityid
        return

    def get_id(self):
        return self._entityid

    def get_type_id(self):
        return self._typeid

    def get_uri(self, baseuri):
        """
        Get fully qualified URI referred to supplied base.

        NOTE: entities are stored, as far as possible, using relative references.
        But when an absolute reference is required, the current context URI must 
        be taken into account.  If the URI returned by this function is stored, 
        subsequent references to that value will be fixed, not relative, so the value
        should only be stored where they may be used as identifiers or "permalink"
        style locators, so the data can continue to be used when moved to a new location.
        """
        return urlparse.urljoin(baseuri, self._entityuri)

    def set_values(self, values):
        """
        Set or update values for a collection
        """
        self._values = values.copy()
        self._values[ANNAL.CURIE.id]        = self._values.get(ANNAL.CURIE.id,      self._entityid)
        self._values[ANNAL.CURIE.type]      = self._values.get(ANNAL.CURIE.type,    self._entitytype)
        self._values[ANNAL.CURIE.uri]       = self._values.get(ANNAL.CURIE.uri,     self._entityuri)
        self._values[ANNAL.CURIE.uripath]   = self._values.get(ANNAL.CURIE.uripath, self._entityuripath)
        self._values[ANNAL.CURIE.urihost]   = self._values.get(ANNAL.CURIE.urihost, "") or self._entityurihost
        return self._values

    def get_values(self):
        """
        Return collection metadata values
        """
        return self._values

    # I/O helper functions

    def _dir_path(self):
        """
        Return directory and path for current entity body file
        """
        if not self._entityfile:
            raise ValueError("Entity._dir_path without defined entity file path")
        (basedir, filepath) = util.entity_dir_path(self._entitydir, [], self._entityfile)
        return (basedir, filepath)

    def _alt_dir_path(self):
        """
        Return alternate directory and path for current entity body file
        """
        if not self._entityfile:
            raise ValueError("Entity._alt_dir_path without defined entity file path")
        if self._entityaltdir:
            (basedir, filepath) = util.entity_dir_path(self._entityaltdir, [], self._entityfile)
            return (basedir, filepath)
        return (None, self._entityfile)

    def _exists_path(self):
        """
        Test if the entity denoted by the current object has been created
        """
        for (d, p) in (self._dir_path(), self._alt_dir_path()):
            if d and os.path.isdir(d):
                if p and os.path.isfile(p):
                    return p
        return None

    def _exists(self):
        """
        Test if the entity denoted by the current object has been created
        """
        # @@TODO use _exists_path (above)
        for (d, p) in (self._dir_path(), self._alt_dir_path()):
            if d and os.path.isdir(d):
                if p and os.path.isfile(p):
                    return True
        return False

    def _save(self):
        """
        Save current entity to Annalist storage
        """
        # @@TODO: think about capturing provenance metadata too.
        if not self._entityref:
            raise ValueError("Entity._save without defined entity reference")
        if not self._values:
            raise ValueError("Entity._save without defined entity values")
        (body_dir, body_file) = self._dir_path()
        log.debug("EntityRoot._save: dir %s, file%s"%(body_dir, body_file))
        fullpath = os.path.join(settings.SITE_SRC_ROOT, body_file)
        # Next is partial protection against code errors
        if not fullpath.startswith(settings.SITE_SRC_ROOT):
            raise ValueError("Attempt to create entity file outside Annalist site tree")
        # Create directory (if needed) and save data
        util.ensure_dir(body_dir)
        values = self._values.copy()
        values["@id"] = self._entityref
        if self._entityid:
            values[ANNAL.CURIE.id]   = self._entityid
        if self._entitytype:
            values[ANNAL.CURIE.type] = self._entitytype
        with open(fullpath, "wt") as entity_io:
            json.dump(values, entity_io, indent=2, separators=(',', ': '))
        return

    def _load_values(self):
        """
        Read current entity from Annalist storage, and return entity body
        """
        body_file = self._exists_path()
        if body_file:
            try:
                with open(body_file, "r") as f:
                    return json.load(f)
            except IOError, e:
                if e.errno != errno.ENOENT:
                    raise
        return None

    def _children(self, cls, include_alt=True):
        """
        Iterates over candidate child entities that are instances of an indicated
        class.  The supplied class is used to determine a subdirectory to be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        include_alt if set to False, returns only those children that are explicitly
                    descended from the current entity, otherwise also includes those
                    that are descended from the alternate entity or parent specified
                    when the current entity was created.  E.g. set this parameter to
                    `False` to exclude site-wide entities when scanning the views or
                    lists in a collection.
        """
        search_dirs = (self._entitydir, self._entityaltdir if include_alt else None)
        for dirpath in search_dirs:
            if dirpath:
                if cls and cls._entitypath:
                    dirpath = os.path.dirname(os.path.join(dirpath, cls._entitypath))
                assert "%" not in dirpath, "_entitypath template variable interpolation may be in filename part only"
                if os.path.isdir(dirpath):
                    files = os.listdir(dirpath)
                    for f in files:
                        if util.valid_id(f):
                            yield f
        return

    # Entity as iterator: returns candidate identifiers of contained entities
    def __iter__(self):
        """
        Implement iterator protocol, returning candidate identifiers of 
        contained entities.  The caller is responsible for checking the validity 
        of each returned value.
        """
        # @@TODO: consider caching result
        if os.path.isdir(self._entitydir):
            files = os.listdir(self._entitydir)
            for f in files:
                if util.valid_id(f):
                    yield f
        return

    # Special methods to facilitate access to entity values by dictionary operations
    # on the Entity object

    def keys(self):
        """
        Return collection metadata value keys
        """
        return self._values.keys()

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._values.items()

    def get(self, key, default):
        """
        Equivalent to dict.get() function
        """
        return self[key] if self._values and key in self._values else default

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._values[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._values[k] = v

#   -------------------------------------------------------------------------------------------
#   Entity
#   -------------------------------------------------------------------------------------------

class Entity(EntityRoot):
    """
    This is the base class for all entities managed by Annalist as 
    descendents of some other entity.
    """

    _entitytype = ANNAL.CURIE.Entity
    _entitypath = None          # Relative path from parent to entity (template)
    _entityfile = None          # Relative reference to body file from entity
    _entityref  = None          # Relative reference to entity from body file
    _last_id    = None          # Last ID allocated

    def __init__(self, parent, entityid, altentity=None, altparent=False):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see ._save() method.

        parent      is the parent entity from which the new entity is descended.
        entityid    the collection identifier for the collection
        altentity   is an alternative entity to search for certain kinds of child
                    entities:  this is used to augment explicitly created entities
                    in a collection with site-wide installed entites.
        altparent   if True (and altentity is not specified), indicates that
                    child entities may be found as children of alternate parents.
        """
        if not util.valid_id(entityid):
            raise ValueError("Invalid entity identifier: %s"%(entityid))
        relpath = self.relpath(entityid)
        super(Entity, self).__init__(parent._entityuri+relpath, parent._entitydir+relpath)
        self._entityalturi = None
        self._entityaltdir = None
        if altentity:
            self._entityalturi = altentity._entityuri
            self._entityaltdir = altentity._entitydir
        elif altparent:
            assert parent._entityalturi, "Parent has no alt entity (%s,%s)"%(entityid, parent._entityid)
            self._entityalturi = parent._entityalturi+relpath
            self._entityaltdir = parent._entityaltdir+relpath
        self._entityid = entityid
        self._typeid   = parent.get_id() 
        log.debug("Entity.__init__: ID %s"%(self._entityid))
        return

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
        log.debug("Entity.relpath: entitytype %s, entityid %s"%(cls._entitytype, entityid))
        relpath = (cls._entitypath or "%(id)s")%{'id': entityid}
        log.debug("Entity.relpath: %s"%(relpath))
        return relpath

    @classmethod
    def path(cls, parent, entityid):
        """
        Returns path string for accessing the body of the indicated entity.

        cls         is the class of the entity whose path is returned.
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altentity   is an alternative entity to look to when looking for 
                    some kinds of child entities.
        """
        log.debug("Entity.path: entitytype %s, parentdir %s, entityid %s"%(cls._entitytype, parent._entitydir, entityid))
        assert cls._entityfile is not None
        p = util.entity_path(parent._entitydir, [cls.relpath(entityid)], cls._entityfile)
        log.debug("Entity.path: %s"%(p))
        return p

    @classmethod
    def _child_entity(cls, parent, entityid, altentity=None, altparent=False):
        """
        Instatiate a chile entity (e.g. for create and load methods)
        """
        if altentity:
            e = cls(parent, entityid, altentity=altentity)
        elif altparent:
            e = cls(parent, entityid, altparent=altparent)
        else:
            e = cls(parent, entityid)
        return e

    @classmethod
    def create(cls, parent, entityid, entitybody, altentity=None):
        """
        Method creates a new entity.

        cls         is a class value used to construct the new entity value
        parent      is the parent entity from which the new entity is descended.
        entityid    is the local identifier (slug) for the new entity - this is 
                    required to be unique among descendents of a common parent.
        entitybody  is a dictionary of values that are stored for the created entity.
        altentity   is an alternative entity to look to when looking for 
                    some kinds of child entities.

        Returns the created entity as an instance of the supplied class object.
        """
        log.debug("Entity.create: entityid %s"%(entityid))
        e = cls._child_entity(parent, entityid, altentity=altentity)
        e.set_values(entitybody)
        e._save()
        return e

    @classmethod
    def load(cls, parent, entityid, altentity=None, altparent=False):
        """
        Return an entity with given identifier belonging to some given parent,
        or None if there is not such identity.

        cls         is the class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altentity   is an alternative entity to look to when looking for 
                    some kinds of child entities.

        Returns an instance of the indicated class with data loaded from the
        corresponding Annalist storage, or None if there is no such entity.
        """
        log.debug("Entity.load: entitytype %s, parentdir %s, entityid %s"%(cls._entitytype, parent._entitydir, entityid))
        e = cls._child_entity(parent, entityid, altentity=altentity, altparent=altparent)
        v = e._load_values()
        if v:
            e.set_values(v)
        else:
            e = None
        return e

    @classmethod
    def exists(cls, parent, entityid):
        """
        Method tests for existence of identified entity descended from given parent.

        cls         is the class of the entity to be tested
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.

        Returns True if the collection exists, as determined by existence of the 
        collection description metadata file.
        """
        log.debug("Entity.exists: entitytype %s, parentdir %s, entityid %s"%(cls._entitytype, parent._entitydir, entityid))
        p = cls.path(parent, entityid)
        return (p != None) and os.path.isfile(p)

    @classmethod
    def remove(cls, parent, entityid):
        """
        Method removes an entity, deleting its details, data and descendents from Annalist storage.

        cls         is the class of the entity to be removed
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.

        Returns None on sucess, of a status value indicating a reason for value.
        """
        log.debug("Colllection.remove: id %s"%(entityid))
        e = cls.load(parent, entityid)
        if e:
            d = e._entitydir
            # Extra check to guard against accidentally deleting wrong thing
            if e['annal:type'] == cls._entitytype and d.startswith(parent._entitydir):
                shutil.rmtree(d)
            else:
                raise Annalist_Error("Entity %s unexpected type %s or path %s"%(entityid, e['type'], d))
        else:
            return Annalist_Error("Entity %s not found"%(entityid))
        return None

# End.
