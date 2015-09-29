"""
Tests for RecordType module and view

Note: this module tests for rendering specifically for RecordType values, using
type description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.entitydata         import EntityData
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.recordview         import RecordView
from annalist.models.recordlist         import RecordList

from annalist.views.recordtypedelete        import RecordTypeDeleteConfirmedView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                              import init_annalist_test_site, resetSitedata
from AnnalistTestCase                   import AnnalistTestCase
from entity_testutils                   import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_test_user
    )
from entity_testtypedata                import (
    recordtype_dir,
    recordtype_coll_url, recordtype_site_url, recordtype_url, recordtype_edit_url,
    recordtype_value_keys, recordtype_load_keys, 
    recordtype_create_values, recordtype_values, recordtype_read_values,
    recordtype_entity_view_context_data, 
    recordtype_entity_view_form_data, recordtype_delete_confirm_form_data
    )
from entity_testentitydata              import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata            import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from entity_testviewdata                import recordview_url
from entity_testlistdata                import recordlist_url

#   -----------------------------------------------------------------------------
#
#   RecordType tests
#
#   -----------------------------------------------------------------------------

class RecordTypeTest(AnnalistTestCase):
    """
    Tests for RecordType object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def test_RecordTypeTest(self):
        self.assertEqual(RecordType.__name__, "RecordType", "Check RecordType class name")
        return

    def test_recordtype_init(self):
        t = RecordType(self.testcoll, "testtype", self.testsite)
        u = recordtype_coll_url(self.testsite, coll_id="testcoll", type_id="testtype")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.Type)
        self.assertEqual(t._entityfile,     layout.TYPE_META_FILE)
        self.assertEqual(t._entityref,      layout.META_TYPE_REF)
        self.assertEqual(t._entityid,       "testtype")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordtype_dir(type_id="testtype"))
        self.assertEqual(t._values,         None)
        return

    def test_recordtype1_data(self):
        t = RecordType(self.testcoll, "type1", self.testsite)
        self.assertEqual(t.get_id(), "type1")
        self.assertEqual(t.get_type_id(), "_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/type1/", t.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_type/type1/", t.get_view_url())
        t.set_values(recordtype_create_values(type_id="type1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype2_data(self):
        t = RecordType(self.testcoll, "type2", self.testsite)
        self.assertEqual(t.get_id(), "type2")
        self.assertEqual(t.get_type_id(), "_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/type2/", t.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_type/type2/", t.get_view_url())
        t.set_values(recordtype_create_values(type_id="type2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_value_keys()))
        v = recordtype_values(type_id="type2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_create_load(self):
        t  = RecordType.create(self.testcoll, "type1", recordtype_create_values(type_id="type1"))
        td = RecordType.load(self.testcoll, "type1").get_values()
        v  = recordtype_read_values(type_id="type1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordtype_default_data(self):
        t = RecordType.load(self.testcoll, "Default_type", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Default_type")
        self.assertIn("/c/testcoll/_annalist_collection/types/Default_type", t.get_url())
        self.assertEqual(t.get_type_id(), "_type")
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordtype_load_keys(type_uri=True)))
        v = recordtype_read_values(type_id="Default_type")
        v.update(
            { 'rdfs:label':     'Default record'
            , 'rdfs:comment':   'Default record type, applied when no type is specified when creating a record.'
            , 'annal:uri':      'annal:Default_type'
            })
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordTypeEditView tests
#
#   -----------------------------------------------------------------------------

class RecordTypeEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.no_options = [ FieldChoice('', label="(no options)") ]
        self.no_view_id = [ FieldChoice('', label="(view id)") ]
        self.no_list_id = [ FieldChoice('', label="(list id)") ]
        self.view_options = self.no_view_id + get_site_views_linked("testcoll")
        self.list_options = self.no_list_id + get_site_lists_linked("testcoll")
        # For checking Location: header values...
        self.continuation_url = TestHostUri + entitydata_list_type_url(coll_id="testcoll", type_id="_type")
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_type(self, type_id, entity_id="testentity"):
        "Helper function creates record type entry with supplied type_id"
        t = RecordType.create(self.testcoll, type_id, recordtype_create_values(type_id=type_id))
        d = RecordTypeData.create(self.testcoll, type_id, {})
        e = EntityData.create(d, entity_id, {})
        return (t, d, e)

    def _check_record_type_values(self, type_id, 
            update="RecordType", 
            type_uri=None,
            extra_values=None
            ):
        "Helper function checks content of record type entry with supplied type_id"
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        t = RecordType.load(self.testcoll, type_id)
        self.assertEqual(t.get_id(), type_id)
        self.assertEqual(t.get_view_url(), TestHostUri + recordtype_url("testcoll", type_id))
        v = recordtype_values(
            type_id=type_id, 
            update=update, 
            type_uri=type_uri
            )
        if extra_values:
            v.update(extra_values)
        # print "t: "+repr(t.get_values())
        # print "v: "+repr(v)
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    def _check_context_fields(self, response, 
            type_id="(?type_id)", 
            type_label="(?type_label)",
            type_help="(?type_help)",
            type_uri="(?type_uri)",
            type_supertype_uris="",
            type_view="_view/Default_view",
            type_list="_list/Default_list"
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 8)
        # 1st field - Id
        type_id_help = (
            "A short identifier that distinguishes this type from all other types in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'],           'Type_id')
        self.assertEqual(r.context['fields'][0]['field_name'],         'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'],        'Id')
        self.assertEqual(r.context['fields'][0]['field_help'],         type_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'],  "(type id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][0]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value'],        type_id)
        self.assertEqual(r.context['fields'][0]['options'],            self.no_options)
        # 2nd field - Label
        type_label_help = (
            "Short string used to describe record type when displayed"
            )
        self.assertEqual(r.context['fields'][1]['field_id'],          'Type_label')
        self.assertEqual(r.context['fields'][1]['field_name'],        'Type_label')
        self.assertEqual(r.context['fields'][1]['field_label'],       'Label')
        self.assertEqual(r.context['fields'][1]['field_help'],        type_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][1]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value'],        type_label)
        self.assertEqual(r.context['fields'][1]['options'],            self.no_options)
        # 3rd field - comment
        type_comment_help = (
            "Descriptive text about a record type"
            )
        type_comment_placeholder = (
            "(type description)"
            )
        self.assertEqual(r.context['fields'][2]['field_id'],          'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_name'],        'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_label'],       'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'],        type_comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], type_comment_placeholder)
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][2]['field_target_type'],  "annal:Richtext")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value'],        type_help)
        self.assertEqual(r.context['fields'][2]['options'],            self.no_options)
        # 4th field - URI
        type_uri_help = (
            "Entity type URI"
            )
        type_uri_placeholder = (
            "(URI)"
            )
        self.assertEqual(r.context['fields'][3]['field_id'],          'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_name'],        'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_label'],       'URI')
        self.assertEqual(r.context['fields'][3]['field_help'],        type_uri_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], type_uri_placeholder)
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:uri")
        self.assertEqual(r.context['fields'][3]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][3]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value'],        type_uri)
        self.assertEqual(r.context['fields'][3]['options'],            self.no_options)
        # 5th field - Supertype URIs
        type_supertype_uris_help = (
            "References to URIs/CURIEs of supertypes."
            )
        type_supertype_uris_placeholder = (
            "(Supertype URIs or CURIEs)"
            )
        self.assertEqual(r.context['fields'][4]['field_id'],          'Type_supertype_uris')
        self.assertEqual(r.context['fields'][4]['field_name'],        'Type_supertype_uris')
        self.assertEqual(r.context['fields'][4]['field_label'],       'Supertype URIs')
        self.assertEqual(r.context['fields'][4]['field_help'],        type_supertype_uris_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], type_supertype_uris_placeholder)
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:supertype_uris")
        self.assertEqual(r.context['fields'][4]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][4]['field_target_type'],  "annal:Type_supertype_uri")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value'],        type_supertype_uris)
        self.assertEqual(r.context['fields'][4]['options'],            self.no_options)
        # 6th field - view id
        type_view_id_help = (
            "Default view id for this type"
            )
        type_view_id_placeholder = (
            "(view id)"
            )
        self.assertEqual(r.context['fields'][5]['field_id'],          'Type_view')
        self.assertEqual(r.context['fields'][5]['field_name'],        'Type_view')
        self.assertEqual(r.context['fields'][5]['field_label'],       'Default view')
        self.assertEqual(r.context['fields'][5]['field_help'],        type_view_id_help)
        self.assertEqual(r.context['fields'][5]['field_placeholder'], type_view_id_placeholder)
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:type_view")
        self.assertEqual(r.context['fields'][5]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][5]['field_target_type'],  "annal:View")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][5]['field_value'],        type_view)
        self.assertEqual(r.context['fields'][5]['options'],            self.view_options)
        # 7th field - list id
        type_list_id_help = (
            "Default list id for this type"
            )
        type_list_id_placeholder = (
            "(list id)"
            )
        self.assertEqual(r.context['fields'][6]['field_id'],          'Type_list')
        self.assertEqual(r.context['fields'][6]['field_name'],        'Type_list')
        self.assertEqual(r.context['fields'][6]['field_label'],       'Default list')
        self.assertEqual(r.context['fields'][6]['field_help'],        type_list_id_help)
        self.assertEqual(r.context['fields'][6]['field_placeholder'], type_list_id_placeholder)
        self.assertEqual(r.context['fields'][6]['field_property_uri'], "annal:type_list")
        self.assertEqual(r.context['fields'][6]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][6]['field_target_type'],  "annal:List")
        self.assertEqual(r.context['fields'][6]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][6]['field_value'],        type_list)
        self.assertEqual(r.context['fields'][6]['options'],            self.list_options)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, "<title>Collection testcoll</title>")
        self.assertContains(r, "<h3>'_type' data in collection 'testcoll'</h3>")
        field_vals = default_fields(coll_id="testcoll", type_id="_type", entity_id="00000001")
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(type id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Type_label" 
                         placeholder="(label)" 
                         value="%(default_label_esc)s" />
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Comment</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Type_comment" 
                            class="small-rows-4 medium-rows-8"
                            placeholder="(type description)"
                            >
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>URI</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Type_uri" 
                         placeholder="(URI)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow5a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow5b = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_left_classes)s">
                  <input type="submit" name="save"      value="Save" />
                  <input type="submit" name="view"      value="View" />
                  <input type="submit" name="cancel"    value="Cancel" />
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        formrow5c = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_right_classes)s">
                  &nbsp;
                  <input name="Define_view_list" value="Define view+list" type="submit">
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5a, html=True)
        self.assertContains(r, formrow5b, html=True)
        self.assertContains(r, formrow5c, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        type_url = collection_entity_view_url(coll_id="testcoll", type_id="_type", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            type_id="00000001",
            type_label=default_label("testcoll", "_type", "00000001"),
            type_help=default_comment("testcoll", "_type", "00000001"),
            type_uri="", type_supertype_uris=""
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(coll_id="testcoll", type_id="_type", entity_id="Default_type")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "Default_type")
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            type_id="Default_type",
            type_label="Default record",
            type_help="Default record type, applied when no type is specified when creating a record.",
            type_uri="", type_supertype_uris=""
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="notype", view_id="Type_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", "_type", "notype")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(coll_id="testcoll", type_id="_type", entity_id="Default_type")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_type")
        self.assertEqual(r.context['entity_id'],        "Default_type")
        self.assertEqual(r.context['orig_id'],          "Default_type")
        self.assertEqual(r.context['entity_uri'],       "annal:Default_type")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            type_id="Default_type",
            type_label="Default record",
            type_help="Default record type, applied when no type is specified when creating a record.",
            type_uri="annal:Default_type", type_supertype_uris=""
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="notype", view_id="Type_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", "_type", "notype")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(
            type_id="newtype", action="new", update="RecordType",
            type_uri="test:type"
            )
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("newtype", update="RecordType", type_uri="test:type")
        return

    def test_post_new_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_entity_view_form_data(
            type_id="newtype", action="new", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        return

    def test_post_new_type_missing_id(self):
        f = recordtype_entity_view_form_data(action="new", update="RecordType")
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(action="new", update="RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", update="RecordType"
            )
        u = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="orig_type_id", action="new", update="RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy type --------

    def test_post_copy_type(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", update="RecordType"
            )
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("copytype", update="RecordType")
        return

    def test_post_copy_type_cancel(self):
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        f = recordtype_entity_view_form_data(
            type_id="copytype", orig_id="Default_type", action="copy", cancel="Cancel", update="RecordType"
            )
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record type still does not exist
        self.assertFalse(RecordType.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_type_missing_id(self):
        f = recordtype_entity_view_form_data(
            action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        expect_context = recordtype_entity_view_context_data(action="copy", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_type_invalid_id(self):
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="Default_type", action="copy", update="Updated RecordType"
            )
        u = entitydata_edit_url("copy", "testcoll", "_type", entity_id="Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="Default_type", 
            action="copy", update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_type(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_record_type_values("edittype", update="Updated RecordType")
        return

    def test_post_edit_type_new_id(self):
        # Check logic applied when type is renamed
        (t, d1, e1) = self._create_record_type("edittype1", entity_id="typeentity")
        self.assertTrue(RecordType.exists(self.testcoll, "edittype1"))
        self.assertFalse(RecordType.exists(self.testcoll, "edittype2"))
        self.assertTrue(RecordTypeData.exists(self.testcoll, "edittype1"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "edittype2"))
        self.assertTrue(EntityData.exists(d1, "typeentity"))
        self._check_record_type_values("edittype1")
        f = recordtype_entity_view_form_data(
            type_id="edittype2", orig_id="edittype1", 
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="edittype1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists and old does not
        self.assertFalse(RecordType.exists(self.testcoll, "edittype1"))
        self.assertTrue(RecordType.exists(self.testcoll, "edittype2"))
        self._check_record_type_values("edittype2", update="Updated RecordType")
        # Check that type data directory has been renamed
        self.assertFalse(RecordTypeData.exists(self.testcoll, "edittype1"))
        self.assertTrue(RecordTypeData.exists(self.testcoll, "edittype2"))
        self.assertFalse(EntityData.exists(d1, "typeentity"))
        d2 = RecordTypeData.load(self.testcoll, "edittype2")
        self.assertTrue(EntityData.exists(d2, "typeentity"))
        return

    def test_post_edit_type_cancel(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        f = recordtype_entity_view_form_data(
            type_id="edittype", orig_id="edittype", 
            action="edit", cancel="Cancel", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record type still does not exist and unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_missing_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with ID missing
        f = recordtype_entity_view_form_data(
            action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordtype_entity_view_context_data(action="edit", update="Updated RecordType")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    def test_post_edit_type_invalid_id(self):
        self._create_record_type("edittype")
        self._check_record_type_values("edittype")
        # Form post with invalid ID
        f = recordtype_entity_view_form_data(
            type_id="!badtype", orig_id="edittype", action="edit", update="Updated RecordType"
            )
        u = entitydata_edit_url("edit", "testcoll", "_type", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record type identifier</h3>")
        # Test context
        expect_context = recordtype_entity_view_context_data(
            type_id="!badtype", orig_id="edittype", 
            action="edit", update="Updated RecordType"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_record_type_values("edittype")
        return

    #   -------- define view+list --------

    def test_define_view_list_task(self):
        # Create new type
        self._create_record_type("tasktype")
        self._check_record_type_values("tasktype")
        # Post define view+list
        f = recordtype_entity_view_form_data(
            type_id="tasktype",
            type_uri="test:tasktype",
            task="Define_view_list"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "_type", entity_id="tasktype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # Check content of type, view and list
        common_vals = (
            { 'type_id':      "tasktype"
            })
        expect_type_values = (
            { 'annal:type':         "annal:Type"
            , 'rdfs:label':         "RecordType testcoll/%(type_id)s"%common_vals
            , 'annal:uri':          "test:%(type_id)s"%common_vals
            , 'annal:type_view':    "_view/%(type_id)s"%common_vals
            , 'annal:type_list':    "_list/%(type_id)s"%common_vals
            })
        expect_view_values = (
            { 'annal:type':         "annal:View"
            , 'rdfs:label':         "View of RecordType testcoll/%(type_id)s"%common_vals
            , 'rdfs:comment':       "View of RecordType testcoll/%(type_id)s"%common_vals
            , 'annal:record_type':  "test:%(type_id)s"%common_vals
            })
        expect_list_values = (
            { 'annal:type':         "annal:List"
            , 'rdfs:label':         "List of RecordType testcoll/%(type_id)s"%common_vals
            , 'rdfs:comment':       "List of RecordType testcoll/%(type_id)s"%common_vals
            , 'annal:default_view': "_view/%(type_id)s"%common_vals
            , 'annal:default_type': "_type/%(type_id)s"%common_vals
            , 'annal:record_type':  "test:%(type_id)s"%common_vals
            , 'annal:display_type': "List"
            , 'annal:list_entity_selector': "'test:%(type_id)s' in [@type]"%common_vals
            })
        self.check_entity_values("_type", "%(type_id)s"%common_vals, expect_type_values)
        self.check_entity_values("_view", "%(type_id)s"%common_vals, expect_view_values)
        self.check_entity_values("_list", "%(type_id)s"%common_vals, expect_list_values)
        return

#   -----------------------------------------------------------------------------
#
#   ConfirmRecordTypeDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmRecordTypeDeleteTests(AnnalistTestCase):
    """
    Tests for record type deletion on response to confirmation form
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        return

    def test_CollectionActionViewTest(self):
        self.assertEqual(RecordTypeDeleteConfirmedView.__name__, "RecordTypeDeleteConfirmedView", "Check RecordTypeDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_type(self):
        t = RecordType.create(self.testcoll, "deletetype", recordtype_create_values("deletetype"))
        self.assertTrue(RecordType.exists(self.testcoll, "deletetype"))
        # Submit positive confirmation
        u = TestHostUri + recordtype_edit_url("delete", "testcoll")
        f = recordtype_delete_confirm_form_data("deletetype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_url("testcoll")+
            r"\?info_head=.*&info_message=.*deletetype.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordType.exists(self.testcoll, "deletetype"))
        return

# End.
