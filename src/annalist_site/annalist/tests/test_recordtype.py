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
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'new'}
                )
        form_data = (
            { 'type_id':          'newtype'
            , 'type_label':       'Record type newtype in collection testcoll'
            , 'type_help':        'Help for newtype'
            , 'type_class':       '/%s/collections/testcoll/newtype/'%TestBasePath
            , 'save':             'Save'
            , 'orig_type_id':     'newtype'
            , 'continuation_uri': '/%s/collections/testcoll/'%TestBasePath
            , 'action':           'new'
            })
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        r = self.client.post(u, form_data)
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
            , 'rdfs:comment':   'Help for newtype'
            , 'annal:uri':      '/testsite/collections/testcoll/newtype/'
            })
        v = t.get_values()
        for k in expect_values:
            self.assertEqual(v[k], expect_values[k])
        return

    # @@ cancel new type form

    # @@ Post with missing/invalid type id


    def test_post_copy_type(self):
        u = reverse(
                "AnnalistRecordTypeNewView", 
                kwargs={'coll_id': "testcoll", 'action': 'copy'}
                )
        form_data = (
            { 'type_id':          'copytype'
            , 'type_label':       'Record type copytype in collection testcoll'
            , 'type_help':        'Help for copytype'
            , 'type_class':       '/%s/collections/testcoll/copyttype/'%TestBasePath
            , 'save':             'Save'
            , 'orig_type_id':     'copytype'
            , 'continuation_uri': '/%s/collections/testcoll/'%TestBasePath
            , 'action':           'copy'
            })
        r = self.client.post(u, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        collectionedituri = reverse(
                "AnnalistCollectionEditView", 
                kwargs={'coll_id': "testcoll"}
                )
        self.assertEqual(r['location'], TestHostUri+collectionedituri)
        return

        # Cancel copy form

        # Copy without type selected

        # edit type

        # confirm delete type

    def test_post_close(self):
        form_data = (
            { "close":  "Close"
            })
        r = self.client.post(self.uri_edit, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        siteviewuri = reverse("AnnalistSiteView")
        self.assertEqual(r['location'], TestHostUri+siteviewuri)
        return

# End.
