from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Tests for collection field and superproperty cache classes.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordfield            import RecordField
from annalist.models.collectionfieldcache   import CollectionFieldCache

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from .entity_testfielddata import (
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    )
from .entity_testsitedata import (
    get_site_fields, get_site_fields_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   CollectionFieldCache tests
#
#   -----------------------------------------------------------------------------

class CollectionFieldCacheTest(AnnalistTestCase):
    """
    Tests for collection field and superproperty cache classes.
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection(self.testsite, "testcoll")
        self.testcoll1  = Collection(self.testsite, "testcoll1")
        self.testcoll2  = Collection(self.testsite, "testcoll2")
        self.fieldcache = CollectionFieldCache()
        self.field1     = RecordField(self.testcoll1, "field1")
        self.field1.set_values(
            recordfield_create_values(field_id="field1", property_uri="test:field1", 
                superproperty_uris=[]
                )
            )
        self.field11   = RecordField(self.testcoll1, "field11")
        self.field11.set_values(
            recordfield_create_values(field_id="field11", property_uri="test:field11", 
                superproperty_uris=["test:field1"]
                )
            )
        self.field111  = RecordField(self.testcoll1, "field111")
        self.field111.set_values(
            recordfield_create_values(field_id="field111", property_uri="test:field111", 
                superproperty_uris=["test:field11"]
                )
            )
        self.field2    = RecordField(self.testcoll1, "field2")
        self.field2.set_values(
            recordfield_create_values(field_id="field2", property_uri="test:field2", 
                superproperty_uris=[]
                )
            )
        return

    def create_field_record(self, coll, field_entity):
        return RecordField.create(coll, field_entity.get_id(), field_entity.get_values())

    def create_test_field_entities(self):
        # Create records in collection data
        self.create_field_record(self.testcoll1, self.field1)
        self.create_field_record(self.testcoll1, self.field11)
        self.create_field_record(self.testcoll1, self.field111)
        self.create_field_record(self.testcoll1, self.field2)
        # Add all records to cache
        self.fieldcache.set_field(self.testcoll1, self.field1)
        self.fieldcache.set_field(self.testcoll1, self.field11)
        self.fieldcache.set_field(self.testcoll1, self.field111)
        self.fieldcache.set_field(self.testcoll1, self.field2)
        # Check cache content
        self.expect_site_field_ids = get_site_fields()
        self.expect_coll_field_ids = (
            { "field1", "field11", "field111", "field2" }
            )
        self.expect_all_field_ids = set.union(self.expect_site_field_ids, self.expect_coll_field_ids)
        retrieve_field_ids = set(f.get_id() for f in self.fieldcache.get_all_fields(self.testcoll1))
        self.assertEqual(retrieve_field_ids, self.expect_coll_field_ids)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    def get_coll_field(self, coll, field_id):
        return self.fieldcache.get_field(coll, field_id)

    def get_coll_field_uri(self, coll, field_id):
        return self.get_coll_field(coll, field_id).get_property_uri()

    def get_coll_uri_field(self, coll, property_uri):
        return self.fieldcache.get_field_from_uri(coll, property_uri)

    def get_coll_uri_id(self, coll, property_uri):
        return self.get_coll_uri_field(coll, property_uri).get_id()

    def get_coll_property_uris(self, coll):
        return { f.get_property_uri() for f in self.fieldcache.get_all_fields(coll) }

    # Start of tests

    def test_empty_cache(self):
        self.assertEqual(set(self.fieldcache.get_all_fields(self.testcoll1)), set())
        self.assertEqual(set(self.fieldcache.get_all_fields(self.testcoll2)), set())
        return

    def test_singleton_cache(self):
        self.assertEqual(self.get_coll_property_uris(self.testcoll1), set())
        self.create_field_record(self.testcoll1, self.field1)
        # NOTE: the 'set_field' call also causes cache initialization of all fields, 
        # including the created field record which is discovered on disk, and the subsequent 
        # set_field call returns 'False'.
        self.assertFalse(self.fieldcache.set_field(self.testcoll1, self.field1))
        self.assertFalse(self.fieldcache.set_field(self.testcoll1, self.field1))
        self.assertEqual(self.get_coll_field_uri(self.testcoll1, "field1"),      "test:field1")
        self.assertEqual(self.get_coll_field(self.testcoll1,     "field2"),      None)
        self.assertEqual(self.get_coll_uri_id(self.testcoll1,    "test:field1"), "field1")
        self.assertEqual(self.get_coll_uri_field(self.testcoll1, "test:field2"), None)
        self.assertEqual(self.get_coll_property_uris(self.testcoll1), {"test:field1"})
        self.assertEqual(self.get_coll_property_uris(self.testcoll2), set())
        return

    def test_empty_cache_2(self):
        self.fieldcache.set_field(self.testcoll1, self.field1)
        self.assertIsNotNone(self.fieldcache.remove_field(self.testcoll1, "field1"))
        self.assertIsNone(self.fieldcache.remove_field(self.testcoll1, "field1"))
        self.assertEqual(list(self.fieldcache.get_all_fields(self.testcoll1)), [])
        self.assertEqual(list(self.fieldcache.get_all_fields(self.testcoll2)), [])
        return

    def test_flush_cache(self):
        self.fieldcache.set_field(self.testcoll1, self.field1)
        self.assertTrue(self.fieldcache.flush_cache(self.testcoll1))
        self.assertIsNone(self.fieldcache.remove_field(self.testcoll1, "field1"))
        self.assertEqual(list(self.fieldcache.get_all_fields(self.testcoll1)), [])
        self.assertEqual(list(self.fieldcache.get_all_fields(self.testcoll2)), [])
        self.assertTrue(self.fieldcache.flush_cache(self.testcoll1))
        self.assertFalse(self.fieldcache.flush_cache(self.testcoll1))
        return

    def test_get_fields_by_uri(self):
        self.create_test_field_entities()
        self.assertEqual(self.fieldcache.get_field_from_uri(self.testcoll1, "test:field1").get_id(),   "field1")
        self.assertEqual(self.fieldcache.get_field_from_uri(self.testcoll1, "test:field11").get_id(),  "field11")
        self.assertEqual(self.fieldcache.get_field_from_uri(self.testcoll1, "test:field111").get_id(), "field111")
        self.assertEqual(self.fieldcache.get_field_from_uri(self.testcoll1, "test:field2").get_id(),   "field2")
        return

    def test_get_all_fields_scope_coll(self):
        self.create_test_field_entities()
        field_ids = set(f.get_id() for f in self.fieldcache.get_all_fields(self.testcoll1))
        self.assertEqual(field_ids, self.expect_coll_field_ids)
        field_ids = set(f.get_id() for f in self.fieldcache.get_all_fields(self.testcoll1))
        self.assertEqual(field_ids, self.expect_coll_field_ids)
        return

    def test_get_all_fields_scope_all(self):
        self.create_test_field_entities()
        field_ids = set(
            f.get_id() 
            for f in self.fieldcache.get_all_fields(self.testcoll1, altscope="all")
            )
        self.assertEqual(field_ids, self.expect_all_field_ids)
        return

    def test_get_superproperty_fields(self):
        self.create_test_field_entities()
        def get_superproperty_uris(property_uri):
            sf_entities = self.fieldcache.get_superproperty_fields(self.testcoll1, property_uri)
            sp_uris     = [ sf.get_property_uri() for sf in sf_entities ]
            return set(sp_uris)
        self.assertEqual(get_superproperty_uris("test:field1"),   set())
        self.assertEqual(get_superproperty_uris("test:field11"),  {"test:field1"})
        self.assertEqual(get_superproperty_uris("test:field111"), {"test:field1", "test:field11"})
        self.assertEqual(get_superproperty_uris("test:field2"),   set({}))
        return

    def test_get_subproperty_fields(self):
        self.create_test_field_entities()
        def get_subproperty_uris(property_uri):
            sf_entities = self.fieldcache.get_subproperty_fields(self.testcoll1, property_uri)
            sp_uris     = [ sf.get_property_uri() for sf in sf_entities ]
            return set(sp_uris)
        self.assertEqual(get_subproperty_uris("test:field1"),   {"test:field11", "test:field111"})
        self.assertEqual(get_subproperty_uris("test:field11"),  {"test:field111"})
        self.assertEqual(get_subproperty_uris("test:field111"), set())
        self.assertEqual(get_subproperty_uris("test:field2"),   set())
        return

    def test_update_superproperty(self):
        self.create_test_field_entities()
        def get_superproperty_uris(property_uri):
            sf_entities = self.fieldcache.get_superproperty_fields(self.testcoll1, property_uri)
            sp_uris     = [ sf.get_property_uri() for sf in sf_entities ]
            return set(sp_uris)
        self.assertEqual(get_superproperty_uris("test:field1"),   set())
        self.assertEqual(get_superproperty_uris("test:field11"),  {"test:field1"})
        self.assertEqual(get_superproperty_uris("test:field111"), {"test:field1", "test:field11"})
        self.assertEqual(get_superproperty_uris("test:field2"),   set())
        # Update super/sub-type
        self.fieldcache.remove_field(self.testcoll1, "field11")
        self.fieldcache.set_field(self.testcoll1, self.field11)
        # Re-check supertypes
        self.assertEqual(get_superproperty_uris("test:field1"),   set())
        self.assertEqual(get_superproperty_uris("test:field11"),  {"test:field1"})
        self.assertEqual(get_superproperty_uris("test:field111"), {"test:field1", "test:field11"})
        self.assertEqual(get_superproperty_uris("test:field2"),   set())
        return

    def test_update_subproperty(self):
        self.create_test_field_entities()
        def get_subproperty_uris(property_uri):
            sf_entities = self.fieldcache.get_subproperty_fields(self.testcoll1, property_uri)
            sp_uris     = [ sf.get_property_uri() for sf in sf_entities ]
            return set(sp_uris)
        self.assertEqual(get_subproperty_uris("test:field1"),   {"test:field11", "test:field111"})
        self.assertEqual(get_subproperty_uris("test:field11"),  {"test:field111"})
        self.assertEqual(get_subproperty_uris("test:field111"), set())
        self.assertEqual(get_subproperty_uris("test:field2"),   set())
        # Update super/sub-property
        self.fieldcache.remove_field(self.testcoll1, "field11")
        self.fieldcache.set_field(self.testcoll1, self.field11)
        # Re-check subproperties
        self.assertEqual(get_subproperty_uris("test:field1"),   {"test:field11", "test:field111"})
        self.assertEqual(get_subproperty_uris("test:field11"),  {"test:field111"})
        self.assertEqual(get_subproperty_uris("test:field111"), set())
        self.assertEqual(get_subproperty_uris("test:field2"),   set())
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
