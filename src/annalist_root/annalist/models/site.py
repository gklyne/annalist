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
import datetime
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
from annalist.util                  import valid_id, extract_entity_id, replacetree
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
    _entityfile     = layout.SITE_META_FILE
    _entityref      = layout.META_SITE_REF

    def __init__(self, sitebaseuri, sitebasedir, host=""):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base directory for site information
        """
        log.debug("Site.__init__: sitebaseuri %s, sitebasedir %s"%(sitebaseuri, sitebasedir))
        sitebaseuri    = sitebaseuri if sitebaseuri.endswith("/") else sitebaseuri + "/"
        sitebasedir    = sitebasedir if sitebasedir.endswith("/") else sitebasedir + "/"
        sitepath       = layout.SITE_META_PATH
        siteuripath    = urlparse.urljoin(sitebaseuri, sitepath) 
        sitedir        = os.path.join(sitebasedir, sitepath)
        self._sitedata = None
        super(Site, self).__init__(host+siteuripath, siteuripath, sitedir, sitebasedir)
        return

    def site_data_collection(self):
        """
        Return collection entity that contains the site data.
        """
        if self._sitedata is None:
            self._sitedata = SiteData.load_sitedata(self)
        return self._sitedata

    def site_data_stream(self):
        """
        Return stream containing the raw site data.
        """
        return self.site_data_collection()._read_stream()

    def site_data(self):
        """
        Return dictionary of site data
        """
        # @@TODO: consider using generic view logic for this mapping (and elsewhere?)
        #         This is currently a bit of a kludge, designed to match the site
        #         view template.  In due course, it may be reviewed and implemented
        #         using the generic Annalist form generating framework
        site_data  = self.site_data_collection().get_values()
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
        return self.site_data_collection().get_user_permissions(user_id, user_uri)

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        Yielded values are collection objects.
        """
        log.debug("site.collections: basedir: %s"%(self._entitydir))
        for f in self._base_children(Collection):
            c = Collection.load(self, f)
            # log.info("Site.colections: Collection.load %s %r"%(f, c.get_values()))
            if c:
                yield c
        return

    def collections_dict(self):
        """
        Return an ordered dictionary of collections indexed by collection id
        """
        coll = [ (c.get_id(), c) for c in self.collections() ]
        return collections.OrderedDict(sorted(coll))

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
        if coll_id == layout.SITEDATA_ID:
            raise ValueError("Attempt to remove site data collection (%s)"%coll_id)
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
        #@@ context = self.get_site_jsonld_context()
        context = self.site_data_collection().get_coll_jsonld_context()
        # Assemble and write out context description
        with self._metaobj(
            layout.SITEDATA_CONTEXT_PATH, layout.COLL_CONTEXT_FILE, "wt"
            ) as context_io:
            json.dump(
                { "@context": context }, 
                context_io, indent=2, separators=(',', ': ')
                )
        return

    # Site data
    #
    # These methods are used by test_createsitedata and annalist-manager to initialize
    # or update Annalist site data.  Tests are run using data copied from sampledata/init
    # to sampledata/data, allowing for additional test fixture files to be included.

    @staticmethod
    def create_empty_site_data(site_base_uri, site_base_dir, 
        label=None, description=None):
        """
        Create empty directory structure for a new site, and returns the
        Site object.
        """
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        if label is None:
            label = "Annalist linked data notebook site"
        if description is None:
            description = "Annalist test site metadata and site-wide values."
        annal_comment = (
            "Initialized by annalist.tests.test_createsitedata.py at "+
            datetime_now.isoformat(' ')
            )
        site = Site(site_base_uri, site_base_dir)
        sitedata_values = (
            { RDFS.CURIE.label:             label
            , RDFS.CURIE.comment:           description
            , ANNAL.CURIE.comment:          annal_comment                                    
            , ANNAL.CURIE.software_version: annalist.__version_data__
            })
        sitedata  = SiteData.create_sitedata(site, sitedata_values)
        return site

    @staticmethod
    def create_site_readme(sitedata):
        """
        Create new site README.md.
        """
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        README = ((
            """%(site_base_dir)s\n"""+
            """\n"""+
            """This directory contains Annalist site data for %(site_base_uri)s.\n"""+
            """\n"""+
            """Directory layout:\n"""+
            """\n"""+
            """    %(site_base_dir)s\n"""+
            """      c/\n"""+
            """        _annalist_site/\n"""+
            """          _annalist_collection/         (site-wide definitions)\n"""+
            """            coll_meta.jsonld            (site metadata)\n"""+
            """            coll_context.jsonld         (JSON-LD context for site definitions)\n"""+
            """            enums/\n"""+
            """              (enumerated type values)\n"""+
            """               :\n"""+
            """            fields/\n"""+
            """              (view-field definitions)\n"""+
            """               :\n"""+
            """            groups/\n"""+
            """              (field group definitions)\n"""+
            """               :\n"""+
            """            lists/\n"""+
            """              (entity list definitions)\n"""+
            """               :\n"""+
            """            types/\n"""+
            """              (type definitions)\n"""+
            """               :\n"""+
            """            users/\n"""+
            """              (user permissions)\n"""+
            """               :\n"""+
            """            views/\n"""+
            """              (entity view definitions)\n"""+
            """               :\n"""+
            """            vocabs/\n"""+
            """              (vocabulary namespace definitions)\n"""+
            """               :\n"""+
            """        (collection-id)/                (user-created data collection)\n"""+
            """          _annalist_collection/         (collection definitions)\n"""+
            """            coll_meta.jsonld            (collection metadata)\n"""+
            """            coll_context.jsonld         (JSON-LD context for collection definitions)\n"""+
            """            types/                      (collection type definitions\n"""+
            """              (type-id)/\n"""+
            """                type_meta.jsonld\n"""+
            """               :\n"""+
            """            lists/                      (collection list definitions\n"""+
            """              (list-id)/\n"""+
            """                list_meta.jsonld\n"""+
            """               :\n"""+
            """            views/                      (collection view definitions\n"""+
            """              (view-id)/\n"""+
            """                view_meta.jsonld\n"""+
            """               :\n"""+
            """            fields/                     (collection field definitions\n"""+
            """              (field-id)/\n"""+
            """                field_meta.jsonld\n"""+
            """               :\n"""+
            """            groups/                     (collection field group definitions\n"""+
            """              (group-id)/\n"""+
            """                group_meta.jsonld\n"""+
            """               :\n"""+
            """            users/                      (collection user permissions\n"""+
            """              (user-id)/\n"""+
            """                user_meta.jsonld\n"""+
            """               :\n"""+
            """          d/\n"""+
            """            (type-id)/                  (contains all entity data for identified type)\n"""+
            """              (entity-id)/              (contains data for identified type/entity)\n"""+
            """                entity_data.jsonld      (entity data)\n"""+
            """                entity_prov.jsonld      (entity provenance @@TODO)\n"""+
            """                (attachment files)      (uploaded/imported attachments)\n"""+
            """\n"""+
            """               :                        (repeat for entities of this type)\n"""+
            """\n"""+
            """             :                          (repeat for types in collection)\n"""+
            """\n"""+
            """         :                              (repeat for collections in site)\n"""+
            """\n"""+
            """Created by annalist.models.site.py\n"""+
            """for Annalist %(version)s at %(datetime)s\n"""+
            """\n"""+
            """\n""")%
                { 'site_base_dir': sitedata._entitydir
                , 'site_base_uri': sitedata._entityurl
                , 'datetime':      datetime_now.isoformat(' ')
                , 'version':       annalist.__version__
                }
            )
        with sitedata._fileobj("README", ANNAL.CURIE.Richtext, "text/markdown", "wt") as readme:
            readme.write(README)
        return

    @staticmethod
    def replace_site_data_dir(sitedata, sdir, site_data_src):
        """
        Replace indicated sitedata directory data from source: 
        old data for the directory is removed.
        """
        site_data_tgt, site_data_file = sitedata._dir_path()
        s = os.path.join(site_data_src, sdir)
        d = os.path.join(site_data_tgt, sdir)
        replacetree(s, d)
        return

    @staticmethod
    def update_site_data_dir(sitedata, sdir, site_data_src):
        """
        Update indicated sitedata directory data from source: 
        old data for the directory thgat ios not updated is left as-is.
        """
        site_data_tgt, site_data_file = sitedata._dir_path()
        s = os.path.join(site_data_src, sdir)
        d = os.path.join(site_data_tgt, sdir)
        updatetree(s, d)
        return

    @staticmethod
    def initialize_site_data(
        site_base_uri, site_base_dir, site_data_src, 
        label=None, description=None):
        """
        Initializes site data for a new site for testing.

        Creates a README.md file in the site base directory, and creates a
        collection _annalist_site containing built-in types, views, etc.
        """
        site = Site.create_empty_site_data(
            site_base_uri, site_base_dir, label=label, description=description
            )
        sitedata = site.site_data_collection()
        Site.create_site_readme(site)
        site_data_tgt, site_data_file = sitedata._dir_path()
        log.info("Copy Annalist site data from %s to %s"%(site_data_src, site_data_tgt))
        for sdir in ("types", "lists", "views", "groups", "fields", "vocabs", "users", "enums"):
            log.info("- %s -> %s"%(sdir, site_data_tgt))
            Site.replace_site_data_dir(sitedata, sdir, site_data_src)
        sitedata.generate_coll_jsonld_context()
        return site

# End.
