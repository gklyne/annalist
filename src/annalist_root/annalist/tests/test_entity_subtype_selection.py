"""
Tests for EntityData subtype selection in list views and select dropdowns
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.test.client             import Client

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.form_utils.fieldchoice  import FieldChoice

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    create_test_user,
    context_list_entities,
    )
from entity_testtypedata            import (
    recordtype_create_values
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    )

#   -----------------------------------------------------------------------------
#
#   Subtype selection tests
#
#   -----------------------------------------------------------------------------

class SubtypeSelectionTest(AnnalistTestCase):
    """
    Tests for 
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection.create(
            self.testsite, "testcoll", collection_create_values("testcoll")
            )
        # Create test types
        self.testtypes = RecordType.create(
            self.testcoll, "testtypes", 
            recordtype_create_values(
                coll_id="testcoll", type_id="testtypes", type_uri="test:testtypes",
                supertype_uris=[]
                )
            )
        self.testtype1 = RecordType.create(
            self.testcoll, "testtype1",
            recordtype_create_values(
                coll_id="testcoll", type_id="testtype1", type_uri="test:testtype1", 
                supertype_uris=["test:testtypes"]
                )
            )
        self.testtype2 = RecordType.create(
            self.testcoll, "testtype2",
            recordtype_create_values(
                coll_id="testcoll", type_id="testtype2", type_uri="test:testtype2", 
                supertype_uris=["test:testtypes"]
                )
            )
        self.ref_type  = RecordType.create(
            self.testcoll, "ref_type", 
            recordtype_create_values(
                coll_id="testcoll", type_id="ref_type", type_uri="test:ref_type",
                supertype_uris=[]
                )
            )
        # Create test type data parents
        self.testdatas = RecordTypeData.create(self.testcoll, "testtypes", {})
        self.testdata1 = RecordTypeData.create(self.testcoll, "testtype1", {})
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        self.ref_data  = RecordTypeData.create(self.testcoll, "ref_type",  {})
        # Create test type data
        es = EntityData.create(self.testdatas, "entitys", 
            entitydata_create_values(
                "entitys", type_id="testtypes", extra_fields={"test:turi": "test:testtypes"} 
                )
            )
        e1 = EntityData.create(self.testdata1, "entity1", 
            entitydata_create_values(
                "entity1", type_id="testtype1", extra_fields={"test:turi": "test:testtype1"} 
                )
            )
        e2 = EntityData.create(self.testdata2, "entity2", 
            entitydata_create_values(
                "entity2", type_id="testtype2", extra_fields={"test:turi": "test:testtype2"} 
                )
            )
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

    def _check_entity_list(self, type_id, expect_entities):
        u = entitydata_list_type_url("testcoll", type_id)
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        self.assertContains(r, "<h3>List entities</h3>", html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],  "testcoll")
        self.assertEqual(r.context['type_id'],  type_id)
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), len(expect_entities))
        for eid in range(len(expect_entities)):
            self.assertEqual(entities[eid]['entity_type_id'], expect_entities[eid][0])
            self.assertEqual(entities[eid]['entity_id'], expect_entities[eid][1])
        return

    def _create_ref_type_view(self, view_id="Test_ref_type_view", record_type="test:testtypes"):
        ref_type_view = RecordView.create(self.testcoll, view_id,
            { 'annal:type':         "annal:View"
            , 'annal:uri':          "test:"+view_id
            , 'rdfs:label':         "Test view label"
            , 'rdfs:comment':       "Test view comment"
            , 'annal:record_type':  record_type
            , 'annal:add_field':    True
            , 'annal:view_fields':
              [ { 'annal:field_id':         "_field/Entity_id"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              , { 'annal:field_id':         "_field/Test_ref_type_field"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              ]
            })
        self.assertTrue(ref_type_view is not None)
        return ref_type_view

    def _create_ref_type_field(self, entity_type="test:testtypes"):
        ref_type_field = RecordField.create(self.testcoll, "Test_ref_type_field",
            { "annal:type":                     "annal:Field"
            , "rdfs:label":                     "Type reference"
            , "rdfs:comment":                   "Type reference field comment"
            , "annal:field_render_type":        "Enum_render_type/Enum_choice"
            , "annal:field_value_mode":         "Enum_value_mode/Value_direct"
            , "annal:field_entity_type":        "test:ref_type"
            , "annal:placeholder":              "(ref type field)"
            , "annal:property_uri":             "test:ref_type"
            , "annal:field_placement":          "small:0,12;medium:0,6"
            , "annal:field_ref_type":           "_type/testtypes"
            , "annal:field_ref_restriction":    "[test:turi] subtype %s"%entity_type
            , "annal:field_entity_type":        entity_type
            })
        self.assertTrue(ref_type_field is not None)
        return ref_type_field

    #   -----------------------------------------------------------------------------
    #   Subtype rendering tests
    #   -----------------------------------------------------------------------------

    def test_list_type1(self):
        expect_entities = (
            [ ("testtype1", "entity1") 
            ])
        self._check_entity_list("testtype1", expect_entities)
        return

    def test_list_type2(self):
        expect_entities = (
            [ ("testtype2", "entity2") 
            ])
        self._check_entity_list("testtype2", expect_entities)
        return

    def test_list_types(self):
        expect_entities = (
            [ ("testtype1", "entity1") 
            , ("testtype2", "entity2") 
            , ("testtypes", "entitys") 
            ])
        self._check_entity_list("testtypes", expect_entities)
        return

    def test_select_subtypes(self):
        ref_view  = self._create_ref_type_view()
        ref_field = self._create_ref_type_field()
        u = entitydata_edit_url(
            "new", "testcoll", "ref_type", view_id="Test_ref_type_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "ref_type")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        self.assertEqual(r.context['fields'][0]['field_id'], "Entity_id")
        self.assertEqual(r.context['fields'][1]['field_id'], "Test_ref_type_field")
        baselabel = "Entity testcoll/"
        baseuri   = TestBasePath+"/c/testcoll/d/%s/"
        ref_options = (
            [ FieldChoice(opt, label=baselabel+opt, link=baseuri%opt)
              for opt in ['testtype1/entity1', 'testtype2/entity2', 'testtypes/entitys']
            ])
        self.assertEqual(r.context['fields'][1]['options'], ref_options)
        return

    def test_select_notype_fields(self):
        ref_view  = self._create_ref_type_view(view_id="Test_ref_notype_view", record_type="test:notypes")
        ref_field = self._create_ref_type_field(entity_type="test:sometypes")
        u = entitydata_edit_url(
            "new", "testcoll", "ref_type", view_id="Test_ref_notype_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "ref_type")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        self.assertEqual(r.context['fields'][0]['field_id'], "Entity_id")
        self.assertEqual(r.context['fields'][1]['field_id'], "Test_ref_type_field")
        baselabel = "Entity testcoll/"
        baseuri   = TestBasePath+"/c/testcoll/d/%s/"
        ref_options = []
        self.assertEqual(r.context['fields'][1]['options'], ref_options)
        return

    def test_select_subtype1_fields(self):
        ref_view  = self._create_ref_type_view(view_id="Test_ref_type1_view", record_type="test:testtypes")
        ref_field = self._create_ref_type_field(entity_type="test:testtype1")
        u = entitydata_edit_url(
            "new", "testcoll", "ref_type", view_id="Test_ref_type1_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "ref_type")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        self.assertEqual(r.context['fields'][0]['field_id'], "Entity_id")
        self.assertEqual(r.context['fields'][1]['field_id'], "Test_ref_type_field")
        baselabel = "Entity testcoll/"
        baseuri   = TestBasePath+"/c/testcoll/d/%s/"
        ref_options = (
            [ FieldChoice(opt, label=baselabel+opt, link=baseuri%opt)
              for opt in ['testtype1/entity1']
            ])
        self.assertEqual(r.context['fields'][1]['options'], ref_options)
        return

    def _no_test_test_select_view_subtype_fields(self):
        # @@INCOMPLETE:  this was an attempt to check field selction from the view context,
        #                but abandoned to to complexity of reconstructing bound fields.
        #                NOTE: sitedata tests use Beautifulsoup representation of rendered
        #                page for these tests
        ref_view  = self._create_ref_type_view()
        ref_field = self._create_ref_type_field()
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", "Test_ref_type_view", view_id="View_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check render context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        # Fields
        self.assertEqual(len(r.context['fields']), 6)
        self.assertEqual(r.context['fields'][0]['field_id'], "View_id")
        self.assertEqual(r.context['fields'][1]['field_id'], "View_label")
        self.assertEqual(r.context['fields'][2]['field_id'], "View_comment")
        self.assertEqual(r.context['fields'][3]['field_id'], "View_target_type")
        self.assertEqual(r.context['fields'][4]['field_id'], "View_edit_view")
        self.assertEqual(r.context['fields'][5]['field_id'], "View_fields")
        print repr(r.context['fields'][5])
        baselabel = "Entity testcoll/"
        baseuri   = TestBasePath+"/c/testcoll/d/%s/"
        ref_options = (
            [ FieldChoice(opt, label=baselabel+opt, link=baseuri%opt)
              for opt in ['testtype1/entity1', 'testtype2/entity2', 'testtypes/entitys']
            ])
        self.assertEqual(r.context['fields'][5]['options'], ref_options)
        return

# End.
