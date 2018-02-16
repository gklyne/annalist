"""
Tests for collection vocabulary namespace cache class.
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
from entity_testentitydata  import (
    # entity_url, entitydata_edit_url, entitydata_list_vocab_url,
    # default_fields, default_label, default_comment, error_label,
    entitydata_create_values
    )

from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordvocab            import RecordVocab
from annalist.models.collectionvocabcache   import CollectionVocabCache

#   -----------------------------------------------------------------------------
#
#   CollectionVocabCache tests
#
#   -----------------------------------------------------------------------------

class CollectionVocabCacheTest(AnnalistTestCase):
    """
    Tests CollectionVocabCache class.
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite     = Site(TestBaseUri, TestBaseDir)
        self.testcoll     = Collection(self.testsite, "testcoll")
        self.testcoll1_a  = Collection(self.testsite, "testcoll1")
        self.testcoll1_b  = Collection(self.testsite, "testcoll1")
        self.testcoll2_a  = Collection(self.testsite, "testcoll2")
        self.testcoll2_b  = Collection(self.testsite, "testcoll2")
        self.vocabcache   = CollectionVocabCache()
        self.vocab1       = RecordVocab(self.testcoll1_a, "vocab1")
        self.vocab1.set_values(
            entitydata_create_values("vocab1", type_id="_vocab", entity_uri="test:vocab1")
            )
        self.vocab2       = RecordVocab(self.testcoll1_a, "vocab2")
        self.vocab2.set_values(
            entitydata_create_values("vocab2", type_id="_vocab", entity_uri="test:vocab2")
            )
        return

    def create_vocab_record(self, coll, vocab_entity):
        return RecordVocab.create(coll, vocab_entity.get_id(), vocab_entity.get_values())

    def create_test_vocab_entities(self):
        # Create entity records in collection data
        self.create_vocab_record(self.testcoll1_a, self.vocab1)
        self.create_vocab_record(self.testcoll1_a, self.vocab2)
        # Add entities to cache
        self.vocabcache.set_vocab(self.testcoll1_a, self.vocab1)
        self.vocabcache.set_vocab(self.testcoll1_a, self.vocab2)
        # Check cache content
        self.expect_site_vocab_ids = (
            { "owl", "rdf", "annal", "xsd", "rdfs"
            })
        self.expect_coll_vocab_ids = (
            {"vocab1", "vocab2"}
            )
        self.expect_all_vocab_ids = set.union(self.expect_site_vocab_ids, self.expect_coll_vocab_ids)
        retrieve_vocab_ids = set(t.get_id() for t in self.vocabcache.get_all_vocabs(self.testcoll1_a))
        self.assertEqual(retrieve_vocab_ids, self.expect_coll_vocab_ids)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    def test_empty_cache(self):
        self.assertEqual(set(self.vocabcache.get_all_vocabs(self.testcoll1_a)), set())
        self.assertEqual(set(self.vocabcache.get_all_vocabs(self.testcoll1_b)), set())
        self.assertEqual(set(self.vocabcache.get_all_vocabs(self.testcoll2_a)), set())
        self.assertEqual(set(self.vocabcache.get_all_vocabs(self.testcoll2_b)), set())
        return

    def test_singleton_cache(self):
        foo = self.vocabcache.get_vocab(self.testcoll1_a, "vocab2")
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_a, "vocab2"), None)
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_b, "vocab2"), None)
        self.assertEqual([t.get_uri() for t in self.vocabcache.get_all_vocabs(self.testcoll1_a)], [])
        self.create_vocab_record(self.testcoll1_a, self.vocab1)
        # NOTE: the 'set_vocab' call also causes cache initialization of all vocabs, 
        # including the created vocab record which is discovered on disk, and the subsequent 
        # set_vocab call returns 'False'.
        self.assertFalse(self.vocabcache.set_vocab(self.testcoll1_a, self.vocab1))
        self.assertFalse(self.vocabcache.set_vocab(self.testcoll1_b, self.vocab1))
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_a, "vocab1").get_uri(), "test:vocab1")
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_b, "vocab1").get_uri(), "test:vocab1")
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_a, "vocab2"), None)
        self.assertEqual(self.vocabcache.get_vocab(self.testcoll1_b, "vocab2"), None)
        self.assertEqual(self.vocabcache.get_vocab_from_uri(self.testcoll1_a, "test:vocab1").get_id(), "vocab1")
        self.assertEqual(self.vocabcache.get_vocab_from_uri(self.testcoll1_b, "test:vocab1").get_id(), "vocab1")
        self.assertEqual(self.vocabcache.get_vocab_from_uri(self.testcoll1_a, "test:vocab2"), None)
        self.assertEqual(self.vocabcache.get_vocab_from_uri(self.testcoll1_b, "test:vocab3"), None)
        self.assertEqual([t.get_uri() for t in self.vocabcache.get_all_vocabs(self.testcoll1_a)], ["test:vocab1"])
        self.assertEqual([t.get_uri() for t in self.vocabcache.get_all_vocabs(self.testcoll1_b)], ["test:vocab1"])
        self.assertEqual([t.get_uri() for t in self.vocabcache.get_all_vocabs(self.testcoll2_a)], [])
        self.assertEqual([t.get_uri() for t in self.vocabcache.get_all_vocabs(self.testcoll2_b)], [])
        return

    def test_empty_cache_2(self):
        self.vocabcache.set_vocab(self.testcoll1_a, self.vocab1)
        self.assertIsNotNone(self.vocabcache.remove_vocab(self.testcoll1_a, "vocab1"))
        self.assertIsNone(self.vocabcache.remove_vocab(self.testcoll1_b, "vocab1"))
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll1_a)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll1_b)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll2_a)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll2_b)), [])
        return

    def test_flush_cache(self):
        self.vocabcache.set_vocab(self.testcoll1_a, self.vocab1)
        self.assertTrue(self.vocabcache.flush_cache(self.testcoll1_a))
        self.assertIsNone(self.vocabcache.remove_vocab(self.testcoll1_b, "vocab1"))
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll1_a)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll1_b)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll2_a)), [])
        self.assertEqual(list(self.vocabcache.get_all_vocabs(self.testcoll2_b)), [])
        self.assertTrue(self.vocabcache.flush_cache(self.testcoll1_b))
        self.assertFalse(self.vocabcache.flush_cache(self.testcoll1_b))
        return

    def test_get_vocabs_by_uri(self):
        self.create_test_vocab_entities()
        self.assertEqual(
            self.vocabcache.get_vocab_from_uri(self.testcoll1_b, "test:vocab1").get_id(),
            "vocab1"
            )
        self.assertEqual(
            self.vocabcache.get_vocab_from_uri(self.testcoll1_b, "test:vocab2").get_id(),
            "vocab2"
            )
        return

    def test_get_all_vocabs_scope_coll(self):
        self.create_test_vocab_entities()
        vocab_ids = set(t.get_id() for t in self.vocabcache.get_all_vocabs(self.testcoll1_a))
        self.assertEqual(vocab_ids, self.expect_coll_vocab_ids)
        vocab_ids = set(t.get_id() for t in self.vocabcache.get_all_vocabs(self.testcoll1_b))
        self.assertEqual(vocab_ids, self.expect_coll_vocab_ids)
        return

    def test_get_all_vocabs_scope_all(self):
        self.create_test_vocab_entities()
        vocab_ids = set(t.get_id() for t in self.vocabcache.get_all_vocabs(self.testcoll1_a, altscope="all"))
        self.assertEqual(vocab_ids, self.expect_all_vocab_ids)
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
