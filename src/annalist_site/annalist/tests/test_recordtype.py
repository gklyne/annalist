"""
Tests for RecordType module and view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.db                  import models
from django.http                import QueryDict
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout
from annalist.models.site       import Site
from annalist.models.sitedata   import SiteData
from annalist.models.collection import Collection
from annalist.models.recordtype import RecordType

from annalist.views.recordtype  import RecordTypeEditView, RecordTypeDeleteConfirmedView

from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                      import init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase
from entity_testutils           import (
    site_dir, collection_dir, recordtype_dir,
    site_view_uri, collection_edit_uri, recordtype_uri, recordtype_edit_uri,
    collection_create_values,
    recordtype_value_keys, recordtype_create_values, recordtype_values,
    recordtype_context_data, recordtype_form_data, recordtype_delete_confirm_form_data,
    site_title
    )

#   -----------------------------------------------------------------------------
#
#   RecordType tests
#
#   -----------------------------------------------------------------------------

class RecordTypeTest(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite, layout.SITEDATA_DIR)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_RecordTypeTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_recordtype_init(self):
        t = RecordType(self.testcoll, "testtype")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.RecordType)
        self.assertEqual(t._entityfile,     layout.TYPE_META_FILE)
        self.assertEqual(t._entityref,      layout.META_TYPE_REF)
        self.assertEqual(t._entityid,       "testtype")
        self.assertEqual(t._entityuri,      TestHostUri + recordtype_uri(type_id="testtype"))
        self.assertEqual(t._entitydir,      recordtype_dir(type_id="testtype"))
        self.assertEqual(t._values,         None)
        return

    def test_recordtype1_data(self):
        t = RecordType(self.testcoll, "type1")
        t.set_values(recordtype_create_values(type_id="type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_create_values(type_id="type1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2")
        t.set_values(recordtype_create_values(type_id="type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_create_values(type_id="type2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", recordtype_create_values(type_id="type1"))
        td = RecordType.load(self.testcoll, "type1").get_values()
        v = recordtype_values(type_id="type1")
        self.assertKeysMatch(td, v)
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

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_type(self, type_id):
        "Helper function creates record type entry with supplied type_id"
        t = RecordType.create(self.testcoll, type_id, recordtype_create_values(type_id=type_id))
        return t    

    def _check_record_type_values(self, type_id, update="RecordType"):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_uri(""), TestHostUri + recordtype_uri("testcoll", type_id))
        v = recordtype_values(type_id=type_id, update=update)
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_RecordTypeEditView(self):
        self.assertEqual(RecordTypeEditView.__name__, "RecordTypeEditView", "Check RecordTypeEditView class name")
        return

    def test_get_new(self):
        u = recordtype_edit_uri("new", "coll1")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['type_label'],       "Record type 00000001 in collection coll1")
        self.assertEqual(r.context['type_help'],        "")
        self.assertEqual(r.context['type_uri'],         recordtype_uri("coll1", "00000001"))
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        return

    def test_get_copy(self):
        u = recordtype_edit_uri("copy", "coll1", type_id="type1")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_id'],          "type1")
        self.assertEqual(r.context['type_label'],       "RecordType coll1/type1")
        self.assertEqual(r.context['type_help'],        "RecordType help for type1 in collection coll1")
        self.assertEqual(r.context['type_uri'],         TestHostUri + recordtype_uri("coll1", "type1"))
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    def test_get_copy_not_exists(self):
        u = recordtype_edit_uri("copy", "coll1", type_id="notype")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Record type notype in collection coll1 does not exist</p>", status_code=404)
        return

    def test_get_edit(self):
        u = recordtype_edit_uri("edit", "coll1", type_id="type1")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_id'],          "type1")
        self.assertEqual(r.context['type_label'],       "RecordType coll1/type1")
        self.assertEqual(r.context['type_help'],        "RecordType help for type1 in collection coll1")
        self.assertEqual(r.context['type_uri'],         TestHostUri + recordtype_uri("coll1", "type1"))
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_form_data(type_id="newtype", action="new", update="Updated RecordType")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that new record type exists
        self._check_record_type_values("newtype", update="Updated RecordType")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_form_data(type_id="newtype", action="new", cancel="Cancel", update="Updated RecordType")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = recordtype_form_data(action="new", update="Updated RecordType")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(action="new", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = recordtype_form_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", 
            update="Updated RecordType"
            )
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(
            type_id="!badtype", orig_id="orig_type_id", 
            action="new", update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_form_data(type_id="copytype", action="copy", update="Updated RecordType")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that new record type exists
        self._check_record_type_values("copytype", update="Updated RecordType")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_form_data(type_id="copytype", action="copy", cancel="Cancel", update="Updated RecordType")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that target record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = recordtype_form_data(action="copy", update="Updated RecordType")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = recordtype_context_data(action="copy", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_type_invalid_id(self):
        f = recordtype_form_data(
            type_id="!badtype", orig_id="orig_type_id", 
            action="copy", 
            update="Updated RecordType"
            )
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = recordtype_context_data(
            type_id="!badtype", orig_id="orig_type_id", 
            action="copy", 
            update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_form_data(type_id="edittype", action="edit", update="Updated RecordType")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        self._check_record_type_values("edittype", update="Updated RecordType")
        return

    def test_post_edit_type_new_id(self):
        self._create_record_type("edittype1")
        self._check_record_type_values("edittype1")
        # Now post edit form submission with different values and new id
        f = recordtype_form_data(type_id="edittype2", orig_id="edittype1", action="edit", update="Updated RecordType")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that new record type exists and old does not
        self.assertFalse(RecordType.exists(self.testcoll, "edittype1"))
        self._check_record_type_values("edittype2", update="Updated RecordType")
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Post from cancelled edit form
        f = recordtype_form_data(type_id="edittype", action="edit", cancel="Cancel", update="Updated RecordType")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = recordtype_form_data(action="edit", update="Updated RecordType")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context for re-rendered form
        expect_context = recordtype_context_data(action="edit", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_edit_type_invalid_id(self):
        f = recordtype_form_data(
            type_id="!badtype", orig_id="orig_type_id", 
            action="edit", 
            update="Updated RecordType"
            )
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(
            type_id="!badtype", orig_id="orig_type_id", 
            action="edit", 
            update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
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
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
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
        u = TestHostUri + recordtype_edit_uri("delete", "testcoll")
        f = recordtype_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_uri("testcoll")+
            r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordType.exists(self.testcoll, "deletetype"))
        return

# End.
