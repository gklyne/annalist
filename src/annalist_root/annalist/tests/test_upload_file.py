"""
Tests for file upload functions.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
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

test_upload_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_upload_type label"
    , 'rdfs:comment':               "test_upload_type comment"
    , 'annal:uri':                  "test:type/test_upload_type"
    , 'annal:type_view':            "test_upload_view"
    , 'annal:type_list':            "test_upload_list"
    })

test_reference_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_reference_type label"
    , 'rdfs:comment':               "test_reference_type comment"
    , 'annal:uri':                  "test:type/test_reference_type"
    , 'annal:type_view':            "test_reference_view"
    , 'annal:type_list':            "test_reference_list"
    })

test_image_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_image_type label"
    , 'rdfs:comment':               "test_image_type comment"
    , 'annal:uri':                  "test:type/test_image_type"
    , 'annal:type_view':            "test_image_view"
    , 'annal:type_list':            "test_image_list"
    })

test_upload_file_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_upload_view label"
    , 'rdfs:comment':               "test_upload_view comment"
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
      , { 'annal:field_id':             "Test_upload_file"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_upload_image_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_upload_image_view label"
    , 'rdfs:comment':               "test_upload_image_view comment"
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
      , { 'annal:field_id':             "Test_upload_image"
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

test_image_ref_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_image_view label"
    , 'rdfs:comment':               "test_image_view comment"
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
      , { 'annal:field_id':             "Test_image_ref"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_image_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_image_view label"
    , 'rdfs:comment':               "test_image_view comment"
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
      , { 'annal:field_id':             "Test_image"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_upload_file_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "upl_field"
    , 'rdfs:label':                     "test_upload_file_field label"
    , 'rdfs:comment':                   "test_upload_file_field comment"
    , 'annal:property_uri':             "test:upload"
    , 'annal:field_render_type':        "FileUpload"
    , 'annal:field_value_mode':         "Value_upload"
    , 'annal:field_target_type':        "annal:Richtext"
    , 'annal:placeholder':              "(File to upload)"
    , 'annal:default_value':            ""
    })

test_upload_image_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "upl_field"
    , 'rdfs:label':                     "test_upload_image_field label"
    , 'rdfs:comment':                   "test_upload_image_field comment"
    , 'annal:property_uri':             "test:upload"
    , 'annal:field_render_type':        "FileUpload"
    , 'annal:field_value_mode':         "Value_upload"
    , 'annal:field_target_type':        "annal:Image"
    , 'annal:placeholder':              "(Image to upload)"
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
    , 'annal:field_target_type':        "annal:Identifier"
    , 'annal:field_ref_type':           "testupltype"
    , 'annal:field_ref_restriction':    "ALL"
    , 'annal:field_ref_field':          "test:upload"
    , 'annal:placeholder':              "(Uploaded file entity reference)"
    , 'annal:default_value':            ""
    })

test_image_ref_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "ref_image"
    , 'rdfs:label':                     "test_image_ref_field label"
    , 'rdfs:comment':                   "test_image_ref_field comment"
    , 'annal:property_uri':             "test:reference"
    , 'annal:field_render_type':        "RefImage"
    , 'annal:field_value_mode':         "Value_field"
    , 'annal:field_target_type':        "annal:Identifier"
    , 'annal:field_ref_type':           "testupltype"
    , 'annal:field_ref_restriction':    "ALL"
    , 'annal:field_ref_field':          "test:upload"
    , 'annal:placeholder':              "(Uploaded image reference)"
    , 'annal:default_value':            ""
    })

test_image_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "img_field"
    , 'rdfs:label':                     "test_image_field label"
    , 'rdfs:comment':                   "test_image_field comment"
    , 'annal:property_uri':             "test:image"
    , 'annal:field_render_type':        "RefImage"
    , 'annal:field_value_mode':         "Value_upload"
    , 'annal:field_target_type':        "annal:Image"
    , 'annal:placeholder':              "(Image to upload)"
    , 'annal:default_value':            ""
    })

def test_upload_file_field_value():
    return (
        { "resource_name":              "upl_field.md"
        , "resource_type":              "text/markdown"
        , "upload_name":                "upl_field"
        , "uploaded_size":              1005
        , "uploaded_file":              "README.md"
        })

def test_upload_image_field_value():
    return (
        { "resource_name":              "upl_field.jpg"
        , "resource_type":              "image/jpeg"
        , "upload_name":                "upl_field"
        , "uploaded_size":              1547926
        , "uploaded_file":              "test-image.jpg"
        })

def test_image_field_value():
    return (
        { "resource_name":              "img_field.jpg"
        , "resource_type":              "image/jpeg"
        , "upload_name":                "img_field"
        , "uploaded_size":              1547926
        , "uploaded_file":              "test-image.jpg"
        })

def test_imp_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_imp_entity %s label"%entity_id
        , 'rdfs:comment':               "test_imp_entity %s comment"%entity_id
        , 'test:upload':                test_upload_file_field_value()
        })

def test_ref_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_ref_entity %s label"%entity_id
        , 'rdfs:comment':               "test_ref_entity %s comment"%entity_id
        , 'test:reference':             "testupltype/"+entity_id
        })

def test_img_entity_create_values(entity_id):
    return (
        { 'rdfs:label':                 "test_img_entity %s label"%entity_id
        , 'rdfs:comment':               "test_img_entity %s comment"%entity_id
        , 'test:image':                 test_image_field_value()
        })

#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class UploadResourceTest(AnnalistTestCase):
    """
    Tests for resource import
    """

    def setUp(self):
        self.filepath  = "%s/README.md"%TestBaseDir
        self.fileuri   = "file://"+self.filepath
        self.imagepath = "%s/test-image.jpg"%TestBaseDir
        self.imageuri  = "file://"+self.imagepath
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection(self.testsite, "testcoll")
        # Populate collection with linked record types, views and lists

        # Types
        self.test_upl_type = RecordType.create(
            self.testcoll, "testupltype", test_upload_type_create_values
            )
        self.test_ref_type = RecordType.create(
            self.testcoll, "testreftype", test_reference_type_create_values
            )
        self.test_image_type = RecordType.create(
            self.testcoll, "testimgtype", test_image_type_create_values
            )

        # Views
        self.test_upl_file_view = RecordView.create(
            self.testcoll, "testuplfileview", test_upload_file_view_create_values
            )
        self.test_upl_image_view = RecordView.create(
            self.testcoll, "testuplimageview", test_upload_image_view_create_values
            )
        self.test_ref_file_view = RecordView.create(
            self.testcoll, "testrefview", test_reference_view_create_values
            )
        self.test_ref_image_view = RecordView.create(
            self.testcoll, "testimgrefview", test_image_ref_view_create_values
            )
        self.test_image_view = RecordView.create(
            self.testcoll, "testimgview", test_image_view_create_values
            )

        # Fields
        self.test_upl_file_field = RecordField.create(
            self.testcoll, "Test_upload_file", test_upload_file_field_create_values
            )
        self.test_upl_image_field = RecordField.create(
            self.testcoll, "Test_upload_image", test_upload_image_field_create_values
            )
        self.test_ref_file_field = RecordField.create(
            self.testcoll, "Test_reference", test_reference_field_create_values
            )
        self.test_ref_image_field = RecordField.create(
            self.testcoll, "Test_image_ref", test_image_ref_field_create_values
            )
        self.test_image_field = RecordField.create(
            self.testcoll, "Test_image", test_image_field_create_values
            )

        # Create data records for testing import and references:
        test_entity_ids = ("test1", "test2")
        test_entity_ids = ("test1",)
        self.test_upl_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testupltype", create_typedata=True
            )
        for entity_id in test_entity_ids:
            self.test_upl_type_info.create_entity(
                entity_id, test_imp_entity_create_values(entity_id)
                )
        self.test_ref_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testreftype", create_typedata=True
            )
        for entity_id in test_entity_ids:
            self.test_ref_type_info.create_entity(
                entity_id, test_ref_entity_create_values(entity_id)
                )
        self.test_img_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testimgtype", create_typedata=True
            )
        for entity_id in test_entity_ids:
            self.test_img_type_info.create_entity(
                entity_id, test_img_entity_create_values(entity_id)
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
        test1    = self.test_upl_type_info.get_entity("test1")
        test1dir, test1file = test1._dir_path()
        testobj1 = self.test_upl_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "wb"
            )
        testobj1.write("Test data test1res.txt")
        self.assertEqual(testobj1.name, test1dir+"/test1res.txt")
        testobj1.close()
        testobj2 = self.test_upl_type_info.get_fileobj(
            "test1", "test1res", "annal:Text", "text/plain", "rb"
            )
        self.assertEqual(testobj2.read(), "Test data test1res.txt")
        testobj2.close()
        return

    def test_util_fileobj(self):
        resource_fileobj, resource_url, resource_type = util.open_url(self.fileuri)
        self.assertEqual(resource_url,  self.fileuri)
        self.assertEqual(resource_type, "text/markdown")
        testobj1 = self.test_upl_type_info.get_fileobj(
            "test1", "test1res", "annal:Richtext", resource_type, "wb"
            )
        util.copy_resource_to_fileobj(resource_fileobj, testobj1)
        resource_fileobj.close()
        testobj1.close()
        # Read back both and compare
        siteobj = open(TestBaseDir+"/README.md", "rb")
        testobj = self.test_upl_type_info.get_fileobj(
            "test1", "test1res", "annal:Richtext", resource_type, "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_upload_file_resource(self):
        # See https://docs.djangoproject.com/en/1.7/topics/testing/tools/#django.test.Client.post
        with open(self.filepath) as fp:
            f = entitydata_default_view_form_data(entity_id="test1", action="edit")
            f['upl_field'] = fp     # Upload file with submission
            u = entitydata_edit_url("edit", "testcoll", "testupltype", entity_id="test1", view_id="testuplfileview")
            r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Retrieve updated form
        r = self.client.get(u)
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
        self.assertEqual(r.context['fields'][i].field_id,     "Test_upload_file")
        self.assertDictionaryMatch(r.context['fields'][i].field_value, test_upload_file_field_value())
        # Read back and compare entity resource just created
        siteobj = open(self.filepath, "rb")
        testobj = self.test_upl_type_info.get_fileobj(
            "test1", "upl_field", "annal:Richtext", "text/markdown", "rb"
            )
        self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_reference_uploaded_resource(self):
        # Create uploaded resource (see previous test)
        with open(self.filepath) as fp:
            f = entitydata_default_view_form_data(entity_id="test1", action="edit")
            f['upl_field'] = fp     # Upload file with submission
            u = entitydata_edit_url(
                "view", "testcoll", "testupltype", entity_id="test1", view_id="testuplfileview"
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
        basepath = TestBasePath + "/c/testcoll/d/testupltype/"
        # print "\n*****\n"+repr(r.context['fields'][i].target_value)+"\n*****\n"
        self.assertEqual(r.context['fields'][i].field_id,     "Test_reference")
        self.assertEqual(r.context['fields'][i].field_value,        "testupltype/test1")
        self.assertEqual(r.context['fields'][i].field_value_link,   basepath+"test1/")
        self.assertEqual(r.context['fields'][i].target_value['upload_name'],   "upl_field")
        self.assertEqual(r.context['fields'][i].target_value['resource_name'], "upl_field.md")
        self.assertEqual(r.context['fields'][i].target_value['resource_type'], "text/markdown")
        self.assertEqual(r.context['fields'][i].target_value['uploaded_file'], "README.md")
        self.assertEqual(r.context['fields'][i].target_value['uploaded_size'], 1005)
        self.assertEqual(r.context['fields'][i].target_value_link,  basepath+"test1/upl_field.md")
        return

    def test_upload_image_resource(self):
        # See https://docs.djangoproject.com/en/1.7/topics/testing/tools/#django.test.Client.post
        with open(self.imagepath) as fp:
            f = entitydata_default_view_form_data(entity_id="test1", action="edit")
            f['upl_field'] = fp     # Upload file with submission
            u = entitydata_edit_url("edit", "testcoll", "testupltype", entity_id="test1", view_id="testuplimageview")
            r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Retrieve updated form
        r = self.client.get(u)
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
        self.assertEqual(r.context['fields'][i].field_id,     "Test_upload_image")
        self.assertDictionaryMatch(r.context['fields'][i].field_value, test_upload_image_field_value())
        # Read back and compare entity resource just created
        siteobj = open(self.imagepath, "rb")
        testobj = self.test_upl_type_info.get_fileobj(
            "test1", "upl_field", "annal:Image", "image/jpeg", "rb"
            )
        self.assertTrue(siteobj.read() == testobj.read(), "Uploaded image != original")
        # self.assertEqual(siteobj.read(), testobj.read())
        return

    def test_reference_uploaded_image(self):
        self.test_upload_image_resource()

        # Display resource with image reference
        u = entitydata_edit_url("view", "testcoll", "testreftype", entity_id="test1", view_id="testimgrefview")
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
        basepath = TestBasePath + "/c/testcoll/d/testupltype/"
        # print "\n*****\n"+repr(r.context['fields'][i].target_value)+"\n*****\n"
        self.assertEqual(r.context['fields'][i].field_id,     "Test_image_ref")
        self.assertEqual(r.context['fields'][i].field_value,        "testupltype/test1")
        self.assertEqual(r.context['fields'][i].field_value_link,   basepath+"test1/")
        self.assertEqual(r.context['fields'][i].target_value['upload_name'],   "upl_field")
        self.assertEqual(r.context['fields'][i].target_value['resource_name'], "upl_field.jpg")
        self.assertEqual(r.context['fields'][i].target_value['resource_type'], "image/jpeg")
        self.assertEqual(r.context['fields'][i].target_value['uploaded_file'], "test-image.jpg")
        self.assertEqual(r.context['fields'][i].target_value['uploaded_size'], 1547926)
        self.assertEqual(r.context['fields'][i].target_value_link,  basepath+"test1/upl_field.jpg")
        # Check for rendered image link
        # log.info(r.content)
        field_details = (
            { "basepath":   TestBasePath
            , "coll_id":    "testcoll"
            , "type_id":    "testupltype"
            , "entity_id":  "test1"
            , "field_id":   "upl_field"
            })
        img_element = (
            """<div class="small-12 columns"> """+
              """<div class="row view-value-row"> """+
                """<div class="view-label small-12 medium-2 columns"> """+
                  """<span>test_image_ref_field label</span> """+
                """</div> """+
                """<div class="view-value small-12 medium-10 columns"> """+
                  """<a href="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg" target="_blank"> """+
                    """<img src="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg" """+
                    """     alt="Image at '%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg'" /> """+
                  """</a> """+
                """</div> """+
              """</div> """+
            """</div> """
            )%field_details
        self.assertContains(r, img_element, html=True)
        return

    def test_image_edit_field(self):
        # Upload to an image view field
        with open(self.imagepath) as fp:
            f = entitydata_default_view_form_data(entity_id="test1", action="edit")
            f['img_field'] = fp     # Upload file with submission
            u = entitydata_edit_url("edit", "testcoll", "testimgtype", entity_id="test1", view_id="testimgview")
            r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")

        # Read back and compare entity resource just created
        siteobj = open(self.imagepath, "rb")
        testobj = self.test_img_type_info.get_fileobj(
            "test1", "img_field", "annal:Image", "image/jpeg", "rb"
            )
        self.assertTrue(siteobj.read() == testobj.read(), "Referenced image != original")

        # Retrieve updated form
        r = self.client.get(u)
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
        self.assertEqual(r.context['fields'][i].field_id,     "Test_image")
        self.assertDictionaryMatch(r.context['fields'][i].field_value, test_image_field_value())
        return

    def test_image_view_field(self):
        # This test is for an image field that supports file upload in the same entity

        # Upload image
        self.test_image_edit_field()

        # Display resource in view mode
        u = entitydata_edit_url("view", "testcoll", "testimgtype", entity_id="test1", view_id="testimgview")
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
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_comment")
        i = 3
        basepath = TestBasePath + "/c/testcoll/d/testimgtype/"
        # print "\n*****\n"+repr(r.context['fields'][i].target_value)+"\n*****\n"
        self.assertEqual(r.context['fields'][i].field_id,           "Test_image")
        self.assertEqual(r.context['fields'][i].field_value,        test_image_field_value())
        self.assertEqual(r.context['fields'][i].target_value_link,  basepath+"test1/img_field.jpg")
        # Check for rendered image link
        # log.info(r.content)
        field_details = (
            { "basepath":   TestBasePath
            , "coll_id":    "testcoll"
            , "type_id":    "testimgtype"
            , "entity_id":  "test1"
            , "field_id":   "img_field"
            })
        img_element = (
            """<div class="small-12 columns"> """+
              """<div class="row view-value-row"> """+
                """<div class="view-label small-12 medium-2 columns"> """+
                  """<span>test_image_field label</span> """+
                """</div> """+
                """<div class="view-value small-12 medium-10 columns"> """+
                  """<a href="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg" target="_blank"> """+
                    """<img src="%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg" """+
                    """     alt="Image at '%(basepath)s/c/%(coll_id)s/d/%(type_id)s/%(entity_id)s/%(field_id)s.jpg'" /> """+
                  """</a> """+
                """</div> """+
              """</div> """+
            """</div> """
            )%field_details
        self.assertContains(r, img_element, html=True)
        return

    def test_image_edit(self):
        # This test that entity editing leaves attachment intact

        # Upload image
        self.test_image_edit_field()

        # Edit entity
        f = entitydata_default_view_form_data(entity_id="test1", action="edit", update="Updated")
        u = entitydata_edit_url("edit", "testcoll", "testimgtype", entity_id="test1", view_id="testimgview")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")

        # Retrieve updated form
        r = self.client.get(u)
        # Test context
        self.assertEqual(len(r.context['fields']), 4)
        i = 0
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_id")
        self.assertEqual(r.context['fields'][i].field_value,  "test1")
        i = 1
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_label")
        self.assertEqual(r.context['fields'][i].field_value,  "Updated testcoll/testtype/test1")
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_comment")
        i = 3
        self.assertEqual(r.context['fields'][i].field_id,     "Test_image")
        self.assertDictionaryMatch(r.context['fields'][i].field_value, test_image_field_value())

        # Read back and compare entity resource
        siteobj = open(self.imagepath, "rb")
        testobj = self.test_img_type_info.get_fileobj(
            "test1", "img_field", "annal:Image", "image/jpeg", "rb"
            )
        self.assertTrue(siteobj.read() == testobj.read(), "Edited entity image != original")
        return

    def test_image_rename(self):
        # This test that entity renaming also copies over an attachment

        # Upload image
        self.test_image_edit_field()

        # Rename entity
        f = entitydata_default_view_form_data(orig_id="test1", entity_id="test_new", action="edit")
        u = entitydata_edit_url("edit", "testcoll", "testimgtype", entity_id="test1", view_id="testimgview")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")

        # Read back and compare renamed entity resource
        siteobj = open(self.imagepath, "rb")
        testobj = self.test_img_type_info.get_fileobj(
            "test_new", "img_field", "annal:Image", "image/jpeg", "rb"
            )
        self.assertTrue(siteobj.read() == testobj.read(), "Renamed entity image != original")
        return

# End.
