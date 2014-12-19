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

(The first couple of tests also check aspects of the test site data setiup.)
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

# from miscutils.MockHttpResources import MockHttpFileResources, MockHttpDictResources

# from annalist.identifiers       import ANNAL
# from annalist.models.entity     import EntityRoot, Entity

from annalist.identifiers           import RDF, RDFS, ANNAL
# from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordfield    import RecordField

from tests                          import TestBaseUri, TestBaseDir, dict_to_str, init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase

from entity_testutils import (
    site_view_url,
    collection_view_url,
    collection_edit_url,
    collection_entity_list_url,
    collection_entity_view_url,
    # collection_entity_edit_url  @@TODO?
    )
from entity_testsitedata            import (
    get_site_types, get_site_types_sorted,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )

# Test assertion summary from http://docs.python.org/2/library/unittest.html#test-cases
#
# Method                    Checks that             New in
# assertEqual(a, b)         a == b   
# assertNotEqual(a, b)      a != b   
# assertTrue(x)             bool(x) is True  
# assertFalse(x)            bool(x) is False     
# assertIs(a, b)            a is b                  2.7
# assertIsNot(a, b)         a is not b              2.7
# assertIsNone(x)           x is None               2.7
# assertIsNotNone(x)        x is not None           2.7
# assertIn(a, b)            a in b                  2.7
# assertNotIn(a, b)         a not in b              2.7
# assertIsInstance(a, b)    isinstance(a, b)        2.7
# assertNotIsInstance(a, b) not isinstance(a, b)    2.7
#
# From AnnalistTestCase:
# self.assertMatch(string, pattern, msg=None)
# self.assertDictionaryMatch(actual_dict, expect_dict, prefix="")


#   -----------------------------------------------------------------------------
#
#   @@stuff@@ tests
#
#   -----------------------------------------------------------------------------

class AnnalistSiteDataTest(AnnalistTestCase):
    """
    Tests for Annalist site data completeness and consistency
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.coll1    = Collection.load(self.testsite, "coll1")
        return

    def tearDown(self):
        return

    # ----------------------------------
    # Helper functions
    # ----------------------------------

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
    def check_input_type_value(self, s, name, input_type, input_value=None, input_text=None):
        input_elem = s.form.find("input", attrs={"name": name})
        self.assertEqual(input_elem['type'], input_type)
        if input_value is not None:
            self.assertEqual(input_elem['value'], input_value)
        if input_text is not None:
            self.assertEqual(input_elem.string, input_text)
        return

    # Test named input is <select> with specified options and selected value
    def check_select_field(self, s, name, options, selection):
        select_elem = s.form.find("select", attrs={"name": name})
        options_here = [o.string for o in select_elem.find_all("option")]
        self.assertEqual(options_here, options)
        if selection is not None:
            self.assertEqual(select_elem.find("option", selected=True).string, selection)
        return

    # row_data:
    #
    # <div class="trow row select-row">
    #   <div class="small-1 columns">
    #     <input class="select-box right" name="entity_select" type="checkbox" value="type2/entity3"/>
    #   </div>
    #   <div class="small-11 columns">
    #     <div class="row">
    #       <div class="small-3 columns"><!-- ... --><a href="...">entity3</a></div>
    #       <div class="small-2 columns"><!-- ... --><a href="...">type2</a></div>
    #       <div class="small-7 columns"><!-- ... -->Entity coll1/type2/entity3</div>
    #       </div>
    #   </div>
    # </div>
    #
    def check_row_column(self, row_data, colnum, row_expected):
        # print "*****"
        # print row_data
        self.assertEqual(
            row_expected[colnum],
            row_data
                .find("div", class_="row")
                .find_all("div", class_="columns")[colnum]
                .stripped_strings.next()
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
        self.assertIn(ANNAL.CURIE.add_field,                    type_view)
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
                self.assertEqual(view_field["@type"],                   [ANNAL.CURIE.Field])
                self.assertEqual(view_field[ANNAL.CURIE.id],            field_id)
                self.assertEqual(view_field[ANNAL.CURIE.type_id],       "_field")
                self.assertIn(ANNAL.CURIE.property_uri,                 view_field)
                self.assertIn(ANNAL.CURIE.field_render_type,            view_field)
                self.assertIn(ANNAL.CURIE.field_value_type,             view_field)
                self.assertIn(ANNAL.CURIE.field_placement,              view_field)
                self.assertIn(ANNAL.CURIE.placeholder,                  view_field)
                self.assertIn(ANNAL.CURIE.field_placement,              view_field)
                if ANNAL.CURIE.field_entity_type in view_field:
                    # @@TODO: need to rethink this for. e.g., Field_sel, il View, List and Group records
                    # Currently have removed annal:field_entity_type from Field_sel, Field_property,
                    # Field_placement so they may now show up for all view forms.  Check this.
                    # Two problems: (a) how to handle ikn app, (b) how to test?
                    self.assertEqual(view_field[ANNAL.CURIE.field_entity_type], type_uri)
                if field_type in ["RepeatGroup", "RepeatGroupRow"]:
                    # Check extra fields
                    group_id = view_field[ANNAL.CURIE.group_ref]
                    self.assertIn(ANNAL.CURIE.repeat_label_add,         view_field)
                    self.assertIn(ANNAL.CURIE.repeat_label_delete,      view_field)
                    # Check field group
                    field_group = RecordGroup.load(self.coll1, group_id, self.testsite)
                    self.assertEqual(field_group["@type"],                  [ANNAL.CURIE.Field_group])
                    self.assertEqual(field_group[ANNAL.CURIE.id],           group_id)
                    self.assertEqual(field_group[ANNAL.CURIE.type_id],      "_group")
                    self.check_type_fields(
                        "_group", ANNAL.CURIE.Field_group, field_group[ANNAL.CURIE.group_fields]
                        )
                    # self.check_type_fields(type_id, type_uri, field_group[ANNAL.CURIE.group_fields])
                    # field_name is present inly if different from field_id
                    # self.assertIn(ANNAL.CURIE.field_name,                   list_field)
                # @@TODO: If enum type, look for typeref
            except Exception as e:
                log.warning("check_type_fields error %s, field_id %s, render_type %s"%(e, field_id, field_type))
                raise
        return

    # ----------------------------------
    # Test cases
    # ----------------------------------

    # Site front page
    def test_site_view(self):
        u = site_view_url()
        s = self.get_page(u)
        # Check displayed collections (check site setup)
        self.assertEqual(s.title.string, "Annalist data notebook test site")
        trows = s.form.find_all("div", class_="row")
        self.assertEqual(len(trows), 5)
        self.assertEqual(trows[1].div.p.a.string,  "coll1")
        self.assertEqual(trows[1].div.p.a['href'], collection_view_url("coll1"))
        self.assertEqual(trows[2].div.p.a.string,  "coll2")
        self.assertEqual(trows[2].div.p.a['href'], collection_view_url("coll2"))
        self.assertEqual(trows[3].div.p.a.string,  "coll3")
        self.assertEqual(trows[3].div.p.a['href'], collection_view_url("coll3"))
        return
 
    # Test collection view
    def test_collection_view(self):
        u = collection_view_url(coll_id="coll1")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List entities with type information")
        self.check_input_type_value(s, "search_for", "text", "")
        options_expected = get_site_lists_sorted() + ['list1', 'list2']
        self.check_select_field(s, "list_choice", options_expected, "Default_list_all")
        self.check_input_type_value(s, "view", "submit", "View")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].p.string, "Id")
        self.assertEqual(thead[1].p.string, "Type")
        self.assertEqual(thead[2].p.string, "Label")
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
        options_expected = get_site_lists_sorted() + ['list1', 'list2']
        self.check_select_field(s, "list_choice", options_expected, "Default_list_all")
        self.check_input_type_value(s, "view", "submit", "View")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].p.string, "Id")
        self.assertEqual(thead[1].p.string, "Type")
        self.assertEqual(thead[2].p.string, "Label")

        trows_expected = (
            [ [ "_list/list1",   ["list1", "_list", "RecordList coll1/list1"] ]
            , [ "_list/list2",   ["list2", "_list", "RecordList coll1/list2"] ]
            , [ "_type/type1",   ["type1", "_type", "RecordType coll1/type1"] ]
            , [ "_type/type2",   ["type2", "_type", "RecordType coll1/type2"] ]
            , [ "_view/view1",   ["view1", "_view", "RecordView coll1/view1"] ]
            , [ "_view/view2",   ["view2", "_view", "RecordView coll1/view2"] ]
            , [ "type1/entity1", ["entity1", "type1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2", ["entity2", "type1", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3", ["entity3", "type1", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1", ["entity1", "type2", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2", ["entity2", "type2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3", ["entity3", "type2", "Entity coll1/type2/entity3"] ]
            ])
        trows = s.form.find_all("div", class_="trow")
        self.assertEqual(len(trows), len(trows_expected))
        for i in range(len(trows_expected)):
            e = trows_expected[i]   # expected
            f = trows[i]            # found
            # <input class="select-box right" name="entity_select" type="checkbox" value="_list/list1"/>
            self.assertEqual(e[0], f.find("input", class_="select-box")["value"])
            self.check_row_column(trows[i], 0, trows_expected[i][1])
            self.check_row_column(trows[i], 1, trows_expected[i][1])
            self.check_row_column(trows[i], 2, trows_expected[i][1])

        return

    # Default list
    def test_default_list(self):
        u = collection_entity_list_url(coll_id="coll1", list_id="Default_list")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "Collection coll1")
        self.assertEqual(s.h3.string, "List entities")
        self.check_input_type_value(s, "search_for", "text", "")
        options_expected = get_site_lists_sorted() + ['list1', 'list2']
        self.check_select_field(s, "list_choice", options_expected, "Default_list")
        self.check_input_type_value(s, "view", "submit", "View")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].p.string, "Id")
        self.assertEqual(thead[1].p.string, "Label")

        trows_expected = (
            [ [ "_list/list1",   ["list1", "RecordList coll1/list1"] ]
            , [ "_list/list2",   ["list2", "RecordList coll1/list2"] ]
            , [ "_type/type1",   ["type1", "RecordType coll1/type1"] ]
            , [ "_type/type2",   ["type2", "RecordType coll1/type2"] ]
            , [ "_view/view1",   ["view1", "RecordView coll1/view1"] ]
            , [ "_view/view2",   ["view2", "RecordView coll1/view2"] ]
            , [ "type1/entity1", ["entity1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2", ["entity2", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3", ["entity3", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1", ["entity1", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2", ["entity2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3", ["entity3", "Entity coll1/type2/entity3"] ]
            ])
        trows = s.form.find_all("div", class_="trow")
        self.assertEqual(len(trows), len(trows_expected))
        for i in range(len(trows_expected)):
            e = trows_expected[i]   # expected
            f = trows[i]            # found
            # <input class="select-box right" name="entity_select" type="checkbox" value="_list/list1"/>
            self.assertEqual(e[0], f.find("input", class_="select-box")["value"])
            self.check_row_column(trows[i], 0, trows_expected[i][1])
            self.check_row_column(trows[i], 1, trows_expected[i][1])

        return

    # Test type / list / view / field consistency for RecordType
    def test_recordtype_type_list_view(self):
        self.check_type_list_view("_type", "Type_list", "Type_view", ANNAL.CURIE.Type)
        return

    # List types using type list

    # Create/edit type using type view

    # Test type / list / view / field consistency for RecordList
    def test_recordlist_type_list_view(self):
        self.check_type_list_view("_list", "List_list", "List_view", ANNAL.CURIE.List)
        return

    # List lists using list list

    # Create/edit list using list view

    # Test type / list / view / field consistency for RecordView
    def test_recordlist_type_view_view(self):
        self.check_type_list_view("_view", "View_list", "View_view", ANNAL.CURIE.View)
        return

    # List lists using view list

    # Create/edit view using view view

    # Test type / list / view / field consistency for RecordGroup
    def test_recordlist_type_group_view(self):
        self.check_type_list_view("_group", "Field_group_list", "Field_group_view", ANNAL.CURIE.Field_group)
        return

    # List groups using group list

    # Create/edit group using group view

    # Test type / list / view / field consistency for RecordField
    def test_recordlist_type_field_view(self):
        self.check_type_list_view("_field", "Field_list", "Field_view", ANNAL.CURIE.Field)
        return

    # List fields using field list

    # Create/edit field using field view

    # Test type / list / view / field consistency for user

    # List users using user list

    # Create/edit user using user view

    # @@TODO: Check that predefined enumerations used are covered in the above:
    #         field render type, list display type, value type, etc.






# End.
