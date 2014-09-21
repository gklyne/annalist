"""
Tests for AnnalistUser module and view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.core.urlresolvers           import resolve, reverse
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.util                      import valid_id

from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.annalistuser       import AnnalistUser
# from annalist.models.recordtype         import AnnalistUser
# from annalist.models.recordview         import RecordView
# from annalist.models.recordlist         import RecordList

from annalist.views.annalistuserdelete  import AnnalistUserDeleteConfirmedView

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site
from AnnalistTestCase                   import AnnalistTestCase
from entity_testutils                   import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_create_values
    )
# from entity_testtypedata                import (
#     recordtype_dir,
#     recordtype_coll_url, recordtype_site_url, recordtype_url, recordtype_edit_url,
#     recordtype_value_keys, recordtype_load_keys, 
#     recordtype_create_values, recordtype_values, recordtype_read_values,
#     recordtype_entity_view_context_data, 
#     recordtype_entity_view_form_data, recordtype_delete_confirm_form_data
#     )
# from entity_testentitydata              import (
#     entity_url, entitydata_edit_url, entitydata_list_type_url,
#     default_fields, default_label, default_comment, error_label,
#     layout_classes
#     )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def annalistuser_dir(coll_id="testcoll", user_id="testuser"):
    return collection_dir(coll_id) + layout.COLL_USER_PATH%{'id': user_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def annalistuser_site_url(site, user_id="testuser"):
    return site._entityurl + layout.SITE_USER_PATH%{'id': user_id} + "/"

def annalistuser_coll_url(site, coll_id="testcoll", user_id="testuser"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_USER_PATH%{'id': user_id} + "/"

def annalistuser_url(coll_id="testcoll", user_id="testuser"):
    """
    URI for record type description data; also view using default entity view
    """
    viewname = "AnnalistEntityAccessView"
    kwargs   = {'coll_id': coll_id, "type_id": "_user"}
    if valid_id(user_id):
        kwargs.update({'entity_id': user_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def annalistuser_edit_url(action=None, coll_id=None, user_id=None):
    """
    URI for record type description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistUserDeleteView'        if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_type", 'view_id': "User_view"})
    if user_id:
        if valid_id(user_id):
            kwargs.update({'entity_id': user_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- AnnalistUser data
#
#   -----------------------------------------------------------------------------

def annalistuser_value_keys():
    ks = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type', 'annal:url', 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:uri'
        , 'annal:user_permissions'
        ])
    return ks

def annalistuser_load_keys():
    return annalistuser_value_keys() | {'@id', '@type'}

def annalistuser_create_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        ):
    """
    Values used when creating a user record
    """
    d = (
        { 'annal:type':             "annal:User"
        , 'rdfs:label':             user_name
        , 'rdfs:comment':           "User %s: permissions for %s in collection %s"%(user_id, user_name, coll_id)
        , 'annal:uri':              user_uri
        , 'annal:user_permissions': user_permissions
        })
    return d

def annalistuser_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
        hosturi=TestHostUri):
    """
    Values filled in automatically when a user record is created
    """
    user_url = hosturi + annalistuser_url(coll_id, user_id)
    if not user_uri:
        user_uri = user_url
    d = annalistuser_create_values(coll_id, user_id, user_name, user_uri, user_permissions)
    d.update(
        { 'annal:id':       user_id
        , 'annal:type_id':  "_user"
        , 'annal:url':      user_url
        })
    return d

def annalistuser_read_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
        hosturi=TestHostUri):
    d = annalistuser_values(
            coll_id, user_id, user_name, user_uri, user_permissions,
            hosturi=hosturi
            )
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:User"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Recordtype delete confirmation form data
#
#   -----------------------------------------------------------------------------

def annalistuser_delete_confirm_form_data(user_id=None):
    return (
        { 'userlist':    user_id,
          'user_delete': 'Delete'
        })

#   -----------------------------------------------------------------------------
#
#   AnnalistUser tests
#
#   -----------------------------------------------------------------------------

class AnnalistUserTest(AnnalistTestCase):
    """
    Tests for AnnalistUser object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_AnnalistUserTest(self):
        self.assertEqual(AnnalistUser.__name__, "AnnalistUser", "Check AnnalistUser class name")
        return

    def test_annalistuser_init(self):
        usr = AnnalistUser(self.testcoll, "testuser", self.testsite)
        url = annalistuser_coll_url(self.testsite, coll_id="testcoll", user_id="testuser")
        self.assertEqual(usr._entitytype,   ANNAL.CURIE.User)
        self.assertEqual(usr._entityfile,   layout.USER_META_FILE)
        self.assertEqual(usr._entityref,    layout.META_USER_REF)
        self.assertEqual(usr._entityid,     "testuser")
        self.assertEqual(usr._entityurl,    url)
        self.assertEqual(usr._entitydir,    annalistuser_dir(user_id="testuser"))
        self.assertEqual(usr._values,       None)
        return

    def test_annalistuser1_data(self):
        usr = AnnalistUser(self.testcoll, "user1", self.testsite)
        self.assertEqual(usr.get_id(), "user1")
        self.assertEqual(usr.get_type_id(), "_user")
        self.assertIn("/c/testcoll/_annalist_collection/users/user1/", usr.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_user/user1/", usr.get_view_url())
        usr.set_values(annalistuser_create_values(user_id="user1"))
        td = usr.get_values()
        self.assertEqual(set(td.keys()), set(annalistuser_value_keys()))
        v = annalistuser_values(user_id="user1")
        self.assertDictionaryMatch(td, v)
        return

    def test_annalistuser2_data(self):
        usr = AnnalistUser(self.testcoll, "user2", self.testsite)
        self.assertEqual(usr.get_id(), "user2")
        self.assertEqual(usr.get_type_id(), "_user")
        self.assertIn("/c/testcoll/_annalist_collection/users/user2/", usr.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_user/user2/", usr.get_view_url())
        usr.set_values(annalistuser_create_values(user_id="user2"))
        ugv = usr.get_values()
        self.assertEqual(set(ugv.keys()), set(annalistuser_value_keys()))
        uev = annalistuser_values(user_id="user2")
        self.assertDictionaryMatch(ugv, uev)
        return

    def test_annalistuser_create_load(self):
        usr  = AnnalistUser.create(self.testcoll, "user1", annalistuser_create_values(user_id="user1"))
        uld = AnnalistUser.load(self.testcoll, "user1").get_values()
        ued  = annalistuser_read_values(user_id="user1")
        self.assertKeysMatch(uld, ued)
        self.assertDictionaryMatch(uld, ued)
        return

    def test_annalistuser_default_data(self):
        usr = AnnalistUser.load(self.testcoll, "_unknown_user", altparent=self.testsite)
        self.assertEqual(usr.get_id(), "_unknown_user")
        self.assertIn("/c/testcoll/_annalist_collection/users/_unknown_user", usr.get_url())
        self.assertEqual(usr.get_type_id(), "_user")
        uld = usr.get_values()
        self.assertEqual(set(uld.keys()), set(annalistuser_load_keys()))
        uev = annalistuser_read_values(user_id="_unknown_user")
        uev.update(
            { 'rdfs:label':             'Unknown user'
            , 'rdfs:comment':           'Permissions for unauthenticated user.'
            , 'annal:uri':              'annal:User/_unknown_user'
            , 'annal:user_permissions': ['VIEW']
            })
        self.assertDictionaryMatch(uld, uev)
        return

#   -----------------------------------------------------------------------------
#
#   AnnalistUserEditView tests
#
#   -----------------------------------------------------------------------------

class AnnalistUserEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user     = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client   = Client(HTTP_HOST=TestHost)
        loggedin      = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        self.continuation_url = TestHostUri + entitydata_list_type_url(coll_id="testcoll", type_id="_user")
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------



#   -----------------------------------------------------------------------------
#
#   ConfirmAnnalistUserDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmAnnalistUserDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_DeleteConfirmedViewTest(self):
        self.assertEqual(AnnalistUserDeleteConfirmedView.__name__, "AnnalistUserDeleteConfirmedView", "Check AnnalistUserDeleteConfirmedView class name")
        return

    @unittest.skip("@@TODO: Delete user not yet implemented")
    def test_post_confirmed_remove_user(self):
        t = AnnalistUser.create(self.testcoll, "deleteuser", annalistuser_create_values("deleteuser"))
        self.assertTrue(AnnalistUser.exists(self.testcoll, "deleteuser"))
        # Submit positive confirmation
        u = TestHostUri + annalistuser_edit_url("delete", "testcoll")
        f = annalistuser_delete_confirm_form_data("deleteuser")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_url("testcoll")+
            r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(AnnalistUser.exists(self.testcoll, "deletetype"))
        return

# End.
