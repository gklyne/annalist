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

from annalist               import layout
from annalist               import util
from annalist.exceptions    import Annalist_Error
from annalist.identifiers   import ANNAL, RDF, RDFS
from annalist.resourcetypes import file_extension, file_extension_for_content_type
from annalist.util          import make_type_entity_id, make_entity_base_url

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
        cls._contextref     relative reference to context from body file
        self._entityid      ID of entity; may be None for "root" entities (e.g. site?)
        self._entityurl     URI at which entity is accessed
        self._entitydir     directory where entity is stored
        self._entitybasedir base directory where all data is stored
        self._values        dictionary of values in entity body
    """

    _entitytype     = ANNAL.CURIE.EntityRoot
    _entitytypeid   = None          # To be overridden
    _entityfile     = None          # To be overriden by entity subclasses..
    _entityref      = None          # Relative ref to entity from body file
    _baseref        = None          # Relative ref to collection base URI from body file
    _contextref     = None          # Relative ref to context file from body file

    def __init__(self, entityurl, entityviewurl, entitydir, entitybasedir):
        """
        Initialize a new Entity object, possibly without values.  The created
        entity is not saved to disk at this stage - see .save() method.

        entityurl       is the base URI at which the entity is accessed
        entityviewurl   is a URI reference that indicates the preferred URI path
                        for accessing the current entity, where this may be the same
        entitydir       is the base directory containing the entity
        entitybasedir   is a directory that contains all data, directly or indirectly,
                        associated with this entity or any possible descendents.  The
                        value is used as a safety check to ensure that data is not 
                        created or deleted outside an area that is known to contain 
                        only annalist data.
        """
        self._entityid      = None
        self._entityurl     = make_entity_base_url(entityurl)
        self._entityviewurl = make_entity_base_url(entityviewurl)
        self._entitydir     = make_entity_base_url(entitydir)
        self._entitybasedir = entitybasedir
        self._values        = None
        # log.debug("EntityRoot.__init__: entity URI %s, entity dir %s"%(self._entityurl, self._entitydir))
        return

    def __repr__(self):
        return (
            "EntityRoot: entitytypeid %s, entityid %s, entitydir %s, values %r"%
            (self._entitytypeid, self._entityid, self._entitydir, self._values)
            )

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
        # log.debug("EntityRoot.get_url: baseurl %s, _entityurl %s"%(baseurl, self._entityurl))
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
        # log.debug("EntityRoot.get_view_url: baseurl %s, _entityurl %s"%(baseurl, self._entityurl))
        return urlparse.urljoin(baseurl, self._entityviewurl)

    def get_view_url_path(self, baseurl=""):
        """
        Return URL path used to view entity data.  This is the URI-path of the URL
        returned by get_view_url (above)
        """
        # log.debug("EntityRoot.get_view_url_path: baseurl %s, _entityurl %s"%(baseurl, self._entityurl))
        return util.entity_url_path(self.get_view_url(), "")

    def get_alt_entities(self, altscope=None):
        """
        Returns a list of alternative entities to the current entity to search for possible 
        child entities.  The root entity has no such alternatives.
        """
        return []

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

    def resource_file(self, resource_ref):
        """
        Returns a file object value for a resource associated with an entity,
        or None if the resource is not present.
        """
        if self._exists_path():
            # (body_dir, _) = self._dir_path()
            body_dir = self._entitydir
            log.debug("EntityRoot.resource_file: dir %s, resource_ref %s"%(body_dir, resource_ref))
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

    def child_entity_ids(self, cls, altscope=None):
        """
        Iterates over child entity identifiers of an indicated class.
        The supplied class is used to determine a subdirectory to be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_entities` for more details.
        """
        if altscope == "select":
            altscope = "all"
        for i in self._children(cls, altscope=altscope):
            if cls.exists(self, i, altscope=altscope):
                yield i
        return

    # I/O helper functions

    def _dir_path(self):
        """
        Return directory and path for current entity body file
        """
        if not self._entityfile:
            raise ValueError("Entity._dir_path without defined entity file path")
        # log.info("    _ EntityRoot._dir_path _entitydir  %s"%(self._entitydir,))
        # log.info("    _ EntityRoot._dir_path _entityfile %s"%(self._entityfile,))
        (basedir, filepath) = util.entity_dir_path(self._entitydir, [], self._entityfile)
        return (basedir, filepath)

    def _dir_path_uri(self):
        (d, p) = self._dir_path()
        return (d, p, self._entityurl)

    def _exists_path(self):
        """
        Test if the entity denoted by the current object has been created.

        If found, also sets the entity in-use URL value for .get_url()

        returns path of of object body, or None
        """
        (d, p, u) = self._dir_path_uri()
        # log.debug("EntityRoot._exists_path %s"%(p))
        if d and os.path.isdir(d):
            if p and os.path.isfile(p):
                # log.debug("EntityRoot._exists_path %s: OK"%(p))
                return p
            mp = self._migrate_path()
            if mp and os.path.isfile(mp):
                assert mp == p, "EntityRoot._exists_path: Migrated filename %s, expected %s"%(mp, p)
                # log.info("EntityRoot._exists_path %s: Migrated from %s"%(mp, p))
                return mp
        # log.debug("EntityRoot._exists_path %s: not present"%(p))
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

    def _save(self, post_update_flags=None):
        """
        Save current entity to Annalist storage
        """
        # @@TODO: think about capturing provenance metadata too.
        if not self._entityref:
            raise ValueError("Entity._save without defined entity reference")
        if not self._contextref:
            raise ValueError("Entity._save without defined context reference")
        if not self._values:
            raise ValueError("Entity._save without defined entity values")
        (body_dir, body_file) = self._dir_path()
        # log.debug("EntityRoot._save: dir %s, file %s"%(body_dir, body_file))
        fullpath = os.path.join(settings.BASE_DATA_DIR, "annalist_site", body_file)
        # Next is partial protection against code errors
        if not fullpath.startswith(os.path.join(settings.BASE_DATA_DIR, "annalist_site")):
            log.error("EntityRoot._save: Failing to create entity at %s"%(fullpath,))
            log.info("EntityRoot._save: dir %s, file %s"%(body_dir, body_file))
            log.info("EntityRoot._save: settings.BASE_DATA_DIR %s"%(settings.BASE_DATA_DIR,))
            raise ValueError(
                "Attempt to create entity file outside Annalist site tree (%s)"%
                fullpath
                )
        # Create directory (if needed) and save data
        util.ensure_dir(body_dir)
        values = self._values.copy()
        values['@id']      = self._entityref
        values['@type']    = self._get_types(values.get('@type', None))
        values['@context'] = (
            [ { '@base': self._baseref }
            , self._contextref
            # layout.COLL_CONTEXT_FILE
            # layout.ENTITY_CONTEXT_PATH + "/" + layout.COLL_CONTEXT_FILE
            ])
        # @TODO: is this next needed?  Put logic in set_values?
        if self._entityid:
            values[ANNAL.CURIE.id] = self._entityid
        values.pop(ANNAL.CURIE.url, None)
        with open(fullpath, "wt") as entity_io:
            json.dump(values, entity_io, indent=2, separators=(',', ': '), sort_keys=True)
        self._post_update_processing(values, post_update_flags)
        return

    def _remove(self, type_uri):
        """
        Remove current entity from Annalist storage.  Requires typ_uri supplied as a 
        double-check that the expected enytity is being removed.
        """
        d = self._entitydir
        # Extra check to guard against accidentally deleting wrong thing
        if type_uri in self._values['@type'] and d.startswith(self._entitybasedir):
            shutil.rmtree(d)
        else:
            log.error("Expected type_uri: %r, got %r"%(type_uri, e[ANNAL.CURIE.type]))
            log.error("Expected dirbase:  %r, got %r"%(parent._entitydir, d))
            raise Annalist_Error("Entity %s unexpected type %s or path %s"%(entityid, e[ANNAL.CURIE.type_id], d))
        return

    def _load_values(self):
        """
        Read current entity from Annalist storage, and return entity body.

        Adds value for 'annal:url' to the entity data returned.
        """
        # log.debug("EntityRoot._load_values %s/%s"%(self.get_type_id(), self.get_id()))
        body_file = self._exists_path()
        if body_file:
            # log.debug("EntityRoot._load_values body_file %r"%(body_file,))
            try:
                # @@TODO: rework name access to support different underlays
                with self._read_stream() as f:
                    entitydata = json.load(util.strip_comments(f))
                    # log.debug("EntityRoot._load_values: url_path %s"%(self.get_view_url_path()))
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

    def _ensure_values_loaded(self):
        """
        If values are not loaded and present for the current entity, read and store them.

        Returns the values loaded, or None.
        """
        if self._values is None:
            vals = self._load_values()
            if vals:
                vals = self._migrate_values(vals)
                self.set_values(vals)
        return self._values

    def _migrate_path(self):
        """
        Migrate entity data filenames from those used in older software versions.

        Returns name of migrated file if migration performed, otherwise None
        """
        # log.debug("EntityRoot._migrate_path (%r)"%(self._migrate_filenames(),))
        if self._migrate_filenames() is None:
            # log.debug("EntityRoot._migrate_path (skip)")
            return
        for old_data_filename in self._migrate_filenames():
            # This logic migrates data from previous filenames
            (basedir, old_data_filepath) = util.entity_dir_path(self._entitydir, [], old_data_filename)
            if basedir and os.path.isdir(basedir):
                if old_data_filepath and os.path.isfile(old_data_filepath):
                    # Old body file found here
                    (d, new_data_filepath) = self._dir_path()
                    log.info(
                        "EntityRoot._migrate_path: Migrate file %s to %s"%
                        (old_data_filepath, new_data_filepath)
                        )
                    os.rename(old_data_filepath, new_data_filepath)
                    return new_data_filepath
        # log.debug("EntityRoot._migrate_path (not found)")
        return None

    def _migrate_filenames(self):
        """
        Default method for filename migration.

        Returns a list of filenames used for the current entity type in previous
        versions of Annalist software.  If the expected filename is not found when 
        attempting to read a file, the _load_values() method calls this function to
        and looks for any of the filenames returned.  If found, the file is renamed
        to the current version filename.

        Default method returns None, which signals that no migration is to be performed.
        """
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

    def _migrate_values_map_field_names(self, migration_map, entitydata):
        """
        Support function to map field names using a supplied map.

        The map is a list of pairs (old_uri, new_uri), where occurrences of the 
        old property URI are replaced with the same value using the new URI.

        The migrations are applied in-place, and the resulting updated entity 
        data is returned.
        """
        for old_key, new_key in migration_map:
            if old_key in entitydata:
                entitydata[new_key] = entitydata.pop(old_key)
        # Return result
        return entitydata

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Default method for post-update processing.

        This method is called when an entity has been updated.  

        Individual entity classes may provide their own override methods for this.  
        (e.g. to trigger regeneration of context data when groups, views, fields or 
        vocabulary descriptions are updated.)
        """
        return entitydata

    def _base_children(self, cls):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        """
        parent_dir = os.path.dirname(os.path.join(self._entitydir, cls._entitypath or ""))
        assert "%" not in parent_dir, "_entitypath template variable interpolation may be in filename part only"
        child_files = []
        if os.path.isdir(parent_dir):
            child_files = os.listdir(parent_dir)
        for fil in child_files:
            if util.valid_id(fil):
                yield fil
        return

    def _children(self, cls, altscope=None):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied value is not "all" or "site", returns empty iterator,
                    otherwise an iterator over child entities.

        NOTE: `Site` class overrides this.
        """
        # log.info("@@ EntityRoot._children: parent %s, altscope %s"%(self.get_id(), altscope))
        if altscope != "site":
            return self._base_children(cls)
        return iter(())     # Empty iterator

    def _entity_files(self):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entitytypeinfo'
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

    def _copy_entity_files(self, src_entity):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entityedit', 'am_managecollections'
        """
        Copy metadata abnd attached resources from the supplied `src_entity` 
        to the current entity.

        Resources that already exist for the current entty are not copied.

        returns     list of error messages; an empty list indicates success.
        """
        msgs = []
        for p, f in src_entity._entity_files():
            if not self._exists_file(f):
                p_new = self._copy_file(p, f)
                if not p_new:
                    msg_vals = (
                        { 'id':     self.get_id()
                        , 'src_id': src_entity.get_id()
                        , 'file':   f
                        })
                    log.warning(
                        "EntityRoot._copy_entity_files: error copying file %(file)s from %(src_id)s to %(id)s"%
                        msg_vals
                        )
                    msgs.APPEND(message.ENTITY_COPY_FILE_ERROR%msg_vals)
        return msgs

    def _unused_entity_files_dirs(self):
        #@@TODO: abstract logic to work with non-file storage
        """
        Iterates over files/resources that are part of the current entity.

        Returns pairs (p,f), where 'p' is a full path name, and 'f' is a filename within the 
        current entity directory. 
        """
        for f in os.listdir(self._entitydir):
            p = os.path.join(self._entitydir, f)
            if os.path.exists(p):
                yield (p, f)
        return

    def _exists_file(self, f):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entitytypeinfo'
        """
        Test if a file named 'f' exists in the current entity directory
        """
        return os.path.isfile(os.path.join(self._entitydir, f))

    def _copy_file(self, p, f):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entitytypeinfo'
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

    def _rename_files(self, old_entity):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entitytypeinfo'
        """
        Rename old entity files to path of current entity (which must not exist),
        and return path to resulting entity, otherwise None.
        """
        new_p = None
        if os.path.exists(self._entitydir):
            log.error("EntityRoot._rename_files: destination %s already exists"%(self._entitydir,))
        elif not self._entitydir.startswith(self._entitybasedir):
            log.error(
                "EntityRoot._rename_files: new expected dirbase:  %r, got %r"%
                (self._entitybasedir, self._entitydir)
                )
        elif not old_entity._entitydir.startswith(self._entitybasedir):
            log.error(
                "EntityRoot._rename_files: old expected dirbase:  %r, got %r"%
                (self._entitybasedir, old_entity._entitydir)
                )
        else:
            try:
                os.rename(old_entity._entitydir, self._entitydir)
                new_p = self._entitydir
            except IOError as e:
                log.error("EntityRoot._rename_files: os.rename IOError: %s" % e.strerror)
        return new_p

    def _fileobj(self, localname, filetypeuri, mimetype, mode):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'entity', 'entitytypeinfo', 'site', 'entityedit', 'util',
        #                'test_import_resource', 'test_render_ref_multifields', 'test_upload_file'
        """
        Returns a file object for accessing a blob associated with the current entity.

        localname   is the local name used to identify the file/resource among all those
                    associated with the current entity.
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

    def _metaobj(self, localpath, localname, mode):
        #@@TODO: abstract logic to work with non-file storage
        #        Used by 'collection', 'site'
        """
        Returns a file object for accessing a metadata resource associated with 
        the current entity.

        localpath   is the local directory path (relative to the current entity's data)
                    where the metadata resource will be accessed.
        localname   is the local name used to identify the file/resource among all those
                    associated with the current entity.
        mode        is a string defining how the resource is opened (using the same values
                    as the built-in `open` function).
        """
        (body_dir, body_file) = self._dir_path()  # Same as `_save`
        local_dir = os.path.join(body_dir, localpath)
        util.ensure_dir(local_dir)
        filename = os.path.join(local_dir, localname)
        # log.debug("entityroot._metaobj: self._entitydir %s"%(self._entitydir,))
        # log.debug("entityroot._metaobj: body_dir %s, body_file %s"%(body_dir, body_file))
        # log.debug("entityroot._metaobj: filename %s"%(filename,))
        return open(filename, mode)

    def _read_stream(self):
        """
        Opens a (file-like) stream to read entity data.

        Returns the stream object, which implements the context protocol to
        close the stream on exit from a containign with block; e.g.

            with e._read_stream() as f:
                // read data from f
            // f is closed here

        """
        # @@TODO: factor out logic in common with _metaobj/_fileobj
        f_stream  = None
        body_file = self._exists_path()
        if body_file:
            try:
                f_stream = open(body_file, "rt")
            except IOError, e:
                if e.errno != errno.ENOENT:
                    raise
                log.error("EntityRoot._read_stream: no file %s"%(body_file))
        return f_stream

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
