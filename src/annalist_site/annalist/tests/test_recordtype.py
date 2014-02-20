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
from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType

import annalist.views
from annalist.views.recordtype  import RecordTypeEditView

from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                      import dict_to_str, init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase

class RecordTypeTest(TestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.type1_add = (
            { 'rdfs:comment': 'Annalist collection1 recordtype1'
            , 'rdfs:label': 'Type testcoll/type1'
            , 'annal:uri': TestBaseUri+'/collections/testcoll/types/type1/'
            })      
        self.expect_value_keys = (
            'id', 'type', 'uri', 'title', 'rdfs:label', 'rdfs:comment', 'annal:uri'
            )
        self.type1 = (
            { '@id': './'
            , 'id': 'type1'
            , 'title': 'Type testcoll/type1'
            , 'type': 'annal:RecordType'
            , 'uri': 'http://test.example.com/testsite/collections/testcoll/types/type1/'
            , 'annal:id': 'type1'
            , 'annal:type': 'annal:RecordType'
            , 'annal:uri': TestBaseUri+'/collections/testcoll/types/type1/'
            , 'rdfs:label': 'Type testcoll/type1'
            , 'rdfs:comment': 'Annalist collection1 recordtype1'
            })
        self.type2_add = (
            { 'rdfs:comment': 'Annalist collection1 recordtype2'
            , 'rdfs:label': 'Type testcoll/type2'
            , 'annal:uri': TestBaseUri+'/collections/testcoll/types/type2/'
            })      
        self.type2 = (
            { '@id': './'
            , 'id': 'type2'
            , 'title': 'Type testcoll/type2'
            , 'type': 'annal:RecordType'
            , 'uri': 'http://test.example.com/testsite/collections/testcoll/types/type2/'
            , 'annal:id': 'type2'
            , 'annal:type': 'annal:RecordType'
            , 'annal:uri': TestBaseUri+'/collections/testcoll/types/type2/'
            , 'rdfs:label': 'Type testcoll/type2'
            , 'rdfs:comment': 'Annalist collection1 recordtype2'
            })
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
        t.set_values(self.type1_add)
        td = t.get_values()
        self.assertEqual(set(td.keys()),set(self.expect_value_keys))
        # Note: some values are added when entity is saved, so just compare those here
        self.assertEqual(td, {k:self.type1[k] for k in self.expect_value_keys})
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2")
        t.set_values(self.type2_add)
        td = t.get_values()
        self.assertEqual(set(td.keys()),set(self.expect_value_keys))
        # Note: some values are added when entity is saved, so just compare those here
        self.assertEqual(td, {k:self.type2[k] for k in self.expect_value_keys})
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", self.type1_add)
        td = RecordType.load(self.testcoll, "type1").get_values()
        self.assertEqual(set(td.keys()),set(self.type1.keys()))
        self.assertEqual(td, self.type1)
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
        self.testcoll = Collection.create(self.testsite, "testcoll",
            { 'rdfs:label':     'Collection testcoll'
            , 'rdfs:comment':   'Description of Collection testcoll'
            })
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def form_data(self, type_id=None, orig_type_id=None, action=None, cancel=None):
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
            form_data_dict['type_class']    = '/%s/collections/testcoll/%s/'%(TestBasePath, type_id)
        if orig_type_id:
            form_data_dict['orig_type_id']  = orig_type_id
        if action:
            form_data_dict['action']        = action
        if cancel:
            form_data_dict['cancel']        = "Cancel"
        else:
            form_data_dict['save']          = 'Save'
        return form_data_dict

    def context_data(self, type_id=None, orig_type_id=None, action=None):
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
            context_dict['type_uri']      = '/%s/collections/testcoll/%s/'%(TestBasePath, type_id)
        if orig_type_id:
            context_dict['orig_type_id']  = orig_type_id
        if action:  
            context_dict['action']  = action
        return context_dict

    def assert_dict_match(self, actual_dict, expect_dict):
        for k in expect_dict:
            self.assertTrue(k in actual_dict, "Expected key %s not found in actual"%(k))
            self.assertEqual(actual_dict[k], expect_dict[k], 
                "Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        return

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

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = self.form_data(type_id="newtype", action="new")
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'new'}
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        collectionedituri = reverse(
                "AnnalistCollectionEditView", 
                kwargs={'coll_id': "testcoll"}
                )
        self.assertEqual(r['location'], TestHostUri+collectionedituri)
        # Check that new record type exists
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        # Check values in new type
        t = RecordType.load(self.testcoll, "newtype")
        self.assertEqual(t.get_id(), "newtype")
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/newtype/")
        expect_values = (
            { '@id':            './'
            , 'annal:id':       'newtype'
            , 'annal:type':     'annal:RecordType'
            , 'rdfs:label':     'Record type newtype in collection testcoll'
            , 'rdfs:comment':   'Help for record type newtype'
            , 'annal:uri':      '/testsite/collections/testcoll/newtype/'
            })
        self.assert_dict_match(t.get_values(), expect_values)
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = self.form_data(type_id="newtype", action="new", cancel="Cancel")
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'new'}
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        collectionedituri = reverse(
                "AnnalistCollectionEditView", 
                kwargs={'coll_id': "testcoll"}
                )
        self.assertEqual(r['location'], TestHostUri+collectionedituri)
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = self.form_data(action="new")
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'new'}
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = self.context_data(action="new")
        self.assert_dict_match(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = self.form_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'new'}
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = self.context_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        self.assert_dict_match(r.context, expect_context)
        return

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = self.form_data(type_id="copytype", action="copy")
        u = reverse(
                "AnnalistRecordTypeCopyView", 
                kwargs={'coll_id': "testcoll", 'type_id': "copytype", 'action': 'copy'}
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        collectionedituri = reverse(
                "AnnalistCollectionEditView", 
                kwargs={'coll_id': "testcoll"}
                )
        self.assertEqual(r['location'], TestHostUri+collectionedituri)
        # Check that new record type exists
        self.assertTrue(RecordType.exists(self.testcoll, "copytype"))
        # Check values in new type
        t = RecordType.load(self.testcoll, "copytype")
        self.assertEqual(t.get_id(), "copytype")
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/copytype/")
        expect_values = (
            { '@id':            './'
            , 'annal:id':       'copytype'
            , 'annal:type':     'annal:RecordType'
            , 'rdfs:label':     'Record type copytype in collection testcoll'
            , 'rdfs:comment':   'Help for record type copytype'
            , 'annal:uri':      '/testsite/collections/testcoll/copytype/'
            })
        self.assert_dict_match(t.get_values(), expect_values)
        return

        # Cancel copy form

        # Copy without type selected

        # edit type

        # confirm delete type

# End.
