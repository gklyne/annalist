"""
Test JSONB-:LD context generat5iobn logic
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from rdflib                         import Graph, URIRef, Literal

from django.test.client             import Client

import annalist
from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.collection     import Collection
# from annalist.models.recordtype     import RecordType
# from annalist.models.recordview     import RecordView
# from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

# from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    collection_create_values,
    create_test_user,
    # context_list_entities,
    )
# from entity_testtypedata            import (
#     recordtype_create_values
#     )
# from entity_testentitydata          import (
#     entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
#     entitydata_list_type_url, entitydata_list_all_url,
#     entitydata_value_keys, entitydata_create_values, entitydata_values, 
#     )

#   -----------------------------------------------------------------------------
#
#   JSON-LD context generation tests
#
#   -----------------------------------------------------------------------------

class JsonldContextTest(AnnalistTestCase):
    """
    Tests site/collection data interpreted as JSON-LD
    """

    def setUp(self):
        self.testsite = init_annalist_test_site()
        self.testcoll = init_annalist_test_coll()

        # self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.testcoll = Collection(self.testsite, "testcoll")

        # Create test types

        #@@
        # self.testtypes = RecordType.create(
        #     self.testcoll, "testtypes", 
        #     recordtype_create_values(
        #         coll_id="testcoll", type_id="testtypes", type_uri="test:testtypes",
        #         supertype_uris=[]
        #         )
        #     )
        # self.testtype1 = RecordType.create(
        #     self.testcoll, "testtype1",
        #     recordtype_create_values(
        #         coll_id="testcoll", type_id="testtype1", type_uri="test:testtype1", 
        #         supertype_uris=["test:testtypes"]
        #         )
        #     )
        # self.testtype2 = RecordType.create(
        #     self.testcoll, "testtype2",
        #     recordtype_create_values(
        #         coll_id="testcoll", type_id="testtype2", type_uri="test:testtype2", 
        #         supertype_uris=["test:testtypes"]
        #         )
        #     )
        # self.ref_type  = RecordType.create(
        #     self.testcoll, "ref_type", 
        #     recordtype_create_values(
        #         coll_id="testcoll", type_id="ref_type", type_uri="test:ref_type",
        #         supertype_uris=[]
        #         )
        #     )
        # # Create test type data parents
        # self.testdatas = RecordTypeData.create(self.testcoll, "testtypes", {})
        # self.testdata1 = RecordTypeData.create(self.testcoll, "testtype1", {})
        # self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        # self.ref_data  = RecordTypeData.create(self.testcoll, "ref_type",  {})
        # # Create test type data
        # es = EntityData.create(self.testdatas, "entitys", 
        #     entitydata_create_values(
        #         "entitys", type_id="testtypes", extra_fields={"test:turi": "test:testtypes"} 
        #         )
        #     )
        # e1 = EntityData.create(self.testdata1, "entity1", 
        #     entitydata_create_values(
        #         "entity1", type_id="testtype1", extra_fields={"test:turi": "test:testtype1"} 
        #         )
        #     )
        # e2 = EntityData.create(self.testdata2, "entity2", 
        #     entitydata_create_values(
        #         "entity2", type_id="testtype2", extra_fields={"test:turi": "test:testtype2"} 
        #         )
        #     )
        #@@

        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    # def _check_entity_list(self, type_id, expect_entities):
    #     u = entitydata_list_type_url("testcoll", type_id)
    #     r = self.client.get(u)
    #     self.assertEqual(r.status_code,   200)
    #     self.assertEqual(r.reason_phrase, "OK")
    #     self.assertContains(r, "<title>Collection testcoll</title>")
    #     self.assertContains(r, "<h3>List entities</h3>", html=True)
    #     # Test context
    #     self.assertEqual(r.context['coll_id'],  "testcoll")
    #     self.assertEqual(r.context['type_id'],  type_id)
    #     entities = context_list_entities(r.context)
    #     self.assertEqual(len(entities), len(expect_entities))
    #     for eid in range(len(expect_entities)):
    #         self.assertEqual(entities[eid]['entity_type_id'], expect_entities[eid][0])
    #         self.assertEqual(entities[eid]['entity_id'], expect_entities[eid][1])
    #     return

    # def _create_ref_type_view(self, view_id="Test_ref_type_view", record_type="test:testtypes"):
    #     ref_type_view = RecordView.create(self.testcoll, view_id,
    #         { 'annal:type':         "annal:View"
    #         , 'annal:uri':          "test:"+view_id
    #         , 'rdfs:label':         "Test view label"
    #         , 'rdfs:comment':       "Test view comment"
    #         , 'annal:record_type':  record_type
    #         , 'annal:add_field':    True
    #         , 'annal:view_fields':
    #           [ { 'annal:field_id':         "_field/Entity_id"
    #             , 'annal:field_placement':  "small:0,12;medium:0,6"
    #             }
    #           , { 'annal:field_id':         "_field/Test_ref_type_field"
    #             , 'annal:field_placement':  "small:0,12;medium:0,6"
    #             }
    #           ]
    #         })
    #     self.assertTrue(ref_type_view is not None)
    #     return ref_type_view

    # def _create_ref_type_field(self, entity_type="test:testtypes"):
    #     ref_type_field = RecordField.create(self.testcoll, "Test_ref_type_field",
    #         { "annal:type":                     "annal:Field"
    #         , "rdfs:label":                     "Type reference"
    #         , "rdfs:comment":                   "Type reference field comment"
    #         , "annal:field_render_type":        "Enum_render_type/Enum_choice"
    #         , "annal:field_value_mode":         "Enum_value_mode/Value_direct"
    #         , "annal:field_entity_type":        "test:ref_type"
    #         , "annal:placeholder":              "(ref type field)"
    #         , "annal:property_uri":             "test:ref_type"
    #         , "annal:field_placement":          "small:0,12;medium:0,6"
    #         , "annal:field_ref_type":           "_type/testtypes"
    #         , "annal:field_ref_restriction":    "[test:turi] subtype %s"%entity_type
    #         , "annal:field_entity_type":        entity_type
    #         })
    #     self.assertTrue(ref_type_field is not None)
    #     return ref_type_field

    #   -----------------------------------------------------------------------------
    #   JSON-LD context tests
    #   -----------------------------------------------------------------------------

    def test_jsonld_site(self):
        """
        Read site data as JSON-LD, and check resulting RDF triples
        """
        # Generate site-level JSON-LD context data
        # self.testsite.generate_site_jsonld_context()

        # Read site data as JSON-LD
        g = Graph()
        s = self.testsite._read_stream()
        # b = self.testsite.get_url()
        b = "file://" + os.path.join(TestBaseDir, layout.SITEDATA_DIR) + "/"
        # print "*****"+repr(b)
        # print "*****"+repr(s)
        # print "*****"+repr(b)
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print "***** site:"
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj      = URIRef(self.testsite.get_url())
        subj      = URIRef("file://" + TestBaseDir + "/")
        site_data = self.testsite.site_data()
        label     = Literal(site_data[RDFS.CURIE.label])
        comment   = Literal(site_data[RDFS.CURIE.comment])
        self.assertIn((subj, URIRef(RDFS.label),   label),   g)
        self.assertIn((subj, URIRef(RDFS.comment), comment), g)
        return

    def test_jsonld_collection(self):
        """
        Read new collection data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        # self.testcoll.generate_coll_jsonld_context()

        # Read collection data as JSON-LD
        g = Graph()
        s = self.testcoll._read_stream()
        b = "file://" + os.path.join(TestBaseDir, layout.SITE_COLL_CONTEXT_PATH%{'id': self.testcoll.get_id()})
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print "***** coll:"
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj      = self.testcoll.get_url()
        subj      = "file://" + os.path.join(TestBaseDir, layout.SITE_COLL_PATH%{'id': self.testcoll.get_id()}) + "/"
        coll_data = self.testcoll._load_values()
        for (s, p, o) in (
            [ (subj, RDFS.label,             Literal(coll_data[RDFS.CURIE.label])       )
            , (subj, RDFS.comment,           Literal(coll_data[RDFS.CURIE.comment])     )
            , (subj, ANNAL.id,               Literal(coll_data[ANNAL.CURIE.id])         )
            , (subj, ANNAL.type_id,          Literal(coll_data[ANNAL.CURIE.type_id])    )
            , (subj, ANNAL.type,             URIRef(ANNAL.Collection)                   )
            , (subj, ANNAL.software_version, Literal(annalist.__version_data__)         )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_jsonld_entity1(self):
        """
        Read default entity data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")

        # Read entity data as JSON-LD
        g = Graph()
        s = entity1._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITE_ENTITY_PATH%
                  { 'coll_id': self.testcoll.get_id()
                  , 'type_id': testdata.get_id()
                  , 'id':      entity1.get_id()
                  }
                ) + 
              "/"
            )
        # print("***** b: (entity1)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj        = b #@@ entity1.get_url()
        entity_data = entity1.get_values()
        for (s, p, o) in (
            [ (subj, RDFS.label,             Literal(entity_data[RDFS.CURIE.label])       )
            , (subj, RDFS.comment,           Literal(entity_data[RDFS.CURIE.comment])     )
            , (subj, ANNAL.id,               Literal(entity_data[ANNAL.CURIE.id])         )
            , (subj, ANNAL.type_id,          Literal(entity_data[ANNAL.CURIE.type_id])    )
            , (subj, ANNAL.type,             URIRef(ANNAL.EntityData)                     )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

# End.
