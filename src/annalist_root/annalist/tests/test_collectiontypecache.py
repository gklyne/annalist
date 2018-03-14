"""
Tests for collection type cache class.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from AnnalistTestCase                       import AnnalistTestCase
from tests                                  import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from init_tests                             import (
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from entity_testtypedata                    import (
    recordtype_coll_url, recordtype_url, recordtype_edit_url,
    recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, recordtype_values, recordtype_read_values,
    recordtype_delete_confirm_form_data
    )

from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordtype             import RecordType
from annalist.models.collectiontypecache    import CollectionTypeCache

#   -----------------------------------------------------------------------------
#
#   CollectionTypeCache tests
#
#   -----------------------------------------------------------------------------

class CollectionTypeCacheTest(AnnalistTestCase):
    """
    Tests for collection type and supertype cache classes.
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        self.testcoll1_a = Collection(self.testsite, "testcoll1")
        self.testcoll1_b = Collection(self.testsite, "testcoll1")
        self.testcoll2_a = Collection(self.testsite, "testcoll2")
        self.testcoll2_b = Collection(self.testsite, "testcoll2")
        self.typecache   = CollectionTypeCache()
        self.type1       = RecordType(self.testcoll1_a, "type1")
        self.type1.set_values(
            recordtype_create_values(type_id="type1", type_uri="test:type1", 
                supertype_uris=[]
                )
            )
        self.type11      = RecordType(self.testcoll1_a, "type11")
        self.type11.set_values(
            recordtype_create_values(type_id="type11", type_uri="test:type11", 
                supertype_uris=["test:type1"]
                )
            )
        self.type111     = RecordType(self.testcoll1_a, "type111")
        self.type111.set_values(
            recordtype_create_values(type_id="type111", type_uri="test:type111", 
                supertype_uris=["test:type11"]
                )
            )
        self.type12      = RecordType(self.testcoll1_a, "type12")
        self.type12.set_values(
            recordtype_create_values(type_id="type12", type_uri="test:type12", 
                supertype_uris=["test:type1"]
                )
            )
        self.type2       = RecordType(self.testcoll1_a, "type2")
        self.type2.set_values(
            recordtype_create_values(type_id="type2", type_uri="test:type2", 
                supertype_uris=[]
                )
            )
        self.type21      = RecordType(self.testcoll1_a, "type21")
        self.type21.set_values(
            recordtype_create_values(type_id="type21", type_uri="test:type21", 
                supertype_uris=["test:type2"]
                )
            )
        self.type22      = RecordType(self.testcoll1_a, "type22")
        self.type22.set_values(
            recordtype_create_values(type_id="type22", type_uri="test:type22", 
                supertype_uris=["test:type2"]
                )
            )
        return

    def create_type_record(self, coll, type_entity):
        return RecordType.create(coll, type_entity.get_id(), type_entity.get_values())

    def create_test_type_entities(self):
        # Create type records in collection data
        self.create_type_record(self.testcoll1_a, self.type1)
        self.create_type_record(self.testcoll1_a, self.type11)
        self.create_type_record(self.testcoll1_a, self.type111)
        self.create_type_record(self.testcoll1_a, self.type12)
        self.create_type_record(self.testcoll1_a, self.type2)
        self.create_type_record(self.testcoll1_a, self.type21)
        self.create_type_record(self.testcoll1_a, self.type22)
        # Add all types to cache
        self.typecache.set_type(self.testcoll1_a, self.type1)
        self.typecache.set_type(self.testcoll1_a, self.type11)
        self.typecache.set_type(self.testcoll1_a, self.type111)
        self.typecache.set_type(self.testcoll1_a, self.type12)
        self.typecache.set_type(self.testcoll1_a, self.type2)
        self.typecache.set_type(self.testcoll1_a, self.type21)
        self.typecache.set_type(self.testcoll1_a, self.type22)
        # Check cache content
        self.expect_site_type_ids = (
            { "_coll"
            , "_enum_list_type", "_enum_render_type", "_enum_value_mode", "_enum_value_type"
            , "_field", "_group", "_list", "_type", "_user", "_view", "_vocab"
            , "Default_type"
            })
        self.expect_coll_type_ids = (
            {"type1", "type11", "type111", "type12", "type2", "type21", "type22"}
            )
        self.expect_all_type_ids = set.union(self.expect_site_type_ids, self.expect_coll_type_ids)
        retrieve_type_ids = set(t.get_id() for t in self.typecache.get_all_types(self.testcoll1_a))
        self.assertEqual(retrieve_type_ids, self.expect_coll_type_ids)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    def test_empty_cache(self):
        self.assertEqual(set(self.typecache.get_all_types(self.testcoll1_a)), set())
        self.assertEqual(set(self.typecache.get_all_types(self.testcoll1_b)), set())
        self.assertEqual(set(self.typecache.get_all_types(self.testcoll2_a)), set())
        self.assertEqual(set(self.typecache.get_all_types(self.testcoll2_b)), set())
        return

    def test_singleton_cache(self):
        self.assertEqual([t.get_uri() for t in self.typecache.get_all_types(self.testcoll1_a)], [])
        # NOTE: if the 'set_type' call also causes cache initialization of all types, 
        # including the created type record which is discovered on disk, and the subsequent 
        # set_type call returns 'False'.
        self.create_type_record(self.testcoll1_a, self.type1)
        self.assertFalse(self.typecache.set_type(self.testcoll1_a, self.type1))
        # self.assertIsNone(self.testcoll1_a.remove_type("type1"))
        self.assertFalse(self.typecache.set_type(self.testcoll1_a, self.type1))
        self.assertFalse(self.typecache.set_type(self.testcoll1_b, self.type1))
        self.assertEqual(self.typecache.get_type(self.testcoll1_a, "type1").get_uri(), "test:type1")
        self.assertEqual(self.typecache.get_type(self.testcoll1_b, "type1").get_uri(), "test:type1")
        self.assertEqual(self.typecache.get_type(self.testcoll1_a, "type2"), None)
        self.assertEqual(self.typecache.get_type(self.testcoll1_b, "type2"), None)
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_a, "test:type1").get_id(), "type1")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type1").get_id(), "type1")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_a, "test:type2"), None)
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type3"), None)
        self.assertEqual([t.get_uri() for t in self.typecache.get_all_types(self.testcoll1_a)], ["test:type1"])
        self.assertEqual([t.get_uri() for t in self.typecache.get_all_types(self.testcoll1_b)], ["test:type1"])
        self.assertEqual([t.get_uri() for t in self.typecache.get_all_types(self.testcoll2_a)], [])
        self.assertEqual([t.get_uri() for t in self.typecache.get_all_types(self.testcoll2_b)], [])
        return

    def test_empty_cache_2(self):
        self.typecache.set_type(self.testcoll1_a, self.type1)
        self.assertIsNotNone(self.typecache.remove_type(self.testcoll1_a, "type1"))
        self.assertIsNone(self.typecache.remove_type(self.testcoll1_b, "type1"))
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll1_a)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll1_b)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll2_a)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll2_b)), [])
        return

    def test_flush_cache(self):
        self.typecache.set_type(self.testcoll1_a, self.type1)
        self.assertTrue(self.typecache.flush_cache(self.testcoll1_a))
        self.assertIsNone(self.typecache.remove_type(self.testcoll1_b, "type1"))
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll1_a)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll1_b)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll2_a)), [])
        self.assertEqual(list(self.typecache.get_all_types(self.testcoll2_b)), [])
        self.assertTrue(self.typecache.flush_cache(self.testcoll1_b))
        self.assertFalse(self.typecache.flush_cache(self.testcoll1_b))
        return

    # def test_collection_has_cache(self):
    #     # Initial state - no cache
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     # Add type: non-empty cache exists for collection
    #     self.typecache.set_type(self.testcoll1_a, self.type1)
    #     self.assertTrue(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertTrue(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     # Remove type: collection cache is empty
    #     self.assertIsNotNone(self.typecache.remove_type(self.testcoll1_a, "type1"))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     self.assertIsNone(self.typecache.remove_type(self.testcoll1_b, "type1"))
    #     # Flush cache: cache is empty, so effectively no longer exists
    #     self.assertFalse(self.typecache.flush_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     # Add type again: non-empty cache exists for collection
    #     self.typecache.set_type(self.testcoll1_a, self.type1)
    #     self.assertTrue(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertTrue(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     # Flush cache: this time returns True as non-empty cache existed
    #     self.assertTrue(self.typecache.flush_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll1_b))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_a))
    #     self.assertFalse(self.typecache.collection_has_cache(self.testcoll2_b))
    #     self.assertIsNone(self.typecache.remove_type(self.testcoll1_b, "type1"))
    #     return

    def test_get_types_by_uri(self):
        self.create_test_type_entities()
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type1").get_id(),   "type1")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type11").get_id(),  "type11")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type111").get_id(), "type111")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type12").get_id(),  "type12")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type2").get_id(),   "type2")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type21").get_id(),  "type21")
        self.assertEqual(self.typecache.get_type_from_uri(self.testcoll1_b, "test:type22").get_id(),  "type22")
        return

    def test_get_all_types_scope_coll(self):
        self.create_test_type_entities()
        type_ids = set(t.get_id() for t in self.typecache.get_all_types(self.testcoll1_a))
        self.assertEqual(type_ids, self.expect_coll_type_ids)
        type_ids = set(t.get_id() for t in self.typecache.get_all_types(self.testcoll1_b))
        self.assertEqual(type_ids, self.expect_coll_type_ids)
        return

    def test_get_all_types_scope_all(self):
        self.create_test_type_entities()
        type_ids = set(
            t.get_id() 
            for t in self.typecache.get_all_types(self.testcoll1_a, altscope="all")
            )
        self.assertEqual(type_ids, self.expect_all_type_ids)
        # type_ids = set(t.get_id() for t in self.typecache.get_all_types(self.testcoll1_b, altscope="all"))
        # self.assertEqual(type_ids, self.expect_all_type_ids)
        return

    def test_get_supertypes(self):
        self.create_test_type_entities()
        def get_supertype_uris(type_uri):
            st_entities = self.typecache.get_type_uri_supertypes(self.testcoll1_b, type_uri)
            st_uris     = [ st.get_uri() for st in st_entities ]
            return set(st_uris)
        self.assertEqual(get_supertype_uris("test:type1"),   set({}))
        self.assertEqual(get_supertype_uris("test:type11"),  {"test:type1"})
        self.assertEqual(get_supertype_uris("test:type111"), {"test:type1", "test:type11"})
        self.assertEqual(get_supertype_uris("test:type12"),  {"test:type1"})
        self.assertEqual(get_supertype_uris("test:type2"),   set({}))
        self.assertEqual(get_supertype_uris("test:type21"),  {"test:type2"})
        self.assertEqual(get_supertype_uris("test:type22"),  {"test:type2"})
        return

    def test_get_subtypes(self):
        self.create_test_type_entities()
        def get_subtype_uris(type_uri):
            st_entities = self.typecache.get_type_uri_subtypes(self.testcoll1_b, type_uri)
            st_uris     = [ st.get_uri() for st in st_entities ]
            return set(st_uris)
        self.assertEqual(get_subtype_uris("test:type1"),   {"test:type11", "test:type111", "test:type12"})
        self.assertEqual(get_subtype_uris("test:type11"),  {"test:type111"})
        self.assertEqual(get_subtype_uris("test:type111"), set({}))
        self.assertEqual(get_subtype_uris("test:type12"),  set({}))
        self.assertEqual(get_subtype_uris("test:type2"),   {"test:type21", "test:type22"})
        self.assertEqual(get_subtype_uris("test:type21"),  set({}))
        self.assertEqual(get_subtype_uris("test:type22"),  set({}))
        return

    def test_update_supertype(self):
        self.create_test_type_entities()
        def get_supertype_uris(type_uri):
            st_entities = self.typecache.get_type_uri_supertypes(self.testcoll1_b, type_uri)
            st_uris     = [ st.get_uri() for st in st_entities ]
            return set(st_uris)
        self.assertEqual(get_supertype_uris("test:type1"),   set({}))
        self.assertEqual(get_supertype_uris("test:type11"),  {"test:type1"})
        self.assertEqual(get_supertype_uris("test:type111"), {"test:type1", "test:type11"})
        self.assertEqual(get_supertype_uris("test:type12"),  {"test:type1"})
        # Update super/sub-type
        self.typecache.remove_type(self.testcoll1_a, "type11")
        self.typecache.set_type(self.testcoll1_a, self.type11)
        # Re-check supertypes
        self.assertEqual(get_supertype_uris("test:type1"),   set({}))
        self.assertEqual(get_supertype_uris("test:type11"),  {"test:type1"})
        self.assertEqual(get_supertype_uris("test:type111"), {"test:type1", "test:type11"})
        self.assertEqual(get_supertype_uris("test:type12"),  {"test:type1"})
        return

    def test_update_subtype(self):
        self.create_test_type_entities()
        def get_subtype_uris(type_uri):
            st_entities = self.typecache.get_type_uri_subtypes(self.testcoll1_b, type_uri)
            st_uris     = [ st.get_uri() for st in st_entities ]
            return set(st_uris)
        self.assertEqual(get_subtype_uris("test:type1"),   {"test:type11", "test:type111", "test:type12"})
        self.assertEqual(get_subtype_uris("test:type11"),  {"test:type111"})
        self.assertEqual(get_subtype_uris("test:type111"), set({}))
        self.assertEqual(get_subtype_uris("test:type12"),  set({}))
        # Update super/sub-type
        self.typecache.remove_type(self.testcoll1_a, "type11")
        self.typecache.set_type(self.testcoll1_a, self.type11)
        # Re-check subtypes
        self.assertEqual(get_subtype_uris("test:type1"),   {"test:type11", "test:type111", "test:type12"})
        self.assertEqual(get_subtype_uris("test:type11"),  {"test:type111"})
        self.assertEqual(get_subtype_uris("test:type111"), set({}))
        self.assertEqual(get_subtype_uris("test:type12"),  set({}))
        return

if __name__ == "__main__":
    # import django
    # django.setup()  # Needed for template loader
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()

# End.
