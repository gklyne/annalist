"""
Tests for EntityData list view with additional inherited bibliography data
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

from annalist.views.uri_builder             import uri_params, uri_with_params, continuation_params_url
from annalist.views.entitylist              import EntityGenericListView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site,
    init_annalist_test_coll,
    install_annalist_named_coll,
    create_test_coll_inheriting,
    init_annalist_named_test_coll,
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
    context_view_field,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value,
    check_context_field, check_context_field_value, check_context_list_field_value,
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
    get_site_bib_types, get_site_bib_types_sorted, get_site_bib_types_linked,
    get_site_bib_lists, get_site_bib_lists_sorted, get_site_bib_lists_linked,
    get_site_schema_types, get_site_schema_types_sorted, get_site_schema_types_linked,
    get_site_schema_lists, get_site_schema_lists_sorted, get_site_schema_lists_linked,
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
        self.testsite  = init_annalist_test_site()
        self.testcoll  = init_annalist_named_test_coll(layout.BIBDATA_ID)
        self.testdata  = RecordTypeData.load(self.testcoll, "testtype")
        self.testtype2 = RecordType.create(
            self.testcoll, "testtype2", recordtype_create_values("testcoll", "testtype2")
            )
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
        resetSitedata()
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
            "testcoll", list_id="Default_list_all", 
            scope="all",
            continuation_url="/xyzzy/"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "Collection testcoll")
        self.assertContains(r, '<h2 class="page-heading">List entities with type information</h2>', html=True)
        # Test context
        self.assertEqual(r.context['title'],            "List entities with type information - Collection testcoll")
        self.assertEqual(r.context['heading'],          "List entities with type information")
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
        if len(entities) != 213:
            for e in entities:
                log.debug("All entities: %s/%s"%(e['annal:type_id'], e['annal:id']))
        self.assertEqual(len(entities), 230)    # Will change with site data
        return

    def test_get_types_scope_all_list(self):
        # List types in current collection and site-wide
        u = entitydata_list_type_url(
            "testcoll", "_type", list_id="Type_list", scope="all"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['title'],            "Entity types - Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 2 cols..
        self.assertEqual(len(head_fields[0]['row_field_descs']), 2)
        # 1st field
        f0 = context_view_field(r.context, 0, 0)
        self.assertEqual(f0['field_id'], 'Entity_id')
        self.assertEqual(f0['field_name'], 'entity_id')
        # 2nd field
        f1 = context_view_field(r.context, 0, 1)
        self.assertEqual(f1['field_id'], 'Entity_label')
        self.assertEqual(f1['field_name'], 'Entity_label')
        # Entities
        entities   = context_list_entities(r.context)
        listed_entities = { e['entity_id']: e for e in entities }
        type_entities = get_site_bib_types() | {"testtype", "testtype2"}
        self.assertEqual(set(listed_entities.keys()), type_entities)
        return

    def test_get_fields_list(self):
        # List fields in current collection
        u = entitydata_list_type_url(
            "testcoll", layout.FIELD_TYPEID, list_id="Field_list", scope="all",
            continuation_url="/xyzzy/"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['title'],            "Field definitions - Collection testcoll")
        self.assertEqual(r.context['heading'],          "Field definitions")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Field_list")
        # Fields
        field_entities = (
            { ('Entity_id',         "EntityId",      "annal:EntityRef",     "Id")
            , ('Bib_address',       "Text",          "annal:Text",          "Address")
            , ('Bib_authors',       "Group_Seq",     "bib:Authors",         "Author(s)")
            , ('Bib_booktitle',     "Text",          "annal:Text",          "Book title")
            , ('Entity_type',       "EntityTypeId",  "annal:EntityRef",     "Type")
            , ('Entity_label',      "Text",          "annal:Text",          "Label")
            , ('Field_comment',     "Textarea",      "annal:Longtext",      "Help")
            , ('Field_placement',   "Placement",     "annal:Placement",     "Position/size")
            , ('Field_render_type', "Enum_choice",   "annal:EntityRef",     "Render type")
            , ('Field_value_mode',  "Enum_choice",   "annal:EntityRef",     "Value mode")
            , ('Field_value_type',  "Identifier",    "annal:Identifier",    "Value type")
            , ('Field_entity_type', "Identifier",    "annal:Identifier",    "Entity type")
            , ('Field_default',     "Text",          "annal:Text",          "Default")
            , ('Field_typeref',     "Enum_optional", "annal:EntityRef",     "Refer to type")
            , ('Field_restrict',    "Text",          "annal:Text",          "Value restriction")
            , ('List_comment',      "Markdown",      "annal:Richtext",      "Help")
            , ('List_default_type', "Enum_optional", "annal:Type",          "Default type")
            , ('List_default_view', "Enum_optional", "annal:View",          "Default view")
            , ('List_target_type',  "Identifier",    "annal:Identifier",    "List entity type")
            , ('Type_label',        "Text",          "annal:Text",          "Label")
            , ('Type_comment',      "Markdown",      "annal:Richtext",      "Comment")
            , ('Type_uri',          "Identifier",    "annal:Identifier",    "Type URI")
            , ('List_choice',       "Enum_choice",   "annal:EntityRef",     "List view")
            , ('View_choice',       "View_choice",   "annal:EntityRef",     "Choose view")
            , ('Group_field_sel',   "Enum_optional", "annal:EntityRef",     "Field id")
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
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        curi     = continuation_params_url(u)
        cont     = uri_params({"continuation_url": curi})
        tooltip1 = ""
        tooltip2 = ""
        tooltip3 = ""
        tooltip4 = ""
        rowdata1 = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="%(field_typeid)s/Bib_address" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-4 medium-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/%(field_typeid)s/Bib_address/%(cont)s">Bib_address</a>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip2)s>
                    <a href="%(base)s/c/testcoll/d/_enum_render_type/Text/%(cont)s">Short text</a>
                  </div>
                  <div class="view-value small-12 medium-3 columns show-for-medium-up" %(tooltip3)s>
                    <span>annal:Text</span>
                  </div>
                  <div class="view-value small-4 medium-3 columns" %(tooltip4)s>
                    <span>Address</span>
                  </div>
                </div>
              </div>
            </div>
            """%(
                { 'base':           TestBasePath
                , 'cont':           cont
                , 'tooltip1':       tooltip1
                , 'tooltip2':       tooltip2
                , 'tooltip3':       tooltip3
                , 'tooltip4':       tooltip4
                , 'field_typeid':   layout.FIELD_TYPEID
                }
            )
        # log.info("*** r.content: "+r.content)
        self.assertContains(r, rowdata1, html=True)
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
            query_params={"search": "Bib_"}
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # self.assertContains(r, site_title("<title>%s</title>"))
        # self.assertContains(r, "<h3>List 'Field_list' of entities in collection 'testcoll'</h3>", html=True)
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.FIELD_TYPEID)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        self.assertEqual(r.context['search_for'],       "Bib_")
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
        self.assertEqual(len(entities), 36)
        field_entities = (
            { ('Bib_address',       "Text",        "annal:Text",          "Address")
            , ('Bib_authors',       "Group_Seq",   "bib:Authors",         "Author(s)")
            , ('Bib_booktitle',     "Text",        "annal:Text",          "Book title")
            , ('Bib_chapter',       "Text",        "annal:Text",          "Chapter")
            , ('Bib_edition',       "Text",        "annal:Text",          "Edition")
            , ('Bib_editors',       "Group_Seq",   "bib:Editors",         "Editor(s)")
            , ('Bib_eprint',        "Text",        "annal:Text",          "Bib_eprint")
            , ('Bib_howpublished',  "Text",        "annal:Text",          "How published")
            , ('Bib_institution',   "Text",        "annal:Text",          "Institution")
            , ('Bib_journal',       "Group_Seq",   "bib:Journal",         "Journal")
            , ('Bib_month',         "Text",        "annal:Text",          "Month")
            , ('Bib_number',        "Text",        "annal:Text",          "Number")
            , ('Bib_organization',  "Text",        "annal:Text",          "Organization")
            , ('Bib_pages',         "Text",        "annal:Text",          "Pages")
            , ('Bib_publisher',     "Text",        "annal:Text",          "Publisher")
            , ('Bib_school',        "Text",        "annal:Text",          "School")
            , ('Bib_title',         "Text",        "annal:Text",          "Title")
            , ('Bib_type',          "Enum",        "annal:EntityRef",     "Type")
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
                        head_field = head_fields[0]['row_field_descs'][fid]
                        for fkey in (
                                'field_id', 'field_name', 'field_label', 
                                'field_property_uri', 'field_render_type',
                                'field_placement', 'field_value_type'):
                            self.assertEqual(item_field[fkey], head_field[fkey])
                        check_context_list_field_value(self, item_field, f[fid])
                    break
            else:
                self.fail("Field %s not found in context"%f[0])
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

    def test_collection_alt_parents(self):
        rdf_coll = install_annalist_named_coll("RDF_schema_defs")
        ann_coll = install_annalist_named_coll("Annalist_schema")
        testcoll = create_test_coll_inheriting("Annalist_schema")
        rdf_coll_alts = [ p.get_id() for p in rdf_coll.get_alt_entities(altscope="all") if p ]
        self.assertEqual(rdf_coll_alts, ["RDF_schema_defs", "_annalist_site"])
        ann_coll_alts = [ p.get_id() for p in ann_coll.get_alt_entities(altscope="all") if p ]
        self.assertEqual(ann_coll_alts, ["Annalist_schema", "RDF_schema_defs", "_annalist_site"])
        testcoll_alts = [ p.get_id() for p in testcoll.get_alt_entities(altscope="all") if p ]
        self.assertEqual(testcoll_alts, ["testcoll", "Annalist_schema", "RDF_schema_defs", "_annalist_site"])
        return

    def test_get_list_inherited_entities(self):
        rdf_coll = install_annalist_named_coll("RDF_schema_defs")
        ann_coll = install_annalist_named_coll("Annalist_schema")
        testcoll = create_test_coll_inheriting("Annalist_schema")
        schema_list_ids = get_site_schema_lists_linked("testcoll")
        u = entitydata_list_type_url("testcoll", "Class", list_id=None, scope="all")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "Class")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(schema_list_ids))
        self.assertEqual(list_choices['field_value'],   "Classes")
        # Entities
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 27)
        field_entities = (
            { ('Audio',         'Class',    'Audio clip'                     )
            , ('Collection',    'Class',    'Data collection'                )
            , ('Default_type',  'Class',    'Default type'                   )
            , ('Entity',        'Class',    'Entity'                         )
            , ('EntityData',    'Class',    'EntityData'                     )
            , ('EntityRoot',    'Class',    'Root entity'                    )
            , ('Enum',          'Class',    'Enumerated type'                )
            , ('Field',         'Class',    'Field definition'               )
            , ('Field_group',   'Class',    'Field group'                    )
            , ('Image',         'Class',    'Image'                          )
            , ('List',          'Class',    'List definition'                )
            , ('Resource',      'Class',    'Resource'                       )
            , ('Site',          'Class',    'Annalist site'                  )
            , ('SiteData',      'Class',    'Site data'                      )
            , ('Type',          'Class',    'Type definition'                )
            , ('Type_Data',     'Class',    'Type data'                      )
            , ('Unknown_type',  'Class',    'Unknown type'                   )
            , ('User',          'Class',    'User permissions'               )
            , ('View',          'Class',    'View definition'                )
            , ('Vocabulary',    'Class',    'Vocabulary namespace definition')
            , ('Boolean',       'Datatype', 'Boolean'                        )
            , ('EntityRef',     'Datatype', 'Local entity reference'         )
            , ('Identifier',    'Datatype', 'Identifier'                     )
            , ('Longtext',      'Datatype', 'Multiline text'                 )
            , ('Placement',     'Datatype', 'Field placement'                )
            , ('Richtext',      'Datatype', 'Rich text'                      )
            , ('Text',          'Datatype', 'Text'                           )
            })
        for f in field_entities:
            for eid in range(len(entities)):
                item_fields = context_list_item_fields(r.context, entities[eid])
                if item_fields[0]['field_value'] == f[0]:
                    for fid in range(3):
                        item_field = item_fields[fid]
                        check_context_list_field_value(self, item_field, f[fid])
                    break
            else:
                self.fail("Field %s not found in context"%f[0])
        return

# End.
