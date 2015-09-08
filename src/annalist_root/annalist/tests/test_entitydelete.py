"""
Tests for EntityData default editing view
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
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entitydelete    import EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import create_test_user
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_all_url, entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_delete_confirm_form_data,
    )

class ConfirmEntityDataDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.testdata = RecordTypeData(self.testcoll, "testtype")
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(EntityDataDeleteConfirmedView.__name__, "EntityDataDeleteConfirmedView", "Check EntityDataDeleteConfirmedView class name")
        return

    # NOTE:  this logic only tests the entity deletion completion code.
    # It is assumed that the response to requesting entity deletion is checked elsewhere.
    def test_post_confirmed_remove_entity(self):
        t = EntityData.create(self.testdata, "deleteentity", entitydata_create_values("deleteentity"))
        self.assertTrue(EntityData.exists(self.testdata, "deleteentity"))
        # Submit positive confirmation
        u = entitydata_delete_confirm_url("testcoll", "testtype")
        f = entitydata_delete_confirm_form_data("deleteentity")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            entitydata_list_all_url("testcoll")
            )
        self.assertMatch(r['location'],    
            r"info_head=.*&info_message=.*deleteentity.*testcoll.*$"
            )
        self.assertNotIn("search=testcoll", r['location'])
        # Confirm deletion
        self.assertFalse(EntityData.exists(self.testcoll, "deleteentity"))
        return

    def test_post_confirmed_remove_entity_from_search(self):
        t = EntityData.create(self.testdata, "deleteentity", entitydata_create_values("deleteentity"))
        self.assertTrue(EntityData.exists(self.testdata, "deleteentity"))
        # Submit positive confirmation
        u = entitydata_delete_confirm_url("testcoll", "testtype")
        f = entitydata_delete_confirm_form_data("deleteentity", search="testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            entitydata_list_all_url("testcoll")
            )
        self.assertMatch(r['location'],    
            r"info_head=.*&info_message=.*deleteentity.*testcoll.*$"
            )
        self.assertIn("search=testcoll", r['location'])
        # Confirm deletion
        self.assertFalse(EntityData.exists(self.testcoll, "deleteentity"))
        return

# End.
