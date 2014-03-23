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

from annalist.views.defaultlist     import EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    entity_uri, entitydata_edit_uri, entitydata_delete_confirm_uri,
    entitydata_list_type_uri,
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
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
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
        u = entitydata_delete_confirm_uri("testcoll", "testtype")
        f = entitydata_delete_confirm_form_data("deleteentity")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            entitydata_list_type_uri("testcoll", "testtype")+
            r"\?info_head=.*&info_message=.*deleteentity.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(EntityData.exists(self.testcoll, "deleteentity"))
        return

# End.