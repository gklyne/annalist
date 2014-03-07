"""
Tests for EntityData module and default view
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
from django.core.urlresolvers   import resolve, reverse
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout
from annalist.models.site       import Site
from annalist.models.collection import Collection
from annalist.models.entitydata import EntityData

from annalist.views.defaultedit import EntityDefaultEditView #, EntityDefaultDeleteConfirmedView

from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                      import init_annalist_test_site
from AnnalistTestCase           import AnnalistTestCase

#   -----------------------------------------------------------------------------
#
#   Test data helpers
#
#   -----------------------------------------------------------------------------

def entitydata_edit_uri(action, coll_id, type_id, entity_id=None):
    viewname = ( 
        'AnnalistEntityDefaultNewView'      if action == "new" else
        'AnnalistEntityDefaultEditView'
        )
    kwargs = {'action': action, 'coll_id': coll_id, 'type_id': type_id}
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def collection_edit_uri(coll_id="testcoll"):
    return TestHostUri + reverse("AnnalistCollectionEditView", kwargs={'coll_id': coll_id})

def entitydata_delete_confirm_uri(coll_id, type_id):
    kwargs = {'coll_id': coll_id, 'type_id': type_id}
    return TestHostUri + reverse("AnnalistEntityDataDeleteView", kwargs=kwargs)

def entitydata_delete_confirm_form_data(entity_id=None):
    return (
        { 'entitylist':    entity_id,
          'entity_delete': 'Delete'
        })

def collection_create_values(coll_id="testcoll"):
    return (
        { 'rdfs:label':     'Collection %s'%coll_id
        , 'rdfs:comment':   'Description of Collection %s'%coll_id
        })

def recordtype_create_values(type_id="testtype"):
    return (
        { 'rdfs:label':     'recordType %s'%type_id
        , 'rdfs:comment':   'Description of RecordType %s'%type_id
        })

def entitydata_create_values(entity_id):
    return (
        { 'rdfs:label': 'Entity testcoll/testtype/%s'%entity_id
        , 'rdfs:comment': 'Entity: coll testcoll, type testtype, entity %s'%entity_id
        , 'annal:uri': '/%s/c/testcoll/d/testtype/%s/'%(TestBasePath, entity_id)
        })

def expect_value_keys():
    return (
        [ 'annal:id', 'annal:type', 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        ])

def entitydata_load_values(entity_id):
    return (
        { '@id':                './'
        , 'annal:id':           entity_id
        , 'annal:type':         'annal:EntityData'
        , 'annal:uri':          '/%s/c/testcoll/d/testtype/%s/'%(TestBasePath, entity_id)
        , 'rdfs:label':         'Entity testcoll/testtype/%s'%entity_id
        , 'rdfs:comment':       'Entity: coll testcoll, type testtype, entity %s'%entity_id
        })

def entitydata_form_data(entity_id=None, orig_entity_id=None, action=None, cancel=None):
    form_data_dict = (
        { 'entity_label':       'Entity data ... in collection testcoll'
        , 'entity_comment':     'Description of entity data ...'
        , 'orig_entity_id':     'orig_entity_id'
        , 'continuation_uri':   '/%s/c/testcoll/d/testtype/'%(TestBasePath)
        })
    if entity_id:
        form_data_dict['entity_id']         = entity_id
        form_data_dict['orig_entity_id']    = entity_id
        form_data_dict['entity_label']      = 'Entity testcoll/testtype/%s'%entity_id
        form_data_dict['entity_comment']    = 'Entity: coll testcoll, type testtype, entity %s'%entity_id
    if orig_entity_id:
        form_data_dict['orig_entity_id']    = orig_entity_id
    if action:
        form_data_dict['action']            = action
    if cancel:
        form_data_dict['cancel']            = "Cancel"
    else:
        form_data_dict['save']              = 'Save'
    return form_data_dict

def entitydata_context_data(entity_id=None, orig_entity_id=None, action=None):
    context_dict = (
        { 'title':              'Annalist data journal test site'
        , 'coll_id':            'testcoll'
        , 'orig_entity_id':     'orig_entity_id'
        , 'entity_label':       'Record type ... in collection testcoll'
        , 'entity_comment':     'Comment for entity ...'
        , 'entity_uri':         '/%s/c/testcoll/d/testtype/.../'%TestBasePath
        , 'continuation_uri':   '/%s/c/testcoll/d/testtype/'%TestBasePath
        })
    if entity_id:
        context_dict['entity_id']       = entity_id
        context_dict['orig_entity_id']  = entity_id
        context_dict['entity_label']    = 'Record type %s in collection testcoll'%(entity_id)
        context_dict['entity_comment']  = 'Comment for entity %s'%(entity_id)
        context_dict['entity_uri']      = '/%s/collections/testcoll/types/%s/'%(TestBasePath, entity_id)
    if orig_entity_id:
        context_dict['orig_entity_id']  = orig_entity_id
    if action:  
        context_dict['action']  = action
    return context_dict

def entitydata_updated_values(entity_id):
    return (
        { '@id':            './'
        , 'annal:id':       entity_id
        , 'annal:type':     'annal:EntityData'
        , 'annal:uri':      '/%s/collections/testcoll/types/%s/'%(TestBasePath, entity_id)
        , 'rdfs:label':     'Record type %s in collection testcoll'%entity_id
        , 'rdfs:comment':   'Help for record type %s'%entity_id
        })

def entitydata_delete_confirm_values(coll_id, entity_id):
    return (
        { "foo": "bar"
        })

#   -----------------------------------------------------------------------------
#
#   EntityData tests
#
#   -----------------------------------------------------------------------------

class EntityDataTest(TestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def test_EntityDataTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_entitydata_init(self):
        t = EntityData(self.testcoll, "testtype")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.EntityData)
        self.assertEqual(t._entityfile,     layout.TYPE_META_FILE)
        self.assertEqual(t._entityref,      layout.META_TYPE_REF)
        self.assertEqual(t._entityid,       "testtype")
        self.assertEqual(t._entityuri,      TestBaseUri+"/collections/testcoll/types/testtype/")
        self.assertEqual(t._entitydir,      TestBaseDir+"/collections/testcoll/types/testtype/")
        self.assertEqual(t._values,         None)
        return

    def test_entitydata1_data(self):
        t = EntityData(self.testcoll, "type1")
        t.set_values(entitydata_create_values("type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(expect_value_keys()))
        v = entitydata_load_values("type1")
        self.assertEqual(td, {k:v[k] for k in expect_value_keys()})
        return

    def test_entitydata2_data(self):
        t = EntityData(self.testcoll, "type2")
        t.set_values(entitydata_create_values("type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(expect_value_keys()))
        v = entitydata_load_values("type2")
        self.assertEqual(td, {k:v[k] for k in expect_value_keys()})
        return

    def test_entitydata_create_load(self):
        t  = EntityData.create(self.testcoll, "type1", entitydata_create_values("type1"))
        td = EntityData.load(self.testcoll, "type1").get_values()
        v = entitydata_load_values("type1")
        self.assertEqual(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   EntityDefaultEditView tests
#
#   -----------------------------------------------------------------------------

class EntityDefaultEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
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

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_type(self, type_id):
        "Helper function creates record type entry with supplied type_id"
        t = EntityData.create(self.testcoll, type_id, entitydata_create_values(type_id))
        return t    

    def _check_record_type_values(self, type_id):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(EntityData.exists(self.testcoll, type_id))
        t = EntityData.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%type_id)
        self._assert_dict_match(t.get_values(), entitydata_load_values(type_id))
        return t

    def _check_updated_record_type_values(self, type_id):
        "Helper function checks content of form-updated record type entry with supplied type_id"
        self.assertTrue(EntityData.exists(self.testcoll, type_id))
        t = EntityData.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%type_id)
        self._assert_dict_match(t.get_values(), entitydata_updated_values(type_id))
        return t

    def _assert_dict_match(self, actual_dict, expect_dict):
        for k in expect_dict:
            self.assertTrue(k in actual_dict, "Expected key %s not found in actual"%(k))
            self.assertEqual(actual_dict[k], expect_dict[k], 
                "Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_EntityDefaultEditView(self):
        self.assertEqual(EntityDefaultEditView.__name__, "EntityDefaultEditView", "Check EntityDefaultEditView class name")
        return

    def test_get_new(self):
        u = reverse(
                "AnnalistEntityDataNewView", 
                kwargs={'coll_id': "coll1", 'action': 'new'}
                )+"?continuation_uri=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "00000001")
        self.assertEqual(r.context['orig_type_id'],     "00000001")
        self.assertEqual(r.context['type_label'],       "Record type 00000001 in collection coll1")
        self.assertEqual(r.context['type_help'],        "")
        self.assertEqual(r.context['type_uri'],         "/%s/collections/coll1/00000001/"%(TestBasePath))
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        return

    def test_get_copy(self):
        u = reverse(
                "AnnalistEntityDataCopyView", 
                kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'copy'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_type_id'],     "type1")
        self.assertEqual(r.context['type_label'],       "Record type coll1/type1")
        self.assertEqual(r.context['type_help'],        "Annalist collection1 entitydata1")
        self.assertEqual(r.context['type_uri'],         "http://localhost:8000/annalist/collections/coll1/types/type1/")
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    def test_get_copy_not_exists(self):
        u = reverse(
                "AnnalistEntityDataCopyView", 
                kwargs={'coll_id': "coll1", 'type_id': 'notype', 'action': 'copy'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        self.assertContains(r, "<p>Record type notype in collection coll1 does not exist</p>", status_code=404)
        return

    def test_get_edit(self):
        u = reverse(
                "AnnalistEntityDefaultEditView", 
                kwargs={'coll_id': "coll1", 'type_id': 'type1', 'action': 'edit'}
                )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Record type in collection coll1</h3>")
        # Test context (values read from test data fixture)
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "coll1")
        self.assertEqual(r.context['type_id'],          "type1")
        self.assertEqual(r.context['orig_type_id'],     "type1")
        self.assertEqual(r.context['type_label'],       "Record type coll1/type1")
        self.assertEqual(r.context['type_help'],        "Annalist collection1 entitydata1")
        self.assertEqual(r.context['type_uri'],         "http://localhost:8000/annalist/collections/coll1/types/type1/")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], None)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(EntityData.exists(self.testcoll, "newtype"))
        f = entitydata_form_data(type_id="newtype", action="new")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_record_type_values("newtype")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(EntityData.exists(self.testcoll, "newtype"))
        f = entitydata_form_data(type_id="newtype", action="new", cancel="Cancel")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = entitydata_form_data(action="new")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = entitydata_context_data(action="new")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = entitydata_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = entitydata_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="new")
        self._assert_dict_match(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(EntityData.exists(self.testcoll, "copytype"))
        f = entitydata_form_data(type_id="copytype", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_record_type_values("copytype")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(EntityData.exists(self.testcoll, "copytype"))
        f = entitydata_form_data(type_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = entitydata_form_data(action="copy")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = entitydata_context_data(action="copy")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_copy_type_invalid_id(self):
        f = entitydata_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        expect_context = entitydata_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="copy")
        self._assert_dict_match(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = entitydata_form_data(type_id="edittype", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        self._check_updated_record_type_values("edittype")
        return

    def test_post_edit_type_new_id(self):
        self._create_record_type("edittype1")
        self._check_record_type_values("edittype1")
        # Now post edit form submission with different values and new id
        f = entitydata_form_data(type_id="edittype2", orig_type_id="edittype1", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testcoll, "edittype1"))
        self._check_updated_record_type_values("edittype2")
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Post from cancelled edit form
        f = entitydata_form_data(type_id="edittype", action="edit", cancel="Cancel")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = entitydata_form_data(action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_context_data(action="edit")
        self._assert_dict_match(r.context, expect_context)
        return

    def test_post_edit_type_invalid_id(self):
        f = entitydata_form_data(type_id="!badtype", orig_type_id="orig_type_id", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        self.assertContains(r, "<h3>Record type in collection testcoll</h3>")
        # Test context
        expect_context = entitydata_context_data(type_id="!badtype", orig_type_id="orig_type_id", action="edit")
        self._assert_dict_match(r.context, expect_context)
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmEntityDataDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmEntityDataDeleteTests(AnnalistTestCase):
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

    def test_CollectionActionViewTest(self):
        self.assertEqual(EntityDataDeleteConfirmedView.__name__, "EntityDataDeleteConfirmedView", "Check EntityDataDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_type(self):
        t = EntityData.create(self.testcoll, "deletetype", entitydata_create_values("deletetype"))
        self.assertTrue(EntityData.exists(self.testcoll, "deletetype"))
        # Submit positive confirmation
        u = entitydata_delete_confirm_uri("testcoll")
        f = entitydata_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+collection_edit_uri("testcoll")+r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(EntityData.exists(self.testcoll, "deletetype"))
        return

# End.
