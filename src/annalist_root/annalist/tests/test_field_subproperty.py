"""
Tests for views and edits that use field subproperty URIs.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.contrib.auth.models     import User
from django.test                    import TestCase
from django.test.client             import Client

from annalist                       import layout
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.entity         import EntityRoot, Entity
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.entitydata     import EntityData

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site,
    init_annalist_test_coll,
    init_annalist_named_test_coll,
    resetSitedata
    )
from entity_testutils       import (
    collection_create_values,
    create_test_user, create_user_permissions,
    context_view_field,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    )
from entity_testtypedata    import (
    recordtype_create_values, 
    )

#   -----------------------------------------------------------------------------
#
#   Field alias tests
#
#   -----------------------------------------------------------------------------

class FieldSubpropertyTest(AnnalistTestCase):
    """
    Tests for field alias values
    """

    def setUp(self):
        self.testsite  = init_annalist_test_site()
        self.testcoll  = Collection.create(
            self.testsite, "testcoll", collection_create_values("testcoll")
            )
        # Create test type
        self.testtypes = RecordType.create(
            self.testcoll, "testtype", 
            recordtype_create_values(
                coll_id="testcoll", type_id="testtype", type_uri="test:testtype",
                supertype_uris=[]
                )
            )
        # Create test type data parents
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        # Create test field using superproperty
        self.test_sup_field = RecordField.create(self.testcoll, "Test_sup_field",
            { ANNAL.CURIE.type:                 "annal:Field"
            , RDFS.CURIE.label:                 "Field using superproperty URI"
            , RDFS.CURIE.comment:               "Field using superproperty URI"
            , ANNAL.CURIE.field_render_type:    "_enum_render_type/Text"
            , ANNAL.CURIE.field_value_mode:     "_enum_value_mode/Value_direct"
            , ANNAL.CURIE.field_entity_type:    "test:testtype"
            , ANNAL.CURIE.placeholder:          "(Test_sup_field)"
            , ANNAL.CURIE.property_uri:         "test:superprop_uri"
            , ANNAL.CURIE.field_placement:      "small:0,12;medium:0,6"
            })
        self.assertTrue(self.test_sup_field is not None)
        # Create test field using subproperty and declaring superproperty
        self.test_sub_field = RecordField.create(self.testcoll, "Test_sub_field",
            { ANNAL.CURIE.type:                 "annal:Field"
            , RDFS.CURIE.label:                 "Field using superproperty URI"
            , RDFS.CURIE.comment:               "Field using superproperty URI"
            , ANNAL.CURIE.field_render_type:    "_enum_render_type/Text"
            , ANNAL.CURIE.field_value_mode:     "_enum_value_mode/Value_direct"
            , ANNAL.CURIE.field_entity_type:    "test:testtype"
            , ANNAL.CURIE.placeholder:          "(Test_sub_field)"
            , ANNAL.CURIE.property_uri:         "test:subprop_uri"
            , ANNAL.CURIE.superproperty_uri:    [{"@id": "test:superprop_uri"}]
            , ANNAL.CURIE.field_placement:      "small:0,12;medium:0,6"
            })
        self.assertTrue(self.test_sub_field is not None)
        # Create test view using superproperty
        self.test_view = RecordView.create(self.testcoll, "testview",
            { ANNAL.CURIE.type:         "annal:View"
            , ANNAL.CURIE.uri:          "test:view"
            , RDFS.CURIE.label:         "Test view label"
            , RDFS.CURIE.comment:       "Test view comment"
            , ANNAL.CURIE.record_type:  "test:testtype"
            , ANNAL.CURIE.view_fields:
              [ { ANNAL.CURIE.field_id:         layout.FIELD_TYPEID+"/Entity_id"
                , ANNAL.CURIE.field_placement:  "small:0,12;medium:0,6"
                }
              , { ANNAL.CURIE.field_id:         layout.FIELD_TYPEID+"/Test_sup_field"
                , ANNAL.CURIE.field_placement:  "small:0,12;medium:0,6"
                }
              ]
            })
        self.assertTrue(self.test_view is not None)
        # Create test entity using subproperty
        self.testentity_data = EntityData.create(self.testdata, "testentity", 
            entitydata_create_values(
                "testentity", type_id="testtype",
                type_uri="test:testtype",
                extra_fields={"test:subprop_uri": "Test field value"} 
                )
            )

        #@@later
        # View test entity; check that value using subproperty is presented
        # Edit test entity; check that updated field value uses subproperty
        #@@

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
    def tearDownClass(cls):
        # resetSitedata()
        return

    def test_view_subproperty_field(self):
        u = entitydata_edit_url(
            "view", "testcoll", "testtype", 
            entity_id="testentity", 
            view_id="testview"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        url = entity_url(coll_id="testcoll", type_id="testtype", entity_id="testentity")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "testentity")
        self.assertEqual(r.context['orig_id'],          "testentity")
        self.assertEqual(r.context['action'],           "view")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # Check id field for sanity
        f1 = context_view_field(r.context, 0, 0)
        self.assertEqual(f1['field_id'], 'Entity_id')
        self.assertEqual(f1['field_property_uri'], ANNAL.CURIE.id)
        self.assertEqual(f1['field_value'], self.testentity_data[ANNAL.CURIE.id])
        # Check superproperty field value
        f2 = context_view_field(r.context, 1, 0)
        self.assertEqual(f2['field_id'], 'Test_sup_field')
        self.assertEqual(f2['field_property_uri'], "test:superprop_uri")
        self.assertEqual(f2['field_value'], self.testentity_data["test:subprop_uri"])
        return

    # def test_list_field_alias(self):
    #     # List BibEntry fields in Default_list
    #     u = entitydata_list_type_url("testcoll", "testtype", list_id="Default_list")
    #     r = self.client.get(u)
    #     self.assertEqual(r.status_code,   200)
    #     self.assertEqual(r.reason_phrase, "OK")
    #     # log.info(r.content) #@@
    #     # Test context
    #     self.assertEqual(r.context['coll_id'],  "testcoll")
    #     self.assertEqual(r.context['type_id'],  "testtype")
    #     self.assertEqual(r.context['list_choices']['field_value'], "Default_list")
    #     # Fields
    #     head_fields = context_list_head_fields(r.context)
    #     self.assertEqual(len(head_fields), 1)       # One row of 2 cols..
    #     self.assertEqual(len(head_fields[0]['row_field_descs']), 2)
    #     f0 = context_view_field(r.context, 0, 0)
    #     f1 = context_view_field(r.context, 0, 1)
    #     # 1st field
    #     self.assertEqual(f0['field_id'], 'Entity_id')
    #     self.assertEqual(f0['field_property_uri'], "annal:id")
    #     self.assertEqual(f0['field_value'], "")
    #     # 2nd field
    #     self.assertEqual(f1['field_id'], 'Entity_label')
    #     self.assertEqual(f1['field_property_uri'], "rdfs:label")
    #     self.assertEqual(f1['field_value'], "")
    #     # List entities (actually, just the one)
    #     entities = context_list_entities(r.context)
    #     self.assertEqual(len(entities), 1)
    #     self.assertEqual(
    #         context_list_item_field_value(r.context, entities[0], 0), 
    #         "testentity"
    #         )
    #     self.assertEqual(
    #         context_list_item_field_value(r.context, entities[0], 1), 
    #         self.testentity_data['bib:title']
    #         )
    #     return

    def test_save_subproperty_field(self):
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", 
            entity_id="testentity", 
            view_id="testview"
            )
        f = (
            { 'entity_id':          "testentity"
            , 'entity_type':        "testtype"
            , 'orig_id':            "testentity"
            , 'orig_type':          "testtype"
            , 'Test_sup_field':     "Updated subproperty value"
            , 'action':             "edit"
            , 'save':               "Save"
            })
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Check entity exists,and compare data with expected
        typeinfo = EntityTypeInfo(self.testcoll, "testtype")
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, "testentity"))
        e = typeinfo.entityclass.load(typeinfo.entityparent, "testentity")
        self.assertEqual(e.get_id(), "testentity")
        # Check superproperty value remains undefined
        self.assertEqual(e.get_values().get("test:superprop_uri", "undefined"), "undefined")
        # Check subproperty has been updated
        v = self.testentity_data.get_values().copy()
        v['test:subprop_uri']   = f['Test_sup_field']
        self.assertDictionaryMatch(e.get_values(), v)
        return

# End.
