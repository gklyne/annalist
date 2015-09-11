"""
Entity editing tests for duplicated fields
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.db                      import models
from django.http                    import QueryDict
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout

from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    continuation_url_param,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_create_values, 
    )
from entity_testviewdata            import (
    recordview_url, 
    recordview_create_values, recordview_values, recordview_values_add_field,
    recordview_entity_view_form_data
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    entitydata_value_keys,
    entitydata_create_values, entitydata_values, entitydata_values_add_field, 
    # entitydata_default_view_form_data,
    entitydata_form_data, entitydata_form_add_field,
    default_comment
    )

#   -----------------------------------------------------------------------------
#
#   Entity edit duplicated field tests
#
#   -----------------------------------------------------------------------------

class EntityEditDupFieldTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})

        # Create view with duplicate field id
        self.viewdata = recordview_create_values(view_id="DupField_view")
        recordview_values_add_field(
            self.viewdata, 
            field_id="Entity_comment", 
            field_placement="small:0,12"
            )
        recordview_values_add_field(
            self.viewdata, 
            field_id="Entity_comment",
            field_property_uri="rdfs:comment_alt",
            field_placement="small:0,12"
            )
        self.testview = RecordView.create(self.testcoll, "DupField_view", self.viewdata)

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

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _check_record_view_values(self, view_id, view_values):
        "Helper function checks content of record view entry with supplied view_id"
        self.assertTrue(RecordView.exists(self.testcoll, view_id))
        t = RecordView.load(self.testcoll, view_id)
        self.assertEqual(t.get_id(), view_id)
        self.assertDictionaryMatch(t.get_values(), view_values)
        return t

    def _create_entity_data(self, 
        entity_id, type_id="testtype", update="Entity", 
        comment2="Comment field 2",
        comment3="Comment field 3"
        ):
        "Helper function creates entity data with supplied entity_id"
        v = entitydata_create_values(entity_id, type_id=type_id, update=update)
        v = entitydata_values_add_field(v, "rdfs:comment", 2, comment2)
        v = entitydata_values_add_field(v, "rdfs:comment_alt", 3, comment3)
        e = EntityData.create(self.testdata, entity_id, v)
        return e    

    def _check_entity_data_values(self, 
        entity_id, type_id="testtype", update="Entity", 
        comment2="Comment field 2",
        comment3="Comment field 3"
        ):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        # log.info("_check_entity_data_values: type_id %s, entity_id %s"%(type_id, entity_id))
        typeinfo = EntityTypeInfo(self.testsite, self.testcoll, type_id)
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, entity_id))
        e = typeinfo.entityclass.load(typeinfo.entityparent, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        v = entitydata_values(entity_id, type_id=type_id, update=update)
        v = entitydata_values_add_field(v, "rdfs:comment", 2, comment2)
        v = entitydata_values_add_field(v, "rdfs:comment_alt", 3, comment3)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    def test_view_dup_field_values(self):
        self._check_record_view_values("DupField_view", self.viewdata)
        return

    def test_dup_field_display(self):
        # Create entity with duplicate fields
        self._create_entity_data("entitydupfield")
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Entity", 
            comment2="Comment field 2",
            comment3="Comment field 3"
            )
        # Display entity in view with duplicate fields
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", 
            entity_id="entitydupfield",
            view_id="DupField_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "Collection testcoll")
        # Check display context
        self.assertEqual(len(r.context['fields']), 6)
        # 4th field - 1st comment
        comment_value = "Entity coll testcoll, type testtype, entity entitydupfield"
        self.assertEqual(r.context['fields'][3]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value'], comment_value)
        # 5th field - 2nd comment
        comment2_value = "Comment field 2"
        self.assertEqual(r.context['fields'][4]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Entity_comment__2')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "rdfs:comment__2")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value'], comment2_value)
        # 6th field - 3rd comment
        comment2_value = "Comment field 3"
        self.assertEqual(r.context['fields'][5]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Entity_comment__3')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "rdfs:comment_alt")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][5]['field_value'], comment2_value)
        return

    def test_dup_field_update(self):
        # Create entity with duplicate fields
        self._create_entity_data("entitydupfield")
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Entity", 
            comment2="Comment field 2",
            comment3="Comment field 3"
            )
        # Post form data to update entity
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", 
            entity_id="entitydupfield",
            view_id="DupField_view"
            )
        f = entitydata_form_data(
            entity_id="entitydupfield",
            type_id="testtype",
            coll_id="testcoll", 
            action="edit", update="Updated Entity"
            )
        f = entitydata_form_add_field(f, "Entity_comment", 2, "Update comment 2")
        f = entitydata_form_add_field(f, "Entity_comment", 3, "Update comment 3")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        # Test resulting entity value
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Updated Entity", 
            comment2="Update comment 2",
            comment3="Update comment 3"
            )
        return

# End.
