"""
Tests for AnnalistUser module and view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest
import re

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings
from django.db                              import models
from django.http                            import QueryDict
from django.core.urlresolvers               import resolve, reverse
from django.contrib.auth.models             import User
from django.test                            import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                     import Client
from django.template                        import Template, Context

from utils.SuppressLoggingContext           import SuppressLogging

from annalist.identifiers                   import RDF, RDFS, ANNAL
from annalist                               import layout
from annalist.util                          import valid_id

from annalist.models.site                   import Site
from annalist.models.sitedata               import SiteData
from annalist.models.collection             import Collection
from annalist.models.annalistuser           import AnnalistUser

from annalist.views.annalistuserdelete      import AnnalistUserDeleteConfirmedView
from annalist.views.fields.render_tokenset  import get_field_tokenset_renderer

from AnnalistTestCase                       import AnnalistTestCase
from tests                                  import init_annalist_test_site, resetSitedata
from tests                                  import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils                       import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_user_permissions,
    create_test_user
    )
from entity_testuserdata                    import (
    annalistuser_dir,
    annalistuser_site_url, annalistuser_coll_url, annalistuser_url, annalistuser_edit_url,
    annalistuser_value_keys, annalistuser_load_keys,
    annalistuser_create_values, annalistuser_values, annalistuser_read_values,
    annalistuser_view_form_data,
    annalistuser_delete_confirm_form_data
    )
from entity_testentitydata                  import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )

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
        resetSitedata()
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
        usr = AnnalistUser.create(self.testcoll, "user1", annalistuser_create_values(user_id="user1"))
        uld = AnnalistUser.load(self.testcoll, "user1").get_values()
        ued = annalistuser_read_values(user_id="user1")
        self.assertKeysMatch(uld, ued)
        self.assertDictionaryMatch(uld, ued)
        return

    def test_annalistuser_default_data(self):
        usr = AnnalistUser.load(self.testcoll, "_unknown_user_perms", altparent=self.testsite)
        self.assertEqual(usr.get_id(), "_unknown_user_perms")
        self.assertIn("/c/testcoll/_annalist_collection/users/_unknown_user_perms", usr.get_url())
        self.assertEqual(usr.get_type_id(), "_user")
        uld = usr.get_values()
        self.assertEqual(set(uld.keys()), set(annalistuser_load_keys()))
        uev = annalistuser_read_values(user_id="_unknown_user_perms")
        uev.update(
            { 'rdfs:label':             'Unknown user'
            , 'rdfs:comment':           'Permissions for unauthenticated user.'
            , 'annal:user_uri':         'annal:User/_unknown_user_perms'
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
    Tests for record user edit view

    This view is generated entirely by generic view code, so opnly the form rendering test is included
    here to cross-check the form definmition.  Other logic is already tested by the generic form
    handling tests.
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # For checking Location: header values...
        self.continuation_url = TestHostUri + entitydata_list_type_url(coll_id="testcoll", type_id="_user")
        # Login and permissions
        create_test_user(
            self.testcoll, "testuser", "testpassword",
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _check_annalist_user_values(self, user_id, user_permissions):
        "Helper function checks content of annalist user entry with supplied user_id"
        self.assertTrue(AnnalistUser.exists(self.testcoll, user_id))
        t = AnnalistUser.load(self.testcoll, user_id)
        self.assertEqual(t.get_id(), user_id)
        self.assertEqual(t.get_view_url_path(), annalistuser_url("testcoll", user_id))
        v = annalistuser_values(
            coll_id="testcoll", user_id=user_id,
            user_name="User %s"%user_id,
            user_uri="mailto:%s@example.org"%user_id, 
            user_permissions=user_permissions
            )
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_object_render(self):
        # Test new Django 1.7 object-as-template include capability, 
        # per https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
        class RenderObject(object):
            def __init__(self):
                return
            def render(self, context):
                return context['render_value']
            def __str__(self):
                return "RenderObject"
        template = Template("{{render_object}}: {% include render_object %}")
        context  = Context({ 'render_object': RenderObject(), 'render_value': "Hello world!" })
        result   = template.render(context)
        # log.info(result)
        self.assertEqual(result, "RenderObject: Hello world!")
        return

    def test_tokenlist_reendering(self):
        field_placement = (
            { 'field': "small-12 columns"
            , 'label': "small-12 medium-2 columns"
            , 'value': "small-12 medium-10 columns"
            })
        field = (
            { 'field_placement':    field_placement
            , 'field_label':        "Permissions"
            , 'field_placeholder':  "(user permissions)"
            , 'field_name':         "User_permissions"
            , 'field_edit_value':   ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            })
        context  = Context({'field': field})
        rendered = get_field_tokenset_renderer().label_edit().render(context)
        rendered = re.sub(r'\s+', " ", rendered)
        self.assertIn('''<div class="small-12 columns">''',                             rendered)
        self.assertIn('''<div class="row view-value-row">''',                           rendered)
        self.assertIn(
            '''<div class="view-label small-12 medium-2 columns"> '''+
              '''<span>Permissions</span> '''+
            '''</div>''',
            rendered
            )
        self.assertIn('''<div class="view-value small-12 medium-10 columns">''',        rendered)
        self.assertIn('''<input type="text" size="64" name="User_permissions" ''',      rendered)
        self.assertIn(       '''placeholder="(user permissions)"''',                    rendered)
        self.assertIn(       '''value="VIEW CREATE UPDATE DELETE CONFIG ADMIN"/>''',    rendered)
        return

    def test_included_tokenlist_rendering(self):
        field_placement = (
            { 'field': "small-12 columns"
            , 'label': "small-12 medium-2 columns"
            , 'value': "small-12 medium-10 columns"
            })
        field = (
            { 'field_placement':        field_placement
            , 'field_label':            "Permissions"
            , 'field_placeholder':      "(user permissions)"
            , 'field_name':             "User_permissions"
            , 'field_edit_value':       ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            , 'field_render_object':    get_field_tokenset_renderer().label_edit()
            })
        template = Template("{% include field.field_render_object %}")
        context  = Context({ 'render_object': get_field_tokenset_renderer().label_edit(), 'field': field})
        rendered = template.render(context)
        rendered = re.sub(r'\s+', " ", rendered)
        self.assertIn('''<div class="small-12 columns">''',                             rendered)
        self.assertIn('''<div class="row view-value-row">''',                           rendered)
        self.assertIn(
            '''<div class="view-label small-12 medium-2 columns"> '''+
              '''<span>Permissions</span> '''+
            '''</div>''',
            rendered
            )
        self.assertIn('''<div class="view-value small-12 medium-10 columns">''',        rendered)
        self.assertIn('''<input type="text" size="64" name="User_permissions" ''',      rendered)
        self.assertIn(       '''placeholder="(user permissions)"''',                    rendered)
        self.assertIn(       '''value="VIEW CREATE UPDATE DELETE CONFIG ADMIN"/>''',    rendered)
        return

    def test_get_new_user_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "_user", view_id="User_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        self.assertContains(r, "<h3>'_user' data in collection 'testcoll'</h3>")
        field_vals = default_fields(coll_id="testcoll", type_id="_user", entity_id="00000001")
        formrow1 = """
            <div class="small-12 medium-6 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>User Id</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="entity_id" 
                                   placeholder="(user id)" 
                                   value="00000001" />
                    </div>
                </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>User name</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="User_name" 
                               placeholder="(user name)"
                               value="" />
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Description</span>
                    </div>
                    <div class="%(input_classes)s">
                        <textarea cols="64" rows="6" name="User_description" 
                                  class="small-rows-4 medium-rows-8"
                                  placeholder="(user description)"
                                  >
                        </textarea>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>URI</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="User_uri" 
                               placeholder="(User URI - e.g. mailto:local-name@example.com)"
                               value=""/>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow5 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Permissions</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="User_permissions" 
                               placeholder="(user permissions; e.g. &#39;VIEW CREATE UPDATE DELETE&#39;)"
                               value=""/>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow6a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow6b = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_left_classes)s">
                  <input type="submit" name="save"      value="Save" />
                  <input type="submit" name="view"      value="View" />
                  <input type="submit" name="cancel"    value="Cancel" />
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        # log.info(r.content)
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5,  html=True)
        self.assertContains(r, formrow6a, html=True)
        self.assertContains(r, formrow6b, html=True)
        return

    def test_user_permissions_form_rendering(self):
        # Test rendering of permissions from list in entity
        u = entitydata_edit_url("edit", "testcoll", "_user", "testuser", view_id="User_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(coll_id="testcoll", type_id="_user", entity_id="testuser")
        formrow5 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Permissions</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="User_permissions" 
                               placeholder="(user permissions; e.g. &#39;VIEW CREATE UPDATE DELETE&#39;)"
                               value="VIEW CREATE UPDATE DELETE CONFIG ADMIN"/>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)
        self.assertContains(r, formrow5, html=True)
        return

    def test_bad_user_permissions_form_rendering(self):
        # Test handling of permissions not stored in entity as a list of values
        create_user_permissions(self.testcoll, 
            "baduserperms",
            user_permissions="VIEW CREATE UPDATE DELETE"
            )
        u = entitydata_edit_url("edit", "testcoll", "_user", "baduserperms", view_id="User_view")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(coll_id="testcoll", type_id="_user", entity_id="baduserperms")
        formrow5 = """
            <div class="small-12 columns">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Permissions</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="User_permissions" 
                               placeholder="(user permissions; e.g. &#39;VIEW CREATE UPDATE DELETE&#39;)"
                               value="VIEW CREATE UPDATE DELETE"/>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)
        self.assertContains(r, formrow5, html=True)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- copy user --------

    def test_post_copy_user(self):
        # The main purpose of this test is to check that user permissions are saved properly
        self.assertFalse(AnnalistUser.exists(self.testcoll, "copyuser"))
        f = annalistuser_view_form_data(
            action="copy", orig_id="_default_user_perms",
            user_id="copyuser",
            user_name="User copyuser",
            user_uri="mailto:copyuser@example.org",
            user_permissions="VIEW CREATE UPDATE DELETE"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "_user", entity_id="_default_user_perms", view_id="User_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self.assertTrue(AnnalistUser.exists(self.testcoll, "copyuser"))
        self._check_annalist_user_values("copyuser", ["VIEW", "CREATE", "UPDATE", "DELETE"])
        return

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
        resetSitedata()
        return

    def test_DeleteConfirmedViewTest(self):
        self.assertEqual(AnnalistUserDeleteConfirmedView.__name__, "AnnalistUserDeleteConfirmedView", "Check AnnalistUserDeleteConfirmedView class name")
        return

    # test disabled - this functionality is handled by generic entity delete, and tested accordingly
    #                 (there is no special-case logic used, e.g. for the configure page.)
    # @unittest.skip("@@TODO: Delete user not yet implemented")
    def no_test_post_confirmed_remove_user(self):
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
