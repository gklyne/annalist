"""
Tests for generic EntityData non-editing view
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

from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout

from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityedit              import GenericEntityEditView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    site_dir, collection_dir, 
    continuation_url_param,
    collection_edit_url,
    collection_entity_view_url,
    site_title,
    render_select_options,
    render_choice_options,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_dir, 
    recordtype_edit_url,
    recordtype_create_values, 
    )
from entity_testentitydata          import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values,
    entitydata_delete_confirm_form_data,
    entitydata_default_view_context_data, entitydata_default_view_form_data,
    entitydata_recordtype_view_context_data, entitydata_recordtype_view_form_data,
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
from entity_testviewdata            import recordview_url
from entity_testlistdata            import recordlist_url

#   -----------------------------------------------------------------------------
#
#   GenericEntityViewView tests
#
#   -----------------------------------------------------------------------------

class GenericEntityViewViewTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        self.no_options = [ FieldChoice('', label="(no options)") ]
        self.no_view_id = [ FieldChoice('', label="(view id)") ]
        self.no_list_id = [ FieldChoice('', label="(list id)") ]
        self.view_options = get_site_views_linked("testcoll")
        self.list_options = get_site_lists_linked("testcoll")
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
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

    def _check_entity_data_values(self, entity_id, type_id="testtype", update="Entity", update_dict=None):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        # log.info("_check_entity_data_values: type_id %s, entity_id %s"%(type_id, entity_id))
        typeinfo = EntityTypeInfo(self.testsite, self.testcoll, type_id)
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, entity_id))
        e = typeinfo.entityclass.load(typeinfo.entityparent, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_view_url(""), TestHostUri + entity_url("testcoll", type_id, entity_id))
        v = entitydata_values(entity_id, type_id=type_id, update=update)
        if update_dict:
            v.update(update_dict)
            for k in update_dict:
                if update_dict[k] is None:
                    v.pop(k, None)
        # log.info(e.get_values())
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_default_form_no_login(self):
        self.client.logout()
        u = entity_url("testcoll", "testtype", "entity1")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    def test_post_default_form_use_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entityuseview", action="view",
                use_view="_view/Type_view", 
                )
        u = entity_url("testcoll", "testtype", "entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        return

    def test_get_view_form_no_login(self):
        self.client.logout()
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    def test_get_view_form_rendering(self):
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        cont_uri = "?continuation_url=%s"%u + "%%3Fcontinuation_url=/xyzzy/"
        cont_uri = ""
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
            entity_url       = "/testsite/c/testcoll/d/testtype/entity1/" + cont_uri,
            default_view_url = "/testsite/c/testcoll/d/_view/Default_view/" + cont_uri,
            default_list_url = "/testsite/c/testcoll/d/_list/Default_list/" + cont_uri
            )
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(entity_url)s">entity1</a>
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
                  <span>Entity testcoll/testtype/entity1</span>
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
                  <span class="markdown">
                    <p>Entity coll testcoll, type testtype, entity entity1</p>
                  </span>
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
                  <span>&nbsp;</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow5 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default view</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(default_view_url)s">Default record view</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow6 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Default list</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(default_list_url)s">List entities</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow7a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow7b = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_left_classes)s">
                  <input type="submit" name="edit"  value="Edit" />
                  <input type="submit" name="copy"  value="Copy" />
                  <input type="submit" name="close" value="Close" />
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        formrow7c = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_right_classes)s">
                  <input type="submit" name="open_view"     value="View description" />
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        formrow8 = ("""
            <div class="row view-value-row">
              <div class="%(label_classes)s">
                <span>Choose view</span>
              </div>
              <div class="%(input_classes)s">
                <div class="row">
                  <div class="small-9 columns">
                  """+
                    render_choice_options(
                      "view_choice",
                      self.view_options,
                      "_view/Type_view")+
                  """
                  </div>
                  <div class="small-3 columns">
                    <input type="submit" name="use_view"      value="Show view" />
                  </div>
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow9 = """
            <div class="%(button_right_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  <input type="submit" name="new_type"      value="New type" />
                  <input type="submit" name="new_view"      value="New view" />
                  <input type="submit" name="new_field"     value="New field type" />
                  <input type="submit" name="new_group"     value="New field group" />
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        # log.info(r.content)
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5,  html=True)
        self.assertContains(r, formrow6,  html=True)
        self.assertContains(r, formrow7a, html=True)
        self.assertContains(r, formrow7b, html=True)
        # self.assertContains(r, formrow7c, html=True)
        self.assertContains(r, formrow8,  html=True)
        # New buttons hidden (for now)
        # self.assertContains(r, formrow9, html=True)
        return

    def test_get_view(self):
        # Note - this test uses Type_view to display en entity of type "testtype"
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        view_url = collection_entity_view_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "entity1")
        self.assertEqual(r.context['orig_id'],          "entity1")
        self.assertEqual(r.context['action'],           "edit")
        # Fields
        self.assertEqual(len(r.context['fields']), 8)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'],           'Type_id')
        self.assertEqual(r.context['fields'][0]['field_name'],         'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'],        'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'],  "(type id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][0]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value'],        "entity1")
        self.assertEqual(r.context['fields'][0]['options'],            self.no_options)
        # 2nd field - Label
        type_label_value = (
            "Entity testcoll/testtype/entity1"
            )
        self.assertEqual(r.context['fields'][1]['field_id'],           'Type_label')
        self.assertEqual(r.context['fields'][1]['field_name'],         'Type_label')
        self.assertEqual(r.context['fields'][1]['field_label'],        'Label')
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][1]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value'],        type_label_value)
        self.assertEqual(r.context['fields'][1]['options'],            self.no_options)
        # 3rd field - comment
        type_comment_value = (
            "Entity coll testcoll, type testtype, entity entity1"
            )
        self.assertEqual(r.context['fields'][2]['field_id'],           'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_name'],         'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_label'],        'Comment')
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][2]['field_target_type'],  "annal:Richtext")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value'],        type_comment_value)
        self.assertEqual(r.context['fields'][2]['options'],            self.no_options)
        # 4th field - URI
        # (NOTE: blank unless explcicit value specified)
        self.assertEqual(r.context['fields'][3]['field_id'],           'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_name'],         'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_label'],        'URI')
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:uri")
        self.assertEqual(r.context['fields'][3]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][3]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value'],        "")
        self.assertEqual(r.context['fields'][3]['options'],            self.no_options)
        # 5th field - Supertype URIs
        type_supertype_uris_help = (
            "References to URIs/CURIEs of supertypes."
            )
        self.assertEqual(r.context['fields'][4]['field_id'],          'Type_supertype_uris')
        self.assertEqual(r.context['fields'][4]['field_name'],        'Type_supertype_uris')
        self.assertEqual(r.context['fields'][4]['field_label'],       'Supertype URIs')
        self.assertEqual(r.context['fields'][4]['field_help'],        type_supertype_uris_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], "(Supertype URIs or CURIEs)")
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:supertype_uris")
        self.assertEqual(r.context['fields'][4]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][4]['field_target_type'],  "annal:Type_supertype_uri")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value'],        "") #@@
        self.assertEqual(r.context['fields'][4]['options'],            self.no_options)
        # 6th field - view id
        self.assertEqual(r.context['fields'][5]['field_id'],           'Type_view')
        self.assertEqual(r.context['fields'][5]['field_name'],         'Type_view')
        self.assertEqual(r.context['fields'][5]['field_label'],        'Default view')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:type_view")
        self.assertEqual(r.context['fields'][5]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][5]['field_target_type'],  "annal:View")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][5]['field_value'],        "Default_view")
        self.assertEqual(r.context['fields'][5]['options'],            self.no_view_id + self.view_options)
        # 7th field - list id
        self.assertEqual(r.context['fields'][6]['field_id'],           'Type_list')
        self.assertEqual(r.context['fields'][6]['field_name'],         'Type_list')
        self.assertEqual(r.context['fields'][6]['field_label'],        'Default list')
        self.assertEqual(r.context['fields'][6]['field_property_uri'], "annal:type_list")
        self.assertEqual(r.context['fields'][6]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][6]['field_target_type'],  "annal:List")
        self.assertEqual(r.context['fields'][6]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][6]['field_value'],        "Default_list")
        self.assertEqual(r.context['fields'][6]['options'],            self.no_list_id + self.list_options)
        return

    def test_get_view_no_collection(self):
        u = entitydata_edit_url("view", "no_collection", "_field", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Collection no_collection does not exist", status_code=404)
        return

    def test_get_view_no_type(self):
        u = entitydata_edit_url("edit", "testcoll", "no_type", entity_id="entity1", view_id="Type_view")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Record type no_type in collection testcoll does not exist", status_code=404)
        return

    def test_get_view_no_view(self):
        u = entitydata_edit_url("edit", "testcoll", "_field", entity_id="entity1", view_id="no_view")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "Record view no_view in collection testcoll does not exist", status_code=404)
        return

    def test_get_view_no_entity(self):
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entitynone", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.debug(r.content)
        err_label = error_label("testcoll", "testtype", "entitynone")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%err_label, status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    def test_post_view_entity_close(self):
        self._create_entity_data("entityview")
        f = entitydata_default_view_form_data(entity_id="entityview", action="view", close="Close")
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self._check_entity_data_values("entityview")
        return

    def test_post_view_entity_edit(self):
        self._create_entity_data("entityview")
        f = entitydata_default_view_form_data(entity_id="entityview", action="view", edit="Edit")
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityview", view_id="Default_view"
            )
        l = continuation_url_param(entitydata_list_type_url("testcoll", "testtype"))
        c = continuation_url_param(u, prev_cont=l)
        self.assertIn(e, r['location'])
        self.assertIn(c, r['location'])
        # 'http://test.example.com/testsite/c/testcoll/v/Default_view/testtype/entityview/!edit
        #   ?continuation_url=/testsite/c/testcoll/v/Default_view/testtype/entityview/!view
        #   %3Fcontinuation_url=/testsite/c/testcoll/d/testtype/'
        return

    def test_post_view_entity_copy(self):
        self._create_entity_data("entityview")
        f = entitydata_default_view_form_data(entity_id="entityview", action="view", copy="Copy")
        u = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entityview", view_id="Default_view"
            )
        l = continuation_url_param(entitydata_list_type_url("testcoll", "testtype"))
        c = continuation_url_param(u, prev_cont=l)
        self.assertIn(e, r['location'])
        self.assertIn(c, r['location'])
        return

# End.
