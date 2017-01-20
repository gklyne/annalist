"""
Annalist collection

A collection is represented by:
- an ID (slug)
- a URI
- a name/label
- a description
- a set of record types
- a set of list views
- a set of record views
- ... and additional supporting metadata (fields, groups, user permissions, etc.)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil
import json
import datetime
from collections    import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                       import layout
from annalist                       import message
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.util                  import valid_id, extract_entity_id, make_type_entity_id

from annalist.models.entity         import Entity
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordvocab    import RecordVocab
from annalist.models.rendertypeinfo import (
    is_render_type_literal,
    is_render_type_id,
    is_render_type_set,
    is_render_type_list,
    is_render_type_object,
    )

class Collection(Entity):

    _entitytype     = ANNAL.CURIE.Collection
    _entitytypeid   = layout.COLL_TYPEID
    _entityview     = layout.SITE_COLL_VIEW
    _entitypath     = layout.SITE_COLL_PATH
    _entityfile     = layout.COLL_META_REF
    _entityref      = layout.META_COLL_REF
    _baseref        = layout.META_COLL_BASE_REF
    _contextref     = layout.COLL_CONTEXT_FILE

    def __init__(self, parentsite, coll_id, altparent=None):
        """
        Initialize a new Collection object.

        parentsite  is the parent site from which the new collection is descended.
        coll_id     the collection identifier for the collection
        altparent   is an alternative parent to search for descendents of the new 
                    Collection.  Effectively, the new Collection inherits definitions
                    from this alternative parent.
        """
        # log.debug("Collection.__init__: coll_id %s, parent dir %s"%(coll_id, parentsite._entitydir))
        if altparent is not None:
            if not isinstance(altparent, Collection):
                msg = "Collection altparent value must be a Collection (got %r)"%(altparent,)
                log.error(msg)
                raise ValueError(msg)
            # msg = (
            #     "Collection %s initialised with altparent %s"%
            #     (coll_id, altparent.get_id())
            #     )
            # raise ValueError(msg)
        self._parentsite = parentsite
        self._parentcoll = (
            altparent or
            None if coll_id == layout.SITEDATA_ID else 
            parentsite.site_data_collection()
            )
        super(Collection, self).__init__(parentsite, coll_id, altparent=self._parentcoll)
        self._types_by_id  = None
        self._types_by_uri = None
        return

    def _migrate_values(self, collmetadata):
        """
        Collection data format migration method.
        """
        migration_map = (
            [ (ANNAL.CURIE.comment,     ANNAL.CURIE.meta_comment    )
            ])
        collmetadata = self._migrate_values_map_field_names(migration_map, collmetadata)
        if collmetadata[ANNAL.CURIE.type_id] == "_collection":
            collmetadata[ANNAL.CURIE.type_id] = self._entitytypeid
        return collmetadata

    # Site

    def get_site(self):
        """
        Return site object for the site from which the current collection is accessed.
        """
        return self._parentsite

    def get_site_data(self):
        """
        Return parent object for accessing site data.
        """
        return self._parentcoll

    # Alternate collections handling

    def set_alt_entities(self, altparent):
        """
        Update the alternative parent for the current collection.

        Returns a list of parents accessible from the supplied altparent (including itself)
        """
        # log.info("Collection.set_alt_entities: coll_id %s, altparent_id %s"%(self.get_id(), altparent.get_id()))
        if not isinstance(altparent, Collection):
            msg = "Collection.set_alt_entities value must be a Collection (got %r)"%(altparent,)
            log.error(msg)
            raise ValueError(msg)
        parents   = super(Collection, self).set_alt_entities(altparent)
        parentids = [ p.get_id() for p in parents ]
        # log.info(
        #     "@@ Collection.set_alt_entities: coll: %r, parentids %r"%
        #     (self.get_id(), parentids)
        #     )
        if layout.SITEDATA_ID not in parentids:
            msg = (
                "Entity.set_alt_entities cannot access site data (%s) via %r)"%
                (layout.SITEDATA_ID, altparent)
                )
            log.error(msg)
            raise ValueError(msg)
        if not self._ensure_values_loaded():
            msg = (
                "Entity.set_alt_entities cannot load collection data for %s)"%
                (self.get_id(),)
                )
            log.error(msg)
            raise ValueError(msg)
        self[ANNAL.CURIE.inherit_from] = make_type_entity_id(layout.COLL_TYPEID, altparent.get_id())
        return parents

    @classmethod
    def create(cls, parent, coll_id, coll_meta):
        """
        Overload Entity.create with logic to set alternative parent details for 
        collection configuration inheritance, if an alternative is specified in 
        the collection data supplied.

        cls         is the Collection class object.
        parent      is the parent from which the collection is descended.
        coll_id     is the local identifier (slug) for the collection.
        coll_meta   is a dictionary of collection metadata values that are stored
                    for the created collection.

        Returns the created Collection instance.
        """
        # log.debug("Collection.create: %s, altscope %s"%(coll_id, altscope))
        coll = super(Collection, cls).create(parent, coll_id, coll_meta)
        if coll is not None:
            cls._set_alt_parent_coll(parent, coll)
        return coll

    @classmethod
    def _migrate_collection_config_dir(cls, parent, coll_id):
        # If old collection layout is present, migrate to new layout using "d/
        # Rename collection configuration directories and files individually so that 
        # existing data directories are not touched.
        parent_base_dir, parent_meta_file = parent._dir_path()
        coll_root_dir     = os.path.join(parent_base_dir, layout.SITE_COLL_PATH%{"id": coll_id})
        coll_base_dir     = os.path.join(coll_root_dir,   layout.COLL_BASE_DIR)
        coll_conf_old_dir = os.path.join(coll_root_dir,   layout.COLL_ROOT_CONF_OLD_DIR)
        # print("@@ Test migrate old configuration from %s"%(coll_conf_old_dir,))
        if os.path.isdir(coll_conf_old_dir):
            log.info("Migrate old configuration from %s"%(coll_conf_old_dir,))
            # print("@@ Migrate old configuration from %s"%(coll_conf_old_dir,))
            for old_name in os.listdir(coll_conf_old_dir):
                old_path = os.path.join(coll_conf_old_dir, old_name)
                if ( ( os.path.isdir(old_path) ) or
                     ( os.path.isfile(old_path) and old_path.endswith(".jsonld") )
                   ):
                    log.info("- %s -> %s"%(old_name, coll_base_dir))
                    new_path = os.path.join(coll_base_dir, old_name)
                    # print ("@@ rename %s -> %s"%(old_path, new_path))
                    try:
                        os.rename(old_path, new_path)
                    except Exception as e:
                        msg = message.COLL_MIGRATE_DIR_FAILED%(coll_id, old_path, new_path, e)
                        # print "@@ "+msg
                        log.error("Collection._migrate_collection_config_dir: "+msg)
                        assert False, msg
            # Rename old config dir to avoid triggering this logic again
            coll_conf_saved_dir = coll_conf_old_dir+".saved"
            try:
                os.rename(coll_conf_old_dir, coll_conf_saved_dir)
            except Exception as e:
                msg = message.COLL_MIGRATE_DIR_FAILED%(coll_id, coll_conf_old_dir, coll_conf_saved_dir, e)
                # print "@@ "+msg
                log.error("Collection._migrate_collection_config_dir: "+msg)
                assert False, msg
        return

    @classmethod
    def load(cls, parent, coll_id, altscope=None):
        """
        Overload Entity.load with logic to set alternative parent details for 
        collection configuration inheritance, if an alternative is specified in 
        the collection data loaded.

        cls         is the Collection class object.
        parent      is the parent from which the collection is descended.
        coll_id    is the local identifier (slug) for the collection.
        altscope    if supplied, indicates a scope other than the current collection
                    to search for children.

        Returns an instance of the indicated Collection class with data loaded from 
        the corresponding Annalist storage, or None if there is no such entity.
        """
        # log.debug("@@ Collection.load: %s, altscope %s"%(coll_id, altscope))
        cls._migrate_collection_config_dir(parent, coll_id)
        coll = super(Collection, cls).load(parent, coll_id, altscope=altscope)
        if coll is not None:
            cls._set_alt_parent_coll(parent, coll)
        return coll

    @classmethod
    def _set_alt_parent_coll(cls, parent, coll):
        """
        Set alternative parent collection - sets up search path for subsequent references.
        """
        coll_id        = coll.get_id()
        parent_coll_id = extract_entity_id(coll.get(ANNAL.CURIE.inherit_from, None))
        if parent_coll_id and parent_coll_id != layout.SITEDATA_ID:
            parent_coll = Collection.load(parent, parent_coll_id)
            if parent_coll is None:
                log.warning(
                    "Collection._set_alt_parent_coll: coll %s references non-existent parent %s"%
                    (coll_id, parent_coll_id)
                    )
            else:
                log.debug(
                    "Collection._set_alt_parent_coll: coll %s references parent %s"%
                    (coll_id, parent_coll_id)
                    )
                coll.set_alt_entities(parent_coll)
        return coll

    # User permissions

    def create_user_permissions(self, user_id, user_uri,
            user_name, user_description,
            user_permissions=["VIEW"]
            ):
        user_values = (
            { ANNAL.CURIE.type:             ANNAL.CURIE.User
            , RDFS.CURIE.label:             user_name
            , RDFS.CURIE.comment:           user_description
            , ANNAL.CURIE.user_uri:         user_uri
            , ANNAL.CURIE.user_permission:  user_permissions
            })
        user = AnnalistUser.create(self, user_id, user_values)
        return user

    def get_user_permissions(self, user_id, user_uri):
        """
        Get a user permissions record (AnnalistUser).

        To return a value, both the user_id and the user_uri (typically a mailto: URI, but
        may be any *authenticated* identifier) must match.  This is to prevent access to 
        records of a deleted account being granted to a new account created with the 
        same user_id (username).

        user_id         local identifier for the type to retrieve.
        user_uri        authenticated identifier associated with the user_id.  That is,
                        the authentication service used is presumed to confirm that
                        the identifier belongs to the user currently logged in with
                        the supplied username.

        returns an AnnalistUser object for the identified user, or None.  This object contains
                information about permissions granted to the user in the current collection.
        """
        user = AnnalistUser.load(self, user_id, altscope="user")
        # log.debug("Collection.get_user_permissions: user_id %s, user_uri %s, user %r"%
        #     (user_id, user_uri, user)
        #     )
        if user:
            for f in [RDFS.CURIE.label, RDFS.CURIE.comment, ANNAL.CURIE.user_uri, ANNAL.CURIE.user_permission]:
                if f not in user:
                    user = None
                    break
        if user and user[ANNAL.CURIE.user_uri] != user_uri:
            user = None         # URI mismatch: return None.
        return user

    # Record types

    def _update_type_cache(self, type_entity):
        """
        Add single type entity to type cache
        """
        if type_entity:
            self._types_by_id[type_entity.get_id()]   = type_entity
            self._types_by_uri[type_entity.get_uri()] = type_entity
        return

    def _flush_type(self, type_id):
        """
        Remove single identified type entity from type cache
        """
        if self._types_by_id:
            t = self._types_by_id.get(type_id, None)
            if t:
                type_uri = t.get_uri()
                self._types_by_id.pop(type_id, None)
                self._types_by_uri.pop(type_uri, None)
        return

    def _load_types(self):
        """
        Initialize cache of RecordType entities
        """
        if not (self._types_by_id and self._types_by_uri):
            self._types_by_id  = {}
            self._types_by_uri = {}
            for type_id in self._children(RecordType, altscope="all"):
                t = RecordType.load(self, type_id, altscope="all")
                self._update_type_cache(t)
        return

    def types(self, altscope="all"):
        """
        Generator enumerates and returns record types that may be stored
        """
        for f in self._children(RecordType, altscope=altscope):
            log.debug("___ Collection.types: "+f)
            t = self.get_type(f)
            if t and t.get_id() != "_initial_values":
                yield t
        return

    def add_type(self, type_id, type_meta):
        """
        Add a new record type to the current collection

        type_id     identifier for the new type, as a string
                    with a form that is valid as URI path segment.
        type_meta   a dictionary providing additional information about
                    the type to be created.

        Returns a RecordType object for the newly created type.
        """
        t = RecordType.create(self, type_id, type_meta)
        if self._types_by_id:
            self._update_type_cache(t)
        return t

    def get_type(self, type_id):
        """
        Retrieve identified type description

        type_id     local identifier for the type to retrieve.

        returns a RecordType object for the identified type, or None.
        """
        if not valid_id(type_id):
            raise ValueError("Collection %s get_type(%s) invalid id"%(self.get_id(), type_id))
        self._load_types()
        t = self._types_by_id.get(type_id, None)
        # Was it created but not cached?
        if not t and RecordType.exists(self, type_id, altscope="all"):
            log.info("___ Collection.get_type: "+type_id)
            t = RecordType.load(self, type_id, altscope="all")
            self._update_type_cache(t)
        return t

    def get_uri_type(self, type_uri):
        """
        Return type entity corresponding to the supplied type URI
        """
        self._load_types()
        t = self._types_by_uri.get(type_uri, None)
        return t

    def remove_type(self, type_id):
        """
        Remove identified type description

        type_id     local identifier for the type to remove.

        Returns a non-False status code if the type is not removed.
        """
        self._flush_type(type_id)
        s = RecordType.remove(self, type_id)
        return s

    def update_entity_types(self, e):
        """
        Updates the list of type URIs associated with an entity by accessing the
        supertypes of the associated type record.
        """
        type_uri = e.get(ANNAL.CURIE.type, None)
        sts = [type_uri]
        t   = self.get_uri_type(type_uri)
        if t:
            assert (t.get_uri() == type_uri), "@@ type %s has unexpected URI"%(type_uri,)
            for st in t.get(ANNAL.CURIE.supertype_uri, []):
                if isinstance(st, dict):
                    st = st['@id']
                if st not in sts:
                    sts.append(st)
        # log.info("@@ update_entity_types %r"%(sts,))
        e['@type'] = sts
        return

    # Record views

    def views(self, altscope="all"):
        """
        Generator enumerates and returns record views that may be stored
        """
        for f in self._children(RecordView, altscope=altscope):
            v = self.get_view(f)
            if v and v.get_id() != "_initial_values":
                yield v
        return

    def add_view(self, view_id, view_meta):
        """
        Add a new record view to the current collection

        view_id     identifier for the new view, as a string
                    with a form that is valid as URI path segment.
        view_meta   a dictionary providing additional information about
                    the view to be created.

        returns a RecordView object for the newly created view.
        """
        v = RecordView.create(self, view_id, view_meta)
        return v

    def get_view(self, view_id):
        """
        Retrieve identified view description

        view_id     local identifier for the view to retrieve.

        returns a RecordView object for the identified view, or None.
        """
        v = RecordView.load(self, view_id, altscope="all")
        return v

    def remove_view(self, view_id):
        """
        Remove identified view description

        view_id     local identifier for the view to remove.

        Returns a non-False status code if the view is not removed.
        """
        s = RecordView.remove(self, view_id)
        return s

    # Record lists

    def lists(self, altscope="all"):
        """
        Generator enumerates and returns record lists that may be stored
        """
        for f in self._children(RecordList, altscope=altscope):
            l = self.get_list(f)
            if l and l.get_id() != "_initial_values":
                yield l
        return

    def add_list(self, list_id, list_meta):
        """
        Add a new record list to the current collection

        list_id     identifier for the new list, as a string
                    with a form that is valid as URI path segment.
        list_meta   a dictionary providing additional information about
                    the list to be created.

        returns a RecordList object for the newly created list.
        """
        l = RecordList.create(self, list_id, list_meta)
        return l

    def get_list(self, list_id):
        """
        Retrieve identified list description

        list_id     local identifier for the list to retrieve.

        returns a RecordList object for the identified list, or None.
        """
        l = RecordList.load(self, list_id, altscope="all")
        return l

    def remove_list(self, list_id):
        """
        Remove identified list description

        list_id     local identifier for the list to remove.

        Returns a non-False status code if the list is not removed.
        """
        s = RecordList.remove(self, list_id)
        return s

    def set_default_list(self, list_id):
        """
        Set and save the default list to be displayed for the current collection.
        """
        self[ANNAL.CURIE.default_list]        = list_id
        self[ANNAL.CURIE.default_view_id]     = None
        self[ANNAL.CURIE.default_view_type]   = None
        self[ANNAL.CURIE.default_view_entity] = None
        self._save()
        return

    def get_default_list(self):
        """
        Return the default list to be displayed for the current collection.
        """
        list_id = self.get(ANNAL.CURIE.default_list, None)
        # print "@@ get_default_list %s"%list_id
        if list_id and not RecordList.exists(self, list_id, altscope="all"):
            log.warning(
                "Default list %s for collection %s does not exist"%
                (list_id, self.get_id())
                )
            list_id = None
        return list_id 

    def set_default_view(self, view_id, type_id, entity_id):
        """
        Set and save the default list to be displayed for the current collection.
        """
        self[ANNAL.CURIE.default_view_id]     = view_id
        self[ANNAL.CURIE.default_view_type]   = type_id
        self[ANNAL.CURIE.default_view_entity] = entity_id
        self._save()
        return

    def get_default_view(self):
        """
        Return the default view id, type and entity to be displayed for the current collection.
        """
        view_id   = self.get(ANNAL.CURIE.default_view_id,     None)
        type_id   = self.get(ANNAL.CURIE.default_view_type,   None)
        entity_id = self.get(ANNAL.CURIE.default_view_entity, None)
        log.info("Collection.get_default_view: %s/%s/%s"%(view_id, type_id, entity_id))
        return (view_id, type_id, entity_id) 

    # JSON-LD context data

    def generate_coll_jsonld_context(self, flags=None):
        """
        (Re)generate JSON-LD context description for the current collection.

        Returns list of errors, or empty list.
        """
        errs = []
        if flags and ("nocontext" in flags):
            # Skip processing if "nocontext" flag provided
            return
        log.info("Generating context for collection %s"%(self.get_id()))
        # Build context data
        context      = self.get_coll_jsonld_context()
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        datetime_str = datetime_now.isoformat(' ')
        # Assemble and write out context description
        with self._metaobj(
                layout.META_COLL_BASE_REF,
                layout.COLL_CONTEXT_FILE,
                "wt"
                ) as context_io:
            json.dump(
                { "_comment": "Generated by generate_coll_jsonld_context on %s"%datetime_str
                , "@context": context 
                }, 
                context_io, indent=2, separators=(',', ': '), sort_keys=True
                )
        return errs

    def get_coll_jsonld_context(self):
        """
        Return dictionary containing context structure for collection.

        Entry '@errs' is set to a list of errors encountered, or an empty list.
        """
        # Use OrderedDict to allow some control over ordering of context file contents:
        # this is for humane purposes only, and is not technically critical.
        errs              = []
        context           = OrderedDict(
            { "@base":                  self.get_url() + layout.META_COLL_BASE_REF
            , ANNAL.CURIE.type:         { "@type":      "@id"   }
            , ANNAL.CURIE.entity_list:  { "@container": "@list" }
            })
        # Collection-local URI prefix
        context.update(
            { 'coll':           self._entityviewurl
            })
        # Common import/upload fields
        context.update(
            { 'resource_name': "annal:resource_name"
            , 'resource_type': "annal:resource_type"
            })
        # upload-file fields
        context.update(
            { 'upload_name':   "annal:upload_name"
            , 'uploaded_file': "annal:uploaded_file"
            , 'uploaded_size': "annal:uploaded_size"
            })
        # import-resource fields
        context.update(
            { 'import_name':   "annal:import_name"
            , 'import_url':    
              { "@id":   "annal:import_url"
              , "@type": "@id"
              }
            })
        # Scan vocabs, generate prefix data
        for v in self.child_entities(RecordVocab, altscope="all"):
            vid = v.get_id()
            if vid != "_initial_values":
                context[v.get_id()] = v[ANNAL.CURIE.uri]
        # Scan view fields and generate context data for property URIs used
        for v in self.child_entities(RecordView, altscope="all"):
            for fref in v[ANNAL.CURIE.view_fields]:
                fid  = extract_entity_id(fref[ANNAL.CURIE.field_id])
                vuri = fref.get(ANNAL.CURIE.property_uri, None)
                furi, fcontext = self.get_field_uri_jsonld_context(fid, self.get_field_jsonld_context)
                if fcontext is not None:
                    fcontext['vid'] = v.get_id()
                    fcontext['fid'] = fid
                e = self.set_field_uri_jsonld_context(vuri or furi, fid, fcontext, context)
                errs.extend(e)
        # Scan group fields and generate context data for property URIs used
        for g in self.child_entities(RecordGroup, altscope="all"):
            for gref in g[ANNAL.CURIE.group_fields]:
                fid  = extract_entity_id(gref[ANNAL.CURIE.field_id])
                guri = gref.get(ANNAL.CURIE.property_uri, None)
                furi, fcontext = self.get_field_uri_jsonld_context(fid, self.get_field_jsonld_context)
                if fcontext is not None:
                    fcontext['gid'] = g.get_id()
                    fcontext['fid'] = fid
                e = self.set_field_uri_jsonld_context(guri or furi, fid, fcontext, context)
                errs.extend(e)
        if errs:
            context['@errs'] = errs
        return context

    def get_field_uri_jsonld_context(self, fid, get_field_context):
        """
        Access field description, and return field property URI and appropriate 
        property description for JSON-LD context.

        If there is no corresponding field description, returns (None, None)

        If no context should be generated for the field URI, returns (uri, None)
        """
        f = RecordField.load(self, fid, altscope="all")
        if f is None:
            return (None, None)
        # @@debugging@@
        # if fid in ["Entity_id", "List_id"]:
        #     print "@@ %s field   %r"%(fid, f)
        #     print "@@ %s context %r"%(fid, get_field_context(f))
        return (f[ANNAL.CURIE.property_uri], get_field_context(f))

    def set_field_uri_jsonld_context(self, puri, field_id, fcontext, property_contexts):
        """
        Save property context description into supplied property_contexts dictionary.  
        If the context is already defined, generate warning if there is a compatibility 
        problem.

        Returns list of errors, or empty list.
        """
        errs = []
        if puri:
            uri_parts = puri.split(":")
            if len(uri_parts) > 1:    # Ignore URIs without ':'
                if not fcontext:
                    # For diagnostics to locate incompatible use...
                    fcontext = {'fid': field_id}
                if puri in property_contexts:
                    pcontext    = property_contexts[puri]
                    p_type      = pcontext.get("@type", None)
                    p_container = pcontext.get("@container", None)
                    f_type      = fcontext.get("@type", None)
                    f_container = fcontext.get("@container", None)
                    if ( ( p_type      != f_type      ) or
                         ( p_container != f_container ) ):
                        msg  = "Incompatible use of property %s in field %s (new %r; was %r)"% (puri, field_id, fcontext, pcontext)
                        # msgp = "pcontext @type %s, @container %s"%(p_type, p_container)
                        # msgf = "fcontext @type %s, @container %s"%(f_type, f_container)
                        log.warning(msg)
                        # print "@@ "+msg
                        # print "@@ pcontext @type %s, @container %s"%(p_type, p_container)
                        # print "@@ fcontext @type %s, @container %s"%(f_type, f_container)
                        property_contexts[puri]['err'] = msg
                        errs.append(msg)
                        # errs.append(msgp)
                        # errs.append(msgf)
                elif ( fcontext and
                       ( uri_parts[0] in property_contexts ) or         # Prefix defined vocab?
                       ( uri_parts[0] in ["http", "https", "file"] ) ): # Full URI?
                    property_contexts[puri] = fcontext
                    # msg = "Save context info for %s in field %s (new %r)"% (puri, field_id, fcontext)
                    # print "@@ "+msg
        return errs

    # @@TODO: move this away from model logic, as it represents a dependency on view logic?
    @staticmethod
    def get_field_jsonld_context(fdesc):
        """
        Returns a context description for the supplied field description.

        Returns None if no property context information is needed for the 
        supplied field.
        """
        rtype = extract_entity_id(fdesc[ANNAL.CURIE.field_render_type])
        vmode = extract_entity_id(fdesc[ANNAL.CURIE.field_value_mode])
        if vmode in ["Value_entity", "Value_field"]:
            rtype = "Enum"
        elif vmode == "Value_import":
            rtype = "URIImport"
        elif vmode == "Value_upload":
            rtype = "FileUpload"

        if is_render_type_literal(rtype):
            fcontext = {} # { "@type": "xsd:string" }
        elif is_render_type_id(rtype):
            fcontext = { "@type": "@id" }   # Add type from field descr?
        elif is_render_type_object(rtype):
            fcontext = {}
        else:
            raise ValueError("Unexpected value mode or render type (%s, %s)"%(vmode, rtype))

        if is_render_type_set(rtype):
            fcontext["@container"] = "@set"
        elif is_render_type_list(rtype):
            fcontext["@container"] = "@list"

        return fcontext

# End.
