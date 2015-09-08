"""
Tests for EntityData module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.entityroot     import EntityRoot
from annalist.models.entity         import Entity
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
# from entity_testutils               import (
from entity_testentitydata          import (
    entitydata_dir, 
    entity_url, 
    entitydata_value_keys, entitydata_create_values, entitydata_values
    )

#   -----------------------------------------------------------------------------
#
#   EntityData tests
#
#   -----------------------------------------------------------------------------

class EntityDataTest(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.testtype = RecordType(self.testcoll, "testtype")
        self.testdata = RecordTypeData(self.testcoll, "testtype")
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_EntityDataTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_entitydata_init(self):
        e = EntityData(self.testdata, "testentity")
        self.assertEqual(e._entitytype,     ANNAL.CURIE.EntityData)
        self.assertEqual(e._entityfile,     layout.ENTITY_DATA_FILE)
        self.assertEqual(e._entityref,      layout.DATA_ENTITY_REF)
        self.assertEqual(e._entityid,       "testentity")
        self.assertEqual(e._entityurl,      TestHostUri + entity_url("testcoll", "testtype", "testentity"))
        self.assertEqual(e._entitydir,      entitydata_dir("testcoll", "testtype", "testentity"))
        self.assertEqual(e._values,         None)
        return

    def test_entitydata1_data(self):
        e = EntityData(self.testdata, "entitydata1")
        e.set_values(entitydata_create_values("entitydata1"))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(entitydata_value_keys()))
        v = entitydata_values("entitydata1")
        self.assertEqual(ed, {k:v[k] for k in entitydata_value_keys()})
        return

    def test_entitydata2_data(self):
        e = EntityData(self.testdata, "entitydata2")
        e.set_values(entitydata_create_values("entitydata2"))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(entitydata_value_keys()))
        v = entitydata_values("entitydata2")
        self.assertEqual(ed, {k:v[k] for k in entitydata_value_keys()})
        return

    def test_entitydata_create_load(self):
        e  = EntityData.create(self.testdata, "entitydata1", entitydata_create_values("entitydata1"))
        self.assertEqual(e._entitydir, entitydata_dir(entity_id="entitydata1"))
        self.assertTrue(os.path.exists(e._entitydir))
        ed = EntityData.load(self.testdata, "entitydata1").get_values()
        v  = entitydata_values("entitydata1")
        self.assertKeysMatch(ed, v)
        self.assertDictionaryMatch(ed, v)
        return

    def test_entitydata_type_id(self):
        r = EntityRoot(TestBaseUri, TestBaseDir)
        self.assertEqual(r.get_type_id(),   None)
        e1 = Entity(r, "testid1")
        self.assertEqual(e1.get_type_id(),  None)
        e2 = EntityData(e1, "testid2")
        self.assertEqual(e2.get_type_id(),  "testid1")
        return

# End.
