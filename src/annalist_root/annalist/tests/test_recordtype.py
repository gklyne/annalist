"""
Tests for RecordType module and view

Note: this module tests for rendering specifically for RecordType values, using
type description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.util                      import valid_id, extract_entity_id
from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist                           import message

from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.entitydata         import EntityData
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.recordview         import RecordView
from annalist.models.recordlist         import RecordList

from annalist.views.recordtypedelete        import RecordTypeDeleteConfirmedView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_test_user,
    context_view_field,
    context_bind_fields,
    check_context_field, check_context_field_value,
    )
from entity_testtypedata    import (
    recordtype_dir,
    recordtype_coll_url, recordtype_url, recordtype_edit_url,
    recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, recordtype_values, recordtype_read_values,
    recordtype_entity_view_context_data, 
    recordtype_entity_view_form_data, recordtype_delete_confirm_form_data
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata    import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from entity_testviewdata    import recordview_url
from entity_testlistdata    import recordlist_url

#   -----------------------------------------------------------------------------
#
#   RecordType tests
#
#   -----------------------------------------------------------------------------

class RecordTypeTest(AnnalistTestCase):
    """
    Tests for RecordType object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
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

    def test_RecordTypeTest(self):
        self.assertEqual(RecordType.__name__, "RecordType", "Check RecordType class name")
        return

    def test_recordtype_init(self):
        t = RecordType(self.testcoll, "testtype")
        u = recordtype_coll_url(self.testsite, coll_id="testcoll", type_id="testtype")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.Type)
        self.assertEqual(t._entityfile,     layout.TYPE_META_FILE)
        self.assertEqual(t._entityref,      layout.COLL_BASE_TYPE_REF%{'id': "testtype"})
        self.assertEqual(t._entityid,       "testtype")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordtype_dir(type_id="testtype"))
        self.assertEqual(t._values,         None)
        return

    def test_recordtype1_data(self):
        t = RecordType(self.testcoll, "type1")
        self.assertEqual(t.get_id(), "type1")
        self.assertEqual(t.get_type_id(), layout.TYPE_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(type_dir)s/type1/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(type_typeid)s/type1/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordtype_create_values(type_id="type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2")
        self.assertEqual(t.get_id(), "type2")
        self.assertEqual(t.get_type_id(), layout.TYPE_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(type_dir)s/type2/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(type_typeid)s/type2/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordtype_create_values(type_id="type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", recordtype_create_values(type_id="type1"))
        td = RecordType.load(self.testcoll, "type1").get_values()
        v  = recordtype_read_values(type_id="type1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_default_data(self):
        t = RecordType.load(self.testcoll, "Default_type", altscope="all")
        self.assertEqual(t.get_id(), "Default_type")
        self.assertIn(
            "/c/_annalist_site/d/%(type_dir)s/Default_type"%self.layout, 
            t.get_url()
            )
        self.assertIn(
            "/c/testcoll/d/%(type_typeid)s/Default_type"%self.layout, 
            t.get_view_url()
            )
        self.assertEqual(t.get_type_id(), layout.TYPE_TYPEID)
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_load_keys(type_uri=True)))
        v = recordtype_read_values(type_id="Default_type")
        v.update(
            { 'rdfs:label':     'Default record'
            , 'annal:uri':      'annal:Default_type'
            })
        v.pop('rdfs:comment', None)
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordTypeEditView tests
#
#   -----------------------------------------------------------------------------

class RecordTypeEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.no_options = [ FieldChoice('', label="(no options)") ]
        self.no_view_id = [ FieldChoice('', label="(view id)") ]
        self.no_list_id = [ FieldChoice('', label="(list id)") ]
        self.view_options = self.no_view_id + get_site_views_linked("testcoll")
        self.list_options = self.no_list_id + get_site_lists_linked("testcoll")
        # For checking Location: header values...
        self.continuation_url = (
            TestHostUri + 
            entitydata_list_type_url(coll_id="testcoll", type_id=layout.TYPE_TYPEID)
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

    def _create_record_type(self, type_id, entity_id="testentity"):
        "Helper function creates record type entry with supplied type_id"
        t = RecordType.create(self.testcoll, type_id, recordtype_create_values(type_id=type_id))
        d = RecordTypeData.create(self.testcoll, type_id, {})
        e = EntityData.create(d, entity_id, {})
        return (t, d, e)

    def _check_record_type_values(self, type_id, 
            update="RecordType", 
            type_uri=None,
            extra_values=None
            ):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_view_url(), TestHostUri + recordtype_url("testcoll", type_id))
        v = recordtype_values(
            type_id=type_id, 
            update=update, 
            type_uri=type_uri
            )
        if extra_values:
            v.update(extra_values)
        # print "t: "+repr(t.get_values())
        # print "v: "+repr(v)
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    def _check_context_fields(self, response, 
            action="",
            type_id="", orig_type_id=None,
            type_label="(?type_label)",
            type_uri="(?type_uri)",
            type_supertype_uris="",
            type_view="Default_view",
            type_list="Default_list"
            ):
        # Common entity attributes
        self.assertEqual(response.context['entity_id'],        type_id)
        self.assertEqual(response.context['orig_id'],          orig_type_id or type_id)
        self.assertEqual(response.context['type_id'],          layout.TYPE_TYPEID)
        self.assertEqual(response.context['orig_type'],        layout.TYPE_TYPEID)
        self.assertEqual(response.context['coll_id'],          'testcoll')
        self.assertEqual(response.context['action'],           action)
        self.assertEqual(response.context['view_id'],          'Type_view')
        # View fields
        self.assertEqual(len(response.context['fields']), 7)
        f0 = context_view_field(response.context, 0, 0)
        f1 = context_view_field(response.context, 1, 0)
        f2 = context_view_field(response.context, 2, 0)
        f3 = context_view_field(response.context, 3, 0)
        f4 = context_view_field(response.context, 4, 0)
        f5 = context_view_field(response.context, 5, 0)
        f6 = context_view_field(response.context, 5, 1)
        # 1st field - Id
        check_context_field(self, f0,
            field_id=           "Type_id",
            field_name=         "entity_id",
            field_label=        "Type Id",
            field_placeholder=  "(type id)",
            field_property_uri= "annal:id",
            field_render_type=  "EntityId",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:EntityRef",
            field_placement=    "small-12 medium-6 columns",
            field_value=        type_id,
            options=            self.no_options
            )
        # 2nd field - Label
        check_context_field(self, f1,
            field_id=           "Type_label",
            field_name=         "Type_label",
            field_label=        "Label",
            field_placeholder=  "(label)",
            field_property_uri= "rdfs:label",
            field_render_type=  "Text",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Text",
            field_placement=    "small-12 columns",
            field_value=        type_label,
            options=            self.no_options
            )
        # 3rd field - comment
        type_comment_placeholder = (
            "(type description)"
            )
        check_context_field(self, f2,
            field_id=           "Type_comment",
            field_name=         "Type_comment",
            field_label=        "Comment",
            field_placeholder=  type_comment_placeholder,
            field_property_uri= "rdfs:comment",
            field_render_type=  "Markdown",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Richtext",
            field_placement=    "small-12 columns",
            options=            self.no_options
            )
        # 4th field - URI
        type_uri_placeholder = (
            "(Type URI)"
            )
        check_context_field(self, f3,
            field_id=           "Type_uri",
            field_name=         "Type_uri",
            field_label=        "Type URI",
            field_placeholder=  type_uri_placeholder,
            field_property_uri= "annal:uri",
            field_render_type=  "Identifier",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Identifier",
            field_value=        type_uri,
            options=            self.no_options
            )
        # 5th field - Supertype URIs
        type_supertype_uris_placeholder = (
            "(Supertype URIs or CURIEs)"
            )
        check_context_field(self, f4,
            field_id=           "Type_supertype_uris",
            field_name=         "Type_supertype_uris",
            field_label=        "Supertype URIs",
            field_placeholder=  type_supertype_uris_placeholder,
            field_property_uri= "annal:supertype_uri",
            field_render_type=  "Group_Seq_Row",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:Type_supertype_uri",
            field_value=        type_supertype_uris,
            options=            self.no_options
            )
        # 6th field - view id
        type_view_id_placeholder = (
            "(view id)"
            )
        check_context_field(self, f5,
            field_id=           "Type_view",
            field_name=         "Type_view",
            field_label=        "Default view",
            field_placeholder=  type_view_id_placeholder,
            field_property_uri= "annal:type_view",
            field_render_type=  "Enum_optional",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:View",
            field_placement=    "small-12 medium-6 columns",
            field_value=        type_view,
            options=            self.view_options
            )
        # 7th field - list id
        type_list_id_placeholder = (
            "(list id)"
            )
        check_context_field(self, f6,
            field_id=           "Type_list",
            field_name=         "Type_list",
            field_label=        "Default list",
            field_placeholder=  type_list_id_placeholder,
            field_property_uri= "annal:type_list",
            field_render_type=  "Enum_optional",
            field_value_mode=   "Value_direct",
            field_value_type=   "annal:List",
            field_placement=    "small-12 medium-6 columns",
            field_value=        type_list,
            options=            self.list_options
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)   #@@
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.TYPE_TYPEID, entity_id="00000001",
            default_label="(New type initial values - label)",
            default_comment=context_view_field(r.context, 2, 0)['field_value'],
            default_label_esc="(New type initial values - label)",
            default_comment_esc=context_view_field(r.context, 2, 0)['field_value'],
            tooltip1=context_view_field(r.context, 0, 0)['field_help'],
            tooltip2=context_view_field(r.context, 1, 0)['field_help'],
            tooltip3=context_view_field(r.context, 2, 0)['field_help'],
            tooltip4=context_view_field(r.context, 3, 0)['field_help'],
            button_save_tip="Save values and return to previous view.",
            button_view_tip="Save values and switch to entity view.",
            button_cancel_tip="Discard unsaved changes and return to previous view.",
            button_view_list_tip=
                "Define initial view and list definitions for the current type.  "+
                "(View and list type information and URI are taken from the current type; "+
                "other fields are taken from the corresponding &#39;_initial_values&#39; record, "+
                "and may be extended or modified later.)"
            )
        formrow1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip1)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Type Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(type id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns" title="%(tooltip2)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Type_label" 
                         placeholder="(label)" 
                         value="%(default_label_esc)s" />
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns" title="%(tooltip3)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Comment</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Type_comment" 
                            class="small-rows-4 medium-rows-8"
                            placeholder="(type description)"
                            >
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns" title="%(tooltip4)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Type URI</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Type_uri" 
                         placeholder="(Type URI)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow5a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow5b = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_left_classes)s">
                  <input type="submit" name="save"      value="Save"   title="%(button_save_tip)s"/>
                  <input type="submit" name="view"      value="View"   title="%(button_view_tip)s"/>
                  <input type="submit" name="cancel"    value="Cancel" title="%(button_cancel_tip)s"/>
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        formrow5c = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_r_med_up_classes)s">
                  <input type="submit" name="Define_view_list" value="Define view+list"
                         title="%(button_view_list_tip)s" />
                  <input type="submit" name="customize" value="Customize"
                         title="Open 'Customize' view for collection 'testcoll'." />
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5a, html=True)
        self.assertContains(r, formrow5b, html=True)
        self.assertContains(r, formrow5c, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.TYPE_TYPEID, entity_id="00000001"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.TYPE_TYPEID)
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            action="new",
            type_id="00000001",
            type_label="(New type initial values - label)",
            type_uri="", type_supertype_uris=""
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.TYPE_TYPEID, entity_id="Default_type"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.TYPE_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Default_type_01")
        self.assertEqual(r.context['orig_id'],          "Default_type_01")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            action="copy",
            type_id="Default_type_01",
            type_label="Default record",
            type_uri="", type_supertype_uris=""
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="notype", view_id="Type_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", layout.TYPE_TYPEID, "notype")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.TYPE_TYPEID, entity_id="Default_type"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.TYPE_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Default_type")
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       "annal:Default_type")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            action="edit",
            type_id="Default_type",
            type_label="Default record",
            type_uri="annal:Default_type", type_supertype_uris=""
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="notype", view_id="Type_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", layout.TYPE_TYPEID, "notype")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(
            type_id="newtype", action="new", update="RecordType",
            type_uri="test:type"
            )
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("newtype", update="RecordType", type_uri="test:type")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(
            type_id="newtype", action="new", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = recordtype_entity_view_form_data(action="new", update="RecordType")
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        self._check_context_fields(r, 
            action="new",
            type_id="", orig_type_id="orig_type_id",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        return

    def test_post_new_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", update="RecordType"
            )
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        self._check_context_fields(r, 
            action="new",
            type_id="!badtype", orig_type_id="orig_type_id",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", update="RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("copytype", update="RecordType")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", cancel="Cancel", update="RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = recordtype_entity_view_form_data(
            action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        self._check_context_fields(r, 
            action="copy",
            type_id="", orig_type_id="orig_type_id",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        return

    def test_post_copy_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="Default_type", action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        self._check_context_fields(r, 
            action="copy",
            type_id="!badtype", orig_type_id="Default_type",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", layout.TYPE_TYPEID, entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("edittype", update="Updated RecordType")
        return

    def test_post_edit_type_new_id(self):
        # Check logic applied when type is renamed
        (t, d1, e1) = self._create_record_type("edittype1", entity_id="typeentity")
        self.assertTrue(RecordType.exists(self.testcoll, "edittype1"))
        self.assertFalse(RecordType.exists(self.testcoll, "edittype2"))
        self.assertTrue(RecordTypeData.exists(self.testcoll, "edittype1"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "edittype2"))
        self.assertTrue(EntityData.exists(d1, "typeentity"))
        self._check_record_type_values("edittype1")
        f = recordtype_entity_view_form_data(
            type_id="edittype2", orig_id="edittype1", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="edittype1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists and old does not
        self.assertFalse(RecordType.exists(self.testcoll, "edittype1"))
        self.assertTrue(RecordType.exists(self.testcoll, "edittype2"))
        self._check_record_type_values("edittype2", update="Updated RecordType")
        # Check that type data directory has been renamed
        self.assertFalse(RecordTypeData.exists(self.testcoll, "edittype1"))
        self.assertTrue(RecordTypeData.exists(self.testcoll, "edittype2"))
        self.assertFalse(EntityData.exists(d1, "typeentity"))
        d2 = RecordTypeData.load(self.testcoll, "edittype2")
        self.assertTrue(EntityData.exists(d2, "typeentity"))
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = recordtype_entity_view_form_data(
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context for re-rendered form
        self._check_context_fields(r, 
            action="edit",
            type_id="", orig_type_id="orig_type_id",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_invalid_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with invalid ID
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="edittype", action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        self._check_context_fields(r, 
            action="edit",
            type_id="!badtype", orig_type_id="edittype",
            type_label=None,
            type_uri=None,
            type_supertype_uris=[],
            )
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    #   -------- define view+list --------

    def test_define_view_list_task(self):
        # Create new type
        self._create_record_type("tasktype")
        self._check_record_type_values("tasktype")
        # Post define view+list
        f = recordtype_entity_view_form_data(
            type_id="tasktype",
            type_uri="test:tasktype",
            task="Define_view_list"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, entity_id="tasktype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # Check content of type, view and list
        common_vals = (
            { 'type_id':      "tasktype"
            , 'type_label':   "RecordType testcoll/tasktype"
            })
        expect_type_values = (
            { 'annal:type':         "annal:Type"
            , 'rdfs:label':         "RecordType testcoll/%(type_id)s"%common_vals
            , 'annal:uri':          "test:%(type_id)s"%common_vals
            , 'annal:type_view':    "_view/%(type_id)s"%common_vals
            , 'annal:type_list':    "_list/%(type_id)s"%common_vals
            })
        expect_view_values = (
            { 'annal:type':         "annal:View"
            , 'rdfs:label':         message.TYPE_VIEW_LABEL%common_vals['type_label']
            , 'annal:record_type':  "test:%(type_id)s"%common_vals
            })
        expect_list_values = (
            { 'annal:type':         "annal:List"
            , 'rdfs:label':         message.TYPE_LIST_LABEL%common_vals['type_label']
            , 'annal:default_view': "_view/%(type_id)s"%common_vals
            , 'annal:default_type': "_type/%(type_id)s"%common_vals
            , 'annal:record_type':  "test:%(type_id)s"%common_vals
            , 'annal:display_type': "_enum_list_type/List"
            , 'annal:list_entity_selector': "'test:%(type_id)s' in [@type]"%common_vals
            })
        self.check_entity_values(layout.TYPE_TYPEID, "%(type_id)s"%common_vals, expect_type_values)
        self.check_entity_values(layout.VIEW_TYPEID, "%(type_id)s"%common_vals, expect_view_values)
        self.check_entity_values(layout.LIST_TYPEID, "%(type_id)s"%common_vals, expect_list_values)
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmRecordTypeDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmRecordTypeDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(RecordTypeDeleteConfirmedView.__name__, "RecordTypeDeleteConfirmedView", "Check RecordTypeDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_type(self):
        t = RecordType.create(self.testcoll, "deletetype", recordtype_create_values("deletetype"))
        self.assertTrue(RecordType.exists(self.testcoll, "deletetype"))
        # Submit positive confirmation
        u = TestHostUri + recordtype_edit_url("delete", "testcoll")
        f = recordtype_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_url("testcoll")+
            r"\?.*info_head=.*$"
            )
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_url("testcoll")+
            r"\?.*info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordType.exists(self.testcoll, "deletetype"))
        return

# End.
