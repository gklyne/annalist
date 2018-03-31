"""
Tests for RecordList module and view

Note: this module tests for rendering specifically for RecordList values, using
list description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import json
import unittest
import markdown

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
from annalist                               import message
from annalist.models.site                   import Site
from annalist.models.sitedata               import SiteData
from annalist.models.collection             import Collection
from annalist.models.recordlist             import RecordList

from annalist.views.displayinfo             import apply_substitutions
from annalist.views.recordlistdelete        import RecordListDeleteConfirmedView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    make_message, make_quoted_message,
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    render_select_options,
    render_choice_options,
    create_test_user,
    context_view_field,
    context_bind_fields,
    check_context_field, check_context_field_value,
    )
from entity_testlistdata    import (
    recordlist_dir,
    recordlist_coll_url, recordlist_url, recordlist_edit_url,
    recordlist_value_keys, recordlist_load_keys, 
    recordlist_create_values, recordlist_values, recordlist_read_values,
    # recordlist_entity_view_context_data, recordlist_entity_view_form_data, 
    list_view_context_data, list_view_form_data, 
    recordlist_delete_confirm_form_data
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, 
    entitydata_list_all_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted, get_site_list_types_linked,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   RecordList tests
#
#   -----------------------------------------------------------------------------

class RecordListTest(AnnalistTestCase):
    """
    Tests for RecordList object interface
    """

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
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

    def test_RecordListTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_recordlist_init(self):
        t = RecordList(self.testcoll, "testlist")
        u = recordlist_coll_url(self.testsite, coll_id="testcoll", list_id="testlist")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.List)
        self.assertEqual(t._entityfile,     layout.LIST_META_FILE)
        self.assertEqual(t._entityref,      layout.COLL_BASE_LIST_REF%{'id': "testlist"})
        self.assertEqual(t._entityid,       "testlist")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordlist_dir(list_id="testlist"))
        self.assertEqual(t._values,         None)
        return

    def test_recordlist1_data(self):
        t = RecordList(self.testcoll, "list1")
        self.assertEqual(t.get_id(), "list1")
        self.assertEqual(t.get_type_id(), layout.LIST_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(list_dir)s/list1/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(list_typeid)s/list1/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordlist_create_values(list_id="list1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordlist_value_keys()))
        v = recordlist_values(list_id="list1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordlist2_data(self):
        t = RecordList(self.testcoll, "list2")
        self.assertEqual(t.get_id(), "list2")
        self.assertEqual(t.get_type_id(), layout.LIST_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(list_dir)s/list2/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(list_typeid)s/list2/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordlist_create_values(list_id="list2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordlist_value_keys()))
        v = recordlist_values(list_id="list2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordlist_create_load(self):
        t  = RecordList.create(self.testcoll, "list1", recordlist_create_values(list_id="list1"))
        td = RecordList.load(self.testcoll, "list1").get_values()
        v  = recordlist_read_values(list_id="list1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordlist_default_data(self):
        t = RecordList.load(self.testcoll, "Default_list", altscope="all")
        self.assertEqual(t.get_id(), "Default_list")
        self.assertIn(
            "/c/_annalist_site/d/%(list_dir)s/Default_list"%self.layout, 
            t.get_url()
            )
        self.assertIn(
            "/c/testcoll/d/%(list_typeid)s/Default_list"%self.layout, 
            t.get_view_url()
            )
        self.assertEqual(t.get_type_id(), layout.LIST_TYPEID)
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordlist_load_keys(list_uri=True)))
        v = recordlist_read_values(list_id="Default_list")
        v.update(
            { '@id':            "%(list_typeid)s/Default_list"%self.layout
            , 'rdfs:label':     "List entities"
            , 'annal:uri':      "annal:display/Default_list"
            })
        v.pop('rdfs:comment', None)
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordList edit view tests
#
#   -----------------------------------------------------------------------------

class RecordListEditViewTest(AnnalistTestCase):
    """
    Tests for record view edit views
    """

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection.create(
            self.testsite, "testcoll", collection_create_values("testcoll")
            )
        self.continuation_path = entitydata_list_type_url(
            coll_id="testcoll", type_id=layout.LIST_TYPEID
            )
        self.continuation_url  = TestHostUri + self.continuation_path
        self.no_options = [ FieldChoice('', label="(no options)") ]
        self.type_options   = get_site_types_linked("testcoll")
        self.type_options.append(
            FieldChoice("_type/testtype", 
                label="RecordType testcoll/_type/testtype", 
                link=entity_url("testcoll", "_type", "testtype")
            ))
        self.view_options   = get_site_views_linked("testcoll")
        self.list_options   = get_site_lists_linked("testcoll")
        self.list_type_opts = get_site_list_types_sorted()
        #@@ self.list_type_opts = get_site_list_types_linked("testcoll")
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

    def _create_list_view(self, list_id):
        "Helper function creates record view entry with supplied list_id"
        t = RecordList.create(self.testcoll, list_id, recordlist_create_values(list_id=list_id))
        return t

    def _check_list_view_values(self, 
        list_id, list_uri=None, update="RecordList", num_fields=4
        ):
        "Helper function checks content of record view entry with supplied list_id"
        self.assertTrue(RecordList.exists(self.testcoll, list_id))
        t = RecordList.load(self.testcoll, list_id)
        self.assertEqual(t.get_id(), list_id)
        self.assertEqual(t.get_view_url(), TestHostUri + recordlist_url("testcoll", list_id))
        v = recordlist_values(list_id=list_id, list_uri=list_uri, update=update)
        if num_fields == 0:
            v['annal:list_fields'] = []
        # log.info("RecordList.load values: %r"%(t.get_values(),))
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    # Check context value used for displaying list view
    def _check_list_view_context_fields(self, response, 
            action=None,
            list_id="(?list_id)", orig_list_id=None,
            list_uri=None,
            list_type="_enum_list_type/List",
            list_label=None,
            list_descr=None,
            list_default_type="_type/Default_type",
            list_default_view="_view/Default_view",
            list_entity_selector="ALL",
            list_entity_type="",
            list_fields=None,
            num_fields=0,
            update="RecordList",
            continuation_url=None
            ):
        expect_context = list_view_context_data(
            coll_id="testcoll", list_id=list_id, orig_id=orig_list_id,
            action=action,
            list_uri=list_uri,
            list_type=list_type,
            list_label=list_label,
            list_descr=list_descr,
            list_default_type=list_default_type,
            list_default_view=list_default_view,
            list_entity_selector=list_entity_selector,
            list_entity_type=list_entity_type,
            list_fields=list_fields,
            num_fields=num_fields,
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

    def test_get_new_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.LIST_TYPEID, entity_id="00000001",
            default_comment=context_view_field(r.context, 2, 0)['field_value'],
            tooltip1a=context_view_field(r.context, 0, 0)['field_tooltip'],
            tooltip1b=context_view_field(r.context, 0, 1)['field_tooltip'],
            tooltip2=context_view_field(r.context, 1, 0)['field_tooltip'],
            tooltip3=context_view_field(r.context, 2, 0)['field_tooltip'],
            tooltip4=context_view_field(r.context, 3, 0)['field_tooltip'],
            tooltip5=context_view_field(r.context, 3, 1)['field_tooltip'],
            tooltip6=context_view_field(r.context, 4, 0)['field_tooltip'],
            tooltip7=context_view_field(r.context, 5, 0)['field_tooltip'],
            )
        formrow1a = """
            <div class="small-12 medium-6 columns" title="%(tooltip1a)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(list id)" 
                         value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow1b = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip1b)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List display type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_choice_options(
                    "List_type",
                    self.list_type_opts,
                    "_enum_list_type/List")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns" title="%(tooltip2)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="List_label" 
                         placeholder="(list label)" 
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
                  <textarea cols="64" rows="6" name="List_comment" 
                          class="small-rows-4 medium-rows-8"
                          placeholder="(description of list view)">
                    %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip4)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default type</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "List_default_type", "Default type",
                    no_selection("(default entity type)") + self.type_options,
                    "_type/Default_type",
                    placeholder="(default entity type)"
                    )+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow5 = ("""
            <div class="small-12 medium-6 columns" title="%(tooltip5)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default view</span>
                </div>
                <div class="%(input_classes)s">
                """+
                  render_select_options(
                    "List_default_view", "Default view",
                    no_selection("(view id)") + self.view_options,
                    "_view/Default_view",
                    placeholder="(view id)"
                    )+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        selector_text = (
            "(entity selector; "+
            "e.g. &#39;ALL&#39;, "+
            "&#39;<type> in [@type]&#39;, "+
            "&#39;[<field>]==<value>&#39;, "+
            "etc.)"
            )
        formrow6 = """
            <div class="small-12 columns" title="%(tooltip6)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Selector</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="List_entity_selector" 
                         placeholder="%(selector_text)s"
                         value="ALL"/>
                </div>
              </div>
            </div>
            """%dict(field_vals(width=12), selector_text=selector_text)
        entitytype_text = "(entity type URI/CURIE displayed by list)"
        formrow7 = """
            <div class="small-12 columns" title="%(tooltip7)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List entity type</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="List_entity_type" 
                         placeholder="%(entitytype_text)s"
                         value=""/>
                </div>
              </div>
            </div>
            """%dict(field_vals(width=12), entitytype_text=entitytype_text)
        formrow9a = """
            <div class="small-12 medium-4 columns">
              <div class="row">
                <div class="form-buttons small-12 columns">
                  <input type="submit" name="edit" value="Edit" 
                         title="Edit entity data.">
                  <input type="submit" name="copy" value="Copy" 
                         title="Copy, then edit entity data as new entity.">
                  <input type="submit" name="close" value="Close" 
                         title="Return to previous page.">
                </div>
              </div>
            </div>
            """
        formrow9a = """
            <div class="small-12 medium-4 columns">
              <div class="row">
                <div class="form-buttons small-12 columns">
                  <input type="submit" name="save" value="Save" 
                         title="Save values and return to previous view.">
                  <input type="submit" name="view" value="View" 
                         title="Save values and switch to entity view.">
                  <input type="submit" name="cancel" value="Cancel" 
                         title="Discard unsaved changes and return to previous view.">
                </div>
              </div>
            </div>
            """
        formrow9b = """
            <div class="small-12 medium-6 columns">
              <div class="row">
                <div class="form-buttons small-12 columns medium-up-text-right">
                  <input type="submit" name="Show_list" value="Show this list" 
                         title="Show the list of entities described the currently displayed list definition.">
                  <input type="submit" name="default_view" value="Set default view" 
                         title="Select this display as the default view for collection 'Carolan_Guitar'.">
                  <input type="submit" name="customize" value="Customize" 
                         title="Open 'Customize' view for collection 'Carolan_Guitar'.">
                </div>
              </div>
            </div>
            """
        formrow9b = """
            <div class="small-12 medium-6 columns">
              <div class="row">
                <div class="form-buttons small-12 columns medium-up-text-right">
                  <input type="submit" name="customize" value="Customize" 
                         title="Open 'Customize' view for collection 'testcoll'.">
                </div>
              </div>
            </div>
            """
        # log.info(r.content)     #@@
        self.assertContains(r, formrow1a, html=True)
        self.assertContains(r, formrow1b, html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5,  html=True)
        self.assertContains(r, formrow6,  html=True)
        self.assertContains(r, formrow7,  html=True)
        self.assertContains(r, formrow9a, html=True)
        self.assertContains(r, formrow9b, html=True)
        return

    def test_get_view_form_rendering(self):
        u = entitydata_edit_url(
            "view", "testcoll", layout.LIST_TYPEID, view_id="List_view", entity_id="List_list"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        default_comment=context_view_field(r.context, 2, 0)['field_value']
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.LIST_TYPEID, entity_id="00000001",
            default_comment=default_comment,
            rendered_help=markdown.markdown(apply_substitutions(r.context, default_comment)),
            tooltip1a=context_view_field(r.context, 0, 0)['field_help'],
            tooltip1b=context_view_field(r.context, 0, 1)['field_help'],
            tooltip2=context_view_field(r.context, 1, 0)['field_help'],
            tooltip3=context_view_field(r.context, 2, 0)['field_help'],
            tooltip4=context_view_field(r.context, 3, 0)['field_help'],
            tooltip5=context_view_field(r.context, 3, 1)['field_help'],
            tooltip6=context_view_field(r.context, 4, 0)['field_help'],
            tooltip7=context_view_field(r.context, 5, 0)['field_help'],
            type_typeid=layout.TYPE_TYPEID,
            list_typeid=layout.LIST_TYPEID,
            view_typeid=layout.VIEW_TYPEID,
            cont_here=u,
            )
        formrow1a = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List Id</span>
                </div>
                <div class="%(input_classes)s">
                  <!-- <span>List_list</span> -->
                  <a href="/testsite/c/testcoll/d/%(list_typeid)s/List_list/?continuation_url=%(cont_here)s">
                    List_list
                  </a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow1b = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List display type</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="/testsite/c/testcoll/d/_enum_list_type/List/?continuation_url=%(cont_here)s">
                    List display
                  </a>
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <span>List definitions</span>
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
                  <span class="markdown">%(rendered_help)s</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default type</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="/testsite/c/testcoll/d/%(type_typeid)s/%(list_typeid)s/?continuation_url=%(cont_here)s">
                    List
                  </a>
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow5 = ("""
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default view</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="/testsite/c/testcoll/d/%(view_typeid)s/List_view/?continuation_url=%(cont_here)s">
                    List definition
                  </a>
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow6 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Selector</span>
                </div>
                <div class="%(input_classes)s">
                  <span>&#39;annal:List&#39; in [@type]</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow7 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>List entity type</span>
                </div>
                <div class="%(input_classes)s">
                  <span>annal:List</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow9a = """
            <div class="small-12 medium-4 columns">
              <div class="row">
                <div class="form-buttons small-12 columns">
                  <input type="submit" name="edit" value="Edit" 
                         title="Edit entity data.">
                  <input type="submit" name="copy" value="Copy" 
                         title="Copy, then edit entity data as new entity.">
                  <input type="submit" name="close" value="Close" 
                         title="Return to previous page.">
                </div>
              </div>
            </div>
            """
        formrow9b = """
            <div class="small-12 medium-6 columns">
              <div class="row">
                <div class="form-buttons small-12 columns medium-up-text-right">
                  <input type="submit" name="Show_list" value="Show this list" 
                         title="Show the list of entities described the currently displayed list definition.">
                  <input type="submit" name="default_view" value="Set default view" 
                         title="Select this display as the default view for collection 'testcoll'.">
                  <input type="submit" name="customize" value="Customize" 
                         title="Open 'Customize' view for collection 'testcoll'.">
                </div>
              </div>
            </div>
            """
        # log.info(r.content)     #@@
        self.assertContains(r, formrow1a, html=True)
        self.assertContains(r, formrow1b, html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5,  html=True)
        self.assertContains(r, formrow6,  html=True)
        self.assertContains(r, formrow7,  html=True)
        self.assertContains(r, formrow9a, html=True)
        self.assertContains(r, formrow9b, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.LIST_TYPEID)
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_list_view_context_fields(r, 
            action="new",
            num_fields=3,
            list_id="00000001",
            list_label=default_label("testcoll", layout.LIST_TYPEID, "00000001"),
            list_uri=None,
            list_type="_enum_list_type/List",
            list_entity_selector="ALL",
            continuation_url="/xyzzy/"
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, entity_id="Default_list", view_id="List_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.LIST_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Default_list_01")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="copy",
            num_fields=2,
            list_id="Default_list_01", orig_list_id="Default_list",
            list_label="List entities",
            list_uri=None,
            continuation_url=""
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, entity_id="nolist", view_id="List_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", layout.LIST_TYPEID, "nolist")
        msg_text  = make_message(message.ENTITY_DOES_NOT_EXIST, 
            type_id=layout.LIST_TYPEID, 
            id="nolist", 
            label=err_label
            )
        self.assertContains(r, "<p>%s</p>"%msg_text, status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, entity_id="Default_list", 
            view_id="List_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.LIST_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Default_list")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_list")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="Default_list", orig_list_id="Default_list",
            list_label="List entities",
            list_uri="annal:display/Default_list",
            continuation_url=""
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, entity_id="nolist", 
            view_id="List_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", layout.LIST_TYPEID, "nolist")
        msg_text  = make_message(message.ENTITY_DOES_NOT_EXIST, 
            type_id=layout.LIST_TYPEID, 
            id="nolist", 
            label=err_label
            )
        self.assertContains(r, "<p>%s</p>"%msg_text, status_code=404)
        return

    # Test rendering of view with repeated field structure - in this case, List_view
    def test_get_recordlist_edit(self):
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", 
            type_id=layout.LIST_TYPEID, entity_id="Default_list", 
            view_id="List_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.LIST_TYPEID)
        self.assertEqual(r.context['entity_id'],        "Default_list")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_list")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="Default_list", orig_list_id="Default_list",
            list_label="List entities",
            list_uri="annal:display/Default_list",
            continuation_url=""
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new list --------

    def test_post_new_list(self):
        self.assertFalse(RecordList.exists(self.testcoll, "newlist"))
        f = list_view_form_data(list_id="newlist", action="new", update="New List")
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_list_view_values("newlist", update="New List", num_fields=0)
        return

    def test_post_new_list_cancel(self):
        self.assertFalse(RecordList.exists(self.testcoll, "newlist"))
        f = list_view_form_data(
            list_id="newlist", action="new", cancel="Cancel", update="Updated RecordList"
            )
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type still does not exist
        self.assertFalse(RecordList.exists(self.testcoll, "newview"))
        return

    def test_post_new_list_missing_id(self):
        f = list_view_form_data(action="new", update="RecordList")
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID))
        # Test context
        self._check_list_view_context_fields(r, 
            action="new",
            num_fields=2,
            list_id="", orig_list_id="orig_list_id",
            list_type="_enum_list_type/List",
            list_entity_selector="ALL",
            list_entity_type=""
            )
        return

    def test_post_new_list_invalid_id(self):
        f = list_view_form_data(
            list_id="!badlist", orig_id="orig_list_id", action="new", update="RecordList"
            )
        u = entitydata_edit_url("new", "testcoll", layout.LIST_TYPEID, view_id="List_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID,))
        # Test context
        self._check_list_view_context_fields(r, 
            action="new",
            num_fields=2,
            list_id="!badlist", orig_list_id="orig_list_id",
            list_type="_enum_list_type/List",
            list_entity_selector="ALL",
            list_entity_type=""
            )
        return

    #   -------- copy list --------

    def test_post_copy_view(self):
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        f = list_view_form_data(
            list_id="copylist", 
            orig_id="Default_list", orig_coll="_annalist_site", action="copy", 
            update="RecordList"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, entity_id="Default_list", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_list_view_values("copylist", update="RecordList")
        return

    def test_post_copy_view_cancel(self):
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        f = list_view_form_data(
            list_id="copylist", orig_id="Default_list", action="copy", 
            cancel="Cancel", update="RecordList"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, entity_id="Default_list", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record view still does not exist
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        return

    def test_post_copy_view_missing_id(self):
        self._create_list_view("listview")
        f = list_view_form_data(
            action="copy", 
            orig_id="listview",
            update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, 
            entity_id="listview", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID,))
        # Test context
        self._check_list_view_context_fields(r, 
            action="copy",
            num_fields=2,
            list_id="", orig_list_id="listview",
            list_type="_enum_list_type/List",
            list_entity_selector="ALL",
            list_entity_type="",
            update="Updated RecordList"
            )
        return

    def test_post_copy_view_invalid_id(self):
        f = list_view_form_data(
            list_id="!badlist", orig_id="Default_list", action="copy", 
            update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.LIST_TYPEID, 
            entity_id="Default_list", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID,))
        # Test context
        self._check_list_view_context_fields(r, 
            action="copy",
            num_fields=2,
            list_id="!badlist", orig_list_id="Default_list",
            list_type="_enum_list_type/List",
            list_uri="annal:display/Default_list",
            list_entity_selector="ALL",
            list_entity_type="",
            update="Updated RecordList"
            )
        return

    #   -------- edit list --------

    def test_post_edit_view(self):
        self._create_list_view("listview")
        self._check_list_view_values("listview")
        f = list_view_form_data(
            list_id="listview", orig_id="listview", 
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, 
            entity_id="listview", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record list exists
        self._check_list_view_values("listview", update="Updated RecordList")
        return

    def test_post_edit_view_new_id(self):
        self._create_list_view("editlist1")
        self._check_list_view_values("editlist1")
        f = list_view_form_data(
            list_id="editlist2", orig_id="editlist1", 
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, 
            entity_id="editlist1", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record list exists and old does not
        self.assertFalse(RecordList.exists(self.testcoll, "editlist1"))
        self._check_list_view_values("editlist2", update="Updated RecordList")
        return

    def test_post_edit_view_cancel(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        f = list_view_form_data(
            list_id="editlist", orig_id="editlist", 
            action="edit", cancel="Cancel", update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, 
            entity_id="editlist", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record list still does not exist and unchanged
        self._check_list_view_values("editlist")
        return

    def test_post_edit_view_missing_id(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        # Form post with ID missing
        f = list_view_form_data(
            action="edit", 
            orig_id="editlist",
            update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, 
            entity_id="editlist", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID,))
        # Test context
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="", orig_list_id="editlist",
            list_type="_enum_list_type/List",
            list_uri=None,
            list_entity_selector="ALL",
            list_entity_type="",
            update="Updated RecordList"
            )
        # Check original data is unchanged
        self._check_list_view_values("editlist")
        return

    def test_post_edit_view_invalid_id(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        # Form post with invalid ID
        f = list_view_form_data(
            list_id="!badlist", orig_id="editlist", 
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.LIST_TYPEID, entity_id="editlist", view_id="List_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_LIST_ID,))
        # Test context
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="!badlist", orig_list_id="editlist",
            list_type="_enum_list_type/List",
            list_uri=None,
            list_entity_selector="ALL",
            list_entity_type="",
            update="Updated RecordList"
            )
        # Check original data is unchanged
        self._check_list_view_values("editlist")
        return

    #   -------- Show this list (task button) --------

    def test_define_show_list_task(self):
        # Post show list to list definition URI
        f = list_view_form_data(
            action="view",
            list_id="List_list",
            task="Show_list"
            )
        u = entitydata_edit_url(
            "view", "testcoll", layout.LIST_TYPEID, 
            view_id="List_view", entity_id="List_list"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        l = entitydata_list_all_url(
            "testcoll", list_id="List_list", scope=None,
            continuation_url=u
            )
        self.assertIn(TestHostUri+l, r['location'])
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmRecordListDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmRecordListDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(
            self.testsite, "testcoll", 
            collection_create_values("testcoll")
            )
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(
            RecordListDeleteConfirmedView.__name__, 
            "RecordListDeleteConfirmedView", 
            "Check RecordListDeleteConfirmedView class name"
            )
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_view(self):
        t = RecordList.create(
            self.testcoll, "deleteview", 
            recordlist_create_values("deleteview")
            )
        self.assertTrue(RecordList.exists(self.testcoll, "deleteview"))
        # Submit positive confirmation
        u = TestHostUri + recordlist_edit_url("delete", "testcoll")
        f = recordlist_delete_confirm_form_data("deleteview")
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
            r"\?.*info_message=.*deleteview.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordList.exists(self.testcoll, "deleteview"))
        return

# End.
