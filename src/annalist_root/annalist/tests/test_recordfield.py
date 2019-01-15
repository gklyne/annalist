"""
Tests for RecordField metadata editing view

Note: this module tests for rendering specifically for Field values, and using
field description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import json
import unittest

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

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site,
    init_annalist_test_coll,
    install_annalist_named_coll,
    create_test_coll_inheriting,
    init_annalist_named_test_coll,
    resetSitedata
    )
from .entity_testfielddata import (
    recordfield_dir,
    recordfield_coll_url, recordfield_url,
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    field_view_context_data,
    field_view_form_data
    )
from .entity_testutils import (
    make_message, make_quoted_message,
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
from .entity_testentitydata import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from .entity_testtypedata  import recordtype_url
from .entity_testviewdata  import recordview_url
from .entity_testlistdata  import recordlist_url
from .entity_testgroupdata import recordgroup_url
from .entity_testsitedata  import (
    make_field_choices, no_selection,
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
    def setUpClass(cls):
        super(RecordFieldTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(RecordFieldTest, cls).tearDownClass()
        resetSitedata(scope="collections")
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
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_entity_type=  "annal:Field",
            field_value_type=   "annal:Identifier",
            field_uri=          None,
            field_url=          field_url,
            field_label=        "Value type",
            field_help=         None,
            field_name=         None,
            field_property_uri= "annal:field_value_type",
            field_placement=    None,
            field_default=      "annal:Text",
            field_placeholder=  "(field value type)",
            field_tooltip=      "Type (URI or CURIE) of underlying data",
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
                label="RecordType testcoll/_type/testtype", 
                link=entity_url("testcoll", "_type", "testtype")
                )
            ])
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
    def setUpClass(cls):
        super(RecordFieldEditViewTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(RecordFieldEditViewTest, cls).tearDownClass()
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_view_data(self, field_id, property_uri=None, type_uri=None, update="Field"):
        "Helper function creates view data with supplied field_id"
        e = RecordField.create(self.testcoll, field_id, 
            recordfield_create_values(
                field_id=field_id, 
                property_uri=property_uri, 
                entity_type_uri=type_uri,
                update=update
                )
            )
        return e    

    def _check_field_data_values(self, field_id,
        update="Field", 
        parent=None, 
        property_uri=None,
        type_uri=None
        ):
        "Helper function checks content of form-updated record type entry with supplied field_id"
        self.assertTrue(RecordField.exists(self.testcoll, field_id, altscope="all"))
        e = RecordField.load(self.testcoll, field_id, altscope="all")
        u = recordfield_coll_url(self.testsite, coll_id="testcoll", field_id=field_id)
        self.assertEqual(e.get_id(), field_id)
        self.assertEqual(e.get_url(), u)
        self.assertEqual(e.get_view_url_path(), recordfield_url("testcoll", field_id))
        # print("@@@@ _check_field_data_values property_uri: "+str(property_uri))
        v = recordfield_values(
            field_id=field_id, 
            property_uri=property_uri, 
            entity_type_uri=type_uri,
            update=update
            )
        # print("@@@@ v: "+repr(v))
        check_field_record(self, e,
            field_id=           field_id,
            field_ref=          layout.COLL_BASE_FIELD_REF%{'id': field_id},
            field_types=        ["annal:Field"],
            field_type_id=      layout.FIELD_TYPEID,
            field_render_type=  extract_entity_id(v['annal:field_render_type']),
            field_value_mode=   extract_entity_id(v['annal:field_value_mode']),
            field_entity_type=  v.get('annal:field_entity_type', None),
            field_value_type=   v.get('annal:field_value_type',  None),
            field_uri=          None,
            field_url=          v['annal:url'],
            field_label=        v['rdfs:label'],
            field_help=         v['rdfs:comment'],
            field_name=         None,
            field_property_uri= v.get('annal:property_uri',      None),
            field_placement=    v.get('annal:field_placement',   None),
            field_placeholder=  v.get('annal:placeholder',       None),
            field_tooltip=      v.get('annal:tooltip',           None),
            field_default=      v.get('annal:default_value',     None),
            )
        return e

    def _check_context_fields(self, response, 
            action="edit",
            orig_id=None, 
            continuation_url=None,
            field_id="(?field_id)", 
            field_render_type="(?field_render_type)",
            field_value_mode="Value_direct",
            field_entity_type="",
            field_value_type="(?field_type)",
            field_label="(?field_label)",
            field_property="(?field_property)",
            field_superproperty_uris=[],
            field_placement="(?field_placement)",
            field_placeholder="(?field_placeholder)",
            field_tooltip=None,
            field_default="",
            field_typeref="",
            field_fieldref="",
            field_viewref="",
            field_fields="",
            field_repeat_label_add="Add",
            field_repeat_label_delete="Remove",
            field_restrict=""
            ):
        expect_context = field_view_context_data(
            field_id=field_id, orig_id=orig_id, action=action,
            continuation_url=continuation_url,
            field_render_type=field_render_type,
            field_value_mode=field_value_mode,
            field_entity_type=field_entity_type,
            field_value_type=field_value_type,
            field_label=field_label,
            field_property=field_property,
            field_placement=field_placement,
            field_placeholder=field_placeholder,
            field_tooltip=field_tooltip,
            field_default=field_default,
            field_typeref=field_typeref,
            field_fieldref=field_fieldref,
            field_viewref=field_viewref,
            field_fields=field_fields,
            field_repeat_label_add=field_repeat_label_add,
            field_repeat_label_delete=field_repeat_label_delete,
            field_restrict=field_restrict,
            )
        actual_context = context_bind_fields(response.context)
        self.assertEqual(len(response.context['fields']), 14)
        self.assertDictionaryMatch(actual_context, expect_context)

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
            tooltip1a=context_view_field(r.context,    0, 0).get_field_tooltip(), # Field id
            tooltip1b=context_view_field(r.context,    0, 1).get_field_tooltip(), # Render type
            tooltip2=context_view_field(r.context,     1, 0).get_field_tooltip(), # Label
            tooltip3=context_view_field(r.context,     2, 0).get_field_tooltip(), # Help
            tooltip4a=context_view_field(r.context,    3, 0).get_field_tooltip(), # Property
            tooltip4b=context_view_field(r.context,    3, 1).get_field_tooltip(), # Placement
            tooltip5=context_view_field(r.context,     4, 0).get_field_tooltip(), # Superproperty URIs
            tooltip6=context_view_field(r.context,     5, 0).get_field_tooltip(), # Entity type URI
            tooltip7a=context_view_field(r.context,    6, 0).get_field_tooltip(), # Value type
            tooltip7b=context_view_field(r.context,    6, 1).get_field_tooltip(), # Value mode
            tooltip8a=context_view_field(r.context,    7, 0).get_field_tooltip(), # Typeref
            tooltip8b=context_view_field(r.context,    7, 1).get_field_tooltip(), # Fieldref
            tooltip9=context_view_field(r.context,     8, 0).get_field_tooltip(), # default
            tooltip10=context_view_field(r.context,    9, 0).get_field_tooltip(), # Placeholder
            tooltip11=context_view_field(r.context,   10, 0).get_field_tooltip(), # Tooltip
            tooltip12=context_view_field(r.context,   11, 0).get_field_tooltip(), # Subfields
            tooltip13a=context_view_field(r.context,  12, 0).get_field_tooltip(), # Add
            tooltip13b=context_view_field(r.context,  12, 1).get_field_tooltip(), # Delete
            tooltip14=context_view_field(r.context,   13, 0).get_field_tooltip(), # Restriction
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
        formrow2 = """
            <div class="small-12 columns" title="%(tooltip2)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Field label</span>
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
            <div class="small-12 columns" title="%(tooltip3)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                    <span>Help</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Field_help" class="small-rows-4 medium-rows-8"
                            placeholder="(Field usage commentary or help text)">
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip4a)s">
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
        formrow4col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip4b)s">
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
        formrow5head = """
            <div class="small-12 columns" title="%(tooltip5)s">
              <div class="grouprow row">
                <div class="group-label small-12 medium-2 columns">
                  <span>Superproperty URIs</span>
                </div>
                <div class="small-12 medium-10 columns hide-for-small-only">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <div class="edit-grouprow col-head row">
                        <div class="view-label col-head small-12 columns">
                          <span>Superproperty URI</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow5tail = """
            <div class="small-12 columns">
              <div class="grouprow row">
                <div class="small-12 medium-2 columns">
                  &nbsp;
                </div>
                <div class="group-buttons small-12 medium-10 columns">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <input type="submit" name="Field_superproperty_uris__remove"
                             value="Remove superproperty URI" />
                      <input type="submit" name="Field_superproperty_uris__add"
                             value="Add superproperty URI" />
                      <input type="submit" name="Field_superproperty_uris__up"
                             value="Move &#x2b06;" />
                      <input type="submit" name="Field_superproperty_uris__down"
                             value="Move &#x2b07;" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        formrow6col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip6)s">
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
            """%field_vals(width=6)
        formrow7col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip7a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
              <span>Value type</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_value_type" 
                         placeholder="(field value type)" 
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow7col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip7b)s">
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
        formrow8col1 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip8a)s">
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
        formrow8col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip8b)s">
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
        formrow9 = """
            <div class="small-12 columns" title="%(tooltip9)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default value</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_default" 
                         placeholder="(field default value)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow10 = """
            <div class="small-12 columns" title="%(tooltip10)s">
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
        formrow11 = """
            <div class="small-12 columns" title="%(tooltip11)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                    <span>Tooltip</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Field_tooltip" class="small-rows-4 medium-rows-8"
                            placeholder="(Field usage popup help text)">
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow12h = """
            <div class="small-12 columns" title="%(tooltip12)s">
              <div class="grouprow row">
                <div class="%(group_label_classes)s">
                  <span>Subfields</span>
                </div>
                <div class="%(group_row_head_classes)s">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <div class="edit-grouprow col-head row">
                        <div class="view-label col-head small-12 medium-4 columns">
                          <span>Subfield ref</span>
                        </div>
                        <div class="view-label col-head small-12 medium-4 columns">
                          <span>Subfield URI</span>
                        </div>
                        <div class="view-label col-head small-12 medium-4 columns">
                          <span>Subfield Pos/size</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%field_vals(width=12)

        # formrow12b1c = """
        #     <div class="small-1 columns checkbox-in-edit-padding">
        #       <input type="checkbox" class="select-box right" 
        #              name="View_fields__select_fields"
        #              value="0" />
        #     </div>        
        #     """

        # formrow12b1f1 = ("""
        #     <div class="small-12 medium-4 columns" title="%(tooltip12b1f1)s">
        #       <div class="row show-for-small-only">
        #         <div class="view-label small-12 columns">
        #           <span>Field ref</span>
        #         </div>
        #       </div>
        #       <div class="row view-value-col">
        #         <div class="view-value small-12 columns">
        #         """+
        #           render_select_options(
        #             "View_fields__0__Field_sel", "Field ref",
        #             no_selection("(field reference)") + get_site_default_entity_fields_sorted(),
        #             layout.FIELD_TYPEID+"/Entity_id",
        #             placeholder="(field reference)"
        #             )+
        #         """
        #         </div>
        #       </div>
        #     </div>
        #     """)%field_vals(width=4)

        formrow12t = """
            <div class="small-12 columns">
              <div class="grouprow row">
                <div class="small-12 medium-2 columns">
                  &nbsp;
                </div>
                <div class="group-buttons small-12 medium-10 columns">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <input type="submit" name="Field_fields__remove"
                             value="Remove selected field(s)" />
                      <input type="submit" name="Field_fields__add"
                             value="Add field" />
                      <input type="submit" name="Field_fields__up"
                             value="Move &#x2b06;" />
                      <input type="submit" name="Field_fields__down"
                             value="Move &#x2b07;" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow13col1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip13a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Add value label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_repeat_label_add"
                         placeholder="(Add repeat field(s) button label)"
                         value="Add"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow13col2 = """
            <div class="small-12 medium-6 columns" title="%(tooltip13b)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Remove value label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Field_repeat_label_delete"
                         placeholder="(Remove field(s) button label)"
                         value="Remove"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow14 = """
            <div class="small-12 columns" title="%(tooltip14)s">
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
        self.assertContains(r, formrow1col1,  html=True)    # Id
        self.assertContains(r, formrow1col2,  html=True)    # Render type
        self.assertContains(r, formrow2,      html=True)    # Field label
        self.assertContains(r, formrow3,      html=True)    # Comment/help
        self.assertContains(r, formrow4col1,  html=True)    # Property URI
        self.assertContains(r, formrow4col2,  html=True)    # Placement
        self.assertContains(r, formrow5head,  html=True)    # Superproperty URIs heading
        self.assertContains(r, formrow5tail,  html=True)    # Superproperty URIs buttons
        self.assertContains(r, formrow6col1,  html=True)    # Entity type
        self.assertContains(r, formrow7col1,  html=True)    # Value type
        self.assertContains(r, formrow7col2,  html=True)    # Value mode
        self.assertContains(r, formrow8col1,  html=True)    # Ref type (enum)
        self.assertContains(r, formrow8col2,  html=True)    # Ref field
        self.assertContains(r, formrow9,      html=True)    # Default
        self.assertContains(r, formrow10,     html=True)    # Placeholder
        self.assertContains(r, formrow11,     html=True)    # Tooltip
        self.assertContains(r, formrow12h,    html=True)    # Field list headers
        self.assertContains(r, formrow12t,    html=True)    # Field list tail (buttons)
        self.assertContains(r, formrow13col1, html=True)    # Add field label
        self.assertContains(r, formrow13col2, html=True)    # Delete field label
        self.assertContains(r, formrow14,     html=True)    # Restriction
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
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['action'],           "new")
        # Fields
        self._check_context_fields(r, 
            action="new",
            field_id="00000001",
            field_render_type="_enum_render_type/Text",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="",
            field_value_type="",
            field_property="",
            field_placement="",
            field_placeholder="",
            field_label= default_label("testcoll", layout.FIELD_TYPEID, "00000001"),
            continuation_url="/xyzzy/"
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
        self.assertEqual(r.context['orig_id'],          None)
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
            field_render_type="_enum_render_type/Text",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="annal:Type",
            field_value_type="annal:Text",
            field_label="Label",
            field_placeholder="(label)",
            field_property="rdfs:label",
            field_placement="small:0,12",
            continuation_url="/xyzzy/"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", layout.FIELD_TYPEID, entity_id="fieldnone", view_id="Field_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.check_entity_not_found_response(r, 
            err_msg=make_message(
                message.ENTITY_DOES_NOT_EXIST, 
                type_id=layout.FIELD_TYPEID, 
                id="fieldnone", 
                label=error_label("testcoll", layout.FIELD_TYPEID, "fieldnone")
                ),
            redirect_url="/xyzzy/"
            )
        return

    def test_get_edit_field_fields(self):
        # Render field fields edit form
        u = entitydata_edit_url("edit", 
            "testcoll", layout.FIELD_TYPEID, entity_id="Field_fields", 
            view_id="Field_view"
            )
        # log.info("test_get_edit uri %s"%u)
        r = self.client.get(u+"?continuation_url=/testsite/c/testcoll/d/_field/")
        # log.info("test_get_edit resp %s"%r.content)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        #@@ field_url = collection_entity_view_url(coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id="Type_label")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Field_fields")
        self.assertEqual(r.context['orig_id'],          "Field_fields")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "/testsite/c/testcoll/d/_field/")
        # Fields
        field_fields = (
              [ { 'annal:property_uri':     'annal:field_id'
                , 'annal:field_placement':  'small:0,12;medium:0,4'
                , 'annal:field_id':         '_field/Field_subfield_sel'
                }
              , { 'annal:property_uri':     'annal:property_uri'
                , 'annal:field_placement':  'small:0,12;medium:4,4'
                , 'annal:field_id':         '_field/Field_subfield_property'
                }
              , { 'annal:property_uri':     'annal:field_placement'
                , 'annal:field_placement':  'small:0,12;medium:8,4'
                , 'annal:field_id':         '_field/Field_subfield_placement'
                }
              ])
        self._check_context_fields(r, 
            field_id="Field_fields",
            field_render_type="_enum_render_type/Group_Seq_Row",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="annal:Field",
            field_value_type="annal:Field_list",
            field_label="Subfields",
            field_placeholder="(list of fields)",
            field_property="annal:field_fields",
            field_placement="small:0,12",
            field_fields=field_fields,
            field_repeat_label_add="Add field",
            field_repeat_label_delete="Remove selected field(s)"
            )
        # Separate context check of 'Field_fields' value
        # (Fields are each listed in a row of the subfields description)
        expect_context = field_view_context_data(
            field_id="Field_fields", orig_id="Field_fields", action="edit",
            field_label="Subfields",
            field_value_type="annal:Field_list",
            field_render_type="_enum_render_type/Group_Seq_Row",
            field_value_mode="_enum_value_mode/Value_direct",
            field_property="annal:field_fields",
            field_placement="small:0,12",
            field_placeholder="(list of fields)",
            field_fields=field_fields,
            field_repeat_label_add="Add field",
            field_repeat_label_delete="Remove selected field(s)",
            field_entity_type="annal:Field"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    def test_post_new_field(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = field_view_form_data(
            field_id="newfield", action="new",
            property_uri="test:new_prop",
            )
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check new entity data created
        self._check_field_data_values("newfield", property_uri="test:new_prop")
        return

    def test_post_new_field_no_continuation(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = field_view_form_data(
            field_id="newfield", action="new",
            property_uri="test:new_prop",
            )
        f['continuation_url'] = ""
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check new entity data created
        self._check_field_data_values("newfield", property_uri="test:new_prop")
        return

    def test_post_new_field_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        f = field_view_form_data(field_id="newfield", action="new", cancel="Cancel")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that new record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "newfield"))
        return

    def test_post_new_field_missing_id(self):
        f = field_view_form_data(action="new")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        # Test context
        expect_context = field_view_context_data(action="new")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_new_field_invalid_id(self):
        f = field_view_form_data(field_id="!badfield", orig_id="orig_field_id", action="new")
        u = entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        # Test context
        expect_context = field_view_context_data(
            field_id="!badfield", orig_id="orig_field_id", action="new"
            )
        # print "@@ context %r"%(context_bind_fields(r.context)['fields'][9],)
        # print "@@ context field value %r"%(context_bind_fields(r.context)['fields'][9]['field_value'],)
        # print "@@ expect  %r"%(expect_context['fields'][9],)
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- copy field --------

    def test_post_copy_entity(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = field_view_form_data(
            field_id="copyfield", action="copy",
            property_uri="test:copy_prop",
            )
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that new record type exists
        self._check_field_data_values("copyfield", property_uri="test:copy_prop")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        f = field_view_form_data(
            field_id="copyfield", action="copy", cancel="Cancel"
            )
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that target record type still does not exist
        self.assertFalse(RecordField.exists(self.testcoll, "copyfield"))
        return

    def test_post_copy_entity_missing_id(self):
        f = field_view_form_data(action="copy")
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        expect_context = field_view_context_data(action="copy")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = field_view_form_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        u = entitydata_edit_url("copy", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="Entity_type"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        expect_context = field_view_context_data(
            field_id="!badentity", orig_id="orig_field_id", action="copy"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- edit field --------

    def test_post_edit_entity(self):
        self._create_view_data("editfield")
        self._check_field_data_values("editfield")
        f = field_view_form_data(
            field_id="editfield", action="edit", 
            property_uri="test:edit_prop",
            update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll",
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        self._check_field_data_values("editfield", 
            property_uri="test:edit_prop", 
            update="Updated entity"
            )
        return

    def test_post_edit_entity_new_id(self):
        self._create_view_data("editfieldid1")
        self._check_field_data_values("editfieldid1")
        # Now post edit form submission with different values and new id
        f = field_view_form_data(
            field_id="editfieldid2", orig_id="editfieldid1", action="edit",
            property_uri="test:edit_prop"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfieldid1"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that new record type exists and old does not
        self.assertFalse(RecordField.exists(self.testcoll, "editfieldid1"))
        self._check_field_data_values("editfieldid2", property_uri="test:edit_prop")
        return

    def test_post_edit_entity_cancel(self):
        self._create_view_data("editfield")
        self._check_field_data_values("editfield")
        # Post from cancelled edit form
        f = field_view_form_data(
            field_id="editfield", action="edit", cancel="Cancel", update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", layout.FIELD_TYPEID))
        # Check that target record type still does not exist and unchanged
        self._check_field_data_values("editfield")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_view_data("editfield")
        self._check_field_data_values("editfield")
        # Form post with ID missing
        f = field_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="editfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        # Test context for re-rendered form
        expect_context = field_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_field_data_values("editfield")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_view_data("editfield")
        self._check_field_data_values("editfield")
        # Form post with ID malformed
        f = field_view_form_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="fieldid"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_FIELD_ID))
        # Test context for re-rendered form
        expect_context = field_view_context_data(
            field_id="!badfieldid", orig_id="orig_field_id", action="edit"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_field_data_values("editfield")
        return

    #   -------- define repeat field and group --------

    def test_define_repeat_field_task(self):
        # @@TODO: In due course, this will be deprecated
        # Create new field entity
        self._create_view_data("taskrepeatfield")
        self._check_field_data_values("taskrepeatfield")
        # Post define repeat field
        f = field_view_form_data(
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
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
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
        rpt_field_id  = tgt_field_id + layout.SUFFIX_SEQUENCE
        rpt_field_uri = "%(property_uri)s"%(common_vals) + layout.SUFFIX_SEQUENCE_P
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
        expect_repeat_field_values = (
            { "annal:id":                   rpt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.LIST_FIELD_LABEL%common_vals
            , "annal:field_render_type":    "_enum_render_type/Group_Seq_Row"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Field_list"
            , "annal:property_uri":         rpt_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          message.LIST_FIELD_PLACEHOLDER%common_vals
            , "annal:repeat_label_add":     "Add %(field_label)s"%common_vals
            , "annal:repeat_label_delete":  "Remove %(field_label)s"%common_vals
            , "annal:field_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:property_uri":     tgt_field_uri
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        # self.check_entity_values(layout.GROUP_TYPEID, rpt_group_id, expect_repeat_group_values)
        self.check_entity_values(layout.FIELD_TYPEID, rpt_field_id, expect_repeat_field_values)
        return

    def test_define_list_field_task(self):
        # Create new field entity
        self._create_view_data("tasklistfield")
        self._check_field_data_values("tasklistfield")
        # Post define repeat field
        f = field_view_form_data(
            field_id="tasklistfield",
            field_label="Test list field",
            entity_type="test:list_field",
            property_uri="test:list_prop",
            value_type="annal:Text",
            field_placement="small:0,12",
            task="Define_list_field"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="tasklistfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        # Check content of type, view and list
        common_vals = (
            { 'coll_id':        "testcoll"
            , 'field_id':       "tasklistfield"
            , 'field_label':    "Test list field"
            , 'type_uri':       "test:list_field"
            , 'property_uri':   "test:list_prop"
            , 'field_typeid':   layout.FIELD_TYPEID
            })
        tgt_field_id  = "%(field_id)s"%common_vals
        tgt_field_uri = "%(property_uri)s"%common_vals
        rpt_field_id  = tgt_field_id + layout.SUFFIX_SEQUENCE
        rpt_field_uri = "%(property_uri)s"%(common_vals) + layout.SUFFIX_SEQUENCE_P
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
        expect_list_field_values = (
            { "annal:id":                   rpt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.LIST_FIELD_LABEL%common_vals
            , "annal:field_render_type":    "_enum_render_type/Group_Seq_Row"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Field_list"
            , "annal:property_uri":         rpt_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          message.LIST_FIELD_PLACEHOLDER%common_vals
            , "annal:repeat_label_add":     "Add %(field_label)s"%common_vals
            , "annal:repeat_label_delete":  "Remove %(field_label)s"%common_vals
            , "annal:field_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:property_uri":     tgt_field_uri
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        self.check_entity_values(layout.FIELD_TYPEID, rpt_field_id, expect_list_field_values)
        return

    def test_define_many_field_task(self):
        # Create new field entity
        self._create_view_data("taskmanyfield")
        self._check_field_data_values("taskmanyfield")
        # Post define multi-value field
        f = field_view_form_data(
            field_id="taskmanyfield",
            field_label="Test many field",
            entity_type="test:many_field",
            property_uri="test:many_prop",
            value_type="annal:Text",
            field_placement="small:0,12",
            task="Define_many_field"
            )
        u = entitydata_edit_url("edit", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", entity_id="taskmanyfield"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        # Check content of field
        common_vals = (
            { 'coll_id':        "testcoll"
            , 'field_id':       "taskmanyfield"
            , 'field_label':    "Test many field"
            , 'type_uri':       "test:many_field"
            , 'property_uri':   "test:many_prop"
            , 'field_typeid':   layout.FIELD_TYPEID
            })
        tgt_field_id  = "%(field_id)s"%common_vals
        tgt_field_uri = "%(property_uri)s"%common_vals
        rpt_field_id  = tgt_field_id + layout.SUFFIX_REPEAT
        rpt_field_uri = "%(property_uri)s"%(common_vals)
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
        expect_many_field_values = (
            { "annal:id":                   rpt_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.MANY_FIELD_LABEL%common_vals
            , "annal:field_render_type":    "_enum_render_type/Group_Set_Row"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "%(type_uri)s"%common_vals
            , "annal:property_uri":         rpt_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          message.MANY_FIELD_PLACEHOLDER%common_vals
            , "annal:repeat_label_add":     "Add %(field_label)s"%common_vals
            , "annal:repeat_label_delete":  "Remove %(field_label)s"%common_vals
            , "annal:field_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:property_uri":     "@id"
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        self.check_entity_values(layout.FIELD_TYPEID, rpt_field_id, expect_many_field_values)
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
        # Create new field
        self._create_view_data(common_vals["field_id"])
        self._check_field_data_values(common_vals["field_id"])
        # Post define field reference
        f = field_view_form_data(
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
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id=layout.FIELD_TYPEID, entity_id=common_vals["field_ref_id"], 
            view_id="Field_view"
            )
        self.assertIn(v, r['location'])
        w = "Created%%20reference%%20to%%20field%%20'%(field_id)s'"%common_vals
        self.assertIn(w, r['location'])
        # Check content of type, view and list
        tgt_field_id  = "%(field_id)s"%common_vals
        tgt_field_uri = "%(property_uri)s"%common_vals
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
        expect_ref_field_values = (
            { "annal:id":                   ref_field_id
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 message.FIELD_REF_LABEL%common_vals
            , "annal:field_render_type":    "_enum_render_type/RefMultifield"
            , "annal:field_value_mode":     "_enum_value_mode/Value_entity"
            , "annal:field_entity_type":    "%(type_uri)s"%common_vals
            , "annal:field_value_type":     "annal:Field_list"
            , "annal:property_uri":         ref_field_uri
            , "annal:field_placement":      "small:0,12"
            , "annal:placeholder":          message.FIELD_REF_PLACEHOLDER%common_vals
            , "annal:field_ref_type":       "Default_type"
            , "annal:field_fields":
              [ { "annal:field_id":         "%(field_typeid)s/%(field_id)s"%common_vals
                , "annal:field_placement":  "small:0,12"
                }
              ]
            })
        self.check_entity_values(layout.FIELD_TYPEID, tgt_field_id, expect_field_values)
        self.check_entity_values(layout.FIELD_TYPEID, ref_field_id, expect_ref_field_values)
        return

    def test_define_subproperty_field_task(self):
        common_vals = (
            { 'coll_id':            "testcoll"
            , 'field_id':           "basefield"
            , 'field_label':        "Test subproperty field"
            , 'type_uri':           "test:subprop_field"
            , 'property_uri':       "test:prop"
            , 'subfield_id':        "basefield"+layout.SUFFIX_SUBPROPERTY
            , 'subfield_label':     "@@ Subfield of Field testcoll/_field/basefield (basefield)@@"
            , 'subproperty_uri':    "test:prop_subproperty"
            , 'field_typeid':       layout.FIELD_TYPEID
            })
        # Create new field
        self._create_view_data(
            common_vals["field_id"], 
            property_uri=common_vals["property_uri"], 
            type_uri=common_vals["type_uri"]
            )
        self._check_field_data_values(
            common_vals["field_id"], 
            property_uri=common_vals["property_uri"], 
            type_uri=common_vals["type_uri"]
            )
        # Post define field reference
        f = field_view_form_data(
            field_id=common_vals["field_id"],
            entity_type=common_vals["type_uri"],
            task="Define_subproperty_field"
            )
        u = entitydata_edit_url("view", "testcoll", 
            type_id=layout.FIELD_TYPEID, view_id="Field_view", 
            entity_id=common_vals["field_id"]
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id=layout.FIELD_TYPEID, 
            entity_id=common_vals["subfield_id"], 
            view_id="Field_view"
            )
        self.assertIn(v, r['location'])
        w = "Created%%20field%%20%(subfield_id)s"%common_vals
        self.assertIn(w, r['location'])
        # Check content of new field
        expect_subfield_values = (
            { "annal:id":                   common_vals["subfield_id"]
            , "annal:type":                 "annal:Field"
            , "rdfs:label":                 common_vals["subfield_label"]
            , "annal:field_render_type":    "_enum_render_type/Text"
            , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
            , "annal:field_entity_type":    common_vals["type_uri"]
            , "annal:field_value_type":     "annal:Text"
            , "annal:property_uri":         common_vals["subproperty_uri"]
            , "annal:superproperty_uri":    [ {"@id": common_vals["property_uri"]} ]
            # , "annal:field_placement":      "small:0,12"
            })
        self.check_entity_values(
            layout.FIELD_TYPEID, common_vals["subfield_id"], expect_subfield_values
            )
        return

    #   -------- Test subfields with different selection types --------

    def test_get_sitedata_field_fields_subfield_sel_options(self):
        u = entitydata_edit_url("edit", 
            "testcoll", layout.FIELD_TYPEID, entity_id="Field_fields", view_id="Field_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Field_fields")
        self.assertEqual(r.context['orig_id'],          "Field_fields")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        expect_subfield_choices = (
            [ FieldChoice('', label=u'(reference to a field definition for a subfield)')
            , FieldChoice("_field/Entity_comment",
                label="Comment", 
                link=entity_url("testcoll", "_field", "Entity_comment")
                )
            , FieldChoice("_field/Entity_id",
                label="Id", 
                link=entity_url("testcoll", "_field", "Entity_id")
                )
            , FieldChoice("_field/Entity_label",
                label="Label", 
                link=entity_url("testcoll", "_field", "Entity_label")
                )
            , FieldChoice("_field/Entity_see_also_r",
                label="See also",
                link=entity_url("testcoll", "_field", "Entity_see_also_r")
                )
            , FieldChoice("_field/Entity_type",
                label="Type", 
                link=entity_url("testcoll", "_field", "Entity_type")
                )
            , FieldChoice("_field/Entity_uri",
                label="Entity URI", 
                link=entity_url("testcoll", "_field", "Entity_uri")
                )
            , FieldChoice("_field/Field_subfield_placement", 
                label="Subfield Pos/size", 
                link=entity_url("testcoll", "_field", "Field_subfield_placement")
                )
            , FieldChoice("_field/Field_subfield_property", 
                label="Subfield URI", 
                link=entity_url("testcoll", "_field", "Field_subfield_property")
                )
            , FieldChoice("_field/Field_subfield_sel", 
                label="Subfield ref", 
                link=entity_url("testcoll", "_field", "Field_subfield_sel")
                )
            ])
        field_fields = (
              [ { 'annal:property_uri':     'annal:field_id'
                , 'annal:field_placement':  'small:0,12;medium:0,4'
                , 'annal:field_id':         '_field/Field_subfield_sel'
                }
              , { 'annal:property_uri':     'annal:property_uri'
                , 'annal:field_placement':  'small:0,12;medium:4,4'
                , 'annal:field_id':         '_field/Field_subfield_property'
                }
              , { 'annal:property_uri':     'annal:field_placement'
                , 'annal:field_placement':  'small:0,12;medium:8,4'
                , 'annal:field_id':         '_field/Field_subfield_placement'
                }
              ])
        self._check_context_fields(r, 
            field_id="Field_fields",
            field_render_type="_enum_render_type/Group_Seq_Row",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="annal:Field",
            field_value_type="annal:Field_list",
            field_label="Subfields",
            field_placeholder="(list of fields)",
            field_property="annal:field_fields",
            field_placement="small:0,12",
            field_fields=field_fields,
            field_repeat_label_add="Add field",
            field_repeat_label_delete="Remove selected field(s)",
            continuation_url=""
            )
        # Access and check selectable options for subfield id
        f_Field_fields          = context_view_field(r.context, 11, 0)
        f_subfield_sel_field    = f_Field_fields.description["group_field_descs"][0]
        actual_subfield_choices = list(f_subfield_sel_field["field_choices"].values())
        # print "@@@@@\n%r\n@@@@@"%(actual_subfield_choices,)
        self.assertEqual(actual_subfield_choices, expect_subfield_choices)
        return

    # test_get_sitedata_entity_seealso_r_options
    def test_get_sitedata_entity_seealso_r_subfield_options(self):
        u = entitydata_edit_url("edit", 
            "testcoll", layout.FIELD_TYPEID, entity_id="Entity_see_also_r", view_id="Field_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Entity_see_also_r")
        self.assertEqual(r.context['orig_id'],          "Entity_see_also_r")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        expect_subfield_choices = (
            [ FieldChoice('', label=u'(reference to a field definition for a subfield)')
            , FieldChoice("_field/Entity_comment",
                label="Comment", 
                link=entity_url("testcoll", "_field", "Entity_comment")
                )
            , FieldChoice("_field/Entity_id",
                label="Id", 
                link=entity_url("testcoll", "_field", "Entity_id")
                )
            , FieldChoice("_field/Entity_label",
                label="Label", 
                link=entity_url("testcoll", "_field", "Entity_label")
                )
            , FieldChoice("_field/Entity_see_also", 
                label="Link to further information", 
                link=entity_url("testcoll", "_field", "Entity_see_also")
                )
            , FieldChoice("_field/Entity_see_also_r",
                label="See also",
                link=entity_url("testcoll", "_field", "Entity_see_also_r")
                )
            , FieldChoice("_field/Entity_type",
                label="Type", 
                link=entity_url("testcoll", "_field", "Entity_type")
                )
            , FieldChoice("_field/Entity_uri",
                label="Entity URI", 
                link=entity_url("testcoll", "_field", "Entity_uri")
                )
            ])
        field_fields = (
              [ { 'annal:property_uri':     '@id'
                , 'annal:field_placement':  'small:0,12'
                , 'annal:field_id':         '_field/Entity_see_also'
                }
              ])
        self._check_context_fields(r, 
            field_id="Entity_see_also_r",
            field_render_type="_enum_render_type/Group_Set_Row",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="",
            field_value_type="annal:Entity_see_also_list",
            field_label="See also",
            field_placeholder="(Links to further information)",
            field_property="rdfs:seeAlso",
            field_placement="small:0,12",
            field_fields=field_fields,
            field_repeat_label_add="Add link",
            field_repeat_label_delete="Remove link",
            continuation_url=""
            )
        # Access and check selectable options for subfield id
        f_Field_fields          = context_view_field(r.context, 11, 0)
        f_subfield_sel_field    = f_Field_fields.description["group_field_descs"][0]
        actual_subfield_choices = list(f_subfield_sel_field["field_choices"].values())
        self.assertEqual(actual_subfield_choices, expect_subfield_choices)
        return

    def test_get_rdf_schema_field_domain_r_subfield_sel_options(self):
        rdf_coll = install_annalist_named_coll("RDF_schema_defs")
        testcoll = create_test_coll_inheriting("RDF_schema_defs")
        self.ref_type_options   = (
            self.ref_type_options +
            [ FieldChoice('_type/Datatype', 
                label=u'Data type', 
                link=entity_url("testcoll", "_type", "Datatype")
                )
            , FieldChoice('_type/Property', 
                label=u'Property',  
                link=entity_url("testcoll", "_type", "Property")
                )
            , FieldChoice('_type/Class',    
                label=u'Class',     
                link=entity_url("testcoll", "_type", "Class")
                )
            ])
        u = entitydata_edit_url("edit", 
            "testcoll", layout.FIELD_TYPEID, entity_id="domain_r", view_id="Field_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['entity_id'],        "domain_r")
        self.assertEqual(r.context['orig_id'],          "domain_r")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        expect_domain_choices = (
            [ FieldChoice('', label='(reference to a field definition for a subfield)')
            , FieldChoice("_field/Entity_comment",
                label="Comment", 
                link=entity_url("testcoll", "_field", "Entity_comment")
                )
            , FieldChoice("_field/Entity_id",
                label="Id", 
                link=entity_url("testcoll", "_field", "Entity_id")
                )
            , FieldChoice("_field/Entity_label",
                label="Label", 
                link=entity_url("testcoll", "_field", "Entity_label")
                )
            , FieldChoice("_field/Entity_see_also_r",
                label="See also",
                link=entity_url("testcoll", "_field", "Entity_see_also_r")
                )
            , FieldChoice("_field/Entity_type",
                label="Type", 
                link=entity_url("testcoll", "_field", "Entity_type")
                )
            , FieldChoice("_field/Entity_uri",
                label="Entity URI", 
                link=entity_url("testcoll", "_field", "Entity_uri")
                )
            , FieldChoice("_field/domain", 
                label="Domain", 
                link=entity_url("testcoll", "_field", "domain")
                )
            , FieldChoice("_field/domain_r", 
                label="Domains", 
                link=entity_url("testcoll", "_field", "domain_r")
                )
            , FieldChoice("_field/entity_uri", 
                label="Entity URI", 
                link=entity_url("testcoll", "_field", "entity_uri")
                )
            , FieldChoice("_field/property_uri", 
                label="Property URI", 
                link=entity_url("testcoll", "_field", "property_uri")
                )
            , FieldChoice("_field/range", 
                label="Range", 
                link=entity_url("testcoll", "_field", "range")
                )
            , FieldChoice("_field/range_r", 
                label="Ranges", 
                link=entity_url("testcoll", "_field", "range_r")
                )
            , FieldChoice("_field/subpropertyOf", 
                label="Subproperty of", 
                link=entity_url("testcoll", "_field", "subpropertyOf")
                )
            , FieldChoice("_field/subpropertyOf_r", 
                label="Superproperties", 
                link=entity_url("testcoll", "_field", "subpropertyOf_r")
                )


            ])
        field_fields = (
              [ { 'annal:property_uri':     '@id'
                , 'annal:field_placement':  'small:0,12'
                , 'annal:field_id':         '_field/domain'
                }
              ])
        self._check_context_fields(r, 
            field_id="domain_r",
            field_render_type="_enum_render_type/Group_Set_Row",
            field_value_mode="_enum_value_mode/Value_direct",
            field_entity_type="rdf:Property",
            field_value_type="rdf:Property",
            field_label="Domains",
            field_placeholder="(Property domains)",
            field_property="rdfs:domain",
            field_placement="small:0,12",
            field_fields=field_fields,
            field_repeat_label_add="Add domain",
            field_repeat_label_delete="Remove domain",
            continuation_url=""
            )
        # Access and check selectable options for domain field
        f_Field_fields = context_view_field(r.context, 11, 0)
        f_domain_field = f_Field_fields.description["group_field_descs"][0]
        actual_domain_choices = list(f_domain_field["field_choices"].values())
        self.assertEqual(actual_domain_choices, expect_domain_choices)
        return

# End.
