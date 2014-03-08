"""
Tests for entity module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist.identifiers       import ANNAL
from annalist.models.entity     import EntityRoot, Entity

from tests                      import TestBaseUri, TestBaseDir, dict_to_str, init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase

#   -----------------------------------------------------------------------------
#
#   EntityRoot tests
#
#   -----------------------------------------------------------------------------

class TestEntityRootType(EntityRoot):

    _entitytype = "test:EntityRootType"
    _entitypath = None
    _entityfile = ".sub/manifest.jsonld"
    _entityref  = "../"

class EntityRootTest(TestCase):
    """
    Tests for EntityRoot object interface
    """

    def setUp(self):
        init_annalist_test_site()
        return

    def tearDown(self):
        return

    def test_EntityRootTest(self):
        self.assertEqual(EntityRootTest.__name__, "EntityRootTest", "Check class name")
        return

    def test_entityroot_init(self):
        e = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertEqual(e._entitytype,     ANNAL.CURIE.EntityRoot)
        self.assertEqual(e._entityfile,     None)
        self.assertEqual(e._entityref,      None)
        self.assertEqual(e._entityid,       None)
        self.assertEqual(e._entityuri,      TestBaseUri+"/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/")
        self.assertEqual(e._values,         None)
        return

    def test_entityroot_id(self):
        e = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertEqual(e.get_id(),        None)
        e.set_id("testId")
        self.assertEqual(e.get_id(),        "testId")
        return

    def test_entityroot_values(self):
        test_values1 = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            , 'uri':    '/annalist/coll1'
            })
        test_values1_returned = (
            { 'annal:id':   None
            , 'annal:type': 'annal:EntityRoot'
            , 'annal:uri': TestBaseUri+'/'
            , 'type':  'annal:EntityRoot'
            , 'title': 'Name collection coll1'
            , 'uri':   '/annalist/coll1'
            })
        test_values2 = (
            { 'id':         'TestId'
            , 'type':       'annal:EntityRoot'
            , 'rdfs:label': 'Name collection coll2'
            , 'uri':        '/annalist/coll2'
            })
        test_values2_returned = (
            { 'annal:id':   None
            , 'annal:type': 'annal:EntityRoot'
            , 'annal:uri': TestBaseUri+'/'
            , 'id':         'TestId'
            , 'type':  'annal:EntityRoot'
            , 'rdfs:label': 'Name collection coll2'
            , 'uri':   '/annalist/coll2'
            })
        e = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertEqual(e.get_values(),    None)
        e.set_values(test_values1)
        self.assertEqual(e.get_values(),    test_values1_returned)
        e.set_values(test_values2)
        self.assertEqual(e.get_values(),    test_values2_returned)
        return

    def test_entityroot_indexing(self):
        test_values1 = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            , 'uri':    '/annalist/coll1'
            })
        test_values1_returned = (
            { 'annal:id':   None
            , 'annal:type': 'annal:EntityRoot'
            , 'type':       'annal:EntityRoot'
            , 'annal:uri':  TestBaseUri+'/'
            , 'title':      'Name collection coll1'
            , 'uri':        '/annalist/coll1'
            })
        test_values2_returned = (
            { 'annal:id':   None
            , 'annal:type': 'annal:EntityRoot'
            , 'annal:uri':  TestBaseUri+'/'
            , 'id':         'testid'
            , 'type':       'annal:EntityRoot'
            , 'title':      'new title'
            , 'uri':        '/annalist/coll2'
            })
        e = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertEqual(e.get_values(),    None)
        e.set_values(test_values1)
        self.assertEqual(set(e.get_values().keys()), set(test_values1_returned.keys()))
        self.assertEqual(e.get_values(),    test_values1_returned)
        for k,v in test_values1_returned.items():
            self.assertEqual(e[k], v)
        e['id']    = "testid"
        e['title'] = "new title" 
        e['uri']   = "/annalist/coll2"
        self.assertEqual(e.get_values(),    test_values2_returned)
        for k,v in test_values2_returned.items():
            self.assertEqual(e[k], v)
        return

    def test_entityroot_iter(self):
        e = EntityRoot(TestBaseUri+"/collections", TestBaseDir+"/collections")
        # e = TestEntityRootType(Te stBaseUri, TestBaseDir)
        expect = [ "coll1", "coll2", "coll3", "testcoll"]
        count = 0
        for i in e:
            self.assertIn(i, expect)
            count += 1
        self.assertEqual(count, len(expect))
        return

    def test_entityroot_subclass(self):
        e = TestEntityRootType(TestBaseUri, TestBaseDir)
        self.assertEqual(e._entitytype,     "test:EntityRootType")
        self.assertEqual(e._entityfile,     ".sub/manifest.jsonld")
        self.assertEqual(e._entityref,      "../")
        self.assertEqual(e._entityid,       None)
        self.assertEqual(e._entityuri,      TestBaseUri+"/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/")
        self.assertEqual(e._values,         None)
        self.assertEqual(e._dir_path(),     (TestBaseDir+"/.sub", TestBaseDir+"/.sub/manifest.jsonld"))
        return

    def test_entityroot_save_load(self):
        test_values = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            , 'uri':    '/annalist/coll1'
            })
        test_values_returned = (
            { '@id': '../'
            , 'annal:id': 'testId'
            , 'annal:type': 'test:EntityRootType'
            , 'annal:uri':  TestBaseUri+'/'
            , 'title': 'Name collection coll1'
            , 'type': 'annal:EntityRoot'
            , 'uri': '/annalist/coll1'
            })
        e = TestEntityRootType(TestBaseUri, TestBaseDir)
        e.set_id("testId")
        self.assertEqual(e._entitytype,     "test:EntityRootType")
        self.assertEqual(e._entityfile,     ".sub/manifest.jsonld")
        self.assertEqual(e._entityref,      "../")
        self.assertEqual(e._entityid,       "testId")
        self.assertEqual(e._entityuri,      TestBaseUri+"/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/")
        self.assertEqual(e._values,         None)
        e.set_values(test_values)
        e._save()
        e2 = TestEntityRootType(TestBaseUri, TestBaseDir)
        e2.set_id("testId")
        v2 = e2._load_values()
        self.assertEqual(set(v2.keys()), set(test_values_returned.keys()))
        self.assertEqual(v2, test_values_returned)
        return

    def test_entityroot_exists(self):
        test_values = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            , 'uri':    '/annalist/coll1'
            })
        test_values_returned = (
            { '@id': '../'
            , 'annal:id': 'testId'
            , 'annal:type': 'test:EntityRootType'
            , 'id': 'testId'
            , 'title': 'Name collection coll1'
            , 'type': 'annal:EntityRoot'
            , 'uri': '/annalist/coll1'
            })
        e = TestEntityRootType(TestBaseUri, TestBaseDir)
        e.set_id("testId")
        e.set_values(test_values)
        self.assertFalse(e._exists())
        e._save()
        self.assertTrue(e._exists())
        return

class TestEntityType(Entity):

    _entitytype = "test:EntityType"
    _entitypath = None
    _entityfile = ".sub/manifest.jsonld"
    _entityref  = "../"

class TestEntityTypeSub(Entity):

    _entitytype = "test:EntityTypeSub"
    _entitypath = "sub/%(id)s"
    _entityfile = ".sub/manifest.jsonld"
    _entityref  = "../"

#   -----------------------------------------------------------------------------
#
#   Entity tests
#
#   -----------------------------------------------------------------------------

class EntityTest(TestCase):
    """
    Tests for Entity object interface
    """

    def setUp(self):
        init_annalist_test_site()
        return

    def tearDown(self):
        return

    def test_EntityTest(self):
        self.assertEqual(EntityTest.__name__, "EntityTest", "Check class name")
        return

    def test_entity_init(self):
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = Entity(r, "testid")
        self.assertEqual(e._entitytype,     ANNAL.CURIE.Entity)
        self.assertEqual(e._entityfile,     None)
        self.assertEqual(e._entityref,      None)
        self.assertEqual(e._entityid,       "testid")
        self.assertEqual(e._entityuri,      TestBaseUri+"/testid/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/testid/")
        self.assertEqual(e._values,         None)
        return

    def test_entity_subclass(self):
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityType(r, "testid")
        self.assertEqual(e._entitytype,     "test:EntityType")
        self.assertEqual(e._entityfile,     ".sub/manifest.jsonld")
        self.assertEqual(e._entityref,      "../")
        self.assertEqual(e._entityid,       "testid")
        self.assertEqual(e._entityuri,      TestBaseUri+"/testid/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/testid/")
        self.assertEqual(e._values,         None)
        self.assertEqual(e._dir_path(),     (TestBaseDir+"/testid/.sub", TestBaseDir+"/testid/.sub/manifest.jsonld"))
        return

    def test_entity_dict(self):
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityType(r, "testid")
        self.assertEqual(e.get("foo",  "bar"),    "bar")
        self.assertEqual(e.get("type", "notype"), "notype")
        test_values = (
            { 'type':   'annal:EntityRoot'
            })
        e.set_values(test_values)
        self.assertEqual(e.get("foo",  "bar"),    "bar")
        self.assertEqual(e.get("type", "notype"), "annal:EntityRoot")
        expect_keys = set(['annal:id', 'annal:type', 'annal:uri', 'type'])
        self.assertEqual(set(e.keys()), expect_keys)
        expect_items = set(
            [ ('annal:id', 'testid')
            , ('annal:type', 'test:EntityType')
            , ('annal:uri',  TestBaseUri+'/testid/')
            , ('type', 'annal:EntityRoot')
            ])
        self.assertEqual(set(e.items()), expect_items)
        return

    def test_entity_path(self):
        test_values = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityType(r, "testid")
        e.set_values(test_values)
        e._save()
        p = TestEntityType.path(r, "testid")
        self.assertEqual(p, TestBaseDir+"/testid/.sub/manifest.jsonld")
        return

    def test_entity_create_exists(self):
        test_values = (
            { 'type':   'test:EntityType'
            , 'title':  'Name entity test'
            })
        test_values_returned = (
            { 'annal:id': 'testid'
            , 'annal:type': 'test:EntityType'
            , 'annal:uri': TestBaseUri+'/testid/'
            , 'title': 'Name entity test'
            , 'type': 'test:EntityType'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertFalse(TestEntityType.exists(r, "testid"))
        e = TestEntityType.create(r, "testid", test_values)
        self.assertTrue(TestEntityType.exists(r, "testid"))
        v = e.get_values()
        self.assertEqual(set(v.keys()), set(test_values_returned.keys()))
        self.assertEqual(v, test_values_returned)
        return

    def test_entity_create_load(self):
        test_values = (
            { 'type':   'test:EntityType'
            , 'title':  'Name entity test2'
            })
        test_values_returned = (
            { '@id':        '../'
            , 'annal:id':   'testid2'
            , 'annal:type': 'test:EntityType'
            , 'annal:uri':  TestBaseUri+'/testid2/'
            , 'title': 'Name entity test2'
            , 'type': 'test:EntityType'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityType.create(r, "testid2", test_values)
        e2 = TestEntityType.load(r, "testid2")
        v = e2.get_values()
        self.assertEqual(set(v.keys()), set(test_values_returned.keys()))
        self.assertEqual(v, test_values_returned)
        return

    def test_entity_create_remove(self):
        test_values = (
            { 'type':   'test:EntityType'
            , 'title':  'Name entity test'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertFalse(TestEntityType.exists(r, "testid3"))
        e = TestEntityType.create(r, "testid3", test_values)
        self.assertTrue(TestEntityType.exists(r, "testid3"))
        s = TestEntityType.remove(r, "testid3")
        self.assertFalse(TestEntityType.exists(r, "testid3"))
        return

    # The following tests repeat the above using an entity class with 
    # an explcit relative path from parent to entity.

    def test_entity_sub_path(self):
        test_values = (
            { 'type':   'annal:EntityRoot'
            , 'title':  'Name collection coll1'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityTypeSub(r, "testid")
        self.assertEqual(e._entitydir, TestBaseDir+"/sub/testid/")
        e.set_values(test_values)
        e._save()
        p = TestEntityTypeSub.path(r, "testid")
        self.assertEqual(p, TestBaseDir+"/sub/testid/.sub/manifest.jsonld")
        return

    def test_entity_sub_create_exists(self):
        test_values = (
            { 'type':   'test:EntityType'
            , 'title':  'Name entity test'
            })
        test_values_returned = (
            { 'annal:id': 'testid'
            , 'annal:type': 'test:EntityTypeSub'
            , 'annal:uri':  TestBaseUri+'/sub/testid/'
            , 'title': 'Name entity test'
            , 'type': 'test:EntityType'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertFalse(TestEntityTypeSub.exists(r, "testid"))
        e = TestEntityTypeSub.create(r, "testid", test_values)
        self.assertTrue(TestEntityTypeSub.exists(r, "testid"))
        p = TestEntityTypeSub.path(r, "testid")
        self.assertEqual(p, TestBaseDir+"/sub/testid/.sub/manifest.jsonld")
        v = e.get_values()
        self.assertEqual(set(v.keys()), set(test_values_returned.keys()))
        self.assertEqual(v, test_values_returned)
        return

    def test_entity_sub_create_load(self):
        test_values = (
            { 'type':   'test:EntityTypeSub'
            , 'title':  'Name entity test2'
            })
        test_values_returned = (
            { '@id':        '../'
            , 'annal:id':   'testid2'
            , 'annal:type': 'test:EntityTypeSub'
            , 'annal:uri':  TestBaseUri+'/sub/testid2/'
            , 'title': 'Name entity test2'
            , 'type': 'test:EntityTypeSub'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        e = TestEntityTypeSub.create(r, "testid2", test_values)
        e2 = TestEntityTypeSub.load(r, "testid2")
        v = e2.get_values()
        self.assertEqual(set(v.keys()), set(test_values_returned.keys()))
        self.assertEqual(v, test_values_returned)
        return

    def test_entity_sub_create_remove(self):
        test_values = (
            { 'type':   'test:EntityTypeSub'
            , 'title':  'Name entity test'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertFalse(TestEntityTypeSub.exists(r, "testid3"))
        e = TestEntityTypeSub.create(r, "testid3", test_values)
        self.assertTrue(TestEntityTypeSub.exists(r, "testid3"))
        s = TestEntityTypeSub.remove(r, "testid3")
        self.assertFalse(TestEntityTypeSub.exists(r, "testid3"))
        return

    def test_entity_allocate_id(self):
        test_values = (
            { 'type':   'test:EntityType'
            , 'title':  'Name entity test'
            })
        r = EntityRoot(TestBaseUri, TestBaseDir)
        eid = TestEntityType.allocate_new_id(r)
        self.assertEqual(eid, "00000001")
        self.assertFalse(TestEntityType.exists(r, eid))
        eid = TestEntityType.allocate_new_id(r)
        self.assertEqual(eid, "00000001")
        e = TestEntityType.create(r, eid, test_values)
        self.assertTrue(TestEntityType.exists(r, eid))
        eid = TestEntityType.allocate_new_id(r)
        self.assertEqual(eid, "00000002")
        return

# End.
