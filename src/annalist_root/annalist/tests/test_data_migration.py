"""
Tests for data migration functions.

This test suite uses a setup that is specifically intended to test functions 
that involve data migration.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
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
from annalist.models.collectiondata import migrate_coll_data

from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase               import AnnalistTestCase
from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests                     import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils               import (
    collection_entity_view_url,
    create_test_user,
    create_user_permissions,
    context_view_field,
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

test_supertype_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_supertype_type label"
    , 'rdfs:comment':               "test_supertype_type comment"
    , 'annal:uri':                  "test:test_supertype_type"
    , 'annal:type_view':            "Default_view"
    , 'annal:type_list':            "Default_list"
    , "annal:supertype_uri":        []
    , "annal:field_aliases":        []
    })

test_subtype_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_supertype_type label"
    , 'rdfs:comment':               "test_supertype_type comment"
    , 'annal:uri':                  "test:test_subtype_type"
    , 'annal:type_view':            "Default_view"
    , 'annal:type_list':            "Default_list"
    # , "annal:supertype_uri":        [ { "@id": "test:test_supertype_type" } ]
    , "annal:supertype_uri":        []
    , "annal:field_aliases":        []
    })

def test_subtype_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_subtype_entity %s label"%entity_id
        , 'rdfs:comment':               "test_subtype_entity %s comment"%entity_id
        })

#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class DataMigrationTest(AnnalistTestCase):
    """
    Tests for linked records
    """

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        # Populate collection with linked record types, views and lists
        self.test_supertype_type = RecordType.create(
            self.testcoll, "test_supertype_type",
            test_supertype_type_create_values
            )
        self.test_subtype_type   = RecordType.create(
            self.testcoll, "test_subtype_type",
            test_subtype_type_create_values
            )
        self.no_options   = [ FieldChoice('', label="(no options)") ]
        # Create type and data records for testing:
        self.test_supertype_type_info = EntityTypeInfo(
            self.testcoll, "test_supertype_type", create_typedata=True
            )
        self.test_subtype_type_info   = EntityTypeInfo(
            self.testcoll, "test_subtype_type",   create_typedata=True
            )
        for entity_id in ("test_subtype_entity",):
            self.test_subtype_type_info.create_entity(entity_id, test_subtype_entity_create_values(entity_id))
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

    def check_subtype_data(self, coll_id, type_id, entity_id, entity_vals):
        expected_types = [ "annal:EntityData", "test:%s"%type_id]
        expected_vals  = (
            { "@id":            "%s/%s"%(type_id, entity_id)
            , "@type":          expected_types
            , "rdfs:label":     "test_subtype_entity %s label"%(entity_id,)
            , "rdfs:comment":   "test_subtype_entity %s comment"%(entity_id,)
            })
        expected_vals.update(entity_vals)
        self.check_entity_values(type_id, entity_id, check_values=expected_vals)
        return

    # Tests

    def test_view_entity_references(self):
        coll_id   = "testcoll"
        type_id   = "test_subtype_type"
        entity_id = "test_subtype_entity"
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ['test:test_subtype_type', 'annal:EntityData']
            })
        # Update subtype definition to include supertype reference
        self.test_subtype_type[ANNAL.CURIE.supertype_uri] = [ { "@id": "test:test_supertype_type" } ]
        self.test_subtype_type._save()
        self.testcoll._update_type_cache(self.test_subtype_type)
        # Test migration of updated type information to data
        migrate_coll_data(self.testcoll)
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ['test:test_subtype_type', 'test:test_supertype_type', 'annal:EntityData']
            })
        return

# End.
