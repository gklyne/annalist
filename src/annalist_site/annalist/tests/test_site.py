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

from django.conf                import settings
from django.db                  import models
from django.http                import QueryDict
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from bs4                        import BeautifulSoup

from miscutils.MockHttpResources import MockHttpFileResources, MockHttpDictResources

from annalist.site      import Site, SiteView
from annalist.layout    import Layout

from tests              import TestBaseDir, dict_to_str, init_annalist_test_site

# Test assertion summary from http://docs.python.org/2/library/unittest.html#test-cases
#
# Method                    Checks that             New in
# assertEqual(a, b)         a == b   
# assertNotEqual(a, b)      a != b   
# assertTrue(x)             bool(x) is True  
# assertFalse(x)            bool(x) is False     
# assertIs(a, b)            a is b                  2.7
# assertIsNot(a, b)         a is not b              2.7
# assertIsNone(x)           x is None               2.7
# assertIsNotNone(x)        x is not None           2.7
# assertIn(a, b)            a in b                  2.7
# assertNotIn(a, b)         a not in b              2.7
# assertIsInstance(a, b)    isinstance(a, b)        2.7
# assertNotIsInstance(a, b) not isinstance(a, b)    2.7

# Initial collection data used for form display
init_collections = (
    { 'coll1':
        { 'title': 'Name collection coll1'
        , 'uri': '/annalist/coll1'
        }
    , 'coll2':
        { 'title': 'Label collection coll2'
        , 'uri': '/annalist/coll2'
        }
    , 'coll3':
        { 'title': 'Label collection coll3'
        , 'uri': '/annalist/coll3'
        }
    })

class SiteTest(TestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        self.coll1 = (
            { '@id': '../'
            , 'id': 'coll1'
            , 'title': 'Name collection coll1'
            , 'uri': 'http://example.com/testsite/coll1'
            , 'annal:id': 'coll1'
            , 'annal:type': 'annal:Collection'
            , 'rdfs:comment': 'Annalist collection metadata.'
            , 'rdfs:label': 'Name collection coll1'
            })        
        self.collnewmeta = (
            { 'rdfs:label': 'Collection new'
            , 'rdfs:comment': 'Annalist new collection metadata.'
            })        
        self.collnew = (
            { '@id': '../'
            , 'id': 'new'
            , 'title': 'Collection new'
            , 'uri': 'http://example.com/testsite/new'
            , 'annal:id': 'new'
            , 'annal:type': 'annal:Collection'
            , 'rdfs:comment': 'Annalist new collection metadata.'
            , 'rdfs:label': 'Collection new'
            })        
        return

    def tearDown(self):
        return

    @unittest.skip("Skip placeholder")
    def test_SiteTest(self):
        self.assertEqual(Site.__name__, "Site", "Check Site class name")
        return

    def test_site_data(self):
        sd = self.testsite.site_data()
        self.assertEquals(set(sd.keys()),set(('rdfs:label', 'rdfs:comment', 'collections', 'title')))
        self.assertEquals(sd["title"],        "Annalist data journal test site")
        self.assertEquals(sd["rdfs:label"],   "Annalist data journal test site")
        self.assertEquals(sd["rdfs:comment"], "Annalist site metadata.")
        self.assertEquals(sd["collections"].keys(),  ["coll1","coll2","coll3"])
        self.assertEquals(dict_to_str(sd["collections"]["coll1"]),  self.coll1)
        return

    def test_collections_dict(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.assertEquals(dict_to_str(colls["coll1"]),  self.coll1)
        return

    def test_add_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.testsite.add_collection("new", self.collnewmeta)
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3","new"])
        self.assertEquals(dict_to_str(colls["coll1"]), self.coll1)
        self.assertEquals(dict_to_str(colls["new"]),   self.collnew)
        return

    def test_remove_collection(self):
        colls = self.testsite.collections_dict()
        self.assertEquals(colls.keys(),["coll1","coll2","coll3"])
        self.testsite.remove_collection("coll2")
        collsb = self.testsite.collections_dict()
        self.assertEquals(collsb.keys(),["coll1","coll3"])
        self.assertEquals(dict_to_str(colls["coll1"]),  self.coll1)
        return


class SiteViewTest(TestCase):
    """
    Tests for Site views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        return

    def tearDown(self):
        return

    @unittest.skip("Skip placeholder")
    def test_SiteViewTest(self):
        self.assertEqual(SiteView.__name__, "SiteView", "Check SiteView class name")
        return

    def test_get(self):
        # @@TODO: use reference to self.client, per 
        # https://docs.djangoproject.com/en/dev/topics/testing/tools/#default-test-client
        c = Client()
        r = c.get("/annalist/site/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        return

    def test_get_home(self):
        c = Client()
        r = c.get("/annalist/")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r["location"], "http://testserver/annalist/site/")
        return

    def test_get_no_login(self):
        c = Client()
        r = c.get("/annalist/site/")
        self.assertFalse(r.context["auth_create"])
        self.assertFalse(r.context["auth_update"])
        self.assertFalse(r.context["auth_delete"])
        colls = r.context['collections']
        for id in init_collections:
            self.assertEqual(colls[id]["annal:id"], id)
            self.assertEqual(colls[id]["uri"],      init_collections[id]["uri"])
            self.assertEqual(colls[id]["title"],    init_collections[id]["title"])
        # Check returned HTML (checks template logic)
        # (Don't need to keep doing this as logic can be tested through context as above)
        # (See: http://stackoverflow.com/questions/2257958/)
        s = BeautifulSoup(r.content)
        self.assertEqual(s.html.title.string, "Annalist data journal test site")
        self.assertEqual(s.find(class_="menu-left").a.string,   "Home")
        self.assertEqual(s.find(class_="menu-left").a['href'],  "/annalist/site/")
        self.assertEqual(s.find(class_="menu-right").a.string,  "Login")
        self.assertEqual(s.find(class_="menu-right").a['href'], "/annalist/profile/")
        # print "*****"
        # #print s.table.tbody.prettify()
        # print s.table.tbody.find_all("tr")
        # print "*****"
        trows = s.table.tbody.find_all("tr")
        self.assertEqual(len(trows), 4)
        self.assertEqual(trows[1].td.a.string,  "coll1")
        self.assertEqual(trows[1].td.a['href'], "/annalist/coll1")
        self.assertEqual(trows[2].td.a.string,  "coll2")
        self.assertEqual(trows[2].td.a['href'], "/annalist/coll2")
        self.assertEqual(trows[3].td.a.string,  "coll3")
        self.assertEqual(trows[3].td.a['href'], "/annalist/coll3")
        return

    def test_get_with_login(self):
        c = Client()
        loggedin = c.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        r = c.get("/annalist/site/")
        # Preferred way to test main view logic
        self.assertTrue(r.context["auth_create"])
        self.assertTrue(r.context["auth_update"])
        self.assertTrue(r.context["auth_delete"])
        colls = r.context['collections']
        for id in init_collections:
            self.assertEqual(colls[id]["annal:id"], id)
            self.assertEqual(colls[id]["uri"],      init_collections[id]["uri"])
            self.assertEqual(colls[id]["title"],    init_collections[id]["title"])
        # Check returned HTML (checks template logic)
        # (Don't need to keep doing this as logic can be tested through context as above)
        # (See: http://stackoverflow.com/questions/2257958/)
        s = BeautifulSoup(r.content)
        # title and top menu
        self.assertEqual(s.html.title.string, "Annalist data journal test site")
        ml = s.find(class_="menu-left").find_all("a")
        self.assertEqual(ml[0].string,   "Home")
        self.assertEqual(ml[0]['href'],  "/annalist/site/")
        mr = s.find(class_="menu-right").find_all("a")
        self.assertEqual(mr[0].string,  "Profile")
        self.assertEqual(mr[0]['href'], "/annalist/profile/")
        self.assertEqual(mr[1].string,  "Logout")
        self.assertEqual(mr[1]['href'], "/annalist/logout/")
        # Displayed colllections and check-buttons
        trows = s.table.tbody.find_all("tr")
        self.assertEqual(len(trows), 6)
        tcols1 = trows[1].find_all("td")
        self.assertEqual(tcols1[0].a.string,       "coll1")
        self.assertEqual(tcols1[0].a['href'],      "/annalist/coll1")
        self.assertEqual(tcols1[2].input['type'],  "checkbox")
        self.assertEqual(tcols1[2].input['name'],  "select")
        self.assertEqual(tcols1[2].input['value'], "coll1")
        tcols2 = trows[2].find_all("td")
        self.assertEqual(tcols2[0].a.string,       "coll2")
        self.assertEqual(tcols2[0].a['href'],      "/annalist/coll2")
        self.assertEqual(tcols2[2].input['type'],  "checkbox")
        self.assertEqual(tcols2[2].input['name'],  "select")
        self.assertEqual(tcols2[2].input['value'], "coll2")
        tcols3 = trows[3].find_all("td")
        self.assertEqual(tcols3[0].a.string,       "coll3")
        self.assertEqual(tcols3[0].a['href'],      "/annalist/coll3")
        self.assertEqual(tcols3[2].input['type'],  "checkbox")
        self.assertEqual(tcols3[2].input['name'],  "select")
        self.assertEqual(tcols3[2].input['value'], "coll3")
        # Remove/new collection buttons
        btn_remove = trows[4].find_all("td")[2]
        self.assertEqual(btn_remove.input["type"],  "submit")
        self.assertEqual(btn_remove.input["name"],  "remove")
        field_id = trows[5].find_all("td")[0]
        self.assertEqual(field_id.input["type"],  "text")
        self.assertEqual(field_id.input["name"],  "new_id")
        field_id = trows[5].find_all("td")[1]
        self.assertEqual(field_id.input["type"],  "text")
        self.assertEqual(field_id.input["name"],  "new_label")
        btn_new = trows[5].find_all("td")[2]
        self.assertEqual(btn_new.input["type"],  "submit")
        self.assertEqual(btn_new.input["name"],  "new")
        return

    def test_post_add(self):
        c = Client()
        loggedin = c.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        form_data = QueryDict("").copy()
        form_data["new"]       = "New collection"
        form_data["new_id"]    = "testnew"
        form_data["new_label"] = "Label for new collection"
        form_data["select"]    = "coll1"
        form_data["select"]    = "coll3"
        r = c.post("/annalist/site/", form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],
            "http://testserver/annalist/site/"+
            "?info_head=Action%20completed"+
            "&info_message=Created%20new%20collection:%20'testnew'")
        # Check site now has new colllection
        r = c.get("/annalist/site/")
        new_collections = init_collections.copy()
        new_collections["testnew"] = (
            { 'title': 'Label for new collection'
            , 'uri':   '/annalist/testnew'
            })
        colls = r.context['collections']
        for id in new_collections:
            self.assertEqual(colls[id]["annal:id"], id)
            self.assertEqual(colls[id]["uri"],      new_collections[id]["uri"])
            self.assertEqual(colls[id]["title"],    new_collections[id]["title"])
        return

    def test_post_remove(self):
        self.assertTrue(False, "@@TODO test_post_remove")
        # INFO:annalist.site:site.post: <QueryDict: {u'new_label': [u''], u'csrfmiddlewaretoken': [u'y9NzIms0uYbY3auNDXaDWsEGUmol20WX'], u'new_id': [u''], u'remove': [u'Remove selected'], u'select': [u'testnew']}>
        # INFO:annalist.site:collections: [u'testnew']
        # INFO:annalist.confirmview:confirmview form data: {'suppress_user': True, 'action_params': '{"new_label": [""], "csrfmiddlewaretoken": ["y9NzIms0uYbY3auNDXaDWsEGUmol20WX"], "new_id": [""], "select": ["testnew"], "remove": ["Remove selected"]}', 'action_description': u'Remove collection(s): testnew', 'title': 'Annalist data journal test site', 'complete_action': '/annalist/site_action/', 'cancel_action': '/annalist/site/'}
        # [02/Feb/2014 16:16:32] "POST /annalist/site/ HTTP/1.1" 200 1822
        # INFO:annalist.site:site.post: <QueryDict: {u'new_label': [u''], u'csrfmiddlewaretoken': [u'y9NzIms0uYbY3auNDXaDWsEGUmol20WX'], u'new_id': [u''], u'select': [u'testnew'], u'remove': [u'Remove selected']}>
        # INFO:annalist.site:Complete remove [u'testnew']
        # [02/Feb/2014 16:16:37] "POST /annalist/confirm/ HTTP/1.1" 302 0
        # [02/Feb/2014 16:16:37] "GET /annalist/site/?info_head=Action%20completed&info_message=The%20following%20collections%20were%20removed:%20testnew HTTP/1.1" 200 2908
        return


class SiteActionView(TestCase):
    """
    Tests for Site action views (completion of confirmed actions
    requested from the site view)
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site("http://example.com/testsite", TestBaseDir)
        return

    def tearDown(self):
        return

    @unittest.skip("Skip TODO")
    def test_SiteActionViewTest(self):
        self.assertEqual(SiteActionView.__name__, "SiteActionView", "Check SiteActionView class name")
        return

    @unittest.skip("Skip TODO")
    def test_post_confirmed_remove(self):
        self.assertTrue(False, "@@TODO test_post_confirmed_remove")
        return


# End.
