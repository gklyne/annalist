"""
Tests for site data.

This module contains tests that are intended to test the validity, 
completeness and consistency of Annalist-defined site-wide data.
It assumes that other test modules confirm operation of the 
underlying web site server code.

The general pattern of these tests is to render a web page and then to 
Check that the rendered page contains appropriate contents as defined 
by the Annalist site data.

A key reason for this module's existence is to catch any regressions in the
presentation of views that have been manually checked for correctness that 
may be caused by changes to the underlying site data structures.
It is not intended to check details of web page presentation.

(The first couple of tests also check aspects of the test site data setup.)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.contrib.auth.models import User
from django.test                import TestCase
from django.test.client         import Client

from bs4                        import BeautifulSoup

from annalist.identifiers                   import RDF, RDFS, ANNAL
from annalist.models.site                   import Site
from annalist.models.collection             import Collection
from annalist.models.recordtype             import RecordType
from annalist.models.recordlist             import RecordList
from annalist.models.recordview             import RecordView
from annalist.models.recordgroup            import RecordGroup
from annalist.models.recordfield            import RecordField

from annalist.views.fields.render_placement import get_placement_options

from AnnalistTestCase           import AnnalistTestCase
from tests                      import dict_to_str, init_annalist_test_site
from tests                      import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils           import (
    site_view_url,
    collection_view_url,
    collection_edit_url,
    collection_entity_list_url,
    collection_entity_view_url,
    collection_entity_edit_url,
    create_user_permissions, create_test_user
    )
from entity_testsitedata        import (
    get_site_types, get_site_types_sorted,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_view_fields, get_site_view_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   Site data tests
#
#   -----------------------------------------------------------------------------

class AnnalistSiteDataTest(AnnalistTestCase):
    """
    Tests for Annalist site data completeness and consistency
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.coll1     = Collection.load(self.testsite, "coll1")
        self.types_expected = get_site_types_sorted() + ["type1", "type2"]
        self.lists_expected = get_site_lists_sorted() + ['list1', 'list2']
        self.views_expected = get_site_views_sorted() + ["view1", "view2"]
        self.list_types_expected   = ["Grid", "List"]
        self.render_types_expected = get_site_field_types_sorted()
        self.grouprefs_expected    = get_site_field_groups_sorted()
        self.placements_expected   = get_placement_options()

        # Login with admin permissions
        permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        create_test_user(
            self.coll1, 
            "testuser", "testpass", user_permissions=permissions
            )
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpass")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    # --------------------------------------------------------------------------
    # Helper functions
    # --------------------------------------------------------------------------

    # Dereference URI and return BeautifulSoup object for the returned HTML
    def get_page(self, uri):
        r = self.client.get(uri)
        if r.status_code == 302:
            r = self.client.get(r['location'])
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        s = BeautifulSoup(r.content)
        return s

    # Test named input has specified type and value
    def check_input_type_value(self, 
            s, name, 
            input_type, input_value=None, input_text=None):
        tag_name = "input"
        tag_type = input_type
        if input_type == "textarea":
            tag_name = "textarea"
            tag_type = None
        input_elem = s.form.find(attrs={"name": name})
        self.assertEqual(input_elem.name, tag_name)
        if tag_type:
            self.assertEqual(input_elem['type'], tag_type)
        if input_value is not None:
            self.assertEqual(input_elem['value'], input_value)
        if input_text is not None:
            self.assertEqual(input_elem.string, input_text)
        return

    # Convert selected Unicode characters to HTMLentity form (undoing changes wrought by BeautifulSoup)
    @staticmethod
    def html_encode(s):
        # See: http://stackoverflow.com/a/1919221/324122
        entity_map = (
            { u'\u2588': u"&block;"
            , u'\u2591': u"&blk14;"
            })
        for u, e in entity_map.iteritems():
            s = s.replace(u, e)
        return s

    # Test named input is <select> with specified options and selected value
    def check_select_field(self, s, name, options, selection):
        select_elem  = s.find("select", attrs={"name": name})
        options_here = [self.html_encode(o.string) for o in select_elem.find_all("option")]
        if options_here != options:
            log.info("options_here: %r"%(options_here,))
            log.info("options:      %r"%(options,))
        self.assertEqual(options_here, options)
        if selection is not None:
            self.assertEqual(
                select_elem.find("option", selected=True).string, 
                selection
                )
        return

    def check_row_column(self, row_data, colnum, row_expected):
        if row_expected[colnum] is not None:
            e = row_expected[colnum]
            f = (row_data
                    .find("div", class_="row")
                    .find_all("div", class_="columns")[colnum]
                    .stripped_strings.next()
                )
            self.assertEqual(e, f, "%s != %s (%r)"%(e, f, row_expected))
        return

    def check_list_row_data(self, s, trows_expected):
        trows = s.form.find_all("div", class_="tbody")
        self.assertEqual(len(trows), len(trows_expected))
        for i in range(len(trows_expected)):
            e = trows_expected[i]   # expected
            f = trows[i]            # found
            # <input class="select-box right" name="entity_select" type="checkbox" value="_list/list1"/>
            self.assertEqual(e[0], f.find("input", class_="select-box")["value"])
            for j in range(len(trows_expected[i][1])):
                self.check_row_column(trows[i], j, trows_expected[i][1])
        return

    def check_view_fields(self, s, expect_fields, expect_field_choices):
        trows = s.find_all("div", class_="select-row")
        self.assertEqual(len(trows), len(expect_fields))
        for i in range(len(trows)):
            tcols = trows[i].select("div.columns div.row div.columns")
            self.assertEqual(trows[i].div.input['type'],  "checkbox")
            self.assertEqual(trows[i].div.input['name'],  "View_fields__select_fields")
            self.assertEqual(trows[i].div.input['value'], str(i))
            self.check_select_field(
                tcols[0], "View_fields__%d__Field_id"%i, 
                expect_field_choices, expect_fields[i]
                )
        return

    # Test consistency of type / list / view / field descriptions
    def check_type_list_view(self, type_id, list_id, view_id, type_uri):
        # Read type description - check required fields are present
        type_type = RecordType.load(self.coll1, type_id, self.testsite)
        self.assertEqual(type_type["@type"],                [ANNAL.CURIE.Type])
        self.assertEqual(type_type[ANNAL.CURIE.id],         type_id)
        self.assertEqual(type_type[ANNAL.CURIE.type_id],    "_type")
        self.assertEqual(type_type[ANNAL.CURIE.uri],        type_uri)
        self.assertEqual(type_type[ANNAL.CURIE.type_list],  list_id)
        self.assertEqual(type_type[ANNAL.CURIE.type_view],  view_id)
        # Read type list description
        type_list = RecordList.load(self.coll1, list_id, self.testsite)
        self.assertEqual(type_list["@type"],                    [ANNAL.CURIE.List])
        self.assertEqual(type_list[ANNAL.CURIE.id],             list_id)
        self.assertEqual(type_list[ANNAL.CURIE.type_id],        "_list")
        self.assertEqual(type_list[ANNAL.CURIE.display_type],   "List")
        self.assertEqual(type_list[ANNAL.CURIE.default_type],   type_id)
        self.assertEqual(type_list[ANNAL.CURIE.default_view],   view_id)
        self.assertEqual(type_list[ANNAL.CURIE.record_type],    type_uri)
        self.assertIn(ANNAL.CURIE.list_entity_selector,         type_list)
        # Read type view description
        type_view = RecordView.load(self.coll1, view_id, self.testsite)
        self.assertEqual(type_view["@type"],                    [ANNAL.CURIE.View])
        self.assertEqual(type_view[ANNAL.CURIE.id],             view_id)
        self.assertEqual(type_view[ANNAL.CURIE.type_id],        "_view")
        self.assertEqual(type_view[ANNAL.CURIE.record_type],    type_uri)
        self.assertIn(ANNAL.CURIE.open_view,                    type_view)
        # Read and check fields used in list and view displays
        self.check_type_fields(type_id, type_uri, type_list[ANNAL.CURIE.list_fields])
        self.check_type_fields(type_id, type_uri, type_view[ANNAL.CURIE.view_fields])
        return

    # Test consistency of field descriptions for a given type
    def check_type_fields(self, type_id, type_uri, view_fields):
        for f in view_fields:
            field_id   = f[ANNAL.CURIE.field_id]
            view_field = RecordField.load(self.coll1, field_id, self.testsite)
            field_type = view_field[ANNAL.CURIE.field_render_type]
            try:
                self.assertEqual(view_field["@type"], [ANNAL.CURIE.Field])
                self.assertEqual(view_field[ANNAL.CURIE.id],      field_id)
                self.assertEqual(view_field[ANNAL.CURIE.type_id], "_field")
                self.assertIn(ANNAL.CURIE.property_uri,           view_field)
                self.assertIn(ANNAL.CURIE.field_render_type,      view_field)
                self.assertIn(ANNAL.CURIE.field_value_type,       view_field)
                self.assertIn(ANNAL.CURIE.field_placement,        view_field)
                self.assertIn(ANNAL.CURIE.placeholder,            view_field)
                self.assertIn(ANNAL.CURIE.field_placement,        view_field)
                if ANNAL.CURIE.field_entity_type in view_field:
                    # @@TODO: make this trequired?
                    self.assertEqual(
                        view_field[ANNAL.CURIE.field_entity_type], type_uri
                        )
                if field_type in ["RepeatGroup", "RepeatGroupRow"]:
                    # Check extra fields
                    group_id = view_field[ANNAL.CURIE.group_ref]
                    self.assertIn(ANNAL.CURIE.repeat_label_add,    view_field)
                    self.assertIn(ANNAL.CURIE.repeat_label_delete, view_field)
                    # Check field group
                    field_group = RecordGroup.load(self.coll1, group_id, self.testsite)
                    self.assertEqual(field_group["@type"], [ANNAL.CURIE.Field_group])
                    self.assertEqual(field_group[ANNAL.CURIE.id],      group_id)
                    self.assertEqual(field_group[ANNAL.CURIE.type_id], "_group")
                    self.check_type_fields(
                        "_group", ANNAL.CURIE.Field_group, field_group[ANNAL.CURIE.group_fields]
                        )
                    # field_name is present only if different from field_id
                    # self.assertIn(ANNAL.CURIE.field_name,  list_field)
                enum_types = (
                    [ "Type", "View", "List", "Field"
                    , "Enum", "Enum_optional"
                    ])
                if field_type in enum_types:
                    self.assertIn(ANNAL.CURIE.options_typeref, view_field)
            except Exception as e:
                log.warning("check_type_fields error %s, field_id %s, render_type %s"%(e, field_id, field_type))
                raise
        return

    # --------------------------------------------------------------------------
    # Test cases
    # --------------------------------------------------------------------------

    # Site front page
    def test_site_view(self):
        u = site_view_url()
        s = self.get_page(u)
        # Check displayed collections (check site setup)
        self.assertEqual(s.title.string, "Annalist data notebook test site")
        trows = s.select("form > div > div > div")
        self.assertEqual(len(trows), 5)
        for i in (1,2,3):
            tcols = trows[i].find_all("div", class_="view-value")
            colln = "coll%d"%i
            self.assertEqual(tcols[0].a.string,  colln)
            self.assertEqual(tcols[0].a['href'], collection_view_url(colln))
        return
 
    # Test collection view
    def test_collection_view(self):
        u = collection_view_url(coll_id="coll1")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List entities with type information")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Default_list_all")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Type")
        self.assertEqual(thead[2].span.string, "Label")
        # test_default_list_all performs other relevant tests
        return

    # Test configuration view
    def test_collection_edit(self):
        u = collection_edit_url(coll_id="coll1")
        s = self.get_page(u)
        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "Customize collection coll1")
        types_expected = ['type1', 'type2']
        self.check_select_field(s, "typelist", types_expected, None)
        lists_expected = ['list1', 'list2']
        self.check_select_field(s, "listlist", lists_expected, None)
        views_expected = ['view1', 'view2']
        self.check_select_field(s, "viewlist", views_expected, None)
        return

    # Default list all
    # Same as test_collection_view but using different URI
    def test_default_list_all(self):
        u = collection_entity_list_url(coll_id="coll1", list_id="Default_list_all")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List entities with type information")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Default_list_all")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Type")
        self.assertEqual(thead[2].span.string, "Label")

        trows_expected = (
            [ [ "_list/list1",    ["list1", "_list", "RecordList coll1/list1"] ]
            , [ "_list/list2",    ["list2", "_list", "RecordList coll1/list2"] ]
            , [ "_type/type1",    ["type1", "_type", "RecordType coll1/type1"] ]
            , [ "_type/type2",    ["type2", "_type", "RecordType coll1/type2"] ]
            , [ "_user/testuser", ["testuser", "_user", "Test User"] ]
            , [ "_view/view1",    ["view1", "_view", "RecordView coll1/view1"] ]
            , [ "_view/view2",    ["view2", "_view", "RecordView coll1/view2"] ]
            , [ "type1/entity1",  ["entity1", "type1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2",  ["entity2", "type1", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3",  ["entity3", "type1", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1",  ["entity1", "type2", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2",  ["entity2", "type2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3",  ["entity3", "type2", "Entity coll1/type2/entity3"] ]
            ])
        self.check_list_row_data(s, trows_expected)

        # @@TODO: check entity and type links
        #         check_list_row_links?  or add 3rd element to each trows_expected
        return

    # Default list
    def test_default_list(self):
        u = collection_entity_list_url(coll_id="coll1", list_id="Default_list")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List entities")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Default_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_list/list1",    ["list1", "RecordList coll1/list1"] ]
            , [ "_list/list2",    ["list2", "RecordList coll1/list2"] ]
            , [ "_type/type1",    ["type1", "RecordType coll1/type1"] ]
            , [ "_type/type2",    ["type2", "RecordType coll1/type2"] ]
            , [ "_user/testuser", ["testuser", "Test User"] ]
            , [ "_view/view1",    ["view1", "RecordView coll1/view1"] ]
            , [ "_view/view2",    ["view2", "RecordView coll1/view2"] ]
            , [ "type1/entity1",  ["entity1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2",  ["entity2", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3",  ["entity3", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1",  ["entity1", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2",  ["entity2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3",  ["entity3", "Entity coll1/type2/entity3"] ]
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # --------------------------------------------------------------------------
    # Test site data for types
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordType
    def test_recordtype_type_list_view(self):
        self.check_type_list_view("_type", "Type_list", "Type_view", ANNAL.CURIE.Type)
        return

    # List types using type list
    def test_type_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="Type_list", type_id="_type", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List types")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Type_list")

        thead = (
            s.form.find("div", class_="thead")
                  .find("div", class_="row")
                  .find_all("div", class_="columns")
            )
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_type/_field",           ["_field",           "Field description type"] ]
            , [ "_type/_group",           ["_group",           "Field group type"] ]
            , [ "_type/_initial_values",  ["_initial_values",  None] ]
            , [ "_type/_list",            ["_list",            "List description type"] ]
            , [ "_type/_type",            ["_type",            "Type description type"] ]
            , [ "_type/_user",            ["_user",            "User permissions type"] ]
            , [ "_type/_view",            ["_view",            "View description type"] ]
            , [ "_type/BibEntry_type",    ["BibEntry_type",    "Bibliographic record type"] ]
            , [ "_type/Default_type",     ["Default_type",     "Default record type"] ]
            , [ "_type/Enum_bib_type",    ["Enum_bib_type",    "Bibliographic entry type"] ]
            , [ "_type/Enum_list_type",   ["Enum_list_type",   "List display type"] ]
            , [ "_type/Enum_render_type", ["Enum_render_type", "Field render type"] ]
            , [ "_type/type1",            ["type1",            "RecordType coll1/type1"] ]
            , [ "_type/type2",            ["type2",            "RecordType coll1/type2"] ]
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit type using type view
    def test_type_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_type",
            view_id="Type_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "Type_label", "text", None)
        self.check_input_type_value(s, "Type_comment", "textarea", None)
        self.check_input_type_value(s, "Type_uri", "text", None)
        self.check_select_field(s, "Type_view",   self.views_expected, "Default_view")
        self.check_select_field(s, "Type_list",   self.lists_expected, "Default_list")
        self.check_select_field(s, "view_choice", self.views_expected, "Type_view")
        return

    # Edit/view type view
    def test_view_edit_type_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Type_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = (
            [ "Entity_comment"
            , "Entity_id"
            , "Entity_label"
            , "Entity_type"
            , "Type_aliases"
            , "Type_comment"
            , "Type_id"
            , "Type_label"
            , "Type_list"
            , "Type_uri"
            , "Type_view"
            ])
        expect_fields = (
            [ "Type_id"
            , "Type_label"
            , "Type_comment"
            , "Type_uri"
            , "Type_view"
            , "Type_list"
            , "Type_aliases"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view type list
    def test_view_edit_type_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="Type_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "Type_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(s, "List_entity_selector", "text", "'annal:Type' in [@type]")
        self.check_input_type_value(s, "List_target_type", "text", "annal:Type")
        self.check_select_field(
            s, "List_type", self.list_types_expected, "List"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_type"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "Type_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for lists
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordList
    def test_recordlist_type_list_view(self):
        self.check_type_list_view("_list", "List_list", "List_view", ANNAL.CURIE.List)
        return

    # List lists using list list
    def test_list_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="List_list", type_id="_list", scope='all'
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List lists")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "List_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_list/_initial_values",    ["_initial_values",     None] ]
            , [ "_list/BibEntry_list",      ["BibEntry_list",       "List bibliographic entries"] ]
            , [ "_list/Default_list",       ["Default_list",        "List entities"] ]
            , [ "_list/Default_list_all",   ["Default_list_all",    "List entities with type information"] ]
            , [ "_list/Field_group_list",   ["Field_group_list",    "List field groups"] ]
            , [ "_list/Field_list",         ["Field_list",          "List fields"] ]
            , [ "_list/List_list",          ["List_list",           "List lists"] ]
            , [ "_list/Type_list",          ["Type_list",           "List types"] ]
            , [ "_list/User_list",          ["User_list",           "List users"] ]
            , [ "_list/View_list",          ["View_list",           "List views"] ]
            , [ "_list/list1",              ["list1",               "RecordList coll1/list1"] ]
            , [ "_list/list2",              ["list2",               "RecordList coll1/list2"] ]   
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit list using list view
    def test_list_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list",
            view_id="List_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_select_field(s, "List_default_type", self.types_expected, "Default_type")
        self.check_select_field(s, "List_default_view", self.views_expected, "Default_view")
        self.check_input_type_value(s, "List_entity_selector", "text", "ALL")
        self.check_input_type_value(s, "List_target_type", "text", "")
        self.check_select_field(s, "view_choice", self.views_expected, "List_view")
        return

    # Edit/view list view
    def test_view_edit_list_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="List_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = (
            [ "Entity_comment"
            , "Entity_id"
            , "Entity_label"
            , "Entity_type"
            , "List_comment"
            , "List_default_type"
            , "List_default_view"
            , "List_entity_selector"
            , "List_id"
            , "List_label"
            , "List_repeat_fields"
            , "List_target_type"
            , "List_type"
            ])
        expect_fields = (
            [ "List_id"
            , "List_type"
            , "List_label"
            , "List_comment"
            , "List_default_type"
            , "List_default_view"
            , "List_entity_selector"
            , "List_target_type"
            , "List_repeat_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view list list
    def test_view_edit_list_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="List_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "List_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(s, "List_entity_selector", "text", "'annal:List' in [@type]")
        self.check_input_type_value(s, "List_target_type", "text", "annal:List")
        self.check_select_field(
            s, "List_type", self.list_types_expected, "List"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_list"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "List_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for views
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordView
    def test_recordlist_type_view_view(self):
        self.check_type_list_view("_view", "View_list", "View_view", ANNAL.CURIE.View)
        return

    # List views using view list
    def test_view_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="View_list", type_id="_view", scope='all'
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List views")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "View_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_view/_initial_values",    ["_initial_values",     None] ]
            , [ "_view/BibEntry_view",      ["BibEntry_view",       "Bibliographic metadata"] ]
            , [ "_view/Default_view",       ["Default_view",        "Default record view"] ]
            , [ "_view/Field_group_view",   ["Field_group_view",    "Field group view description"] ]
            , [ "_view/Field_view",         ["Field_view",          "View description for view field description"] ]
            , [ "_view/List_view",          ["List_view",           "View description for record list description"] ]
            , [ "_view/Type_view",          ["Type_view",           "View description for record type description"] ]
            , [ "_view/User_view",          ["User_view",           "User permissions view"] ]
            , [ "_view/View_view",          ["View_view",           "View description for record view description"] ]
            , [ "_view/view1",              ["view1",               "RecordView coll1/view1"] ]
            , [ "_view/view2",              ["view2",               "RecordView coll1/view2"] ]   
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit view using view view
    def test_view_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view",
            view_id="View_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "View_label", "text", None)
        self.check_input_type_value(s, "View_comment", "textarea", None)
        self.check_input_type_value(s, "View_target_type", "text", None)
        self.check_input_type_value(s, "View_edit_view", "checkbox", "Yes")
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view view view
    def test_view_edit_view_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="View_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = get_site_view_fields_sorted()
        expect_fields        = (
            [ "View_id"
            , "View_label"
            , "View_comment"
            , "View_target_type"
            , "View_edit_view"
            , "View_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view view list
    def test_view_edit_view_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="View_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "View_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_select_field(
            s, "List_type", self.list_types_expected, "List"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_view"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "View_view"
            )
        self.check_input_type_value(
            s, "List_entity_selector", "text", "'annal:View' in [@type]"
            )
        self.check_input_type_value(
            s, "List_target_type", "text", "annal:View"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for field groups
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordGroup
    def test_recordlist_type_group_view(self):
        self.check_type_list_view("_group", "Field_group_list", "Field_group_view", ANNAL.CURIE.Field_group)
        return

    # List groups using group list
    def test_group_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="Field_group_list", type_id="_group", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List field groups")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Field_group_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_group/Bib_book_group",        ["Bib_book_group",        "BibEntry book fields"] ]
            , [ "_group/Bib_identifier_group",  ["Bib_identifier_group",  "BibEntry identifier fields"] ]
            , [ "_group/Bib_journal_group",     ["Bib_journal_group",     "BibEntry journal fields"] ]
            , [ "_group/Bib_license_group",     ["Bib_license_group",     "BibEntry license fields"] ]
            , [ "_group/Bib_person_group",      ["Bib_person_group",      "BibEntry person fields"] ]
            , [ "_group/Bib_publication_group", ["Bib_publication_group", "BibEntry publication detail fields"] ]
            , [ "_group/Group_field_group",     ["Group_field_group",     "Group field description"] ]
            , [ "_group/List_field_group",      ["List_field_group",      "List field description"] ]
            , [ "_group/Type_alias_group",      ["Type_alias_group",      "Field alias"] ]
            , [ "_group/View_field_group",      ["View_field_group",      "View field description"] ]
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit group using group view
    def test_group_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_group",
            view_id="Field_group_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "Group_label", "text", None)
        self.check_input_type_value(s, "Group_comment", "textarea", None)
        self.check_input_type_value(s, "Group_target_type", "text", None)
        self.check_select_field(
            s, "view_choice", self.views_expected, "Field_group_view"
            )
        return

    # Edit/view group view
    def test_view_edit_group_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Field_group_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = (
            [ "Entity_comment"
            , "Entity_id"
            , "Entity_label"
            , "Entity_type"
            , "Group_comment"
            , "Group_field_placement"
            , "Group_field_property"
            , "Group_field_sel"
            , "Group_id"
            , "Group_label"
            , "Group_repeat_fields"
            , "Group_target_type"
            , "Type_alias_source"
            , "Type_alias_target"
            ])
        expect_fields = (
            [ "Group_id"
            , "Group_label"
            , "Group_comment"
            , "Group_target_type"
            , "Group_repeat_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view group list
    def test_view_edit_group_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="Field_group_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "Field_group_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(
            s, "List_entity_selector", "text", "'annal:Field_group' in [@type]"
            )
        self.check_input_type_value(
            s, "List_target_type", "text", "annal:Field_group"
            )
        self.check_select_field(
            s, "List_type", self.list_types_expected, "List"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_group"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "Field_group_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for record fields
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordField
    def test_recordlist_type_field_view(self):
        self.check_type_list_view("_field", "Field_list", "Field_view", ANNAL.CURIE.Field)
        return

    # List fields using field list
    def test_field_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="Field_list", type_id="_field", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List fields")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "Field_list")

        thead = (
            s.form.find("div", class_="thead")
            .find("div", class_="row")
            .find_all("div", class_="columns")
            )
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Field value type")
        self.assertEqual(thead[2].span.string, "Label")

        trows_expected = (
            [ [ "_field/_initial_values",           ["_initial_values",   "annal:Text", None     ] ]
            , [ "_field/Bib_address",               ["Bib_address",       "annal:Text", "Address"] ]
            , [ "_field/Bib_alternate",             ["Bib_alternate",     "annal:Text"    ] ]
            , [ "_field/Bib_authors",               ["Bib_authors",       "bib:Authors"   ] ]
            , [ "_field/Bib_bookentry",             ["Bib_bookentry",     "bib:BookEntry" ] ]
            , [ "_field/Bib_booktitle",             ["Bib_booktitle",     "annal:Text"    ] ]
            , [ "_field/Bib_chapter",               ["Bib_chapter",       "annal:Text"    ] ]
            , [ "_field/Bib_description",           ["Bib_description",   "annal:Text"    ] ]
            , [ "_field/Bib_edition",               ["Bib_edition",       "annal:Text"    ] ]
            , [ "_field/Bib_editors",               ["Bib_editors",       "bib:Editors"   ] ]
            , [ "_field/Bib_eprint",                ["Bib_eprint",        "annal:Text"    ] ]
            , [ "_field/Bib_firstname",             ["Bib_firstname",     "annal:Text"    ] ]
            , [ "_field/Bib_howpublished",          ["Bib_howpublished",  "annal:Text"    ] ]
            , [ "_field/Bib_id",                    ["Bib_id",            "annal:Text"    ] ]
            , [ "_field/Bib_idanchor",              ["Bib_idanchor",      "annal:Text"    ] ]
            , [ "_field/Bib_identifiers",           ["Bib_identifiers",   "bib:Identifiers" ] ]
            , [ "_field/Bib_idtype",                ["Bib_idtype",        "annal:Text"    ] ]
            , [ "_field/Bib_institution",           ["Bib_institution",   "annal:Text"    ] ]
            , [ "_field/Bib_journal",               ["Bib_journal",       "bib:Journal"   ] ]
            , [ "_field/Bib_jurisdiction",          ["Bib_jurisdiction",  "annal:Text"    ] ]
            , [ "_field/Bib_lastname",              ["Bib_lastname",      "annal:Text"    ] ]
            , [ "_field/Bib_license",               ["Bib_license",       "bib:Licenses"  ] ]
            , [ "_field/Bib_month",                 ["Bib_month",         "annal:Text"    ] ]
            , [ "_field/Bib_name",                  ["Bib_name",          "annal:Text"    ] ]
            , [ "_field/Bib_note",                  ["Bib_note",          "annal:Longtext" ] ]
            , [ "_field/Bib_number",                ["Bib_number",        "annal:Text"    ] ]
            , [ "_field/Bib_organization",          ["Bib_organization",  "annal:Text"    ] ]
            , [ "_field/Bib_pages",                 ["Bib_pages",         "annal:Text"    ] ]
            , [ "_field/Bib_publication_details",   ["Bib_publication_details"            ] ]
            , [ "_field/Bib_publisher",             ["Bib_publisher",     "annal:Text"    ] ]
            , [ "_field/Bib_school",                ["Bib_school",        "annal:Text"    ] ]
            , [ "_field/Bib_shortcode",             ["Bib_shortcode",     "annal:Text"    ] ]
            , [ "_field/Bib_title",                 ["Bib_title",         "annal:Text"    ] ]
            , [ "_field/Bib_type",                  ["Bib_type",          "annal:Slug"    ] ]
            , [ "_field/Bib_url",                   ["Bib_url",           "annal:Text"    ] ]
            , [ "_field/Bib_volume",                ["Bib_volume",        "annal:Text"    ] ]
            , [ "_field/Bib_year",                  ["Bib_year",          "annal:Text"    ] ]
            , [ "_field/Entity_comment",            ["Entity_comment"                     ] ]
            , [ "_field/Entity_id",                 ["Entity_id"                          ] ]
            , [ "_field/Entity_label",              ["Entity_label"                       ] ]
            , [ "_field/Entity_type",               ["Entity_type"                        ] ]
            , [ "_field/Field_comment",             ["Field_comment"                      ] ]
            , [ "_field/Field_default",             ["Field_default"                      ] ]
            , [ "_field/Field_entity_type",         ["Field_entity_type"                  ] ]
            , [ "_field/Field_groupref",            ["Field_groupref"                     ] ]
            , [ "_field/Field_id",                  ["Field_id"                           ] ]
            , [ "_field/Field_label",               ["Field_label"                        ] ]
            , [ "_field/Field_missing",             ["Field_missing"                      ] ]
            , [ "_field/Field_placeholder",         ["Field_placeholder"                  ] ]
            , [ "_field/Field_placement",           ["Field_placement"                    ] ]
            , [ "_field/Field_property",            ["Field_property"                     ] ]
            , [ "_field/Field_render",              ["Field_render"                       ] ]
            , [ "_field/Field_repeat_label_add",    ["Field_repeat_label_add"             ] ]
            , [ "_field/Field_repeat_label_delete", ["Field_repeat_label_delete"          ] ]
            , [ "_field/Field_restrict",            ["Field_restrict"                     ] ]
            , [ "_field/Field_type",                ["Field_type"                         ] ]
            , [ "_field/Field_typeref",             ["Field_typeref"                      ] ]
            , [ "_field/Group_comment",             ["Group_comment"                      ] ]
            , [ "_field/Group_field_placement",     ["Group_field_placement"              ] ]
            , [ "_field/Group_field_property",      ["Group_field_property"               ] ]
            , [ "_field/Group_field_sel",           ["Group_field_sel"                    ] ]
            , [ "_field/Group_id",                  ["Group_id"                           ] ]
            , [ "_field/Group_label",               ["Group_label"                        ] ]
            , [ "_field/Group_repeat_fields",       ["Group_repeat_fields"                ] ]
            , [ "_field/Group_target_type",         ["Group_target_type"                  ] ]
            , [ "_field/List_choice",               ["List_choice"                        ] ]
            , [ "_field/List_comment",              ["List_comment"                       ] ]
            , [ "_field/List_default_type",         ["List_default_type"                  ] ]
            , [ "_field/List_default_view",         ["List_default_view"                  ] ]
            , [ "_field/List_entity_selector",      ["List_entity_selector"               ] ]
            , [ "_field/List_id",                   ["List_id"                            ] ]
            , [ "_field/List_label",                ["List_label"                         ] ]
            , [ "_field/List_repeat_fields",        ["List_repeat_fields"                 ] ]
            , [ "_field/List_target_type",          ["List_target_type"                   ] ]
            , [ "_field/List_type",                 ["List_type"                          ] ]
            , [ "_field/Type_alias_source",         ["Type_alias_source"                  ] ]
            , [ "_field/Type_alias_target",         ["Type_alias_target"                  ] ]
            , [ "_field/Type_aliases",              ["Type_aliases"                       ] ]
            , [ "_field/Type_comment",              ["Type_comment"                       ] ]
            , [ "_field/Type_id",                   ["Type_id"                            ] ]
            , [ "_field/Type_label",                ["Type_label"                         ] ]
            , [ "_field/Type_list",                 ["Type_list"                          ] ]
            , [ "_field/Type_uri",                  ["Type_uri"                           ] ]
            , [ "_field/Type_view",                 ["Type_view"                          ] ]
            , [ "_field/User_description",          ["User_description"                   ] ]
            , [ "_field/User_id",                   ["User_id"                            ] ]
            , [ "_field/User_name",                 ["User_name"                          ] ]
            , [ "_field/User_permissions",          ["User_permissions"                   ] ]
            , [ "_field/User_uri",                  ["User_uri"                           ] ]
            , [ "_field/View_choice",               ["View_choice"                        ] ]
            , [ "_field/View_comment",              ["View_comment"                       ] ]
            , [ "_field/View_edit_view",            ["View_edit_view"                     ] ]
            , [ "_field/View_fields",               ["View_fields"                        ] ]
            , [ "_field/View_id",                   ["View_id"                            ] ]
            , [ "_field/View_label",                ["View_label"                         ] ]
            , [ "_field/View_target_type",          ["View_target_type"                   ] ]
            ])
        self.check_list_row_data(s, trows_expected)

    # Create/edit field using field view
    def test_field_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_field",
            view_id="Field_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "Field_type", "text", "annal:Text")
        self.check_input_type_value(s, "Field_label", "text", "")
        self.check_input_type_value(s, "Field_comment", "textarea", None)
        self.check_input_type_value(s, "Field_placeholder", "text", "")
        self.check_input_type_value(s, "Field_property", "text", "")
        # self.check_input_type_value(s, "Field_placement", "text", "")
        self.check_select_field(
            s, "Field_placement", 
            ["(field position and size)"]+self.placements_expected, 
            "(field position and size)"
            )
        self.check_input_type_value(s, "Field_default", "text", None)
        self.check_input_type_value(s, "Field_entity_type", "text", "")
        self.check_input_type_value(s, "Field_restrict", "text", "")
        self.check_select_field(
            s, "Field_render",   self.render_types_expected, "Text"
            )
        self.check_select_field(
            s, "Field_typeref", 
            ["(no type selected)"]+self.types_expected, 
            "(no type selected)"
            )
        self.check_select_field(
            s, "Field_groupref",
            ["(no field group selected)"]+self.grouprefs_expected, 
            "(no field group selected)"
            )
        self.check_select_field(
            s, "view_choice", self.views_expected, "Field_view"
            )
        return

    # Edit/view field view
    def test_view_edit_field_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Field_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = (
            [ "Entity_comment"
            , "Entity_id"
            , "Entity_label"
            , "Entity_type"
            , "Field_comment"
            , "Field_default"
            , "Field_entity_type"
            , "Field_groupref"
            , "Field_id"
            , "Field_label"
            , "Field_missing"
            , "Field_placeholder"
            , "Field_placement"
            , "Field_property"
            , "Field_render"
            , "Field_repeat_label_add"
            , "Field_repeat_label_delete"
            , "Field_restrict"
            , "Field_type"
            , "Field_typeref"
            ])
        expect_fields = (
            [ "Field_id"
            , "Field_type"
            , "Field_render"
            , "Field_placement"
            , "Field_label"
            , "Field_comment"
            , "Field_placeholder"
            , "Field_property"
            , "Field_default"
            , "Field_entity_type"
            , "Field_typeref"
            , "Field_restrict"
            , "Field_groupref"
            , "Field_repeat_label_add"
            , "Field_repeat_label_delete"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view field list
    def test_view_edit_field_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="Field_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "Field_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(s, "List_target_type", "text", "annal:Field")
        self.check_input_type_value(
            s, "List_entity_selector", "text", "'annal:Field' in [@type]"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_field"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "Field_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for user permissions
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for user
    def test_recorduser_type_field_view(self):
        self.check_type_list_view("_user", "User_list", "User_view", ANNAL.CURIE.User)
        return

    # List users using user list
    def test_user_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="User_list", type_id="_user", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List users")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "User_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "User Id")
        self.assertEqual(thead[1].span.string, "URI")
        self.assertEqual(thead[2].span.string, "Permissions")

        trows_expected = (
            [ [ "_user/_default_user_perms",  
                [ "_default_user_perms",  "annal:User/_default_user_perms"
                , "VIEW"]
              ]
            , [ "_user/_unknown_user_perms",
                [ "_unknown_user_perms",  "annal:User/_unknown_user_perms"
                , "VIEW"
                ] 
              ]
            , [ "_user/admin", 
                [ "admin", "mailto:admin@localhost"
                , "VIEW CREATE UPDATE DELETE CONFIG CREATE_COLL DELETE_COLL ADMIN"
                ]
              ]
            , [ "_user/testuser",
                [ "testuser", "mailto:testuser@test.example.com"
                , "VIEW CREATE UPDATE DELETE CONFIG ADMIN"
                ]
              ]
            ])
        self.check_list_row_data(s, trows_expected)

    # Create/edit user using user view
    def test_user_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_user",
            view_id="User_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "User_name", "text", None)
        self.check_input_type_value(s, "User_description", "textarea", None)
        self.check_input_type_value(s, "User_uri", "text", None)
        self.check_input_type_value(s, "User_permissions", "text", None)
        self.check_select_field(s, "view_choice", self.views_expected, "User_view")
        return

    # Edit/view user view
    def test_view_edit_user_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="User_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = (
            [ "Entity_comment"
            , "Entity_id"
            , "Entity_label"
            , "Entity_type"
            , "User_description"
            , "User_id"
            , "User_name"
            , "User_permissions"
            , "User_uri"
            ])
        expect_fields = (
            [ "User_id"
            , "User_name"
            , "User_description"
            , "User_uri"
            , "User_permissions"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "View_view")
        return

    # Edit/view user list
    def test_view_edit_user_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="User_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "User_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(s, "List_target_type", "text", "annal:User")
        self.check_input_type_value(
            s, "List_entity_selector", "text", "'annal:User' in [@type]"
            )
        self.check_select_field(
            s, "List_default_type", self.types_expected, "_user"
            )
        self.check_select_field(
            s, "List_default_view", self.views_expected, "User_view"
            )
        return

# End.
