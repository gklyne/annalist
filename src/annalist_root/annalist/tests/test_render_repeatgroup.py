"""
Tests for repeat group rendering
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import os
import unittest
import re

from django.test.client                 import Client

from annalist.models.site               import Site
from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField
from annalist.models.entitydata         import EntityData

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site,
    init_annalist_test_coll,
    resetSitedata
    )
from .entity_testfielddesc import (
    get_field_description, get_bound_field
    )
from .entity_testutils import (
    collection_create_values,
    create_test_user,
    context_view_field,
    context_bind_fields,
    context_field_row
    )
from .entity_testtypedata import (
    recordtype_create_values, 
    )
from .entity_testentitydata import (
    entity_url, entitydata_edit_url, 
    specified_view_context_data,
    default_fields
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
        # resetSitedata(scope="collections")
        return


    @classmethod
    def setUpClass(cls):
        super(RepeatGroupRenderingTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(RepeatGroupRenderingTest, cls).tearDownClass()
        resetSitedata(scope="collections")
        return

    # Support methods

    def _create_testview(self):
        testview = RecordView.create(self.testcoll, "testview",
            { 'annal:type':             "annal:View"
            , 'annal:uri':              "test:testtype"
            , 'rdfs:label':             "Test view label"
            , 'rdfs:comment':           "Test view comment"
            , 'annal:view_entity_type': "testtype"
            , 'annal:view_fields':
              [ { 'annal:field_id':         "Entity_id"
                , 'annal:field_placement':  "small:0,12;medium:0,6"
                }
              , { 'annal:field_id':         "Test_repeat_field"
                , 'annal:field_placement':  "small:0,12"
                }
              ]
            })
        self.assertTrue(testview is not None)
        return testview

    def _create_testrepeatfield(self, label_add=None, label_delete=None):
        testrepeatfield = RecordField.create(self.testcoll, "Test_repeat_field",
            { "annal:type":                 "annal:Field"
            , "rdfs:label":                 "Test repeat field label"
            , "rdfs:comment":               "Test repeat field comment"
            , "annal:field_render_type":    "Group_Seq_Row"
            , "annal:field_value_mode":     "Value_direct"
            , "annal:field_value_type":     "annal:Field_group"
            , "annal:field_entity_type":    "test:testtype"
            , "annal:placeholder":          "(test repeat field)"
            , "annal:property_uri":         "test:repeat_fields"
            , "annal:field_placement":      "small:0,12"
            , "annal:field_fields": 
                [ { "annal:field_id":   "Entity_comment" }
                ]
            , "annal:repeat_label_add":     label_add
            , "annal:repeat_label_delete":  label_delete
            })
        self.assertTrue(testrepeatfield is not None)
        return testrepeatfield

    def _create_testentity(self):
        testentity = EntityData.create(self.testdata, "testentity",
            { "annal:type":         "test:testtype"
            , "test:repeat_fields": []
            })
        self.assertTrue(testentity is not None)
        return testentity

    def _create_repeat_group_view_context(self, 
            entity_id=None,
            action=None,
            label_add=None,
            label_delete=None,
            field_value=None,
            continuation_url=None
        ):
        view_fields = (
            [ context_field_row(
                get_bound_field("Entity_id",         entity_id,
                    placement="small:0,12;medium:0,6"
                    ),
                )
            , get_bound_field("Test_repeat_field",   field_value,
                placement="small:0,12",
                group_add_label=label_add,
                group_delete_label=label_delete,
                )
            ])
        context_dict = specified_view_context_data(
            coll_id="testcoll", type_id="testtype", 
            view_id="testview", view_heading="Test view label",
            entity_id=entity_id,
            entity_label="",
            view_fields=view_fields,
            action=action, 
            continuation_url=continuation_url
            )
        return context_dict

    # Tests

    def test_RenderRepeatGroup(self):
        # Create view with repeat-field and repeat-group
        testview        = self._create_testview()
        testrepeatfield = self._create_testrepeatfield(
            label_add="Add group",
            label_delete="Remove group")

        # Render view
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="testview")
        response = self.client.get(u)
        self.assertEqual(response.status_code,   200)
        self.assertEqual(response.reason_phrase, "OK")

        # Check render context
        expect_context = self._create_repeat_group_view_context(
            entity_id="00000001",
            action="new",
            label_add="Add group",
            label_delete="Remove group",
            field_value="",
            continuation_url=""
            )
        actual_context = context_bind_fields(response.context)
        self.assertEqual(len(response.context['fields']), 2)
        self.assertDictionaryMatch(actual_context, expect_context)

        # Test rendered result
        f0 = context_view_field(response.context, 0, 0)
        f1 = context_view_field(response.context, 1, 0)
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
            tooltip1=f0['field_tooltip'],
            )
        formrow1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip1)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                    <input type="text" size="64" name="entity_id" 
                           placeholder="(entity id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2a = """
            <div class="%(group_label_classes)s">
              <span>Test repeat field label</span>
            </div>
            """%field_vals(width=12)
        formrow2b = """
            <div class="%(group_row_head_classes)s">
              <div class="row">
                <div class="small-1 columns">
                  &nbsp;
                </div>
                <div class="small-11 columns">
                  <div class="edit-grouprow col-head row">
                    <div class="%(col_head_classes)s">
                      <span>Comment</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow2c = """
            <div class="%(group_buttons_classes)s">
              <div class="row">
                <div class="small-1 columns">
                  &nbsp;
                </div>
                <div class="small-11 columns">
                  <input type="submit" name="Test_repeat_field__remove" value="Remove group" />
                  <input type="submit" name="Test_repeat_field__add"    value="Add group" />
                  <input type="submit" name="Test_repeat_field__up"     value="Move &#x2b06;" />
                  <input type="submit" name="Test_repeat_field__down"   value="Move &#x2b07;" />
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)
        self.assertContains(response, formrow1,  html=True)
        self.assertContains(response, formrow2a, html=True)
        self.assertContains(response, formrow2b, html=True)
        self.assertContains(response, formrow2c, html=True)
        return

    def test_RenderRepeatGroup_no_labels(self):
        # Create view with repeat-field and repeat-group
        testview        = self._create_testview()
        Test_repeat_field = self._create_testrepeatfield(
            label_add=None,
            label_delete="")

        # Render view
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="testview")
        response = self.client.get(u)
        self.assertEqual(response.status_code,   200)
        self.assertEqual(response.reason_phrase, "OK")

        # Check render context
        expect_context = self._create_repeat_group_view_context(
            entity_id="00000001",
            action="new",
            label_add="Add Test_repeat_field",
            label_delete="Remove Test_repeat_field",
            field_value="",
            continuation_url=""
            )
        actual_context = context_bind_fields(response.context)
        self.assertEqual(len(response.context['fields']), 2)
        self.assertDictionaryMatch(actual_context, expect_context)
        return

    def test_RenderRepeatGroup_view_no_values(self):
        # Create view with repeat-field and repeat-group
        testview        = self._create_testview()
        testrepeatfield = self._create_testrepeatfield(
            label_add="Add group",
            label_delete="Remove group")
        testentity      = self._create_testentity()
        # Render view
        u = entitydata_edit_url(
            "view", "testcoll", "testtype", entity_id="testentity", view_id="testview"
            )
        v = entity_url("testcoll", "testtype", entity_id="testentity")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test rendered result
        cont_uri_param = "?continuation_url="+u
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
            view_url=v, cont_uri_param=cont_uri_param,
            tooltip1="",
            tooltip2="",
            )
        formrow1 = """
            <div class="small-12 medium-6 columns" %(tooltip1)s>
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(view_url)s%(cont_uri_param)s">testentity</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="grouprow row">
              <div class="%(group_label_classes)s">
                <span>Test repeat field label</span>
              </div>
              <div class="group-placeholder %(group_row_body_classes)s">
                <span>(None specified)</span>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content) #@@
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2, html=True)
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
