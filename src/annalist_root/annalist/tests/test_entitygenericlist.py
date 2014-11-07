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
# from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.uri_builder     import uri_params, uri_with_params
from annalist.views.entitylist      import EntityGenericListView #, EntityDataDeleteConfirmedView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    site_dir, collection_dir,
    site_view_url,
    collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user, create_user_permissions
    )
from entity_testtypedata        import (
    recordtype_dir, 
    recordtype_url,
    recordtype_create_values, 
    )
from entity_testentitydata          import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data,
    get_site_lists
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
        self.testtype  = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testcoll", "testtype"))
        self.testtype2 = RecordType.create(self.testcoll, "testtype2", recordtype_create_values("testcoll", "testtype2"))
        self.testdata  = RecordTypeData.create(self.testcoll, "testtype", {})
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        # self.user = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        # self.user.save()
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        e1 = self._create_entity_data("entity1")
        e2 = self._create_entity_data("entity2")
        e3 = self._create_entity_data("entity3")
        e4 = EntityData.create(self.testdata2, "entity4", 
            entitydata_create_values("entity4", type_id="testtype2")
            )
        self.initial_list_ids = get_site_lists()
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
        u = entitydata_list_all_url("testcoll", list_id="Default_list_all") + "?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "Collection testcoll")
        self.assertContains(r, "<h3>List entities with type information</h3>", html=True)
        self.assertMatch(r.content, r'<input.type="hidden".name="continuation_url".+value="/xyzzy/"/>')
        # log.info(r.content) #@@
        cont = uri_params({"continuation_url": u})
        rowdata = """
            <tr class="select_row">
                <td class="small-2 columns"><a href="%(base)s/c/testcoll/d/testtype/entity1/%(cont)s">entity1</a></td>
                <td class="small-2 columns"><a href="%(base)s/c/testcoll/d/_type/testtype/%(cont)s">testtype</a></td>
                <td class="small-8 columns">Entity testcoll/testtype/entity1</td>
                <td class="select_row">
                    <input type="checkbox" name="entity_select" value="testtype/entity1" />
                </td>
            </tr>
            """%({'base': TestBasePath, 'cont': cont})
        # log.info(r.content)
        self.assertContains(r, rowdata, html=True)
        # Test context
        self.assertEqual(r.context['title'],            "Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          None)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.initial_list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list_all")
        # Unbound field descriptions
        self.assertEqual(len(r.context['fields']), 3)
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][1]['field_id'], 'Entity_type')
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        # Entities and bound fields
        # log.info(r.context['entities'])  #@@
        self.assertEqual(len(r.context['entities']), 6)
        entity_fields = (
            [ {'entity_type_id': "_type",     'annal:id': "testtype",  'rdfs:label': "RecordType testcoll/testtype"}
            , {'entity_type_id': "_type",     'annal:id': "testtype2", 'rdfs:label': "RecordType testcoll/testtype2"}
            , {'entity_type_id': "testtype",  'annal:id': "entity1",   'rdfs:label': "Entity testcoll/testtype/entity1"}
            , {'entity_type_id': "testtype",  'annal:id': "entity2",   'rdfs:label': "Entity testcoll/testtype/entity2"}
            , {'entity_type_id': "testtype",  'annal:id': "entity3",   'rdfs:label': "Entity testcoll/testtype/entity3"}
            , {'entity_type_id': "testtype2", 'annal:id': "entity4",   'rdfs:label': "Entity testcoll/testtype2/entity4"}
            ])
        field_keys = ('annal:id', 'entity_type_id', 'rdfs:label')
        for eid in range(6):
            for fid in range(3):
                item_field = r.context['entities'][eid]['fields'][fid]
                head_field = r.context['fields'][fid]
                # Check that row field descriptions match corresponding heading feld descriptions
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_head',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field[fkey], head_field[fkey])
                # Check row field values
                fkey = field_keys[fid]
                self.assertEqual(item_field['field_value'],    entity_fields[eid][fkey])
                self.assertEqual(item_field['entity_type_id'], entity_fields[eid]['entity_type_id'])
        return

    def test_get_fields_list(self):
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")+"?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        rowdata1 = """
            <tr class="select_row">
                <td class="small-3 columns"><a href="%s/c/testcoll/d/_field/Bib_address/%s">Bib_address</a></td>
                <td class="small-3 columns">annal:Text</td>
                <td class="small-6 columns">Bib_address</td>
                <td class="select_row">
                    <input name="entity_select" value="_field/Bib_address" type="checkbox">
                </td>
            </tr>
            """%(TestBasePath, cont)
        # log.info(r.content)
        self.assertContains(r, rowdata1, html=True)
        # Test context
        self.assertEqual(r.context['title'],            "Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.initial_list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        self.assertEqual(len(r.context['fields']), 3)
        # 1st field
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(entity id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][0]['field_render_item'], "field/annalist_item_entityid.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "")
        # 2nd field
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Field value type')
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(field value type)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:field_value_type")
        self.assertEqual(r.context['fields'][1]['field_render_head'], "field/annalist_head_any.html")
        self.assertEqual(r.context['fields'][1]['field_render_item'], "field/annalist_item_identifier.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-3 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Identifier")
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
        # log.info([e['fields'][0]['field_value'] for e in r.context['entities']])
        self.assertIn('_initial_values', [ e['fields'][0]['field_value'] for e in r.context['entities'] ])
        self.assertEqual(len(r.context['entities']), 65)
        field_entities = (
            { ('Entity_id',         "annal:Slug",          "Id")
            , ('Bib_address',       "annal:Text",          "Bib_address")
            , ('Bib_author',        "annal:Text",          "Bib_author")
            , ('Bib_booktitle',     "annal:Text",          "Bib_booktitle")
            , ('Entity_type',       "annal:Slug",          "Type")
            , ('Entity_label',      "annal:Text",          "Label")
            , ('Field_comment',     "annal:Longtext",      "Help")
            , ('Field_placement',   "annal:Placement",     "Size/position")
            , ('Field_type',        "annal:Identifier",    "Field value type")
            , ('Field_render',      "annal:Slug",          "Field render type")
            , ('Field_default',     "annal:Text",          "Default")
            , ('Field_typeref',     "annal:Slug",          "Enum type")
            , ('Field_restrict',    "annal:Text",          "Enum restriction")
            , ('List_comment',      "annal:Longtext",      "Help")
            , ('List_default_type', "annal:Type",          "Record type")
            , ('List_default_view', "annal:View",          "View")
            , ('Type_label',        "annal:Text",          "Label")
            , ('Type_comment',      "annal:Longtext",      "Comment")
            , ('Type_uri',          "annal:Identifier",    "URI")
            , ('List_choice',       "annal:Slug",          "List view")
            , ('View_choice',       "annal:Slug",          "Choose view")
            , ('Field_sel',         "annal:Slug",          "Field id")
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

    def test_get_fields_list_no_continuation(self):
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.get(u+"?foo=bar")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        rowdata1 = """
            <tr class="select_row">
                <td class="small-3 columns"><a href="%s/c/testcoll/d/_field/Bib_address/%s">Bib_address</a></td>
                <td class="small-3 columns">annal:Text</td>
                <td class="small-6 columns">Bib_address</td>
                <td class="select_row">
                    <input name="entity_select" value="_field/Bib_address" type="checkbox">
                </td>
            </tr>
            """%(TestBasePath, cont)
        # log.info(r.content)
        self.assertContains(r, rowdata1, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.initial_list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        self.assertEqual(len(r.context['fields']), 3)
        return

    def test_get_fields_list_search(self):
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list") + "?search=Bib_&continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        rowdata = """
            <tr class="select_row">
                <td class="small-3 columns"><a href="%s/c/testcoll/d/_field/Bib_address/%s">Bib_address</a></td>
                <td class="small-3 columns">annal:Text</td>
                <td class="small-6 columns">Bib_address</td>
                <td class="select_row">
                    <input name="entity_select" value="_field/Bib_address" type="checkbox">
                </td>
            </tr>
            """%(TestBasePath, cont)
        # log.info(r.content)
        # If this test fails, check ordering of URI parameters
        self.assertContains(r, rowdata, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        self.assertEqual(r.context['search_for'],       "Bib_")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.initial_list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        self.assertEqual(len(r.context['fields']), 3)
        self.assertEqual(r.context['fields'][0]['field_id'], 'Entity_id')
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][2]['field_id'], 'Entity_label')
        # Entities
        self.assertEqual(len(r.context['entities']), 21)
        field_entities = (
            { ('Bib_address',       "annal:Text",          "Bib_address")
            , ('Bib_author',        "annal:Text",          "Bib_author")
            , ('Bib_booktitle',     "annal:Text",          "Bib_booktitle")
            , ('Bib_chapter',       "annal:Text",          "Bib_chapter")
            , ('Bib_edition',       "annal:Text",          "Bib_edition")
            , ('Bib_editor',        "annal:Text",          "Bib_editor")
            , ('Bib_eprint',        "annal:Text",          "Bib_eprint")
            , ('Bib_howpublished',  "annal:Text",          "Bib_howpublished")
            , ('Bib_institution',   "annal:Text",          "Bib_institution")
            , ('Bib_journal',       "annal:Text",          "Bib_journal")
            , ('Bib_month',         "annal:Text",          "Bib_month")
            , ('Bib_number',        "annal:Text",          "Bib_number")
            , ('Bib_organization',  "annal:Text",          "Bib_organization")
            , ('Bib_pages',         "annal:Text",          "Bib_pages")
            , ('Bib_publisher',     "annal:Text",          "Bib_publisher")
            , ('Bib_school',        "annal:Text",          "Bib_school")
            , ('Bib_title',         "annal:Text",          "Bib_title")
            , ('Bib_type',          "annal:Text",          "Bib_type")
            , ('Bib_url',           "annal:Text",          "Bib_url")
            , ('Bib_volume',        "annal:Text",          "Bib_volume")
            , ('Bib_year',          "annal:Text",          "Bib_year")
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

    def test_get_list_select_by_type(self):
        u = entitydata_list_type_url("testcoll", "_field", list_id=None)
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.initial_list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        return

    def test_get_list_no_collection(self):
        u = entitydata_list_type_url("no_collection", "_field", list_id="Field_list")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Collection no_collection does not exist", status_code=404)
        return

    def test_get_list_no_type(self):
        u = entitydata_list_type_url("testcoll", "no_type", list_id="Field_list")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Record type no_type in collection testcoll does not exist", status_code=404)
        return

    def test_get_list_no_list(self):
        u = entitydata_list_type_url("testcoll", "_field", list_id="no_list")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Record list no_list in collection testcoll does not exist", status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new --------

    def test_post_new_type_entity(self):
        f = entitylist_form_data("new", list_id="Field_list")
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_all_entity(self):
        # Also tests continuation_url parameter handling
        s = site_view_url()
        f = entitylist_form_data("new", list_id="Field_list", continuation_url=s)
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_url_param(u, continuation_url_param(s))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_one(self):
        f = entitylist_form_data("new", list_id="Field_list", entities=["_field/field1"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_many(self):
        f = entitylist_form_data("new", list_id="Field_list", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'][:len(e)])
        return

    #   -------- copy --------

    def test_post_copy_type_entity(self):
        # Also tests continuation_url parameter handling
        s = site_view_url()
        f = entitylist_form_data("copy", entities=["_field/field1"], continuation_url=s)
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("copy", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_url_param(u, continuation_url_param(s))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_all_entity(self):
        f = entitylist_form_data("copy", entities=["_field/field1"])
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("copy", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_other(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("copy", "testcoll", "testtype", "entity1", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_none(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = "continuation_url"
        e = error_head="Problem%20with%20input&error_message=No%20data%20record%20selected%20to%20copy"
        self.assertIn(TestHostUri + u, r['location'])
        self.assertNotIn(c, r['location'])
        self.assertIn(e, r['location'])
        return

    def test_post_copy_type_entity_select_many(self):
        f = entitylist_form_data("copy", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "testtype")
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
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit --------

    def test_post_edit_type_entity(self):
        f = entitylist_form_data("edit", entities=["_field/field1"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_url_param(u)
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_field", "field1", view_id="Field_view")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_all_entity(self):
        f = entitylist_form_data("edit", entities=["_field/field1"])
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_field", "field1", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_type_entity_select_none(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_select_many(self):
        f = entitylist_form_data("edit", entities=["_field/field1", "testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
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
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- delete --------

    def test_post_delete_type_entity(self):
        testtypedelete = RecordType.create(self.testcoll, "testtypedelete", recordtype_create_values("testcoll", "testtypedelete"))
        testdatadelete = RecordTypeData.create(self.testcoll, "testtypedelete", {})
        f = entitylist_form_data("delete", entities=["_type/testtypedelete"])
        u = entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Confirm requested action</h3>")
        self.assertContains(r, "Remove record testtypedelete of type _type in collection testcoll: Are you sure?")
        self.assertContains(r, 'Click "Confirm" to continue, or "Cancel" to abort operation')
        self.assertContains(r,
            '<input type="hidden" name="confirmed_action"  value="/testsite/c/testcoll/d/_type/!delete_confirmed"/>', 
            html=True
            )
        self.assertEqual(r.context['action_description'], 
            'Remove record testtypedelete of type _type in collection testcoll')
        self.assertEqual(r.context['confirmed_action'], 
            '/testsite/c/testcoll/d/_type/!delete_confirmed')
        self.assertEqual(r.context['action_params'], 
            confirm_delete_params(button_id="entity_delete", entity_id="testtypedelete", type_id="_type", list_id="Type_list")
            )
        self.assertEqual(r.context['cancel_action'], 
            '/testsite/c/testcoll/l/Type_list/_type/')
        return

    def test_post_delete_type_not_exists(self):
        f = entitylist_form_data("delete", entities=["_type/sitetype"])
        u = entitydata_list_all_url("testcoll", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        l = r['location']
        self.assertIn(u, l)
        self.assertIn("error_head=Problem%20with%20input", l)
        # Absent entity assumed to be site level
        self.assertIn("error_message=Cannot%20remove%20site%20built-in%20entity%20sitetype", l)
        return

    def test_post_delete_type_entity_with_values(self):
        f = entitylist_form_data("delete", entities=["_type/testtype"])
        u = entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        l = r['location']
        self.assertIn(u, l)
        self.assertIn("error_head=Problem%20with%20input", l)
        self.assertIn("error_message=Cannot%20remove%20type%20testtype%20with%20existing%20values", l)
        return

    def test_post_delete_site_entity(self):
        f = entitylist_form_data("delete", entities=["_field/Field_comment"])
        u = entitydata_list_type_url("testcoll", "_field", list_id="Field_list")
        # log.info("entitydata_list_all_url: %s"%u)
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
        # 'Close' button on list view
        c = "/xyzzy/"
        f = entitylist_form_data("close", entities=["testtype/entity1", "testtype/entity2"], continuation_url=c)
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + c
        self.assertEqual(v, r['location'])
        return

    def test_post_close_no_continuation(self):
        # 'Close' button on list view with no continuation URI given in form
        f = entitylist_form_data("close", 
            entities=["testtype/entity1", "testtype/entity2"], 
            continuation_url=""
            )
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + site_view_url()
        self.assertEqual(v, r['location'])
        return

    def test_post_view_list(self):
        # 'View' button on list view: change displayed list
        f = entitylist_form_data("view", list_id="View_list")
        u = entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url("testcoll", "_type", list_id="View_list")
        self.assertIn(v, r['location'])
        self.assertNotIn("continuation_url", r['location'])
        return

    def test_post_view_search(self):
        # Redisplay list with entries matching search string
        f = entitylist_form_data("view", search="search&term", continuation_url="/xyzxy/")
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url("testcoll", "testtype", list_id="Default_list")
        c = continuation_url_param("/xyzxy/")
        s = "search=search%26term"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(s, r['location'])
        # Note: Search rendering tested by test_get_fields_list_search above
        return

    def test_post_view_no_type(self):
        # Redisplay list with entries matching search string
        f = entitylist_form_data("view", list_id="Type_list")
        u = entitydata_list_all_url("testcoll", list_id="Default_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_all_url("testcoll", list_id="Type_list")
        c = continuation_url_param(collection_edit_url("testcoll"))
        self.assertIn(v, r['location'])
        self.assertNotIn("continuation_url", r['location'])
        return

    def test_post_default_list(self):
        # This button makes the current list view default for the collection
        f = entitylist_form_data("default_view", list_id="View_list")
        u = entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        h = "info_head=Action%20completed"
        m = "info_message=.*view.*testcoll.*Type_list"
        c = continuation_url_param(collection_edit_url("testcoll"))
        self.assertIn(v, r['location'])
        self.assertIn(h, r['location'])
        self.assertMatch(r['location'], m)
        self.assertNotIn("continuation_url", r['location'])
        return

    def test_post_customize(self):
        f = entitylist_form_data("customize", continuation_url="/xyzxy/")
        u = entitydata_list_all_url("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + collection_edit_url("testcoll")
        c = continuation_url_param(u, continuation_url_param("/xyzxy/"))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

# End.
