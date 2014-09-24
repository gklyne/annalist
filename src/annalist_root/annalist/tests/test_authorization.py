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
from django.test.client             import Client

from annalist.identifiers           import ANNAL
from annalist.models.entity         import EntityRoot, Entity
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testentitydata          import (
    # recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, 
    entitydata_delete_form_data,
    entitydata_delete_confirm_form_data,
    # entitylist_form_data,
    # get_site_lists
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
    # recordtype_dir,
    # recordtype_coll_url, recordtype_site_url, recordtype_url, recordtype_edit_url,
    # recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, 
    # recordtype_values, recordtype_read_values,
    # recordtype_entity_view_context_data, 
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
                user_uri="mailto:user_admin@example.org", 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
                )
            )
        self.user_config  = AnnalistUser.create(self.testcoll, "user_config", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_config",
                user_name="Admin User",
                user_uri="mailto:user_config@example.org", 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
                )
            )
        self.user_create  = AnnalistUser.create(self.testcoll, "user_create", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_create",
                user_name="Admin User",
                user_uri="mailto:user_create@example.org", 
                user_permissions=["VIEW", "UPDATE", "CREATE"]
                )
            )
        self.user_update  = AnnalistUser.create(self.testcoll, "user_update", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_update",
                user_name="Admin User",
                user_uri="mailto:user_update@example.org", 
                user_permissions=["VIEW", "UPDATE"]
                )
            )
        self.user_delete  = AnnalistUser.create(self.testcoll, "user_delete", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_delete",
                user_name="Admin User",
                user_uri="mailto:user_delete@example.org", 
                user_permissions=["VIEW", "UPDATE", "DELETE"]
                )
            )
        self.user_view  = AnnalistUser.create(self.testcoll, "user_view", 
            annalistuser_create_values(
                coll_id="testcoll", user_id="user_view",
                user_name="Admin User",
                user_uri="mailto:user_view@example.org", 
                user_permissions=["VIEW"]
                )
            )
        return

    def tearDown(self):
        return

    # Utility functions

    def login_user(self, user_id):
        # Create user identity and log in (authenticate).  Updates the test client object.
        self.user = User.objects.create_user(user_id, '%s@test.example.org'%(user_id), 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username=user_id, password="testpassword")
        self.assertTrue(loggedin)
        return

    # User access - requires ADMIN permission

    def create_user(self, user_id):
        # Create placeholder for testing
        user = AnnalistUser.create(self.testcoll, user_id, 
            annalistuser_create_values(
                coll_id="testcoll", user_id=user_id,
                user_name="Test User",
                user_uri="mailto:%s@example.org"%(user_id), 
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
                )
            )
        return user

    def list_users(self):
        # requires ADMIN
        u = entitydata_list_type_url(
            coll_id="testcoll", type_id="_user", 
            list_id="Default_list"
            )
        r = self.client.get(u)
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
            user_uri="mailto:new_user@example.org", 
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
            user_uri="mailto:copy_user_new@example.org", 
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
            user_uri="mailto:edit_user@example.org", 
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

    def test_admin_user(self):
        self.login_user("user_admin")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             200)
        self.assertEqual(self.new_user().status_code,               302)
        self.assertEqual(self.copy_user().status_code,              302)
        self.assertEqual(self.edit_user().status_code,              302)
        self.assertEqual(self.delete_user().status_code,            200)
        self.assertEqual(self.delete_user_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               302)
        self.assertEqual(self.copy_type().status_code,              302)
        self.assertEqual(self.edit_type().status_code,              302)
        self.assertEqual(self.delete_type().status_code,            200)
        self.assertEqual(self.delete_type_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_config_user(self):
        self.login_user("user_config")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               302)
        self.assertEqual(self.copy_type().status_code,              302)
        self.assertEqual(self.edit_type().status_code,              302)
        self.assertEqual(self.delete_type().status_code,            200)
        self.assertEqual(self.delete_type_confirmed().status_code,  302)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_create_user(self):
        self.login_user("user_create")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               302)
        self.assertEqual(self.copy_data().status_code,              302)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_update_user(self):
        self.login_user("user_update")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_delete_user(self):
        self.login_user("user_delete")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              302)
        self.assertEqual(self.delete_data().status_code,            200)
        self.assertEqual(self.delete_data_confirmed().status_code,  302)
        return

    def test_view_user(self):
        self.login_user("user_view")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_default_user(self):
        self.login_user("other_user")
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             403)
        self.assertEqual(self.new_user().status_code,               403)
        self.assertEqual(self.copy_user().status_code,              403)
        self.assertEqual(self.edit_user().status_code,              403)
        self.assertEqual(self.delete_user().status_code,            403)
        self.assertEqual(self.delete_user_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               403)
        self.assertEqual(self.copy_type().status_code,              403)
        self.assertEqual(self.edit_type().status_code,              403)
        self.assertEqual(self.delete_type().status_code,            403)
        self.assertEqual(self.delete_type_confirmed().status_code,  403)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               403)
        self.assertEqual(self.copy_data().status_code,              403)
        self.assertEqual(self.edit_data().status_code,              403)
        self.assertEqual(self.delete_data().status_code,            403)
        self.assertEqual(self.delete_data_confirmed().status_code,  403)
        return

    def test_no_login_user(self):
        # try each function, test result
        self.assertEqual(self.list_users().status_code,             401)
        self.assertEqual(self.new_user().status_code,               401)
        self.assertEqual(self.copy_user().status_code,              401)
        self.assertEqual(self.edit_user().status_code,              401)
        self.assertEqual(self.delete_user().status_code,            401)
        self.assertEqual(self.delete_user_confirmed().status_code,  401)
        #
        self.assertEqual(self.list_types().status_code,             200)
        self.assertEqual(self.new_type().status_code,               401)
        self.assertEqual(self.copy_type().status_code,              401)
        self.assertEqual(self.edit_type().status_code,              401)
        self.assertEqual(self.delete_type().status_code,            401)
        self.assertEqual(self.delete_type_confirmed().status_code,  401)
        #
        self.assertEqual(self.list_data().status_code,              200)
        self.assertEqual(self.new_data().status_code,               401)
        self.assertEqual(self.copy_data().status_code,              401)
        self.assertEqual(self.edit_data().status_code,              401)
        self.assertEqual(self.delete_data().status_code,            401)
        self.assertEqual(self.delete_data_confirmed().status_code,  401)
        return

    def test_list_all(self):
        u = entitydata_list_all_url("testcoll", list_id="Default_list_all")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        # Entities and bound fields
        # log.info(r.context['entities'])  #@@
        # rows = []
        # for i in range(len(r.context['entities'])):
        #     efs = r.context['entities'][i]['fields']
        #     rows.append((efs[0]['field_value'], efs[1]['field_value'], efs[2]['field_value']))
        # for row in rows:
        #     log.info("entity_id %s, type_id %s, label %s"%row)
        self.assertEqual(len(r.context['entities']), 8)
        entity_fields = (
            [ ('testtype',    '_type',    'RecordType testtype/testtype')
            # , ('user_admin',  '_user',    'Admin User')
            # , ('user_config', '_user',    'Admin User')
            # , ('user_create', '_user',    'Admin User')
            # , ('user_delete', '_user',    'Admin User')
            # , ('user_update', '_user',    'Admin User')
            # , ('user_view',   '_user',    'Admin User')
            , ('entity1',     'testtype', 'Entity testcoll/testtype/entity1')
            ])
        for eid in range(6):
            for fid in range(3):
                item_field = r.context['entities'][eid]['fields'][fid]
                self.assertEqual(item_field['field_value'],    entity_fields[eid][fid])
        return

# End.
