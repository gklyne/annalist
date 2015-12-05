"""
Tests for EntityData list view with additional inherited bbiography data
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

from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.uri_builder             import uri_params, uri_with_params
from annalist.views.entitylist              import EntityGenericListView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site, init_annalist_bib_site, 
    init_annalist_test_coll, init_annalist_bib_coll, 
    resetSitedata
    )
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url,
    collection_view_url, collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user, create_user_permissions,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value
    )
from entity_testtypedata    import (
    recordtype_dir, 
    recordtype_url,
    recordtype_create_values, 
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    # get_site_types, get_site_types_sorted, get_site_types_linked,
    # get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    # get_site_views, get_site_views_sorted, get_site_views_linked,
    # get_site_list_types, get_site_list_types_sorted,
    # get_site_field_groups, get_site_field_groups_sorted, 
    # get_site_fields, get_site_fields_sorted, 
    # get_site_field_types, get_site_field_types_sorted, 
    get_site_bib_types, get_site_bib_types_sorted, get_site_bib_types_linked,
    get_site_bib_lists, get_site_bib_lists_sorted, get_site_bib_lists_linked,
    )
from entity_testlistdata    import recordlist_url

#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------

class EntityInheritListViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        self.testsite  = init_annalist_bib_site()
        self.testcoll  = init_annalist_bib_coll()
        self.testdata  = RecordTypeData.load(self.testcoll, "testtype")
        self.testtype2 = RecordType.create(self.testcoll, "testtype2", recordtype_create_values("testcoll", "testtype2"))
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
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
        self.list_ids = get_site_bib_lists_linked("testcoll")
        return

    def tearDown(self):
        # resetSitedata()
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
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

    def test_get_default_all_scope_all_list(self):
        # List all entities in current collection and site-wide
        u = entitydata_list_all_url(
            "testcoll", list_id="Default_list_all", scope="all"
            ) + "?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "Collection testcoll")
        self.assertContains(r, "<h3>List entities with type information</h3>", html=True)
        # Test context
        self.assertEqual(r.context['title'],            "Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "Default_type")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list_all")
        # Unbound field descriptions
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 3)
        self.assertEqual(head_fields[0]['field_id'], 'Entity_id')
        self.assertEqual(head_fields[1]['field_id'], 'Entity_type')
        self.assertEqual(head_fields[2]['field_id'], 'Entity_label')
        # Entities and bound fields
        entities = context_list_entities(r.context)
        if len(entities) != 210:
            for e in entities:
                log.debug("All entities: %s/%s"%(e['annal:type_id'], e['annal:id']))
        self.assertEqual(len(entities), 210)    # Will change with site data
        return

    def test_get_types_scope_all_list(self):
        # List types in current collection and site-wide
        u = entitydata_list_type_url(
            "testcoll", "_type", list_id="Type_list", scope="all"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content) #@@
        # Test context
        self.assertEqual(r.context['title'],            "Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 2)
        # 1st field
        self.assertEqual(head_fields[0]['field_id'], 'Entity_id')
        self.assertEqual(head_fields[0]['field_name'], 'entity_id')
        # 2nd field
        self.assertEqual(head_fields[1]['field_id'], 'Entity_label')
        self.assertEqual(head_fields[1]['field_name'], 'Entity_label')
        # Entities
        entities   = context_list_entities(r.context)
        listed_entities = { e['entity_id']: e for e in entities }
        #@@ self.assertIn('_initial_values', listed_entities)
        type_entities = get_site_bib_types() | {"testtype", "testtype2"}
        self.assertEqual(set(listed_entities.keys()), type_entities)
        return

    def test_get_fields_list(self):
        # List fields in current collection
        u = entitydata_list_type_url(
            "testcoll", "_field", list_id="Field_list", scope="all"
            )+"?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content) #@@
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        cont = ""
        rowdata1 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="_field/Bib_address" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/_field/Bib_address/%(cont)s">Bib_address</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/Enum_render_type/Text/%(cont)s">Short text</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up"><span>annal:Text</span></div>
                  <div class="view-value small-4 medium-3 columns"><span>Address</span></div>
                </div>
              </div>
            </div>
            """%({'base': TestBasePath, 'cont': cont})
        # log.info(r.content)
        self.assertContains(r, rowdata1, html=True)
        # Test context
        self.assertEqual(r.context['title'],            "Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 4)
        # 1st field
        self.assertEqual(head_fields[0]['field_id'],           'Entity_id')
        self.assertEqual(head_fields[0]['field_name'],         'entity_id')
        self.assertEqual(head_fields[0]['field_label'],        'Id')
        self.assertEqual(head_fields[0]['field_placeholder'],  "(entity id)")
        self.assertEqual(head_fields[0]['field_property_uri'], "annal:id")
        self.assertEqual(head_fields[0]['field_render_type'],  "EntityId")
        self.assertEqual(head_fields[0]['field_value_mode'],   "Value_direct")
        self.assertEqual(head_fields[0]['field_target_type'],  "annal:Slug")
        self.assertEqual(head_fields[0]['field_placement'].field, "small-4 medium-3 columns")
        self.assertEqual(head_fields[0]['field_value'],        "")
        # 2nd field
        self.assertEqual(head_fields[1]['field_id'],           'Field_render')
        self.assertEqual(head_fields[1]['field_name'],         'Field_render')
        self.assertEqual(head_fields[1]['field_label'],        'Field render type')
        self.assertEqual(head_fields[1]['field_placeholder'],  "(field render type)")
        self.assertEqual(head_fields[1]['field_property_uri'], "annal:field_render_type")
        self.assertEqual(head_fields[1]['field_render_type'],  "Enum_choice")
        self.assertEqual(head_fields[1]['field_value_mode'],   "Value_direct")
        self.assertEqual(head_fields[1]['field_target_type'],  "annal:Slug")
        self.assertEqual(head_fields[1]['field_placement'].field, "small-4 medium-3 columns")
        # 3rd field
        self.assertEqual(head_fields[2]['field_id'],           'Field_type')
        self.assertEqual(head_fields[2]['field_name'],         'Field_type')
        self.assertEqual(head_fields[2]['field_label'],        'Field value type')
        self.assertEqual(head_fields[2]['field_placeholder'],  "(field value type)")
        self.assertEqual(head_fields[2]['field_property_uri'], "annal:field_value_type")
        self.assertEqual(head_fields[2]['field_render_type'],  "Identifier")
        self.assertEqual(head_fields[2]['field_value_mode'],   "Value_direct")
        self.assertEqual(head_fields[2]['field_target_type'],  "annal:Identifier")
        self.assertEqual(head_fields[2]['field_placement'].field, "small-12 medium-3 columns show-for-medium-up")
        # 3th field
        self.assertEqual(head_fields[3]['field_id'],           'Entity_label')
        self.assertEqual(head_fields[3]['field_name'],         'Entity_label')
        self.assertEqual(head_fields[3]['field_label'],        'Label')
        self.assertEqual(head_fields[3]['field_placeholder'],  "(label)")
        self.assertEqual(head_fields[3]['field_property_uri'], "rdfs:label")
        self.assertEqual(head_fields[3]['field_render_type'],  "Text")
        self.assertEqual(head_fields[3]['field_value_mode'],   "Value_direct")
        self.assertEqual(head_fields[3]['field_target_type'],  "annal:Text")
        self.assertEqual(head_fields[3]['field_placement'].field, "small-4 medium-3 columns")
        # Entities
        entities = context_list_entities(r.context)
        entity_ids = [ context_list_item_field_value(r.context, e, 0) for e in entities ]
        #@@ self.assertIn('_initial_values', entity_ids)
        field_entities = (
            { ('Entity_id',         "EntityId",      "annal:Slug",          "Id")
            , ('Bib_address',       "Text",          "annal:Text",          "Address")
            , ('Bib_authors',       "RepeatGroup",   "bib:Authors",         "Author(s)")
            , ('Bib_booktitle',     "Text",          "annal:Text",          "Book title")
            , ('Entity_type',       "EntityTypeId",  "annal:Slug",          "Type")
            , ('Entity_label',      "Text",          "annal:Text",          "Label")
            , ('Field_comment',     "Markdown",      "annal:Richtext",      "Help")
            , ('Field_placement',   "Placement",     "annal:Placement",     "Position/size")
            , ('Field_type',        "Identifier",    "annal:Identifier",    "Field value type")
            , ('Field_render',      "Enum_choice",   "annal:Slug",          "Field render type")
            , ('Field_default',     "Text",          "annal:Text",          "Default")
            , ('Field_typeref',     "Enum_optional", "annal:Slug",          "Refer to type")
            , ('Field_restrict',    "Text",          "annal:Text",          "Value restriction")
            , ('List_comment',      "Markdown",      "annal:Richtext",      "Help")
            , ('List_default_type', "Enum_optional", "annal:Type",          "Record type")
            , ('List_default_view', "Enum_optional", "annal:View",          "View")
            , ('Type_label',        "Text",          "annal:Text",          "Label")
            , ('Type_comment',      "Markdown",      "annal:Richtext",      "Comment")
            , ('Type_uri',          "Identifier",    "annal:Identifier",    "URI")
            , ('List_choice',       "Enum_choice",   "annal:Slug",          "List view")
            , ('View_choice',       "View_choice",   "annal:Slug",          "Choose view")
            , ('Group_field_sel',   "Enum_optional", "annal:Slug",          "Field id")
            })
        for f in field_entities:
            for eid in range(len(entities)):
                item_fields = context_list_item_fields(r.context, entities[eid])
                if item_fields[0]['field_value'] == f[0]:
                    for fid in range(4):
                        item_field = item_fields[fid]
                        head_field = head_fields[fid]
                        for fkey in (
                                'field_id', 'field_name', 'field_label', 
                                'field_property_uri', 'field_render_type',
                                'field_placement', 'field_target_type'):
                            self.assertEqual(item_field[fkey], head_field[fkey])
                        self.assertEqual(item_field['field_value'], f[fid])
                    break
            else:
                self.fail("Field %s not found in context"%f[0])
        return

    def test_get_fields_list_no_continuation(self):
        u = entitydata_list_type_url(
            "testcoll", "_field", list_id="Field_list", scope="all"
            )
        r = self.client.get(u+"?foo=bar")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        cont = ""
        rowdata1 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="_field/Bib_address" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/_field/Bib_address/%(cont)s">Bib_address</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/Enum_render_type/Text/%(cont)s">Short text</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up"><span>annal:Text</span></div>
                  <div class="view-value small-4 medium-3 columns"><span>Address</span></div>
                </div>
              </div>
            </div>
            """%({'base': TestBasePath, 'cont': cont})
        # log.info("*** r.content: "+r.content)
        self.assertContains(r, rowdata1, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 4)
        return

    def test_get_fields_list_search(self):
        u = entitydata_list_type_url(
            "testcoll", "_field", list_id="Field_list", scope="all"
            ) + "?search=Bib_&continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        cont = uri_params({"continuation_url": u})
        cont = ""
        rowdata = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="_field/Bib_address" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/_field/Bib_address/%(cont)s">Bib_address</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns">
                    <a href="%(base)s/c/testcoll/d/Enum_render_type/Text/%(cont)s">Short text</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up"><span>annal:Text</span></div>
                  <div class="view-value small-4 medium-3 columns"><span>Address</span></div>
                </div>
              </div>
            </div>
            """%({'base': TestBasePath, 'cont': cont})
        # log.info(r.content)
        # If this test fails, check ordering of URI parameters
        self.assertContains(r, rowdata, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        self.assertEqual(r.context['search_for'],       "Bib_")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 4)
        self.assertEqual(head_fields[0]['field_id'], 'Entity_id')
        self.assertEqual(head_fields[1]['field_id'], 'Field_render')
        self.assertEqual(head_fields[2]['field_id'], 'Field_type')
        self.assertEqual(head_fields[3]['field_id'], 'Entity_label')
        # Entities
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 36)
        field_entities = (
            { ('Bib_address',       "Text",        "annal:Text",          "Address")
            , ('Bib_authors',       "RepeatGroup", "bib:Authors",         "Author(s)")
            , ('Bib_booktitle',     "Text",        "annal:Text",          "Book title")
            , ('Bib_chapter',       "Text",        "annal:Text",          "Chapter")
            , ('Bib_edition',       "Text",        "annal:Text",          "Edition")
            , ('Bib_editors',       "RepeatGroup", "bib:Editors",         "Editor(s)")
            , ('Bib_eprint',        "Text",        "annal:Text",          "Bib_eprint")
            , ('Bib_howpublished',  "Text",        "annal:Text",          "How published")
            , ('Bib_institution',   "Text",        "annal:Text",          "Institution")
            , ('Bib_journal',       "RepeatGroup", "bib:Journal",         "Journal")
            , ('Bib_month',         "Text",        "annal:Text",          "Month")
            , ('Bib_number',        "Text",        "annal:Text",          "Number")
            , ('Bib_organization',  "Text",        "annal:Text",          "Organization")
            , ('Bib_pages',         "Text",        "annal:Text",          "Pages")
            , ('Bib_publisher',     "Text",        "annal:Text",          "Publisher")
            , ('Bib_school',        "Text",        "annal:Text",          "School")
            , ('Bib_title',         "Text",        "annal:Text",          "Title")
            , ('Bib_type',          "Enum",        "annal:Slug",          "Type")
            , ('Bib_url',           "Text",        "annal:Text",          "URL")
            , ('Bib_volume',        "Text",        "annal:Text",          "Volume")
            , ('Bib_year',          "Text",        "annal:Text",          "Year")
            })
        for f in field_entities:
            for eid in range(len(entities)):
                item_fields = context_list_item_fields(r.context, entities[eid])
                if item_fields[0]['field_value'] == f[0]:
                    for fid in range(3):
                        item_field = item_fields[fid]
                        head_field = head_fields[fid]
                        for fkey in (
                                'field_id', 'field_name', 'field_label', 
                                'field_property_uri', 'field_render_type',
                                'field_placement', 'field_target_type'):
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
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        return

# End.
