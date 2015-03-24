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
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    create_test_user,
    create_user_permissions,
    context_list_entities,
    context_list_head_fields,
    context_list_item_fields
    )
# from entity_testentitydata          import (
#     entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
#     entitydata_list_type_url, entitydata_list_all_url,
#     )
from entity_testentitydata          import (
    # recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    # entitydata_list_type_url,
    # entitydata_value_keys, entitydata_create_values, entitydata_values,
    # entitydata_delete_confirm_form_data,
    entitydata_default_view_context_data, entitydata_default_view_form_data,
    # entitydata_recordtype_view_context_data, entitydata_recordtype_view_form_data,
    # default_fields, default_label, default_comment, error_label,
    # layout_classes
    )




#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

test_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_type label"
    , 'rdfs:comment':               "test_type comment"
    , 'annal:uri':                  "test:type/test_type"
    , 'annal:type_view':            "test_view"
    , 'annal:type_list':            "test_list"
    })

test_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_view label"
    , 'rdfs:comment':               "test_view comment"
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

test_import_field_create_values = (
    { 'annal:type':                 "annal:Field"
    , 'rdfs:label':                 "test_import_field label"
    , 'rdfs:comment':               "test_import_field comment"
    , 'annal:property_uri':         "test:import"
    , 'annal:field_value_type':     "annal:Markdown"
    , 'annal:field_render_type':    "URIImport"
    , 'annal:placeholder':          "(URI to import)"
    , 'annal:default_value':        ""
    })

def test_import_field_value():
    return (
        { "resource_name":            "Test_import.md"
        , "import_url":               "file://%s/README.md"%TestBaseDir
        , "resource_url":             "file://%s/README.md"%TestBaseDir
        , "import_name":              "Test_import"
        , "resource_type":            "text/markdown"
        })

def test_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_entity %s label"%entity_id
        , 'rdfs:comment':               "test_entity %s comment"%entity_id
        , 'test:import':                test_import_field_value()
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
        self.test_type = RecordType.create(self.testcoll, "testtype", test_type_create_values)
        self.test_view = RecordView.create(self.testcoll, "testview", test_view_create_values)
        self.test_import_field = RecordField.create(
            self.testcoll, "Test_import", test_import_field_create_values
            )
        # Create data records for testing:
        self.test_type_info = EntityTypeInfo(self.testsite, self.testcoll, "testtype", create_typedata=True)
        for entity_id in ("test1", "test2"):
            self.test_type_info.create_entity(entity_id, test_entity_create_values(entity_id))
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    # Utility functions

    # Tests

    def test_entity_fileobj(self):
        test1    = self.test_type_info.get_entity("test1")
        test1dir, test1file = test1._dir_path()
        testobj1 = self.test_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "wb"
            )
        testobj1.write("Test data test1res.txt")
        self.assertEqual(testobj1.name, test1dir+"/test1res.txt")
        testobj1.close()
        testobj2 = self.test_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "rb"
            )
        self.assertEqual(testobj2.read(), "Test data test1res.txt")
        testobj2.close()
        return

    def test_util_fileobj(self):
        resource_fileobj, resource_url, resource_type = util.open_url(self.fileuri)
        self.assertEqual(resource_url,  self.fileuri)
        self.assertEqual(resource_type, "text/markdown")
        testobj1 = self.test_type_info.get_fileobj(
            "test1", "test1res", "annal:Markdown", resource_type, "wb"
            )
        util.copy_resource_to_fileobj(resource_fileobj, testobj1)
        resource_fileobj.close()
        testobj1.close()
        # Read back both and compare
        siteobj = open(TestBaseDir+"/README.md", "rb")
        testobj = self.test_type_info.get_fileobj(
            "test1", "test1res", "annal:Markdown", resource_type, "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_import_resource(self):
        f = entitydata_default_view_form_data(entity_id="test1", action="edit", do_import="Test_import__import")
        f['Test_import'] = self.fileuri
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="test1", view_id="testview")
        r = self.client.post(u, f)
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
        testobj = self.test_type_info.get_fileobj(
            "test1", "Test_import", "annal:Markdown", "text/markdown", "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

# End.
