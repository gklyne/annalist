"""
Tests for EntityData default editing view
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

from annalist.views.defaultedit     import EntityDefaultEditView, EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    recordtype_create_values, collection_create_values,
    site_dir, collection_dir, recordtype_dir, recorddata_dir,  entitydata_dir,
    recordtype_uri,
    entity_uri, entitydata_list_uri, entitydata_edit_uri, entitydata_delete_confirm_uri,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data
    )

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

    def _create_entity_data(self, entity_id, update="Entity"):
        "Helper function creates entity data with supplied entity_id"
        e = EntityData.create(self.testdata, entity_id, 
            entitydata_create_values(entity_id, update=update)
            )
        return e    

    def _check_entity_data_values(self, entity_id, update="Entity"):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        self.assertTrue(EntityData.exists(self.testdata, entity_id))
        e = EntityData.load(self.testdata, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_uri(""), TestHostUri + entity_uri("testcoll", "testtype", entity_id))
        self.assertDictionaryMatch(e.get_values(), entitydata_values(entity_id, update=update))
        return e

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_EntityDefaultEditView(self):
        self.assertEqual(EntityDefaultEditView.__name__, "EntityDefaultEditView", "Check EntityDefaultEditView class name")
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri(entity_id="00000001"))
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
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-6 medium-4 columns")
        self.assertEqual(r.context['fields'][0]['field_placement'].label, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_placement'].value, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        # log.info(repr(r.context['fields'][0]))
        self.assertEqual(r.context['fields'][0].field_value, "00000001")
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
        self.assertEqual(r.context['fields'][1]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
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
        self.assertEqual(r.context['fields'][2]['field_render_view'], "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'], "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], "")
        return

    def test_get_edit(self):
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entity1")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            "Annalist data journal test site")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "entity1")
        self.assertEqual(r.context['orig_id'],          "entity1")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri("testcoll", "testtype", "entity1"))
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
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-6 medium-4 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "entity1")
        # 2nd field
        field_label_help = (
            "Short string used to describe entity when displayed"
            )
        field_label_value = (
            "Entity testcoll/testtype/entity1"
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], field_label_value)
        # 3rd field
        field_comment_help = (
            "Descriptive text about an entity."
            )
        field_comment_value = (
            "Entity coll testcoll, type testtype, entity entity1"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(description)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_render_view'], "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'], "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], field_comment_value)
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entitynone")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.debug(r.content)
        self.assertContains(r, "<p>Record &#39;entitynone&#39; of type &#39;testtype&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    def test_post_new_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity")
        return

    def test_post_new_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", action="new", cancel="Cancel")
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    def test_post_new_entity_missing_id(self):
        f = entitydata_form_data(action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_context_data(action="new")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_entity_invalid_id(self):
        f = entitydata_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(entity_id="copytype", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check that new record type exists
        self._check_entity_data_values("copytype")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(entity_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    def test_post_copy_entity_missing_id(self):
        f = entitydata_form_data(action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_context_data(action="copy")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = entitydata_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="copy"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_entity_data("entityedit")
        self._check_entity_data_values("entityedit")
        f = entitydata_form_data(entity_id="entityedit", action="edit", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityedit")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity")
        return

    def test_post_edit_entity_new_id(self):
        self._create_entity_data("edittype1")
        self._check_entity_data_values("edittype1")
        # Now post edit form submission with different values and new id
        f = entitydata_form_data(entity_id="edittype2", orig_id="edittype1", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "edittype1"))
        self._check_entity_data_values("edittype2")
        return

    def test_post_edit_entity_cancel(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Post from cancelled edit form
        f = entitydata_form_data(entity_id="edittype", action="edit", cancel="Cancel", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_uri("testcoll", "testtype"))
        # Check that target record type still does not exist and unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID missing
        f = entitydata_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID malformed
        f = entitydata_form_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Annalist data journal test site</title>")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmEntityDataDeleteTests - tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmEntityDataDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.testdata = RecordTypeData(self.testcoll, "testtype")
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

    # NOTE:  this logic only tests the entity deletion completion code.
    # It is assumed that the response to requesting entity deletion is checked elsewhere.
    def test_post_confirmed_remove_entity(self):
        t = EntityData.create(self.testdata, "deleteentity", entitydata_create_values("deleteentity"))
        self.assertTrue(EntityData.exists(self.testdata, "deleteentity"))
        # Submit positive confirmation
        u = entitydata_delete_confirm_uri("testcoll", "testtype")
        f = entitydata_delete_confirm_form_data("deleteentity")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            entitydata_list_uri("testcoll", "testtype")+
            r"\?info_head=.*&info_message=.*deleteentity.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(EntityData.exists(self.testcoll, "deleteentity"))
        return

# End.
