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
from annalist.identifiers   import ANNAL, RDF, RDFS
from annalist.resourcetypes import file_extension, file_extension_for_content_type
from annalist.util          import make_type_entity_id

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
        self._entityurl     URI at which entity is accessed
        # self._entityurlhost URI host at which entity is accessed (per HTTP host: header)
        # self._entityurlpath URI absolute path at which entity is accessed
        self._entitydir     directory where entity is stored
        self._values        dictionary of values in entity body
    """

    _entitytype     = ANNAL.CURIE.EntityRoot
    _entitytypeid   = None          # To be overridden
    _entityfile     = None          # To be overriden by entity subclasses..
    _entityref      = None          # Relative reference to entity from body file

    def __init__(self, entityurl, entitydir):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see .save() method.

        entityurl   is the base URI at which the entity is accessed
        entitydir   is the base directory containing the entity
        """
        self._entityid      = None
        self._entityurl     = entityurl if entityurl.endswith("/") else entityurl + "/"
        self._entitydir     = entitydir if entitydir.endswith("/") else entitydir + "/"
        self._entityalturl  = None
        self._entityaltdir  = None
        self._entityuseurl  = self._entityurl
        self._values        = None
        log.debug("EntityRoot.__init__: entity URI %s, entity dir %s"%(self._entityurl, self._entitydir))
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

    def get_type_entity_id(self):
        """
        Return type+entity Id that is unique within collection
        """
        return make_type_entity_id(self._entitytypeid, self._entityid)

    def get_label(self):
        """
        Return label string for the current entity.
        """
        return self._values.get(RDFS.CURIE.label, self._entityid)

    def get_url(self, baseurl=""):
        """
        Get fully qualified URL referred to supplied base.

        NOTE: entities are stored, as far as possible, using relative references.
        But when an absolute reference is required, the current context URL must 
        be taken into account.  If the URL returned by this function is stored, 
        subsequent references to that value will be fixed, not relative, so the value
        should only be stored where they may be used as identifiers or "permalink"
        style locators, so the data can continue to be used when moved to a new location.

        NOTE: this function always returns the primary URL associated with the entity.
        Where the entity is accessed at a secondary location, that is handled internally
        and not exposed through this function.  E.g. site-wide metadata entities are
        presented as belonging to a collection.  This allows for collection-specific
        specializations to be created without changing the URI used.
        """
        return urlparse.urljoin(baseurl, self._entityurl)

    def get_view_url(self, baseurl=""):
        """
        Return URL used to view entity data.  For metadata entities, this may be 
        different from the URL at which the resource is located, per get_url().
        The intent is to provide a URL that works regardless of whether the metadata
        is stored as site-wide or collection-specific data.

        This implementation just uses get_url(), but for entities that belong to a
        collection the URL is mapped via the web application to the underlying storage
        location.
        """
        return self.get_url(baseurl=baseurl)

    def get_view_url_path(self, baseurl=""):
        """
        Return URL path used to view entity data.  This is the URI-path of the URL
        returned by get_view_url (above)
        """
        return util.entity_url_path(self.get_view_url(), "")

    def set_values(self, values):
        """
        Set or update values for a collection
        """
        self._values = values.copy()
        self._values[ANNAL.CURIE.id]        = self._values.get(ANNAL.CURIE.id,      self._entityid)
        self._values[ANNAL.CURIE.type_id]   = self._values.get(ANNAL.CURIE.type_id, self._entitytypeid)
        self._values[ANNAL.CURIE.type]      = self._values.get(ANNAL.CURIE.type,    self._entitytype)
        if ANNAL.CURIE.url not in self._values:
            self._values[ANNAL.CURIE.url] = self.get_view_url_path()
        # log.info("set_values %r"%(self._values,))
        return self._values

    def get_values(self):
        """
        Return collection metadata values
        """
        return self._values

    def get_uri(self):
        """
        Return URI for current entity, which may be set explicitly or derived from
        its present URL.
        """
        return self._values.get(ANNAL.CURIE.uri, self._values[ANNAL.CURIE.url])

    def enum_fields(self):
        """
        Enumerate fields in entity.

        Recurses into fields that are lists or sequences of dictionaries,
        this being the structure used for repeated field groups.

        Yields `(path, value)` pairs, where `path` is a list of index values applied
        successively to access the corresponding value.
        """
        def is_dict(e):
            return isinstance(e,dict)
        def enum_f(p, d):
            for k in d:
                if isinstance(d[k], (list, tuple)) and all([is_dict(e) for e in d[k]]):
                    for i in range(len(d[k])):
                        for f in enum_f(p+[k,i], d[k][i]):
                            yield f
                else:
                    yield (p+[k], d[k])
            return
        if self._values:
            for f in enum_f([], self._values):
                yield f
        return

    def field_resource_file(self, resource_ref):
        """
        Returns a file object value for a resource associated with an entity,
        or None if the resouce is not present.
        """
        (body_dir, _) = self._dir_path()
        file_name = os.path.join(body_dir, resource_ref)
        if os.path.isfile(file_name):
            return open(file_name, "rb")
        return None

    def get_field(self, path):
        """
        Returns a field value corresponding to a path returned by enum_fields.
        """
        def get_f(p, v):
            if p == []:
                return v
            else:
                return get_f(p[1:], v[p[0]])
        return get_f(path, self._values)

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
        return (d, p, self._entityurl)

    def _alt_dir_path_uri(self):
        (d, p) = self._alt_dir_path()
        return (d, p, self._entityalturl)

    def _exists_path(self):
        """
        Test if the entity denoted by the current object has been created.

        If found, also sets the enity in-use URL value for .get_url()

        returns path of of object body, or None
        """
        for (d, p, u) in (self._dir_path_uri(), self._alt_dir_path_uri()):
            # log.info("_exists %s"%(p))
            if d and os.path.isdir(d):
                if p and os.path.isfile(p):
                    self._entityuseurl = u
                    return p
        return None

    def _exists(self):
        """
        Test if the entity denoted by the current object has been created.

        returns True or False.
        """
        return self._exists_path() is not None

    def _get_types(self, types):
        """
        Processes a supplied type value and returns a list of types to be stored.

        1. None is converted to an empty list
        2. A simple string is wrapped in a list
        3. A tuple is converted to a list
        4. If not already present, the current entity type is added to the list
        """
        if types is None:
            types = []
        elif isinstance(types, (tuple, list)):
            types = list(types)     # Make mutable copy
        else:
            types = [types]
        if self._entitytype not in types:
            types.append(self._entitytype)
        return types

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
        log.debug("EntityRoot._save: dir %s, file %s"%(body_dir, body_file))
        fullpath = os.path.join(settings.BASE_DATA_DIR, "annalist_site", body_file)
        # Next is partial protection against code errors
        if not fullpath.startswith(os.path.join(settings.BASE_DATA_DIR, "annalist_site")):
            raise ValueError("Attempt to create entity file outside Annalist site tree")
        # Create directory (if needed) and save data
        util.ensure_dir(body_dir)
        values = self._values.copy()
        values['@id']   = self._entityref
        values['@type'] = self._get_types(values.get('@type', None))
        # @TODO: is this next needed?  Put logic in set_values?
        if self._entityid:
            values[ANNAL.CURIE.id] = self._entityid
        values.pop(ANNAL.CURIE.url, None)
        with open(fullpath, "wt") as entity_io:
            json.dump(values, entity_io, indent=2, separators=(',', ': '))
        self._entityuseurl  = self._entityurl
        return

    def _load_values(self):
        """
        Read current entity from Annalist storage, and return entity body.

        Adds value for 'annal:url' to the entity data returned.
        """
        body_file = self._exists_path()
        if body_file:
            try:
                with open(body_file, "r") as f:
                    entitydata = json.load(util.strip_comments(f))
                    entitydata[ANNAL.CURIE.url] = self.get_view_url_path()
                    return entitydata
            except IOError, e:
                if e.errno != errno.ENOENT:
                    raise
                log.error("EntityRoot._load_values: no file %s"%(body_file))
            except ValueError, e:
                log.error("EntityRoot._load_values: error loading %s"%(body_file))
                log.error(e)
                return (
                    { "@error": body_file 
                    , "@message": "Error loading entity values %r"%(e,)
                    })
        return None

    def _migrate_values(self, entitydata):
        """
        Default method for entity format migration hook.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        This default implementation applies no migrations, and simply returns the 
        supplied value.  The method may be overridden for entity types and instances
        for which migrations are to be applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exctly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        return entitydata

    def _child_dirs(self, cls, altparent):
        """
        Returns a pair of directories that may contain child entities.
        The second of the pair is descended from the "altparent", which is 
        used only for entities that are not in the main directory.

        cls         is a subclass of Entity indicating the type of children to
                    be located
        altparent   is an alternative parent entity to be checked using the specified
                    class's alternate relative path, or None if only potential children 
                    of the current entity are returned.
        """
        dir1 = os.path.dirname(os.path.join(self._entitydir, cls._entitypath or ""))
        if altparent and cls._entityaltpath:
            dir2 = os.path.dirname(os.path.join(altparent._entitydir, cls._entityaltpath))
        else:
            dir2 = None
        return (dir1, dir2)

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
        coll_dir, site_dir = self._child_dirs(cls, altparent)
        assert "%" not in coll_dir, "_entitypath/_entityaltpath template variable interpolation may be in filename part only"
        site_files = []
        coll_files = []
        if site_dir and os.path.isdir(site_dir):
            site_files = os.listdir(site_dir)
        if os.path.isdir(coll_dir):
            coll_files = os.listdir(coll_dir)
        for fil in [ f for f in site_files if f not in coll_files] + coll_files:
            if util.valid_id(fil):
                yield fil
        return

    def _entity_files(self):
        """
        Iterates over files/resources (not subdirectories) that are part of the current entity.

        Returns pairs (p,f), where 'p' is a full path name, and 'f' is a filename within the 
        current entity directory. 
        """
        for f in os.listdir(self._entitydir):
            p = os.path.join(self._entitydir, f)
            if os.path.isfile(p):
                yield (p, f)
        return

    def _exists_file(self, f):
        """
        Test if a file named 'f' exists inthe current entity directory
        """
        return os.path.isfile(os.path.join(self._entitydir, f))

    def _copy_file(self, p, f):
        """
        Copy file with path 'p' to a new file 'f' in the current entity directory
        """
        new_p = os.path.join(self._entitydir, f)
        try:
            shutil.copy(p, new_p)
        except shutil.Error as e:
            log.error('shutil.copy error: %s' % e)
            return None
        except IOError as e:
            log.error('shutil.copy IOError: %s' % e.strerror)
            return None
        return new_p

    def _fileobj(self, localname, filetypeuri, mimetype, mode):
        """
        Returns a file object for accessing a blob associated with the current entity.

        localname   is the local name used to identify the file/resource among all those
                    associated with the ciurrent entity.
        filetypeuri is a URI/CURIE that identifies the type of data stored in the blob.
        mimetype    is a MIME content-type string for the resource representation used,
                    used in selecting the file extension to be used, or None in which case 
                    a default file extension for the type is used.
        mode        is a string defining how the resource is opened (using the same values
                    as the built-in `open` function).
        """
        (body_dir, body_file) = self._dir_path()  # Same as `_save`
        file_ext  = (
            file_extension_for_content_type(filetypeuri, mimetype) or 
            file_extension(filetypeuri)
            )
        file_name = os.path.join(body_dir, localname+"."+file_ext)
        return open(file_name, mode)

    # Special methods to facilitate access to entity values by dictionary operations
    # on the Entity object

    def __iter__(self):
        """
        Return entity value keys
        """
        if self._values:
            for k in self._values:
                yield k
        return

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
        # log.info("entityroot.get key %r, self._values %r"%(key, self._values))
        return self[key] if self._values and key in self._values else default

    def setdefault(self, key, default):
        """
        Equivalent to dict.setdefault() function, 
        except that blank values also are overridden
        """
        if self._values and key in self._values and self._values[key]:
            result = self._values[key]
        else:
            self._values[key] = default
            result = default
        return result

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
