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

from annalist.views.defaultedit     import EntityDefaultEditView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    site_dir, collection_dir, 
    collection_edit_uri,
    collection_create_values,
    site_title
    )
from entity_testtypedata            import (
    recordtype_edit_uri,
    recordtype_create_values,
    )
from entity_testentitydata          import (
    recorddata_dir,  entitydata_dir,
    entity_uri, entitydata_edit_uri, 
    entitydata_list_type_uri,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitydata_recordtype_view_form_data
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
        self.type_ids   = ['testtype', 'Default_type', 'fields']
        self.no_options = ['(no options)']
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

    def _check_entity_data_values(self, entity_id, type_id="testtype", update="Entity", parent=None):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        recorddata = RecordTypeData.load(self.testcoll, type_id)
        self.assertTrue(EntityData.exists(recorddata, entity_id))
        e = EntityData.load(recorddata, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_uri(""), TestHostUri + entity_uri("testcoll", type_id, entity_id))
        v = entitydata_values(entity_id, type_id=type_id, update=update)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_EntityDefaultEditView(self):
        self.assertEqual(EntityDefaultEditView.__name__, "EntityDefaultEditView", "Check EntityDefaultEditView class name")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        formrow1 = """
              <!-- editable text field -->
              <div class="small-12 medium-6 columns">
                <div class="row">
                  <div class="view_label small-12 medium-4 columns">
                    <p>
                      Id
                    </p>
                  </div>
                  <div class="small-12 medium-8 columns">
                    <!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->
                    <input type="text" size="64" name="entity_id" value="00000001">
                  </div>
                </div>
              </div>
            """
        formrow2 = """
              <!-- record type dropdown -->
              <div class="small-12 medium-6 right columns">
                <div class="row">
                  <div class="view_label small-12 medium-4 columns">
                    <p>
                      Type
                    </p>
                  </div>
                  <div class="small-12 medium-8 columns">
                    <select name="entity_type" class="right">
                        <option selected="selected">testtype</option>
                        <option>Default_type</option>
                        <option>fields</option>
                    </select>
                  </div>
                </div>
              </div>
            """
        formrow3 = """
              <!-- editable text field -->
              <div class="small-12 columns">
                <div class="row">
                  <div class="view_label small-12 medium-2 columns">
                    <p>
                      Label
                    </p>
                  </div>
                  <div class="small-12 medium-10 columns">
                    <!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->
                    <input type="text" size="64" name="Entity_label" value="Entity '00000001' of type 'testtype' in collection 'testcoll'">
                  </div>
                </div>
              </div>
            """
        formrow4 = """
              <!-- editable textarea field -->
              <div class="small-12 columns">
                <div class="row">
                  <div class="view_label small-12 medium-2 columns">
                    <p>
                      Comment
                    </p>
                  </div>
                  <div class="small-12 medium-10 columns">
                    <textarea cols="64" rows="6" name="Entity_comment" class="small-rows-4 medium-rows-8"></textarea>
                  </div>
                </div>
              </div>
            """
        # log.info("******\n"+r.content)
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri(entity_id="00000001"))
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 4)
        # 1st field
        field_id_help = (
            "A short identifier that distinguishes this record from "+
            "all other records of the same type in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'],            'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'],          'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'],         'Id')
        self.assertEqual(r.context['fields'][0]['field_help'],          field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'],   "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'],  "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_view'],   "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'],   "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_placement'].label, "small-12 medium-4 columns")
        self.assertEqual(r.context['fields'][0]['field_placement'].value, "small-12 medium-8 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'],    "annal:Slug")
        self.assertEqual(r.context['fields'][0].field_value,            "00000001")
        self.assertEqual(r.context['fields'][0]['field_value'],         "00000001")
        self.assertEqual(r.context['fields'][0]['entity_type_id'],      "testtype")
        self.assertEqual(r.context['fields'][0]['options'],             self.no_options)
        # 2nd field
        field_type_help = (
            "A short identifier that identifies the type of the corresponding entity."
            )
        self.assertEqual(r.context['fields'][1]['field_id'],            'Entity_type')
        self.assertEqual(r.context['fields'][1]['field_name'],          'entity_type')
        self.assertEqual(r.context['fields'][1]['field_label'],         'Type')
        self.assertEqual(r.context['fields'][1]['field_help'],          field_type_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'],   "(recordtype id)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'],  "entity_type_id")
        self.assertEqual(r.context['fields'][1]['field_render_view'],   "field/annalist_view_select.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'],   "field/annalist_edit_select.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 medium-6 right columns")
        self.assertEqual(r.context['fields'][1]['field_placement'].label, "small-12 medium-4 columns")
        self.assertEqual(r.context['fields'][1]['field_placement'].value, "small-12 medium-8 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'],    "annal:Slug")
        self.assertEqual(r.context['fields'][1].field_value,            "testtype")
        self.assertEqual(r.context['fields'][1]['field_value'],         "testtype")
        self.assertEqual(r.context['fields'][1]['entity_type_id'],      "testtype")
        self.assertEqual(r.context['fields'][1]['options'],             self.type_ids)
        # 3rd field
        field_label_help = (
            "Short string used to describe entity when displayed"
            )
        field_label_value = (
            "Entity '00000001' of type 'testtype' in collection 'testcoll'"
            )
        self.assertEqual(r.context['fields'][2]['field_id'],            'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_name'],          'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_label'],         'Label')
        self.assertEqual(r.context['fields'][2]['field_help'],          field_label_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'],   "(label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'],  "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_view'],   "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'],   "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'],    "annal:Text")
        self.assertEqual(r.context['fields'][2]['field_value'],         field_label_value)
        self.assertEqual(r.context['fields'][2]['entity_type_id'],      "testtype")
        self.assertEqual(r.context['fields'][2]['options'],             self.no_options)
        # 4th field
        field_comment_help = (
            "Descriptive text about an entity."
            )
        self.assertEqual(r.context['fields'][3]['field_id'],            'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_name'],          'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_label'],         'Comment')
        self.assertEqual(r.context['fields'][3]['field_help'],          field_comment_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'],   "(description)")
        self.assertEqual(r.context['fields'][3]['field_property_uri'],  "rdfs:comment")
        self.assertEqual(r.context['fields'][3]['field_render_view'],   "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_render_edit'],   "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'],    "annal:Longtext")
        self.assertEqual(r.context['fields'][3]['field_value'],         "")
        self.assertEqual(r.context['fields'][3]['entity_type_id'],      "testtype")
        self.assertEqual(r.context['fields'][3]['options'],             self.no_options)
        return

    def test_get_edit(self):
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entity1")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "entity1")
        self.assertEqual(r.context['orig_id'],          "entity1")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri("testcoll", "testtype", "entity1"))
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 4)        
        # 1st field
        field_id_help = (
            "A short identifier that distinguishes this record from "+
            "all other records of the same type in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "entity1")
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field
        field_type_help = (
            "A short identifier that identifies the type of the corresponding entity."
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'entity_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Type')
        self.assertEqual(r.context['fields'][1]['field_help'], field_type_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(recordtype id)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "entity_type_id")
        self.assertEqual(r.context['fields'][1]['field_render_view'],   "field/annalist_view_select.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'],   "field/annalist_edit_select.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 medium-6 right columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][1]['field_value'], "testtype")
        self.assertEqual(r.context['fields'][1]['options'], self.type_ids)
        # 3rd field
        field_label_help = (
            "Short string used to describe entity when displayed"
            )
        field_label_value = (
            "Entity testcoll/testtype/entity1"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][2]['field_value'], field_label_value)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field
        field_comment_help = (
            "Descriptive text about an entity."
            )
        field_comment_value = (
            "Entity coll testcoll, type testtype, entity entity1"
            )
        self.assertEqual(r.context['fields'][3]['field_id'], 'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Entity_comment')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][3]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], "(description)")
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][3]['field_render_view'], "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_render_edit'], "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][3]['field_value'], field_comment_value)
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entitynone")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.debug(r.content)
        self.assertContains(r, "<p>Entity &#39;entitynone&#39; of type &#39;testtype&#39; in collection &#39;testcoll&#39; does not exist</p>", status_code=404)
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    def test_post_new_entity_missing_id(self):
        f = entitydata_form_data(action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
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
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        # log.info(repr(r.context['fields'][1]))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", type_id="Default_type", action="new")
        u = entitydata_edit_uri("new", "testcoll", "Default_type")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "Default_type"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="Default_type")
        return

    def test_new_entity_new_type(self):
        # Checks logic for creating an entity which may require creation of new recorddata
        # Create new type
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = entitydata_recordtype_view_form_data(
            coll_id="testcoll", type_id="_type", entity_id="newtype",
            action="new"
            )
        u = entitydata_edit_uri("new", "testcoll", type_id="_type", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "_type"))
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        # Create new entity
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", type_id="newtype", action="new")
        u = entitydata_edit_uri("new", "testcoll", "newtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "newtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="newtype")
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    def test_post_copy_entity_missing_id(self):
        f = entitydata_form_data(action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
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
        self.assertContains(r, site_title("<title>%s</title>"))
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity")
        return

    def test_post_edit_entity_new_id(self):
        self._create_entity_data("entityeditid1")
        self._check_entity_data_values("entityeditid1")
        # Now post edit form submission with different values and new id
        f = entitydata_form_data(entity_id="entityeditid2", orig_id="entityeditid1", action="edit")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityeditid1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "entityeditid1"))
        self._check_entity_data_values("entityeditid2")
        return

    def test_post_edit_entity_new_type(self):
        self._create_entity_data("entityedittype")
        self._check_entity_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        newtype = RecordType.create(self.testcoll, "newtype", recordtype_create_values("newtype"))
        newtypedata = RecordTypeData(self.testcoll, "newtype")
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id
        f = entitydata_form_data(
            entity_id="entityedittype", orig_id="entityedittype", 
            type_id="newtype", orig_type="testtype",
            action="edit")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityedittype")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type data now exists, and that new record exists and old does not
        self.assertTrue(RecordTypeData.exists(self.testcoll, "newtype"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(EntityData.exists(newtypedata, "entityedittype"))
        self._check_entity_data_values("entityedittype", type_id="newtype")
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
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
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
        self.assertContains(r, site_title("<title>%s</title>"))
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
        self.assertContains(r, site_title("<title>%s</title>"))
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

# End.
