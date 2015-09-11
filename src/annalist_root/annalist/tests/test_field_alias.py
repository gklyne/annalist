"""
Tests for views that use field aliased.
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
from django.test.client             import Client

from annalist.identifiers           import ANNAL, RDFS

from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.entity         import EntityRoot, Entity
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase

from entity_testutils               import (
    collection_create_values,
    create_test_user, create_user_permissions,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value
    )

from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    )

#   -----------------------------------------------------------------------------
#
#   Field alias tests
#
#   -----------------------------------------------------------------------------

class FieldAliasTest(AnnalistTestCase):
    """
    Tests for field alias values
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        # Create BibEntry record (BibEntry_type defines field alias)
        self.testdata   = RecordTypeData.create(self.testcoll, "BibEntry_type", {})
        self.bibentity1_data = (
            { "@type": 
                [ "bib:BibEntry"
                , ANNAL.CURIE.EntityData
                ]
            , ANNAL.CURIE.type: ANNAL.CURIE.EntityData
            , ANNAL.CURIE.type_id: "BibEntry_type"
            , "bib:type": "article"
            , "bib:title": "bib:title for bibentity1"
            , "bib:note": "Sample bibliographic entry with field aliasing"
            , "bib:month": "09"
            , "bib:year": "2014"
            , "bib:author": [
                { "bib:id": "author_id"
                , "bib:name": "Author, J. H."
                , "bib:alternate": "Joe H. Author"
                , "bib:firstname": "Joe"
                , "bib:lastname": "Author"
                }]
            , "bib:identifier": []
            , "bib:journal": []
            , "bib:editor": []
            , "bib:publication_details": []
            , "bib:license": []
            , "bib:bookentry": []
            })
        self.testbib1   = EntityData.create(self.testdata, "bibentity1", self.bibentity1_data)
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

    def test_view_field_alias(self):
        # View BibEntry field in Default_view
        u = entitydata_edit_url(
            "edit", "testcoll", "BibEntry_type", 
            entity_id="bibentity1", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        # Test context
        url = entity_url(coll_id="testcoll", type_id="BibEntry_type", entity_id="bibentity1")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "BibEntry_type")
        self.assertEqual(r.context['entity_id'],        "bibentity1")
        self.assertEqual(r.context['orig_id'],          "bibentity1")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        self.assertEqual(len(r.context['fields']), 4)        
        # Check aliased label field
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_property_uri'], RDFS.CURIE.label)
        self.assertEqual(r.context['fields'][2]['field_value'], self.bibentity1_data['bib:title'])
        return

    def test_list_field_alias(self):
        # List BibEntry fields in Default_list
        u = entitydata_list_type_url("testcoll", "BibEntry_type", list_id="Default_list")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content) #@@
        # Test context
        self.assertEqual(r.context['coll_id'],  "testcoll")
        self.assertEqual(r.context['type_id'],  "BibEntry_type")
        self.assertEqual(r.context['list_choices']['field_value'], "Default_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 2)
        # 1st field
        self.assertEqual(head_fields[0]['field_id'], 'Entity_id')
        self.assertEqual(head_fields[0]['field_property_uri'], "annal:id")
        self.assertEqual(head_fields[0]['field_value'], "")
        # 2nd field
        self.assertEqual(head_fields[1]['field_id'], 'Entity_label')
        self.assertEqual(head_fields[1]['field_property_uri'], "rdfs:label")
        self.assertEqual(head_fields[1]['field_value'], "")
        # List entities (actually, just the one)
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 1)
        self.assertEqual(
            context_list_item_field_value(r.context, entities[0], 0), 
            "bibentity1"
            )
        self.assertEqual(
            context_list_item_field_value(r.context, entities[0], 1), 
            self.bibentity1_data['bib:title']
            )
        return

    def test_save_field_alias_source(self):
        # Save BibEntry from BibEntry_view: aliases should not be included
        u = entitydata_edit_url(
            "edit", "testcoll", "BibEntry_type", 
            entity_id="bibentity1", 
            view_id="BibEntry_view"
            )
        f = (
            { 'entity_id':          "bibentity1"
            , 'entity_type':        "BibEntry_type"
            , 'orig_id':            "bibentity1"
            , 'orig_type':          "BibEntry_type"
            , 'Bib_type':           "article"
            , 'Bib_title':          "Updated "+self.bibentity1_data['bib:title']
            , 'Bib_year':           "2014"
            , 'Bib_month':          "09"
            , 'Bib_note':           "Updated "+self.bibentity1_data['bib:note']
            , 'action':             "edit"
            , 'save':               "Save"
            })
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Check entity exists,and compare data with expected
        typeinfo = EntityTypeInfo(self.testsite, self.testcoll, "BibEntry_type")
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, "bibentity1"))
        e = typeinfo.entityclass.load(typeinfo.entityparent, "bibentity1")
        self.assertEqual(e.get_id(), "bibentity1")
        v = self.bibentity1_data.copy()
        v['bib:title']        = f['Bib_title']
        v['bib:note']         = f['Bib_note']
        del v['bib:author']
        self.assertDictionaryMatch(e.get_values(), v)
        self.assertEqual(e.get_values().get(RDFS.CURIE.label, None),   None)
        self.assertEqual(e.get_values().get(RDFS.CURIE.comment, None), None)
        return

    def test_save_field_alias_target(self):
        # Save BibEntry from Default_view: aliased values should be included
        u = entitydata_edit_url(
            "edit", "testcoll", "BibEntry_type", 
            entity_id="bibentity1", 
            view_id="Default_view"
            )
        f = (
            { 'entity_id':          "bibentity1"
            , 'entity_type':        "BibEntry_type"
            , 'orig_id':            "bibentity1"
            , 'orig_type':          "BibEntry_type"
            , 'Entity_label':       "Updated "+self.bibentity1_data['bib:title']
            , 'Entity_comment':     "Updated "+self.bibentity1_data['bib:note']
            , 'action':             "edit"
            , 'save':               "Save"
            })
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Check entity exists,and compare data with expected
        typeinfo = EntityTypeInfo(self.testsite, self.testcoll, "BibEntry_type")
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, "bibentity1"))
        e = typeinfo.entityclass.load(typeinfo.entityparent, "bibentity1")
        self.assertEqual(e.get_id(), "bibentity1")
        v = self.bibentity1_data.copy()
        v[RDFS.CURIE.label]   = f['Entity_label']
        v[RDFS.CURIE.comment] = f['Entity_comment']
        self.assertDictionaryMatch(e.get_values(), v)
        return

# End.
