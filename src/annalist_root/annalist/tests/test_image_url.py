"""
Tests image URL display field.

(Unlike test_render_ref_image, this tests rendering from saved data)

(Unlike test_upload_file, this tests rendering of a field with a direct URI value, 
not a reference to an upload/import field in some other entity)
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

test_image_ref_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_reference_type label"
    , 'rdfs:comment':               "test_reference_type comment"
    , 'annal:uri':                  "test:type/test_reference_type"
    , 'annal:type_view':            "test_reference_view"
    , 'annal:type_list':            "test_reference_list"
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

test_image_ref_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "ref_image"
    , 'rdfs:label':                     "test_image_ref_field label"
    , 'rdfs:comment':                   "test_image_ref_field comment"
    , 'annal:property_uri':             "test:reference"
    , 'annal:field_render_type':        "RefImage"
    , 'annal:field_value_mode':         "Value_direct"
    , 'annal:field_target_type':        "annal:Identifier"
    , 'annal:placeholder':              "(Image reference)"
    , 'annal:default_value':            ""
    })

def test_ref_entity_create_values(image_uri):
    return (
        { 'rdfs:label':                 "test_ref_image label"
        , 'rdfs:comment':               "test_ref_image comment"
        , 'test:reference':             image_uri
        })

#   -----------------------------------------------------------------------------
#
#   Linked record tests
#
#   -----------------------------------------------------------------------------

class ImageReferenceTest(AnnalistTestCase):
    """
    Tests image URI reference
    """

    def setUp(self):
        self.filepath  = "%s/README.md"%TestBaseDir
        self.fileuri   = "file://"+self.filepath
        self.imagepath = "%s/test-image.jpg"%TestBaseDir
        self.imageuri  = "file://"+self.filepath
        init_annalist_test_site()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        # Populate collection with linked record types, views and lists
        self.test_ref_type = RecordType.create(
            self.testcoll, "testreftype", test_image_ref_type_create_values
            )
        self.test_ref_view = RecordView.create(
            self.testcoll, "testrefview", test_image_ref_view_create_values
            )
        self.test_ref_field = RecordField.create(
            self.testcoll, "Test_image_ref", test_image_ref_field_create_values
            )
        # Create data records for testing image references:
        self.test_ref_type_info = EntityTypeInfo(
            self.testsite, self.testcoll, "testreftype", create_typedata=True
            )
        self.test_ref_type_info.create_entity("test1", test_ref_entity_create_values(self.imageuri))
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

    def test_reference_image(self):

        # Display resource with image reference
        u = entitydata_edit_url("view", "testcoll", "testreftype", entity_id="test1", view_id="testrefview")
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
        self.assertEqual(r.context['fields'][i].field_value,  "test_ref_image label")
        i = 2
        self.assertEqual(r.context['fields'][i].field_id,     "Entity_comment")
        self.assertEqual(r.context['fields'][i].field_value,  "test_ref_image comment")
        i = 3
        basepath = TestBasePath + "/c/testcoll/d/testreftype/"
        # print "\n*****\n"+repr(r.context['fields'][i])+"\n*****\n"
        self.assertEqual(r.context['fields'][i].field_id,           "Test_image_ref")
        self.assertEqual(r.context['fields'][i].field_value,        self.imageuri)
        self.assertEqual(r.context['fields'][i].field_value_link,   None)
        self.assertEqual(r.context['fields'][i].target_value,       self.imageuri)
        self.assertEqual(r.context['fields'][i].target_value_link,  self.imageuri)
        # Check for rendered image link
        # log.info(r.content)
        field_details = (
            { "basepath":   TestBasePath
            , "coll_id":    "testcoll"
            , "type_id":    "testupltype"
            , "entity_id":  "test1"
            , "image_uri":  self.imageuri
            , "field_id":   "ref_image"
            })
        img_element = (
            """<div class="small-12 columns"> """+
              """<div class="row view-value-row"> """+
                """<div class="view-label small-12 medium-2 columns"> """+
                  """<span>test_image_ref_field label</span> """+
                """</div> """+
                """<div class="view-value small-12 medium-10 columns"> """+
                  """<a href="%(image_uri)s" target="_blank"> """+
                    """<img src="%(image_uri)s" """+
                    """     alt="Image at '%(image_uri)s'" /> """+
                  """</a> """+
                """</div> """+
              """</div> """+
            """</div> """
            )%field_details
        self.assertContains(r, img_element, html=True)
        return

# End.
