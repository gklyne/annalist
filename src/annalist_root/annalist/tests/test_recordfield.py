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
from annalist.util                          import extract_entity_id
from annalist                               import layout
from annalist                               import message

from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordfield            import RecordField

from annalist.views.entityedit              import GenericEntityEditView
from annalist.views.form_utils.fieldchoice  import FieldChoice
from annalist.views.fields.render_placement import (
    get_placement_options, get_placement_option_value_dict
    )

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testfielddata   import (
    recordfield_dir,
    recordfield_coll_url, recordfield_url,
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    recordfield_entity_view_context_data, recordfield_entity_view_form_data
    )
from entity_testutils       import (
    collection_entity_view_url,
    collection_create_values,
    render_select_options,
    render_choice_options,
    create_test_user,
    context_view_field,
    context_bind_fields,
    check_context_field, check_context_field_value,
    check_field_record,
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testtypedata    import recordtype_url
from entity_testviewdata    import recordview_url
from entity_testlistdata    import recordlist_url
from entity_testgroupdata   import recordgroup_url
from entity_testsitedata    import (
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
        init_annalist_test_coll()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.layout = (
            { 'enum_field_placement_id':    layout.ENUM_FIELD_PLACEMENT_ID
            , 'enum_list_type_id':          layout.ENUM_LIST_TYPE_ID
            , 'enum_render_type_id':        layout.ENUM_RENDER_TYPE_ID
            , 'enum_value_type_id':         layout.ENUM_VALUE_TYPE_ID
            , 'enum_value_mode_id':         layout.ENUM_VALUE_MODE_ID
            , 'field_typeid':               layout.FIELD_TYPEID
            , 'group_typeid':               layout.GROUP_TYPEID
            , 'list_typeid':                layout.LIST_TYPEID
            , 'type_typeid':                layout.TYPE_TYPEID
            , 'user_typeid':                layout.USER_TYPEID
            , 'view_typeid':                layout.VIEW_TYPEID
            , 'vocab_typeid':               layout.VOCAB_TYPEID
            , 'field_dir':                  layout.FIELD_DIR
            , 'group_dir':                  layout.GROUP_DIR
            , 'list_dir':                   layout.LIST_DIR
            , 'type_dir':                   layout.TYPE_DIR
            , 'user_dir':                   layout.USER_DIR
            , 'view_dir':                   layout.VIEW_DIR
            , 'vocab_dir':                  layout.VOCAB_DIR
            })
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
        self.assertEqual(t._entityref,      layout.COLL_BASE_FIELD_REF%{'id': "testfield"})
        self.assertEqual(t._entityid,       "testfield")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordfield_dir(field_id="testfield"))
        self.assertEqual(t._values,         None)
        return

    def test_recordfield1_data(self):
        t = RecordField(self.testcoll, "field1")
        self.assertEqual(t.get_id(), "field1")
        self.assertEqual(t.get_type_id(), layout.FIELD_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(field_dir)s/field1/"%self.layout, 
            t.get_url()
            )
        t.set_values(recordfield_create_values(field_id="field1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_init_keys()))
        v = recordfield_values(field_id="field1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordfield2_data(self):
        t = RecordField(self.testcoll, "field2")
        self.assertEqual(t.get_id(), "field2")
        self.assertEqual(t.get_type_id(), layout.FIELD_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(field_dir)s/field2/"%self.layout, 
            t.get_url()
            )
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
        t = RecordField.load(self.testcoll, "Field_value_type", altscope="all")
        self.assertEqual(t.get_id(), "Field_value_type")
        self.assertIn(
            "/c/_annalist_site/d/%(field_dir)s/Field_value_type"%self.layout, 
            t.get_url()
            )
        self.assertIn(
            "/c/testcoll/d/%(field_typeid)s/Field_value_type"%self.layout, 
            t.get_view_url()
            )
        self.assertEqual(t.get_type_id(), layout.FIELD_TYPEID)
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordfield_load_keys(field_uri=True)))
        field_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.FIELD_TYPEID, 
            entity_id="Field_value_type"
            )
        check_field_record(self, td,
            field_id=           "Field_value_type",
            field_ref=          "%(field_typeid)s/Field_value_type"%self.layout,
            field_types=        ["annal:Field"],
            field_type_id=      layout.FIELD_TYPEID,
            field_type=         "annal:Field",
            field_uri=          None,
            field_url=          field_url,
            field_label=        "Value type",
            field_comment=      None,
            field_name=         None,
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_property_uri= "annal:field_value_type",
            field_placement=    None,
            field_entity_type=  None,
            field_value_type=   "annal:Identifier",
            field_placeholder=  "(field value type)",
            field_default=      "annal:Text",
            )
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
        init_annalist_test_coll()
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
        self.assertTrue(RecordField.exists(self.testcoll, field_id, altscope="all"))
        e = RecordField.load(self.testcoll, field_id, altscope="all")
        u = recordfield_coll_url(self.testsite, coll_id="testcoll", field_id=field_id)
        self.assertEqual(e.get_id(), field_id)
        self.assertEqual(e.get_url(), u)
        self.assertEqual(e.get_view_url_path(), recordfield_url("testcoll", field_id))
        v = recordfield_values(field_id=field_id, update=update)
        check_field_record(self, e,
            field_id=           field_id,
            field_ref=          layout.COLL_BASE_FIELD_REF%{'id': field_id},
            field_types=        ["annal:Field"],
            field_type_id=      layout.FIELD_TYPEID,
            field_type=         "annal:Field",
            field_uri=          None,
            field_url=          v['annal:url'],
            field_label=        v['rdfs:label'],
            field_comment=      v['rdfs:comment'],
            field_name=         None,
            field_render_type=  extract_entity_id(v['annal:field_render_type']),
            field_value_mode=   extract_entity_id(v['annal:field_value_mode']),
            field_property_uri= v.get('annal:property_uri',      None),
            field_placement=    v.get('annal:field_placement',   None),
            field_entity_type=  v.get('annal:field_entity_type', None),
            field_value_type=   v.get('annal:field_value_type',  None),
            field_placeholder=  v.get('annal:placeholder',       None),
            field_default=      v.get('annal:default_value',     None),
            )
        return e

    def _check_context_fields(self, response, 
            field_id="(?field_id)", 
            field_type="(?field_type)",
            field_render_type="(?field_render_type)",
            field_value_mode="Value_direct",
            field_label="(?field_label)",
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
        self.assertEqual(len(r.context['fields']), 12)
        f0  = context_view_field(r.context, 0, 0)
        f1  = context_view_field(r.context, 0, 1)
        f2  = context_view_field(r.context, 1, 0)
        f3  = context_view_field(r.context, 1, 1)
        f4  = context_view_field(r.context, 2, 0)
        f5  = context_view_field(r.context, 3, 0)
        f6  = context_view_field(r.context, 4, 0)
        f7  = context_view_field(r.context, 4, 1)
        f8  = context_view_field(r.context, 5, 0)
        f9  = context_view_field(r.context, 5, 1)
        f10 = context_view_field(r.context, 6, 0)
        f11 = context_view_field(r.context, 7, 0)
        f12 = context_view_field(r.context, 8, 0)
        f13 = context_view_field(r.context, 9, 0)
        f14 = context_view_field(r.context, 9, 1)
        f15 = context_view_field(r.context, 10, 0)
        f16 = context_view_field(r.context, 11, 0)
        # Field 0: Id
        check_context_field(self, f0,
            field_id=           "Field_id",
            field_name=         "entity_id",
            field_property_uri= "annal:id",
            field_render_type=  "EntityId",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_placement=    "small-12 medium-6 columns",
            field_value=        field_id,
            options=            self.no_options
            )
        check_context_field(self, f1,
            field_id=           "Field_render_type",
            field_name=         "Field_render_type",
            field_property_uri= "annal:field_render_type",
            field_render_type=  "Enum_choice",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_placement=    "small-12 medium-6 columns",
            field_value=        field_render_type,
            options=            self.render_options
            )
        # Field 2: Value type
        check_context_field(self, f2,
            field_id=           "Field_value_type",
            field_name=         "Field_value_type",
            field_property_uri= "annal:field_value_type",
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Identifier",
            field_value=        field_type,
            options=            self.no_options
            )
        # Field 3: Value mode
        check_context_field(self, f3,
            field_id=           "Field_value_mode",
            field_name=         "Field_value_mode",
            field_property_uri= "annal:field_value_mode",
            field_render_type=  "Enum_choice",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_value=        field_value_mode,
            options=            self.value_mode_options
            )
        # Field 4: Label
        check_context_field(self, f4,
            field_id=           "Field_label",
            field_name=         "Field_label",
            field_property_uri= "rdfs:label",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_label,
            options=            self.no_options
            )
        # Field 5: comment
        check_context_field(self, f5,
            field_id=           "Field_comment",
            field_name=         "Field_comment",
            field_property_uri= "rdfs:comment",
            field_render_type=  "Textarea",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Longtext",
            options=            self.no_options
            )
        # Field 6: Field_property URI
        check_context_field(self, f6,
            field_id=           "Field_property",
            field_name=         "Field_property",
            field_property_uri= "annal:property_uri",
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Identifier",
            field_value=        field_property,
            options=            self.no_options
            )
        # Field 7: placement
        check_context_field(self, f7,
            field_id=           "Field_placement",
            field_name=         "Field_placement",
            field_property_uri= "annal:field_placement",
            field_render_type=  "Placement",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Placement",
            field_value=        field_placement,
            options=            self.no_options
            )
        # Field 8: type of referenced entity
        check_context_field(self, f8,
            field_id=           "Field_typeref",
            field_name=         "Field_typeref",
            field_property_uri= "annal:field_ref_type",
            field_render_type=  "Enum_optional",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_value=        field_typeref,
            options=            self.ref_type_options
            )
        # Field 9: field of referenced entity
        check_context_field(self, f9,
            field_id=           "Field_fieldref",
            field_name=         "Field_fieldref",
            field_property_uri= "annal:field_ref_field",
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Identifier",
            field_value=        field_fieldref,
            options=            self.no_options
            )
        # Field 10: Placeholder
        check_context_field(self, f10,
            field_id=           "Field_placeholder",
            field_name=         "Field_placeholder",
            field_property_uri= "annal:placeholder",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_placeholder,
            options=            self.no_options
            )
        # Field 11: default value
        check_context_field(self, f11,
            field_id=           "Field_default",
            field_name=         "Field_default",
            field_property_uri= "annal:default_value",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_default,
            options=            self.no_options
            )
        # Field 12: enumeration restriction (for select rendering)
        check_context_field(self, f12,
            field_id=           "Field_groupref",
            field_name=         "Field_groupref",
            field_property_uri= "annal:group_ref",
            field_render_type=  "Enum_optional",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_value=        field_viewref,
            options=            self.group_options
            )
        # Field 13: enumeration restriction (for select rendering)
        check_context_field(self, f13,
            field_id=           "Field_repeat_label_add",
            field_name=         "Field_repeat_label_add",
            field_property_uri= "annal:repeat_label_add",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_repeat_label_add,
            options=            self.no_options
            )
        # Field 14: enumeration restriction (for select rendering)
        check_context_field(self, f14,
            field_id=           "Field_repeat_label_delete",
            field_name=         "Field_repeat_label_delete",
            field_property_uri= "annal:repeat_label_delete",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_repeat_label_delete,
            options=            self.no_options
            )
        # Field 15: enumeration type (for select rendering)
        check_context_field(self, f15,
            field_id=           "Field_entity_type",
            field_name=         "Field_entity_type",
            field_property_uri= "annal:field_entity_type",
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Identifier",
            field_value=        field_entity_type,
            options=            self.no_options
            )
        # Field 16: enumeration restriction (for select rendering)
        check_context_field(self, f16,
            field_id=           "Field_restrict",
            field_name=         "Field_restrict",
            field_property_uri= "annal:field_ref_restriction",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_value=        field_restrict,
            options=            self.no_options
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_GenericEntityEditView(self):
        self.assertEqual(GenericEntityEditView.__name__, "GenericEntityEditView", "Check GenericEntityEditView class name")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id="00000001",
            tooltip1a=context_view_field(r.context, 0, 0)['field_help'],
            tooltip1b=context_view_field(r.context, 0, 1)['field_help'],
            tooltip2a=context_view_field(r.context, 1, 0)['field_help'],
            tooltip2b=context_view_field(r.context, 1, 1)['field_help'],
            tooltip3=context_view_field(r.context, 2, 0)['field_help'],
            tooltip4=context_view_field(r.context, 3, 0)['field_help'],
            tooltip5a=context_view_field(r.context, 4, 0)['field_help'],
            tooltip5b=context_view_field(r.context, 4, 1)['field_help'],
            tooltip6a=context_view_field(r.context, 5, 0)['field_help'],
            tooltip6b=context_view_field(r.context, 5, 1)['field_help'],
            tooltip7=context_view_field(r.context, 6, 0)['field_help'],
            tooltip8=context_view_field(r.context, 7, 0)['field_help'],
            tooltip9a=context_view_field(r.context, 8, 0)['field_help'],
            tooltip10a=context_view_field(r.context, 9, 0)['field_help'],
            tooltip10b=context_view_field(r.context, 9, 1)['field_help'],
            tooltip11=context_view_field(r.context, 10, 0)['field_help'],
            tooltip12=context_view_field(r.context, 11, 0)['field_help'],
            )
        formrow1col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip1a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Field Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(field id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow1col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip1b)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Render type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_choice_options(
                    "Field_render_type",
                    get_site_field_types_sorted(),
                    "_enum_render_type/Text",
                    escape_label=True)+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow2col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip2a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
              <span>Value type</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_value_type" 
                         placeholder="(field value type)" 
                         value="annal:Text"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip2b)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Value mode</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_choice_options(
                    "Field_value_mode",
                    get_site_value_modes_sorted(),
                    "_enum_value_mode/Value_direct")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow3 = """
            <div class="small-12 columns" title="%(tooltip3)s">
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
            <div class="small-12 columns" title="%(tooltip4)s">
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

        formrow5col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip5a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Property URI</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_property" 
                         placeholder="(field URI or CURIE)" value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        # log.info("placement_option_value_dict %r"%(get_placement_option_value_dict(),))
        formrow5col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip5b)s">
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
                  select_class="placement-text",
                  placeholder="(field position and size)"
                  )+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6col1 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip6a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Refer to type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Field_typeref", "Refer to type",
                    self.ref_type_options,
                    "",
                    placeholder="(no type selected)"
                    )+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip6b)s">
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
            <div class="small-12 columns" title="%(tooltip7)s">
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
            <div class="small-12 columns" title="%(tooltip8)s">
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
            <div class="small-12 medium-6 columns" title="%(tooltip9a)s">
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
            <div class="small-12 medium-6 columns" title="%(tooltip10a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Add value label</span>
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
            <div class="small-12 medium-6 columns" title="%(tooltip10b)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Delete value label</span>
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
            <div class="small-12 columns" title="%(tooltip11)s">
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
            <div class="small-12 columns" title="%(tooltip12)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Value restriction</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_restrict" 
                         placeholder="(enumeration value restriction)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1col1, html=True)     # Id
        self.assertContains(r, formrow1col2, html=True)     # Render type
        self.assertContains(r, formrow2col1, html=True)     # Value type
        self.assertContains(r, formrow2col2, html=True)     # Value mode
        self.assertContains(r, formrow3, html=True)         # Label
        self.assertContains(r, formrow4, html=True)         # Comment/help
        self.assertContains(r, formrow5col1, html=True)     # Property URI
        self.assertContains(r, formrow5col2, html=True)     # Placement
        self.assertContains(r, formrow6col1, html=True)     # Ref type (enum)
        self.assertContains(r, formrow6col2, html=True)     # Ref field
        self.assertContains(r, formrow7, html=True)         # Placeholder
        self.assertContains(r, formrow8, html=True)         # Default
        self.assertContains(r, formrow9col1, html=True)     # Field group
                                                            # Spacing
        self.assertContains(r, formrow10col1, html=True)    # Add field label
        self.assertContains(r, formrow10col2, html=True)    # Delete field label
        self.assertContains(r, formrow11, html=True)        # Entity type
        self.assertContains(r, formrow12, html=True)        # Restriction
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_url = collection_entity_view_url(coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="00000001",
            field_type="annal:Text",
            field_render_type="Text",
            field_label=default_label("testcoll", layout.FIELD_TYPEID, "00000001"),
            field_placeholder="",
            field_property="",
            field_placement="",
            field_entity_type=""
            )
        return

    def test_get_new_no_continuation(self):
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_url = collection_entity_view_url(coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "")
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", layout.FIELD_TYPEID, entity_id="Type_label", view_id="Field_view")
        # log.info("test_get_edit uri %s"%u)
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        # log.info("test_get_edit resp %s"%r.content)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        #@@ field_url = collection_entity_view_url(coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id="Type_label")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Type_label")
        self.assertEqual(r.context['orig_id'],          "Type_label")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="Type_label",
            field_type="annal:Text",
            field_render_type="Text",
            field_label="Label",
            field_placeholder="(label)",
            field_property="rdfs:label",
            field_placement="small:0,12",
            field_entity_type="annal:Type"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", layout.FIELD_TYPEID, entity_id="fieldnone", view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.info(r.content)
        err_label = error_label("testcoll", layout.FIELD_TYPEID, "fieldnone")
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
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_no_continuation(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = recordfield_entity_view_form_data(field_id="newfield", action="new")
        f['continuation_url'] = ""
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check new entity data created
        self._check_view_data_values("newfield")
        return

    def test_post_new_field_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = recordfield_entity_view_form_data(field_id="newfield", action="new", cancel="Cancel")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that new record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        return

    def test_post_new_field_missing_id(self):
        f = recordfield_entity_view_form_data(action="new")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        # Test context
        expect_context = recordfield_entity_view_context_data(action="new")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_new_field_invalid_id(self):
        f = recordfield_entity_view_form_data(field_id="!badfield", orig_id="orig_field_id", action="new")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        # Test context
        expect_context = recordfield_entity_view_context_data(
            field_id="!badfield", orig_id="orig_field_id", action="new"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- copy field --------

    def test_post_copy_entity(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = recordfield_entity_view_form_data(field_id="copyfield", action="copy")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that new record type exists
        self._check_view_data_values("copyfield")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = recordfield_entity_view_form_data(field_id="copyfield", action="copy", cancel="Cancel")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # NOTE: Location header must be absolute URI
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that target record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        return

    def test_post_copy_entity_missing_id(self):
        f = recordfield_entity_view_form_data(action="copy")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        expect_context = recordfield_entity_view_context_data(action="copy")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = recordfield_entity_view_form_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        expect_context = recordfield_entity_view_context_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- edit field --------

    def test_post_edit_entity(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        f = recordfield_entity_view_form_data(
            field_id="editfield", action="edit", update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll",
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
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
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfieldid1"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
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
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that target record type still does not exist and unchanged
        self._check_view_data_values("editfield")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_view_data("editfield")
        self._check_view_data_values("editfield")
        # Form post with ID missing
        f = recordfield_entity_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordfield_entity_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
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
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="fieldid"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record field identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordfield_entity_view_context_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("editfield")
        return

    #   -------- define repeat field and group --------

    def test_define_repeat_field_task(self):
        # Create new field entity
        self._create_view_data("taskrepeatfield")
        self._check_view_data_values("taskrepeatfield")
        # Post define repeat field
        f = recordfield_entity_view_form_data(
            field_id="taskrepeatfield",
            field_label="Test repeat field",
            entity_type="test:repeat_field",
            property_uri="test:repeat_prop",
            value_type="annal:Text",
            field_placement="small:0,12",
            task="Define_repeat_field"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="taskrepeatfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # Check content of type, view and list
        common_vals = (
            { 'coll_id':        "testcoll"
            , 'field_id':       "taskrepeatfield"
            , 'field_label':    "Test repeat field"
            , 'type_uri':       "test:repeat_field"
            , 'property_uri':   "test:repeat_prop"
            , 'field_typeid':   layout.FIELD_TYPEID
            })
        tgt_field_id  = "%(field_id)s"%common_vals
        tgt_field_uri = "%(property_uri)s"%common_vals
        rpt_group_id  = tgt_field_id + layout.SUFFIX_REPEAT_G
        rpt_field_id  = tgt_field_id + layout.SUFFIX_REPEAT
        rpt_field_uri = "%(property_uri)s"%(common_vals) + layout.SUFFIX_REPEAT_P
        expect_field_values = (
            { "annal:id":                   tgt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "%(field_label)s"%common_vals
            , "annal:field_render_type":    "_enum_render_type/Text"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_value_type":     "annal:Text"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:property_uri":         tgt_field_uri
            , "annal:field_placement":      "small:0,12"
            })
        expect_repeat_group_values = (
            { "annal:id":           rpt_group_id
            , "annal:type":         "annal:Field_group"
            , "rdfs:label":         message.REPEAT_GROUP_LABEL%common_vals['field_label']
            , "annal:record_type":  "%(type_uri)s"%common_vals
            , "annal:group_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:property_uri":     tgt_field_uri
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        expect_repeat_field_values = (
            { "annal:id":                   rpt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.REPEAT_FIELD_LABEL%common_vals['field_label']
            , "annal:field_render_type":    "_enum_render_type/Group_Seq_Row"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Text"
            , "annal:property_uri":         rpt_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          "(Repeat field %(field_label)s)"%common_vals
            , "annal:repeat_label_add":     "Add %(field_label)s"%common_vals
            , "annal:repeat_label_delete":  "Remove %(field_label)s"%common_vals
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        self.check_entity_values(layout.GROUP_TYPEID, rpt_group_id, expect_repeat_group_values)
        self.check_entity_values(layout.FIELD_TYPEID, rpt_field_id, expect_repeat_field_values)
        return

    def test_define_field_reference_task(self):
        common_vals = (
            { 'coll_id':        "testcoll"
            , 'field_id':       "taskfieldreference"
            , 'field_ref_id':   "taskfieldreference"+layout.SUFFIX_MULTI
            , 'field_label':    "Test reference field"
            , 'type_uri':       "test:ref_field"
            , 'property_uri':   "test:ref_prop"
            , 'field_typeid':   layout.FIELD_TYPEID
            })
        # Create new type
        self._create_view_data(common_vals["field_id"])
        self._check_view_data_values(common_vals["field_id"])
        # Post define field reference
        f = recordfield_entity_view_form_data(
            field_id=common_vals["field_id"],
            field_label=common_vals["field_label"],
            entity_type=common_vals["type_uri"],
            property_uri=common_vals["property_uri"],
            value_type="annal:Text",
            field_placement="small:0,12",
            task="Define_field_ref"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id=common_vals["field_id"]
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id=common_vals["field_ref_id"], 
            view_id="Field_view"
            )
        self.assertIn(v, r['location'])
        w = "Created%%20reference%%20to%%20field%%20%(field_id)s"%common_vals
        self.assertIn(w, r['location'])
        # Check content of type, view and list
        tgt_field_id  = "%(field_id)s"%common_vals
        tgt_field_uri = "%(property_uri)s"%common_vals
        ref_group_id  = tgt_field_id + layout.SUFFIX_MULTI_G
        ref_field_id  = tgt_field_id + layout.SUFFIX_MULTI
        ref_field_uri = "%(property_uri)s"%(common_vals) + layout.SUFFIX_MULTI_P
        expect_field_values = (
            { "annal:id":                   tgt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 "%(field_label)s"%common_vals
            , "annal:field_render_type":    "_enum_render_type/Text"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Text"
            , "annal:property_uri":         tgt_field_uri
            , "annal:field_placement":      "small:0,12"
            })
        expect_ref_group_values = (
            { "annal:id":           ref_group_id
            , "annal:type":         "annal:Field_group"
            , "rdfs:label":         message.FIELD_REF_LABEL%common_vals['field_label']
            , "annal:record_type":  "%(type_uri)s"%common_vals
            , "annal:group_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        expect_ref_field_values = (
            { "annal:id":                   ref_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.FIELD_REF_LABEL%common_vals['field_label']
            , "annal:field_render_type":    "_enum_render_type/RefMultifield"
            , "annal:field_value_mode":     "_enum_value_mode/Value_entity"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Text"
            , "annal:property_uri":         ref_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          message.FIELD_REF_PLACEHOLDER%common_vals['field_label']
            , "annal:field_ref_type":       "Default_type"
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        self.check_entity_values(layout.GROUP_TYPEID, ref_group_id, expect_ref_group_values)
        self.check_entity_values(layout.FIELD_TYPEID, ref_field_id, expect_ref_field_values)
        return

# End.
