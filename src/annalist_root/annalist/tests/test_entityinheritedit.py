"""
Tests for EntityData list view with additional inherited bibliography data
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
# from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from utils.SuppressLoggingContext   import SuppressLogging

from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.uri_builder             import uri_params, uri_with_params, continuation_params_url
from annalist.views.entitylist              import EntityGenericListView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site,
    init_annalist_test_coll,
    install_annalist_named_coll,
    create_test_coll_inheriting,
    init_annalist_named_test_coll,
    resetSitedata
    )
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url,
    collection_view_url, collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user, create_user_permissions,
    context_view_field,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value,
    check_context_field, check_context_field_value, check_context_list_field_value,
    check_field_list_context_fields,
    )
from entity_testtypedata    import (
    recordtype_dir, 
    recordtype_url,
    recordtype_create_values, 
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    default_view_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    get_site_bib_types, get_site_bib_types_sorted, get_site_bib_types_linked,
    get_site_bib_lists, get_site_bib_lists_sorted, get_site_bib_lists_linked,
    get_site_schema_types, get_site_schema_types_sorted, get_site_schema_types_linked,
    get_site_schema_lists, get_site_schema_lists_sorted, get_site_schema_lists_linked,
    )
from entity_testlistdata    import recordlist_url

#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------

class EntityInheritListViewTest(AnnalistTestCase):
    """
    Tests for get/copy/edit entity inherited from parent collection, 
    including tests of access control restrictions.
    """

    def setUp(self):
        self.testsite  = init_annalist_test_site()
        self.testcoll  = init_annalist_test_coll()
        self.testsubcoll = create_test_coll_inheriting(
            base_coll_id="testcoll", coll_id="testsubcoll", type_id="testtype"
            )
        create_test_user(self.testcoll,    "testuser",    "testpassword")
        create_test_user(self.testsubcoll, "testsubuser", "testpassword")
        # Allow user "testuser" access in collectrion "testsubcoll"
        user_permissions = ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
        user_id          = "testuser"
        user_perms = self.testsubcoll.create_user_permissions(
            user_id, "mailto:%s@%s"%(user_id, TestHost),
            "Test Subuser",
            "User %s: permissions for %s in collection %s"%
              ( user_id, "Test Subuser", self.testsubcoll.get_id() ),
            user_permissions)
        # Block user "testsubuser" access in collection "testcoll"
        user_permissions = []
        user_id          = "testsubuser"
        user_perms = self.testcoll.create_user_permissions(
            user_id, "mailto:%s@%s"%(user_id, TestHost),
            "Test Subuser",
            "User %s: permissions for %s in collection %s"%
              ( user_id, "Test Subuser", self.testcoll.get_id() ),
            user_permissions)
        # Block default user access in collection "testcoll"
        user_permissions = []
        user_id          = "_default_user_perms"
        user_uri         = "annal:User/_default_user_perms"
        user_perms = self.testcoll.create_user_permissions(
            user_id, user_uri,
            "Test Subuser",
            "User %s: permissions for %s in collection %s"%
              ( user_id, "Test Subuser", self.testcoll.get_id() ),
            user_permissions)
        # Create inherited entity "testcoll/testtype/entity2"
        self.testdata    = RecordTypeData.load(self.testcoll, "testtype")
        self.testentity2 = self._create_entity_data("entity2")
        self.testsubdata = RecordTypeData.load(self.testsubcoll, "testtype")
        # loggedin = self.client.login(username="testuser", password="testpassword")
        # self.assertTrue(loggedin)
        self.continuation_url = entitydata_list_type_url(
            coll_id="testsubcoll", type_id="testtype"
            )
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        # resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_entity_data(self, entity_id, update="Entity"):
        "Helper function creates entity data in 'testcoll/testtype' with supplied id"
        e = EntityData.create(self.testdata, entity_id, 
            entitydata_create_values(entity_id, update=update)
            )
        return e    

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    #   -----------------------------------------------------------------------------
    #   Form submission tests
    #   -----------------------------------------------------------------------------

    #   See: test_upload_file.py

    #   -----------------------------------------------------------------------------
    #   Access control tests
    #   -----------------------------------------------------------------------------

    #   ----- Confirm view/edit/copy operations with access allowed -----

    # GET inherited entity from collection with access allowed

    def test_get_view_inherited_entity(self):
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        u = entitydata_edit_url(
            "edit", "testsubcoll", 
            "testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertEqual(r.content,       "")
        return

    # POST edit inherited entity from collection with access allowed

    def test_post_edit_inherited_entity(self):
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        f = default_view_form_data(action="edit", 
            entity_id="entity2", type_id="testtype", coll_id="testsubcoll",
            orig_coll="testcoll"
            )
        u = entitydata_edit_url(
            "edit", "testsubcoll", "testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertIn(self.continuation_url, r['location'])
        # Check that new data exists
        self.assertTrue(EntityData.exists(self.testsubdata, "entity2"))
        return

    # POST copy inherited entity from collection with access allowed

    def test_post_copy_inherited_entity(self):
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        f = default_view_form_data(action="copy", 
            entity_id="entity2", type_id="testtype", coll_id="testsubcoll",
            orig_coll="testcoll"
            )
        u = entitydata_edit_url(action="copy", 
            coll_id="testsubcoll", type_id="testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertIn(self.continuation_url, r['location'])
        # Check that new data exists
        self.assertTrue(EntityData.exists(self.testsubdata, "entity2"))
        return

    #   ----- Confirm view/edit/copy operations with access disallowed -----

    # GET inherited entity from collection with no access

    def test_post_edit_inherited_entity_no_access(self):
        loggedin = self.client.login(username="testsubuser", password="testpassword")
        # self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        f = default_view_form_data(action="edit", 
            entity_id="entity2", type_id="testtype", coll_id="testsubcoll",
            orig_coll="testcoll"
            )
        u = entitydata_edit_url(
            "edit", "testsubcoll", "testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   403)
        self.assertEqual(r.reason_phrase, "Forbidden")
        # Check that no new data exists
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        return

    # POST edit inherited entity from collection with no access

    def test_post_edit_inherited_entity_no_access(self):
        loggedin = self.client.login(username="testsubuser", password="testpassword")
        self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        f = default_view_form_data(action="edit", 
            entity_id="entity2", type_id="testtype", coll_id="testsubcoll",
            orig_coll="testcoll"
            )
        u = entitydata_edit_url(
            "edit", "testsubcoll", "testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        # print "@@@@ r.content %r, r['location'] %r"%(r.content, r['location'])
        self.assertEqual(r.status_code,   403)
        self.assertEqual(r.reason_phrase, "Forbidden")
        # Check that no new data exists
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        return

    # POST copy inherited entity from collection with no access
    def test_post_copy_inherited_entity_no_access(self):
        loggedin = self.client.login(username="testsubuser", password="testpassword")
        self.assertTrue(loggedin)
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        f = default_view_form_data(action="copy", 
            entity_id="entity2", type_id="testtype", coll_id="testsubcoll",
            orig_coll="testcoll"
            )
        u = entitydata_edit_url(action="copy", 
            coll_id="testsubcoll", type_id="testtype", entity_id="entity2", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   403)
        self.assertEqual(r.reason_phrase, "Forbidden")
        # Check that no new data exists
        self.assertFalse(EntityData.exists(self.testsubdata, "entity2"))
        return

# End.
