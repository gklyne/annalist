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

from annalist.views.recordtype  import RecordTypeEditView

from tests                      import TestHost, TestHostUri, TestBaseUri, TestBaseDir
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
    Tests for Collection views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        uriargs         = {'coll_id': "coll1", 'action': 'new'}
        self.uri_new    = reverse("AnnalistRecordTypeNewView", kwargs=uriargs)
        uriargs.update(type_id='type1', action='copy')
        self.uri_copy   = reverse("AnnalistRecordTypeCopyView", kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'copy'})
        uriargs.update(action='edit')
        self.uri_edit   = reverse("AnnalistRecordTypeCopyView", kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'copy'})
        uriargs.update(action='delete')
        self.uri_delete = reverse("AnnalistRecordTypeCopyView", kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'copy'})
        self.client     = Client(HTTP_HOST=TestHost)
        return

    def tearDown(self):
        return

    def test_RecordTypeEditView(self):
        self.assertEqual(RecordTypeEditView.__name__, "RecordTypeEditView", "Check RecordTypeEditView class name")
        return

    def test_get_new(self):
        r = self.client.get(self.uri_new)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        return

    def test_get_copy(self):
        r = self.client.get(self.uri_new)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        return

    def test_get_edit(self):
        r = self.client.get(self.uri_new)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        return

    def test_get_delete(self):
        r = self.client.get(self.uri_new)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Customize collection coll1</h3>")
        return

    # def test_get_context(self):
    #     r = self.client.get(self.uri)
    #     self.assertEqual(r.status_code,   200)
    #     self.assertEqual(r.reason_phrase, "OK")
    #     self.assertEquals(r.context['title'],   "Annalist data journal test site")
    #     self.assertEquals(r.context['coll_id'], "coll1")
    #     self.assertEquals(r.context['types'],   ["type1", "type2"])
    #     self.assertEquals(r.context['lists'],   ["list1", "list2"])
    #     self.assertEquals(r.context['views'],   ["view1", "view2"])
    #     self.assertEquals(r.context['select_rows'], "6")
    #     return

    def test_post_new_type(self):
        form_data = (
            { "type_new":   "New"
            })
        r = self.client.post(self.uri, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        typenewuri = reverse(
            "AnnalistTypeNewView", 
            kwargs={'coll_id': "coll1", 'action': "new"}
            )
        self.assertEqual(r['location'], TestHostUri+typenewuri)
        return

    def test_post_copy_type(self):
        form_data = (
            { "typelist":   "type1"
            , "type_copy":  "Copy"
            })
        r = self.client.post(self.uri, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        typecopyuri = reverse(
            "AnnalistTypeCopyView", 
            kwargs={'coll_id': "coll1", 'type_id': "type1", 'action': "copy"}
            )
        self.assertEqual(r['location'], TestHostUri+typecopyuri)
        return

    def test_post_close(self):
        form_data = (
            { "close":  "Close"
            })
        r = self.client.post(self.uri, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        siteviewuri = reverse("AnnalistSiteView")
        self.assertEqual(r['location'], TestHostUri+siteviewuri)
        return

# End.
