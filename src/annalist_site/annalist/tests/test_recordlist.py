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

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.recordlist         import RecordList

from annalist.views.recordlistdelete    import RecordListDeleteConfirmedView

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site
from AnnalistTestCase                   import AnnalistTestCase
from entity_testutils                   import (
    site_dir, collection_dir,
    site_view_uri, collection_edit_uri, 
    collection_create_values,
    site_title
    )
from entity_testlistdata                import (
    recordlist_dir,
    recordlist_coll_uri, recordlist_site_uri, recordlist_uri, recordlist_edit_uri,
    recordlist_value_keys, recordlist_load_keys, 
    recordlist_create_values, recordlist_values, recordlist_read_values,
    # recordlist_entity_view_context_data, recordlist_entity_view_form_data, 
    recordlist_view_context_data, recordlist_view_form_data, 
    recordlist_delete_confirm_form_data
    )
from entity_testentitydata              import (
    entity_uri, entitydata_edit_uri, entitydata_list_type_uri
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
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_RecordListTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_recordlist_init(self):
        t = RecordList(self.testcoll, "testlist", self.testsite)
        u = recordlist_coll_uri(self.testsite, coll_id="testcoll", list_id="testlist")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.List)
        self.assertEqual(t._entityfile,     layout.LIST_META_FILE)
        self.assertEqual(t._entityref,      layout.META_LIST_REF)
        self.assertEqual(t._entityid,       "testlist")
        self.assertEqual(t._entityuri,      u)
        self.assertEqual(t._entitydir,      recordlist_dir(list_id="testlist"))
        self.assertEqual(t._values,         None)
        return

    def test_recordlist1_data(self):
        t = RecordList(self.testcoll, "list1", self.testsite)
        self.assertEqual(t.get_id(), "list1")
        self.assertEqual(t.get_type_id(), "_list")
        self.assertIn("/c/testcoll/_annalist_collection/lists/list1/", t.get_uri())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_list/list1/", t.get_view_uri())
        t.set_values(recordlist_create_values(list_id="list1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordlist_value_keys()))
        v = recordlist_values(list_id="list1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordlist2_data(self):
        t = RecordList(self.testcoll, "list2", self.testsite)
        self.assertEqual(t.get_id(), "list2")
        self.assertEqual(t.get_type_id(), "_list")
        self.assertIn("/c/testcoll/_annalist_collection/lists/list2/", t.get_uri())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_list/list2/", t.get_view_uri())
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
        t = RecordList.load(self.testcoll, "Default_list", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Default_list")
        self.assertIn("/c/testcoll/_annalist_collection/lists/Default_list", t.get_uri())
        self.assertEqual(t.get_type_id(), "_list")
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordlist_load_keys()))
        v = recordlist_read_values(list_id="Default_list")
        v.update(
            { 'rdfs:label':     'List one type'
            , 'rdfs:comment':   'Default list of entities of given type'
            , 'annal:uri':      "annal:display/Default_list"
            })
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
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user     = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client   = Client(HTTP_HOST=TestHost)
        loggedin      = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.no_options = ['(no options)']
        self.continuation_uri = TestHostUri + entitydata_list_type_uri(coll_id="testcoll", type_id="_list")
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_list_view(self, list_id):
        "Helper function creates record view entry with supplied list_id"
        t = RecordList.create(self.testcoll, list_id, recordlist_create_values(list_id=list_id))
        return t

    def _check_list_view_values(self, list_id, update="RecordList", num_fields=4):
        "Helper function checks content of record view entry with supplied list_id"
        self.assertTrue(RecordList.exists(self.testcoll, list_id))
        t = RecordList.load(self.testcoll, list_id)
        self.assertEqual(t.get_id(), list_id)
        self.assertEqual(t.get_view_uri(), TestHostUri + recordlist_uri("testcoll", list_id))
        v = recordlist_values(list_id=list_id, update=update)
        if num_fields == 0:
            v['annal:list_fields'] = []
        # log.info("RecordList.load values: %r"%(t.get_values(),))
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    # Check context value used for displaying list view
    def _check_list_view_context_fields(self, response, 
            action="",
            num_fields=0,
            list_id="(?list_id)", 
            list_label="(?list_label)",
            list_help="(?list_help)",
            list_uri="(?list_uri)",
            list_type="annal:display_type/List",
            list_default_type="Default_type",
            list_default_view="Default_view",
            list_selector="ALL"
            ):
        r = response
        #log.info("r.context['fields']: %r"%(r.context['fields'],))
        # Common structure
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['entity_id'],        list_id)
        self.assertEqual(r.context['orig_id'],          list_id)
        self.assertEqual(r.context['type_id'],          '_list')
        self.assertEqual(r.context['orig_type'],        '_list')
        self.assertEqual(r.context['coll_id'],          'testcoll')
        self.assertEqual(r.context['entity_uri'],       list_uri)
        self.assertEqual(r.context['action'],           action)
        self.assertEqual(r.context['view_id'],          'List_view')

        # Fields
        self.assertEqual(len(r.context['fields']), 8)
        #
        self.assertEqual(r.context['fields'][0]['field_id'], 'List_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_value'], list_id)
        #
        self.assertEqual(r.context['fields'][1]['field_id'], 'List_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'List_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'List display type')
        self.assertEqual(r.context['fields'][1]['field_value'], list_type)
        #
        self.assertEqual(r.context['fields'][2]['field_id'], 'List_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'List_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_value'], list_label)
        #
        self.assertEqual(r.context['fields'][3]['field_id'], 'List_comment')
        self.assertEqual(r.context['fields'][3]['field_name'], 'List_comment')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Help')
        self.assertEqual(r.context['fields'][3]['field_value'], list_help)
        #
        self.assertEqual(r.context['fields'][4]['field_id'], 'List_default_type')
        self.assertEqual(r.context['fields'][4]['field_name'], 'List_default_type')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Record type')
        self.assertEqual(r.context['fields'][4]['field_value'], list_default_type)
        #
        self.assertEqual(r.context['fields'][5]['field_id'], 'List_default_view')
        self.assertEqual(r.context['fields'][5]['field_name'], 'List_default_view')
        self.assertEqual(r.context['fields'][5]['field_label'], 'View')
        self.assertEqual(r.context['fields'][5]['field_value'], list_default_view)
        #
        self.assertEqual(r.context['fields'][6]['field_id'], 'List_entity_selector')
        self.assertEqual(r.context['fields'][6]['field_name'], 'List_entity_selector')
        self.assertEqual(r.context['fields'][6]['field_label'], 'Selector')
        self.assertEqual(r.context['fields'][6]['field_value'], list_selector)
        #
        # Field list (List_id, List_label, List_comment, field descriptions)
        # log.info("r.context['fields'][7]: %r"%(r.context['fields'][7],))
        # log.info("viewfields: %r"%(viewfields,))
        viewfields = r.context['fields'][7]['repeat']
        self.assertEqual(len(viewfields), num_fields)
        if num_fields == 0: return
        self.assertEqual(len(viewfields[0]['fields']), 2)
        self.assertEqual(len(viewfields[1]['fields']), 2)
        # Entity_id
        self.assertEqual(viewfields[0]['fields'][0].field_value_key,        "annal:field_id")
        self.assertEqual(viewfields[0]['fields'][0].field_value,            "Entity_id")
        self.assertEqual(viewfields[0]['fields'][1].field_value_key,        "annal:field_placement")
        self.assertEqual(viewfields[0]['fields'][1].field_value,            "small:0,3")
        # Entity_label
        self.assertEqual(viewfields[1]['fields'][0].field_value_key,        "annal:field_id")
        self.assertEqual(viewfields[1]['fields'][0].field_value,            "Entity_label")
        self.assertEqual(viewfields[1]['fields'][1].field_value_key,        "annal:field_placement")
        self.assertEqual(viewfields[1]['fields'][1].field_value,            "small:3,9")
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_list' data in collection 'testcoll'</h3>")
        formrow1 = """
            <div class="small-12 medium-6 columns">
                <div class="row">
                    <div class="view_label small-12 medium-6 columns">
                        <p>Id</p>
                    </div>
                    <div class="small-12 medium-6 columns">
                        <input type="text" size="64" name="entity_id" value="00000001"/>
                    </div>
                </div>
            </div>
            """
        formrow2 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-3 columns">
                        <p>Label</p>
                    </div>
                    <div class="small-12 medium-9 columns">
                        <input type="text" size="64" name="List_label" 
                               value="Entity &#39;00000001&#39; of type &#39;_list&#39; in collection &#39;testcoll&#39;"/>
                    </div>
                </div>
            </div>
            """
        formrow3 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-3 columns">
                        <p>Help</p>
                    </div>
                    <div class="small-12 medium-9 columns">
                                <textarea cols="64" rows="6" name="List_comment" class="small-rows-4 medium-rows-8"></textarea>
                    </div>
                </div>
            </div>
            """
        # @@TODO: more .....
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        view_uri = entity_uri(type_id="_list", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_list")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + view_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_list_view_context_fields(r, 
            action="new",
            num_fields=0,
            list_id="00000001",
            list_label="Entity '00000001' of type '_list' in collection 'testcoll'",
            list_help="",
            list_uri=TestHostUri + recordlist_uri("testcoll", "00000001"),
            list_type="(list type)", # @@TODO: don't use placeholders as results
            list_default_type="(default record type)",
            list_default_view="(view id)",
            list_selector="(entity selector)"
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="Default_list", view_id="List_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_list")
        self.assertEqual(r.context['entity_id'],        "Default_list")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_list")
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_uri'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="copy",
            num_fields=2,
            list_id="Default_list",
            list_label="List one type",
            list_help="Default list of entities of given type",
            list_uri="annal:display/Default_list"
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="notype", view_id="List_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Entity &#39;notype&#39; of type &#39;_list&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_uri(
            "edit", "testcoll", "_list", entity_id="Default_list", 
            view_id="List_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_list")
        self.assertEqual(r.context['entity_id'],        "Default_list")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_list")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="Default_list",
            list_label="List one type",
            list_help="Default list of entities of given type",
            list_uri="annal:display/Default_list"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri(
            "edit", "testcoll", "_list", entity_id="nolist", 
            view_id="List_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Entity &#39;nolist&#39; of type &#39;_list&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    # Test rendering of view with repeated field structure - in this case, List_view
    def test_get_recordlist_edit(self):
        u = entitydata_edit_uri(
            action="edit", coll_id="testcoll", 
            type_id="_list", entity_id="Default_list", 
            view_id="List_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_list")
        self.assertEqual(r.context['entity_id'],        "Default_list")
        self.assertEqual(r.context['orig_id'],          "Default_list")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_list")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "")
        # Fields
        self._check_list_view_context_fields(r, 
            action="edit",
            num_fields=2,
            list_id="Default_list",
            list_label="List one type",
            list_help="Default list of entities of given type",
            list_uri="annal:display/Default_list"
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new list --------

    def test_post_new_list(self):
        self.assertFalse(RecordList.exists(self.testcoll, "newlist"))
        f = recordlist_view_form_data(list_id="newlist", action="new", update="New List")
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists
        self._check_list_view_values("newlist", update="New List", num_fields=0)
        return

    def test_post_new_list_cancel(self):
        self.assertFalse(RecordList.exists(self.testcoll, "newlist"))
        f = recordlist_view_form_data(
            list_id="newlist", action="new", cancel="Cancel", update="Updated RecordList"
            )
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type still does not exist
        self.assertFalse(RecordList.exists(self.testcoll, "newview"))
        return

    def test_post_new_list_missing_id(self):
        f = recordlist_view_form_data(action="new", update="RecordList")
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        # Test context
        # log.info("r.context[0] %r\n\n"%(r.context[0],))
        # log.info("r.context[1] %r\n\n"%(r.context[1],))
        # log.info("r.context[2] \n--------\n%r\n\n"%(r.context[2],))
        expect_context = recordlist_view_context_data(action="new", update="RecordList")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_list_invalid_id(self):
        f = recordlist_view_form_data(
            list_id="!badlist", orig_id="orig_view_id", action="new", update="RecordList"
            )
        u = entitydata_edit_uri("new", "testcoll", "_list", view_id="List_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        # Test context
        expect_context = recordlist_view_context_data(
            list_id="!badlist", orig_id="orig_view_id", action="new", update="RecordList"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy list --------

    def test_post_copy_view(self):
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        f = recordlist_view_form_data(
            list_id="copylist", orig_id="Default_list", action="copy", update="RecordList"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="Default_list", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record type exists
        self._check_list_view_values("copylist", update="RecordList")
        return

    def test_post_copy_view_cancel(self):
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        f = recordlist_view_form_data(
            list_id="copylist", orig_id="Default_list", action="copy", cancel="Cancel", update="RecordList"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="Default_list", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that target record view still does not exist
        self.assertFalse(RecordList.exists(self.testcoll, "copylist"))
        return

    def test_post_copy_view_missing_id(self):
        f = recordlist_view_form_data(
            action="copy", update="Updated RecordList"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="Default_list", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        expect_context = recordlist_view_context_data(action="copy", update="Updated RecordList")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_view_invalid_id(self):
        f = recordlist_view_form_data(
            list_id="!badlist", orig_id="Default_list", action="copy", update="Updated RecordList"
            )
        u = entitydata_edit_uri("copy", "testcoll", "_list", entity_id="Default_list", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        expect_context = recordlist_view_context_data(
            list_id="!badlist", orig_id="Default_list", 
            action="copy", update="Updated RecordList"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit list --------

    def test_post_edit_view(self):
        self._create_list_view("listview")
        self._check_list_view_values("listview")
        f = recordlist_view_form_data(
            list_id="listview", orig_id="listview", 
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_list", entity_id="listview", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record list exists
        self._check_list_view_values("listview", update="Updated RecordList")
        return

    def test_post_edit_view_new_id(self):
        self._create_list_view("editlist1")
        self._check_list_view_values("editlist1")
        f = recordlist_view_form_data(
            list_id="editlist2", orig_id="editlist1", 
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_list", entity_id="editlist1", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that new record list exists and old does not
        self.assertFalse(RecordList.exists(self.testcoll, "editlist1"))
        self._check_list_view_values("editlist2", update="Updated RecordList")
        return

    def test_post_edit_view_cancel(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        f = recordlist_view_form_data(
            list_id="editlist", orig_id="editlist", 
            action="edit", cancel="Cancel", update="Updated RecordList"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_list", entity_id="editlist", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_uri)
        # Check that target record list still does not exist and unchanged
        self._check_list_view_values("editlist")
        return

    def test_post_edit_view_missing_id(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        # Form post with ID missing
        f = recordlist_view_form_data(
            action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_list", entity_id="editlist", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordlist_view_context_data(action="edit", update="Updated RecordList")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_list_view_values("editlist")
        return

    def test_post_edit_view_invalid_id(self):
        self._create_list_view("editlist")
        self._check_list_view_values("editlist")
        # Form post with invalid ID
        f = recordlist_view_form_data(
            list_id="!badlist", orig_id="editlist", action="edit", update="Updated RecordList"
            )
        u = entitydata_edit_uri("edit", "testcoll", "_list", entity_id="editlist", view_id="List_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record list identifier</h3>")
        # Test context
        expect_context = recordlist_view_context_data(
            list_id="!badlist", orig_id="editlist", 
            action="edit", update="Updated RecordList"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_list_view_values("editlist")
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
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(RecordListDeleteConfirmedView.__name__, "RecordListDeleteConfirmedView", "Check RecordListDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_view(self):
        t = RecordList.create(self.testcoll, "deleteview", recordlist_create_values("deleteview"))
        self.assertTrue(RecordList.exists(self.testcoll, "deleteview"))
        # Submit positive confirmation
        u = TestHostUri + recordlist_edit_uri("delete", "testcoll")
        f = recordlist_delete_confirm_form_data("deleteview")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_uri("testcoll")+
            r"\?info_head=.*&info_message=.*deleteview.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordList.exists(self.testcoll, "deleteview"))
        return

# End.
