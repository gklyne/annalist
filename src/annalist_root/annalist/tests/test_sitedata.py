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

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.util                  import extract_entity_id

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordfield    import RecordField

from annalist.views.fields.find_renderers   import is_repeat_field_render_type
from annalist.views.fields.render_placement import get_placement_options
from annalist.views.form_utils.fieldchoice  import FieldChoice, get_choice_labels

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_view_url,
    collection_view_url,
    collection_edit_url,
    collection_entity_list_url,
    collection_entity_view_url,
    collection_entity_edit_url,
    create_user_permissions, create_test_user
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    get_site_types,        get_site_types_sorted,
    get_site_lists,        get_site_lists_sorted,
    get_site_views,        get_site_views_sorted,
    get_site_fields,       get_site_fields_sorted, 
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_list_types,   get_site_list_types_sorted, 
    get_site_field_types,  get_site_field_types_sorted,
    # Fields by entity type
    get_site_type_fields,  get_site_type_fields_sorted, 
    get_site_list_fields,  get_site_list_fields_sorted, 
    get_site_view_fields,  get_site_view_fields_sorted, 
    get_site_vocab_fields, get_site_vocab_fields_sorted, 
    get_site_field_fields, get_site_field_fields_sorted,
    get_site_group_fields, get_site_group_fields_sorted,
    get_site_user_fields,  get_site_user_fields_sorted, 
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
        self.local_types = make_field_choices(
            [ ("_type/type1", "RecordType coll1/type1")
            , ("_type/type2", "RecordType coll1/type2")
            ])
        self.local_lists = make_field_choices(
            [ ("_list/list1", "RecordList coll1/list1")
            , ("_list/list2", "RecordList coll1/list2")
            ])
        self.local_views = make_field_choices(
            [ ("_view/view1", "RecordView coll1/view1")
            , ("_view/view2", "RecordView coll1/view2")
            ])
        self.types_expected = get_site_types_sorted() + self.local_types
        self.lists_expected = get_site_lists_sorted() + self.local_lists
        self.views_expected = get_site_views_sorted() + self.local_views
        self.list_types_expected   = get_site_list_types_sorted()
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
        # resetSitedata()
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
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
        s = BeautifulSoup(r.content, "html.parser")
        return s

    # Test named input field has specified type and value
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
    # self.check_select_field(s, "typelist", self.local_types, None)
    def check_select_field(self, s, name, options, selection):
        select_elem  = s.find("select", attrs={"name": name})
        option_values_here     = (
            [self.html_encode(o.get('value',"@@novalue:%s"%o.string))
             for o in select_elem.find_all("option")
            ])
        option_values_expected = [ fc.value for fc in options ]
        if option_values_here != option_values_expected:
            log.info("option_values_here:     %r"%(option_values_here,))
            log.info("option_values_expected: %r"%(option_values_expected,))
        self.assertEqual(option_values_here, option_values_expected)
        option_labels_here     = (
            [self.html_encode(o.string) for o in select_elem.find_all("option")]
            )
        #@@ option_labels_expected = [ fc.choice() for fc in options ]
        option_labels_expected = get_choice_labels(options)
        if option_labels_here != option_labels_expected:
            log.info("option_labels_here:     %r"%(option_labels_here,))
            log.info("option_labels_expected: %r"%(option_labels_expected,))
        self.assertEqual(option_labels_here, option_labels_expected)
        if selection is not None:
            find_selection = select_elem.find("option", selected=True)
            if find_selection is None:
                self.fail("No selection %s for %s"%(selection, select_elem))
            self.assertEqual(find_selection['value'], selection)
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
        #@@
        # for i in range(len(trows)):
        #     print "\n@@ trow[%d]:\n%s\n"%(i, trows[i])
        #@@
        self.assertEqual(len(trows), len(trows_expected))
        for i in range(len(trows_expected)):
            e = trows_expected[i]   # expected
            f = trows[i]            # found
            #@@ print "e: "+repr(e)
            #@@ print "f: "+str(f)
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
            # print "@@ trows[%d]\n%s"%(i, trows[i].prettify())
            # print "@@tcols\n%s"%("\n\n".join([c.prettify() for c in tcols]))
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
        type_type = RecordType.load(self.coll1, type_id, altscope="all")
        self.assertEqual(type_type["@type"],                [ANNAL.CURIE.Type])
        self.assertEqual(type_type[ANNAL.CURIE.id],         type_id)
        self.assertEqual(type_type[ANNAL.CURIE.type_id],    "_type")
        self.assertEqual(type_type[ANNAL.CURIE.uri],        type_uri)
        self.assertEqual(type_type[ANNAL.CURIE.type_list],  "_list/"+list_id)
        self.assertEqual(type_type[ANNAL.CURIE.type_view],  "_view/"+view_id)
        # Read type list description
        type_list = RecordList.load(self.coll1, list_id, altscope="all")
        self.assertEqual(type_list["@type"],                    [ANNAL.CURIE.List])
        self.assertEqual(type_list[ANNAL.CURIE.id],             list_id)
        self.assertEqual(type_list[ANNAL.CURIE.type_id],        "_list")
        self.assertEqual(type_list[ANNAL.CURIE.display_type],   "_enum_list_type/List")
        self.assertEqual(type_list[ANNAL.CURIE.default_type],   "_type/"+type_id)
        self.assertEqual(type_list[ANNAL.CURIE.default_view],   "_view/"+view_id)
        self.assertEqual(type_list[ANNAL.CURIE.record_type],    type_uri)
        self.assertIn(ANNAL.CURIE.list_entity_selector,         type_list)
        # Read type view description
        type_view = RecordView.load(self.coll1, view_id, altscope="all")
        self.assertEqual(type_view["@type"],                    [ANNAL.CURIE.View])
        self.assertEqual(type_view[ANNAL.CURIE.id],             view_id)
        self.assertEqual(type_view[ANNAL.CURIE.type_id],        "_view")
        self.assertEqual(type_view[ANNAL.CURIE.record_type],    type_uri)
        self.assertIn(ANNAL.CURIE.open_view,                    type_view)
        # Read and check fields used in list and view displays
        # print "l: " + type_list[ANNAL.CURIE.id]
        self.check_type_fields(type_id, type_uri, type_list[ANNAL.CURIE.list_fields])
        # print "v: " + type_view[ANNAL.CURIE.id]
        self.check_type_fields(type_id, type_uri, type_view[ANNAL.CURIE.view_fields])
        return

    # Test consistency of field descriptions for a given type
    def check_type_fields(self, type_id, type_uri, view_fields):
        # print "t: " + type_id
        for f in view_fields:
            field_id   = extract_entity_id(f[ANNAL.CURIE.field_id])
            # print "f: " + field_id
            view_field = RecordField.load(self.coll1, field_id, altscope="all")
            render_type = view_field[ANNAL.CURIE.field_render_type]
            value_type = view_field[ANNAL.CURIE.field_value_type]
            try:
                self.assertEqual(view_field["@type"], [ANNAL.CURIE.Field])
                self.assertEqual(view_field[ANNAL.CURIE.id],      field_id)
                self.assertEqual(view_field[ANNAL.CURIE.type_id], "_field")
                self.assertIn(ANNAL.CURIE.property_uri,           view_field)
                self.assertIn(ANNAL.CURIE.field_render_type,      view_field)
                self.assertIn(ANNAL.CURIE.field_value_mode,       view_field)
                self.assertIn(ANNAL.CURIE.field_value_type,       view_field)
                self.assertIn(ANNAL.CURIE.field_placement,        view_field)
                self.assertIn(ANNAL.CURIE.placeholder,            view_field)
                self.assertIn(ANNAL.CURIE.field_placement,        view_field)
                if ANNAL.CURIE.field_entity_type in view_field:
                    if view_field[ANNAL.CURIE.field_entity_type] != "":
                        # Field is restricted to named type
                        # @@TODO: allow for subtypes?
                        self.assertEqual(
                            view_field[ANNAL.CURIE.field_entity_type], type_uri
                            )
                if is_repeat_field_render_type(render_type):
                    # Check extra fields
                    group_id = extract_entity_id(view_field[ANNAL.CURIE.group_ref])
                    self.assertIn(ANNAL.CURIE.repeat_label_add,    view_field)
                    self.assertIn(ANNAL.CURIE.repeat_label_delete, view_field)
                    # Check field group
                    field_group = RecordGroup.load(self.coll1, group_id, altscope="all")
                    self.assertEqual(field_group["@type"], [ANNAL.CURIE.Field_group])
                    self.assertEqual(field_group[ANNAL.CURIE.id],          group_id)
                    self.assertEqual(field_group[ANNAL.CURIE.type_id],     "_group")
                    #@@ self.assertEqual(field_group[ANNAL.CURIE.record_type], value_type)
                    self.check_type_fields("_group", 
                        field_group[ANNAL.CURIE.record_type], field_group[ANNAL.CURIE.group_fields]
                        )
                    # field_name is present only if different from field_id
                    # self.assertIn(ANNAL.CURIE.field_name,  list_field)
                enum_types = (
                    [ "Type", "View", "List", "Field"
                    , "Enum", "Enum_optional"
                    ])
                if render_type in enum_types:
                    self.assertIn(ANNAL.CURIE.field_ref_type, view_field)
            except Exception as e:
                log.warning("check_type_fields error %s, field_id %s, render_type %s"%(e, field_id, render_type))
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
            tcols = trows[i+1].find_all("div", class_="view-value")
            colln = "coll%d"%i
            self.assertEqual(tcols[0].a.string,  colln)
            self.assertEqual(tcols[0].a['href'], collection_view_url(colln))
        return
 
    # Test collection view
    def test_collection_view(self):
        u = collection_view_url(coll_id="coll1")
        s = self.get_page(u)

        self.assertEqual(s.title.string, "List entities with type information - Collection coll1")
        self.assertEqual(s.h2.string, "List entities with type information")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Default_list_all")

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
        self.assertEqual(s.h2.string, "Customize collection: Collection coll1")
        local_types_expected = make_field_choices(
            [ ("type1", "RecordType coll1/type1")
            , ("type2", "RecordType coll1/type2")
            ])
        local_lists_expected = make_field_choices(
            [ ("list1", "RecordList coll1/list1")
            , ("list2", "RecordList coll1/list2")
            ])
        local_views_expected = make_field_choices(
            [ ("view1", "RecordView coll1/view1")
            , ("view2", "RecordView coll1/view2")
            ])
        self.check_select_field(s, "typelist", local_types_expected, None)
        self.check_select_field(s, "listlist", local_lists_expected, None)
        self.check_select_field(s, "viewlist", local_views_expected, None)
        return

    # Default list all
    # Same as test_collection_view but using different URI
    def test_default_list_all(self):
        u = collection_entity_list_url(coll_id="coll1", list_id="Default_list_all")
        s = self.get_page(u)

        self.assertEqual(s.h2.string, "List entities with type information")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Default_list_all")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Type")
        self.assertEqual(thead[2].span.string, "Label")
        #@@ Original
        trows_expected = (
            [ [ "_list/list1",    ["list1",    "_list", "RecordList coll1/list1"] ]
            , [ "_list/list2",    ["list2",    "_list", "RecordList coll1/list2"] ]
            , [ "_type/type1",    ["type1",    "_type", "RecordType coll1/type1"] ]
            , [ "_type/type2",    ["type2",    "_type", "RecordType coll1/type2"] ]
            , [ "_user/testuser", ["testuser", "_user", "Test User"] ]
            , [ "_view/view1",    ["view1",    "_view", "RecordView coll1/view1"] ]
            , [ "_view/view2",    ["view2",    "_view", "RecordView coll1/view2"] ]
            , [ "type1/entity1",  ["entity1",  "type1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2",  ["entity2",  "type1", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3",  ["entity3",  "type1", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1",  ["entity1",  "type2", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2",  ["entity2",  "type2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3",  ["entity3",  "type2", "Entity coll1/type2/entity3"] ]
            ])
        #@@ Updated
        trows_expected = (
            [ [ "_list/list1",    ["list1",    "List",              "RecordList coll1/list1"] ]
            , [ "_list/list2",    ["list2",    "List",              "RecordList coll1/list2"] ]
            , [ "_type/type1",    ["type1",    "Type",              "RecordType coll1/type1"] ]
            , [ "_type/type2",    ["type2",    "Type",              "RecordType coll1/type2"] ]
            , [ "_user/testuser", ["testuser", "User permissions",  "Test User"] ]
            , [ "_view/view1",    ["view1",    "View",              "RecordView coll1/view1"] ]
            , [ "_view/view2",    ["view2",    "View",              "RecordView coll1/view2"] ]
            , [ "type1/entity1",  ["entity1",  "RecordType coll1/type1", "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2",  ["entity2",  "RecordType coll1/type1", "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3",  ["entity3",  "RecordType coll1/type1", "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1",  ["entity1",  "RecordType coll1/type2", "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2",  ["entity2",  "RecordType coll1/type2", "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3",  ["entity3",  "RecordType coll1/type2", "Entity coll1/type2/entity3"] ]
            ])
        self.check_list_row_data(s, trows_expected)

        # @@TODO: check entity and type links
        #         check_list_row_links?  or add 3rd element to each trows_expected
        return

    # Default list
    def test_default_list(self):
        u = collection_entity_list_url(coll_id="coll1", list_id="Default_list")
        s = self.get_page(u)

        self.assertEqual(s.h2.string, "List entities")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Default_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_list/list1",    ["list1",    "RecordList coll1/list1"] ]
            , [ "_list/list2",    ["list2",    "RecordList coll1/list2"] ]
            , [ "_type/type1",    ["type1",    "RecordType coll1/type1"] ]
            , [ "_type/type2",    ["type2",    "RecordType coll1/type2"] ]
            , [ "_user/testuser", ["testuser", "Test User"] ]
            , [ "_view/view1",    ["view1",    "RecordView coll1/view1"] ]
            , [ "_view/view2",    ["view2",    "RecordView coll1/view2"] ]
            , [ "type1/entity1",  ["entity1",  "Entity coll1/type1/entity1"] ]
            , [ "type1/entity2",  ["entity2",  "Entity coll1/type1/entity2"] ]
            , [ "type1/entity3",  ["entity3",  "Entity coll1/type1/entity3"] ]
            , [ "type2/entity1",  ["entity1",  "Entity coll1/type2/entity1"] ]
            , [ "type2/entity2",  ["entity2",  "Entity coll1/type2/entity2"] ]
            , [ "type2/entity3",  ["entity3",  "Entity coll1/type2/entity3"] ]
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

        self.assertEqual(s.h2.string, "Entity types")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Type_list")

        thead = (
            s.form.find("div", class_="thead")
                  .find("div", class_="row")
                  .find_all("div", class_="columns")
            )
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            [ [ "_type/_coll",             ["_coll",             "Collection"] ]
            , [ "_type/_enum_list_type",   ["_enum_list_type",   "List display type"] ]
            , [ "_type/_enum_render_type", ["_enum_render_type", "Field render type"] ]
            , [ "_type/_enum_value_mode",  ["_enum_value_mode",  "Field value mode"] ]
            , [ "_type/_enum_value_type",  ["_enum_value_type",  "Field value type"] ]
            , [ "_type/_field",            ["_field",            "Field"] ]
            , [ "_type/_group",            ["_group",            "Field group"] ]
            , [ "_type/_list",             ["_list",             "List"] ]
            , [ "_type/_type",             ["_type",             "Type"] ]
            , [ "_type/_user",             ["_user",             "User permissions"] ]
            , [ "_type/_view",             ["_view",             "View"] ]
            , [ "_type/_vocab",            ["_vocab",            "Vocabulary namespace"] ]
            , [ "_type/Default_type",      ["Default_type",      "Default record"] ]
            , [ "_type/type1",             ["type1",             "RecordType coll1/type1"] ]
            , [ "_type/type2",             ["type2",             "RecordType coll1/type2"] ]
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
        self.check_select_field(
            s, "Type_view",   
            no_selection("(view id)") + self.views_expected, "_view/Default_view"
            )
        self.check_select_field(
            s, "Type_list",
            no_selection("(list id)") + self.lists_expected, "_list/Default_list"
            )
        self.check_select_field(s, "view_choice", self.views_expected, "_view/Type_view")
        return

    # Edit/view type view
    def test_view_edit_type_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Type_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_type_fields_sorted()
        expect_fields = (
            [ "_field/Type_id"
            , "_field/Type_label"
            , "_field/Type_comment"
            , "_field/Type_uri"
            , "_field/Type_supertype_uris"
            , "_field/Type_view"
            , "_field/Type_list"
            , "_field/Type_aliases"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
            s, "List_type", 
            self.list_types_expected, 
            "_enum_list_type/List"
            )
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_type"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/Type_view"
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

        self.assertEqual(s.h2.string, "List definitions")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/List_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            # [ [ "_list/_initial_values",    ["_initial_values",     None] ]
            [ [ "_list/Default_list",       ["Default_list",        "List entities"                      ] ]
            , [ "_list/Default_list_all",   ["Default_list_all",    "List entities with type information"] ]
            , [ "_list/Enum_list_all",      ["Enum_list_all",       "List enumeration values and types"  ] ]
            , [ "_list/Field_group_list",   ["Field_group_list",    "Field groups"                       ] ]
            , [ "_list/Field_list",         ["Field_list",          "Field definitions"                  ] ]
            , [ "_list/List_list",          ["List_list",           "List definitions"                   ] ]
            , [ "_list/Type_list",          ["Type_list",           "Entity types"                       ] ]
            , [ "_list/User_list",          ["User_list",           "User permissions"                   ] ]
            , [ "_list/View_list",          ["View_list",           "View definitions"                   ] ]
            , [ "_list/Vocab_list",         ["Vocab_list",          "Vocabulary namespaces"              ] ]
            , [ "_list/list1",              ["list1",               "RecordList coll1/list1"             ] ]
            , [ "_list/list2",              ["list2",               "RecordList coll1/list2"             ] ]   
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
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/Default_type"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/Default_view"
            )
        self.check_input_type_value(s, "List_entity_selector", "text", "ALL")
        self.check_input_type_value(s, "List_target_type", "text", "")
        self.check_select_field(s, "view_choice", self.views_expected, "_view/List_view")
        return

    # Edit/view list view
    def test_view_edit_list_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="List_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_list_fields_sorted()
        expect_fields = (
            [ "_field/List_id"
            , "_field/List_type"
            , "_field/List_label"
            , "_field/List_comment"
            , "_field/List_default_type"
            , "_field/List_default_view"
            , "_field/List_entity_selector"
            , "_field/List_target_type"
            , "_field/List_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
        self.check_select_field(s, "List_type", self.list_types_expected, "_enum_list_type/List")
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_list"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/List_view"
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

        self.assertEqual(s.h2.string, "View definitions")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/View_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            # [ [ "_view/_initial_values",    ["_initial_values",     None] ]
            [ [ "_view/Collection_view",    ["Collection_view",     "Collection metadata"   ] ]
            , [ "_view/Default_view",       ["Default_view",        "Default record view"   ] ]
            , [ "_view/Enum_view",          ["Enum_view",           "Enumerated value view" ] ]
            , [ "_view/Field_group_view",   ["Field_group_view",    "Field group definition"] ]
            , [ "_view/Field_view",         ["Field_view",          "Field definition"      ] ]
            , [ "_view/List_view",          ["List_view",           "List definition"       ] ]
            , [ "_view/Type_view",          ["Type_view",           "Type definition"       ] ]
            , [ "_view/User_view",          ["User_view",           "User permissions"      ] ]
            , [ "_view/View_view",          ["View_view",           "View definition"       ] ]
            , [ "_view/Vocab_view",         ["Vocab_view",          "Vocabulary namespace"  ] ]
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
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
        return

    # Edit/view view view
    def test_view_edit_view_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="View_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_view_fields_sorted()
        expect_fields        = (
            [ "_field/View_id"
            , "_field/View_label"
            , "_field/View_comment"
            , "_field/View_target_type"
            , "_field/View_edit_view"
            , "_field/View_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
        self.check_select_field(s, "List_type", self.list_types_expected, "_enum_list_type/List")
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_view"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/View_view"
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
        self.check_type_list_view(
            "_group", "Field_group_list", "Field_group_view", ANNAL.CURIE.Field_group
            )
        return

    # List groups using group list
    def test_group_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="Field_group_list", type_id="_group", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.h2.string, "Field groups")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Field_group_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")

        trows_expected = (
            # [ [ "_group/_initial_values",          ["_initial_values"] ]
            [ [ "_group/Entity_see_also_r",    ["Entity_see_also_r",    "Links to further information"] ]
            , [ "_group/Group_field_group",    ["Group_field_group",    "Group field fields"] ]
            , [ "_group/List_field_group",     ["List_field_group",     "List field fields"] ]
            , [ "_group/Type_alias_group",     ["Type_alias_group",     "Field alias fields"] ]
            , [ "_group/Type_supertype_uri_r", ["Type_supertype_uri_r", "Supertype URIs"] ]
            , [ "_group/View_field_group",     ["View_field_group",     "View field fields"] ]
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
            s, "view_choice", self.views_expected, "_view/Field_group_view"
            )
        return

    # Edit/view group view
    def test_view_edit_group_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Field_group_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_group_fields_sorted()
        expect_fields = (
            [ "_field/Group_id"
            , "_field/Group_label"
            , "_field/Group_comment"
            , "_field/Group_target_type"
            , "_field/Group_fields"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
        self.check_input_type_value(s, "List_target_type", "text", "annal:Field_group")
        self.check_select_field(s, "List_type", self.list_types_expected, "_enum_list_type/List")
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_group"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/Field_group_view"
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

        self.assertEqual(s.h2.string, "Field definitions")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Field_list")

        thead = (
            s.form.find("div", class_="thead")
            .find("div", class_="row")
            .find_all("div", class_="columns")
            )
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Render type")
        self.assertEqual(thead[2].span.string, "Value type")
        self.assertEqual(thead[3].span.string, "Label")

        trows_expected = (
            #     Field selector                      Field id             Render type      Value type   Field label (?)
            # [ [ "_field/_initial_values",           ["_initial_values",   "Short text",    "annal:Text", None       ] ]
            [ [ "_field/Coll_comment",              ["Coll_comment",      "Markdown rich text", 
                                                                                            "annal:Richtext"         ] ]
            , [ "_field/Coll_default_list_id",      ["Coll_default_list_id", 
                                                                          "Display text",   "annal:Text"             ] ]
            , [ "_field/Coll_default_view_entity",  ["Coll_default_view_entity", 
                                                                          "Display text",   "annal:Text"             ] ]
            , [ "_field/Coll_default_view_id",      ["Coll_default_view_id", 
                                                                          "Display text",   "annal:Text"             ] ]
            , [ "_field/Coll_default_view_type",    ["Coll_default_view_type", 
                                                                          "Display text",   "annal:Text"             ] ]
            , [ "_field/Coll_parent",               ["Coll_parent",       "Optional entity choice",  
                                                                                            "annal:EntityRef"        ] ]
            , [ "_field/Coll_software_version",     ["Coll_software_version", 
                                                                          "Display text",   "annal:Text"             ] ]
            , [ "_field/Entity_comment",            ["Entity_comment",    "Markdown rich text", "annal:Richtext"     ] ]
            , [ "_field/Entity_id",                 ["Entity_id",         "Entity Id",      "annal:EntityRef"        ] ]
            , [ "_field/Entity_label",              ["Entity_label",      "Short text",     "annal:Text"             ] ]
            , [ "_field/Entity_see_also",           ["Entity_see_also",   "Web link",       "rdfs:Resource"          ] ]
            , [ "_field/Entity_see_also_r",         ["Entity_see_also_r", "Field group set as table", 
                                                                                            "rdfs:Resource"          ] ]
            , [ "_field/Entity_type",               ["Entity_type",       "Entity type Id", "annal:EntityRef"        ] ]
            , [ "_field/Enum_uri",                  ["Enum_uri",          "Identifier",     "annal:Identifier"       ] ]
            , [ "_field/Field_comment",             ["Field_comment",     "Multiline text", "annal:Longtext"         ] ]
            , [ "_field/Field_default",             ["Field_default",     "Short text",     "annal:Text"             ] ]
            , [ "_field/Field_entity_type",         ["Field_entity_type", "Identifier",     "annal:Identifier"       ] ]
            , [ "_field/Field_fieldref",            ["Field_fieldref",    "Identifier",     "annal:Identifier"       ] ]
            , [ "_field/Field_groupref",            ["Field_groupref",    "Optional entity ref", "annal:EntityRef"   ] ]
            , [ "_field/Field_id",                  ["Field_id",          "Entity Id",      "annal:EntityRef"        ] ]
            , [ "_field/Field_label",               ["Field_label",       "Short text",     "annal:Text"             ] ]
            , [ "_field/Field_missing",             ["Field_missing",     "Short text",     "annal:Text"             ] ]
            , [ "_field/Field_placeholder",         ["Field_placeholder", "Short text",     "annal:Text"             ] ]
            , [ "_field/Field_placement",           ["Field_placement",   "Position/size",  "annal:Placement"        ] ]
            , [ "_field/Field_property",            ["Field_property",    "Identifier",     "annal:Identifier"       ] ]
            , [ "_field/Field_render_type",         ["Field_render_type", "Entity choice",  "annal:EntityRef"        ] ]
            , [ "_field/Field_repeat_label_add",    ["Field_repeat_label_add", "Short text", "annal:Text"            ] ]
            , [ "_field/Field_repeat_label_delete", ["Field_repeat_label_delete", "Short text", "annal:Text"         ] ]
            , [ "_field/Field_restrict",            ["Field_restrict",    "Short text",     "annal:Text"             ] ]
            , [ "_field/Field_typeref",             ["Field_typeref",     "Optional entity ref", "annal:EntityRef"   ] ]
            , [ "_field/Field_value_mode",          ["Field_value_mode",  "Entity choice",  "annal:EntityRef"        ] ]
            , [ "_field/Field_value_type",          ["Field_value_type",  "Identifier",     "annal:Identifier"       ] ]
            , [ "_field/Group_comment",             ["Group_comment"             ] ]
            , [ "_field/Group_field_placement",     ["Group_field_placement"     ] ]
            , [ "_field/Group_field_property",      ["Group_field_property"      ] ]
            , [ "_field/Group_field_sel",           ["Group_field_sel"           ] ]
            , [ "_field/Group_fields",              ["Group_fields"              ] ]
            , [ "_field/Group_id",                  ["Group_id"                  ] ]
            , [ "_field/Group_label",               ["Group_label"               ] ]
            , [ "_field/Group_target_type",         ["Group_target_type"         ] ]
            , [ "_field/List_choice",               ["List_choice"               ] ]
            , [ "_field/List_comment",              ["List_comment"              ] ]
            , [ "_field/List_default_type",         ["List_default_type"         ] ]
            , [ "_field/List_default_view",         ["List_default_view"         ] ]
            , [ "_field/List_entity_selector",      ["List_entity_selector"      ] ]
            , [ "_field/List_field_placement",      ["List_field_placement"      ] ]
            , [ "_field/List_field_property",       ["List_field_property"       ] ]
            , [ "_field/List_field_sel",            ["List_field_sel"            ] ]
            , [ "_field/List_fields",               ["List_fields"               ] ]
            , [ "_field/List_id",                   ["List_id"                   ] ]
            , [ "_field/List_label",                ["List_label"                ] ]
            , [ "_field/List_target_type",          ["List_target_type"          ] ]
            , [ "_field/List_type",                 ["List_type"                 ] ]
            , [ "_field/Type_alias_source",         ["Type_alias_source"         ] ]
            , [ "_field/Type_alias_target",         ["Type_alias_target"         ] ]
            , [ "_field/Type_aliases",              ["Type_aliases"              ] ]
            , [ "_field/Type_comment",              ["Type_comment"              ] ]
            , [ "_field/Type_id",                   ["Type_id"                   ] ]
            , [ "_field/Type_label",                ["Type_label"                ] ]
            , [ "_field/Type_list",                 ["Type_list"                 ] ]
            , [ "_field/Type_supertype_uri",        ["Type_supertype_uri"        ] ]
            , [ "_field/Type_supertype_uris",       ["Type_supertype_uris"       ] ]
            , [ "_field/Type_uri",                  ["Type_uri"                  ] ]
            , [ "_field/Type_view",                 ["Type_view"                 ] ]
            , [ "_field/User_description",          ["User_description"          ] ]
            , [ "_field/User_id",                   ["User_id"                   ] ]
            , [ "_field/User_name",                 ["User_name"                 ] ]
            , [ "_field/User_permissions",          ["User_permissions"          ] ]
            , [ "_field/User_uri",                  ["User_uri"                  ] ]
            , [ "_field/View_choice",               ["View_choice"               ] ]
            , [ "_field/View_comment",              ["View_comment"              ] ]
            , [ "_field/View_edit_view",            ["View_edit_view"            ] ]
            , [ "_field/View_field_placement",      ["View_field_placement"      ] ]
            , [ "_field/View_field_property",       ["View_field_property"       ] ]
            , [ "_field/View_field_sel",            ["View_field_sel"            ] ]
            , [ "_field/View_fields",               ["View_fields"               ] ]
            , [ "_field/View_id",                   ["View_id"                   ] ]
            , [ "_field/View_label",                ["View_label"                ] ]
            , [ "_field/View_target_type",          ["View_target_type"          ] ]
            , [ "_field/Vocab_id",                  ["Vocab_id"                  ] ]
            , [ "_field/Vocab_uri",                 ["Vocab_uri"                 ] ]
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit field using field view
    def test_field_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_field",
            view_id="Field_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", None)
        self.check_input_type_value(s, "Field_value_type", "text", "annal:Text")
        self.check_input_type_value(s, "Field_label", "text", "")
        self.check_input_type_value(s, "Field_comment", "textarea", None)
        self.check_input_type_value(s, "Field_placeholder", "text", "")
        self.check_input_type_value(s, "Field_property", "text", "")
        # self.check_input_type_value(s, "Field_placement", "text", "")
        self.check_select_field(
            s, "Field_placement", 
            [FieldChoice("",label="(field position and size)")]+self.placements_expected, 
            ""
            )
        self.check_input_type_value(s, "Field_default", "text", None)
        self.check_input_type_value(s, "Field_entity_type", "text", "")
        self.check_input_type_value(s, "Field_restrict", "text", "")
        self.check_select_field(
            s, "Field_render_type",   self.render_types_expected, "_enum_render_type/Text"
            )
        self.check_select_field(
            s, "Field_typeref", 
            [FieldChoice("",label="(no type selected)")]+self.types_expected, 
            ""
            )
        self.check_select_field(
            s, "Field_groupref",
            [FieldChoice("",label="(no field group selected)")]+self.grouprefs_expected, 
            ""
            )
        self.check_select_field(
            s, "view_choice", self.views_expected, "_view/Field_view"
            )
        return

    # Edit/view field view
    def test_view_edit_field_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Field_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_field_fields_sorted()
        expect_fields = (
            [ "_field/Field_id"
            , "_field/Field_render_type"
            , "_field/Field_value_type"
            , "_field/Field_value_mode"
            , "_field/Field_label"
            , "_field/Field_comment"
            , "_field/Field_property"
            , "_field/Field_placement"
            , "_field/Field_typeref"
            , "_field/Field_fieldref"
            , "_field/Field_placeholder"
            , "_field/Field_default"
            , "_field/Field_groupref"
            , "_field/Field_repeat_label_add"
            , "_field/Field_repeat_label_delete"
            , "_field/Field_entity_type"
            , "_field/Field_restrict"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_field"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/Field_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for vocabulary namespaces
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for RecordGroup
    def test_recordlist_type_group_view(self):
        self.check_type_list_view(
            "_vocab", "Vocab_list", "Vocab_view", ANNAL.CURIE.Vocabulary
            )
        return

    # List vocabularies using vocab list
    def test_vocab_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="Vocab_list", type_id="_vocab", scope="all"
            )
        s = self.get_page(u)
        self.assertEqual(s.h2.string, "Vocabulary namespaces")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/Vocab_list")
        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "Id")
        self.assertEqual(thead[1].span.string, "Label")
        trows_expected = (
            # [ [ "_vocab/_initial_values",          ["_initial_values"] ]
            [ [ "_vocab/annal",                    ["annal",    "Vocabulary namespace for Annalist-defined terms"] ]
            , [ "_vocab/owl",                      ["owl",      "OWL ontology namespace"] ]
            , [ "_vocab/rdf",                      ["rdf",      "RDF core namespace"] ]
            , [ "_vocab/rdfs",                     ["rdfs",     "RDF schema namespace"] ]
            , [ "_vocab/xsd",                      ["xsd",      "XML Schema datatypes namespace"] ]
            ])
        self.check_list_row_data(s, trows_expected)
        return

    # Create/edit Vocabulary using vocab view
    def test_vocab_edit_new(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_vocab",
            view_id="Vocab_view", action="new"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id",              "text",     None)
        self.check_input_type_value(s, "Entity_label",           "text",     None)
        self.check_input_type_value(s, "Entity_comment",         "textarea", None)
        self.check_input_type_value(s, "Vocab_uri",              "text",     None)
        self.check_select_field(
            s, "view_choice", self.views_expected, "_view/Vocab_view"
            )
        return

    # Edit/view vocabulary view
    def test_view_edit_vocab_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="Vocab_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_vocab_fields_sorted()
        expect_fields = (
            [ "_field/Vocab_id"
            , "_field/Entity_label"
            , "_field/Entity_comment"
            , "_field/Vocab_uri"
            , "_field/Entity_see_also_r"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
        return

    # Edit/view vocabulary list
    def test_view_edit_vocab_list(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_list", entity_id="Vocab_list",
            view_id="List_view", action="edit"
            )
        s = self.get_page(u)
        self.check_input_type_value(s, "entity_id", "text", "Vocab_list")
        self.check_input_type_value(s, "List_label", "text", None)
        self.check_input_type_value(s, "List_comment", "textarea", None)
        self.check_input_type_value(
            s, "List_entity_selector", "text", "'annal:Vocabulary' in [@type]"
            )
        self.check_input_type_value(s, "List_target_type", "text", "annal:Vocabulary")
        self.check_select_field(s, "List_type", self.list_types_expected, "_enum_list_type/List")
        self.check_select_field(
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_vocab"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/Vocab_view"
            )
        return

    # --------------------------------------------------------------------------
    # Test site data for user permissions
    # --------------------------------------------------------------------------

    # Test type / list / view / field consistency for user
    def test_recorduser_type_field_view(self):
        self.check_type_list_view("_user", "User_list", "User_view", ANNAL.CURIE.User)
        return

    # List user permissions using user list
    def test_user_list(self):
        u = collection_entity_list_url(
            coll_id="coll1", list_id="User_list", type_id="_user", scope="all"
            )
        s = self.get_page(u)

        self.assertEqual(s.h2.string, "User permissions")
        self.check_input_type_value(s, "search_for", "text", "")
        self.check_select_field(s, "list_choice", self.lists_expected, "_list/User_list")

        thead = s.form.find("div", class_="thead").find("div", class_="row").find_all("div", class_="columns")
        self.assertEqual(thead[0].span.string, "User Id")
        self.assertEqual(thead[1].span.string, "User URI")
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
            # , [ "_user/admin", 
            #     [ "admin", "mailto:admin@localhost"
            #     , "VIEW CREATE UPDATE DELETE CONFIG CREATE_COLLECTION DELETE_COLLECTION ADMIN"
            #     ]
            #   ]
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
        self.check_select_field(s, "view_choice", self.views_expected, "_view/User_view")
        return

    # Edit/view user view
    def test_view_edit_user_view(self):
        u = collection_entity_edit_url(
            coll_id="coll1", type_id="_view", entity_id="User_view",
            view_id="View_view", action="edit"
            )
        s = self.get_page(u)
        expect_field_choices = no_selection("(field sel)") + get_site_user_fields_sorted()
        expect_fields = (
            [ "_field/User_id"
            , "_field/User_name"
            , "_field/User_description"
            , "_field/User_uri"
            , "_field/User_permissions"
            ])
        self.check_view_fields(s, expect_fields, expect_field_choices)
        self.check_select_field(s, "view_choice", self.views_expected, "_view/View_view")
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
            s, "List_default_type", 
            no_selection("(default record type)") + self.types_expected, 
            "_type/_user"
            )
        self.check_select_field(
            s, "List_default_view", 
            no_selection("(view id)") + self.views_expected, 
            "_view/User_view"
            )
        return

# End.
