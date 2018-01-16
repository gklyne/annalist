"""
Tests for closure cache class.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf    import settings
from tests          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir

from AnnalistTestCase               import AnnalistTestCase

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.closurecache   import ClosureCache, Closure_Error

# Test assertion summary from http://docs.python.org/2/library/unittest.html#test-cases
#
# Method                    Checks that             New in
# assertEqual(a, b)         a == b   
# assertNotEqual(a, b)      a != b   
# assertTrue(x)             bool(x) is True  
# assertFalse(x)            bool(x) is False     
# assertIs(a, b)            a is b                  2.7
# assertIsNot(a, b)         a is not b              2.7
# assertIsNone(x)           x is None               2.7
# assertIsNotNone(x)        x is not None           2.7
# assertIn(a, b)            a in b                  2.7
# assertNotIn(a, b)         a not in b              2.7
# assertIsInstance(a, b)    isinstance(a, b)        2.7
# assertNotIsInstance(a, b) not isinstance(a, b)    2.7
#
# From AnnalistTestCase:
# self.assertMatch(string, pattern, msg=None)
# self.assertDictionaryMatch(actual_dict, expect_dict, prefix="")


#   -----------------------------------------------------------------------------
#
#   ClosureCache tests
#
#   -----------------------------------------------------------------------------

class ClosureCacheTest(AnnalistTestCase):
    """
    Tests for transitive closure calculations in ClosureCache class.
    """

    def setUp(self):
        self.testsite     = Site(TestBaseUri, TestBaseDir)
        self.testcoll     = Collection(self.testsite, "testcoll")
        self.closurecache = ClosureCache(self.testcoll.get_id(), "test:rel")
        return

    def tearDown(self):
        return

    def test_empty_closure(self):
        self.assertEqual(self.closurecache.get_collection_id(), "testcoll")
        self.assertEqual(self.closurecache.get_relation_uri(),  "test:rel")
        self.assertEqual(self.closurecache.get_values(),         set())
        self.assertEqual(self.closurecache.fwd_closure("val1"),  set())
        self.assertEqual(self.closurecache.rev_closure("val2"),  set())
        return

    def test_singleton_closure(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertEqual(self.closurecache.get_values(),        {"val1", "val2"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), {"val2"})
        self.assertEqual(self.closurecache.rev_closure("val2"), {"val1"})
        return

    def test_empty_closure_2(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertFalse(self.closurecache.add_rel("val1", "val2"))
        self.closurecache.add_rel("val1", "val2")
        self.closurecache.remove_val("val1")
        self.assertEqual(self.closurecache.get_values(),        set())
        self.assertEqual(self.closurecache.fwd_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), set())
        return

    def test_empty_closure_3(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertFalse(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.remove_val("val2"))
        self.assertFalse(self.closurecache.remove_val("val2"))
        self.assertEqual(self.closurecache.get_values(),        set())
        self.assertEqual(self.closurecache.fwd_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), set())
        return

    def test_simple_transitive_closure(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertEqual(self.closurecache.get_values(),        {"val1", "val2", "val3"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), {"val2", "val3"})
        self.assertEqual(self.closurecache.fwd_closure("val2"), {"val3"})
        self.assertEqual(self.closurecache.fwd_closure("val3"), set())
        self.assertEqual(self.closurecache.rev_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), {"val1"})
        self.assertEqual(self.closurecache.rev_closure("val3"), {"val1", "val2"})
        return

    def test_extended_transitive_closure(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertTrue(self.closurecache.add_rel("val3", "val4"))
        self.assertTrue(self.closurecache.add_rel("val3", "val5"))
        self.assertEqual(self.closurecache.get_values(),        {"val1", "val2", "val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), {"val2", "val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val2"), {"val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val3"), {"val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val4"), set())
        self.assertEqual(self.closurecache.fwd_closure("val5"), set())
        self.assertEqual(self.closurecache.rev_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), {"val1"})
        self.assertEqual(self.closurecache.rev_closure("val3"), {"val1", "val2"})
        self.assertEqual(self.closurecache.rev_closure("val4"), {"val1", "val2", "val3"})
        self.assertEqual(self.closurecache.rev_closure("val5"), {"val1", "val2", "val3"})
        return

    def test_multipath_transitive_closure(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertTrue(self.closurecache.add_rel("val2", "val4"))
        self.assertTrue(self.closurecache.add_rel("val3", "val5"))
        self.assertTrue(self.closurecache.add_rel("val4", "val5"))
        self.assertEqual(self.closurecache.get_values(),        {"val1", "val2", "val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), {"val2", "val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val2"), {"val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val3"), {"val5"})
        self.assertEqual(self.closurecache.fwd_closure("val4"), {"val5"})
        self.assertEqual(self.closurecache.fwd_closure("val5"), set())
        self.assertEqual(self.closurecache.rev_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), {"val1"})
        self.assertEqual(self.closurecache.rev_closure("val3"), {"val1", "val2"})
        self.assertEqual(self.closurecache.rev_closure("val4"), {"val1", "val2"})
        self.assertEqual(self.closurecache.rev_closure("val5"), {"val1", "val2", "val3", "val4"})
        return

    def test_multipath_closure_remove_path(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertTrue(self.closurecache.add_rel("val2", "val4"))
        self.assertTrue(self.closurecache.add_rel("val3", "val5"))
        self.assertTrue(self.closurecache.add_rel("val4", "val5"))
        self.assertTrue(self.closurecache.remove_val("val4"))
        self.assertFalse(self.closurecache.remove_val("val4"))
        self.assertEqual(self.closurecache.get_values(),        {"val1", "val2", "val3", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), {"val2", "val3", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val2"), {"val3", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val3"), {"val5"})
        self.assertEqual(self.closurecache.fwd_closure("val4"), set())
        self.assertEqual(self.closurecache.fwd_closure("val5"), set())
        self.assertEqual(self.closurecache.rev_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), {"val1"})
        self.assertEqual(self.closurecache.rev_closure("val3"), {"val1", "val2"})
        self.assertEqual(self.closurecache.rev_closure("val4"), set())
        self.assertEqual(self.closurecache.rev_closure("val5"), {"val1", "val2", "val3"})
        return

    def test_multipath_closure_remove_nexus(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertTrue(self.closurecache.add_rel("val2", "val4"))
        self.assertTrue(self.closurecache.add_rel("val3", "val5"))
        self.assertTrue(self.closurecache.add_rel("val4", "val5"))
        self.assertTrue(self.closurecache.remove_val("val2"))
        self.assertFalse(self.closurecache.remove_val("val2"))
        self.assertEqual(self.closurecache.get_values(),        {"val3", "val4", "val5"})
        self.assertEqual(self.closurecache.fwd_closure("val1"), set())
        self.assertEqual(self.closurecache.fwd_closure("val2"), set())
        self.assertEqual(self.closurecache.fwd_closure("val3"), {"val5"})
        self.assertEqual(self.closurecache.fwd_closure("val4"), {"val5"})
        self.assertEqual(self.closurecache.fwd_closure("val5"), set())
        self.assertEqual(self.closurecache.rev_closure("val1"), set())
        self.assertEqual(self.closurecache.rev_closure("val2"), set())
        self.assertEqual(self.closurecache.rev_closure("val3"), set())
        self.assertEqual(self.closurecache.rev_closure("val4"), set())
        self.assertEqual(self.closurecache.rev_closure("val5"), {"val3", "val4"})
        return

    def test_reflexive_relation(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        with self.assertRaises(Closure_Error):
            self.closurecache.add_rel("val1", "val1")
        with self.assertRaises(Closure_Error):
            self.closurecache.add_rel("val2", "val2")
        self.assertEqual(self.closurecache.get_values(), {"val1", "val2"})
        return

    def test_recursive_relation(self):
        self.assertTrue(self.closurecache.add_rel("val1", "val2"))
        self.assertTrue(self.closurecache.add_rel("val2", "val3"))
        self.assertTrue(self.closurecache.add_rel("val3", "val4"))
        self.assertTrue(self.closurecache.add_rel("val3", "val5"))
        with self.assertRaises(Closure_Error):
            self.closurecache.add_rel("val5", "val1")
        with self.assertRaises(Closure_Error):
            self.closurecache.add_rel("val3", "val2")
        self.assertEqual(self.closurecache.get_values(), {"val1", "val2", "val3", "val4", "val5"})
        return

# End.
