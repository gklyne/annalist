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

from django.conf                import settings

from annalist                   import util
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL

from annalist.models.entityroot import EntityRoot

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
        idcheck     is set False to skip the valid-identifier check
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.
        """
        if idcheck and not util.valid_id(entityid):
            raise ValueError("Invalid entity identifier: %s"%(entityid))
        relpath = self.relpath(entityid)
        if use_altpath:
            relpath = self.altpath(entityid)
        super(Entity, self).__init__(parent._entityurl+relpath, parent._entitydir+relpath)
        self._entityviewuri = parent._entityurl+self._entityview%{'id': entityid, 'type_id': self._entitytypeid}
        self._entityalturi  = None
        self._entityaltdir  = None
        if altparent:
            altpath = self.altpath(entityid)
            self._entityalturi = altparent._entityurl+altpath
            self._entityaltdir = altparent._entitydir+altpath
            self._entityuseuri = None   # URI not known until entity is created or accessed
            log.debug("Entity.__init__: entity alt URI %s, entity alt dir %s"%(self._entityalturi, self._entityaltdir))
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
        return urlparse.urljoin(baseurl, self._entityviewuri)

    # I/O helper functions

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
        relpath = (cls._entitypath or "%(id)s")%{'id': entityid, 'type_id': cls._entitytypeid}
        log.debug("Entity.relpath: %s"%(relpath))
        return relpath

    @classmethod
    def altpath(cls, entityid):
        """
        Returns parent-relative path string for an identified entity of the given class.

        cls         is the class of the entity whose alternative relative path is returned.
        entityid    is the local identifier (slug) for the entity.
        """
        log.debug("Entity.altpath: entitytype %s, entityid %s"%(cls._entitytype, entityid))
        altpath = (cls._entityaltpath or "%(id)s")%{'id': entityid, 'type_id': cls._entitytypeid}
        log.debug("Entity.altpath: %s"%(altpath))
        return altpath

    @classmethod
    def path(cls, parent, entityid):
        """
        Returns path string for accessing the body of the indicated entity.

        cls         is the class of the entity whose path is returned.
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        """
        log.debug("Entity.path: entitytype %s, parentdir %s, entityid %s"%
            (cls._entitytype, parent._entitydir, entityid)
            )
        assert cls._entityfile is not None
        p = util.entity_path(parent._entitydir, [cls.relpath(entityid)], cls._entityfile)
        log.debug("Entity.path: %s"%(p))
        return p

    # Create and access functions

    def child_entity_ids(self, cls, altparent=None):
        """
        Iterates over child entity identifiers of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altparent   is an alternative parent entity to be checked using the class's
                    alternate relative path, or None if only potential child IDs of the
                    current entity are returned.
        """
        for i in self._children(cls, altparent=altparent):
            if cls.exists(self, i, altparent=altparent):
                yield i
        return

    def child_entities(self, cls, altparent=None):
        """
        Iterates over child entities of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned, 
        and to instantiate and load data for the entities found.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altparent   is an alternative parent entity to be checked using the class's
                    alternate relative path, or None if only potential child IDs of the
                    current entity are returned.
        """
        for i in self._children(cls, altparent=altparent):
            e = cls.load(self, i, altparent=altparent)
            if e:
                yield e
        return

    @classmethod
    def _child_init(cls, parent, entityid, altparent=None, use_altpath=False):
        """
        Instantiate a child entity (e.g. for create and load methods)
        """
        if use_altpath:
            e = cls(parent, entityid, use_altpath=use_altpath)
        elif altparent:
            e = cls(parent, entityid, altparent=altparent)
        else:
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
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns the created entity as an instance of the supplied class object.
        """
        log.debug("Entity.create: entityid %s"%(entityid))
        e = cls._child_init(parent, entityid, use_altpath=use_altpath)
        e.set_values(entitybody)
        e._save()
        return e

    @classmethod
    def load(cls, parent, entityid, altparent=None, use_altpath=False):
        """
        Return an entity with given identifier belonging to some given parent,
        or None if there is not such identity.

        cls         is the class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altparent   is an alternative parent entity to search for the loaded entity, 
                    using the alternative path for the entity type.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns an instance of the indicated class with data loaded from the
        corresponding Annalist storage, or None if there is no such entity.
        """
        log.debug("Entity.load: entitytype %s, parentdir %s, entityid %s, altparentdir %s"%
            (cls._entitytype, parent._entitydir, entityid,
                altparent._entitydir if altparent else "(no alt)")
            )
        entity = None
        if util.valid_id(entityid):
            e = cls._child_init(parent, entityid, altparent=altparent, use_altpath=use_altpath)
            v = e._load_values()
            # log.info("entity.load %r"%(v,))
            if v:
                v = e._migrate_values(v)
                e.set_values(v)
                entity = e
        return entity

    @classmethod
    def exists(cls, parent, entityid, altparent=None, use_altpath=False):
        """
        Method tests for existence of identified entity descended from given parent.

        cls         is the class of the entity to be tested
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altparent   is an alternative parent entity to search for the tested entity, 
                    using the alternative path for the entity type.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns True if the entity exists, as determined by existence of the 
        entity description metadata file.
        """
        log.debug("Entity.exists: entitytype %s, parentdir %s, entityid %s"%
            (cls._entitytype, parent._entitydir, entityid)
            )
        e = cls._child_init(parent, entityid, altparent=altparent, use_altpath=use_altpath)
        return e._exists()

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
        log.debug("Colllection.remove: id %s"%(entityid))
        e = cls.load(parent, entityid, use_altpath=use_altpath)
        if e:
            d = e._entitydir
            # Extra check to guard against accidentally deleting wrong thing
            if cls._entitytype in e['@type'] and d.startswith(parent._entitydir):
                shutil.rmtree(d)
            else:
                log.error("Expected type_id: %s, got %s"%(cls._entitytypeid, e[ANNAL.CURIE.type_id]))
                log.error("Expected dirbase: %s, got %s"%(parent._entitydir, d))
                raise Annalist_Error("Entity %s unexpected type %s or path %s"%(entityid, e[ANNAL.CURIE.type_id], d))
        else:
            return Annalist_Error("Entity %s not found"%(entityid))
        return None

    @classmethod
    def fileobj(cls, parent, entityid, filename, filetypeuri, mimetype, mode, altparent=None, use_altpath=False):
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
        altparent   is an alternative parent entity to search for the tested entity, 
                    using the alternative path for the entity type.
        use_altpath is set True if this entity is situated at the alternative
                    path relative to its parent.

        Returns a file object value, or None.
        """
        log.debug("Entity.exists: entitytype %s, parentdir %s, entityid %s"%
            (cls._entitytype, parent._entitydir, entityid)
            )
        e = cls._child_init(parent, entityid, altparent=altparent, use_altpath=use_altpath)
        return e._fileobj(filename, filetypeuri, mimetype, mode)

# End.
