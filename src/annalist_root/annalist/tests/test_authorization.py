"""
Tests for authorization functions
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

from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import ANNAL

from annalist.models.entity         import EntityRoot, Entity
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    create_user_permissions,
    collection_new_form_data, collection_remove_form_data,
    context_list_entities,
    context_list_item_fields, context_list_item_field_value
    )
from entity_testentitydata          import (
    # recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, 
    entitydata_delete_form_data,
    entitydata_delete_confirm_form_data
    )
from entity_testuserdata            import (
    annalistuser_dir,
    annalistuser_site_url, annalistuser_coll_url, annalistuser_url, annalistuser_edit_url,
    annalistuser_value_keys, annalistuser_load_keys,
    annalistuser_create_values, annalistuser_values, annalistuser_read_values,
    annalistuser_view_form_data,
    annalistuser_delete_form_data,
    annalistuser_delete_confirm_form_data
    )
from entity_testtypedata                import (
    recordtype_create_values, 
    recordtype_entity_view_form_data,
    recordtype_delete_form_data,
    recordtype_delete_confirm_form_data
    )


#   -----------------------------------------------------------------------------
#
#   Authorization tests
#
#   -----------------------------------------------------------------------------

class AuthorizationTest(AnnalistTestCase):
    """
    Tests for authorization (access control) logic
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite    = Site(TestBaseUri, TestBaseDir)
        self.testcoll    = Collection(self.testsite, "testcoll")
        # populate site with different classes of users: admin, config, create, update, delete, view
        self.user_admin  = AnnalistUser.create(self.testcoll, "user_admin", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_admin",
                user_name="Admin User",
                user_uri="mailto:user_admin@%s"%TestHost, 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
                )
            )
        self.user_config  = AnnalistUser.create(self.testcoll, "user_config", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_config",
                user_name="Admin User",
                user_uri="mailto:user_config@%s"%TestHost, 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
                )
            )
        self.user_create  = AnnalistUser.create(self.testcoll, "user_create", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_create",
                user_name="Admin User",
                user_uri="mailto:user_create@%s"%TestHost, 
                user_permissions=["VIEW", "UPDATE", "CREATE"]
                )
            )
        self.user_update  = AnnalistUser.create(self.testcoll, "user_update", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_update",
                user_name="Admin User",
                user_uri="mailto:user_update@%s"%TestHost, 
                user_permissions=["VIEW", "UPDATE"]
                )
            )
        self.user_delete  = AnnalistUser.create(self.testcoll, "user_delete", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_delete",
                user_name="Admin User",
                user_uri="mailto:user_delete@%s"%TestHost, 
                user_permissions=["VIEW", "UPDATE", "DELETE"]
                )
            )
        self.user_view  = AnnalistUser.create(self.testcoll, "user_view", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_view",
                user_name="Admin User",
                user_uri="mailto:user_view@%s"%TestHost, 
                user_permissions=["VIEW"]
                )
            )
        self.user_site_admin  = AnnalistUser.create(
            self.testsite, 
            "user_site_admin", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_site_admin",
                user_name="Site_admin User",
                user_uri="mailto:user_site_admin@%s"%TestHost, 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
                ),
            use_altpath=True
            )
        self.user_site_create_coll  = AnnalistUser.create(
            self.testsite, 
            "user_site_create_coll", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_site_create_coll",
                user_name="Site_create User",
                user_uri="mailto:user_site_create_coll@%s"%TestHost, 
                user_permissions=["VIEW", "CREATE_COLLECTION"]
                ),
            use_altpath=True
            )
        self.user_site_delete_coll  = AnnalistUser.create(
            self.testsite, 
            "user_site_delete_coll", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_site_delete_coll_coll",
                user_name="Site_delete User",
                user_uri="mailto:user_site_delete_coll@%s"%TestHost, 
                user_permissions=["VIEW", "CREATE_COLLECTION", "DELETE_COLLECTION"]
                ),
            use_altpath=True
            )
        self.user_site_view  = AnnalistUser.create(
            self.testsite, 
            "user_site_view", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_site_view",
                user_name="Site_view User",
                user_uri="mailto:user_site_view@%s"%TestHost, 
                user_permissions=["VIEW"]
                ),
            use_altpath=True
            )
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    # Utility functions

    def login_user(self, user_id):
        # Create user identity and log in (authenticate).  Updates the test client object.
        self.user = User.objects.create_user(user_id, '%s@%s'%(user_id, TestHost), 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username=user_id, password="testpassword")
        self.assertTrue(loggedin)
        return

    # View site home page
    def view_site_home_page(self):
        u = reverse("AnnalistSiteView")
        r = self.client.get(u)
        return r

    # Create collection: requires site-level CREATE permission

    def create_collection(self):
        u = reverse("AnnalistSiteView")
        f = collection_new_form_data("testnew")
        r = self.client.post(u, f)
        return r

    # Remove collection: requires site-level DELETE permission

    def remove_collection(self):
        u = reverse("AnnalistSiteView")
        f = collection_remove_form_data(["coll1", "coll3"])
        r = self.client.post(u, f)
        return r

    # User access - requires ADMIN permission

    def create_user(self, user_id):
        # Create placeholder for testing
        return create_user_permissions(
            self.testcoll, user_id, 
            ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )

    def list_users(self):
        # requires ADMIN
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="_user", 
            list_id="Default_list"
            )
        r = self.client.get(u)
        return r

    def view_user_get(self):
        # requires ADMIN
        e = self.create_user("view_user")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_user", entity_id="view_user", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        return r

    def view_user_edit(self):
        # requires ADMIN
        e = self.create_user("view_user")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_user", entity_id="view_user", 
            view_id="Default_view"
            )
        f = annalistuser_view_form_data(action="view",
            coll_id="testcoll", user_id="view_user",
            user_name="View User",
            user_uri="mailto:view_user@%s"%(TestHost), 
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
            edit="edit"
            )
        r = self.client.post(u, f)
        return r

    def view_user_copy(self):
        # requires ADMIN
        e = self.create_user("view_user")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_user", entity_id="view_user", 
            view_id="Default_view"
            )
        f = annalistuser_view_form_data(action="view",
            coll_id="testcoll", user_id="view_user",
            user_name="View User",
            user_uri="mailto:view_user@%s"%(TestHost), 
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
            copy="copy"
            )
        r = self.client.post(u, f)
        return r

    def new_user(self):
        # requires ADMIN
        u = entitydata_edit_url(action="new", 
            coll_id="testcoll", type_id="_user",
            view_id="Default_view"
            )
        f = annalistuser_view_form_data(action="new",
            coll_id="testcoll", user_id="new_user",
            user_name="New User",
            user_uri="mailto:new_user@%s"%(TestHost), 
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        r = self.client.post(u, f)
        return r

    def copy_user(self):
        # requires ADMIN
        e = self.create_user("copy_user")
        u = entitydata_edit_url(action="copy", 
            coll_id="testcoll", type_id="_user", entity_id="copy_user", 
            view_id="Default_view"
            )
        f = annalistuser_view_form_data(action="copy",
            coll_id="testcoll", user_id="copy_user_new", orig_id="copy_user",
            user_name="Copy User",
            user_uri="mailto:copy_user_new@%s"%(TestHost), 
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        r = self.client.post(u, f)
        return r

    def edit_user(self):
        e = self.create_user("edit_user")
        u = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id="_user", entity_id="edit_user", 
            view_id="Default_view"
            )
        f = annalistuser_view_form_data(action="edit",
            coll_id="testcoll", user_id="edit_user",
            user_name="Edit User",
            user_uri="mailto:edit_user@%s"%(TestHost), 
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        r = self.client.post(u, f)
        return r

    def delete_user(self):
        # requires ADMIN
        e = self.create_user("delete_user")
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="_user", 
            list_id="Default_list"
            )
        f = annalistuser_delete_form_data(user_id="delete_user")
        r = self.client.post(u, f)
        # log.info(r.content)
        return r

    def delete_user_confirmed(self):
        # requires ADMIN
        e = self.create_user("delete_user")
        u = entitydata_delete_confirm_url(coll_id="testcoll", type_id="_user")
        f = annalistuser_delete_confirm_form_data(user_id="delete_user")
        r = self.client.post(u, f)
        return r

    # Type access - requires VIEW/CONFIG permission

    def create_type(self, type_id):
        # Create placeholder for testing
        t = RecordType.create(self.testcoll, type_id, 
            recordtype_create_values(coll_id="testcoll", type_id="testtype")
            )
        return t

    def list_types(self):
        # requires VIEW
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="_type", 
            list_id="Default_list"
            )
        r = self.client.get(u)
        return r

    def view_type_get(self):
        # requires VIEW
        e = self.create_type("view_type")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_type", entity_id="view_type", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        return r

    def view_type_edit(self):
        # requires CONFIG
        e = self.create_type("view_type")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_type", entity_id="view_type", 
            view_id="Default_view"
            )
        f = recordtype_entity_view_form_data(action="view",
            coll_id="testcoll", type_id="_type", orig_id="view_type",
            edit="edit"
            )
        r = self.client.post(u, f)
        return r

    def view_type_copy(self):
        # requires CONFIG
        e = self.create_type("view_type")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="_type", entity_id="view_type", 
            view_id="Default_view"
            )
        f = recordtype_entity_view_form_data(action="view",
            coll_id="testcoll", type_id="_type", orig_id="view_type",
            copy="copy"
            )
        r = self.client.post(u, f)
        return r

    def new_type(self):
        # requires CONFIG
        u = entitydata_edit_url(action="new", 
            coll_id="testcoll", type_id="_type",
            view_id="Default_view"
            )
        f = recordtype_entity_view_form_data(action="new",
            coll_id="testcoll", 
            type_id="new_type", orig_id="orig_type"
            )
        r = self.client.post(u, f)
        return r

    def copy_type(self):
        # requires CONFIG
        e = self.create_type("copy_type")
        u = entitydata_edit_url(action="copy", 
            coll_id="testcoll", type_id="_type", entity_id="copy_type", 
            view_id="Default_view"
            )
        f = recordtype_entity_view_form_data(action="copy",
            coll_id="testcoll", 
            type_id="copy_type_new", orig_id="copy_type"
            )
        r = self.client.post(u, f)
        return r

    def edit_type(self):
        # requires CONFIG
        e = self.create_type("edit_type")
        u = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id="_type", entity_id="edit_type", 
            view_id="Default_view"
            )
        f = recordtype_entity_view_form_data(action="edit",
            coll_id="testcoll", 
            type_id="edit_type"
            )
        r = self.client.post(u, f)
        return r

    def delete_type(self):
        # requires CONFIG
        e = self.create_type("delete_type")
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="_type", 
            list_id="Default_list"
            )
        f = recordtype_delete_form_data(type_id="delete_type")
        # log.info("u %s"%u)
        # log.info("f %r"%f)
        r = self.client.post(u, f)
        # log.info(r.content)
        return r

    def delete_type_confirmed(self):
        # requires CONFIG
        e = self.create_type("delete_type")
        u = entitydata_delete_confirm_url(coll_id="testcoll", type_id="_type")
        f = entitydata_delete_confirm_form_data(entity_id="delete_type")
        r = self.client.post(u, f)
        return r

    # Data access - requires VIEW/CREATE/UPDATE/DELETE permissions

    def create_data(self, entity_id):
        # Create placeholder for testing
        typedata = RecordTypeData.create(self.testcoll, "Default_type", {})
        assert typedata is not None
        e = EntityData.create(typedata, entity_id, 
            entitydata_create_values(entity_id, coll_id="testcoll", type_id="Default_type")
            )
        return e

    def list_data(self):
        # requires VIEW
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="Default_type", 
            list_id="Default_list"
            )
        r = self.client.get(u)
        return r

    def view_data_get(self):
        # requires VIEW
        e = self.create_data("view_data")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="Default_type", entity_id="view_data", 
            view_id="Default_view"
            )
        r = self.client.get(u)
        return r

    def view_data_edit(self):
        # requires UPDATE
        e = self.create_data("view_data")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="Default_type", entity_id="view_data", 
            view_id="Default_view"
            )
        f = entitydata_form_data(action="edit",
            coll_id="testcoll", type_id="Default_data", 
            entity_id="view_data", orig_id="view_data",
            edit="edit"
            )
        r = self.client.post(u, f)
        return r

    def view_data_copy(self):
        # requires CREATE
        e = self.create_data("view_data")
        u = entitydata_edit_url(action="view", 
            coll_id="testcoll", type_id="Default_type", entity_id="view_data", 
            view_id="Default_view"
            )
        f = entitydata_form_data(action="copy",
            coll_id="testcoll", type_id="Default_data", 
            entity_id="copy_view_data", orig_id="view_data",
            copy="copy"
            )
        r = self.client.post(u, f)
        return r

    def new_data(self):
        # requires CREATE
        u = entitydata_edit_url(action="new", 
            coll_id="testcoll", type_id="Default_type",
            view_id="Default_view"
            )
        f = entitydata_form_data(action="new",
            coll_id="testcoll", type_id="Default_type", entity_id="new_entity"
            )
        r = self.client.post(u, f)
        return r

    def copy_data(self):
        # requires CREATE
        e = self.create_data("copy_entity")
        u = entitydata_edit_url(action="copy", 
            coll_id="testcoll", type_id="Default_type", entity_id="copy_entity", 
            view_id="Default_view"
            )
        f = entitydata_form_data(action="copy",
            coll_id="testcoll", type_id="Default_type", 
            entity_id="copy_entity_new", orig_id="copy_entity"
            )
        r = self.client.post(u, f)
        # log.info("r %s"%r)
        return r

    def edit_data(self):
        # requires UPDATE
        e = self.create_data("edit_entity")
        u = entitydata_edit_url(action="edit", 
            coll_id="testcoll", type_id="Default_type", entity_id="edit_entity", 
            view_id="Default_view"
            )
        f = entitydata_form_data(action="edit",
            coll_id="testcoll", type_id="Default_type", entity_id="edit_entity"
            )
        r = self.client.post(u, f)
        # log.info("r %s"%r)
        return r

    def delete_data(self):
        # requires DELETE
        e = self.create_data("delete_entity")
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="Default_type", 
            list_id="Default_list"
            )
        f = entitydata_delete_form_data(entity_id="delete_entity")
        # log.info("u %s"%u)
        # log.info("f %r"%f)
        r = self.client.post(u, f)
        # log.info(r)
        return r

    def delete_data_confirmed(self):
        # requires DELETE
        e = self.create_data("delete_entity")
        u = entitydata_delete_confirm_url(coll_id="testcoll", type_id="Default_type")
        f = entitydata_delete_confirm_form_data(entity_id="delete_entity")
        r = self.client.post(u, f)
        return r

    # Tests

    def test_bad_user_id(self):
        self.login_user("user-bad-name")
        with SuppressLogging(logging.WARNING):
            self.assertEqual(self.view_site_home_page().status_code, 400)
        return

    def test_admin_user(self):
        self.login_user("user_admin")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             200)
        self.assertEqual(self.view_user_get().status_code,          200)
        self.assertEqual(self.view_user_edit().status_code,         302)
        self.assertEqual(self.view_user_copy().status_code,         302)
        self.assertEqual(self.new_user().status_code,               302)
        self.assertEqual(self.copy_user().status_code,              302)
        self.assertEqual(self.edit_user().status_code,              302)
        self.assertEqual(self.delete_user().status_code,            200)
        self.assertEqual(self.delete_user_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         302)
        self.assertEqual(self.view_type_copy().status_code,         302)
        self.assertEqual(self.new_type().status_code,               302)
        self.assertEqual(self.copy_type().status_code,              302)
        self.assertEqual(self.edit_type().status_code,              302)
        self.assertEqual(self.delete_type().status_code,            200)
        self.assertEqual(self.delete_type_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         302)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_config_user(self):
        self.login_user("user_config")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         302)
        self.assertEqual(self.view_type_copy().status_code,         302)
        self.assertEqual(self.new_type().status_code,               302)
        self.assertEqual(self.copy_type().status_code,              302)
        self.assertEqual(self.edit_type().status_code,              302)
        self.assertEqual(self.delete_type().status_code,            200)
        self.assertEqual(self.delete_type_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         302)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_create_user(self):
        self.login_user("user_create")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         302)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_update_user(self):
        self.login_user("user_update")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_delete_user(self):
        self.login_user("user_delete")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_view_user(self):
        self.login_user("user_view")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         403)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_default_user(self):
        self.login_user("other_user")
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         403)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_no_login_user(self):
        # try each function, test result
        self.assertEqual(self.view_site_home_page().status_code,    200)
        self.assertEqual(self.create_collection().status_code,      401)
        self.assertEqual(self.remove_collection().status_code,      401)
        #
        self.assertEqual(self.list_users().status_code,             401)
        self.assertEqual(self.view_user_get().status_code,          401)
        self.assertEqual(self.view_user_edit().status_code,         401)
        self.assertEqual(self.view_user_copy().status_code,         401)
        self.assertEqual(self.new_user().status_code,               401)
        self.assertEqual(self.copy_user().status_code,              401)
        self.assertEqual(self.edit_user().status_code,              401)
        self.assertEqual(self.delete_user().status_code,            401)
        self.assertEqual(self.delete_user_confirmed().status_code,  401)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         401)
        self.assertEqual(self.view_type_copy().status_code,         401)
        self.assertEqual(self.new_type().status_code,               401)
        self.assertEqual(self.copy_type().status_code,              401)
        self.assertEqual(self.edit_type().status_code,              401)
        self.assertEqual(self.delete_type().status_code,            401)
        self.assertEqual(self.delete_type_confirmed().status_code,  401)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         401)
        self.assertEqual(self.view_data_copy().status_code,         401)
        self.assertEqual(self.new_data().status_code,               401)
        self.assertEqual(self.copy_data().status_code,              401)
        self.assertEqual(self.edit_data().status_code,              401)
        self.assertEqual(self.delete_data().status_code,            401)
        self.assertEqual(self.delete_data_confirmed().status_code,  401)
        return

    # Test site-level permissions

    def test_site_admin_user(self):
        self.login_user("user_site_admin")
        # try each function, test result
        self.assertEqual(self.create_collection().status_code,      302)
        self.assertEqual(self.remove_collection().status_code,      200)
        #
        self.assertEqual(self.list_users().status_code,             200)
        self.assertEqual(self.view_user_get().status_code,          200)
        self.assertEqual(self.view_user_edit().status_code,         302)
        self.assertEqual(self.view_user_copy().status_code,         302)
        self.assertEqual(self.new_user().status_code,               302)
        self.assertEqual(self.copy_user().status_code,              302)
        self.assertEqual(self.edit_user().status_code,              302)
        self.assertEqual(self.delete_user().status_code,            200)
        self.assertEqual(self.delete_user_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         302)
        self.assertEqual(self.view_type_copy().status_code,         302)
        self.assertEqual(self.new_type().status_code,               302)
        self.assertEqual(self.copy_type().status_code,              302)
        self.assertEqual(self.edit_type().status_code,              302)
        self.assertEqual(self.delete_type().status_code,            200)
        self.assertEqual(self.delete_type_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         302)
        self.assertEqual(self.view_data_copy().status_code,         302)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_site_create_user(self):
        self.login_user("user_site_create_coll")
        # try each function, test result
        self.assertEqual(self.create_collection().status_code,      302)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         403)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_site_delete_user(self):
        self.login_user("user_site_delete_coll")
        # try each function, test result
        self.assertEqual(self.create_collection().status_code,      302)
        self.assertEqual(self.remove_collection().status_code,      200)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         403)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_site_view_user(self):
        self.login_user("user_site_view")
        # try each function, test result
        self.assertEqual(self.create_collection().status_code,      403)
        self.assertEqual(self.remove_collection().status_code,      403)
        #
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.view_user_get().status_code,          403)
        self.assertEqual(self.view_user_edit().status_code,         403)
        self.assertEqual(self.view_user_copy().status_code,         403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.view_type_get().status_code,          200)
        self.assertEqual(self.view_type_edit().status_code,         403)
        self.assertEqual(self.view_type_copy().status_code,         403)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.view_data_get().status_code,          200)
        self.assertEqual(self.view_data_edit().status_code,         403)
        self.assertEqual(self.view_data_copy().status_code,         403)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    # Test permissions effect on entity lists

    def test_list_all(self):
        # Only list things we can view/list
        u = entitydata_list_all_url("testcoll", list_id="Default_list_all")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        # Entities and bound fields
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 2)
        entity_fields = (
            [ ('testtype',    '_type',    'RecordType testcoll/testtype')
            , ('entity1',     'testtype', 'Entity testcoll/testtype/entity1')
            ])
        for eid in range(2):
            for fid in range(3):
                item_field_value = context_list_item_field_value(r.context, entities[eid], fid)
                self.assertEqual(item_field_value, entity_fields[eid][fid])
        return

# End.
