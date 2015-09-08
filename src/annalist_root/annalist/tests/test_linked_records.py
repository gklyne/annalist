"""
Tests for linked record functions.

This test suite uses a setup that is specifically intended to test functions that involve 
links between entities.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.contrib.auth.models     import User
from django.test                    import TestCase
from django.core.urlresolvers       import resolve, reverse
from django.test.client             import Client

from annalist.identifiers           import ANNAL

from annalist.models.entity         import EntityRoot, Entity
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.entitytypeinfo import EntityTypeInfo

from annalist.views.form_utils.fieldchoice  import FieldChoice


from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    collection_entity_view_url,
    create_test_user,
    create_user_permissions,
    context_list_entities,
    context_list_head_fields,
    context_list_item_fields
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    )

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

testsrc_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "testsrc_type label"
    , 'rdfs:comment':               "testsrc_type comment"
    , 'annal:uri':                  "test:type/testsrc_type"
    , 'annal:type_view':            "testsrc_view"
    , 'annal:type_list':            "testsrc_list"
    })

testtgt_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "testtgt_type label"
    , 'rdfs:comment':               "testtgt_type comment"
    , 'annal:uri':                  "test:type/testtgt_type"
    , 'annal:type_view':            "testtgt_view"
    , 'annal:type_list':            "testtgt_list"
    })

testsrc_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "testsrc_view label"
    , 'rdfs:comment':               "testsrc_view comment"
    , 'annal:record_type':          ""
    , 'annal:add_field':            "yes"
    , 'annal:view_fields':
      [ { 'annal:field_id':             "Entity_id"
        , 'annal:field_placement':      "small:0,12;medium:0,6"
        }
      , { 'annal:field_id':             "testtgtref_field"
        , 'annal:field_placement':      "small:0,12;medium:6,6"
        }
      , { 'annal:field_id':             "Entity_label"
        , 'annal:field_placement':      "small:0,12"
        }
      , { 'annal:field_id':             "Entity_comment"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

testtgt_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "testtgt_view label"
    , 'rdfs:comment':               "testtgt_view commemnt"
    , 'annal:record_type':          ""
    , 'annal:add_field':            "yes"
    , 'annal:view_fields':
      [ { 'annal:field_id':             "Entity_id"
        , 'annal:field_placement':      "small:0,12;medium:0,6"
        }
      , { 'annal:field_id':             "Entity_label"
        , 'annal:field_placement':      "small:0,12"
        }
      , { 'annal:field_id':             "Entity_comment"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

testsrc_list_create_values = (
    { 'annal:type':                 "annal:List"
    , 'rdfs:label':                 "testsrc_list label"
    , 'rdfs:comment':               "testsrc_list commemnt"
    , 'annal:record_type':          ""
    , "annal:display_type":         "List"
    , "annal:default_view":         "testsrc_view"
    , "annal:default_type":         "testsrc_type"
    , "annal:list_entity_selector": "test:type/testsrc_type in [@type]"
    , "annal:list_fields":
      [ { "annal:field_id":             "Entity_id"
        , "annal:field_placement":      "small:0,3"
        }
      , { "annal:field_id":             "testtgtref_field"
        , "annal:field_placement":      "small:3,3"
        }
      , { "annal:field_id":             "Entity_label"
        , "annal:field_placement":      "small:6,6"
        }
      ]
    })

testtgt_list_create_values = (
    { 'annal:type':                 "annal:List"
    , 'rdfs:label':                 "testtgt_list label"
    , 'rdfs:comment':               "testtgt_list commemnt"
    , 'annal:record_type':          ""
    , "annal:display_type":         "List"
    , "annal:default_view":         "testtgt_view"
    , "annal:default_type":         "testtgt_type"
    , "annal:list_entity_selector": "test:type/testtgt_type in [@type]"
    , "annal:list_fields":
      [ { "annal:field_id":             "Entity_id"
        , "annal:field_placement":      "small:0,3"
        }
      , { "annal:field_id":             "Entity_label"
        , "annal:field_placement":      "small:3,9"
        }
      ]
    })

testtgtref_field_create_values = (
    { 'annal:type':                 "annal:Field"
    , 'rdfs:label':                 "testtgtref_field label"
    , 'rdfs:comment':               "testtgtref_field comment"
    , 'annal:property_uri':         "test:testtgtref"
    , 'annal:field_entity_type':    "test:type/testsrc_type"    # Field-ref domain type
    , 'annal:field_value_type':     "test:type/testtgt_type"    # Field-ref range type
    , 'annal:field_render_type':    "Enum"
    , 'annal:field_ref_type':       "testtgt_type"
    , 'annal:placeholder':          "(reference to testtgt_type entity)"
    , 'annal:default_value':        ""
    })

def testsrc_entity_create_values(entity_id, tgtref_id):
    return (
        { 'rdfs:label':                 "testsrc_entity %s label"%entity_id
        , 'rdfs:comment':               "testsrc_entity %s comment"%entity_id
        , 'test:testtgtref':            "testtgt_type/"+tgtref_id
        })

def testtgt_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "testtgt_entity %s label"%entity_id
        , 'rdfs:comment':               "testtgt_entity %s comment"%entity_id
        })

#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class LinkedRecordTest(AnnalistTestCase):
    """
    Tests for linked records
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        # Populate collection with linked record types, views and lists
        self.testsrc_type = RecordType.create(self.testcoll, "testsrc_type", testsrc_type_create_values)
        self.testtgt_type = RecordType.create(self.testcoll, "testtgt_type", testtgt_type_create_values)
        self.testsrc_view = RecordView.create(self.testcoll, "testsrc_view", testsrc_view_create_values)
        self.testtgt_view = RecordView.create(self.testcoll, "testtgt_view", testtgt_view_create_values)
        self.testsrc_list = RecordList.create(self.testcoll, "testsrc_list", testsrc_list_create_values)
        self.testtgt_list = RecordList.create(self.testcoll, "testtgt_list", testtgt_list_create_values)
        self.testtgtref_field = RecordField.create(self.testcoll, "testtgtref_field", testtgtref_field_create_values)
        self.no_options   = [ FieldChoice('', label="(no options)") ]
        self.tgt_options  = (
            [ FieldChoice("testtgt_type/"+v, 
                label="testtgt_entity %s label"%v,
                link=entity_url("testcoll", "testtgt_type", v))
              for v in ["testtgt1", "testtgt2"]
            ])
        # Create data records for testing:
        self.testtgt_type_info = EntityTypeInfo(self.testsite, self.testcoll, "testtgt_type", create_typedata=True)
        self.testsrc_type_info = EntityTypeInfo(self.testsite, self.testcoll, "testsrc_type", create_typedata=True)
        for tgt_id in ("testtgt1", "testtgt2"):
            self.testtgt_type_info.create_entity(tgt_id, testtgt_entity_create_values(tgt_id))
        for src_id, tgt_ref in (("testsrc1", "testtgt1"), ("testsrc2", "testtgt2")):
            self.testsrc_type_info.create_entity(src_id, testsrc_entity_create_values(src_id, tgt_ref))
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    # Utility functions

    # Tests

    def test_view_entity_references(self):
        u = entity_url(coll_id="testcoll", type_id="testsrc_type", entity_id="testsrc1")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(len(r.context['fields']), 4)
        i = 0
        self.assertEqual(r.context['fields'][i].field_id,         "Entity_id")
        self.assertEqual(r.context['fields'][i].field_value,      "testsrc1")
        self.assertEqual(r.context['fields'][i].field_value_link, None)
        self.assertEqual(r.context['fields'][i].options,          self.no_options)
        i = 1
        self.assertEqual(r.context['fields'][i].field_id,         "testtgtref_field")
        self.assertEqual(r.context['fields'][i].field_value,      "testtgt_type/testtgt1")
        self.assertEqual(r.context['fields'][i].field_value_link, "/testsite/c/testcoll/d/testtgt_type/testtgt1/")
        self.assertEqual(r.context['fields'][i].options,          self.tgt_options)
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,         "Entity_label")
        self.assertEqual(r.context['fields'][i].field_value,      "testsrc_entity testsrc1 label")
        self.assertEqual(r.context['fields'][i].field_value_link, None)
        self.assertEqual(r.context['fields'][i].options,          self.no_options)
        i = 3
        self.assertEqual(r.context['fields'][i].field_id,         "Entity_comment")
        self.assertEqual(r.context['fields'][i].field_value,      "testsrc_entity testsrc1 comment")
        self.assertEqual(r.context['fields'][i].field_value_link, None)
        self.assertEqual(r.context['fields'][i].options,          self.no_options)
        return

    def test_list_entity_references(self):
        # List linked records - check values in listing
        u = entitydata_list_type_url("testcoll", "testsrc_type", list_id="testsrc_list")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        entities    = context_list_entities(r.context)
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(entities),    2)
        self.assertEqual(len(head_fields), 3)
        entity_values = (
            (entities[0], "testsrc1", "testtgt1"), 
            (entities[1], "testsrc2", "testtgt2")
            )
        for entc, esrc, etgt in entity_values:
            item_fields = context_list_item_fields(r.context, entc)
            self.assertEqual(len(item_fields), 3)
            self.assertEqual(entc['entity_id'],               esrc)
            self.assertEqual(entc['entity_type_id'],          "testsrc_type")
            self.assertEqual(item_fields[0].field_id,         "Entity_id")
            self.assertEqual(item_fields[0].field_value,      esrc)
            self.assertEqual(item_fields[0].field_value_link, None)
            self.assertEqual(item_fields[1].field_id,         "testtgtref_field")
            self.assertEqual(item_fields[1].field_value,      "testtgt_type/"+etgt)
            self.assertEqual(item_fields[1].field_value_link, "/testsite/c/testcoll/d/testtgt_type/%s/"%etgt)
            self.assertEqual(item_fields[2].field_id,         "Entity_label")
            self.assertEqual(item_fields[2].field_value,      "testsrc_entity %s label"%esrc)
            self.assertEqual(item_fields[2].field_value_link, None)
        return

# End.
