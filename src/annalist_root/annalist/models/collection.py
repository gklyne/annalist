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
    _entitytypeid   = "_coll"
    _entityview     = layout.SITE_COLL_VIEW
    _entitypath     = layout.SITE_COLL_PATH
    _entityfile     = layout.COLL_META_REF
    _entityref      = layout.META_COLL_REF
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
        log.debug("Collection.__init__: coll_id %s, parent dir %s"%(coll_id, parentsite._entitydir))
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
        # log.info("Collection.set_alt_entities: parentids %r"%parentids)
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
        self[ANNAL.CURIE.inherit_from] = make_type_entity_id("_coll", altparent.get_id())
        return parents

    @classmethod
    def load(cls, parent, entityid, altscope=None):
        """
        Overload Entity.load with logic to set alternative parent details for 
        collection configuration inheritance, if an alternative is specified in 
        the collection data loaded.

        cls         is the Collection class of the entity to be loaded
        parent      is the parent from which the entity is descended.
        entityid    is the local identifier (slug) for the entity.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_entities` for more details.

        Returns an instance of the indicated Collection class with data loaded from 
        the corresponding Annalist storage, or None if there is no such entity.
        """
        log.debug("Collection.load: %s, altscope %s"%(entityid, altscope))
        coll = super(Collection, cls).load(parent, entityid, altscope=altscope)
        if coll is not None:
            parent_coll_id = extract_entity_id(coll.get(ANNAL.CURIE.inherit_from, None))
            if parent_coll_id and parent_coll_id != layout.SITEDATA_ID:
                parent_coll = super(Collection, cls).load(parent, parent_coll_id)
                if parent_coll is None:
                    log.warning(
                        "Collection.load: coll %s references non-existent parent %s"%
                        (entityid, parent_coll_id)
                        )
                else:
                    log.debug(
                        "Collection.load: coll %s references parent %s"%
                        (entityid, parent_coll_id)
                        )
                    coll.set_alt_entities(parent_coll)
            else:
                log.debug("Collection.load: coll %s references no parent"%(entityid,))
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
            , ANNAL.CURIE.user_permissions: user_permissions
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
            for f in [RDFS.CURIE.label, RDFS.CURIE.comment, ANNAL.CURIE.user_uri, ANNAL.CURIE.user_permissions]:
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
        self[ANNAL.CURIE.default_list] = list_id
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

    # JSON-LD context data

    def generate_coll_jsonld_context(self):
        """
        (Re)generate JSON-LD context description for the current collection.

        get_field_uri_context
                is a supplied function that accepts a RecordField object abnd
                returns a context dictionary for the field thus described.
        """
        # Build context data
        context      = self.get_coll_jsonld_context()
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        datetime_str = datetime_now.isoformat(' ')
        # Assemble and write out context description
        with self._metaobj(
                layout.COLL_META_CONTEXT_PATH,
                layout.COLL_CONTEXT_FILE,
                "wt"
                ) as context_io:
            json.dump(
                { "_comment": "Generated by generate_coll_jsonld_context on %s (for user data)"%datetime_str
                , "@context": context 
                }, 
                context_io, indent=2, separators=(',', ': ')
                )
        with self._metaobj(
                layout.SITEDATA_CONTEXT_PATH,
                layout.COLL_CONTEXT_FILE,
                "wt"
                ) as context_io:
            json.dump(
                { "_comment": "Generated by generate_coll_jsonld_context on %s (for collection data)"%datetime_str
                , "@context": context 
                }, 
                context_io, indent=2, separators=(',', ': ')
                )
        # @@TODO: fix ad-hocery used to ensure enum data can reference context in file system:
        with self._metaobj(
                layout.SITEDATA_ENUM_PATH,
                layout.COLL_CONTEXT_FILE,
                "wt"
                ) as context_io:
            json.dump(
                { "_comment": "Generated by generate_coll_jsonld_context on %s (for enums)"%datetime_str
                , "@context": context 
                }, 
                context_io, indent=2, separators=(',', ': ')
                )
        return

    def get_coll_jsonld_context(self):
        """
        Return dictionary containing context structure for collection.
        """
        # @@REVIEW: as a workaround for a problem with @base handling in rdflib-jsonld, don't
        #           include @base in context.
        #
        # context           = OrderedDict(
        #     { "@base":          self.get_url() + layout.COLL_CONTEXT_PATH
        #     , ANNAL.CURIE.type: { "@type": "@id" }
        #     })
        #
        # Use OrderedDict to allow some control over ordering of context file contents:
        # this is for humane purposes only, and is not technically important.
        context           = OrderedDict(
            { ANNAL.CURIE.type: { "@type": "@id" }
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
              { "@id": "annal:import_url"
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
                # fcontext['vid'] = v.get_id()
                # fcontext['fid'] = fid
                self.set_field_uri_jsonld_context(vuri or furi, fcontext, context)
        # Scan group fields and generate context data for property URIs used
        for g in self.child_entities(RecordGroup, altscope="all"):
            for gref in g[ANNAL.CURIE.group_fields]:
                fid  = extract_entity_id(gref[ANNAL.CURIE.field_id])
                guri = gref.get(ANNAL.CURIE.property_uri, None)
                furi, fcontext = self.get_field_uri_jsonld_context(fid, self.get_field_jsonld_context)
                # fcontext['gid'] = g.get_id()
                # fcontext['fid'] = fid
                self.set_field_uri_jsonld_context(guri or furi, fcontext, context)
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
        return (f[ANNAL.CURIE.property_uri], get_field_context(f))

    def set_field_uri_jsonld_context(self, puri, fcontext, property_contexts):
        """
        Save property context description into supplied property_contexts dictionary.  
        If the context is already defined, generate warning if there is a compatibility 
        problem.
        """
        if puri:
            uri_parts = puri.split(":")
            if len(uri_parts) > 1:
                # Ignore URIs without ':'
                if puri in property_contexts:
                    pcontext = property_contexts[puri]
                    if ( ( not fcontext ) or
                         ( pcontext.get("@type", None)      != fcontext.get("@type", None) ) or
                         ( pcontext.get("@container", None) != fcontext.get("@container", None) ) ):
                        log.warning(
                            "Incompatible use of property %s (%r, %r)"% (puri, fcontext, pcontext)
                            )
                elif ( fcontext and
                       ( uri_parts[0] in property_contexts ) or         # Prefix defined vocab?
                       ( uri_parts[0] in ["http", "https", "file"] ) ): # Full URI?
                    property_contexts[puri] = fcontext
        return

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
            fcontext = None # { "@type": "xsd:string" }
        elif is_render_type_id(rtype):
            fcontext = { "@type": "@id" }   # Add type from field descr?
        elif is_render_type_set(rtype):
            fcontext = { "@container": "@set"}
        elif is_render_type_list(rtype):
            fcontext = { "@container": "@list"}
        elif is_render_type_object(rtype):
            fcontext = None
        else:
            raise ValueError("Unexpected value mode or render type (%s, %s)"%(vmode, rtype))
        return fcontext

# End.
