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

from entity_testfielddesc   import get_field_description, get_bound_field
from entity_testutils       import (
    make_message, make_quoted_message,
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_test_user,
    render_select_options,
    render_choice_options,
    context_view_field,
    context_bind_fields,
    check_context_field, check_context_field_value,
    )
from entity_testtypedata    import (
    recordtype_dir,
    recordtype_coll_url, recordtype_url, recordtype_edit_url,
    recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, recordtype_values, recordtype_read_values,
    type_view_form_data, recordtype_delete_confirm_form_data,
    type_view_context_data, 
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
        resetSitedata(scope="collections")
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
        # resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_type(self, type_id, type_uri=None, entity_id="testentity"):
        "Helper function creates record type entry with supplied type_id"
        t = RecordType.create(
            self.testcoll, type_id, 
            recordtype_create_values(
                type_id=type_id,
                type_uri=type_uri
                )
            )
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
            type_ids=None,
            type_label=None,
            type_descr=None,
            type_uri="(?type_uri)",
            type_supertype_uris=[],
            type_view="_view/Default_view",
            type_list="_list/Default_list",
            type_aliases=[],
            record_type="annal:Type",
            update="RecordType",
            continuation_url=None
            ):
        expect_context = type_view_context_data(action=action,
            coll_id="testcoll", type_entity_id=type_id, orig_id=orig_type_id,
            type_ids=type_ids,
            type_label=type_label,
            type_descr=type_descr,
            type_uri=type_uri,
            type_supertype_uris=type_supertype_uris,
            type_view=type_view,
            type_list=type_list,
            type_aliases=type_aliases,
            record_type=record_type,
            update=update,
            continuation_url=continuation_url
            )
        actual_context = context_bind_fields(response.context)
        self.assertEqual(len(response.context['fields']), 7)
        self.assertDictionaryMatch(actual_context, expect_context)
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
            default_label="",
            default_comment=context_view_field(r.context, 2, 0)['field_value'],
            default_label_esc="",
            default_comment_esc=context_view_field(r.context, 2, 0)['field_value'],
            tooltip1=context_view_field(r.context,  0, 0)['field_tooltip'],
            tooltip2=context_view_field(r.context,  1, 0)['field_tooltip'],
            tooltip3=context_view_field(r.context,  2, 0)['field_tooltip'],
            tooltip4=context_view_field(r.context,  3, 0)['field_tooltip'],
            tooltip5=context_view_field(r.context,  4, 0)['field_tooltip'],
            tooltip6col1=context_view_field(r.context, 5, 0)['field_tooltip'],
            tooltip6col2=context_view_field(r.context, 5, 1)['field_tooltip'],
            tooltip7=context_view_field(r.context,  6, 0)['field_tooltip'],
            button_save_tip="Save values and return to previous view.",
            button_view_tip="Save values and switch to entity view.",
            button_cancel_tip="Discard unsaved changes and return to previous view.",
            button_view_list_tip=
                "Define initial view and list definitions for the current type.  "+
                "(View and list type information and URI are taken from the current type; "+
                "other fields are taken from the corresponding &#39;_initial_values&#39; record, "+
                "and may be extended or modified later.)",
            button_subtype_tip=
                "Create a subtype of the current type.  "+
                "(View and list type identifiers are copied from the current type; "+
                "the URI of the current type is inserted as a supertype URI of the new type; "+
                "other fields are taken from the corresponding '_initial_values' record, "+
                "and may be extended or modified later.)"+
                "",
            button_subtype_view_list_tip=
                "Create a subtype of the current type with associated view and list definitions.  "+
                "As far as sensible, details are copied and enhanced from the current type and "+
                "its associated view and list."+
                ""
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
                         placeholder="(Type URI or CURIE)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # Supertypes
        type_supertype_uris_placeholder = (
            "(Supertype URIs or CURIEs)"
            )
        formrow5head = """
            <div class="small-12 columns" title="%(tooltip5)s">
              <div class="grouprow row">
                <div class="group-label small-12 medium-2 columns">
                  <span>Supertype URIs</span>
                </div>
                <div class="small-12 medium-10 columns hide-for-small-only">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <div class="edit-grouprow col-head row">
                        <div class="view-label col-head small-12 columns">
                          <span>Supertype URI</span>
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
                      <input type="submit" name="Type_supertype_uris__remove"
                             value="Remove supertype URI" />
                      <input type="submit" name="Type_supertype_uris__add"
                             value="Add supertype URI" />
                      <input type="submit" name="Type_supertype_uris__up"
                             value="Move &#x2b06;" />
                      <input type="submit" name="Type_supertype_uris__down"
                             value="Move &#x2b07;" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        # Default view, list
        formrow6col1 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip6col1)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default view</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Type_view", "Default view",
                    [ FieldChoice('', label="(view id)") ] + get_site_views_linked("testcoll"),
                    "_view/Default_view", placeholder="(view id)")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6col2 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip6col2)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default list</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "Type_list", "Default list",
                    [ FieldChoice('', label="(list id)") ] + get_site_lists_linked("testcoll"),
                    "_list/Default_list", placeholder="(list id)")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        # Field aliases...
        type_aliases_placeholder = (
            "(field aliases)"
            )
        formrow7head = """
            <div class="small-12 columns" title="%(tooltip7)s">
              <div class="grouprow row">
                <div class="group-label small-12 medium-2 columns">
                  <span>Field aliases</span>
                </div>
                <div class="small-12 medium-10 columns hide-for-small-only">
                  <div class="row">
                    <div class="small-1 columns">
                      &nbsp;
                    </div>
                    <div class="small-11 columns">
                      <div class="edit-grouprow col-head row">
                        <div class="view-label col-head small-12 medium-6 columns">
                          <span>Field alias name</span>
                        </div>
                        <div class="view-label col-head small-12 medium-6 columns">
                          <span>Field alias value</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow7tail = """
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
                      <input type="submit" name="Type_aliases__remove"
                             value="Remove alias" />
                      <input type="submit" name="Type_aliases__add"
                             value="Add alias" />
                      <input type="submit" name="Type_aliases__up"
                             value="Move &#x2b06;" />
                      <input type="submit" name="Type_aliases__down"
                             value="Move &#x2b07;" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        formrow8a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow8b = """
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
        formrow8c = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_r_med_up_classes)s">
                  <input type="submit" name="Define_view_list" 
                         value="Define view+list"
                         title="%(button_view_list_tip)s" />
                  <input type="submit" name="Define_subtype" 
                         value="Define subtype"
                         title="%(button_subtype_tip)s" />
                  <input type="submit" name="customize" 
                         value="Customize"
                         title="Open 'Customize' view for collection 'testcoll'." />
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1,     html=True)
        self.assertContains(r, formrow2,     html=True)
        self.assertContains(r, formrow3,     html=True)
        self.assertContains(r, formrow4,     html=True)
        self.assertContains(r, formrow5head, html=True)
        self.assertContains(r, formrow5tail, html=True)
        self.assertContains(r, formrow6col1, html=True)
        self.assertContains(r, formrow6col2, html=True)
        self.assertContains(r, formrow7head, html=True)
        self.assertContains(r, formrow7tail, html=True)
        self.assertContains(r, formrow8a,    html=True)
        self.assertContains(r, formrow8b,    html=True)
        self.assertContains(r, formrow8c,    html=True)
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
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            action="new",
            type_id="00000001", orig_type_id=None,
            type_label="",
            type_uri="", type_supertype_uris="",
            type_aliases="",
            continuation_url="/xyzzy/"
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
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            action="copy",
            type_id="Default_type_01", orig_type_id="Default_type",
            type_label="Default record",
            type_uri="", type_supertype_uris="",
            type_aliases="",
            continuation_url=""
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
        msg_text  = make_message(message.ENTITY_DOES_NOT_EXIST, 
            type_id=layout.TYPE_TYPEID, 
            id="notype", 
            label=err_label
            )
        self.assertContains(r, "<p>%s</p>"%msg_text, status_code=404)
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
            type_id="Default_type", orig_type_id="Default_type",
            type_label="Default record",
            type_uri="annal:Default_type", type_supertype_uris="",
            type_aliases="",
            continuation_url=""
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
        msg_text  = make_message(message.ENTITY_DOES_NOT_EXIST, 
            type_id=layout.TYPE_TYPEID, 
            id="notype", 
            label=err_label
            )
        self.assertContains(r, "<p>%s</p>"%msg_text, status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = type_view_form_data(action="new", 
            type_entity_id="newtype", type_entity_uri="test:type",
            update="RecordType"
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
        f = type_view_form_data(action="new", 
            type_entity_id="newtype", 
            cancel="Cancel", 
            update="Updated RecordType"
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
        f = type_view_form_data(action="new", update="RecordType")
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context
        self._check_context_fields(r, 
            action="new",
            type_id="",
            type_uri=None,
            type_supertype_uris=[],
            record_type=None
            )
        return

    def test_post_new_type_invalid_id(self):
        f = type_view_form_data(action="new", 
            type_entity_id="!badtype", orig_id="orig_type_id", 
            update="RecordType"
            )
        u = entitydata_edit_url("new", "testcoll", layout.TYPE_TYPEID, view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context
        self._check_context_fields(r, 
            action="new",
            type_id="!badtype", orig_type_id="orig_type_id",
            type_uri=None,
            type_supertype_uris=[],
            )
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = type_view_form_data(action="copy", 
            orig_coll="_annalist_site",
            type_entity_id="copytype", orig_id="Default_type", 
            type_entity_uri=" test:type ",  # Tests space stripping
            update="RecordType"
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
        self._check_record_type_values(
            "copytype", update="RecordType", type_uri="test:type"
            )
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = type_view_form_data(action="copy", 
            type_entity_id="copytype", orig_id="Default_type", 
            cancel="Cancel", 
            update="RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, 
            entity_id="Default_type", view_id="Type_view"
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
        f = type_view_form_data(action="copy", 
            orig_id="Default_type",
            update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, 
            entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context
        self._check_context_fields(r, 
            action="copy",
            type_id="", orig_type_id="Default_type",
            type_uri=None,
            type_supertype_uris=[],
            update="Updated RecordType"
            )
        return

    def test_post_copy_type_invalid_id(self):
        f = type_view_form_data(action="copy", 
            type_entity_id="!badtype", orig_id="Default_type", 
            update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.TYPE_TYPEID, entity_id="Default_type", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context
        self._check_context_fields(r, 
            action="copy",
            type_id="!badtype", orig_type_id="Default_type",
            type_uri=None,
            type_supertype_uris=[],
            update="Updated RecordType"
            )
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = type_view_form_data(action="edit", 
            type_entity_id="edittype", orig_id="edittype", 
            update="Updated RecordType"
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
        f = type_view_form_data(action="edit", 
            type_entity_id="edittype2", orig_id="edittype1", 
            update="Updated RecordType"
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
        f = type_view_form_data(action="edit", 
            type_entity_id="edittype", orig_id="edittype", 
            cancel="Cancel", 
            update="Updated RecordType"
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
        f = type_view_form_data(action="edit", 
            orig_id="edittype",
            update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, 
            entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context for re-rendered form
        self._check_context_fields(r, 
            action="edit",
            type_id="", orig_type_id="edittype",
            type_uri=None,
            type_supertype_uris=[],
            update="Updated RecordType"
            )
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_invalid_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with invalid ID
        f = type_view_form_data(action="edit", 
            type_entity_id="!badtype", orig_id="edittype", 
            update="Updated RecordType"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.TYPE_TYPEID, 
            entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_TYPE_ID,))
        # Test context
        self._check_context_fields(r, 
            action="edit",
            type_id="!badtype", orig_type_id="edittype",
            type_uri=None,
            type_supertype_uris=[],
            update="Updated RecordType"
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
        f = type_view_form_data(
            type_entity_id="tasktype", type_entity_uri="test:tasktype",
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
            { 'type_id':    "tasktype"
            , 'type_label': "RecordType testcoll/_type/tasktype"
            })
        expect_type_values = (
            { 'annal:type':                 "annal:Type"
            , 'rdfs:label':                 "%(type_label)s"%common_vals
            , 'annal:uri':                  "test:%(type_id)s"%common_vals
            , 'annal:type_view':            "_view/%(type_id)s"%common_vals
            , 'annal:type_list':            "_list/%(type_id)s"%common_vals
            })
        expect_view_values = (
            { 'annal:type':                 "annal:View"
            , 'rdfs:label':                 message.TYPE_VIEW_LABEL%common_vals
            , 'annal:view_entity_type':     "test:%(type_id)s"%common_vals
            })
        expect_list_values = (
            { 'annal:type':                 "annal:List"
            , 'rdfs:label':                 message.TYPE_LIST_LABEL%common_vals
            , 'annal:default_view':         "_view/%(type_id)s"%common_vals
            , 'annal:default_type':         "_type/%(type_id)s"%common_vals
            , 'annal:list_entity_type':     "test:%(type_id)s"%common_vals
            , 'annal:display_type':         "_enum_list_type/List"
            , 'annal:list_entity_selector': "'test:%(type_id)s' in [@type]"%common_vals
            })
        self.check_entity_values(layout.TYPE_TYPEID, "%(type_id)s"%common_vals, expect_type_values)
        self.check_entity_values(layout.VIEW_TYPEID, "%(type_id)s"%common_vals, expect_view_values)
        self.check_entity_values(layout.LIST_TYPEID, "%(type_id)s"%common_vals, expect_list_values)
        return

    def test_define_subtype_task(self):
        # Create new type
        self._create_record_type("tasktype", type_uri="test:tasktype")
        self._check_record_type_values("tasktype")
        # Post define subtype
        f = type_view_form_data(
            type_entity_id="tasktype", type_entity_uri="test:tasktype",
            task="Define_subtype"
            )
        u = entitydata_edit_url(
            "view", "testcoll", layout.TYPE_TYPEID, entity_id="tasktype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        subtype_id = "tasktype" + layout.SUFFIX_SUBTYPE
        self.assertIn(
            "/testsite/c/testcoll/v/Type_view/_type/%s/"%(subtype_id,), 
            r['location']
            )
        self.assertEqual(r.content,       "")
        # Check content of type record
        common_vals = (
            { 'coll_id':    "testcoll"
            , 'type_id':    "tasktype"
            , 'subtype_id': subtype_id
            , 'type_label': "RecordType testcoll/_type/tasktype"
            })
        expect_type_values = (
            { 'annal:type':             "annal:Type"
            , 'rdfs:label':             "@@subtype of %(type_label)s"%common_vals
            , 'annal:uri':              "test:%(subtype_id)s"%common_vals
            , 'annal:supertype_uri':    [{'@id': "test:%(type_id)s"%common_vals}]
            , 'annal:type_view':        "_view/Default_view"%common_vals
            , 'annal:type_list':        "_list/Default_list"%common_vals
            })
        self.check_entity_values(layout.TYPE_TYPEID, "%(subtype_id)s"%common_vals, expect_type_values)
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
