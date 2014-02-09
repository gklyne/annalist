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
        self._entityid   = None
        self._entityuri  = entityuri if entityuri.endswith("/") else entityuri + "/"
        self._entitydir  = entitydir if entitydir.endswith("/") else entitydir + "/"
        self._values     = None
        log.debug("EntityRoot.__init__: entity URI %s, entity dir %s"%(self._entityuri, self._entitydir))
        return

    # General entity access methods

    def set_id(self, entityid):
        self._entityid = entityid
        return

    def get_id(self):
        return self._entityid

    def set_values(self, values):
        """
        Set or update values for a collection
        """
        self._values = values.copy()
        # @@TODO do we really want this ad hoc stuff in addition to the explicit data?
        self._values["id"]    = self._values.get("id",         self._entityid)
        self._values["uri"]   = self._values.get("uri",        self._entityuri)
        self._values["type"]  = self._values.get("type",       self._entitytype)
        self._values["title"] = (
            self._values.get("title",      None) or
            self._values.get("rdfs:label", "%s %s"%(self._entitytype, self._entityid))
            )
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
        # @@TODO: move logic from util to here and rationalize
        (basedir, filepath) = util.entity_dir_path(self._entitydir, [], self._entityfile)
        return (basedir, filepath)

    def _save(self):
        """
        Save current entity to Annalist storage
        """
        if not self._entityref:
            raise ValueError("Entity._save without defined entity reference")
        if not self._values:
            raise ValueError("Entity._save without defined entity values")
        (body_dir, body_file) = self._dir_path()
        util.ensure_dir(body_dir)
        # @@TODO: move logic from util to here and rationalize
        util.write_entity(
            body_file, self._entityref, self._values, 
            entityid=self._entityid, 
            entitytype=self._entitytype
            )
        return

    def _load_values(self):
        """
        Read current entity from Annalist storage, and return entity body
        """
        (body_dir, body_file) = self._dir_path()
        v = util.read_entity(body_file)
        return v

    # Entity as iterator: returns candidate identifiers of contained entities
    def __iter__(self):
        """
        Implement iterator protocol, returning candidate identifiers of 
        contained entities.  The caller is responsible for checking the validity 
        of each returned value.
        """
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
    _entityfile = None          # To be overriden by entity subclasses..
    _entityref  = None          # Relative reference to entity from body file

    def __init__(self, parent, entityid):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see .save() method.

        parent      is the parent entity from which the new entity is descended.
        entityid    the collection identifier for the collection
        """
        if not util.valid_id(entityid):
            raise ValueError("Invalid entity identifier: %s"%(entityid))
        super(Entity, self).__init__(parent._entityuri+entityid, parent._entitydir+entityid)
        self._entityid = entityid
        log.debug("Entity.__init__: ID %s"%(self._entityid))
        return

    @classmethod
    def path(cls, parent, entityid):
        """
        Returns path string for accessing the body of the indicated entity.

        cls         is the class of the entity whose path is returned.
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        """
        log.debug("Entity.path: entitytype %s, parentdir %s, entityid %s"%(cls._entitytype, parent._entitydir, entityid))
        assert cls._entityfile is not None
        p = util.entity_path(parent._entitydir, [entityid], cls._entityfile)
        log.debug("Entity.path: %s"%(p))
        return p

    @classmethod
    def create(cls, parent, entityid, entitybody):
        """
        Method creates a new entity.

        cls         is a class value used to construct the new entity value
        parent      is the parent entity from which the new entity is descended.
        entityid    is the local identifier (slug) for the new entity - this is 
                    required to be unique among descendents of a common parent.
        entitybody  is a dictionary of values that are stored for the created entity.

        Returns the created entity as an instance of the supplied class object.
        """
        log.debug("Entity.create: entityid %s"%(entityid))
        c = cls(parent, entityid)
        c.set_values(entitybody)
        c._save()
        return c

    @classmethod
    def load(cls, parent, entityid):
        """
        Return an entity with given identifier belonging to some given parent,
        or None if there is not such identity.

        cls         is the class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.

        Returns an instance of the indicated class with data loaded from the
        corresponding Annalist storage, or None if there is no such entity.
        """
        log.debug("Entity.load: entitytype %s, parentdir %s, entityid %s"%(cls._entitytype, parent._entitydir, entityid))
        e = cls(parent, entityid)
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
            if e['type'] == cls._entitytype and d.startswith(parent._entitydir):
                shutil.rmtree(d)
            else:
                raise Annalist_Error("Entity %s unexpected type %s or path %s"%(entityid, e['type'], d))
        else:
            return Annalist_Error("Entity %s not found"%(entityid))
        return None


# End.
