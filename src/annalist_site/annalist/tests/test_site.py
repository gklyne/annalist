"""
Tests for site module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf        import settings
from django.test        import TestCase
from django.test.client import Client

from miscutils.MockHttpResources import MockHttpFileResources, MockHttpDictResources

from annalist.site      import Site, SiteView
from annalist.layout    import Layout

from tests              import TestBaseDir, dict_to_str, init_annalist_test_site

class SiteTest(TestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        self.coll1 = (
            { '@id': '../'
            , 'id': 'coll1'
            , 'title': 'Name collection coll1'
            , 'uri': 'http://example.com/testsite/coll1'
            , 'annal:id': 'coll1'
            , 'annal:type': 'annal:Collection'
            , 'rdfs:comment': 'Annalist collection metadata.'
            , 'rdfs:label': 'Name collection coll1'
            })        
        self.collnewmeta = (
            { 'rdfs:label': 'Collection new'
            , 'rdfs:comment': 'Annalist new collection metadata.'
            })        
        self.collnew = (
            { '@id': '../'
            , 'id': 'new'
            , 'title': 'Collection new'
            , 'uri': 'http://example.com/testsite/new'
            , 'annal:id': 'new'
            , 'annal:type': 'annal:Collection'
            , 'rdfs:comment': 'Annalist new collection metadata.'
            , 'rdfs:label': 'Collection new'
            })        
        return

    def tearDown(self):
        return

    @unittest.skip("Skip placeholder")
    def test_SiteTest(self):
        self.assertEqual(Site.__name__, "Site", "Check Site class name")
        return

    def test_site_data(self):
        sd = self.testsite.site_data()
        self.assertEquals(set(sd.keys()),set(('rdfs:label', 'rdfs:comment', 'collections', 'title')))
        self.assertEquals(sd["title"],        "Annalist data journal test site")
        self.assertEquals(sd["rdfs:label"],   "Annalist data journal test site")
        self.assertEquals(sd["rdfs:comment"], "Annalist site metadata.")
        self.assertEquals(sd["collections"].keys(),  ["coll1","coll2","coll3"])
        self.assertEquals(dict_to_str(sd["collections"]["coll1"]),  self.coll1)
        return

    def test_collections_dict(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.assertEquals(dict_to_str(colls["coll1"]),  self.coll1)
        return

    def test_add_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.testsite.add_collection("new", self.collnewmeta)
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3","new"])
        self.assertEquals(dict_to_str(colls["coll1"]), self.coll1)
        self.assertEquals(dict_to_str(colls["new"]),   self.collnew)
        return

    def test_remove_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.testsite.remove_collection("coll2")
        collsb = self.testsite.collections_dict()
        self.assertEquals(collsb.keys(),["coll1","coll3"])
        self.assertEquals(dict_to_str(colls["coll1"]),  self.coll1)
        return


class SiteViewTest(TestCase):
    """
    Tests for Site views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        return

    def tearDown(self):
        return

    def test_SiteViewTest(self):
        self.assertEqual(SiteView.__name__, "SiteView", "Check SiteView class name")
        return

    def test_get(self):
        self.assertTrue(False, "@@TODO test_get")
        return

    def test_post_add(self):
        self.assertTrue(False, "@@TODO test_post_add")
        return

    def test_post_remove(self):
        self.assertTrue(False, "@@TODO test_post_remove")
        return




class SiteActionView(TestCase):
    """
    Tests for Site action views (completion of confirmed actions
    requested from the site view)
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        return

    def tearDown(self):
        return

    def test_SiteActionViewTest(self):
        self.assertEqual(SiteActionView.__name__, "SiteActionView", "Check SiteActionView class name")
        return

    def test_post_confirmed_remove(self):
        self.assertTrue(False, "@@TODO test_post_confirmed_remove")
        return


# End.
