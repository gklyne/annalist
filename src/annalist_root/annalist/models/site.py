"""
Analist site-related facilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import collections
import urlparse
import json
from collections    import OrderedDict

import traceback
import logging
log = logging.getLogger(__name__)

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.conf                    import settings
from django.core.urlresolvers       import resolve, reverse

import annalist
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.exceptions            import Annalist_Error, EntityNotFound_Error
from annalist.util                  import valid_id, extract_entity_id
from annalist                       import layout
from annalist                       import message

from annalist.models.annalistuser   import AnnalistUser
from annalist.models.entityroot     import EntityRoot
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordvocab    import RecordVocab
from annalist.models.recordview     import RecordView
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordfield    import RecordField
from annalist.models.rendertypeinfo import (
    is_render_type_literal,
    is_render_type_id,
    is_render_type_set,
    is_render_type_list,
    is_render_type_object,
    )

class Site(EntityRoot):

    _entitytype     = ANNAL.CURIE.Site
    _entitytypeid   = "_site"
    _entityfile     = layout.SITEDATA_META_FILE
    _entityref      = layout.META_SITE_REF

    def __init__(self, sitebaseuri, sitebasedir, host=""):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base directory for site information
        """
        log.debug("Site init: %s"%(sitebasedir))
        super(Site, self).__init__(host+sitebaseuri, sitebasedir)
        self._sitedata = SiteData(self)
        return

    def get_user_permissions(self, user_id, user_uri):
        """
        Get a site-wide user permissions record (AnnalistUser).

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
        user = AnnalistUser.load(self, user_id, use_altpath=True)
        log.debug(
            "Site.get_user_permissions: user_id %s, user_uri %s, user %r"%
            (user_id, user_uri, user)
            )
        if user:
            for f in [RDFS.CURIE.label, RDFS.CURIE.comment, ANNAL.CURIE.user_uri, ANNAL.CURIE.user_permissions]:
                if f not in user:
                    user = None
                    break
        if user and user[ANNAL.CURIE.user_uri] != user_uri:
            user = None         # URI mismatch: return None.
        return user

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        Yielded values are collection objects.
        """
        log.debug("site.collections: basedir: %s"%(self._entitydir))
        for f in self._children(Collection):
            c = Collection.load(self, f)
            # log.info("Site.colections: Collection.load %s %r"%(f, c.get_values()))
            if c:
                yield c
        return

    def collections_dict(self):
        """
        Return an ordered dictionary of collection URIs indexed by collection id
        """
        coll = [ (c.get_id(), c) for c in self.collections() ]
        return collections.OrderedDict(sorted(coll))

    def site_data(self):
        """
        Return dictionary of site data
        """
        # @@TODO: consider using generic view logic for this mapping (and elsewhere?)
        #         This is currently a bit of a kludge, designed to match the site
        #         view template.  In due course, it may be reviewed and implemented
        #         using the generic Annalist form generating framework
        site_data = self._load_values()
        if not site_data:
            return None
        site_data["title"] = site_data.get(RDFS.CURIE.label, message.SITE_NAME_DEFAULT)
        # log.info("site.site_data: site_data %r"%(site_data))
        colls = collections.OrderedDict()
        for k, v in self.collections_dict().items():
            # log.info("site.site_data: colls[%s] %r"%(k, v))
            colls[k] = dict(v.items(), id=k, url=v[ANNAL.CURIE.url], title=v[RDFS.CURIE.label])
        site_data["collections"] = colls
        return site_data

    def add_collection(self, coll_id, coll_meta, annal_ver=annalist.__version_data__):
        """
        Add a new collection to the current site

        coll_id     identifier for the new collection, as a string
                    with a form that is valid as URI path segment.
        coll_meta   a dictionary providing additional information about
                    the collection to be created.
        annal_ver   Override annalist version stored in collection metadata
                    (parameter provided for testing)

        returns a Collection object for the newly created collection.
        """
        d = dict(coll_meta)
        d[ANNAL.CURIE.software_version] = annal_ver
        c = Collection.create(self, coll_id, d)
        return c

    def remove_collection(self, coll_id):
        """
        Remove a collection from the site data.

        coll_id     identifier for the collection to remove.

        Returns a non-False status code if the collection is not removed.
        """
        log.debug("remove_collection: %s"%(coll_id))
        return Collection.remove(self, coll_id)

    # JSON-LD context data

    def generate_site_jsonld_context(self):
        """
        (Re)generate JSON-LD context description for the current collection.

        get_field_uri_context
                is a supplied function that accepts a RecordField object abnd
                returns a context dictionary for the field thus described.
        """
        # Build context data
        context = self.get_site_jsonld_context()
        # Assemble and write out context description
        with self._metaobj(layout.SITEDATA_CONTEXT_PATH, layout.COLL_CONTEXT_FILE, "wt") as context_io:
            json.dump(
                { "@context": context }, 
                context_io, indent=2, separators=(',', ': ')
                )
        return

    def get_site_jsonld_context(self):
        """
        Return dictionary containing context structure for collection.
        """
        # @@REVIEW: as a workaround for a problem with @base handling in rdflib-jsonld, don't
        #           include @base in context.
        #
        # context           = OrderedDict(
        #     { "@base": self.get_url() + layout.SITEDATA_DIR + "/"
        #     })
        # context           = OrderedDict(
        #     { "@base": "./"
        #     })
        #
        # Use OrderedDict to allow some control over ordering of context file contents:
        # this is for humane purposes only, and is not technically important.
        context           = OrderedDict(
            { ANNAL.CURIE.type: { "@type": "@id" }
            })
        # Scan vocabs, generate prefix data
        for v in self._site_children(RecordVocab):
            vid = v.get_id()
            if vid != "_initial_values":
                context[v.get_id()] = v[ANNAL.CURIE.uri]
        # Set type info for predefined URI fields
        # for f in [ANNAL.CURIE.user_uri]:
        #     self.set_field_uri_jsonld_context(f, { "@type": "@id" }, context)
        # Scan view fields and generate context data for property URIs used
        for v in self._site_children(RecordView):
            for fref in v[ANNAL.CURIE.view_fields]:
                fid  = extract_entity_id(fref[ANNAL.CURIE.field_id])
                vuri = fref.get(ANNAL.CURIE.property_uri, None)
                furi, fcontext = self.get_field_uri_jsonld_context(fid, self.get_field_jsonld_context)
                # fcontext['vid'] = v.get_id()
                # fcontext['fid'] = fid
                self.set_field_uri_jsonld_context(vuri or furi, fcontext, context)
        # Scan group fields and generate context data for property URIs used
        for g in self._site_children(RecordGroup):
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
        f = RecordField.load(self, fid, use_altpath=True)
        if f is None:
            return (None, None)
        return (f[ANNAL.CURIE.property_uri], get_field_context(f))

    # @@TODO: Make static and use common copy with `collection`
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

    # Temporary helper functions
    #
    # @@TODO - temporary fix
    #
    # These helpers return children of the site object.  
    #
    # It works like the EntityRoot._children method except that it uses the 
    # alternative parent path for the supplied class.  This alternative path
    # logic should be eliminated when the site data is moved to a special
    # site data collection: then the access for all child data should be
    # unified.

    def _site_children_ids(self, cls):
        """
        Iterates over candidate child entyity ids that are possible instances 
        of an indicated class.  The supplied class is used to determine a 
        subdirectory to be scanned.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        """
        site_dir = os.path.dirname(os.path.join(self._entitydir, cls._entityaltpath))
        assert "%" not in site_dir, "_entitypath/_entityaltpath template variable interpolation may be in filename part only"
        site_files = []
        if site_dir and os.path.isdir(site_dir):
            site_files = os.listdir(site_dir)
        for fil in site_files:
            if valid_id(fil):
                yield fil
        return

    def _site_children(self, cls):
        """
        Iterates over candidate children of the current site object that are instances 
        of an indicated class.

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        """
        for i in self._site_children_ids(cls):
            e = cls.load(self, i, use_altpath=True)
            if e:
                yield e
        return

# End.
