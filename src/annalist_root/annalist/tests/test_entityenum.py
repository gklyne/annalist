"""
Tests for EntityEnum module
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
from annalist.models.recordenum     import RecordEnumBase, RecordEnumFactory


from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import collection_dir, site_view_url, site_title

#   -----------------------------------------------------------------------------
#
#   Helper functions
#
#   -----------------------------------------------------------------------------

def recordenum_url(enum_id, coll_id="testcoll", type_id="testtype"):
    """
    Returns internal access URL for indicated enumerated value.

    enum_id     id of enumerated value
    coll-id     id of collection
    type_id     id of enumeration type
    """
    return (
        "/testsite/c/%(coll_id)s/d/%(type_id)s/%(enum_id)s/"%
            { 'coll_id': coll_id
            , 'type_id': type_id
            , 'enum_id': enum_id
            }
        )

def recordenum_view_url(enum_id, coll_id="testcoll", type_id="testtype"):
    """
    Returns public access URL / URI for indicated enumerated value.

    enum_id     id of enumerated value
    coll-id     id of collection
    type_id     id of enumeration type
    """
    return (
        "/testsite/c/%(coll_id)s/d/%(type_id)s/%(enum_id)s/"%
        {'coll_id': coll_id
        , 'type_id': type_id
        , 'enum_id': enum_id}
        )

def recordenum_dir(enum_id, coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_ENUM_PATH%{'type_id': type_id, 'id': enum_id} + "/"

def recordenum_value_keys():
    """
    Keys in default view entity data
    """
    return (
        [ '@type'
        , 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordenum_create_values(
        enum_id, coll_id="testcoll", type_id="testtype", 
        type_uri="annal:List_type", update="Enum", hosturi=TestHostUri):
    """
    Data used when creating enumeration test data
    """
    enumuri = "annal:%s/%s"%(type_id, enum_id)
    types   = ["annal:Enum", type_uri]
    return (
        { '@type':          types
        , 'annal:type':     types[0]
        , 'rdfs:label':     '%s %s/%s/%s'%(update, coll_id, type_id, enum_id)
        , 'rdfs:comment':   '%s %s/%s/%s'%(update, coll_id, type_id, enum_id)
        , 'annal:uri':      enumuri
        })

def recordenum_values(enum_id, coll_id="testcoll", type_id="testtype", update="Enum", hosturi=TestHostUri):
    enumurl = recordenum_view_url(enum_id, coll_id=coll_id, type_id=type_id)
    d = recordenum_create_values(
        enum_id, coll_id=coll_id, type_id=type_id, update=update, hosturi=hosturi
        ).copy() #@@ copy needed here?
    d.update(
        { 'annal:id':       enum_id
        , 'annal:type_id':  type_id
        , 'annal:url':      enumurl
        })
    # log.info(d)
    return d

def recordenum_read_values(
        enum_id, coll_id="testcoll", type_id="testtype", update="Enum", hosturi=TestHostUri):
    d = recordenum_values(
        enum_id, coll_id=coll_id, type_id=type_id, update=update, hosturi=hosturi
        ).copy()
    d.update(
        { '@id':        layout.COLL_BASE_ENUM_REF%{'type_id': layout.ENUM_LIST_TYPE_ID, 'id': "testenum1"}
        , '@context':   [{'@base': "../../"}, "../../coll_context.jsonld"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   RecordEnum tests
#
#   -----------------------------------------------------------------------------

class RecordEnumTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection(self.testsite, "testcoll")
        self.testenum  = RecordEnumFactory("testenum", layout.ENUM_LIST_TYPE_ID)
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_RecordEnumTest(self):
        self.assertEqual(self.testenum.__name__, "testenum", "Check enumeration class name")
        return

    def test_recordenum_init(self):
        e = self.testenum(self.testcoll, "testenum")
        self.assertEqual(e._entitytype,     ANNAL.CURIE.Enum)
        self.assertEqual(e._entityfile,     layout.ENUM_META_FILE)
        self.assertEqual(e._entityref,      
            layout.COLL_BASE_ENUM_REF%{'type_id': layout.ENUM_LIST_TYPE_ID, 'id': "testenum"}
            )
        self.assertEqual(e._entityid,       "testenum")
        self.assertEqual(e._entityurl,      
            TestHostUri + recordenum_url("testenum", coll_id="testcoll", type_id=layout.ENUM_LIST_TYPE_ID)
            )
        self.assertEqual(e._entitydir,      
            recordenum_dir("testenum", coll_id="testcoll", type_id=layout.ENUM_LIST_TYPE_ID)
            )
        self.assertEqual(e._values,         None)
        return

    def test_recordenum_base_init(self):
        # Note that if base class is used directly, the type_id value isn't recognized 
        # as it needs to be a class property.
        e = RecordEnumBase(self.testcoll, "testenum2", layout.ENUM_LIST_TYPE_ID)
        self.assertEqual(e._entitytype,     ANNAL.CURIE.Enum)
        self.assertEqual(e._entityfile,     layout.ENUM_META_FILE)
        self.assertEqual(e._entityref,      
            layout.COLL_BASE_ENUM_REF%{'type_id': layout.ENUM_LIST_TYPE_ID, 'id': "testenum2"}
            )
        self.assertEqual(e._entityid,       "testenum2")
        self.assertEqual(e._entityurl,      
            TestHostUri + recordenum_url(
                "testenum2", coll_id="testcoll", type_id="_enum_base_id"    # See note
                )
            )
        self.assertEqual(e._entitydir,      
            recordenum_dir(
                "testenum2", coll_id="testcoll", type_id="_enum_base_id"    # See note
                )
            )
        self.assertEqual(e._values,         None)
        resetSitedata()
        return

    def test_recordenum1_data(self):
        e = self.testenum(self.testcoll, "testenum1")
        e.set_values(recordenum_create_values("testenum1", type_id=layout.ENUM_LIST_TYPE_ID))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(recordenum_value_keys()))
        v = recordenum_values("testenum1", type_id=layout.ENUM_LIST_TYPE_ID)
        self.assertDictionaryMatch(ed, v)
        return

    def test_recordenum2_data(self):
        e = self.testenum(self.testcoll, "testenum2")
        e.set_values(recordenum_create_values("testenum2", type_id=layout.ENUM_LIST_TYPE_ID))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(recordenum_value_keys()))
        v = recordenum_values("testenum2", type_id=layout.ENUM_LIST_TYPE_ID)
        self.assertDictionaryMatch(ed, v)
        return

    def test_recordenum_create_load(self):
        ev = recordenum_create_values("testenum1", type_id=layout.ENUM_LIST_TYPE_ID)
        e  = self.testenum.create(self.testcoll, "testenum1", ev)
        self.assertEqual(e._entitydir, recordenum_dir("testenum1", type_id=layout.ENUM_LIST_TYPE_ID))
        self.assertTrue(os.path.exists(e._entitydir))
        ed = self.testenum.load(self.testcoll, "testenum1").get_values()
        v  = recordenum_read_values("testenum1", type_id=layout.ENUM_LIST_TYPE_ID)
        self.assertKeysMatch(ed, v)
        self.assertDictionaryMatch(ed, v)
        return

    def test_recordenum_type_id(self):
        r = EntityRoot(TestBaseUri, TestBaseUri, TestBaseDir, TestBaseDir)
        self.assertEqual(r.get_type_id(),   None)
        e1 = Entity(r, "testid1")
        self.assertEqual(e1.get_type_id(),  None)
        e2 = self.testenum(e1, "testid2")
        self.assertEqual(e2.get_type_id(),  layout.ENUM_LIST_TYPE_ID)
        return

    def test_recordenum_child_ids(self):
        child_ids1 = self.testcoll.child_entity_ids(self.testenum, altscope="all")
        self.assertEqual(set(child_ids1), {'_initial_values', 'Grid', 'List'})
        ev = recordenum_create_values("testenum1", type_id=layout.ENUM_LIST_TYPE_ID)
        e  = self.testenum.create(self.testcoll, "testenum1", ev)
        child_ids2 = self.testcoll.child_entity_ids(self.testenum, altscope="all")
        self.assertEqual(set(child_ids2), {'_initial_values', 'Grid', 'List', 'testenum1'})
        return

# End.
