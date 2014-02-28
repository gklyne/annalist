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
from django.core.urlresolvers   import resolve, reverse
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout
from annalist.models.site       import Site
from annalist.models.collection import Collection
from annalist.models.recordtype import RecordType

from annalist.views.recordtype  import RecordTypeEditView, RecordTypeDeleteConfirmedView

from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                      import init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase

#   -----------------------------------------------------------------------------
#
#   Test data helpers
#
#   -----------------------------------------------------------------------------

def recordtype_edit_uri(action, coll_id, type_id=None):
    viewname = ( 
        "AnnalistRecordTypeNewView"  if action == "new" else
        "AnnalistRecordTypeCopyView" if action == "copy" else
        "AnnalistRecordTypeEditView"
        )
    if type_id:
        kwargs = {'action': action, 'coll_id': coll_id, 'type_id': type_id}
    else:
        kwargs = {'action': action, 'coll_id': coll_id}
    return reverse(viewname, kwargs=kwargs)

def collection_edit_uri(coll_id="testcoll"):
    return TestHostUri + reverse("AnnalistCollectionEditView", kwargs={'coll_id': coll_id})

def recordtype_delete_confirm_uri(coll_id):
    return TestHostUri + reverse("AnnalistRecordTypeDeleteView", kwargs={'coll_id': coll_id})

def recordtype_delete_confirm_form_data(type_id=None):
    return (
        { 'typelist':    type_id,
          'type_delete': 'Delete'
        })

def collection_create_values(coll_id="testcoll"):
    return (
        { 'rdfs:label':     'Collection %s'%coll_id
        , 'rdfs:comment':   'Description of Collection %s'%coll_id
        })

def recordtype_create_values(type_id):
    return (
        { 'rdfs:label': 'Type testcoll/%s'%type_id
        , 'rdfs:comment': 'Annalist collection: testcoll, record type: %s'%type_id
        , 'annal:uri': '/testsite/collections/testcoll/types/%s/'%type_id
        })

def expect_value_keys():
    return (
        [ 'annal:id', 'annal:type', 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordtype_load_values(type_id):
    return (
        { '@id':            './'
        , 'annal:id':       type_id
        , 'annal:type':     'annal:RecordType'
        , 'annal:uri':      '/%s/collections/testcoll/types/%s/'%(TestBasePath, type_id)
        , 'rdfs:label':     'Type testcoll/%s'%type_id
        , 'rdfs:comment':   'Annalist collection: testcoll, record type: %s'%type_id
        })

def recordtype_form_data(type_id=None, orig_type_id=None, action=None, cancel=None):
    form_data_dict = (
        { 'type_label':       'Record type ... in collection testcoll'
        , 'type_help':        'Help for record type ...'
        , 'type_class':       '/%s/collections/testcoll/.../'%TestBasePath
        , 'orig_type_id':     'orig_type_id'
        , 'continuation_uri': '/%s/collections/testcoll/'%TestBasePath
        })
    if type_id:
        form_data_dict['type_id']       = type_id
        form_data_dict['orig_type_id']  = type_id
        form_data_dict['type_label']    = 'Record type %s in collection testcoll'%(type_id)
        form_data_dict['type_help']     = 'Help for record type %s'%(type_id)
        form_data_dict['type_class']    = '/%s/collections/testcoll/types/%s/'%(TestBasePath, type_id)
    if orig_type_id:
        form_data_dict['orig_type_id']  = orig_type_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

def recordtype_context_data(type_id=None, orig_type_id=None, action=None):
    context_dict = (
        { 'title':              'Annalist data journal test site'
        , 'coll_id':            'testcoll'
        , 'orig_type_id':       'orig_type_id'
        , 'type_label':         'Record type ... in collection testcoll'
        , 'type_help':          'Help for record type ...'
        , 'type_uri':           '/%s/collections/testcoll/.../'%TestBasePath
        , 'continuation_uri':   '/%s/collections/testcoll/'%TestBasePath
        })
    if type_id:
        context_dict['type_id']       = type_id
        context_dict['orig_type_id']  = type_id
        context_dict['type_label']    = 'Record type %s in collection testcoll'%(type_id)
        context_dict['type_help']     = 'Help for record type %s'%(type_id)
        context_dict['type_uri']      = '/%s/collections/testcoll/types/%s/'%(TestBasePath, type_id)
    if orig_type_id:
        context_dict['orig_type_id']  = orig_type_id
    if action:  
        context_dict['action']  = action
    return context_dict

def recordtype_updated_values(type_id):
    return (
        { '@id':            './'
        , 'annal:id':       type_id
        , 'annal:type':     'annal:RecordType'
        , 'annal:uri':      '/%s/collections/testcoll/types/%s/'%(TestBasePath, type_id)
        , 'rdfs:label':     'Record type %s in collection testcoll'%type_id
        , 'rdfs:comment':   'Help for record type %s'%type_id
        })

def recordtype_delete_confirm_values(coll_id, type_id):
    return (
        { "foo": "bar"
        })

#   -----------------------------------------------------------------------------
#
#   RecordType tests
#
#   -----------------------------------------------------------------------------

class RecordTypeTest(TestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
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
        self.assertEqual(t._entityuri,      TestBaseUri+"/collections/testcoll/types/testtype/")
        self.assertEqual(t._entitydir,      TestBaseDir+"/collections/testcoll/types/testtype/")
        self.assertEqual(t._values,         None)
        return

    def test_recordtype1_data(self):
        t = RecordType(self.testcoll, "type1")
        t.set_values(recordtype_create_values("type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(expect_value_keys()))
        v = recordtype_load_values("type1")
        self.assertEqual(td, {k:v[k] for k in expect_value_keys()})
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2")
        t.set_values(recordtype_create_values("type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(expect_value_keys()))
        v = recordtype_load_values("type2")
        self.assertEqual(td, {k:v[k] for k in expect_value_keys()})
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", recordtype_create_values("type1"))
        td = RecordType.load(self.testcoll, "type1").get_values()
        v = recordtype_load_values("type1")
        self.assertEqual(td, v)
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
        t = RecordType.create(self.testcoll, type_id, recordtype_create_values(type_id))
        return t    

    def _check_record_type_values(self, type_id):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%type_id)
        self._assert_dict_match(t.get_values(), recordtype_load_values(type_id))
        return t

    def _check_updated_record_type_values(self, type_id):
        "Helper function checks content of form-updated record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%type_id)
        self._assert_dict_match(t.get_values(), recordtype_updated_values(type_id))
        return t

    def _assert_dict_match(self, actual_dict, expect_dict):
        for k in expect_dict:
            self.assertTrue(k in actual_dict, "Expected key %s not found in actual"%(k))
            self.assertEqual(actual_dict[k], expect_dict[k], 
                "Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_RecordTypeEditView(self):
        self.assertEqual(RecordTypeEditView.__name__, "RecordTypeEditView", "Check RecordTypeEditView class name")
        return

    def test_get_new(self):
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "coll1", 'action': 'new'}
                )+"?continuation_uri=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "00000001")
        self.assertEqual(r.context['orig_type_id'],     "00000001")
        self.assertEqual(r.context['type_label'],       "Record type 00000001 in collection coll1")
        self.assertEqual(r.context['type_help'],        "")
        self.assertEqual(r.context['type_uri'],         "/%s/collections/coll1/00000001/"%(TestBasePath))
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        return

    def test_get_copy(self):
        u = reverse(
                "AnnalistRecordTypeCopyView", 
                kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'copy'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_type_id'],     "type1")
        self.assertEqual(r.context['type_label'],       "Record type coll1/type1")
        self.assertEqual(r.context['type_help'],        "Annalist collection1 recordtype1")
        self.assertEqual(r.context['type_uri'],         "http://localhost:8000/annalist/collections/coll1/types/type1/")
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    def test_get_copy_not_exists(self):
        u = reverse(
                "AnnalistRecordTypeCopyView", 
                kwargs={'coll_id': "coll1", 'type_id': 'notype', 'action': 'copy'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Record type notype in collection coll1 does not exist</p>", status_code=404)
        return

    def test_get_edit(self):
        u = reverse(
                "AnnalistRecordTypeEditView", 
                kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'edit'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_type_id'],     "type1")
        self.assertEqual(r.context['type_label'],       "Record type coll1/type1")
        self.assertEqual(r.context['type_help'],        "Annalist collection1 recordtype1")
        self.assertEqual(r.context['type_uri'],         "http://localhost:8000/annalist/collections/coll1/types/type1/")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_form_data(type_id="newtype", action="new")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_record_type_values("newtype")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_form_data(type_id="newtype", action="new", cancel="Cancel")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = recordtype_form_data(action="new")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(action="new")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = recordtype_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        self._assert_dict_match(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_form_data(type_id="copytype", action="copy")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_record_type_values("copytype")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_form_data(type_id="copytype", action="copy", cancel="Cancel")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = recordtype_form_data(action="copy")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = recordtype_context_data(action="copy")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_copy_type_invalid_id(self):
        f = recordtype_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="copy")
        u = recordtype_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = recordtype_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="copy")
        self._assert_dict_match(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_form_data(type_id="edittype", action="edit")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        self._check_updated_record_type_values("edittype")
        return

    def test_post_edit_type_new_id(self):
        self._create_record_type("edittype1")
        self._check_record_type_values("edittype1")
        # Now post edit form submission with different values and new id
        f = recordtype_form_data(type_id="edittype2", orig_type_id="edittype1", action="edit")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists and old does not
        self.assertFalse(RecordType.exists(self.testcoll, "edittype1"))
        self._check_updated_record_type_values("edittype2")
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Post from cancelled edit form
        f = recordtype_form_data(type_id="edittype", action="edit", cancel="Cancel")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = recordtype_form_data(action="edit")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context for re-rendered form
        expect_context = recordtype_context_data(action="edit")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_edit_type_invalid_id(self):
        f = recordtype_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="edit")
        u = recordtype_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = recordtype_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="edit")
        self._assert_dict_match(r.context, expect_context)
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
        u = recordtype_delete_confirm_uri("testcoll")
        f = recordtype_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+collection_edit_uri("testcoll")+r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordType.exists(self.testcoll, "deletetype"))
        return

# End.
