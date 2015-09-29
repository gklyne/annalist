"""
Tests for RecordField metadata editing view

Note: this module tests for rendering specifically for Field values, and using
field description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import json
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings
from django.db                              import models
from django.http                            import QueryDict
from django.contrib.auth.models             import User
from django.test                            import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                     import Client
        
from annalist.identifiers                   import RDF, RDFS, ANNAL
from annalist                               import layout
from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordfield            import RecordField

from annalist.views.entityedit              import GenericEntityEditView
from annalist.views.form_utils.fieldchoice  import FieldChoice
from annalist.views.fields.render_placement import (
    get_placement_options, get_placement_option_value_dict
    )

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testfielddata           import (
    recordfield_dir,
    recordfield_coll_url, recordfield_url,
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    recordfield_entity_view_context_data, recordfield_entity_view_form_data
    )
from entity_testutils               import (
    collection_entity_view_url,
    collection_create_values,
    render_select_options,
    render_choice_options,
    create_test_user
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testtypedata                import recordtype_url
from entity_testviewdata                import recordview_url
from entity_testlistdata                import recordlist_url
from entity_testgroupdata               import recordgroup_url
from entity_testsitedata            import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_field_groups, get_site_field_groups_sorted, get_site_field_groups_linked, 
    get_site_field_types,  get_site_field_types_sorted,  get_site_field_types_linked ,
    get_site_value_modes,  get_site_value_modes_sorted,  get_site_value_modes_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_fields, get_site_fields_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   RecordField (model) tests
#
#   -----------------------------------------------------------------------------

class RecordFieldTest(AnnalistTestCase):
    """
    Tests for RecordField object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_RecordFieldTest(self):
        self.assertEqual(RecordField.__name__, "RecordField", "Check RecordField class name")
        return

    def test_recordfield_init(self):
        t = RecordField(self.testcoll, "testfield")
        u = recordfield_coll_url(self.testsite, coll_id="testcoll", field_id="testfield")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.Field)
        self.assertEqual(t._entityfile,     layout.FIELD_META_FILE)
        self.assertEqual(t._entityref,      layout.META_FIELD_REF)
        self.assertEqual(t._entityid,       "testfield")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordfield_dir(field_id="testfield"))
        self.assertEqual(t._values,         None)
        return

    def test_recordfield1_data(self):
        t = RecordField(self.testcoll, "field1")
        self.assertEqual(t.get_id(), "field1")
        self.assertEqual(t.get_type_id(), "_field")
        self.assertIn("/c/testcoll/_annalist_collection/fields/field1/", t.get_url())
        t.set_values(recordfield_create_values(field_id="field1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_init_keys()))
        v = recordfield_values(field_id="field1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield2_data(self):
        t = RecordField(self.testcoll, "field2")
        self.assertEqual(t.get_id(), "field2")
        self.assertEqual(t.get_type_id(), "_field")
        self.assertIn("/c/testcoll/_annalist_collection/fields/field2/", t.get_url())
        t.set_values(recordfield_create_values(field_id="field2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_init_keys()))
        v = recordfield_values(field_id="field2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield_create_load(self):
        t  = RecordField.create(self.testcoll, "field1", recordfield_create_values(field_id="field1"))
        td = RecordField.load(self.testcoll, "field1").get_values()
        v  = recordfield_read_values(field_id="field1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield_default_data(self):
        t = RecordField.load(self.testcoll, "Field_type", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Field_type")
        self.assertIn("/c/testcoll/_annalist_collection/fields/Field_type", t.get_url())
        self.assertEqual(t.get_type_id(), "_field")
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_load_keys()))
        field_url = collection_entity_view_url(coll_id="testcoll", type_id="_field", entity_id="Field_type")
        v = recordfield_read_values(field_id="Field_type")
        v.update(
            { '@id':                        "annal:fields/Field_type"
            , 'rdfs:label':                 "Field value type"
            , 'rdfs:comment':               "Type (URI or CURIE) of underlying data that is stored in a field."
            , 'annal:type':                 "annal:Field"
            , 'annal:url':                  field_url
            , 'annal:field_value_type':     "annal:Identifier"
            , 'annal:field_render_type':    "Identifier"
            , 'annal:placeholder':          "(field value type)"
            , 'annal:property_uri':         "annal:field_value_type"
            , 'annal:default_value':        "annal:Text"
            })
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield_create_migrate(self):
        # Test field migration for RecordField values
        vc = recordfield_create_values(field_id="field1")
        vc.update(
            { 'annal:options_typeref':  "test_target_type"
            , 'annal:restrict_values':  "ALL"
            , 'annal:target_field':     "annal:test_target_field"
            })
        t  = RecordField.create(self.testcoll, "field1", vc)
        td = RecordField.load(self.testcoll, "field1").get_values()
        vr  = recordfield_read_values(field_id="field1")
        vr.update(
            { 'annal:field_ref_type':           "test_target_type"
            , 'annal:field_ref_restriction':    "ALL"
            , 'annal:field_ref_field':          "annal:test_target_field"
            })
        self.assertKeysMatch(td, vr)
        self.assertDictionaryMatch(td, vr)
        return

#   -----------------------------------------------------------------------------
#
#   RecordField edit view tests
#
#   -----------------------------------------------------------------------------

class RecordFieldEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.no_options         = [ FieldChoice('', label="(no options)") ]
        self.type_options       = get_site_types_linked("testcoll")
        self.ref_type_options   = (
            [FieldChoice("", label="(no type selected)")] +
            self.type_options +
            [ FieldChoice("_type/testtype", 
                label="RecordType testcoll/testtype", 
                link=entity_url("testcoll", "_type", "testtype")
            )])
        self.view_options       = get_site_views_linked("testcoll")
        self.group_options      = (
            [FieldChoice("", label="(no field group selected)")] +
            get_site_field_groups_linked("testcoll")
            )
        self.render_options     = get_site_field_types_linked("testcoll")
        self.value_mode_options = get_site_value_modes_linked("testcoll")
        self.placement_options  = (
            [FieldChoice("", label="(field position and size)")] + 
            get_placement_options()
            )
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_view_data(self, field_id, update="Field"):
        "Helper function creates view data with supplied field_id"
        e = RecordField.create(self.testcoll, field_id, 
            recordfield_create_values(field_id=field_id, update=update)
            )
        return e    

    def _check_view_data_values(self, field_id, update="Field", parent=None):
        "Helper function checks content of form-updated record type entry with supplied field_id"
        self.assertTrue(RecordField.exists(self.testcoll, field_id, altparent=self.testsite))
        e = RecordField.load(self.testcoll, field_id, altparent=self.testsite)
        u = recordfield_coll_url(self.testsite, coll_id="testcoll", field_id=field_id)
        self.assertEqual(e.get_id(), field_id)
        self.assertEqual(e.get_url(), u)
        self.assertEqual(e.get_view_url_path(), recordfield_url("testcoll", field_id))
        v = recordfield_values(field_id=field_id, update=update)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    def _check_context_fields(self, response, 
            field_id="(?field_id)", 
            field_type="(?field_type)",
            field_render="(?field_type)",
            field_value_mode="Value_direct",
            field_label="(?field_label)",
            field_comment="(?field_comment)",
            field_placeholder="(?field_placeholder)",
            field_property="(?field_property)",
            field_placement="(?field_placement)",
            field_default="",
            field_entity_type="",
            field_typeref="",
            field_fieldref="",
            field_restrict="",
            field_viewref="",
            field_repeat_label_add="",
            field_repeat_label_delete=""
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 17)
        # Field 0: Id
        i = 0
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_id')
        self.assertEqual(r.context['fields'][i]['field_name'],         'entity_id')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "EntityId")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][i]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_id)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 1: Value type
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_type')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_type')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_value_type")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Identifier")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_type)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 2: Label
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_label')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_label')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_label)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 3: comment
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_comment')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_comment')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Markdown")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Richtext")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_comment)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 4: Field_property URI
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_property')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_property')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:property_uri")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Identifier")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_property)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 5: placement
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_placement')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_placement')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_placement")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Placement")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Placement")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_placement)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 6: Render type
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_render')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_render')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_render_type")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Enum_choice")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_render)
        self.assertEqual(set(r.context['fields'][i]['options']),       set(self.render_options))
        # Field 7: Value mode
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_value_mode')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_value_mode')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_value_mode")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Enum_choice")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_value_mode)
        self.assertEqual(set(r.context['fields'][i]['options']),       set(self.value_mode_options))
        # Field 8: type of referenced entity
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_typeref')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_typeref')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_ref_type")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Enum_optional")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_typeref)
        self.assertEqual(r.context['fields'][i]['options'],            self.ref_type_options)
        # Field 9: field of referenced entity
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_fieldref')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_fieldref')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_ref_field")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Identifier")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_fieldref)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 10: Placeholder
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_placeholder')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_placeholder')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:placeholder")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_placeholder)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 11: default value
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_default')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_default')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:default_value")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_default)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 12: enumeration restriction (for select rendering)
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_groupref')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_groupref')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:group_ref")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Enum_optional")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_viewref)
        self.assertEqual(r.context['fields'][i]['options'],            self.group_options)
        # Field 13: enumeration restriction (for select rendering)
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_repeat_label_add')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_repeat_label_add')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:repeat_label_add")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_repeat_label_add)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 14: enumeration restriction (for select rendering)
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_repeat_label_delete')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_repeat_label_delete')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:repeat_label_delete")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_repeat_label_delete)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 15: enumeration type (for select rendering)
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_entity_type')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_entity_type')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_entity_type")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Identifier")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_entity_type)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        # Field 16: enumeration restriction (for select rendering)
        i += 1
        self.assertEqual(r.context['fields'][i]['field_id'],           'Field_restrict')
        self.assertEqual(r.context['fields'][i]['field_name'],         'Field_restrict')
        self.assertEqual(r.context['fields'][i]['field_property_uri'], "annal:field_ref_restriction")
        self.assertEqual(r.context['fields'][i]['field_render_type'],  "Text")
        self.assertEqual(r.context['fields'][i]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][i]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][i]['field_value'],        field_restrict)
        self.assertEqual(r.context['fields'][i]['options'],            self.no_options)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_GenericEntityEditView(self):
        self.assertEqual(GenericEntityEditView.__name__, "GenericEntityEditView", "Check GenericEntityEditView class name")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        field_vals = default_fields(coll_id="testcoll", type_id="_field", entity_id="00000001")
        formrow1col1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(field id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow1col2 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Field value type</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_type" 
                         placeholder="(field value type)" 
                         value="annal:Text"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_label" 
                  placeholder="(field label)"
                  value="%(default_label_esc)s"/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                    <span>Help</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Field_comment" class="small-rows-4 medium-rows-8"
                            placeholder="(field usage commentary or help text)">
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4col1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Property</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_property" 
                         placeholder="(field URI or CURIE)" value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        # log.info("placement_option_value_dict %r"%(get_placement_option_value_dict(),))
        formrow4col2 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Position/size</span>
                </div>
                <div class="%(input_classes)s">
                """+
                render_choice_options(
                  "Field_placement",
                  self.placement_options,
                  "", 
                  select_class="placement-text")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow5col1 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Field render type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_choice_options(
                    "Field_render",
                    get_site_field_types_sorted(),
                    "Enum_render_type/Text")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow5col2 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Value mode</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_choice_options(
                    "Field_value_mode",
                    get_site_value_modes_sorted(),
                    "Enum_value_mode/Value_direct")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6col1 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Refer to type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Field_typeref", "Refer to type",
                    self.ref_type_options,
                    "")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6col2 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Refer to field</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_fieldref" 
                         placeholder="(field URI or CURIE)" value="">
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow7 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Placeholder</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_placeholder"
                         placeholder="(placeholder text)" value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow8 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_default" 
                         placeholder="(field default value)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow9col1 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Field group</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Field_groupref", "Field group",
                    [""] + get_site_field_groups_sorted(),
                    "",
                    placeholder="(no field group selected)")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow10col1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Add fields label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_repeat_label_add"
                         placeholder="(add repeat field(s) button label)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow10col2 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Delete fields label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_repeat_label_delete"
                         placeholder="(delete field(s) button label)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow11 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Entity type</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_entity_type" 
                         placeholder="(type URI/CURIE of entity to which field applies)" 
                         value="" />
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow12 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Value restriction</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_restrict" 
                         placeholder="(enumeration value restriction; e.g. &#39;entity[annal:record_type] subtype [annal:field_entity_type]&#39;)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1col1, html=True)     # Id
        self.assertContains(r, formrow1col2, html=True)     # Value type
        self.assertContains(r, formrow2, html=True)         # Label
        self.assertContains(r, formrow3, html=True)         # Comment/help
        self.assertContains(r, formrow4col1, html=True)     # Property URI
        self.assertContains(r, formrow4col2, html=True)     # Placement
        self.assertContains(r, formrow5col1, html=True)     # Render type
        self.assertContains(r, formrow5col2, html=True)     # Value mode
        self.assertContains(r, formrow6col1, html=True)     # Ref type (enum)
        self.assertContains(r, formrow6col2, html=True)     # Ref field
        self.assertContains(r, formrow7, html=True)         # Placeholder
        self.assertContains(r, formrow8, html=True)         # Default
        self.assertContains(r, formrow9col1, html=True)     # Field group
        self.assertContains(r, formrow10col1, html=True)    # Add field label
        self.assertContains(r, formrow10col2, html=True)    # Delete field label
        self.assertContains(r, formrow11, html=True)        # Entity type
        self.assertContains(r, formrow12, html=True)        # Restriction
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_url = collection_entity_view_url(coll_id="testcoll", type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="00000001",
            field_type="annal:Text",
            field_render="Text",
            field_label=default_label("testcoll", "_field", "00000001"),
            field_comment=default_comment("testcoll", "_field", "00000001"),
            field_placeholder="",
            field_property="",
            field_placement="",
            field_entity_type=""
            )
        return

    def test_get_new_no_continuation(self):
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_url = collection_entity_view_url(coll_id="testcoll", type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "")
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", "_field", entity_id="Type_label", view_id="Field_view")
        # log.info("test_get_edit uri %s"%u)
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        # log.info("test_get_edit resp %s"%r.content)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        #@@ field_url = collection_entity_view_url(coll_id="testcoll", type_id="_field", entity_id="Type_label")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "Type_label")
        self.assertEqual(r.context['orig_id'],          "Type_label")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="Type_label",
            field_type="annal:Text",
            field_render="Text",
            field_label="Label",
            field_comment="Short string used to describe record type when displayed",
            field_placeholder="(label)",
            field_property="rdfs:label",
            field_placement="small:0,12",
            field_entity_type="annal:Type"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", "_field", entity_id="fieldnone", view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.info(r.content)
        err_label = error_label("testcoll", "_field", "fieldnone")
        self.assertContains(r, 
            "<p>Entity %s does not exist</p>"%(err_label), 
            status_code=404
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    def test_post_new_field(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = recordfield_entity_view_form_data(field_id="newfield", action="new")
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_no_continuation(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = recordfield_entity_view_form_data(field_id="newfield", action="new")
        f['continuation_url'] = ""
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = recordfield_entity_view_form_data(field_id="newfield", action="new", cancel="Cancel")
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check that new record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        return

    def test_post_new_field_missing_id(self):
        f = recordfield_entity_view_form_data(action="new")
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = recordfield_entity_view_context_data(action="new")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_field_invalid_id(self):
        f = recordfield_entity_view_form_data(field_id="!badfield", orig_id="orig_field_id", action="new")
        u = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = recordfield_entity_view_context_data(
            field_id="!badfield", orig_id="orig_field_id", action="new"
            )
        # log.info(repr(r.context['fields'][3]))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy field --------

    def test_post_copy_entity(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = recordfield_entity_view_form_data(field_id="copyfield", action="copy")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check that new record type exists
        self._check_view_data_values("copyfield")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = recordfield_entity_view_form_data(field_id="copyfield", action="copy", cancel="Cancel")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check that target record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        return

    def test_post_copy_entity_missing_id(self):
        f = recordfield_entity_view_form_data(action="copy")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        expect_context = recordfield_entity_view_context_data(action="copy")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = recordfield_entity_view_form_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        u = entitydata_edit_url("copy", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        expect_context = recordfield_entity_view_context_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit field --------

    def test_post_edit_entity(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        f = recordfield_entity_view_form_data(
            field_id="editfield", action="edit", update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll",
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        self._check_view_data_values("editfield", update="Updated entity")
        return

    def test_post_edit_entity_new_id(self):
        self._create_view_data("editfieldid1")
        self._check_view_data_values("editfieldid1")
        # Now post edit form submission with different values and new id
        f = recordfield_entity_view_form_data(
            field_id="editfieldid2", orig_id="editfieldid1", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfieldid1"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check that new record type exists and old does not
        self.assertFalse(RecordField.exists(self.testcoll, "editfieldid1"))
        self._check_view_data_values("editfieldid2")
        return

    def test_post_edit_entity_cancel(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Post from cancelled edit form
        f = recordfield_entity_view_form_data(
            field_id="editfield", action="edit", cancel="Cancel", update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_field"))
        # Check that target record type still does not exist and unchanged
        self._check_view_data_values("editfield")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Form post with ID missing
        f = recordfield_entity_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = recordfield_entity_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("editfield")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Form post with ID malformed
        f = recordfield_entity_view_form_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="fieldid"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = recordfield_entity_view_context_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("editfield")
        return

    #   -------- define repeat field and group --------

    def test_define_repeat_field_task(self):
        # Create new type
        self._create_view_data("taskrepeatfield")
        self._check_view_data_values("taskrepeatfield")
        # Post define repeat field
        f = recordfield_entity_view_form_data(
            field_id="taskrepeatfield",
            field_label="Test repeat field",
            type_uri="test:repeat_field",
            property_uri="test:repeat_prop",
            field_placement="small:0,12",
            task="Define_repeat_field"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id="taskrepeatfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # Check content of type, view and list
        common_vals = (
            { 'coll_id':       "testcoll"
            , 'field_id':      "taskrepeatfield"
            , 'field_label':   "Test repeat field"
            , 'type_uri':      "test:repeat_field"
            , 'property_uri':  "test:repeat_prop"
            })
        expect_field_values = (
            { "annal:id":                   "%(field_id)s"%common_vals
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "%(field_label)s"%common_vals
            , "annal:field_render_type":    "Text"
            , "annal:field_value_mode":     "Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:property_uri":         "%(property_uri)s"%common_vals
            , "annal:field_placement":      "small:0,12"
            })
        expect_repeat_group_values = (
            { "annal:id":           "%(field_id)s_repeat"%common_vals
            , "annal:type":         "annal:Field_group"
            , "rdfs:label":         "Repeat field '%(field_label)s'"%common_vals
            , "annal:record_type":  "%(type_uri)s"%common_vals
            , "annal:group_fields":
              [ { "annal:field_id":         "_field/%(field_id)s"%common_vals
                , "annal:property_uri":     "%(property_uri)s"%common_vals
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        expect_repeat_field_values = (
            { "annal:id":                   "%(field_id)s_repeat"%common_vals
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "Repeat field '%(field_label)s'"%common_vals
            , "annal:field_render_type":    "RepeatGroupRow"
            , "annal:field_value_mode":     "Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:property_uri":         "%(property_uri)s_repeat"%common_vals
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          "(Repeat field %(field_label)s)"%common_vals
            , "annal:repeat_label_add":     "Add %(field_label)s"%common_vals
            , "annal:repeat_label_delete":  "Remove %(field_label)s"%common_vals
            })
        self.check_entity_values("_field", "%(field_id)s"%common_vals, expect_field_values)
        self.check_entity_values("_group", "%(field_id)s_repeat"%common_vals, expect_repeat_group_values)
        self.check_entity_values("_field", "%(field_id)s_repeat"%common_vals, expect_repeat_field_values)
        return

    def test_define_field_reference_task(self):
        common_vals = (
            { 'coll_id':       "testcoll"
            , 'field_id':      "taskfieldreference"
            , 'field_ref_id':  "taskfieldreference_ref"
            , 'field_label':   "Test reference field"
            , 'type_uri':      "test:ref_field"
            , 'property_uri':  "test:ref_prop"
            })
        # Create new type
        self._create_view_data(common_vals["field_id"])
        self._check_view_data_values(common_vals["field_id"])
        # Post define field reference
        f = recordfield_entity_view_form_data(
            field_id=common_vals["field_id"],
            field_label=common_vals["field_label"],
            type_uri=common_vals["type_uri"],
            property_uri=common_vals["property_uri"],
            field_placement="small:0,12",
            task="Define_field_ref"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id="_field", view_id="Field_view", entity_id=common_vals["field_id"]
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id="_field", entity_id=common_vals["field_ref_id"], 
            view_id="Field_view"
            )
        self.assertIn(v, r['location'], v)
        w = "Created%%20reference%%20to%%20field%%20%(field_id)s"%common_vals
        self.assertIn(w, r['location'])
        # Check content of type, view and list
        expect_field_values = (
            { "annal:id":                   "%(field_id)s"%common_vals
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "%(field_label)s"%common_vals
            , "annal:field_render_type":    "Text"
            , "annal:field_value_mode":     "Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:property_uri":         "%(property_uri)s"%common_vals
            , "annal:field_placement":      "small:0,12"
            })
        expect_ref_group_values = (
            { "annal:id":           "%(field_id)s_ref"%common_vals
            , "annal:type":         "annal:Field_group"
            , "rdfs:label":         "Reference field '%(field_label)s'"%common_vals
            , "annal:record_type":  "%(type_uri)s"%common_vals
            , "annal:group_fields":
              [ { "annal:field_id":         "_field/%(field_id)s"%common_vals
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        expect_ref_field_values = (
            { "annal:id":                   "%(field_id)s_ref"%common_vals
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "Reference field '%(field_label)s'"%common_vals
            , "annal:field_render_type":    "RefMultifield"
            , "annal:field_value_mode":     "Value_entity"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:property_uri":         "%(property_uri)s_ref"%common_vals
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          "(Reference field %(field_label)s)"%common_vals
            , "annal:field_ref_type":       "Default_type"
            })
        self.check_entity_values("_field", "%(field_id)s"%common_vals, expect_field_values)
        self.check_entity_values("_group", "%(field_id)s_ref"%common_vals, expect_ref_group_values)
        self.check_entity_values("_field", "%(field_id)s_ref"%common_vals, expect_ref_field_values)
        return

# End.
