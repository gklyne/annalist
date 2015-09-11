"""
Tests for site module
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
from django.core.urlresolvers       import resolve, reverse
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from bs4                            import BeautifulSoup

from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.models.site           import Site
from annalist.models.site           import Collection
from annalist.models.annalistuser   import AnnalistUser

from annalist.views.site            import SiteView, SiteActionView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import dict_to_str, init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    site_view_url, collection_view_url, collection_edit_url, 
    collection_value_keys, collection_create_values, collection_values,
    collection_new_form_data, collection_remove_form_data,
    site_title,
    create_user_permissions, create_test_user
    )
from entity_testuserdata            import (
    annalistuser_create_values, annalistuser_values, annalistuser_read_values
    )
from entity_testtypedata            import (
    recordtype_url, recordtype_edit_url
    )

# Keys in side metadata entity
site_data_keys = {'@id', 'annal:url', 'rdfs:label', 'rdfs:comment', 'collections', 'title'}

# Initial collection data used for form display
init_collections = (
    { 'coll1': collection_values("coll1", hosturi=TestHostUri)
    , 'coll2': collection_values("coll2", hosturi=TestHostUri)
    , 'coll3': collection_values("coll3", hosturi=TestHostUri)
    })

class SiteTest(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.coll1 = collection_values(coll_id="coll1")
        self.collnewmeta = collection_create_values(coll_id="new")
        self.collnew = collection_values(coll_id="new")
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_SiteTest(self):
        self.assertEqual(Site.__name__, "Site", "Check Site class name")
        return

    def test_site_init(self):
        s = Site(TestBaseUri, TestBaseDir)
        self.assertEqual(s._entitytype,     ANNAL.CURIE.Site)
        self.assertEqual(s._entityfile,     layout.SITE_META_FILE)
        self.assertEqual(s._entityref,      layout.META_SITE_REF)
        self.assertEqual(s._entityid,       None)
        self.assertEqual(s._entityurl,      TestBaseUri+"/")
        self.assertEqual(s._entitydir,      TestBaseDir+"/")
        self.assertEqual(s._values,         None)
        return

    def test_site_data(self):
        sd = self.testsite.site_data()
        self.assertEquals(set(sd.keys()),site_data_keys)
        self.assertEquals(sd["title"],        site_title())
        self.assertEquals(sd["rdfs:label"],   site_title())
        self.assertEquals(sd["rdfs:comment"], "Annalist site metadata.")
        self.assertEquals(sd["collections"].keys(), ["coll1","coll2","coll3","testcoll"])
        self.assertDictionaryMatch(sd["collections"]["coll1"], self.coll1)
        return

    # User permissions

    def test_get_user_permissions(self):
        s = self.testsite
        # Create local permissions
        usr = AnnalistUser.create(s, "user1", annalistuser_create_values(user_id="user1"), use_altpath=True)
        # Test access to permissions defined in site
        ugp = s.get_user_permissions("user1", "mailto:testuser@example.org")
        self.assertEqual(ugp[ANNAL.CURIE.id],                 "user1")
        self.assertEqual(ugp[ANNAL.CURIE.type_id],            "_user")
        self.assertEqual(ugp[RDFS.CURIE.label],               "Test User")
        self.assertEqual(ugp[RDFS.CURIE.comment],             "User user1: permissions for Test User in collection testcoll")
        self.assertEqual(ugp[ANNAL.CURIE.user_uri],           "mailto:testuser@example.org")
        self.assertEqual(ugp[ANNAL.CURIE.user_permissions],   ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"])
        return

    def test_get_local_user_not_defined(self):
        s = self.testsite
        ugp = s.get_user_permissions("user1", "mailto:testuser@example.org")
        self.assertIsNone(ugp)
        return

    def test_get_user_uri_mismatch(self):
        s = self.testsite
        # Create local permissions
        usr = AnnalistUser.create(s, "user1", annalistuser_create_values(user_id="user1"))
        # Test access to permissions defined locally in collection
        ugp = s.get_user_permissions("user1", "mailto:anotheruser@example.org")
        self.assertIsNone(ugp)
        return

    def test_get_default_user_permissions(self):
        s = self.testsite
        # Test access to default permissions defined in site
        ugp = s.get_user_permissions("_default_user_perms", "annal:User/_default_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.id],                 "_default_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.type_id],            "_user")
        self.assertEqual(ugp[RDFS.CURIE.label],               "Default permissions")
        self.assertEqual(ugp[RDFS.CURIE.comment],             "Default permissions for authenticated user.")
        self.assertEqual(ugp[ANNAL.CURIE.user_uri],           "annal:User/_default_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.user_permissions],   ["VIEW"])
        return

    # Collections

    def test_collections_dict(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3","testcoll"])
        self.assertDictionaryMatch(colls["coll1"], self.coll1)
        return

    def test_add_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3","testcoll"])
        self.testsite.add_collection("new", self.collnewmeta)
        colls = self.testsite.collections_dict()
        self.assertEquals(set(colls.keys()),set(["coll1","coll2","coll3","testcoll","new"]))
        self.assertDictionaryMatch(colls["coll1"], self.coll1)
        self.assertDictionaryMatch(colls["new"],   self.collnew)
        return

    def test_remove_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3","testcoll"])
        self.testsite.remove_collection("coll2")
        collsb = self.testsite.collections_dict()
        self.assertEquals(collsb.keys(),["coll1","coll3","testcoll"])
        self.assertDictionaryMatch(colls["coll1"], self.coll1)
        return

#   -----------------------------------------------------------------------------
#
#   SiteView tests
#
#   -----------------------------------------------------------------------------

class SiteViewTest(AnnalistTestCase):
    """
    Tests for Site views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.uri        = reverse("AnnalistSiteView")
        self.homeuri    = reverse("AnnalistHomeView")
        self.profileuri = reverse("AnnalistProfileView")
        # Login and permissions
        create_test_user(None, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        create_user_permissions(
            self.testsite, "testuser",
            user_permissions=
              [ "VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"
              , "CREATE_COLLECTION", "DELETE_COLLECTION"
              ],
            use_altpath=True
            )
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_SiteViewTest(self):
        self.assertEqual(SiteView.__name__, "SiteView", "Check SiteView class name")
        return

    def test_get(self):
        # @@TODO: use reference to self.client, per 
        # https://docs.djangoproject.com/en/dev/topics/testing/tools/#default-test-client
        r = self.client.get(self.uri)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        return

    def test_get_error(self):
        r = self.client.get(self.uri+"?error_head=Error&error_message=Error%20presented")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertEqual(r.content, "???")
        self.assertContains(r, """<h3>Error</h3>""", html=True)
        self.assertContains(r, """<p>Error presented</p>""", html=True)
        return

    def test_get_info(self):
        r = self.client.get(self.uri+"?info_head=Information&info_message=Information%20presented")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, """<h3>Information</h3>""", html=True)
        self.assertContains(r, """<p>Information presented</p>""", html=True)
        return

    def test_get_home(self):
        r = self.client.get(self.homeuri)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r["location"], TestHostUri+self.uri)
        return

    def test_get_no_login(self):
        self.client.logout()
        r = self.client.get(self.uri)
        self.assertFalse(r.context["auth_create"])
        self.assertFalse(r.context["auth_update"])
        self.assertFalse(r.context["auth_delete"])
        colls = r.context['collections']
        self.assertEqual(len(colls), 4)
        for id in init_collections:
            self.assertEqual(colls[id]["annal:id"],   id)
            self.assertEqual(colls[id]["annal:url"],  init_collections[id]["annal:url"])
            self.assertEqual(colls[id]["rdfs:label"], init_collections[id]["rdfs:label"])
        # Check returned HTML (checks template logic)
        # (Don't need to keep doing this as logic can be tested through context as above)
        # (See: http://stackoverflow.com/questions/2257958/)
        s = BeautifulSoup(r.content, "html.parser")
        self.assertEqual(s.html.title.string, site_title())
        homelink = s.find(class_="title-area").find(class_="name").h1.a
        self.assertEqual(homelink.string,   "Home")
        self.assertEqual(homelink['href'],  self.uri)
        menuitems = s.find(class_="top-bar-section").find(class_="right").find_all("li")
        self.assertEqual(menuitems[0].a.string,  "Login")
        self.assertEqual(menuitems[0].a['href'], self.profileuri)
        # Check displayed collections
        trows = s.form.find_all("div", class_="tbody")
        self.assertEqual(len(trows), 4)
        self.assertEqual(trows[0].div.div('div')[1].a.string,  "coll1")
        self.assertEqual(trows[0].div.div('div')[1].a['href'], collection_view_url("coll1"))
        self.assertEqual(trows[1].div.div('div')[1].a.string,  "coll2")
        self.assertEqual(trows[1].div.div('div')[1].a['href'], collection_view_url("coll2"))
        self.assertEqual(trows[2].div.div('div')[1].a.string,  "coll3")
        self.assertEqual(trows[2].div.div('div')[1].a['href'], collection_view_url("coll3"))
        return

    def test_get_with_login(self):
        r = self.client.get(self.uri)
        # Preferred way to test main view logic
        self.assertTrue(r.context["auth_create"])
        self.assertTrue(r.context["auth_update"])
        self.assertTrue(r.context["auth_delete"])
        self.assertTrue(r.context["auth_create_coll"])
        self.assertTrue(r.context["auth_delete_coll"])
        colls = r.context['collections']
        self.assertEqual(len(colls), 4)
        for id in init_collections:
            # First two here added in models.site.site_data()
            self.assertEqual(colls[id]["id"],         id)
            self.assertEqual(colls[id]["url"],        init_collections[id]["annal:url"])
            self.assertEqual(colls[id]["annal:id"],   id)
            self.assertEqual(colls[id]["annal:url"],  init_collections[id]["annal:url"])
            self.assertEqual(colls[id]["rdfs:label"], init_collections[id]["rdfs:label"])
        # Check returned HTML (checks template logic)
        # (Don't need to keep doing this as logic can be tested through context as above)
        # (See: http://stackoverflow.com/questions/2257958/)
        s = BeautifulSoup(r.content, "html.parser")
        # title and top menu
        self.assertEqual(s.html.title.string, site_title())
        homelink = s.find(class_="title-area").find(class_="name").h1.a
        self.assertEqual(homelink.string,   "Home")
        self.assertEqual(homelink['href'],  self.uri)
        menuitems = s.find(class_="top-bar-section").find(class_="right").find_all("li")
        self.assertEqual(menuitems[0].a.string,     "User testuser")
        self.assertEqual(menuitems[0].a['href'],    TestBasePath+"/profile/")
        self.assertEqual(menuitems[1].a.string,     "Logout")
        self.assertEqual(menuitems[1].a['href'],    TestBasePath+"/logout/")
        # Displayed colllections and check-buttons
        # trows = s.form.find_all("div", class_="tbody")
        trows = s.select("form > div > div > div")
        self.assertEqual(len(trows), 8)
        site_data = (
            [ (1, "checkbox", "select", "coll1")
            , (2, "checkbox", "select", "coll2")
            , (3, "checkbox", "select", "coll3")
            , (4, "checkbox", "select", "testcoll")
            ])
        for i, itype, iname, ivalue in site_data:
            # tcols = trows[i].find_all("div", class_="view-value")
            tcols = trows[i].select("div > div > div")
            self.assertEqual(tcols[0].input['type'],   itype)
            self.assertEqual(tcols[0].input['name'],   iname)
            self.assertEqual(tcols[0].input['value'],  ivalue)
            self.assertEqual(tcols[1].a.string,        ivalue)
            self.assertEqual(tcols[1].a['href'],       collection_view_url(ivalue))
        # button to remove selected
        btn_remove = trows[5].select("div > input")[0]
        self.assertEqual(btn_remove["type"],  "submit")
        self.assertEqual(btn_remove["name"],  "remove")
        # Input fields for new collection
        add_fields = trows[6].select("div > div > div")
        field_id    = add_fields[1].input
        field_label = add_fields[2].input
        self.assertEqual(field_id["type"],    "text")
        self.assertEqual(field_id["name"],    "new_id")
        self.assertEqual(field_label["type"], "text")
        self.assertEqual(field_label["name"], "new_label")
        # Button for new collection
        btn_new = trows[7].select("div > input")[0]
        self.assertEqual(btn_new["type"],     "submit")
        self.assertEqual(btn_new["name"],     "new")

        return

    def test_post_add(self):
        form_data = collection_new_form_data("testnew")
        r = self.client.post(self.uri, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],
            TestBaseUri+"/site/"
            "?info_head=Action%20completed"+
            "&info_message=Created%20new%20collection:%20'testnew'")
        # Check site now has new colllection
        r = self.client.get(self.uri)
        new_collections = init_collections.copy()
        new_collections["testnew"] = collection_values("testnew", hosturi=TestHostUri)
        colls = r.context['collections']
        for id in new_collections:
            p = "[%s]"%id
            # First two here added in model.site.site_data for view template
            self.assertEqualPrefix(colls[id]["id"],         id,                                p)
            self.assertEqualPrefix(colls[id]["url"],        new_collections[id]["annal:url"],  p)
            self.assertEqualPrefix(colls[id]["annal:id"],   id,                                p)
            self.assertEqualPrefix(colls[id]["annal:url"],  new_collections[id]["annal:url"],  p)
            self.assertEqualPrefix(colls[id]["rdfs:label"], new_collections[id]["rdfs:label"], p)
        # Check new collection has admin permissions for creator
        new_coll = Collection(self.testsite, "testnew")
        testuser_perms = new_coll.get_user_permissions("testuser", "mailto:testuser@%s"%TestHost)
        expect_perms   = ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        expect_descr   = "User testuser: permissions for Test User in collection testnew"
        self.assertEqual(testuser_perms[ANNAL.CURIE.id],                "testuser")
        self.assertEqual(testuser_perms[RDFS.CURIE.label],              "Test User")
        self.assertEqual(testuser_perms[RDFS.CURIE.comment],            expect_descr)
        self.assertEqual(testuser_perms[ANNAL.CURIE.user_uri],          "mailto:testuser@%s"%TestHost)
        self.assertEqual(testuser_perms[ANNAL.CURIE.user_permissions],  expect_perms)
        return

    def test_post_remove(self):
        form_data = collection_remove_form_data(["coll1", "coll3"])
        r = self.client.post(self.uri, form_data)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertTemplateUsed(r, "annalist_confirm.html")
        # Returns confirmation form: check
        self.assertContains(r, '''<form method="POST" action="'''+TestBasePath+'''/confirm/">''', status_code=200)
        self.assertContains(r, '''<input type="submit" name="confirm" value="Confirm"/>''', html=True)
        self.assertContains(r, '''<input type="submit" name="cancel" value="Cancel"/>''', html=True)
        self.assertContains(r, '''<input type="hidden" name="confirmed_action" value="'''+reverse("AnnalistSiteActionView")+'''"/>''', html=True)
        self.assertContains(r, '''<input type="hidden" name="action_params"   value="{&quot;new_label&quot;: [&quot;&quot;], &quot;new_id&quot;: [&quot;&quot;], &quot;select&quot;: [&quot;coll1&quot;, &quot;coll3&quot;], &quot;remove&quot;: [&quot;Remove selected&quot;]}"/>''', html=True)
        self.assertContains(r, '''<input type="hidden" name="cancel_action"   value="'''+reverse("AnnalistSiteView")+'''"/>''', html=True)
        return

#   -----------------------------------------------------------------------------
#
#   SiteActionView tests
#
#   -----------------------------------------------------------------------------

class SiteActionViewTests(AnnalistTestCase):
    """
    Tests for Site action views (completion of confirmed actions
    requested from the site view)
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        # self.user.save()
        # self.client = Client(HTTP_HOST=TestHost)
        # Login and permissions
        create_test_user(None, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        create_user_permissions(
            self.testsite, "testuser",
            user_permissions=
              [ "VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"
              , "CREATE_COLLECTION", "DELETE_COLLECTION"
              ],
            use_altpath=True
            )
        return

    def tearDown(self):
        return

    def _conf_data(self, action="confirm"):
        action_values = (
            { 'confirm': "Confirm"
            , 'cancel':  "Cancel"
            })
        return (
            { action:             action_values[action]
            , "confirmed_action": reverse("AnnalistSiteActionView")
            , "action_params":    """{"new_label": [""], "new_id": [""], "select": ["coll1", "coll3"], "remove": ["Remove selected"]}"""
            , "cancel_action":    reverse("AnnalistSiteView")
            })

    def test_SiteActionViewTest(self):
        self.assertEqual(SiteActionView.__name__, "SiteActionView", "Check SiteActionView class name")
        return

    def test_post_confirmed_remove(self):
        # Submit positive confirmation
        u = reverse("AnnalistConfirmView")
        r = self.client.post(u, self._conf_data(action="confirm"))
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],     "^"+TestHostUri+reverse("AnnalistSiteView")+"\\?info_head=.*&info_message=.*coll1,.*coll3.*$")
        # Confirm collections deleted
        r = self.client.get(TestBasePath+"/site/")
        colls = r.context['collections']
        self.assertEqual(len(colls), 2)
        id = "coll2"
        self.assertEqual(colls[id]["annal:id"],   id)
        self.assertEqual(colls[id]["annal:url"],  init_collections[id]["annal:url"])
        self.assertEqual(colls[id]["rdfs:label"], init_collections[id]["rdfs:label"])
        return
 
    def test_post_cancelled_remove(self):
        u = reverse("AnnalistConfirmView")
        r = self.client.post(u, self._conf_data(action="cancel"))
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertEqual(r['location'],     TestBaseUri+"/site/")
        # Confirm no collections deleted
        r = self.client.get(TestBasePath+"/site/")
        colls = r.context['collections']
        self.assertEqual(len(colls), 4)
        for id in init_collections:
            self.assertEqual(colls[id]["annal:id"],   id)
            self.assertEqual(colls[id]["annal:url"],  init_collections[id]["annal:url"])
            self.assertEqual(colls[id]["rdfs:label"], init_collections[id]["rdfs:label"])
        return

# End.
