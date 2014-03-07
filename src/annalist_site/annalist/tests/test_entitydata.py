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

from django.conf                    import settings
from django.db                      import models
from django.http                    import QueryDict
from django.core.urlresolvers       import resolve, reverse
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.defaultedit     import EntityDefaultEditView #, EntityDefaultDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase

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
        self.testtype = RecordType(self.testcoll, "testtype")
        self.testdata = RecordTypeData(self.testcoll, "testtype")
        return

    def tearDown(self):
        return

    def test_EntityDataTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_entitydata_init(self):
        e = EntityData(self.testdata, "testentity")
        self.assertEqual(e._entitytype,     ANNAL.CURIE.EntityData)
        self.assertEqual(e._entityfile,     layout.ENTITY_DATA_FILE)
        self.assertEqual(e._entityref,      layout.DATA_ENTITY_REF)
        self.assertEqual(e._entityid,       "testentity")
        self.assertEqual(e._entityuri,      TestBaseUri+"/collections/testcoll/d/testtype/testentity/")
        self.assertEqual(e._entitydir,      TestBaseDir+"/collections/testcoll/d/testtype/testentity/")
        self.assertEqual(e._values,         None)
        return

    def test_entitydata1_data(self):
        e = EntityData(self.testdata, "entitydata1")
        e.set_values(entitydata_create_values("entitydata1"))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(expect_value_keys()))
        v = entitydata_load_values("entitydata1")
        self.assertEqual(ed, {k:v[k] for k in expect_value_keys()})
        return

    def test_entitydata2_data(self):
        e = EntityData(self.testdata, "entitydata2")
        e.set_values(entitydata_create_values("entitydata2"))
        ed = e.get_values()
        self.assertEqual(set(ed.keys()), set(expect_value_keys()))
        v = entitydata_load_values("entitydata2")
        self.assertEqual(ed, {k:v[k] for k in expect_value_keys()})
        return

    def test_entitydata_create_load(self):
        e  = EntityData.create(self.testdata, "entitydata1", entitydata_create_values("entitydata1"))
        self.assertEqual(e._entitydir, TestBaseDir+"/collections/testcoll/d/testtype/entitydata1/")
        self.assertTrue(os.path.exists(e._entitydir))
        ed = EntityData.load(self.testdata, "entitydata1").get_values()
        v  = entitydata_load_values("entitydata1")
        self.assertEqual(ed, v)
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
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
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

    def _create_entity_data(self, entity_id):
        "Helper function creates entity data with supplied entity_id"
        e = EntityData.create(self.testdata, entity_id, entitydata_create_values(entity_id))
        return e    

    def _check_entity_data_values(self, entity_id):
        "Helper function checks content of record type entry with supplied entity_id"
        self.assertTrue(EntityData.exists(self.testdata, entity_id))
        e = EntityData.load(self.testdata, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%entity_id)
        self._assert_dict_match(e.get_values(), entitydata_load_values(entity_id))
        return e

    def _check_updated_entity_data_values(self, entity_id):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        self.assertTrue(EntityData.exists(self.testdata, entity_id))
        e = EntityData.load(self.testdata, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_uri(""), TestBaseUri+"/collections/testcoll/types/%s/"%entity_id)
        self._assert_dict_match(e.get_values(), entitydata_updated_values(entity_id))
        return e

    def _assert_dict_match(self, actual_dict, expect_dict):
        for k in expect_dict:
            self.assertTrue(k in actual_dict, "Expected key %s not found in actual"%(k))
            self.assertEqual(actual_dict[k], expect_dict[k], 
                "Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        return

    def _entity_new_args(self):
        return {'coll_id': "testcoll", 'type_id': 'testtype', 'action': "new"}

    def _entity_edit_args(self, entity_id):
        editargs = self._entity_new_args()
        editargs.update({'entity_id': entity_id, 'action': "edit"})
        return editargs

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_EntityDefaultEditView(self):
        self.assertEqual(EntityDefaultEditView.__name__, "EntityDefaultEditView", "Check EntityDefaultEditView class name")
        return

    def test_get_new(self):
        u = reverse(
                "AnnalistEntityDefaultNewView", 
                kwargs=self._entity_new_args()
                )+"?continuation_uri=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_entity_id'],   "00000001")
        self.assertEqual(r.context['entity_uri'],       "/%s/collections/testcoll/d/testtype/00000001/"%(TestBasePath))
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # 1st field
        field_id_help = (
            "A short identifier that distinguishes this record from "+
            "all other records of the same type in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render'], "field/annalist_field_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'], "small-12 medium-4 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "00000001")
        # 2nd field
        field_label_help = (
            "Short string used to describe entity when displayed"
            )
        field_label_value = (
            "Record '00000001' of type 'testtype' in collection 'testcoll'"
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render'], "field/annalist_field_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'], "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], field_label_value)
        # 3rd field
        field_comment_help = (
            "Descriptive text about an entity."
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(description)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_render'], "field/annalist_field_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_placement'], "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], "")
        return

    def test_get_edit(self):
        u = reverse(
                "AnnalistEntityDefaultEditView", 
                kwargs=self._entity_edit_args("entity1")
                )+"?continuation_uri=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "entity1")
        self.assertEqual(r.context['orig_entity_id'],   "entity1")
        self.assertEqual(r.context['entity_uri'],       "/%s/collections/testcoll/d/testtype/entity1/"%(TestBasePath))
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # 1st field
        field_id_help = (
            "A short identifier that distinguishes this record from "+
            "all other records of the same type in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render'], "field/annalist_field_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'], "small-12 medium-4 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "entity1")
        # 2nd field
        field_label_help = (
            "Short string used to describe entity when displayed"
            )
        field_label_value = (
            "Record 'entity1' of type 'testtype' in collection 'testcoll'"
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render'], "field/annalist_field_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'], "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], field_label_value)
        # 3rd field
        field_comment_help = (
            "Descriptive text about an entity."
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(description)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_render'], "field/annalist_field_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_placement'], "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], "Comment for entity1")
        return

    def test_get_edit_not_exists(self):
        u = reverse(
                "AnnalistEntityDefaultEditView", 
                kwargs=self._entity_edit_args("entitynone")
                )+"?continuation_uri=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.info(r.content)
        self.assertContains(r, "<p>Record &#39;entitynone&#39; of type &#39;testtype&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(EntityData.exists(self.testdata, "newtype"))
        f = entitydata_form_data(type_id="newtype", action="new")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_entity_data_values("newtype")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newtype"))
        f = entitydata_form_data(type_id="newtype", action="new", cancel="Cancel")
        u = entitydata_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newtype"))
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
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(type_id="copytype", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists
        self._check_updated_entity_data_values("copytype")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(type_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_uri("copy", "testcoll", type_id="copytype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
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
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        f = entitydata_form_data(type_id="edittype", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        self._check_updated_entity_data_values("edittype")
        return

    def test_post_edit_type_new_id(self):
        self._create_entity_data("edittype1")
        self._check_entity_data_values("edittype1")
        # Now post edit form submission with different values and new id
        f = entitydata_form_data(type_id="edittype2", orig_type_id="edittype1", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "edittype1"))
        self._check_updated_entity_data_values("edittype2")
        return

    def test_post_edit_type_cancel(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Post from cancelled edit form
        f = entitydata_form_data(type_id="edittype", action="edit", cancel="Cancel")
        u = entitydata_edit_uri("edit", "testcoll", type_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], collection_edit_uri())
        # Check that target record type still does not exist and unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
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

    @unittest.skip("unimplemented")
    def test_CollectionActionViewTest(self):
        self.assertEqual(EntityDataDeleteConfirmedView.__name__, "EntityDataDeleteConfirmedView", "Check EntityDataDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    @unittest.skip("unimplemented")
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
