"""
Tests for EntityData default editing view
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

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist                       import message

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

#@@ from annalist.views.defaultedit             import EntityDefaultEditView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    make_message, make_quoted_message,
    site_dir, collection_dir, 
    collection_edit_url,
    collection_create_values,
    site_title,
    render_select_options, render_choice_options,
    create_test_user,
    context_view_field,
    context_bind_fields
    )
from entity_testtypedata    import (
    recordtype_url,
    recordtype_edit_url,
    recordtype_create_values,
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitydata_recordtype_view_form_data,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata    import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted,
    get_site_list_types, get_site_list_types_sorted,
    get_site_views, get_site_views_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )

#   -----------------------------------------------------------------------------
#
#   Helper function to generate context value for testing
#   @@TODO: move this to a suppport module where it can be re-used
#
#   -----------------------------------------------------------------------------

#@@REMOVE

def __unused_default_view_context_data(
        coll_id="testcoll", type_it="testtype", entity_id=None, orig_id=None, type_ids=[],
        field_label=None,
        field_value_type="annal:Text",
        field_render_type="Text",
        field_value_mode="Value_direct",
        field_property="",
        field_placement="",
        field_superproperty_uris=None,
        field_placeholder="",
        field_tooltip=None,
        field_fields=[],
        field_repeat_label_add="Add",
        field_repeat_label_delete="Remove",
        field_entity_type="",
        action=None, update="Field"
    ):
    if not field_label:
        if field_id:
            field_label = "%s %s/_field/%s"%(update, coll_id, field_id)
        else:
            field_label = "%s data ... (testcoll/_field)"%(update)
    padding_placement = Placement(
        width=make_field_width(sw=0, mw=6, lw=6),
        offset=make_field_offset(so=0, mo=0, lo=0),
        display=make_field_display(sd=False, md=True, ld=True),
        field="hide-for-small-only medium-6 large-6 columns",
        label="small-4 columns",
        value="small-8 columns"
        )
    # @@TODO: re-work context structure used for testing so that field definitions present
    #         as an included dictionary, not as direct dictionary elements of bound_field.
    #         I'm not sure how extensive a re-work this would be, but there's an opportunity
    #         here to rationalize the test framework; e.g. define field desription values once
    #         and re-use, rather than duplicate values here.
    context_dict = (
        { "title":              "%s - Field definition - Collection %s"%(field_label, coll_id)
        , 'heading':            "Field definition"
        , 'coll_id':            coll_id
        , 'type_id':            "_field"
        , 'orig_id':            "orig_field_id"
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_field")
        , 'fields':
          [ context_field_row(
              get_bound_field("Field_id", field_id),                        # 0 (0,0)
              get_bound_field("Field_render_type", field_render_type)       # 1 (0,1)
              )
          , context_field_row(
              get_bound_field("Field_label", field_label)                   # 2 (1,0)
              )
          , context_field_row(
              get_bound_field("Field_help")                                 # 3 (2,0)
              )
          , context_field_row(
              get_bound_field("Field_property", field_property),            # 4 (3,0)
              get_bound_field("Field_placement", field_placement)           # 5 (3,1)
              )
          , get_bound_field('Field_superproperty_uris', field_superproperty_uris)
          , context_field_row(
              get_bound_field("Field_value_type", field_value_type),        # 7 (5,0)
              get_bound_field("Field_value_mode", field_value_mode)         # 8 (5,1)
              )
          , context_field_row(
              get_bound_field("Field_entity_type", field_entity_type)       # 9 (6,0)
              )
          , context_field_row(
              get_bound_field("Field_typeref"),                             # 10 (7,0)
              get_bound_field("Field_fieldref")                             # 11 (7,1)
              )
          , context_field_row(
              get_bound_field("Field_default")                              # 12 (8,0)
              )
          , context_field_row(
              get_bound_field("Field_placeholder", field_placeholder)       # 13 (9,0)
              )
          , context_field_row(
              get_bound_field("Field_tooltip", field_tooltip)               # 14 (10,0)
              )
          , get_bound_field("Field_fields", field_fields)                   # 15 (11,0)
          , context_field_row(
              get_bound_field("Field_repeat_label_add", field_repeat_label_add),
                                                                            # 16 (12,0)
              get_bound_field("Field_repeat_label_delete", field_repeat_label_delete)
                                                                            # 17 (12,1)
              )
          , context_field_row(
              get_bound_field("Field_restrict")                             # 18 (18,0)
              )
          ]
        })
    if field_id:
        context_dict['orig_id']     = field_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

#   -----------------------------------------------------------------------------
#
#   EntityDefaultEditView tests
#
#   -----------------------------------------------------------------------------

class EntityDefaultEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testcoll", "testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        self.type_ids = get_site_types_linked("testcoll")
        self.type_ids.append(FieldChoice("_type/testtype", 
                label="RecordType testcoll/testtype",
                link=recordtype_url("testcoll", "testtype")
            ))
        self.no_options = [ FieldChoice('', label="(no options)") ]
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
        #@@checkme@@ resetSitedata()
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

    def _check_entity_data_values(self, 
            entity_id, type_id="testtype", type_uri=None,
            update="Entity", parent=None, 
            update_dict=None):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        recorddata = RecordTypeData.load(self.testcoll, type_id)
        self.assertTrue(EntityData.exists(recorddata, entity_id))
        e = EntityData.load(recorddata, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_url(""), TestHostUri + entity_url("testcoll", type_id, entity_id))
        v = entitydata_values(entity_id, type_id=type_id, type_uri=type_uri, update=update)
        if update_dict:
            v.update(update_dict)
            for k in update_dict:
                if update_dict[k] is None:
                    v.pop(k, None)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    #@@
    # def test_EntityDefaultEditView(self):
    #     self.assertEqual(EntityDefaultEditView.__name__, "EntityDefaultEditView", "Check EntityDefaultEditView class name")
    #     return
    #@@

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "Collection testcoll")
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
            tooltip1=context_view_field(r.context, 0, 0)['field_tooltip'],
            tooltip2=context_view_field(r.context, 0, 1)['field_tooltip'],
            tooltip3=context_view_field(r.context, 1, 0)['field_tooltip'],
            tooltip4=context_view_field(r.context, 2, 0)['field_tooltip'],
            )
        formrow1 = """
              <div class="small-12 medium-6 columns" title="%(tooltip1)s">
                <div class="row view-value-row">
                  <div class="%(label_classes)s">
                      <span>Id</span>
                  </div>
                  <div class="%(input_classes)s">
                    <!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->
                    <input type="text" size="64" name="entity_id" 
                           placeholder="(entity id)" value="00000001">
                  </div>
                </div>
              </div>
            """%field_vals(width=6)
        formrow2 = ("""
              <div class="small-12 medium-6 columns" title="%(tooltip2)s">
                <div class="row view-value-row">
                  <div class="%(label_classes)s">
                      <span>Type</span>
                  </div>
                  <div class="%(input_classes)s">
                  """+
                    render_choice_options(
                        "entity_type",
                        self.type_ids,
                        "_type/testtype")+
                  """
                  </div>
                </div>
              </div>
            """)%field_vals(width=6)
        formrow3 = """
              <!-- editable text field -->
              <div class="small-12 columns" title="%(tooltip3)s">
                <div class="row view-value-row">
                  <div class="%(label_classes)s">
                      <span>Label</span>
                  </div>
                  <div class="%(input_classes)s">
                    <input type="text" size="64" name="Entity_label" 
                           placeholder="(label)" 
                           value="%(default_label_esc)s">
                  </div>
                </div>
              </div>
            """%field_vals(width=12)
        formrow4 = """
              <div class="small-12 columns" title="%(tooltip4)s">
                <div class="row view-value-row">
                  <div class="%(label_classes)s">
                      <span>Comment</span>
                  </div>
                  <div class="%(input_classes)s">
                    <textarea cols="64" rows="6" name="Entity_comment" 
                              class="small-rows-4 medium-rows-8"
                              placeholder="(description)">
                        %(default_comment_esc)s
                    </textarea>
                  </div>
                </div>
              </div>
            """%field_vals(width=12)
        # log.info("******\n"+r.content)
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context

        expect_context = entitydata_context_data(
            coll_id="testcoll", type_id="testtype", entity_id="00000001", orig_id=None,
            type_ref="testtype", type_choices=self.type_ids,
            entity_label="",
            entity_descr="",
            action="new", 
            update="Entity",
            continuation_url="/xyzzy/"
            )
        self.assertEqual(len(r.context['fields']), 3) # 4 fields over 3 rows
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)

        #@@REMOVE
        view_url = entity_url(coll_id="testcoll", type_id="testtype", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        # self.assertEqual(len(r.context['fields']), 3)
        # f0  = context_view_field(r.context, 0, 0)
        # f1  = context_view_field(r.context, 0, 1)
        # f2  = context_view_field(r.context, 1, 0)
        # f3  = context_view_field(r.context, 2, 0)
        # # 1st fieldtttff
        # self.assertEqual(f0.description['field_id'],            'Entity_id')
        # self.assertEqual(f0.description['field_name'],          'entity_id')
        # self.assertEqual(f0.description['field_label'],         'Id')
        # self.assertEqual(f0.description['field_placeholder'],   "(entity id)")
        # self.assertEqual(f0.description['field_property_uri'],  "annal:id")
        # self.assertEqual(f0.description['field_render_type'],   "EntityId")
        # self.assertEqual(f0.description['field_value_mode'],    "Value_direct")
        # self.assertEqual(f0.description['field_value_type'],    "annal:EntityRef")
        # self.assertEqual(f0.field_value,                        "00000001")
        # self.assertEqual(f0.entity_type_id,                     "testtype")
        # self.assertEqual(f0.options,                            self.no_options)
        # # 2nd field
        # self.assertEqual(f1['field_id'],            'Entity_type')
        # self.assertEqual(f1['field_name'],          'entity_type')
        # self.assertEqual(f1['field_label'],         'Type')
        # self.assertEqual(f1['field_placeholder'],   "(type id)")
        # self.assertEqual(f1['field_property_uri'],  "annal:type_id")
        # self.assertEqual(f1['field_render_type'],   "EntityTypeId")
        # self.assertEqual(f1['field_value_mode'],    "Value_direct")
        # self.assertEqual(f1['field_value_type'],    "annal:EntityRef")
        # self.assertEqual(f1.field_value,            "testtype")
        # self.assertEqual(f1['field_value'],         "testtype")
        # self.assertEqual(f1['entity_type_id'],      "testtype")
        # self.assertEqual(set(f1['options']),        set(self.type_ids))
        # # 3rd field
        # field_label_value = default_label("testcoll", "testtype", "00000001")
        # self.assertEqual(f2['field_id'],            'Entity_label')
        # self.assertEqual(f2['field_name'],          'Entity_label')
        # self.assertEqual(f2['field_label'],         'Label')
        # self.assertEqual(f2['field_placeholder'],   "(label)")
        # self.assertEqual(f2['field_property_uri'],  "rdfs:label")
        # self.assertEqual(f2['field_render_type'],   "Text")
        # self.assertEqual(f2['field_value_mode'],    "Value_direct")
        # self.assertEqual(f2['field_value_type'],    "annal:Text")
        # self.assertEqual(f2['field_value'],         field_label_value)
        # self.assertEqual(f2['entity_type_id'],      "testtype")
        # self.assertEqual(f2['options'],             self.no_options)
        # # 4th field
        # field_comment_value = default_comment("testcoll", "testtype", "00000001")
        # self.assertEqual(f3['field_id'],            'Entity_comment')
        # self.assertEqual(f3['field_name'],          'Entity_comment')
        # self.assertEqual(f3['field_label'],         'Comment')
        # self.assertEqual(f3['field_placeholder'],   "(description)")
        # self.assertEqual(f3['field_property_uri'],  "rdfs:comment")
        # self.assertEqual(f3['field_render_type'],   "Markdown")
        # self.assertEqual(f3['field_value_mode'],    "Value_direct")
        # self.assertEqual(f3['field_value_type'],    "annal:Richtext")
        # self.assertEqual(f3['field_value'],         field_comment_value)
        # self.assertEqual(f3['entity_type_id'],      "testtype")
        # self.assertEqual(f3['options'],             self.no_options)
        #@@
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, "<title>Entity testcoll/testtype/entity1 - Default record view - Collection testcoll</title>")
        # Test context
        #@@REMOVE
        view_url = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        self.assertEqual(r.context['entity_id'],        "entity1")
        self.assertEqual(r.context['orig_id'],          "entity1")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        #@@

        expect_context = entitydata_context_data(
            coll_id="testcoll", type_id="testtype", entity_id="entity1", 
            type_ref="testtype", type_choices=self.type_ids,
            entity_label="Entity testcoll/testtype/entity1",
            entity_descr="Entity coll testcoll, type testtype, entity entity1",
            action="edit", 
            update="Entity",
            continuation_url="/xyzzy/"
            )
        self.assertEqual(len(r.context['fields']), 3) # 4 fields over 3 rows
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
 
        #@@REMOVE
        # self.assertEqual(len(r.context['fields']), 3)
        # f0  = context_view_field(r.context, 0, 0)
        # f1  = context_view_field(r.context, 0, 1)
        # f2  = context_view_field(r.context, 1, 0)
        # f3  = context_view_field(r.context, 2, 0)
        # # 1st field
        # self.assertEqual(f0['field_id'],            'Entity_id')
        # self.assertEqual(f0['field_name'],          'entity_id')
        # self.assertEqual(f0['field_label'],         'Id')
        # self.assertEqual(f0['field_placeholder'],   "(entity id)")
        # self.assertEqual(f0['field_property_uri'],  "annal:id")
        # self.assertEqual(f0['field_render_type'],   "EntityId")
        # self.assertEqual(f0['field_value_mode'],    "Value_direct")
        # self.assertEqual(f0['field_value_type'],    "annal:EntityRef")
        # self.assertEqual(f0['field_value'],         "entity1")
        # self.assertEqual(f0['options'],             self.no_options)
        # # 2nd field
        # self.assertEqual(f1['field_id'],            'Entity_type')
        # self.assertEqual(f1['field_name'],          'entity_type')
        # self.assertEqual(f1['field_label'],         'Type')
        # self.assertEqual(f1['field_placeholder'],   "(type id)")
        # self.assertEqual(f1['field_property_uri'],  "annal:type_id")
        # self.assertEqual(f1['field_render_type'],   "EntityTypeId")
        # self.assertEqual(f1['field_value_mode'],    "Value_direct")
        # self.assertEqual(f1['field_value_type'],    "annal:EntityRef")
        # self.assertEqual(f1['field_value'],         "testtype")
        # self.assertEqual(set(f1['options']),        set(self.type_ids))
        # # 3rd field
        # field_label_value = (
        #     "Entity testcoll/testtype/entity1"
        #     )
        # self.assertEqual(f2['field_id'],            'Entity_label')
        # self.assertEqual(f2['field_name'],          'Entity_label')
        # self.assertEqual(f2['field_label'],         'Label')
        # self.assertEqual(f2['field_placeholder'],   "(label)")
        # self.assertEqual(f2['field_property_uri'],  "rdfs:label")
        # self.assertEqual(f2['field_render_type'],   "Text")
        # self.assertEqual(f2['field_value_mode'],    "Value_direct")
        # self.assertEqual(f2['field_value_type'],    "annal:Text")
        # self.assertEqual(f2['field_value'],         field_label_value)
        # self.assertEqual(f2['options'],             self.no_options)
        # # 4th field
        # field_comment_value = (
        #     "Entity coll testcoll, type testtype, entity entity1"
        #     )
        # self.assertEqual(f3['field_id'],            'Entity_comment')
        # self.assertEqual(f3['field_name'],          'Entity_comment')
        # self.assertEqual(f3['field_label'],         'Comment')
        # self.assertEqual(f3['field_placeholder'],   "(description)")
        # self.assertEqual(f3['field_property_uri'],  "rdfs:comment")
        # self.assertEqual(f3['field_render_type'],   "Markdown")
        # self.assertEqual(f3['field_value_mode'],    "Value_direct")
        # self.assertEqual(f3['field_value_type'],    "annal:Richtext")
        # self.assertEqual(f3['field_value'],         field_comment_value)
        # self.assertEqual(f3['options'],             self.no_options)
        #@@

        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynone")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.debug(r.content)
        err_label = error_label("testcoll", "testtype", "entitynone")
        msg_text  = make_message(message.ENTITY_DOES_NOT_EXIST, id="entitynone", label=err_label)
        self.assertContains(r, "<p>%s</p>"%msg_text, status_code=404)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    def test_post_new_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity")
        return

    def test_post_new_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", action="new", cancel="Cancel")
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    def test_post_new_entity_missing_id(self):
        f = entitydata_form_data(action="new")
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = entitydata_context_data(
            coll_id="testcoll", type_id="testtype", 
            entity_id="", orig_id="orig_entity_id",
            type_ref="", type_choices=self.type_ids,
            action="new"
            )
        self.assertEqual(len(r.context['fields']), 3) # 4 fields over 3 rows
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_new_entity_invalid_id(self):
        f = entitydata_form_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        #@@
        expect_context = entitydata_context_data(
            coll_id="testcoll", type_id="testtype", 
            entity_id="!badentity", orig_id="orig_entity_id",
            type_ref="_type/testtype", type_choices=self.type_ids,
            action="new"
            )
        #@@REMOVE
        bound_context = context_bind_fields(r.context)
        #@@
        bound_context = r.context
        self.assertDictionaryMatch(bound_context, expect_context)
        return

    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", type_id="Default_type", action="new")
        u = entitydata_edit_url("new", "testcoll", "Default_type")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "Default_type"))
        # Check new entity data created
        self._check_entity_data_values(
            "newentity", type_id="Default_type", type_uri="annal:Default_type",
            update_dict=
                { '@type': ['annal:Default_type', 'annal:EntityData'] }
            )
        return

    def test_new_entity_new_type(self):
        # Checks logic for creating an entity which may require creation of new recorddata
        # Create new type
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = entitydata_recordtype_view_form_data(
            coll_id="testcoll", type_id="_type", entity_id="newtype",
            action="new"
            )
        u = entitydata_edit_url("new", "testcoll", type_id="_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "_type"))
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        # Create new entity
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_form_data(entity_id="newentity", type_id="newtype", action="new")
        u = entitydata_edit_url("new", "testcoll", "newtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "newtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="newtype")
        return

    #   -------- copy type --------

    def test_post_copy_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(entity_id="copytype", action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists
        self._check_entity_data_values("copytype")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_form_data(entity_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    def test_post_copy_entity_missing_id(self):
        f = entitydata_form_data(action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = entitydata_context_data(
            action="copy", orig_id="orig_entity_id",
            type_ref="", type_choices=self.type_ids
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = entitydata_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="copy")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = entitydata_context_data(
            action="copy", entity_id="!badentity", orig_id="orig_entity_id",
            type_ref="_type/testtype", type_choices=self.type_ids
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_entity_data("entityedit")
        self._check_entity_data_values("entityedit")
        f  = entitydata_form_data(entity_id="entityedit", action="edit", update="Updated entity")
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedit")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity")
        return

    def test_post_edit_entity_new_id(self):
        self._create_entity_data("entityeditid1")
        e1 = self._check_entity_data_values("entityeditid1")
        # Now post edit form submission with different values and new id
        f  = entitydata_form_data(entity_id="entityeditid2", orig_id="entityeditid1", action="edit")
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditid1")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "entityeditid1"))
        self._check_entity_data_values("entityeditid2")
        return

    def test_post_edit_entity_new_type(self):
        self._create_entity_data("entityedittype")
        e1 = self._check_entity_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        newtype     = RecordType.create(self.testcoll, "newtype", recordtype_create_values("newtype"))
        newtypedata = RecordTypeData(self.testcoll, "newtype")
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id
        f = entitydata_form_data(
            entity_id="entityedittype", orig_id="entityedittype", 
            type_id="newtype", orig_type="testtype",
            action="edit")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedittype")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type data now exists, and that new record exists and old does not
        self.assertTrue(RecordTypeData.exists(self.testcoll, "newtype"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(EntityData.exists(newtypedata, "entityedittype"))
        self._check_entity_data_values("entityedittype", type_id="newtype")
        return

    def test_post_edit_entity_cancel(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Post from cancelled edit form
        f = entitydata_form_data(entity_id="edittype", action="edit", cancel="Cancel", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype")
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
        f = entitydata_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_context_data(
            action="edit", update="Updated entity",
            orig_id="orig_entity_id",
            type_ref="", type_choices=self.type_ids
            )
        self.assertEqual(len(r.context['fields']), 3) # 4 fields over 3 rows
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID malformed
        f = entitydata_form_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit",
            type_ref="_type/testtype", type_choices=self.type_ids
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

# End.
