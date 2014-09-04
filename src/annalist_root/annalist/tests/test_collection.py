"""
Tests for collection module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import json
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.db                  import models
from django.http                import QueryDict
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist.identifiers       import ANNAL
from annalist                   import layout
from annalist.models.site       import Site
from annalist.models.collection import Collection
from annalist.models.recordtype import RecordType

from annalist.views.collection  import CollectionEditView

from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                      import dict_to_str, init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase
from entity_testutils           import (
    site_dir, collection_dir,
    site_view_url, 
    collection_view_url, 
    collection_edit_url, 
    continuation_url_param,
    collection_value_keys, collection_create_values, collection_values,
    site_title
    )
from entity_testtypedata            import (
    recordtype_edit_url,
    recordtype_create_values, recordtype_read_values
    )
from entity_testviewdata            import (
    recordview_create_values, recordview_read_values,
    )
from entity_testlistdata            import (
    recordlist_create_values, recordlist_read_values,
    )
from entity_testentitydata          import (
    entitydata_list_all_url,
    get_site_types, get_site_views, get_site_lists
    )

#   -----------------------------------------------------------------------------
#
#   Collection object tests
#
#   -----------------------------------------------------------------------------

site_types = get_site_types()
site_views = get_site_views()
site_lists = get_site_lists()

class CollectionTest(AnnalistTestCase):
    """
    Tests for Collection object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite     = Site(TestBaseUri, TestBaseDir)
        self.testcoll     = Collection(self.testsite, "testcoll")
        self.coll1        = collection_values("coll1")
        self.testcoll_add = collection_create_values("testcoll")
        self.type1_add    = recordtype_create_values("testcoll", "type1")
        self.type1        = recordtype_read_values("testcoll", "type1")
        self.type2_add    = recordtype_create_values("testcoll", "type2")
        self.type2        = recordtype_read_values("testcoll", "type2")
        self.view1_add    = recordview_create_values("testcoll", "view1")
        self.view1        = recordview_read_values("testcoll", "view1")
        self.view2_add    = recordview_create_values("testcoll", "view2")
        self.view2        = recordview_read_values("testcoll", "view2")
        self.list1_add    = recordlist_create_values("testcoll", "list1")
        self.list1        = recordlist_read_values("testcoll", "list1")
        self.list2_add    = recordlist_create_values("testcoll", "list2")
        self.list2        = recordlist_read_values("testcoll", "list2")
        return

    def tearDown(self):
        return

    def test_CollectionTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_collection_init(self):
        s = Site(TestBaseUri, TestBaseDir)
        c = Collection(s, "testcoll")
        self.assertEqual(c._entitytype,     ANNAL.CURIE.Collection)
        self.assertEqual(c._entityfile,     layout.COLL_META_FILE)
        self.assertEqual(c._entityref,      layout.META_COLL_REF)
        self.assertEqual(c._entityid,       "testcoll")
        self.assertEqual(c._entityurl,      TestHostUri + collection_view_url(coll_id="testcoll"))
        self.assertEqual(c._entitydir,      collection_dir(coll_id="testcoll"))
        self.assertEqual(c._values,         None)
        return

    def test_collection_data(self):
        c = self.testcoll
        c.set_values(self.testcoll_add)
        cd = c.get_values()
        self.assertDictionaryMatch(cd, self.testcoll_add)
        return

    # Record types

    def test_add_type(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        typenames = { t.get_id() for t in self.testcoll.types() }
        self.assertEqual(typenames, {"testtype"}|site_types)
        t1 = self.testcoll.add_type("type1", self.type1_add)
        t2 = self.testcoll.add_type("type2", self.type2_add)
        typenames = { t.get_id() for t in self.testcoll.types() }
        self.assertEqual(typenames, {"type1", "type2", "testtype"}|site_types)
        return

    def test_get_type(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_type("type1", self.type1_add)
        t2 = self.testcoll.add_type("type2", self.type2_add)
        self.assertDictionaryMatch(self.testcoll.get_type("type1").get_values(), self.type1)
        self.assertDictionaryMatch(self.testcoll.get_type("type2").get_values(), self.type2)
        return

    def test_remove_type(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_type("type1", self.type1_add)
        t2 = self.testcoll.add_type("type2", self.type2_add)
        typenames = { t.get_id() for t in self.testcoll.types() }
        self.assertEqual(typenames, {"type1", "type2", "testtype"}|site_types)
        self.testcoll.remove_type("type1")
        typenames =  { t.get_id() for t in self.testcoll.types() }
        self.assertEqual(typenames, {"type2", "testtype"}|site_types)
        typenames =  { t.get_id() for t in self.testcoll.types(include_alt=False) }
        self.assertEqual(typenames, {"type2", "testtype"})
        return

    def test_exists_type(self):
        # Some type existence tests takling accounbt of site data default type
        self.assertTrue(RecordType.exists(self.testcoll, "testtype"))
        self.assertFalse(RecordType.exists(self.testcoll, "notype"))
        self.assertFalse(RecordType.exists(self.testcoll, "Default_type"))
        self.assertTrue(RecordType.exists(self.testcoll, "Default_type", self.testsite))
        return

    # Record views

    def test_add_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        viewnames = { t.get_id() for t in self.testcoll.views() }
        self.assertEqual(viewnames, site_views)
        t1 = self.testcoll.add_view("view1", self.view1_add)
        t2 = self.testcoll.add_view("view2", self.view2_add)
        viewnames = { t.get_id() for t in self.testcoll.views() }
        self.assertEqual(viewnames, {"view1", "view2"}|site_views)
        return

    def test_get_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_view("view1", self.view1_add)
        t2 = self.testcoll.add_view("view2", self.view2_add)
        self.assertKeysMatch(self.testcoll.get_view("view1").get_values(), self.view1)
        self.assertKeysMatch(self.testcoll.get_view("view2").get_values(), self.view2)
        self.assertDictionaryMatch(self.testcoll.get_view("view1").get_values(), self.view1)
        self.assertDictionaryMatch(self.testcoll.get_view("view2").get_values(), self.view2)
        return

    def test_remove_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_view("view1", self.view1_add)
        t2 = self.testcoll.add_view("view2", self.view2_add)
        viewnames = { t.get_id() for t in self.testcoll.views() }
        self.assertEqual(viewnames, {"view1", "view2"}|site_views)
        self.testcoll.remove_view("view1")
        viewnames = { t.get_id() for t in self.testcoll.views() }
        self.assertEqual(viewnames, {"view2"}|site_views)
        viewnames = { t.get_id() for t in self.testcoll.views(include_alt=False) }
        self.assertEqual(viewnames, {"view2"})
        return

    # Record lists

    def test_add_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        listnames = { t.get_id() for t in self.testcoll.lists() }
        self.assertEqual(listnames, site_lists)
        t1 = self.testcoll.add_list("list1", self.list1_add)
        t2 = self.testcoll.add_list("list2", self.list2_add)
        listnames = { t.get_id() for t in self.testcoll.lists() }
        self.assertEqual(listnames, {"list1", "list2"}|site_lists)
        listnames = { t.get_id() for t in self.testcoll.lists(include_alt=False) }
        self.assertEqual(listnames, {"list1", "list2"})
        return

    def test_get_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_list("list1", self.list1_add)
        t2 = self.testcoll.add_list("list2", self.list2_add)
        self.assertDictionaryMatch(self.testcoll.get_list("list1").get_values(), self.list1)
        self.assertDictionaryMatch(self.testcoll.get_list("list2").get_values(), self.list2)
        return

    def test_remove_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        t1 = self.testcoll.add_list("list1", self.list1_add)
        t2 = self.testcoll.add_list("list2", self.list2_add)
        listnames = { t.get_id() for t in self.testcoll.lists() }
        self.assertEqual(listnames, {"list1", "list2"}|site_lists)
        self.testcoll.remove_list("list1")
        listnames = { t.get_id() for t in self.testcoll.lists() }
        self.assertEqual(listnames, {"list2"}|site_lists)
        return

#   -----------------------------------------------------------------------------
#
#   CollectionEditView tests
#
#   -----------------------------------------------------------------------------

class CollectionEditViewTest(AnnalistTestCase):
    """
    Tests for Collection views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.view_url = collection_view_url(coll_id="coll1")
        self.edit_url = collection_edit_url(coll_id="coll1")
        self.continuation = "?" + continuation_url_param(self.edit_url)
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionEditViewTest(self):
        self.assertEqual(CollectionEditView.__name__, "CollectionEditView", "Check CollectionView class name")
        return

    def test_get_view(self):
        r = self.client.get(self.view_url)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_all_url(coll_id="coll1"))
        return

    def test_get_edit(self):
        r = self.client.get(self.edit_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Customize collection coll1</h3>")
        return

    def test_get_edit_context(self):
        r = self.client.get(self.edit_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEquals(r.context['title'],   site_title())
        self.assertEquals(r.context['coll_id'], "coll1")
        self.assertEquals(r.context['types'],   ["type1", "type2"])
        self.assertEquals(r.context['lists'],   ["list1", "list2"])
        self.assertEquals(r.context['views'],   ["view1", "view2"])
        self.assertEquals(r.context['select_rows'], "6")
        return

    def test_post_new_type(self):
        form_data = (
            { "type_new":   "New"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        new_type_uri = recordtype_edit_url("new", "coll1")
        self.assertEqual(r['location'], TestHostUri+new_type_uri+self.continuation)
        return

    def test_post_copy_type(self):
        form_data = (
            { "typelist":   "type1"
            , "type_copy":  "Copy"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        copy_type_uri = recordtype_edit_url("copy", "coll1", type_id="type1")
        self.assertEqual(r['location'], TestHostUri+copy_type_uri+self.continuation)
        return

    def test_post_copy_type_no_selection(self):
        form_data = (
            { "type_copy":  "Copy"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        erroruri = self.edit_url+r"\?error_head=.*\&error_message=.*"
        self.assertMatch(r['location'], TestHostUri+erroruri)
        return

    def test_post_edit_type(self):
        form_data = (
            { "typelist":   "type1"
            , "type_edit":  "Edit"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        edit_type_uri = recordtype_edit_url("edit", "coll1", type_id="type1")
        self.assertEqual(r['location'], TestHostUri+edit_type_uri+self.continuation)
        return

    def test_post_edit_type_no_selection(self):
        form_data = (
            { "type_edit":  "Edit"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        erroruri = self.edit_url+r"\?error_head=.*\&error_message=.*"
        self.assertMatch(r['location'], TestHostUri+erroruri)
        return

    def test_post_delete_type(self):
        form_data = (
            { "typelist":   "type1"
            , "type_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertTemplateUsed(r, "annalist_confirm.html")
        # Check confirmation form content
        confirmed_action_uri = recordtype_edit_url("delete", "coll1")
        self.assertContains(r, '''<form method="POST" action="'''+TestBasePath+'''/confirm/">''', status_code=200)
        self.assertEqual(r.context['confirmed_action'], confirmed_action_uri)
        self.assertEqual(r.context['cancel_action'], self.edit_url)
        action_params = json.loads(r.context['action_params'])
        self.assertEqual(action_params['type_delete'], ["Delete"])
        self.assertEqual(action_params['typelist'],    ["type1"])
        return

    def test_post_delete_type_no_selection(self):
        form_data = (
            { "type_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        erroruri = self.edit_url+r"\?error_head=.*\&error_message=.*"
        self.assertMatch(r['location'], TestHostUri+erroruri)
        return

    def test_post_close(self):
        form_data = (
            { "close":  "Close"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri+site_view_url())
        return

# End.
