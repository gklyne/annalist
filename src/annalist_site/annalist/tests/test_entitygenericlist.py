"""
Tests for EntityData generic list view

This test suite focuses on listing of record fields used by 
record views and lists.  This serves two purposes:
- it tests some additional options of the entity list logic 
  that are not tested by the dfeault list view, and
- it tests the logic that access site-wide data in addition to
  local data.
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

from annalist.views.entitylist      import EntityGenericListView #, EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    site_dir, collection_dir, 
    collection_edit_uri,
    continuation_uri_param,
    collection_create_values,
    site_title
    )
from entity_testtypedata        import (
    recordtype_dir, 
    recordtype_uri,
    recordtype_create_values, 
    )
from entity_testentitydata          import (
    recorddata_dir,  entitydata_dir,
    entity_uri, entitydata_edit_uri, entitydata_delete_confirm_uri,
    entitydata_list_type_uri, entitydata_list_all_uri,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data
    )

#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------


class EntityGenericListViewTest(AnnalistTestCase):
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
        # @@TODO: add some collection-specific fields
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
        self.initial_list_ids = (
            [ "Default_list", "Default_list_all"
            , "Field_list"
            , "List_list"
            , "Type_list"
            , "View_list"
            ])
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
        self.assertEqual(EntityGenericListView.__name__, "EntityGenericListView", "Check EntityGenericListView class name")
        return

    def test_get_default_all_list(self):
        u = entitydata_list_all_uri("testcoll", list_id="Default_list_all")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>List 'Default_list_all' of entities in collection 'testcoll'</h3>", html=True)
        self.assertMatch(r.content, r'<input.type="hidden".name="continuation_uri".+value="/xyzzy/"/>')
        rowdata = """
            <tr class="select_row">
                <td class="small-2 columns">testtype</td>
                <td class="small-2 columns"><a href="%s/c/testcoll/v/Default_view/testtype/entity1">entity1</a></td>
                <td class="small-8 columns">Entity testcoll/testtype/entity1</td>
                <td class="select_row">
                    <input type="checkbox" name="entity_select" value="testtype/entity1" />
                </td>
            </tr>
            """%(TestBasePath)
        self.assertContains(r, rowdata, html=True)
        # log.info(r.content)
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          None)
        self.assertEqual(r.context['list_ids'],         self.initial_list_ids)
        self.assertEqual(r.context['list_selected'],    "Default_list_all")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Unbound field descriptions
        self.assertEqual(len(r.context['fields']), 3)
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_type')
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
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

    def test_get_fields_list(self):
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        rowdata = """
            <tr class="select_row">
                <td class="small-3 columns"><a href="%s/c/testcoll/v/Field_view/_field/Bib_address">Bib_address</a></td>
                <td class="small-3 columns">annal:field_render/Text</td>
                <td class="small-6 columns">Bib_address</td>
                <td class="select_row">
                    <input name="entity_select" value="_field/Bib_address" type="checkbox">
                </td>
            </tr>
            """%(TestBasePath)
        # log.info(r.content)
        self.assertContains(r, rowdata, html=True)
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['list_ids'],         self.initial_list_ids)
        self.assertEqual(r.context['list_selected'],    "Field_list")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 3)
        # 1st field
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][0]['field_render_item'], "field/annalist_item_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "(entity id)")
        # 2nd field
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Field value type')
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(field value type)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:field_render")
        self.assertEqual(r.context['fields'][1]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][1]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:RenderType")
        # 3rd field
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Entity_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][2]['field_render_item'], "field/annalist_item_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-6 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Text")
        # Entities
        self.assertEqual(len(r.context['entities']), 49)
        field_entities = (
            { ('Entity_id',         "annal:field_render/EntityRef",     "Id")
            , ('Bib_address',       "annal:field_render/Text",          "Bib_address")
            , ('Bib_author',        "annal:field_render/Text",          "Bib_author")
            , ('Bib_booktitle',     "annal:field_render/Text",          "Bib_booktitle")
            , ('Entity_type',       "annal:field_render/Type",          "Type")
            , ('Entity_label',      "annal:field_render/Text",          "Label")
            , ('Field_comment',     "annal:field_render/Textarea",      "Help")
            , ('Field_placement',   "annal:field_render/Placement",     "Size/position")
            , ('Field_type',        "annal:field_render/Identifier",    "Field value type")
            , ('List_comment',      "annal:field_render/Textarea",      "Help")
            , ('List_record_type',  "annal:field_render/Record_type",   "Record type")
            , ('Type_label',        "annal:field_render/Text",          "Label")
            , ('Type_comment',      "annal:field_render/Textarea",      "Comment")
            , ('Type_uri',          "annal:field_render/Text",          "URI")
            })
        for f in field_entities:
            for eid in range(len(r.context['entities'])):
                item_fields = r.context['entities'][eid]['fields']
                if item_fields[0]['field_value'] == f[0]:
                    for fid in range(3):
                        item_field = r.context['entities'][eid]['fields'][fid]
                        head_field = r.context['fields'][fid]
                        for fkey in (
                                'field_id', 'field_name', 'field_label', 
                                'field_property_uri', 'field_render_head',
                                'field_placement', 'field_value_type'):
                            self.assertEqual(item_field[fkey], head_field[fkey])
                        self.assertEqual(item_field['field_value'], f[fid])
                    break
            else:
                self.fail("Field %s not found in context"%f[0])
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new --------

    def test_post_new_type_entity(self):
        f = entitylist_form_data("new", list_id="Field_list")
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_all_entity(self):
        f = entitylist_form_data("new", list_id="Field_list")
        u = entitydata_list_all_uri("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_one(self):
        f = entitylist_form_data("new", list_id="Field_list", entities=["_field/field1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_many(self):
        f = entitylist_form_data("new", list_id="Field_list", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'][:len(e)])
        return

    #   -------- copy --------

    def test_post_copy_type_entity(self):
        f = entitylist_form_data("copy", entities=["_field/field1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("copy", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_all_entity(self):
        f = entitylist_form_data("copy", entities=["_field/field1"])
        u = entitydata_list_all_uri("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("copy", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_other(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("copy", "testcoll", "testtype", "entity1", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_none(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_uri_param(collection_edit_uri("testcoll"))
        e = error_head="Problem%20with%20input&error_message=No%20data%20record%20selected%20to%20copy"
        self.assertIn(TestHostUri + u, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(e, r['location'])
        return

    def test_post_copy_type_entity_select_many(self):
        f = entitylist_form_data("copy", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
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
        f = entitylist_form_data("copy", entities=["_field/field1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit --------

    def test_post_edit_type_entity(self):
        f = entitylist_form_data("edit", entities=["_field/field1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        v = TestHostUri + entitydata_edit_uri("edit", "testcoll", "_field", "field1", view_id="Field_view")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_all_entity(self):
        f = entitylist_form_data("edit", entities=["_field/field1"])
        u = entitydata_list_all_uri("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_uri("edit", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_type_entity_select_none(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_select_many(self):
        f = entitylist_form_data("edit", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("edit", entities=["_field/field1"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- delete --------

    def test_post_delete_type_entity(self):
        f = entitylist_form_data("delete", entities=["_type/testtype"])
        u = entitydata_list_type_uri("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Confirm requested action</h3>")
        self.assertContains(r, "Remove record testtype of type _type in collection testcoll: Are you sure?")
        self.assertContains(r, 'Click "Confirm" to continue, or "Cancel" to abort operation')
        self.assertContains(r, '<input type="hidden" name="complete_action"  value="/testsite/c/testcoll/d/_type/!delete_confirmed"/>')
        self.assertEqual(r.context['action_description'], 
            'Remove record testtype of type _type in collection testcoll')
        self.assertEqual(r.context['complete_action'], 
            '/testsite/c/testcoll/d/_type/!delete_confirmed')
        self.assertEqual(r.context['action_params'], 
            '{"entity_delete": ["Delete"], "entity_id": ["testtype"], "continuation_uri": ["/testsite/c/testcoll/l/Type_list/_type/"]}')
        self.assertEqual(r.context['cancel_action'], 
            '/testsite/c/testcoll/l/Type_list/_type/')
        return

    def test_post_delete_all_entity(self):
        f = entitylist_form_data("delete", entities=["_type/testtype"])
        u = entitydata_list_all_uri("testcoll", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Confirm requested action</h3>")
        # print "**********"
        # print r.content
        # print "**********"
        self.assertContains(r, "<h3>Confirm requested action</h3>")
        self.assertContains(r, "Remove record testtype of type _type in collection testcoll: Are you sure?")
        self.assertContains(r, 'Click "Confirm" to continue, or "Cancel" to abort operation')
        self.assertContains(r, '<input type="hidden" name="complete_action"  value="/testsite/c/testcoll/d/_type/!delete_confirmed"/>')
        self.assertEqual(r.context['action_description'], 
            'Remove record testtype of type _type in collection testcoll')
        self.assertEqual(r.context['complete_action'], 
            '/testsite/c/testcoll/d/_type/!delete_confirmed')
        self.assertEqual(r.context['action_params'], 
            '{"entity_delete": ["Delete"], "entity_id": ["testtype"], "continuation_uri": ["/testsite/c/testcoll/l/Type_list/"]}')
        self.assertEqual(r.context['cancel_action'], 
            '/testsite/c/testcoll/l/Type_list/')
        return

    def test_post_delete_site_entity(self):
        f = entitylist_form_data("delete", entities=["_field/Field_comment"])
        u = entitydata_list_type_uri("testcoll", "_field", list_id="Field_list")
        # log.info("entitydata_list_all_uri: %s"%u)
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e1 = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e1, r['location'])
        e2 = "Cannot%20remove%20site%20built-in%20entity%20Field_comment"
        self.assertIn(e2, r['location'])
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

    @unittest.skip("@@TODO genericlist search button handler")
    def test_post_search(self):
        return

    @unittest.skip("@@TODO genericlist default-view button handler")
    def test_post_default_view(self):
        return

    def test_post_customize(self):
        f = entitylist_form_data("customize")
        u = entitydata_list_all_uri("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + collection_edit_uri("testcoll")
        c = continuation_uri_param(u, continuation_uri_param(collection_edit_uri("testcoll")))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

# End.
