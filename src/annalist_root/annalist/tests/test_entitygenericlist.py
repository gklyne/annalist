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

from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.util                  import extract_entity_id

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData
from annalist.models.entityfinder   import EntityFinder
from annalist.models.entitytypeinfo import EntityTypeInfo

from annalist.views.uri_builder             import uri_params, uri_with_params, continuation_params_url
from annalist.views.entitylist              import EntityGenericListView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_dir, collection_dir,
    entitydata_list_url_query,
    site_view_url,
    collection_view_url, collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user, create_user_permissions,
    context_view_field,
    # context_bind_fields
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value,
    check_field_list_context_fields,
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
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    get_site_entities, get_site_entities_sorted,  
    )
from entity_testlistdata    import recordlist_url

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
        self.list_ids = get_site_lists_linked("testcoll")
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

    def test_EntityDefaultListView(self):
        self.assertEqual(EntityGenericListView.__name__, "EntityGenericListView", "Check EntityGenericListView class name")
        return

    def test_enumerate_all_entities(self):
        # Test enumeration of all collection and site entities
        # Introduced to facilitate debugging of site data storage rework
        entity_list = (
            EntityFinder(self.testcoll, selector="ALL")
                .get_entities_sorted(type_id=None, altscope="all",
                    user_permissions=None, 
                    context={}, 
                    search=""
                    )
            )
        entity_types_ids = [ "%s/%s"%(e.get_type_id(), e.get_id()) for e in entity_list ]
        # log.debug("@@ entity_types_ids: \n"+"\n".join([repr(eti) for eti in entity_types_ids]))
        self.assertEqual(len(entity_types_ids), 173)    # Will change with site data
        expect_entities  = get_site_entities_sorted()
        expect_types_ids = [ fc.id for fc in expect_entities ]
        # log.debug("@@ entity_types_ids: \n"+"\n".join([ repr(eti) for eti in entity_types_ids[145:] ]))
        # log.debug("@@ expect_types_ids: \n"+"\n".join([ repr(eti) for eti in expect_types_ids[145:] ]))
        self.assertEqual(entity_types_ids, expect_types_ids)
        return

    def test_enumerate_value_modes(self):
        # Test enumeration of value modes (tests enumeration type listing)
        # Introduced to facilitate debugging of site data storage rework
        entity_list = (
            EntityFinder(self.testcoll, selector="ALL")
                .get_entities_sorted(type_id="_enum_value_mode", altscope="all",
                    user_permissions=None, 
                    context={}, 
                    search=""
                    )
            )
        # Enumerate enumeration types
        entity_types_ids = [ (e.get_type_id(), e.get_id()) for e in entity_list ]
        # log.info("@@ entity_types_ids: \n"+"\n".join([repr(eti) for eti in entity_types_ids]))
        self.assertEqual(len(entity_types_ids), 5)
        return

    def test_get_default_all_list(self):
        # List all entities in current collection
        u = entitydata_list_all_url("testcoll", list_id="Default_list_all") + "?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        list_label = "List entities with type information" 
        list_title = "List entities with type information - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        self.assertMatch(r.content, r'<input.type="hidden".name="continuation_url".+value="/xyzzy/"/>')
        # log.info(r.content) #@@
        cont = uri_params({"continuation_url": u})
        #@@ cont = ""
        tooltip1 = "" # 'title="%s"'%r.context['fields'][0]['field_help']
        tooltip2 = "" # 'title="%s"'%r.context['fields'][1]['field_help']
        tooltip3 = "" # 'title="%s"'%r.context['fields'][2]['field_help']
        rowdata = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="testtype/entity1" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/testtype/entity1/%(cont)s">entity1</a>
                  </div>
                  <div class="view-value small-2 columns" %(tooltip2)s>
                    <a href="/testsite/c/testcoll/d/_type/testtype/%(cont)s">RecordType testcoll/testtype</a>
                  </div>
                  <div class="view-value small-7 columns" %(tooltip3)s>
                    <span>Entity testcoll/testtype/entity1</span>
                  </div>
                </div>
              </div>
            </div>
            """%(
                { 'base':     TestBasePath
                , 'cont':     cont
                , 'tooltip1': tooltip1
                , 'tooltip2': tooltip2
                , 'tooltip3': tooltip3
                }
            )
        # log.info(r.content)
        # log.info(r.context["fields"])
        # log.info(r.context["List_rows"])
        self.assertContains(r, rowdata, html=True)
        # Test context
        self.assertEqual(r.context['title'],            list_title)
        self.assertEqual(r.context['heading'],          list_label)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "Default_type")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list_all")
        # Unbound field descriptions
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 3 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 3)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        f2 = context_view_field(r.context, 0, 2)
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f1['field_id'], 'Entity_type')
        self.assertEqual(f2['field_id'], 'Entity_label')
        # Entities and bound fields
        # log.info(entities)  #@@
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 6)
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
            item_fields = context_list_item_fields(r.context, entities[eid])
            for fid in range(3):
                item_field = item_fields[fid]
                head_field = head_fields[0]['row_field_descs'][fid]
                # Check that row field descriptions match corresponding heading feld descriptions
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_type',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field[fkey], head_field[fkey])
                # Check row field values
                fkey = field_keys[fid]
                self.assertEqual(item_field['field_value'],    entity_fields[eid][fkey])
                self.assertEqual(item_field['entity_type_id'], entity_fields[eid]['entity_type_id'])
        return

    def test_get_default_all_scope_all_list(self):
        # List all entities in current collection and site-wiude
        # This repeats parts of the previous test but with scope='all'
        u = entitydata_list_all_url(
            "testcoll", list_id="Default_list_all", 
            scope="all", continuation_url="/xyzzy/"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        list_label = "List entities with type information" 
        list_title = "List entities with type information - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        # Test context
        self.assertEqual(r.context['title'],            list_title)
        self.assertEqual(r.context['heading'],          list_label)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "Default_type")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list_all")
        # Unbound field descriptions
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 3 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 3)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        f2 = context_view_field(r.context, 0, 2)
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f1['field_id'], 'Entity_type')
        self.assertEqual(f2['field_id'], 'Entity_label')
        # Entities and bound fields
        entities = context_list_entities(r.context)
        # listed_entities = { e['entity_id']: e for e in entities }
        # for eid in listed_entities:
        #     print "@@ eid %s"%(eid)
        self.assertEqual(len(entities), 170)    # Will change with site data
        return

    def test_get_types_list(self):
        # List types in current collection
        u = entitydata_list_type_url(
            "testcoll", "_type", list_id="Type_list", scope=None
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content) #@@
        list_label = "Entity types" 
        list_title = "Entity types - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        # Test context
        self.assertEqual(r.context['title'],            list_title)
        self.assertEqual(r.context['heading'],          list_label)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 2 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 2)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        # 1st field
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f0['field_name'], 'entity_id')
        # 2nd field
        self.assertEqual(f1['field_id'], 'Entity_label')
        self.assertEqual(f1['field_name'], 'Entity_label')
        # Entities
        entities   = context_list_entities(r.context)
        listed_entities = { e['entity_id']: e for e in entities }
        # self.assertIn('_initial_values', listed_entities)
        type_entities = {"testtype", "testtype2"}
        self.assertEqual(set(listed_entities.keys()), type_entities)
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
        list_label = "Entity types" 
        list_title = "Entity types - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        # Test context
        self.assertEqual(r.context['title'],            list_title)
        self.assertEqual(r.context['heading'],          list_label)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 2 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 2)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)

        # 1st field
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f0['field_name'], 'entity_id')
        # 2nd field
        self.assertEqual(f1['field_id'], 'Entity_label')
        self.assertEqual(f1['field_name'], 'Entity_label')
        # Entities
        entities   = context_list_entities(r.context)
        listed_entities = { e['entity_id']: e for e in entities }
        #@@ self.assertIn('_initial_values', listed_entities)
        type_entities = get_site_types() | {"testtype", "testtype2"}
        self.assertEqual(set(listed_entities.keys()), type_entities)
        return

    def test_get_fields_list(self):
        # List fields in current collection
        u = entitydata_list_type_url(
            "testcoll", layout.FIELD_TYPEID, list_id="Field_list", 
            scope="all",
            continuation_url="/xyzzy/"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content) #@@
        list_label = "Field definitions" 
        list_title = "Field definitions - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        # Test context
        self.assertEqual(r.context['title'],            list_title)
        self.assertEqual(r.context['heading'],          list_label)
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        field_entities = (
            { ('Entity_id',         "EntityId",        "annal:EntityRef",  "Id")
            , ('Coll_comment',      "Markdown",        "annal:Richtext",   "Collection metadata")
            , ('Coll_parent',       "Enum_choice_opt", "annal:EntityRef",  "Parent")
            , ('Coll_software_version', "Showtext",    "annal:Text",       "S/W version")
            , ('Entity_type',       "EntityTypeId",    "annal:EntityRef",  "Type")
            , ('Entity_label',      "Text",            "annal:Text",       "Label")
            , ('Field_comment',     "Textarea",        "annal:Longtext",   "Help")
            , ('Field_placement',   "Placement",       "annal:Placement",  "Position/size")
            , ('Field_render_type', "Enum_choice",     "annal:EntityRef",  "Render type")
            , ('Field_value_mode',  "Enum_choice",     "annal:EntityRef",  "Value mode")
            , ('Field_value_type',  "Identifier",      "annal:Identifier", "Value type")
            , ('Field_entity_type', "Identifier",      "annal:Identifier", "Entity type")
            , ('Field_default',     "Text",            "annal:Text",       "Default")
            , ('Field_typeref',     "Enum_optional",   "annal:EntityRef",  "Refer to type")
            , ('Field_restrict',    "Text",            "annal:Text",       "Value restriction")
            , ('List_comment',      "Markdown",        "annal:Richtext",   "Help")
            , ('List_default_type', "Enum_optional",   "annal:Type",       "Default type")
            , ('List_default_view', "Enum_optional",   "annal:View",       "Default view")
            , ('Type_label',        "Text",            "annal:Text",       "Label")
            , ('Type_comment',      "Markdown",        "annal:Richtext",   "Comment")
            , ('Type_uri',          "Identifier",      "annal:Identifier", "Type URI")
            , ('List_choice',       "Enum_choice",     "annal:EntityRef",  "List view")
            , ('View_choice',       "View_choice",     "annal:EntityRef",  "Choose view")
            , ('Group_field_sel',   "Enum_optional",   "annal:EntityRef",  "Field id")
            })
        check_field_list_context_fields(self, r, field_entities)
        return

    def test_get_fields_list_no_continuation(self):
        u = entitydata_list_type_url(
            "testcoll", layout.FIELD_TYPEID, list_id="Field_list", scope="all",
            query_params={"foo": "bar"}
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        list_label = "Field definitions" 
        list_title = "Field definitions - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        curi = continuation_params_url(u)
        field_params = (
            { 'base':           TestBasePath
            , 'cont':           uri_params({"continuation_url": curi})
            , 'tooltip1':       "" # 'title="%s"'%r.context['fields'][0]['field_help']
            , 'tooltip2':       "" # 'title="%s"'%r.context['fields'][1]['field_help']
            , 'tooltip3':       "" # 'title="%s"'%r.context['fields'][2]['field_help']
            , 'tooltip4':       "" # 'title="%s"'%r.context['fields'][3]['field_help']
            , 'field_typeid':   layout.FIELD_TYPEID
            })
        rowdata1 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="%(field_typeid)s/Coll_comment" />
              </div>
              <div class="small-11 columns">
                <div class="view-listrow row">
                  <div class="view-value small-4 medium-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/%(field_typeid)s/Coll_comment/%(cont)s">Coll_comment</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip2)s>
                    <a href="%(base)s/c/testcoll/d/_enum_render_type/Markdown/%(cont)s">
                      Markdown rich text
                    </a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up" %(tooltip3)s>
                    <span>annal:Richtext</span>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip4)s>
                    <span>Collection metadata</span>
                  </div>
                </div>
              </div>
            </div>
            """%field_params
        rowdata2 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="%(field_typeid)s/Coll_parent" />
              </div>
              <div class="small-11 columns">
                <div class="view-listrow row">
                  <div class="view-value small-4 medium-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/%(field_typeid)s/Coll_parent/%(cont)s">Coll_parent</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip2)s>
                    <a href="%(base)s/c/testcoll/d/_enum_render_type/Enum_choice_opt/%(cont)s">Optional entity choice</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up" %(tooltip3)s>
                    <span>annal:EntityRef</span>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip4)s>
                    <span>Parent</span>
                  </div>
                </div>
              </div>
            </div>
            """%field_params
        rowdata3 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="%(field_typeid)s/Coll_software_version" />
              </div>
              <div class="small-11 columns">
                <div class="view-listrow row">
                  <div class="view-value small-4 medium-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/%(field_typeid)s/Coll_software_version/%(cont)s">Coll_software_version</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip2)s>
                    <a href="%(base)s/c/testcoll/d/_enum_render_type/Showtext/%(cont)s">Display text</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up" %(tooltip3)s>
                    <span>annal:Text</span>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip4)s>
                    <span>S/W version</span>
                  </div>
                </div>
              </div>
            </div>
            """%field_params
        # log.info("*** r.content: "+r.content) #@@
        self.assertContains(r, rowdata1, html=True)
        self.assertContains(r, rowdata2, html=True)
        self.assertContains(r, rowdata3, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['continuation_url'], "")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 4 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 4)
        return

    def test_get_fields_list_search(self):
        u = entitydata_list_type_url(
            "testcoll", layout.FIELD_TYPEID, list_id="Field_list", scope="all",
            continuation_url="/xyzzy/",
            query_params={"search": "Coll_"}
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        list_label = "Field definitions" 
        list_title = "Field definitions - Collection testcoll"
        self.assertContains(r, "<title>%s</title>"%list_title, html=True)
        self.assertContains(r, '<h2 class="page-heading">%s</h2>'%list_label, html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        self.assertEqual(r.context['search_for'],       "Coll_")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 4 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 4)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        f2 = context_view_field(r.context, 0, 2)
        f3 = context_view_field(r.context, 0, 3)
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f1['field_id'], 'Field_render_type')
        self.assertEqual(f2['field_id'], 'Field_value_type')
        self.assertEqual(f3['field_id'], 'Entity_label')
        # Entities
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 7)
        field_entities = (
            { ( "Coll_comment",             "Markdown",        "annal:Richtext",  "Collection metadata" )
            , ( "Coll_default_list_id",     "Showtext",        "annal:Text",      "Default list"        )
            , ( "Coll_default_view_entity", "Showtext",        "annal:Text",      "Default view entity" )
            , ( "Coll_default_view_id",     "Showtext",        "annal:Text",      "Default view"        )
            , ( "Coll_default_view_type",   "Showtext",        "annal:Text",      "Default view type"   )
            , ( "Coll_parent",              "Enum_choice_opt", "annal:EntityRef", "Parent"              )
            , ( "Coll_software_version",    "Showtext",        "annal:Text",      "S/W version"         )
            })
        check_field_list_context_fields(self, r, field_entities)
        return

    def test_get_list_select_by_type(self):
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id=None)
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        return

    def test_get_list_no_collection(self):
        u = entitydata_list_type_url("no_collection", layout.FIELD_TYPEID, list_id="Field_list")
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
        self.assertContains(r, 
            "Record type no_type in collection testcoll does not exist", 
            status_code=404
            )
        return

    def test_get_list_no_list(self):
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="no_list")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, 
            "Record list no_list in collection testcoll does not exist", 
            status_code=404
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new --------

    def test_post_new_type_entity(self):
        f = entitylist_form_data("new", list_id="Field_list")
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_all_entity(self):
        # Also tests continuation_url parameter handling
        #@@ s = site_view_url()
        s = collection_view_url(coll_id="testcoll")
        f = entitylist_form_data("new", list_id="Field_list", continuation_url=s)
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view"
            )
        c = continuation_url_param(u, continuation_url_param(s))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_one(self):
        f = entitylist_form_data(
            "new", list_id="Field_list", 
            entities=[layout.FIELD_TYPEID+"/field1"]
            )
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "new", "testcoll", layout.FIELD_TYPEID, view_id="Field_view"
            )
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_new_type_entity_select_many(self):
        f = entitylist_form_data(
            "new", list_id="Field_list", 
            entities=[layout.FIELD_TYPEID+"/field1", "testtype/entity1", "testtype/entity2"]
            )
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
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
        f = entitylist_form_data("copy", entities=[layout.FIELD_TYPEID+"/field1"], continuation_url=s)
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("copy", "testcoll", layout.FIELD_TYPEID, "field1", view_id="Field_view")
        c = continuation_url_param(u, continuation_url_param(s))
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_all_entity(self):
        f = entitylist_form_data("copy", entities=[layout.FIELD_TYPEID+"/field1"])
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "copy", "testcoll", layout.FIELD_TYPEID, "field1", view_id="Field_view"
            )
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_other(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "copy", "testcoll", "testtype", "entity1", view_id="Field_view"
            )
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_copy_type_entity_select_none(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
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
        f = entitylist_form_data(
            "copy", 
            entities=[layout.FIELD_TYPEID+"/field1", "testtype/entity1", "testtype/entity2"]
            )
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
        f = entitylist_form_data("copy", entities=[layout.FIELD_TYPEID+"/field1"])
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit --------

    def test_post_edit_type_entity(self):
        f = entitylist_form_data("edit", entities=[layout.FIELD_TYPEID+"/field1"])
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c = continuation_url_param(u)
        v = TestHostUri + entitydata_edit_url(
            "edit", "testcoll", layout.FIELD_TYPEID, "field1", view_id="Field_view"
            )
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_all_entity(self):
        f = entitylist_form_data("edit", entities=[layout.FIELD_TYPEID+"/field1"])
        u = entitydata_list_all_url("testcoll", list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "edit", "testcoll", layout.FIELD_TYPEID, "field1", view_id="Field_view"
            )
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        return

    def test_post_edit_type_entity_select_none(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_select_many(self):
        f = entitylist_form_data(
            "edit", 
            entities=[layout.FIELD_TYPEID+"/field1", "testtype/entity1", "testtype/entity2"]
            )
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + u + "?error_head=Problem%20with%20input&error_message="
        self.assertIn(e, r['location'])
        return

    def test_post_edit_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("edit", entities=[layout.FIELD_TYPEID+"/field1"])
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
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
        f = entitylist_form_data("delete", entities=[layout.FIELD_TYPEID+"/Field_comment"])
        u = entitydata_list_type_url("testcoll", layout.FIELD_TYPEID, list_id="Field_list")
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
        v = TestHostUri + collection_view_url(coll_id="testcoll")
        self.assertEqual(v, r['location'])
        return

    def test_post_view_list(self):
        # 'View' button on list view: change displayed list
        f = entitylist_form_data("list_type", list_id="View_list")
        u = entitydata_list_type_url("testcoll", "_type", list_id="Type_list")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url("testcoll", "_type", list_id="View_list")
        self.assertIn(v, r['location'])
        self.assertNotIn("continuation_url", r['location'])
        return

    def test_post_view_all_list(self):
        # 'View' button on list view: change displayed list
        f = entitylist_form_data("list_type", list_scope_all="all", list_id="View_list")
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
        f = entitylist_form_data("list_type", search="search&term", continuation_url="/xyzxy/")
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url(
            "testcoll", "testtype", list_id="Default_list"
            )
        c = continuation_url_param("/xyzxy/")
        s = "search=search%26term"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(s, r['location'])
        # Note: Search rendering tested by test_get_fields_list_search above
        return

    def test_post_view_all_search(self):
        # Redisplay list with entries matching search string
        f = entitylist_form_data(
            "list_type", list_scope_all="all", 
            search="search&term", 
            continuation_url="/xyzxy/"
            )
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_list_type_url(
            "testcoll", "testtype", list_id="Default_list"
            )
        c = continuation_url_param("/xyzxy/")
        s = "search=search%26term"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(s, r['location'])
        # Note: Search rendering tested by test_get_fields_list_search above
        return

    def test_post_view_no_type(self):
        # Redisplay list with entries matching search string
        f = entitylist_form_data("list_all", list_id="Type_list")
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
