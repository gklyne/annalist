"""
Tests for resource import functions.
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

from annalist                       import util
from annalist.identifiers           import ANNAL
from annalist.models.entity         import EntityRoot, Entity
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.entitytypeinfo import EntityTypeInfo

from tests                          import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    create_test_user,
    create_user_permissions,
    context_list_entities,
    context_list_head_fields,
    context_list_item_fields
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    entitydata_default_view_context_data, entitydata_default_view_form_data,
    )

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

test_import_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_import_type label"
    , 'rdfs:comment':               "test_import_type comment"
    , 'annal:uri':                  "test:type/test_import_type"
    , 'annal:type_view':            "_view/test_import_view"
    , 'annal:type_list':            "_list/test_import_list"
    })

test_reference_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_reference_type label"
    , 'rdfs:comment':               "test_reference_type comment"
    , 'annal:uri':                  "test:type/test_reference_type"
    , 'annal:type_view':            "_view/test_reference_view"
    , 'annal:type_list':            "_list/test_reference_list"
    })

test_import_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_import_view label"
    , 'rdfs:comment':               "test_import_view comment"
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
      , { 'annal:field_id':             "Test_import"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_reference_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_reference_view label"
    , 'rdfs:comment':               "test_reference_view comment"
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
      , { 'annal:field_id':             "Test_reference"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_import_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "imp_field"
    , 'rdfs:label':                     "test_import_field label"
    , 'rdfs:comment':                   "test_import_field comment"
    , 'annal:property_uri':             "test:import"
    , 'annal:field_render_type':        "URIImport"
    , 'annal:field_value_mode':         "Value_import"
    , 'annal:field_value_type':         "annal:Richtext"
    , 'annal:placeholder':              "(URI to import)"
    , 'annal:default_value':            ""
    })

test_reference_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "ref_field"
    , 'rdfs:label':                     "test_reference_field label"
    , 'rdfs:comment':                   "test_reference_field comment"
    , 'annal:property_uri':             "test:reference"
    , 'annal:field_render_type':        "URILink"
    , 'annal:field_value_mode':         "Value_field"
    , 'annal:field_value_type':         "annal:Identifier"
    , 'annal:field_ref_type':           "testimptype"
    , 'annal:field_ref_restriction':    "ALL"
    , 'annal:field_ref_field':          "test:import"
    , 'annal:placeholder':              "(URI to import)"
    , 'annal:default_value':            ""
    })

def test_import_field_value():
    return (
        { "resource_name":              "imp_field.md"
        , "import_url":                 "file://%s/README.md"%TestBaseDir
        , "resource_url":               "file://%s/README.md"%TestBaseDir
        , "import_name":                "imp_field"
        , "resource_type":              "text/markdown"
        })

def test_imp_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_imp_entity %s label"%entity_id
        , 'rdfs:comment':               "test_imp_entity %s comment"%entity_id
        , 'test:import':                "" # test_import_field_value()
        })

def test_ref_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_ref_entity %s label"%entity_id
        , 'rdfs:comment':               "test_ref_entity %s comment"%entity_id
        , 'test:reference':             "testimptype/"+entity_id
        })

#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class ImportResourceTest(AnnalistTestCase):
    """
    Tests for resource import
    """

    def setUp(self):
        self.fileuri = "file://%s/README.md"%TestBaseDir
        init_annalist_test_site()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        # Populate collection with linked record types, views and lists
        self.test_imp_type = RecordType.create(
            self.testcoll, "testimptype", test_import_type_create_values
            )
        self.test_imp_view = RecordView.create(
            self.testcoll, "testimpview", test_import_view_create_values
            )
        self.test_imp_field = RecordField.create(
            self.testcoll, "Test_import", test_import_field_create_values
            )
        self.test_ref_type = RecordType.create(
            self.testcoll, "testreftype", test_reference_type_create_values
            )
        self.test_ref_view = RecordView.create(
            self.testcoll, "testrefview", test_reference_view_create_values
            )
        self.test_ref_field = RecordField.create(
            self.testcoll, "Test_reference", test_reference_field_create_values
            )
        # Create data records for testing import and references:
        self.test_imp_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testimptype", create_typedata=True
            )
        for entity_id in ("test1", "test2"):
            self.test_imp_type_info.create_entity(
                entity_id, test_imp_entity_create_values(entity_id)
                )
        self.test_ref_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testreftype", create_typedata=True
            )
        for entity_id in ("test1", "test2"):
            self.test_ref_type_info.create_entity(
                entity_id, test_ref_entity_create_values(entity_id)
                )
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

    def test_entity_fileobj(self):
        test1    = self.test_imp_type_info.get_entity("test1")
        test1dir, test1file = test1._dir_path()
        testobj1 = self.test_imp_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "wb"
            )
        testobj1.write("Test data test1res.txt")
        self.assertEqual(testobj1.name, test1dir+"/test1res.txt")
        testobj1.close()
        testobj2 = self.test_imp_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "rb"
            )
        self.assertEqual(testobj2.read(), "Test data test1res.txt")
        testobj2.close()
        return

    def test_util_fileobj(self):
        resource_fileobj, resource_url, resource_type = util.open_url(self.fileuri)
        self.assertEqual(resource_url,  self.fileuri)
        self.assertEqual(resource_type, "text/markdown")
        testobj1 = self.test_imp_type_info.get_fileobj(
            "test1", "test1res", "annal:Richtext", resource_type, "wb"
            )
        util.copy_resource_to_fileobj(resource_fileobj, testobj1)
        resource_fileobj.close()
        testobj1.close()
        # Read back both and compare
        siteobj = open(TestBaseDir+"/README.md", "rb")
        testobj = self.test_imp_type_info.get_fileobj(
            "test1", "test1res", "annal:Richtext", resource_type, "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_import_resource(self):
        f = entitydata_default_view_form_data(
            entity_id="test1", type_id="testimptype", action="edit", 
            do_import="imp_field__import"
            )
        f['imp_field'] = self.fileuri
        u = entitydata_edit_url(
            "edit", "testcoll", "testimptype", entity_id="test1", view_id="testimpview"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertMatch(r['location'], TestHostUri+u)
        # Read back form following redirect
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(len(r.context['fields']), 4)
        i = 0
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_id")
        self.assertEqual(r.context['fields'][i].field_value,  "test1")
        i = 1
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_label")
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_comment")
        i = 3
        self.assertEqual(r.context['fields'][i].field_id,     "Test_import")
        self.assertDictionaryMatch(r.context['fields'][i].field_value, test_import_field_value())
        # Read back and compare entity resource just created
        siteobj = open(TestBaseDir+"/README.md", "rb")
        testobj = self.test_imp_type_info.get_fileobj(
            "test1", "imp_field", "annal:Richtext", "text/markdown", "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_reference_imported_resource(self):
        # Create imported resource (see previous test)
        f = entitydata_default_view_form_data(
            entity_id="test1", type_id="testimptype", action="edit", 
            do_import="imp_field__import"
            )
        f['imp_field'] = self.fileuri
        u = entitydata_edit_url(
            "edit", "testcoll", "testimptype", entity_id="test1", view_id="testimpview"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Display resource with reference
        u = entitydata_edit_url(
            "view", "testcoll", "testreftype", entity_id="test1", view_id="testrefview"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check display context
        self.assertEqual(len(r.context['fields']), 4)
        i = 0
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_id")
        self.assertEqual(r.context['fields'][i].field_value,  "test1")
        i = 1
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_label")
        self.assertEqual(r.context['fields'][i].field_value,  "test_ref_entity test1 label")
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_comment")
        self.assertEqual(r.context['fields'][i].field_value,  "test_ref_entity test1 comment")
        i = 3
        basepath = TestBasePath + "/c/testcoll/d/testimptype/"
        self.assertEqual(r.context['fields'][i].field_id,           "Test_reference")
        self.assertEqual(r.context['fields'][i].field_value,        "testimptype/test1")
        self.assertEqual(r.context['fields'][i].field_value_link,   basepath+"test1/")
        # {u'resource_url': u'file:///usr/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/README.md'
        # , u'resource_name': u'imp_field.md'
        # , u'import_name': u'imp_field'
        # , u'resource_type': u'text/markdown'
        # , u'import_url': u'file:///usr/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/README.md'}
        self.assertEqual(r.context['fields'][i].target_value['import_name'],   "imp_field")
        self.assertEqual(r.context['fields'][i].target_value['resource_name'], "imp_field.md")
        self.assertEqual(r.context['fields'][i].target_value['resource_type'], "text/markdown")
        self.assertEqual(r.context['fields'][i].target_value_link,  basepath+"test1/imp_field.md")
        return

# End.
