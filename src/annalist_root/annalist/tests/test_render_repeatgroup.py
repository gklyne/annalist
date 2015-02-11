"""
Tests for repeat group rendering
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
import re
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.test.client                 import Client

from annalist.models.site               import Site
from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.recordgroup        import RecordGroup
from annalist.models.entitydata         import EntityData

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site
from annalist.tests.AnnalistTestCase    import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_create_values, 
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    )

class RepeatGroupRenderingTest(AnnalistTestCase):

    def setUp(self):
        # Set up basic site data
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    # Support methods

    def _create_testview(self):
        testview = RecordView.create(self.testcoll, "testview",
            { 'annal:type':         "annal:View"
            , 'annal:uri':          "test:testtype"
            , 'rdfs:label':         "Test view label"
            , 'rdfs:comment':       "Test view comment"
            , 'annal:record_type':  "testtype"
            , 'annal:add_field':    True
            , 'annal:view_fields':
              [ { 'annal:field_id':         "Entity_id"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              , { 'annal:field_id':         "testrepeatfield"
                , 'annal:field_placement':  "small:0,12"
                }
              ]
            })
        self.assertTrue(testview is not None)
        return testview

    def _create_testrepeatfield(self, label_add=None, label_delete=None):
        testrepeatfield = RecordField.create(self.testcoll, "testrepeatfield",
            { "annal:type":                 "annal:Field"
            , "rdfs:label":                 "Test repeat field label"
            , "rdfs:comment":               "Test repeat field comment"
            , "annal:field_render_type":    "RepeatGroupRow"
            , "annal:field_value_type":     "annal:Field_group"
            , "annal:field_entity_type":    "test:testtype"
            , "annal:placeholder":          "(test repeat field)"
            , "annal:property_uri":         "test:repeat_fields"
            , "annal:field_placement":      "small:0,12"
            , "annal:group_ref":            "testrepeatgroup"
            , "annal:repeat_label_add":     label_add
            , "annal:repeat_label_delete":  label_delete
            })
        self.assertTrue(testrepeatfield is not None)
        return testrepeatfield

    def _create_testrepeatgroup(self):
        testrepeatgroup = RecordGroup.create(self.testcoll, "testrepeatgroup",
            { "annal:type":         "annal:Field_group"
            , "annal:uri":          "test:testrecordgroup"
            , "rdfs:label":         "Test record group label"
            , "rdfs:comment":       "Test record group comment"
            , "annal:record_type":  "test:testtype"
            , "annal:group_fields": 
                [ { "annal:field_id":   "Entity_comment" }
                ]
            })
        self.assertTrue(testrepeatgroup is not None)
        return testrepeatgroup

    # Tests

    def test_RenderRepeatGroup(self):
        # Create view with repeat-field and repeat-group
        testview        = self._create_testview()
        testrepeatfield = self._create_testrepeatfield(
            label_add="Add group",
            label_delete="Remove group")
        testrepeatgroup = self._create_testrepeatgroup()
        # Render view
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="testview")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test rendered values
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['action'],           "new")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_value'], "00000001")
        # 1st field - repeat group
        self.assertEqual(r.context['fields'][1]['field_id'],           "testrepeatfield")
        self.assertEqual(r.context['fields'][1]['field_name'],         "testrepeatfield")
        self.assertEqual(r.context['fields'][1]['field_label'],        "Test repeat field label")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "test:repeat_fields")
        self.assertEqual(r.context['fields'][1]['field_value_type'],   "annal:Field_group")
        self.assertEqual(r.context['fields'][1]['field_group_ref'],    "testrepeatgroup")
        self.assertEqual(r.context['fields'][1]['group_label'],        "Test repeat field label")
        self.assertEqual(r.context['fields'][1]['group_add_label'],    "Add group")
        self.assertEqual(r.context['fields'][1]['group_delete_label'], "Remove group")
        self.assertEqual(len(r.context['fields'][1]['field_value']), 0)
        self.assertEqual(r.context['fields'][1]['field_value'], "") #@@ Really?
        return

    def test_RenderRepeatGroup_no_labels(self):
        # Create view with repeat-field and repeat-group
        testview        = self._create_testview()
        testrepeatfield = self._create_testrepeatfield(
            label_add=None,
            label_delete="")
        testrepeatgroup = self._create_testrepeatgroup()
        # Render view
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="testview")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test rendered values
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['action'],           "new")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_value'], "00000001")
        # 1st field - repeat group
        self.assertEqual(r.context['fields'][1]['field_id'],           "testrepeatfield")
        self.assertEqual(r.context['fields'][1]['field_name'],         "testrepeatfield")
        self.assertEqual(r.context['fields'][1]['field_label'],        "Test repeat field label")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "test:repeat_fields")
        self.assertEqual(r.context['fields'][1]['field_value_type'],   "annal:Field_group")
        self.assertEqual(r.context['fields'][1]['field_group_ref'],    "testrepeatgroup")
        self.assertEqual(r.context['fields'][1]['group_label'],        "Test repeat field label")
        self.assertEqual(r.context['fields'][1]['group_add_label'],    "Add testrepeatfield")
        self.assertEqual(r.context['fields'][1]['group_delete_label'], "Remove testrepeatfield")
        self.assertEqual(len(r.context['fields'][1]['field_value']), 0)
        self.assertEqual(r.context['fields'][1]['field_value'], "") #@@ Really?
        return

# End.

if __name__ == "__main__":
    # import django
    # django.setup()  # Needed for template loader
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()
