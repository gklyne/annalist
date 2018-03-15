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

from django.conf                    import settings
from django.db                      import models
from django.http                    import QueryDict
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist                       import message
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.recordtype     import RecordType

from annalist.views.collection      import CollectionEditView

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url, 
    collection_view_url, 
    collection_edit_url, 
    collection_entity_view_url,
    continuation_url_param,
    collection_value_keys, collection_create_values, collection_values,
    site_title,
    create_test_user
    )
from entity_testuserdata    import (
    annalistuser_create_values, annalistuser_values, annalistuser_read_values
    )
from entity_testtypedata    import (
    recordtype_edit_url,
    recordtype_create_values, recordtype_read_values
    )
from entity_testviewdata    import (
    recordview_edit_url,
    recordview_create_values, recordview_read_values,
    )
from entity_testlistdata    import (
    recordlist_edit_url,
    recordlist_create_values, recordlist_read_values,
    )
from entity_testfielddata import (
    recordfield_init_keys, recordfield_value_keys, recordfield_load_keys,
    recordfield_create_values, recordfield_values, recordfield_read_values,
    )
from entity_testentitydata  import (
    entitydata_list_all_url
    )
from entity_testsitedata    import (
    get_site_types, get_site_types_sorted,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from entity_testcolldata    import (
    collectiondata_view_url
    )

#   -----------------------------------------------------------------------------
#
#   Collection object tests
#
#   -----------------------------------------------------------------------------

site_types  = get_site_types()
site_views  = get_site_views()
site_lists  = get_site_lists()
site_fields = get_site_fields()

class CollectionTest(AnnalistTestCase):
    """
    Tests for Collection object interface
    """

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
        self.testsite     = Site(TestBaseUri, TestBaseDir)
        self.testcoll     = Collection(self.testsite, "testcoll")
        self.coll1        = collection_values("coll1")
        self.testcoll_add = collection_create_values("testcoll")
        self.type1_add    = recordtype_create_values("testcoll",  "type1")
        self.type1        = recordtype_read_values("testcoll",    "type1")
        self.type2_add    = recordtype_create_values("testcoll",  "type2")
        self.type2        = recordtype_read_values("testcoll",    "type2")
        self.view1_add    = recordview_create_values("testcoll",  "view1")
        self.view1        = recordview_read_values("testcoll",    "view1")
        self.view2_add    = recordview_create_values("testcoll",  "view2")
        self.view2        = recordview_read_values("testcoll",    "view2")
        self.list1_add    = recordlist_create_values("testcoll",  "list1")
        self.list1        = recordlist_read_values("testcoll",    "list1")
        self.list2_add    = recordlist_create_values("testcoll",  "list2")
        self.list2        = recordlist_read_values("testcoll",    "list2")
        self.field1_add   = recordfield_create_values("testcoll", "field1")
        self.field1       = recordfield_read_values("testcoll",   "field1")
        self.field2_add   = recordfield_create_values("testcoll", "field2")
        self.field2       = recordfield_read_values("testcoll",   "field2")
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata(scope="all")
        return

    def test_CollectionTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_collection_init(self):
        log.debug("test_collection_init: TestBaseUri %s, TestBaseDir %s"%(TestBaseUri,TestBaseDir))
        s = Site(TestBaseUri, TestBaseDir)
        c = Collection(s, "testcoll")
        self.assertEqual(c._entitytype,     ANNAL.CURIE.Collection)
        self.assertEqual(c._entitybase,     layout.COLL_BASE_REF)
        self.assertEqual(c._entityfile,     layout.COLL_META_FILE)
        self.assertEqual(c._entityref,      layout.META_COLL_REF)
        self.assertEqual(c._entityid,       "testcoll")
        self.assertEqual(c._entityurl,      TestHostUri + collection_view_url(coll_id="testcoll"))
        self.assertEqual(c._entitydir,      collection_dir(coll_id="testcoll"))
        self.assertEqual(c._values,         None)
        return

    def test_collection_data(self):
        self.testcoll.set_values(self.testcoll_add)
        cd = self.testcoll.get_values()
        self.assertDictionaryMatch(cd, self.testcoll_add)
        return

    # User permissions

    def test_get_local_user_permissions(self):
        # Create local permissions
        usr = AnnalistUser.create(self.testcoll, "user1", annalistuser_create_values(user_id="user1"))
        # Test access to permissions defined locally in collection
        ugp = self.testcoll.get_user_permissions("user1", "mailto:testuser@example.org")
        self.assertEqual(ugp[ANNAL.CURIE.id],                 "user1")
        self.assertEqual(ugp[ANNAL.CURIE.type_id],            "_user")
        self.assertEqual(ugp[RDFS.CURIE.label],               "Test User")
        self.assertEqual(ugp[RDFS.CURIE.comment],             "User user1: permissions for Test User in collection testcoll")
        self.assertEqual(ugp[ANNAL.CURIE.user_uri],           "mailto:testuser@example.org")
        self.assertEqual(ugp[ANNAL.CURIE.user_permission],    ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"])
        return

    def test_get_local_user_not_defined(self):
        ugp = self.testcoll.get_user_permissions("user1", "mailto:testuser@example.org")
        self.assertIsNone(ugp)
        return

    def test_get_local_user_uri_mismatch(self):
        usr = AnnalistUser.create(self.testcoll, "user1", annalistuser_create_values(user_id="user1"))
        ugp = self.testcoll.get_user_permissions("user1", "mailto:anotheruser@example.org")
        self.assertIsNone(ugp)
        return

    def test_get_local_user_missing_fields(self):
        # E.g. what happens if user record is created through default view?  Don't return value.
        d = annalistuser_create_values(user_id="user1")
        d.pop(ANNAL.CURIE.user_permission)
        usr = AnnalistUser.create(self.testcoll, "user1", d)
        ugp = self.testcoll.get_user_permissions("user1", "mailto:testuser@example.org")
        self.assertIsNone(ugp)
        return

    def test_get_site_user_permissions(self):
        ugp = self.testcoll.get_user_permissions("_unknown_user_perms", "annal:User/_unknown_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.id],                 "_unknown_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.type_id],            "_user")
        self.assertEqual(ugp[RDFS.CURIE.label],               "Unknown user")
        self.assertEqual(ugp[ANNAL.CURIE.user_uri],           "annal:User/_unknown_user_perms")
        self.assertEqual(ugp[ANNAL.CURIE.user_permission],    ["VIEW"])
        return

    def test_get_site_user_uri_mismatch(self):
        ugp = self.testcoll.get_user_permissions("_unknown_user_perms", "annal:User/_another_user")
        self.assertIsNone(ugp)
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
        typenames =  { t.get_id() for t in self.testcoll.types(altscope=None) }
        self.assertEqual(typenames, {"type2", "testtype"})
        return

    def test_exists_type(self):
        # Some type existence tests taking account of site data default type
        self.assertTrue(RecordType.exists(self.testcoll, "testtype"))
        self.assertFalse(RecordType.exists(self.testcoll, "notype"))
        self.assertFalse(RecordType.exists(self.testcoll, "Default_type"))
        self.assertTrue(RecordType.exists(self.testcoll, "Default_type", altscope="all"))
        return

    # Record views

    def test_add_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        viewnames = { v.get_id() for v in self.testcoll.views() }
        self.assertEqual(viewnames, site_views)
        v1 = self.testcoll.add_view("view1", self.view1_add)
        v2 = self.testcoll.add_view("view2", self.view2_add)
        viewnames = { v.get_id() for v in self.testcoll.views() }
        self.assertEqual(viewnames, {"view1", "view2"}|site_views)
        return

    def test_get_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        v1 = self.testcoll.add_view("view1", self.view1_add)
        v2 = self.testcoll.add_view("view2", self.view2_add)
        self.assertKeysMatch(self.testcoll.get_view("view1").get_values(), self.view1)
        self.assertKeysMatch(self.testcoll.get_view("view2").get_values(), self.view2)
        self.assertDictionaryMatch(self.testcoll.get_view("view1").get_values(), self.view1)
        self.assertDictionaryMatch(self.testcoll.get_view("view2").get_values(), self.view2)
        return

    def test_remove_view(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        v1 = self.testcoll.add_view("view1", self.view1_add)
        v2 = self.testcoll.add_view("view2", self.view2_add)
        viewnames = { v.get_id() for v in self.testcoll.views() }
        self.assertEqual(viewnames, {"view1", "view2"}|site_views)
        self.testcoll.remove_view("view1")
        viewnames = { v.get_id() for v in self.testcoll.views() }
        self.assertEqual(viewnames, {"view2"}|site_views)
        viewnames = { v.get_id() for v in self.testcoll.views(altscope=None) }
        self.assertEqual(viewnames, {"view2"})
        return

    # Record lists

    def test_add_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        listnames = { l.get_id() for l in self.testcoll.lists() }
        self.assertEqual(listnames, site_lists)
        l1 = self.testcoll.add_list("list1", self.list1_add)
        l2 = self.testcoll.add_list("list2", self.list2_add)
        listnames = { l.get_id() for l in self.testcoll.lists() }
        self.assertEqual(listnames, {"list1", "list2"}|site_lists)
        listnames = { l.get_id() for l in self.testcoll.lists(altscope=None) }
        self.assertEqual(listnames, {"list1", "list2"})
        return

    def test_get_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        l1 = self.testcoll.add_list("list1", self.list1_add)
        l2 = self.testcoll.add_list("list2", self.list2_add)
        self.assertDictionaryMatch(self.testcoll.get_list("list1").get_values(), self.list1)
        self.assertDictionaryMatch(self.testcoll.get_list("list2").get_values(), self.list2)
        return

    def test_remove_list(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        l1 = self.testcoll.add_list("list1", self.list1_add)
        l2 = self.testcoll.add_list("list2", self.list2_add)
        listnames = { l.get_id() for l in self.testcoll.lists() }
        self.assertEqual(listnames, {"list1", "list2"}|site_lists)
        self.testcoll.remove_list("list1")
        listnames = { l.get_id() for l in self.testcoll.lists() }
        self.assertEqual(listnames, {"list2"}|site_lists)
        return

    # View/list fields

    def test_add_field(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        fieldnames = { f.get_id() for f in self.testcoll.fields() }
        self.assertEqual(fieldnames, site_fields)
        f1 = self.testcoll.add_field("field1", self.field1_add)
        f2 = self.testcoll.add_field("field2", self.field2_add)
        fieldnames = { f.get_id() for f in self.testcoll.fields() }
        self.assertEqual(fieldnames, {"field1", "field2"}|site_fields)
        return

    def test_get_field(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        f1 = self.testcoll.add_field("field1", self.field1_add)
        f2 = self.testcoll.add_field("field2", self.field2_add)
        self.assertDictionaryMatch(self.testcoll.get_field("field1").get_values(), self.field1)
        self.assertDictionaryMatch(self.testcoll.get_field("field2").get_values(), self.field2)
        return

    def test_remove_field(self):
        self.testsite.add_collection("testcoll", self.testcoll_add)
        f1 = self.testcoll.add_field("field1", self.field1_add)
        f2 = self.testcoll.add_field("field2", self.field2_add)
        fieldnames = { f.get_id() for f in self.testcoll.fields() }
        self.assertEqual(fieldnames, {"field1", "field2"}|site_fields)
        self.testcoll.remove_field("field1")
        fieldnames =  { f.get_id() for f in self.testcoll.fields() }
        self.assertEqual(fieldnames, {"field2"}|site_fields)
        fieldnames =  { f.get_id() for f in self.testcoll.fields(altscope=None) }
        self.assertEqual(fieldnames, {"field2"})
        return

    # Alternative parent setting

    def test_set_alt_entities_1(self):
        altcoll1  = Collection(self.testsite, "altcoll1")
        parents   = self.testcoll.set_alt_entities(altcoll1)
        parentids = [ p.get_id() for p in parents ]
        self.assertEqual( parentids, ["testcoll", "altcoll1", layout.SITEDATA_ID])
        return

    def test_set_alt_entities_2(self):
        coll_id   = "altcoll1"
        altcoll1  = Collection.create(self.testsite, coll_id, collection_create_values(coll_id))
        parents   = altcoll1.set_alt_entities(self.testcoll)
        parentids = [ p.get_id() for p in parents ]
        self.assertEqual( parentids, ["altcoll1", "testcoll", layout.SITEDATA_ID])
        return

    def test_set_alt_entities_loop(self):
        altcoll1  = Collection(self.testsite, "altcoll1")
        parents   = self.testcoll.set_alt_entities(altcoll1)
        parentids = [ p.get_id() for p in parents ]
        self.assertEqual( parentids, ["testcoll", "altcoll1", layout.SITEDATA_ID])
        with SuppressLogging(logging.ERROR):
            with self.assertRaises(ValueError):
                parents   = altcoll1.set_alt_entities(self.testcoll)
        return

    def test_set_alt_entities_no_site(self):
        altcoll1  = Collection(self.testsite, "altcoll1")
        parents   = self.testcoll.set_alt_entities(altcoll1)
        parentids = [ p.get_id() for p in parents ]
        self.assertEqual( parentids, ["testcoll", "altcoll1", layout.SITEDATA_ID])
        altcoll1._altparent = None
        with SuppressLogging(logging.ERROR):
            with self.assertRaises(ValueError):
                parents   = self.testcoll.set_alt_entities(altcoll1)
        return

    def test_alt_parent_inherit_coll(self):
        # Test inheritance of definitions from an alternative collection
        # (tescoll is set up with testtype created)
        coll_id = "newcoll"
        newcoll = Collection.create(self.testsite, coll_id, collection_create_values(coll_id))
        altparents = newcoll.set_alt_entities(self.testcoll)
        parentids  = [ p.get_id() for p in altparents ]
        self.assertEqual(parentids, ["newcoll", "testcoll", layout.SITEDATA_ID])
        self.assertTrue(RecordType.exists(newcoll, "testtype", altscope="all"))
        testtype = RecordType.load(newcoll, "testtype", altscope="all")
        self.assertEquals(testtype["rdfs:label"], "RecordType testcoll/_type/testtype")
        return

    def test_alt_parent_inherit_site(self):
        # Test inheritance of definitions from site with an alternative collection set
        coll_id = "newcoll"
        newcoll = Collection.create(self.testsite, coll_id, collection_create_values(coll_id))
        altparents = newcoll.set_alt_entities(self.testcoll)
        parentids  = [ p.get_id() for p in altparents ]
        self.assertEqual(parentids, ["newcoll", "testcoll", layout.SITEDATA_ID])
        self.assertTrue(RecordType.exists(newcoll, "Default_type", altscope="all"))
        def_type = RecordType.load(newcoll, "Default_type", altscope="all")
        self.assertEquals(def_type["rdfs:label"], "Default record")
        return

    def test_alt_parent_inherit_user(self):
        # Test inheritance of "user" scope definitions
        coll_id = "newcoll"
        newcoll = Collection.create(self.testsite, coll_id, collection_create_values(coll_id))
        user1   = AnnalistUser.create(self.testcoll, "user1", annalistuser_create_values(user_id="user1"))
        user2   = AnnalistUser.create(newcoll,       "user2", annalistuser_create_values(user_id="user2"))
        altparents = newcoll.set_alt_entities(self.testcoll)
        parentids  = [ p.get_id() for p in altparents ]
        self.assertEqual(parentids, ["newcoll", "testcoll", layout.SITEDATA_ID])
        self.assertFalse(AnnalistUser.exists(newcoll, "user1", altscope="user"))
        self.assertTrue(AnnalistUser.exists(newcoll, "_default_user_perms", altscope="user"))   # Access site data
        self.assertTrue(AnnalistUser.exists(newcoll, "user2", altscope="user"))
        testuser = AnnalistUser.load(newcoll, "user2", altscope="user")
        self.assertEquals(testuser["rdfs:label"], "Test User")
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
        self.coll1    = Collection.load(self.testsite, "coll1")
        self.view_url = collection_view_url(coll_id="coll1")
        self.edit_url = collection_edit_url(coll_id="coll1")
        self.continuation = "?" + continuation_url_param(self.edit_url)
        # Login and permissions
        create_test_user(self.coll1, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata(scope="all")
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

    def test_get_view_no_collection(self):
        u = collection_view_url(coll_id="no_collection")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<p>Collection no_collection does not exist</p>", status_code=404)
        return

    def test_get_view_newer_version(self):
        collmeta = collection_create_values(coll_id="newer_version")
        self.testsite.add_collection("newer_version", collmeta, annal_ver="99.99.99")
        u = collection_view_url(coll_id="newer_version")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   500)
        self.assertEqual(r.reason_phrase, "Server error")
        self.assertContains(r, "created by software version 99.99.99", status_code=500)
        return

    def test_get_edit(self):
        r = self.client.get(self.edit_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection coll1</title>")
        self.assertContains(r, 
            '<h2 class="page-heading">Customize collection: Collection coll1</h2>', 
            html=True
            )
        return

    def test_get_edit_no_collection(self):
        u = collection_edit_url(coll_id="no_collection")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        return

    def test_get_edit_context(self):
        r = self.client.get(self.edit_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEquals(r.context['title'],   "Collection coll1")
        self.assertEquals(r.context['coll_id'], "coll1")
        self.assertEquals([e.get_id() for e in r.context['types']],   ["type1", "type2"])
        self.assertEquals([e.get_id() for e in r.context['lists']],   ["list1", "list2"])
        self.assertEquals([e.get_id() for e in r.context['views']],   ["view1", "view2"])
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
        # Create empty type
        empty_type_values = recordtype_create_values("coll1", "type_empty")
        empty_type        = self.coll1.add_type("type_empty", empty_type_values)
        # Now try to delete it
        form_data = (
            { "typelist":   "type_empty"
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
        self.assertEqual(action_params['typelist'],    ["type_empty"])
        return

    def test_post_delete_type_with_values(self):
        form_data = (
            { "typelist":   "type1"
            , "type_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertIn(self.edit_url+"?",                   r['location'])
        self.assertIn("error_head=Problem%20with%20input", r['location'])
        self.assertIn("error_message=",                    r['location'])
        return

    def test_post_delete_type_no_selection(self):
        form_data = (
            { "type_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertIn(self.edit_url+"?",                   r['location'])
        self.assertIn("error_head=Problem%20with%20input", r['location'])
        self.assertIn("error_message=",                    r['location'])
        return

    def test_post_delete_list(self):
        # Try to delete list
        form_data = (
            { "listlist":   "list1"
            , "list_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertTemplateUsed(r, "annalist_confirm.html")
        # Check confirmation form content
        confirmed_action_uri = recordlist_edit_url("delete", "coll1")
        self.assertContains(r, '''<form method="POST" action="'''+TestBasePath+'''/confirm/">''', status_code=200)
        self.assertEqual(r.context['confirmed_action'], confirmed_action_uri)
        self.assertEqual(r.context['cancel_action'], self.edit_url)
        action_params = json.loads(r.context['action_params'])
        self.assertEqual(action_params['list_delete'], ["Delete"])
        self.assertEqual(action_params['listlist'],    ["list1"])
        return

    def test_post_delete_view(self):
        # Try to delete view
        form_data = (
            { "viewlist":   "view1"
            , "view_delete":  "Delete"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertTemplateUsed(r, "annalist_confirm.html")
        # Check confirmation form content
        confirmed_action_uri = recordview_edit_url("delete", "coll1")
        self.assertContains(r, '''<form method="POST" action="'''+TestBasePath+'''/confirm/">''', status_code=200)
        self.assertEqual(r.context['confirmed_action'], confirmed_action_uri)
        self.assertEqual(r.context['cancel_action'], self.edit_url)
        action_params = json.loads(r.context['action_params'])
        self.assertEqual(action_params['view_delete'], ["Delete"])
        self.assertEqual(action_params['viewlist'],    ["view1"])
        return

    def test_post_migrate(self):
        form_data = (
            { "migrate":  "Migrate data"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        l1 = TestHostUri+self.edit_url
        l2 = "info_head=Action%20completed"
        l3 = "info_message=Migrated%20data%20for%20collection%20coll1"
        self.assertIn(l1, r['location'])
        self.assertIn(l2, r['location'])
        self.assertIn(l3, r['location'])
        return

    def test_post_metadata(self):
        form_data = (
            { "metadata":  "Collection metadata"
            })
        r = self.client.post(self.edit_url, form_data)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        metadataurl = collectiondata_view_url(coll_id="coll1", action="edit")
        self.assertEqual(r['location'], TestHostUri+metadataurl+self.continuation)
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
