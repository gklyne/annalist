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
#
#   EntityRoot
#
#   -------------------------------------------------------------------------------------------

class EntityRoot(object):
    """
    This is the base class for entities that do not have any parent entity
    (e.g. Annalist Site objects).

    An entity presents at least the following interface:
        cls._entitytype     type of entity (CURIE or URI)
        cls._entitytypeid   local type id (slug) used in local URI construction
        cls._entityfile     relative path to file where entity body is stored
        cls._entityref      relative reference to entity from body file
        self._entityid      ID of entity; may be None for "root" entities (e.g. site?)
        self._entityuri     URI at which entity is accessed
        self._entityurihost URI host at which entity is accessed (per HTTP host: header)
        self._entityuripath URI absolute path at which entity is accessed
        self._entitydir     directory where entity is stored
        self._values        dictionary of values in entity body
    """

    _entitytype     = ANNAL.CURIE.EntityRoot
    _entitytypeid   = None          # To be overridden
    _entityfile     = None          # To be overriden by entity subclasses..
    _entityref      = None          # Relative reference to entity from body file

    def __init__(self, entityuri, entitydir):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see .save() method.

        entityuri   is the base URI at which the entity is accessed
        entitydir   is the base directory containing the entity
        """
        self._entityid      = None
        self._entityuri     = entityuri if entityuri.endswith("/") else entityuri + "/"
        self._entitydir     = entitydir if entitydir.endswith("/") else entitydir + "/"
        self._entityalturi  = None
        self._entityaltdir  = None
        self._entityuseuri  = self._entityuri
        self._values        = None
        self._entityurihost = util.entity_uri_host(self._entityuri, "")
        self._entityuripath = util.entity_uri_path(self._entityuri, "")
        log.debug("EntityRoot.__init__: entity URI %s, entity dir %s"%(self._entityuri, self._entitydir))
        return

    def __repr__(self):
        return "Entity: entityid %s, values %r"%(self._entityid, self._values)

    # General entity access methods

    def set_id(self, entityid):
        self._entityid = entityid
        return

    def get_id(self):
        return self._entityid

    def get_type_id(self):
        return self._entitytypeid

    def get_uri(self, baseuri=""):
        """
        Get fully qualified URI referred to supplied base.

        NOTE: entities are stored, as far as possible, using relative references.
        But when an absolute reference is required, the current context URI must 
        be taken into account.  If the URI returned by this function is stored, 
        subsequent references to that value will be fixed, not relative, so the value
        should only be stored where they may be used as identifiers or "permalink"
        style locators, so the data can continue to be used when moved to a new location.

        NOTE: this function always returns the primary URI associated with the entity.
        Where the entity is accessed at a secondary location, that is handled internally
        and not exposed through this function.  E.g. site-wide metadata entities are
        presented as belonging to a collection.  This allows for collection-specific
        specializations to be created without changing the URI used.
        """
        return urlparse.urljoin(baseuri, self._entityuri)

    def get_view_uri(self, baseuri=""):
        """
        Return URI used to view entity data.  For metadata entities, this may be 
        different from the URI at which the resource is located, per get_uri().
        The intent is to provide a URI that works regardless of whether the metadata
        is stored as site-wide or collection-specific data.
        """
        return self.get_uri(baseuri=baseuri)

    def set_values(self, values):
        """
        Set or update values for a collection
        """
        self._values = values.copy()
        self._values[ANNAL.CURIE.id]        = self._values.get(ANNAL.CURIE.id,      self._entityid)
        self._values[ANNAL.CURIE.type]      = self._values.get(ANNAL.CURIE.type,    self._entitytype)
        self._values[ANNAL.CURIE.uri]       = self._values.get(ANNAL.CURIE.uri,     self.get_view_uri())
        # self._values[ANNAL.CURIE.uripath]   = self._values.get(ANNAL.CURIE.uripath, self._entityuripath)
        # self._values[ANNAL.CURIE.urihost]   = self._values.get(ANNAL.CURIE.urihost, "") or self._entityurihost
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
        return (None, None)

    def _dir_path_uri(self):
        (d, p) = self._dir_path()
        return (d, p, self._entityuri)

    def _alt_dir_path_uri(self):
        (d, p) = self._alt_dir_path()
        return (d, p, self._entityalturi)

    def _exists_path(self):
        """
        Test if the entity denoted by the current object has been created.

        If found, also sets the enity in-use URI value for .get_uri()

        returns path of of object body, or None
        """
        for (d, p, u) in (self._dir_path_uri(), self._alt_dir_path_uri()):
            # log.info("_exists %s"%(p))
            if d and os.path.isdir(d):
                if p and os.path.isfile(p):
                    self._entityuseuri = u
                    return p
        return None

    def _exists(self):
        """
        Test if the entity denoted by the current object has been created.

        returns True or False.
        """
        return self._exists_path() is not None

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
        self._entityuseuri  = self._entityuri
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

    def _child_dirs(self, cls, altparent):
        """
        Iterates over directories which may contain child entities.

        cls         is a subclass of Entity indicating the type of children to
                    be located
        altparent   is an alternative parent entity to be checked using the specified
                    class's alternate relative path, or None if only potential children 
                    of the current entity are returned.
        """
        yield os.path.dirname(os.path.join(self._entitydir, cls._entitypath))
        if altparent and cls._entityaltpath:
            yield os.path.dirname(os.path.join(altparent._entitydir, cls._entityaltpath))
        return

    def _children(self, cls, altparent=None):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altparent   is an alternative parent entity to be checked using the class's
                    alternate relative path, or None if only potential child IDs of the
                    current entity are returned.
        """
        for dirpath in self._child_dirs(cls, altparent):
            assert "%" not in dirpath, "_entitypath/_entityaltpath template variable interpolation may be in filename part only"
            if os.path.isdir(dirpath):
                files = os.listdir(dirpath)
                log.debug("_children files %r"%files)
                for f in files:
                    if util.valid_id(f):
                        yield f
        return

    def __iter__(self):
        """
        Return entity value keys
        """
        if self._values:
            for k in self._values:
                yield k
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

# End.
