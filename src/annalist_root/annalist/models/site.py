"""
Annalist site-related facilities
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
from annalist                       import layout
from annalist                       import message
from annalist.util                  import (
    valid_id, extract_entity_id, replacetree, updatetree
    )

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
    _entitytypeid   = layout.SITE_TYPEID
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
        self.set_id(layout.SITEDATA_ID)
        return

    def _exists(self):
        """
        The site entity has no explicit data, so always respond with 'True' to an _exists() query
        """
        return True

    def _children(self, cls, altscope=None):
        """
        Iterates over candidate child identifiers that are possible instances of an 
        indicated class.  The supplied class is used to determine a subdirectory to 
        be scanned.  As a spoecial case, the children are iterated only in a special 
        `altscope` called "site".

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    Ignored, accepoted for compatibility with Entity._children()
        """
        if altscope == "site":
            return self._base_children(cls)
        return iter(())     # Empty iterator

    def child_entity_ids(self, cls, altscope=None):
        """
        Iterates over child entity identifiers of an indicated class.
        If the altscope is "all" or not specified, the altscope value
        used is "site".

        cls         is a subclass of Entity indicating the type of children to
                    iterate over.
        altscope    if supplied, indicates a scope other than the current entity to
                    search for children.  See method `get_alt_entities` for more details.
        """
        if altscope == "select":
            altscope = "site"
        return super(Site, self).child_entity_ids(cls, altscope=altscope)

    def site_data_collection(self, test_exists=True):
        """
        Return collection entity that contains the site data.

        test_exists unless this is supllied as False, generates an error if the site
                    metadata does not exist.
        """
        if self._sitedata is None:
            self._sitedata = SiteData.load_sitedata(self, test_exists=test_exists)
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
        context = self.site_data_collection().get_coll_jsonld_context()
        # Assemble and write out context description
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        datetime_str = datetime_now.isoformat(' ')
        with self._metaobj(
            layout.SITEDATA_CONTEXT_PATH, layout.SITE_CONTEXT_FILE, "wt"
            ) as context_io:
            json.dump(
                { "_comment": "Generated by generate_site_jsonld_context on %s"%datetime_str
                , "@context": context 
                }, 
                context_io, indent=2, separators=(',', ': '), sort_keys=True
                )
        return

    # Site data
    #
    # These methods are used by test_createsitedata and annalist-manager to initialize
    # or update Annalist site data.  Tests are run using data copied from sampledata/init
    # to sampledata/data, allowing for additional test fixture files to be included.
    #
    @staticmethod
    def create_site_metadata(site_base_uri, site_base_dir, 
        label=None, description=None):
        """
        Create new site metadata record for a new site, and 
        return the Site object.

        This resets the site label and description that 
        may have been updated by a sirte administrator.
        """
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        if label is None:
            label = "Annalist linked data notebook site"
        if description is None:
            description = "Annalist site metadata and site-wide values."
        annal_comment = (
            "Initialized by annalist.models.site.create_site_metadata at "+
            datetime_now.isoformat(' ')
            )
        site = Site(site_base_uri, site_base_dir)
        sitedata_values = (
            { RDFS.CURIE.label:             label
            , RDFS.CURIE.comment:           description
            , ANNAL.CURIE.meta_comment:     annal_comment                                    
            , ANNAL.CURIE.software_version: annalist.__version_data__
            })
        sitedata = SiteData.create_sitedata(site, sitedata_values)
        return site

    @staticmethod
    def create_site_readme(site):
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
            """        _annalist_site/                 (site-wide definitions)\n"""+
            """          d/\n"""+
            """            coll_meta.jsonld            (site metadata)\n"""+
            """            coll_context.jsonld         (JSON-LD context for site definitions)\n"""+
            """            %(enum_field_placement_dir)s/\n"""+
            """              (field-placement-value)/\n"""+
            """                enum_meta.jsonld\n"""+
            """               :\n"""+
            """            %(enum_list_type_dir)s/\n"""+
            """              (list-type-id)/\n"""+
            """                enum_meta.jsonld\n"""+
            """               :\n"""+
            """            %(enum_render_type_dir)s/\n"""+
            """              (render-type-id)/\n"""+
            """                enum_meta.jsonld\n"""+
            """               :\n"""+
            """            %(enum_value_type_dir)s/\n"""+
            """              (value-type-id)/\n"""+
            """                enum_meta.jsonld\n"""+
            """               :\n"""+
            """            %(enum_value_mode_dir)s/\n"""+
            """              (value-mode-id)/\n"""+
            """                enum_meta.jsonld\n"""+
            """               :\n"""+
            """            %(field_dir)s/\n"""+
            """              (view-field definitions)\n"""+
            """               :\n"""+
            """            %(group_dir)s/\n"""+
            """              (field group definitions)\n"""+
            """               :\n"""+
            """            %(list_dir)s/\n"""+
            """              (entity list definitions)\n"""+
            """               :\n"""+
            """            %(type_dir)s/\n"""+
            """              (type definitions)\n"""+
            """               :\n"""+
            """            %(user_dir)s/\n"""+
            """              (user permissions)\n"""+
            """               :\n"""+
            """            %(view_dir)s/\n"""+
            """              (entity view definitions)\n"""+
            """               :\n"""+
            """            %(vocab_dir)s/\n"""+
            """              (vocabulary namespace definitions)\n"""+
            """               :\n"""+
            """        (collection-id)/                (user-created data collection)\n"""+
            """          d/\n"""+
            """            coll_meta.jsonld            (collection metadata)\n"""+
            """            coll_context.jsonld         (JSON-LD context for collection data)\n"""+
            """            %(type_dir)s/                      (collection type definitions)\n"""+
            """              (type-id)/\n"""+
            """                type_meta.jsonld\n"""+
            """               :\n"""+
            """            %(list_dir)s/                      (collection list definitions)\n"""+
            """              (list-id)/\n"""+
            """                list_meta.jsonld\n"""+
            """               :\n"""+
            """            %(view_dir)s/                      (collection view definitions)\n"""+
            """              (view-id)/\n"""+
            """                view_meta.jsonld\n"""+
            """               :\n"""+
            """            %(field_dir)s/                     (collection field definitions)\n"""+
            """              (field-id)/\n"""+
            """                field_meta.jsonld\n"""+
            """               :\n"""+
            """            %(group_dir)s/                     (collection field group definitions)\n"""+
            """              (group-id)/\n"""+
            """                group_meta.jsonld\n"""+
            """               :\n"""+
            """            %(user_dir)s/                      (collection user permissions)\n"""+
            """              (user-id)/\n"""+
            """                user_meta.jsonld\n"""+
            """               :\n"""+
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
                { 'site_base_dir':              site._entitydir
                , 'site_base_uri':              site._entityurl
                , 'datetime':                   datetime_now.isoformat(' ')
                , 'version':                    annalist.__version__
                , 'enum_field_placement_dir':   layout.ENUM_FIELD_PLACEMENT_DIR
                , 'enum_list_type_dir':         layout.ENUM_LIST_TYPE_DIR
                , 'enum_render_type_dir':       layout.ENUM_RENDER_TYPE_DIR
                , 'enum_value_type_dir':        layout.ENUM_VALUE_TYPE_DIR
                , 'enum_value_mode_dir':        layout.ENUM_VALUE_MODE_DIR
                , 'field_dir':                  layout.FIELD_DIR
                , 'group_dir':                  layout.GROUP_DIR
                , 'list_dir':                   layout.LIST_DIR
                , 'type_dir':                   layout.TYPE_DIR
                , 'user_dir':                   layout.USER_DIR
                , 'view_dir':                   layout.VIEW_DIR
                , 'vocab_dir':                  layout.VOCAB_DIR
                }
            )
        with site._fileobj("README", ANNAL.CURIE.Richtext, "text/markdown", "wt") as readme:
            readme.write(README)
        return

    @staticmethod
    def create_empty_coll_data(
        site, coll_id,
        label=None, description=None):
        """
        Create empty collection, and returns the Collection object.
        """
        datetime_now = datetime.datetime.today().replace(microsecond=0)
        if label is None:
            label = "Collection %s"%coll_id
        if description is None:
            description = "Annalist data collection %s"%coll_id
        annal_comment = (
            "Initialized by annalist.models.site.create_empty_coll_data at "+
            datetime_now.isoformat(' ')
            )
        coll_values = (
            { RDFS.CURIE.label:             label
            , RDFS.CURIE.comment:           description
            , ANNAL.CURIE.meta_comment:     annal_comment                                    
            , ANNAL.CURIE.software_version: annalist.__version_data__
            })
        coll = Collection.create(site, coll_id, coll_values)
        return coll

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
        old data for the directory that is not updated is left as-is.
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
        site = Site.create_site_metadata(
            site_base_uri, site_base_dir, label=label, description=description
            )
        sitedata = site.site_data_collection()
        Site.create_site_readme(site)
        site_data_tgt, site_data_file = sitedata._dir_path()
        log.info("Copy Annalist site data from %s to %s"%(site_data_src, site_data_tgt))
        for sdir in layout.COLL_DIRS:
            log.info("- %s -> %s"%(sdir, site_data_tgt))
            Site.replace_site_data_dir(sitedata, sdir, site_data_src)
        sitedata.generate_coll_jsonld_context()
        return site

    @staticmethod
    def initialize_bib_data(site, bib_data_src ):
        # label=None, description=None
        """
        Initializes bibliography definitions data for a new site for testing.
        """
        bibdatacoll = site.create_empty_coll_data(site, layout.BIBDATA_ID, 
            label="Bibliographic record definitions", 
            description=
                "Definitions for bibliographic records, broadly following BibJSON. "+
                "Used for some Annalist test cases."
            )
        bib_data_tgt, bib_data_file = bibdatacoll._dir_path()
        log.info("Copy Annalist bibliographic definitions data from %s to %s"%(bib_data_src, bib_data_tgt))
        for sdir in layout.DATA_DIRS:
            log.info("- %s -> %s"%(sdir, bib_data_tgt))
            Site.replace_site_data_dir(bibdatacoll, sdir, bib_data_src)
        bibdatacoll.generate_coll_jsonld_context()
        return bibdatacoll

    # @staticmethod
    # def initialize_named_coll(
    #     site, coll_id, coll_data_src,
    #     label=None, description=None):
    #     """
    #     Initializes bibliography definitions data for a new site for testing.
    #     """
    #     namedcoll = site.create_empty_coll_data(
    #         site, coll_id, 
    #         label=label, description=description
    #         )
    #     coll_data_tgt, coll_data_file = namedcoll._dir_path()
    #     log.info("Copy Annalist %s definitions data from %s to %s"%(coll_id, coll_data_src, coll_data_tgt))
    #     for sdir in layout.DATA_DIRS:
    #         log.info("- %s -> %s"%(sdir, coll_data_tgt))
    #         Site.replace_site_data_dir(namedcoll, sdir, coll_data_src)
    #     namedcoll.generate_coll_jsonld_context()
    #     return namedcoll

# End.
