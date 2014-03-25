"""
Tests for EntityData default list view
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

from annalist.views.defaultlist     import EntityDefaultListView #, EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    recordtype_create_values, collection_create_values,
    site_dir, collection_dir, recordtype_dir, recorddata_dir,  entitydata_dir,
    collection_edit_uri,
    continuation_uri_param,
    recordtype_uri,
    entity_uri, entitydata_edit_uri, entitydata_delete_confirm_uri,
    entitydata_list_type_uri, entitydata_list_all_uri,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data,
    site_title
    )

#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------

class EntityDefaultListViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype  = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata  = RecordTypeData.create(self.testcoll, "testtype", {})
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        e1 = self._create_entity_data("entity1")
        e2 = self._create_entity_data("entity2")
        e3 = self._create_entity_data("entity3")
        e4 = EntityData.create(self.testdata2, "entity4", 
            entitydata_create_values("entity4", type_id="testtype2")
            )
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

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_EntityDefaultListView(self):
        self.assertEqual(EntityDefaultListView.__name__, "EntityDefaultListView", "Check EntityDefaultListView class name")
        return

    def test_get_default_all_list(self):
        u = entitydata_list_all_uri("testcoll")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>List 'Default_list_all' of entities in collection 'testcoll'</h3>", html=True)
        self.assertMatch(r.content, r'<input.type="hidden".name="continuation_uri".+value="/xyzzy/"/>')
        rowdata = """
            <tr class="select_row">
                <td class="small-2 columns">testtype</td>
                <td class="small-2 columns">entity1</td>
                <td class="small-8 columns">Entity testcoll/testtype/entity1</td>
                <td class="select_row">
                    <input type="checkbox" name="entity_select" value="testtype/entity1" />
                </td>
            </tr>
            """
        self.assertContains(r, rowdata, html=True)
        # log.info(r.content)
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          None)
        self.assertEqual(r.context['list_ids'],         ["Default_list", "Default_list_all"])
        self.assertEqual(r.context['list_selected'],    "Default_list_all")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Unbound field descriptions
        self.assertEqual(len(r.context['fields']), 3)
        #  1st field
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_type')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Entity_type')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Type')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(recordtype id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "entity_type_id")
        self.assertEqual(r.context['fields'][0]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][0]['field_render_item'], "field/annalist_item_type.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-2 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], None)
        self.assertEqual(r.context['fields'][0]['entity_type_id'], None)
        #  2nd field
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_id')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][1]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][1]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-2 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][1]['field_value'], None)
        self.assertEqual(r.context['fields'][1]['entity_type_id'], None)
        # 3rd field
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][2]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-8 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][2]['field_value'], None)
        self.assertEqual(r.context['fields'][2]['entity_type_id'], None)
        # Entities and bound fields
        self.assertEqual(len(r.context['entities']), 4)
        field_values = ("%(etyp)s", "entity%(eid)d", "Entity testcoll/%(etyp)s/entity%(eid)d")
        entity_types = ("testtype", "testtype", "testtype", "testtype2")
        for eid in range(4):
            for fid in range(3):
                item_field = r.context['entities'][eid]['fields'][fid]
                head_field = r.context['fields'][fid]
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_head',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field[fkey], head_field[fkey])
                if field_values[fid]:
                    field_val = field_values[fid]%{'eid': (eid+1), 'etyp': entity_types[eid]}
                else:
                    field_val = None
                self.assertEqual(item_field['field_value'], field_val)
                self.assertEqual(item_field['entity_type_id'], entity_types[eid])
        return

    def test_get_default_type_list(self):
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>List 'Default_list' of entities in collection 'testcoll'</h3>", html=True)
        rowdata = """
            <tr class="select_row">
                <td class="small-3 columns">entity1</td>
                <td class="small-9 columns">Entity testcoll/testtype/entity1</td>
                <td class="select_row">
                    <input type="checkbox" name="entity_select" value="testtype/entity1" />
                </td>
            </tr>
            """
        self.assertContains(r, rowdata, html=True)
        # log.info(r.content)
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['list_ids'],         ["Default_list", "Default_list_all"])
        self.assertEqual(r.context['list_selected'],    "Default_list")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][0]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], None)
        # 2nd field
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][1]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-9 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        # Entities
        self.assertEqual(len(r.context['entities']), 3)
        field_val = ("entity%d", "Entity testcoll/testtype/entity%d")
        for eid in range(3):
            for fid in range(2):
                item_field = r.context['entities'][eid]['fields'][fid]
                head_field = r.context['fields'][fid]
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_head',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field[fkey], head_field[fkey])
                self.assertEqual(item_field['field_value'], field_val[fid]%(eid+1))
        return

    @unittest.skip("@@TODO - handle URI with specified list ID (probably another module)")
    def test_get_named_list(self):
        u = entitydata_list_uri("testcoll", "testtype")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>List of entities in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 2)
        # 1st field
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][0]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], None)
        # 2nd field
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][1]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-9 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        # Entities
        self.assertEqual(len(r.context['entities']), 3)
        field_val = ("entity%d", "Entity testcoll/testtype/entity%d")
        for eid in range(3):
            for fid in range(2):
                item_field = r.context['entities'][eid]['fields'][fid]
                head_field = r.context['fields'][fid]
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_head',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field[fkey], head_field[fkey])
                self.assertEqual(item_field['field_value'], field_val[fid]%(eid+1))
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new --------

    def test_post_new_type_entity(self):
        f = entitylist_form_data("new")
        u = entitydata_list_type_uri("testcoll", "testtype")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_edit_uri("new", "testcoll", "testtype") + c)
        return
        
    @unittest.skip("@@TODO new without type_id")
    def test_post_new_all_entity(self):
        f = entitylist_form_data("new")
        u = entitydata_list_all_uri("testcoll")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestHostUri + entitydata_edit_uri("new", "testcoll") + c)
        return

    def test_post_new_type_entity_select_one(self):
        f = entitylist_form_data("new", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_edit_uri("new", "testcoll", "testtype") + c)
        return

    def test_post_new_type_entity_select_many(self):
        f = entitylist_form_data("new", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'][:len(e)])
        return

    #   -------- copy --------

    def test_post_copy_type_entity(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        v = TestHostUri + entitydata_edit_uri("copy", "testcoll", "testtype", "entity1")
        self.assertEqual(r['location'], v+c)
        return

    @unittest.skip("@@TODO copy without type_id")
    def test_post_new_all_entity(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_all_uri("testcoll")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestHostUri + entitydata_edit_uri("copy", "testcoll") + c)
        return

    def test_post_copy_type_entity_select_none(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_copy_type_entity_select_many(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_copy_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit --------

    def test_post_edit_type_entity(self):
        f = entitylist_form_data("edit", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        v = TestHostUri + entitydata_edit_uri("edit", "testcoll", "testtype", "entity1")
        self.assertEqual(r['location'], v+c)
        return

    @unittest.skip("@@TODO edit without type_id")
    def test_post_new_all_entity(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_all_uri("testcoll")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestHostUri + entitydata_edit_uri("edit", "testcoll") + c)
        return

    def test_post_edit_type_entity_select_none(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_select_many(self):
        f = entitylist_form_data("edit", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("edit", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- close / search / view / default-view / customize--------

    def test_post_close(self):
        f = entitylist_form_data("close", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + collection_edit_uri("testcoll")
        self.assertEqual(v, r['location'])
        return

    @unittest.skip("@@TODO defaultlist search handler")
    def test_post_search(self):
        return

    @unittest.skip("@@TODO defaultlist default-view handler")
    def test_post_default_view(self):
        return

    def test_post_customize(self):
        f = entitylist_form_data("customize")
        u = entitydata_list_all_uri("testcoll")
        c = continuation_uri_param(u + continuation_uri_param(collection_edit_uri("testcoll")))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestHostUri + collection_edit_uri("testcoll") + c)
        return

# End.
