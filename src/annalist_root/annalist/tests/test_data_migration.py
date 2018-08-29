from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

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
from annalist.models.recordgroup    import RecordGroup, RecordGroup_migration
from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.collectiondata import migrate_coll_data

from annalist.views.form_utils.fieldchoice  import FieldChoice

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    test_layout,
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    copySitedata,
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from .entity_testutils import (
    collection_entity_view_url,
    create_test_user,
    create_user_permissions,
    context_view_field,
    context_list_entities,
    context_list_head_fields,
    context_list_item_fields
    )
from .entity_testentitydata import (
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    )

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

# Test data for adding supertype URIs to entity type list

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

# Test data for record group migration

test_group_id            = "List_field_group"
test_group_create_values = (
    { "annal:type":                 "annal:Field_group"
    , "rdfs:label":                 "List fields group"
    , "rdfs:comment":               "Group for fields presented in a list view."
    , "annal:uri":                  "annal:group/List_field_group"
    , "annal:group_entity_type":    "annal:List_field"
    , "annal:group_fields":
      [ { "annal:field_id":         "_field/List_field_sel"
        , "annal:property_uri":     "annal:field_id"
        , "annal:field_placement":  "small:0,12;medium:0,6"
        }
      , { "annal:field_id":         "_field/List_field_placement"
        , "annal:property_uri":     "annal:field_placement"
        , "annal:field_placement":  "small:0,12;medium:6,6"
        }
      ]
    })

test_field_id = "List_fields"
test_field_group_create_values = (
    { "annal:type":                 "annal:Field"
    , "rdfs:label":                 "Fields"
    , "rdfs:comment":               "Fields presented in a list view."
    , "annal:uri":                  "annal:fields/List_fields"
    , "annal:field_render_type":    "_enum_render_type/Group_Seq_Row"
    , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
    , "annal:field_value_type":     "annal:List_field"
    , "annal:field_entity_type":    "annal:List_field"
    , "annal:placeholder":          "(list field description)"
    , "annal:tooltip":              "Fields presented in a list view."
    , "annal:property_uri":         "annal:list_fields"
    , "annal:field_placement":      "small:0,12"
    , "annal:group_ref":            "_group/List_field_group"
    , "annal:repeat_label_add":     "Add field"
    , "annal:repeat_label_delete":  "Remove selected field(s)"
    })

test_field_group_migrated_values = (
    { "annal:type":                 "annal:Field"
    , "rdfs:label":                 "Fields"
    , "rdfs:comment":               "Fields presented in a list view."
    , "annal:uri":                  "annal:fields/List_fields"
    , "annal:field_render_type":    "_enum_render_type/Group_Seq_Row"
    , "annal:field_value_mode":     "_enum_value_mode/Value_direct"
    , "annal:field_value_type":     "annal:List_field"
    , "annal:field_entity_type":    "annal:List_field"
    , "annal:placeholder":          "(list field description)"
    , "annal:tooltip":              "Fields presented in a list view."
    , "annal:property_uri":         "annal:list_fields"
    , "annal:field_placement":      "small:0,12"
    , "annal:field_fields":
      [ { "annal:field_id":         "_field/List_field_sel"
        , "annal:property_uri":     "annal:field_id"
        , "annal:field_placement":  "small:0,12;medium:0,6"
        }
      , { "annal:field_id":         "_field/List_field_placement"
        , "annal:property_uri":     "annal:field_placement"
        , "annal:field_placement":  "small:0,12;medium:6,6"
        }
      ]
    , "annal:repeat_label_add":     "Add field"
    , "annal:repeat_label_delete":  "Remove selected field(s)"
    })

test_field_tooltip_create_values = (
    { "annal:type":                 "annal:Field"
    , "rdfs:label":                 "Fields"
    , "rdfs:comment":               "Fields presented in a list view."
    , "annal:property_uri":         "annal:list_fields"
    })

test_field_tooltip_migrated_values = (
    { "annal:type":                 "annal:Field"
    , "rdfs:label":                 "Fields"
    , "rdfs:comment":               "# Fields\r\n\r\nFields presented in a list view."
    , "annal:tooltip":              "Fields presented in a list view."
    })

test_view_id = "test_view_id"

test_view_create_values = (
    { "annal:id":                   test_view_id
    , "annal:type":                 "annal:View"
    , "rdfs:label":                 "View label"
    , "rdfs:comment":               "# View comment"
    , "annal:record_type":          "_type/View"
    , "annal:view_fields":
      [ { "annal:field_id":         "Field_render"      } 
      , { "annal:field_id":         "Field_type"        } 
      , { "annal:field_id":         "View_target_type"  } 
      , { "annal:field_id":         "List_target_type"  } 
      ]
    })

test_view_migrated_values = (
    { "annal:id":                   test_view_id
    , "annal:type":                 "annal:View"
    , "rdfs:label":                 "View label"
    , "rdfs:comment":               "# View comment"
    , "annal:view_entity_type":     "_type/View"
    , "annal:view_fields":
      [ { "annal:field_id":         "_field/Field_render_type" } 
      , { "annal:field_id":         "_field/Field_value_type"  } 
      , { "annal:field_id":         "_field/View_entity_type"  } 
      , { "annal:field_id":         "_field/List_entity_type"  } 
      ]
    })

test_list_id = "test_list_id"

test_list_create_values = (
    { "annal:id":                   test_list_id
    , "annal:type":                 "annal:List"
    , "rdfs:label":                 "List label"
    , "rdfs:comment":               "# List comment"
    , "annal:display_type":         "List"
    , "annal:record_type":          "_type/List"
    , "annal:list_fields":
      [ { "annal:field_id":         "Field_render"      } 
      , { "annal:field_id":         "Field_type"        } 
      , { "annal:field_id":         "View_target_type"  } 
      , { "annal:field_id":         "List_target_type"  } 
      ]
    })

test_list_migrated_values = (
    { "annal:id":                   test_list_id
    , "annal:type":                 "annal:List"
    , "rdfs:label":                 "List label"
    , "rdfs:comment":               "# List comment"
    , "annal:display_type":         "_enum_list_type/List"
    , "annal:list_entity_type":     "_type/List"
    , "annal:list_fields":
      [ { "annal:field_id":         "_field/Field_render_type" } 
      , { "annal:field_id":         "_field/Field_value_type"  } 
      , { "annal:field_id":         "_field/View_entity_type"  } 
      , { "annal:field_id":         "_field/List_entity_type"  } 
      ]
    })



#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class DataMigrationTest(AnnalistTestCase):
    """
    Tests for entity data migration
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
            self.test_subtype_type_info.create_entity(
                entity_id, test_subtype_entity_create_values(entity_id)
                )
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def setUpClass(cls):
        super(DataMigrationTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(DataMigrationTest, cls).tearDownClass()
        resetSitedata(scope="all")
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

    def test_subtype_supertype_references(self):
        coll_id   = "testcoll"
        type_id   = "test_subtype_type"
        entity_id = "test_subtype_entity"
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ["test:test_subtype_type", "annal:EntityData"]
            })
        # Update subtype definition to include supertype reference
        test_subtype_meta = self.test_subtype_type.get_values()
        test_subtype_meta[ANNAL.CURIE.supertype_uri] = [ { "@id": "test:test_supertype_type" } ]
        self.testcoll.add_type(type_id, test_subtype_meta)
        # Test migration of updated type information to data
        migrate_coll_data(self.testcoll)
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ['test:test_subtype_type', 'test:test_supertype_type', 'annal:EntityData']
            })
        return

    def test_wrong_type_uri_references(self):
        coll_id   = "testcoll"
        type_id   = "test_subtype_type"
        entity_id = "test_subtype_entity"
        # Create subtype record with wrong type URI
        subtype_entity_values = test_subtype_entity_create_values(entity_id)
        entity = self.test_subtype_type_info.create_entity(
            entity_id, subtype_entity_values
            )
        entity[ANNAL.CURIE.type] = "test:wrong_type_uri"
        entity._save()
        # Test subtype entity created
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ['test:test_subtype_type', 'annal:EntityData']
            , 'annal:type': "test:wrong_type_uri"
            })
        # Update subtype definition to include supertype reference
        test_subtype_meta = self.test_subtype_type.get_values()
        test_subtype_meta[ANNAL.CURIE.supertype_uri] = [ { "@id": "test:test_supertype_type" } ]
        self.testcoll.add_type(type_id, test_subtype_meta)
        # Test migration of updated type information to data
        migrate_coll_data(self.testcoll)
        self.check_subtype_data(
            coll_id, type_id, entity_id, 
            { '@type':      ['test:test_subtype_type', 'test:test_supertype_type', 'annal:EntityData']
            , 'annal:type': "test:test_subtype_type"
            })
        return

    def test_field_fieldgroup_references(self):
        """
        Test migration of field group references in field definitions 
        """
        # Create field group
        self.test_group = RecordGroup_migration.create(
            self.testcoll, test_group_id, test_group_create_values
            )
        # Create field definition referencing field group
        self.test_field = RecordField.create(
            self.testcoll, test_field_id, test_field_group_create_values
            )
        # Apply migration to collection
        migrate_coll_data(self.testcoll)
        # Read field definition and check for inline field list
        field_data = self.check_entity_values(
            "_field", test_field_id, check_values=test_field_group_migrated_values
            )
        self.assertNotIn("annal:group_ref", field_data)
        self.check_entity_does_not_exist("_group", test_group_id)
        return

    def test_field_comment_tooltip(self):
        """
        Test migration of field without tooltip
        """
        # Create field definition
        self.test_field = RecordField.create(
            self.testcoll, test_field_id, test_field_tooltip_create_values
            )
        # Apply migration to collection
        migrate_coll_data(self.testcoll)
        # Read field definition and check for inline field list
        field_data = self.check_entity_values(
            "_field", test_field_id, check_values=test_field_tooltip_migrated_values
            )
        return

    def test_migrate_view_fields(self):
        """
        Test migration of view fields
        """
        self.test_view = RecordView.create(
            self.testcoll, test_view_id, test_view_create_values
            )
        migrate_coll_data(self.testcoll)
        # Read field definition and check for inline field list
        view_data = self.check_entity_values(
            "_view", test_view_id, check_values=test_view_migrated_values
            )
        return

    def test_migrate_list_fields(self):
        """
        Test migration of list fields
        """
        self.test_list = RecordList.create(
            self.testcoll, test_list_id, test_list_create_values
            )
        migrate_coll_data(self.testcoll)
        # Read field definition and check for inline field list
        view_data = self.check_entity_values(
            "_list", test_list_id, check_values=test_list_migrated_values
            )
        return

# End.
