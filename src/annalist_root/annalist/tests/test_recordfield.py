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
from annalist.views.fields.render_placement import get_placement_options, get_placement_option_value_dict

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
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
from entity_testsitedata            import (
    get_site_types, get_site_types_sorted,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
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
        self.no_options     = ['(no options)']
        self.view_options   = get_site_views_sorted()
        self.group_options  = get_site_field_groups_sorted()
        self.render_options = get_site_field_types_sorted()
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
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
            field_label="(?field_label)",
            field_comment="(?field_comment)",
            field_placeholder="(?field_placeholder)",
            field_property="(?field_property)",
            field_placement="(?field_placement)",
            field_default="",
            field_entity_type="",
            field_typeref="",
            field_restrict="",
            field_viewref="",
            field_repeat_label_add="",
            field_repeat_label_delete=""
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 15)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'], 'Field_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_type'], "EntityId")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], field_id)
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Value type
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:field_value_type")
        self.assertEqual(r.context['fields'][1]['field_render_type'], "Identifier")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][1]['field_value'], field_type)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - Render type
        self.assertEqual(r.context['fields'][2]['field_id'], 'Field_render')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Field_render')
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "annal:field_render_type")
        self.assertEqual(r.context['fields'][2]['field_render_type'], "Enum_choice")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][2]['field_value'], field_render)
        self.assertEqual(set(r.context['fields'][2]['options']), set(self.render_options))
        # 4th field - placement (default)
        self.assertEqual(r.context['fields'][3]['field_id'], 'Field_placement')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Field_placement')
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:field_placement")
        self.assertEqual(r.context['fields'][3]['field_render_type'], "Placement")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Placement")
        self.assertEqual(r.context['fields'][3]['field_value'], field_placement)
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - Label
        self.assertEqual(r.context['fields'][4]['field_id'], 'Field_label')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Field_label')
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][4]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][4]['field_value'], field_label)
        self.assertEqual(r.context['fields'][4]['options'], self.no_options)
        # 6th field - comment
        self.assertEqual(r.context['fields'][5]['field_id'], 'Field_comment')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Field_comment')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][5]['field_render_type'], "Textarea")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][5]['field_value'], field_comment)
        self.assertEqual(r.context['fields'][5]['options'], self.no_options)
        # 7th field - URI
        self.assertEqual(r.context['fields'][6]['field_id'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][6]['field_name'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][6]['field_property_uri'], "annal:placeholder")
        self.assertEqual(r.context['fields'][6]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][6]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][6]['field_value'], field_placeholder)
        self.assertEqual(r.context['fields'][6]['options'], self.no_options)
        # 8th field - Field_property
        self.assertEqual(r.context['fields'][7]['field_id'], 'Field_property')
        self.assertEqual(r.context['fields'][7]['field_name'], 'Field_property')
        self.assertEqual(r.context['fields'][7]['field_property_uri'], "annal:property_uri")
        self.assertEqual(r.context['fields'][7]['field_render_type'], "Identifier")
        self.assertEqual(r.context['fields'][7]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][7]['field_value'], field_property)
        self.assertEqual(r.context['fields'][7]['options'], self.no_options)
        # 9th field - default value
        self.assertEqual(r.context['fields'][8]['field_id'], 'Field_default')
        self.assertEqual(r.context['fields'][8]['field_name'], 'Field_default')
        self.assertEqual(r.context['fields'][8]['field_property_uri'], "annal:default_value")
        self.assertEqual(r.context['fields'][8]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][8]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][8]['field_value'], field_default)
        self.assertEqual(r.context['fields'][8]['options'], self.no_options)
        # 10th field - enumeration type (for select rendering)
        self.assertEqual(r.context['fields'][9]['field_id'], 'Field_entity_type')
        self.assertEqual(r.context['fields'][9]['field_name'], 'Field_entity_type')
        self.assertEqual(r.context['fields'][9]['field_property_uri'], "annal:field_entity_type")
        self.assertEqual(r.context['fields'][9]['field_render_type'], "Identifier")
        self.assertEqual(r.context['fields'][9]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][9]['field_value'], field_entity_type)
        self.assertEqual(r.context['fields'][9]['options'], self.no_options)
        # 10th field - enumeration type (for select rendering)
        self.assertEqual(r.context['fields'][10]['field_id'], 'Field_typeref')
        self.assertEqual(r.context['fields'][10]['field_name'], 'Field_typeref')
        self.assertEqual(r.context['fields'][10]['field_property_uri'], "annal:options_typeref")
        self.assertEqual(r.context['fields'][10]['field_render_type'], "Enum_optional")
        self.assertEqual(r.context['fields'][10]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][10]['field_value'], field_typeref)
        self.assertEqual(r.context['fields'][10]['options'], [""]+get_site_types_sorted()+["testtype"])
        # 11th field - enumeration restriction (for select rendering)
        self.assertEqual(r.context['fields'][11]['field_id'], 'Field_restrict')
        self.assertEqual(r.context['fields'][11]['field_name'], 'Field_restrict')
        self.assertEqual(r.context['fields'][11]['field_property_uri'], "annal:restrict_values")
        self.assertEqual(r.context['fields'][11]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][11]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][11]['field_value'], field_restrict)
        self.assertEqual(r.context['fields'][11]['options'], self.no_options)
        # 12th field - enumeration restriction (for select rendering)
        self.assertEqual(r.context['fields'][12]['field_id'], 'Field_groupref')
        self.assertEqual(r.context['fields'][12]['field_name'], 'Field_groupref')
        self.assertEqual(r.context['fields'][12]['field_property_uri'], "annal:group_ref")
        self.assertEqual(r.context['fields'][12]['field_render_type'], "Enum_optional")
        self.assertEqual(r.context['fields'][12]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][12]['field_value'], field_viewref)
        self.assertEqual(r.context['fields'][12]['options'], [""] + self.group_options)
        # 13th field - enumeration restriction (for select rendering)
        self.assertEqual(r.context['fields'][13]['field_id'], 'Field_repeat_label_add')
        self.assertEqual(r.context['fields'][13]['field_name'], 'Field_repeat_label_add')
        self.assertEqual(r.context['fields'][13]['field_property_uri'], "annal:repeat_label_add")
        self.assertEqual(r.context['fields'][13]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][13]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][13]['field_value'], field_repeat_label_add)
        self.assertEqual(r.context['fields'][13]['options'], self.no_options)
        # 14th field - enumeration restriction (for select rendering)
        self.assertEqual(r.context['fields'][14]['field_id'], 'Field_repeat_label_delete')
        self.assertEqual(r.context['fields'][14]['field_name'], 'Field_repeat_label_delete')
        self.assertEqual(r.context['fields'][14]['field_property_uri'], "annal:repeat_label_delete")
        self.assertEqual(r.context['fields'][14]['field_render_type'], "Text")
        self.assertEqual(r.context['fields'][14]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][14]['field_value'], field_repeat_label_delete)
        self.assertEqual(r.context['fields'][14]['options'], self.no_options)
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
        formrow2 = ("""
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
                    "Text")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow3 = """
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
        formrow4 = """
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
        formrow5 = """
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
        formrow6 = """
            <div class="small-12 columns">
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
            """%field_vals(width=12)
        # log.info("placement_option_value_dict %r"%(get_placement_option_value_dict(),))
        formrow7 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Position/size</span>
                </div>
                <div class="%(input_classes)s">
                """+
                render_choice_options(
                  "Field_placement", # "Position/size",
                  [""] + get_placement_options(),
                  "", 
                  placeholder="(field position and size)", select_class="placement-text",
                  value_dict=get_placement_option_value_dict())+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
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
        formrow9 = ("""
            <div class="small-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Enum type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Field_typeref", "Enum type",
                    [""]+get_site_types_sorted()+["testtype"],
                    "", placeholder="(no type selected)")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow10 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Enum restriction</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_restrict" 
                         placeholder="(enumeration value restriction; e.g. &#39;[annal:field_entity_type] in entity[annal:record_type]&#39;)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow11 = ("""
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
        formrow12col1 = """
            <div class="small-6 columns">
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
        formrow12col2 = """
            <div class="small-6 columns">
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
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1col1, html=True)
        self.assertContains(r, formrow1col2, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        self.assertContains(r, formrow6, html=True)
        self.assertContains(r, formrow7, html=True)
        self.assertContains(r, formrow8, html=True)
        self.assertContains(r, formrow9, html=True)
        self.assertContains(r, formrow10, html=True)
        self.assertContains(r, formrow11, html=True)
        self.assertContains(r, formrow12col1, html=True)
        self.assertContains(r, formrow12col2, html=True)
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
        self.assertEqual(r.context['entity_url'],       field_url)
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
        self.assertEqual(r.context['entity_url'],       field_url)
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
        field_url = collection_entity_view_url(coll_id="testcoll", type_id="_field", entity_id="Type_label")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "Type_label")
        self.assertEqual(r.context['orig_id'],          "Type_label")
        self.assertEqual(r.context['entity_url'],       field_url)
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
            "<p>%s does not exist</p>"%(err_label), 
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

# End.
