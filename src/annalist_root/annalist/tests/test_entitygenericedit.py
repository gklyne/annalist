"""
Tests for generic EntityData editing view
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

from annalist.views.entityedit      import GenericEntityEditView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
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
    get_site_types, get_site_types_sorted,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   GenericEntityEditView tests
#
#   -----------------------------------------------------------------------------

class GenericEntityEditViewTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        self.type_ids   = ['testtype', 'Default_type']
        self.no_options = ['(no options)']
        self.view_options    = sorted(
            [ vid for vid in self.testcoll.child_entity_ids(RecordView, self.testsite) 
                  if vid != "_initial_values"
            ])
        self.list_options    = sorted(
            [ lid for lid in self.testcoll.child_entity_ids(RecordList, self.testsite) 
                  if lid != "_initial_values"
            ])
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
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

    def test_GenericEntityEditView(self):
        self.assertEqual(GenericEntityEditView.__name__, "GenericEntityEditView", "Check GenericEntityEditView class name")
        return

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
                entity_id="entityuseview", action="new", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entity_url("testcoll", "testtype", "entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_get_new_form_no_login(self):
        self.client.logout()
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_get_copy_form_no_login(self):
        self.client.logout()
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_get_edit_form_no_login(self):
        self.client.logout()
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        field_vals = default_fields(coll_id="testcoll", type_id="testtype", entity_id="00000001")
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
                  value="%(default_label_esc)s"/>
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
                            placeholder="(type description)">
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
            """%field_vals(width=6)
        # formrow5c = """
        #     <div class="%(button_wide_classes)s">
        #       <div class="row">
        #         <div class="%(button_right_classes)s">
        #           <input type="submit" name="open_view" value="Edit view" />
        #         </div>
        #       </div>
        #     </div>
        #     """%field_vals(width=4)
        formrow6 = ("""
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
                        sorted(get_site_views()),
                        "Type_view")+
                    """
                  </div>
                  <div class="small-3 columns">
                    <input type="submit" name="use_view"      value="Show view" />
                  </div>
                </div>
              </div>
            </div>
            """)%field_vals(width=6)
        formrow7 = """
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
        self.assertContains(r, formrow5a, html=True)
        self.assertContains(r, formrow5b, html=True)
        # self.assertContains(r, formrow5c, html=True)
        self.assertContains(r, formrow6,  html=True)
        # New buttons hidden (for now)
        # self.assertContains(r, formrow7, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        view_url = collection_entity_view_url(coll_id="testcoll", type_id="testtype", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 7)
        # 1st field - Id
        id_help = (
            "A short identifier that distinguishes this type from all other types in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Type_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(type id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "00000001")
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Label
        label_help = (
            "Short string used to describe record type when displayed"
            )
        label_value = default_label("testcoll", "testtype", "00000001")
        self.assertEqual(r.context['fields'][1]['field_id'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_help'], label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], label_value)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - comment
        comment_help = (
            "Descriptive text about a record type"
            )
        comment_value = default_comment("testcoll", "testtype", "00000001")
        self.assertEqual(r.context['fields'][2]['field_id'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_help'], comment_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(type description)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], comment_value)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field - URI
        uri_help = (
            "Entity type URI"
            )
        self.assertEqual(r.context['fields'][3]['field_id'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_label'], 'URI')
        self.assertEqual(r.context['fields'][3]['field_help'], uri_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], "(URI)")
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:uri")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][3]['field_value'], "")
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - view id
        view_id_help = (
            "Default view id for this type"
            )
        self.assertEqual(r.context['fields'][4]['field_id'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Default view')
        self.assertEqual(r.context['fields'][4]['field_help'], view_id_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], "(view id)")
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:type_view")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:View")
        self.assertEqual(r.context['fields'][4]['field_value'], "Default_view")
        self.assertEqual(r.context['fields'][4]['options'], self.view_options)
        # 6th field - list id
        list_id_help = (
            "Default list id for this type"
            )
        self.assertEqual(r.context['fields'][5]['field_id'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Default list')
        self.assertEqual(r.context['fields'][5]['field_help'], list_id_help)
        self.assertEqual(r.context['fields'][5]['field_placeholder'], "(list id)")
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:type_list")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:List")
        self.assertEqual(r.context['fields'][5]['field_value'], "Default_list")
        self.assertEqual(r.context['fields'][5]['options'], self.list_options)
        return

    def test_get_new_no_continuation(self):
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        view_url = collection_entity_view_url(coll_id="testcoll", type_id="testtype", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "")
        return

    def test_get_edit(self):
        # Note - this test uses Type_view to display en entity of type "testtype"
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
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
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self.assertEqual(len(r.context['fields']), 7)
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'], 'Type_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(type id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], "entity1")
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Label
        type_label_value = (
            "Entity testcoll/testtype/entity1"
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Type_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_value'], type_label_value)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - comment
        type_comment_value = (
            "Entity coll testcoll, type testtype, entity entity1"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Type_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Comment')
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][2]['field_value'], type_comment_value)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field - URI
        # (NOTE: blank unless explcicit value specified)
        self.assertEqual(r.context['fields'][3]['field_id'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Type_uri')
        self.assertEqual(r.context['fields'][3]['field_label'], 'URI')
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:uri")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][3]['field_value'], "")
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - view id
        self.assertEqual(r.context['fields'][4]['field_id'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Type_view')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Default view')
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:type_view")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:View")
        self.assertEqual(r.context['fields'][4]['field_value'], "Default_view")
        self.assertEqual(r.context['fields'][4]['options'], self.view_options)
        # 6th field - list id
        self.assertEqual(r.context['fields'][5]['field_id'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Type_list')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Default list')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:type_list")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:List")
        self.assertEqual(r.context['fields'][5]['field_value'], "Default_list")
        self.assertEqual(r.context['fields'][5]['options'], self.list_options)
        return

    def test_get_view_no_collection(self):
        u = entitydata_edit_url("edit", "no_collection", "_field", entity_id="entity1", view_id="Type_view")
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

    def test_get_edit_no_entity(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynone", view_id="Type_view")
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

    # @@TODO: consider changing Type_view to Default_view in the following

    #   -------- new entity --------

    def test_post_new_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity")
        return

    def test_post_new_entity_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_no_continuation(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new")
        f['continuation_url'] = ""
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity")
        return

    def test_post_new_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new", cancel="Cancel")
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    def test_post_new_entity_missing_id(self):
        f = entitydata_recordtype_view_form_data(action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordtype_view_context_data(action="new")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_entity_invalid_id(self):
        f = entitydata_recordtype_view_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        # log.info(repr(r.context['fields'][1]))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", type_id="Default_type", action="new")
        u = entitydata_edit_url("new", "testcoll", "Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "Default_type"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="Default_type", update_dict=
            { '@type':          ['annal:Default_type', 'annal:EntityData']
            , 'annal:uri':      f['Type_uri']   # because using Type_view
            })
        return

    def create_new_type(self, coll_id, type_id):
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = entitydata_recordtype_view_form_data(
            coll_id=coll_id, type_id="_type", entity_id=type_id,
            action="new"
            )
        u = entitydata_edit_url("new", coll_id, type_id="_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url(coll_id, "_type"))
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        return

    def test_new_entity_new_recorddata(self):
        # Checks logic for creating an entity which may require creation of new recorddata
        self.create_new_type("testcoll", "newtype")
        # Create new entity
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_default_view_form_data(entity_id="newentity", type_id="newtype", action="new")
        u = entitydata_edit_url("new", "testcoll", "newtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "newtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="newtype")
        return

    def test_new_entity_builtin_type(self):
        # Create new entity
        self.assertFalse(RecordField.exists(self.testcoll, "newfield", self.testsite))
        f = entitydata_default_view_form_data(
                entity_id="newfield", type_id="_field", orig_type="Default_type", action="new"
                )
        u = entitydata_edit_url("new", "testcoll", "Default_type", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "Default_type"))
        # Check new entity data created
        self.assertTrue(RecordField.exists(self.testcoll, "newfield", self.testsite))
        self._check_entity_data_values("newfield", type_id="_field", update_dict=
            { '@type':          ['annal:Field']
            })
        return

    def test_post_new_entity_add_view_field(self):
        self.assertFalse(EntityData.exists(self.testdata, "entityaddfield"))
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        f = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="new",
                add_view_field="View_fields"
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        c = continuation_url_param(w)
        a = "add_field=View_fields"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(a, r['location'])
        self._check_entity_data_values("entityaddfield")
        return

    def test_post_new_entity_add_view_field_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="new",
                add_view_field="View_fields"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_edit_view(self):
        self.assertFalse(EntityData.exists(self.testdata, "entityeditview"))
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        f = entitydata_recordtype_view_form_data(
                entity_id="entityeditview", action="new",
                open_view="Edit view"
                )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view")
        c = continuation_url_param(w)
        a = "add_field="
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertNotIn(a, r['location'])
        self._check_entity_data_values("entityeditview")
        return

    def test_post_new_entity_edit_view_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
                entity_id="entityeditview", action="new",
                open_view="Edit view"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_use_view(self):
        self.assertFalse(EntityData.exists(self.testdata, "entityuseview"))
        f = entitydata_default_view_form_data(
                entity_id="entityuseview", action="new", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview", update="Updated entity")
        return

    def test_post_new_entity_use_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entityuseview", action="new", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_view(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewview"))
        f = entitydata_default_view_form_data(
                entity_id="entitynewview", action="new", update="Updated entity", 
                new_view="New view"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview", update="Updated entity")
        return

    def test_post_new_entity_new_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewview", action="new", update="Updated entity", 
                new_view="New view"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_field(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewfield"))
        f = entitydata_default_view_form_data(
                entity_id="entitynewfield", action="new", update="Updated entity", 
                new_field="New field"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield", update="Updated entity")
        return

    def test_post_new_entity_new_field_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewfield", action="new", update="Updated entity", 
                new_field="New field"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_type(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewview"))
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="new", update="Updated entity", 
                new_type="New type"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_new_entity_new_type_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="new", update="Updated entity", 
                new_type="New type"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- copy type --------

    def test_post_copy_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_recordtype_view_form_data(entity_id="copytype", action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists
        self._check_entity_data_values("copytype")
        return

    def test_post_copy_entity_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(entity_id="copytype", action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_recordtype_view_form_data(entity_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    def test_post_copy_entity_missing_id(self):
        f = entitydata_recordtype_view_form_data(action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordtype_view_context_data(action="copy")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = entitydata_recordtype_view_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="copy"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_entity_add_view_field(self):
        self._create_entity_data("entyity1")
        self._check_entity_data_values("entyity1")
        f = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="copy", update="Updated entity", 
                add_view_field="View_fields"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        c = continuation_url_param(w)
        a = "add_field=View_fields"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(a, r['location'])
        self._check_entity_data_values("entityaddfield", update="Updated entity")
        return

    def test_post_copy_entity_add_view_field_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="copy", update="Updated entity", 
                add_view_field="View_fields"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_edit_view(self):
        self._create_entity_data("entyity1")
        self._check_entity_data_values("entyity1")
        f = entitydata_recordtype_view_form_data(
            entity_id="entityeditview", action="copy", update="Updated entity", 
            open_view="Edit view"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view"
            )
        w = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view"
            )
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityeditview", update="Updated entity")
        return

    def test_post_copy_entity_edit_view_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
            entity_id="entityeditview", action="copy", update="Updated entity", 
            open_view="Edit view"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_use_view(self):
        self._create_entity_data("entityuseview")
        self._check_entity_data_values("entityuseview")
        f = entitydata_default_view_form_data(
                entity_id="entityuseview1", action="copy", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview1", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview1", update="Updated entity")
        return

    def test_post_copy_entity_use_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entityuseview1", action="copy", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_new_view(self):
        self._create_entity_data("entitynewview")
        self._check_entity_data_values("entitynewview")
        f = entitydata_default_view_form_data(
                entity_id="entitynewview1", action="copy", update="Updated entity", 
                new_view="New view"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview1", update="Updated entity")
        return

    def test_post_copy_entity_new_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewview1", action="copy", update="Updated entity", 
                new_view="New view"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_new_field(self):
        self._create_entity_data("entitynewfield")
        self._check_entity_data_values("entitynewfield")
        f = entitydata_default_view_form_data(
                entity_id="entitynewfield1", action="copy", update="Updated entity", 
                new_field="New field"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield1", update="Updated entity")
        return

    def test_post_copy_entity_new_field_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewfield1", action="copy", update="Updated entity", 
                new_field="New field"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_new_type(self):
        self._create_entity_data("entitynewtype")
        self._check_entity_data_values("entitynewtype")
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype1", action="copy", update="Updated entity", 
                new_type="New type"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype1", update="Updated entity")
        return

    def test_post_copy_entity_new_type_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype1", action="copy", update="Updated entity", 
                new_type="New type"
                )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_entity_data("entityedit")
        e1 = self._check_entity_data_values("entityedit")
        f  = entitydata_recordtype_view_form_data(entity_id="entityedit", action="edit", update="Updated entity")
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedit", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity")
        return

    def test_post_edit_entity_blank_label_comment(self):
        self._create_entity_data("entityedit")
        e1 = self._check_entity_data_values("entityedit")
        f  = entitydata_recordtype_view_form_data(entity_id="entityedit", action="edit", update="Updated entity")
        f['Type_label']   = ""
        f['Type_comment'] = ""
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedit", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity", 
            update_dict=
                { 'rdfs:label':   ""
                , 'rdfs:comment': ""
                }
            )
        return

    def test_post_edit_entity_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(entity_id="edittype", action="edit")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_new_id(self):
        # Also tests continuation URL update whejn entity Id is changed
        self._create_entity_data("entityeditid1")
        e1 = self._check_entity_data_values("entityeditid1")
        c1 = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityeditid1", view_id="Type_view")
        # Now post edit form submission with different values and new id
        f  = entitydata_recordtype_view_form_data(
            entity_id="entityeditid2", orig_id="entityeditid1", action="edit"
            )
        f['continuation_url'] = c1
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditid1", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        c2 = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityeditid2", view_id="Type_view")
        self.assertEqual(r['location'], TestHostUri + c2)
        # self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "entityeditid1"))
        self._check_entity_data_values("entityeditid2")
        return

    def test_post_edit_entity_new_type(self):
        # NOTE that the RecordType_viewform does not include a type field, but the new-type
        # logic is checked by the test_entitydefaultedit suite
        self._create_entity_data("entityedittype")
        self._check_entity_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        newtype = RecordType.create(self.testcoll, "newtype", recordtype_create_values("newtype"))
        newtypedata = RecordTypeData(self.testcoll, "newtype")
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id
        f = entitydata_recordtype_view_form_data(
            entity_id="entityedittype", orig_id="entityedittype", 
            type_id="newtype", orig_type="testtype",
            action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedittype", view_id="Default_view")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(EntityData.exists(newtypedata, "entityedittype"))
        return

    def test_post_edit_entity_new_builtin_type(self):
        # Test logic for changing type to built-in type (_field)
        self._create_entity_data("entityedittype")
        self._check_entity_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id sert to "_field"
        f = entitydata_recordtype_view_form_data(
            entity_id="entityedittype", orig_id="entityedittype", 
            type_id="_field", orig_type="testtype",
            action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedittype", view_id="Default_view")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(RecordField.exists(self.testcoll, "entityedittype"))
        return

    def test_post_edit_entity_cancel(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Post from cancelled edit form
        f = entitydata_recordtype_view_form_data(entity_id="edittype", action="edit", cancel="Cancel", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that target record type still does not exist and unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_missing_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID missing
        f = entitydata_recordtype_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordtype_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID malformed
        f = entitydata_recordtype_view_form_data(

            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_add_view_field(self):
        self._create_entity_data("entityaddfield")
        e1 = self._check_entity_data_values("entityaddfield")
        f  = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="edit", update="Updated entity", 
                add_view_field="View_fields"
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        c = continuation_url_param(u)
        a = "add_field=View_fields"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(a, r['location'])
        self._check_entity_data_values("entityaddfield", update="Updated entity")
        return

    def test_post_edit_entity_add_view_field_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
                entity_id="entityaddfield", action="edit", update="Updated entity", 
                add_view_field="View_fields"
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_edit_view(self):
        self._create_entity_data("entityeditview")
        e1 = self._check_entity_data_values("entityeditview")
        f  = entitydata_recordtype_view_form_data(
                entity_id="entityeditview", action="edit", update="Updated entity", 
                open_view="Edit view"
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityeditview", update="Updated entity")
        return

    def test_post_edit_entity_edit_view_no_login(self):
        self.client.logout()
        f = entitydata_recordtype_view_form_data(
                entity_id="entityeditview", action="edit", update="Updated entity", 
                open_view="Edit view"
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_use_view(self):
        self._create_entity_data("entityuseview")
        e1 = self._check_entity_data_values("entityuseview")
        f  = entitydata_default_view_form_data(
                entity_id="entityuseview", action="edit", update="Updated entity", 
                use_view="Type_view", 
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview", update="Updated entity")
        return

    def test_post_edit_entity_use_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entityuseview", action="edit", update="Updated entity", 
                use_view="Type_view", 
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_new_view(self):
        self._create_entity_data("entitynewview")
        e1 = self._check_entity_data_values("entitynewview")
        f  = entitydata_default_view_form_data(
                entity_id="entitynewview", action="edit", update="Updated entity", 
                new_view="New view"
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview", update="Updated entity")
        return

    def test_post_edit_entity_new_view_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewview", action="edit", update="Updated entity", 
                new_view="New view"
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_new_field(self):
        self._create_entity_data("entitynewfield")
        e1 = self._check_entity_data_values("entitynewfield")
        f  = entitydata_default_view_form_data(
                entity_id="entitynewfield", action="edit", update="Updated entity", 
                new_field="New field"
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield", update="Updated entity")
        return

    def test_post_edit_entity_new_field_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewfield", action="edit", update="Updated entity", 
                new_field="New field"
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_new_type(self):
        self._create_entity_data("entitynewtype")
        e1 = self._check_entity_data_values("entitynewtype")
        f  = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="edit", update="Updated entity", 
                new_type="New type"
                )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_edit_entity_new_type_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="edit", update="Updated entity", 
                new_type="New type"
                )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- view current entity --------

    def test_post_edit_entity_view(self):
        self._create_entity_data("entityeditview")
        f = entitydata_default_view_form_data(entity_id="entityeditview", action="edit", view="View")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        e = TestHostUri + entitydata_edit_url(
            "view", "testcoll", "testtype", entity_id="entityeditview", view_id="Default_view"
            )
        l = continuation_url_param(entitydata_list_type_url("testcoll", "testtype"))
        c = continuation_url_param(u, prev_cont=l)
        self.assertIn(e, r['location'])
        self.assertIn(c, r['location'])
        # 'http://test.example.com/testsite/c/testcoll/v/Default_view/testtype/entityview/!edit
        #   ?continuation_url=/testsite/c/testcoll/v/Default_view/testtype/entityview/!view
        #   %3Fcontinuation_url=/testsite/c/testcoll/d/testtype/'
        return

    #   -------- view type --------

    def test_post_view_entity_use_view(self):
        self._create_entity_data("entityuseview")
        e1 = self._check_entity_data_values("entityuseview")
        # View doesn't return form entry field values...
        f  = entitydata_default_view_form_data(
                action="view",
                use_view="Type_view", 
                )
        u  = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview")
        return

# End.
