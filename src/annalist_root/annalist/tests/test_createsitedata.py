"""
Test module used to create some initial site data for experimentation and manual testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions

import annalist
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                  import test_layout
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from init_tests             import copySitedata
from entity_testutils       import collection_create_values
from entity_testtypedata    import recordtype_create_values
from entity_testviewdata    import recordview_create_values
from entity_testlistdata    import recordlist_create_values

#   -----------------------------------------------------------------------------
#
#   Helper functions
#
#   -----------------------------------------------------------------------------

def entitydata_create_values(coll, etype, entity_id, update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s %s/%s/%s'%(update, coll._entityid, etype._entityid, entity_id)
        , 'rdfs:comment': '%s coll %s, type %s, entity %s'%(update, coll._entityid, etype._entityid, entity_id)
        })

def site_create_data(site_base_uri, target_subdir):
    """
    Create site data in `target_subdir`...

    @@NOTE: due to the way EntityRoot is defenfensively coded, all test data is created
    under settings.BASE_SITE_DIR, and the supplied 'target_subdir' parameter is ignored.
    """
    # target_dir = os.path.join(settings.SAMPLEDATA_DIR, target_subdir)
    target_dir = settings.BASE_SITE_DIR
    site       = Site.initialize_site_data(
        site_base_uri, target_dir,
        settings.SITE_SRC_ROOT + "/annalist/data/sitedata",
        label="Annalist data notebook test site", 
        description="Annalist test site metadata and site-wide values."
        )
    return site

def coll123_create_data(site):
    coll1 = Collection.create(site, "coll1", collection_create_values("coll1"))
    coll2 = Collection.create(site, "coll2", collection_create_values("coll2"))
    coll3 = Collection.create(site, "coll3", collection_create_values("coll3"))
    #
    for coll in [coll1, coll2, coll3]:
        type1 = RecordType.create(coll, "type1", recordtype_create_values(coll._entityid, "type1"))
        view1 = RecordView.create(coll, "view1", recordview_create_values(coll._entityid, "view1"))
        list1 = RecordList.create(coll, "list1", recordlist_create_values(coll._entityid, "list1"))
        data1 = RecordTypeData.create(coll, "type1", {})
        type2 = RecordType.create(coll, "type2", recordtype_create_values(coll._entityid, "type2"))
        view2 = RecordView.create(coll, "view2", recordview_create_values(coll._entityid, "view2"))
        list2 = RecordList.create(coll, "list2", recordlist_create_values(coll._entityid, "list2"))
        data2 = RecordTypeData.create(coll, "type2", {})
        #
        for t,d in [(type1,data1),(type2,data2)]:
            for eid in ["entity1", "entity2", "entity3"]:
                e = EntityData.create(d, eid, entitydata_create_values(coll,t,eid))
    return

def collbib_create_data(site):
    bibcoll = Site.initialize_bib_data(site, 
        settings.SITE_SRC_ROOT+"/annalist/data/bibdata",
        # label="Bibliographic definitions", 
        # description="Bibliographic definitions for testing"
        )
    return

#   -----------------------------------------------------------------------------
#
#   CreateSiteData
#
#   -----------------------------------------------------------------------------

class CreateSiteData(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Create site data
    #   -----------------------------------------------------------------------------

    def make_CreateDevelSiteData(self):
        # Note: copysitedata copies also copies from source tree
        #       def copySitedata(src, sitedatasrc, tgt):
        copySitedata(
            settings.SITE_SRC_ROOT+"/devel/"+test_layout.SITE_DIR, 
            settings.SITE_SRC_ROOT+"/annalist/data/sitedata",
            TestBaseDir)
        # Use localhost base URI for devel site
        develsite = site_create_data("http://localhost:8000/annalist/", "devel")
        coll123_create_data(develsite)
        return

    def test_CreateTestSiteData(self):
        testsite = site_create_data(TestBaseUri, "testinit")
        coll123_create_data(testsite)
        return

    #@@
    # def test_CreateBibTestSiteData(self):
    #     testsite = site_create_data(TestBaseUri, "bibtestinit")
    #     collbib_create_data(testsite)
    #     coll123_create_data(testsite)
    #     return
    #@@

    def test_CreateEmptySiteData(self):
        emptysite = site_create_data(TestBaseUri, "empty")
        return

# End.
