"""
Tests for RecordView module and view

Note: this module tests for rendering specifically for RecordView values, using
view description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import json
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
from annalist.models.recordview         import RecordView
from annalist.models.recordfield        import RecordField

from annalist.views.uri_builder             import uri_with_params
from annalist.views.recordviewdelete        import RecordViewDeleteConfirmedView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from tests                              import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from tests                              import init_annalist_test_site, resetSitedata
from AnnalistTestCase                   import AnnalistTestCase
from entity_testutils                   import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    render_select_options,
    create_test_user
    )
from entity_testviewdata                import (
    recordview_dir,
    recordview_coll_url, recordview_site_url, recordview_url, recordview_edit_url,
    recordview_value_keys, recordview_load_keys, 
    recordview_create_values, recordview_values, recordview_read_values,
    recordview_entity_view_context_data, recordview_entity_view_form_data, 
    # recordview_view_context_data, recordview_view_form_data, 
    recordview_delete_confirm_form_data
    )
from entity_testentitydata              import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata                import (
    make_field_choices, no_selection,
    get_site_default_entity_fields_sorted,
    get_site_bibentry_fields_sorted
    ) 

#   -----------------------------------------------------------------------------
#
#   RecordView tests
#
#   -----------------------------------------------------------------------------

class RecordViewTest(AnnalistTestCase):

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

    def test_RecordViewTest(self):
        self.assertEqual(Collection.__name__, "Collection", "Check Collection class name")
        return

    def test_recordview_init(self):
        t = RecordView(self.testcoll, "testview", self.testsite)
        u = recordview_coll_url(self.testsite, coll_id="testcoll", view_id="testview")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.View)
        self.assertEqual(t._entityfile,     layout.VIEW_META_FILE)
        self.assertEqual(t._entityref,      layout.META_VIEW_REF)
        self.assertEqual(t._entityid,       "testview")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordview_dir(view_id="testview"))
        self.assertEqual(t._values,         None)
        return

    def test_recordview1_data(self):
        t = RecordView(self.testcoll, "view1", self.testsite)
        self.assertEqual(t.get_id(), "view1")
        self.assertEqual(t.get_type_id(), "_view")
        self.assertIn("/c/testcoll/_annalist_collection/views/view1/", t.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_view/view1/", t.get_view_url())
        t.set_values(recordview_create_values(view_id="view1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordview_value_keys()))
        v = recordview_values(view_id="view1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordview2_data(self):
        t = RecordView(self.testcoll, "view2", self.testsite)
        self.assertEqual(t.get_id(), "view2")
        self.assertEqual(t.get_type_id(), "_view")
        self.assertIn("/c/testcoll/_annalist_collection/views/view2/", t.get_url())
        self.assertEqual(TestBaseUri + "/c/testcoll/d/_view/view2/", t.get_view_url())
        t.set_values(recordview_create_values(view_id="view2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordview_value_keys()))
        v = recordview_values(view_id="view2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordview_create_load(self):
        t  = RecordView.create(self.testcoll, "view1", recordview_create_values(view_id="view1"))
        td = RecordView.load(self.testcoll, "view1").get_values()
        v  = recordview_read_values(view_id="view1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

    def test_recordview_default_data(self):
        t = RecordView.load(self.testcoll, "Default_view", altparent=self.testsite)
        self.assertEqual(t.get_id(), "Default_view")
        self.assertIn("/c/testcoll/_annalist_collection/views/Default_view", t.get_url())
        self.assertEqual(t.get_type_id(), "_view")
        td = t.get_values()
        self.assertEqual(
            set(td.keys()), 
            set(recordview_load_keys(view_uri=True, target_record_type=False))
            )
        v = recordview_read_values(view_id="Default_view")
        v.update(
            { 'rdfs:label':   'Default record view'
            , 'rdfs:comment': 'Default record view, applied when no view is specified when creating a record.'
            , 'annal:uri':    'annal:display/Default_view'
            })
        v.pop('annal:record_type', None)
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordView edit view tests
#
#   -----------------------------------------------------------------------------

class RecordViewEditViewTest(AnnalistTestCase):
    """
    Tests for record view edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.no_options = [ FieldChoice('', label="(no options)") ]
        def special_field(fid):
            return ( 
                fid.startswith("Field_") or 
                fid.startswith("List_") or
                fid.startswith("Type_") or
                fid.startswith("View_") or
                fid.startswith("User_")
                )
        self.field_options    = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, self.testsite) 
                  if fid != "_initial_values"
            ])
        self.field_options_no_bibentry = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, self.testsite) 
                  if fid != "_initial_values" and not fid.startswith("Bib_")
            ])
        self.field_options_bib_no_special = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, self.testsite) 
                  if fid != "_initial_values" and not special_field(fid)
            ])
        self.field_options_no_special = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, self.testsite) 
                  if fid != "_initial_values" and 
                      not (fid.startswith("Bib_") or special_field(fid))
            ])
        # log.info(self.field_options_no_bibentry)
        # For checking Location: header values...
        self.continuation_path = entitydata_list_type_url(coll_id="testcoll", type_id="_view")
        self.continuation_url  = TestHostUri + self.continuation_path
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

    def _create_record_view(
            self, view_id, 
            target_record_type="annal:View",
            extra_field=None, extra_field_uri=None
            ):
        "Helper function creates record view entry with supplied view_id"
        t = RecordView.create(
            self.testcoll, view_id, 
            recordview_create_values(
                view_id=view_id, 
                target_record_type=target_record_type,
                extra_field=extra_field, extra_field_uri=extra_field_uri
                )
            )
        return t

    def _check_recordview_values(
            self, view_id, view_uri=None, 
            target_record_type="annal:View",
            update="RecordView", 
            num_fields=4, field3_placement="small:0,12",
            extra_field=None, extra_field_uri=None,
            update_dict=None,
            ):
        "Helper function checks content of record view entry with supplied view_id"
        self.assertTrue(RecordView.exists(self.testcoll, view_id))
        t = RecordView.load(self.testcoll, view_id)
        self.assertEqual(t.get_id(), view_id)
        self.assertEqual(t.get_view_url(), TestHostUri + recordview_url("testcoll", view_id))
        v = recordview_values(
            view_id=view_id, view_uri=view_uri, update=update, 
            target_record_type=target_record_type,
            num_fields=num_fields, field3_placement=field3_placement,
            extra_field=extra_field, extra_field_uri=extra_field_uri
            )
        if update_dict:
            v.update(update_dict)
            for k in update_dict:
                if update_dict[k] is None:
                    v.pop(k, None)
        # log.info("*** actual: %r"%(t.get_values(),))
        # log.info("*** expect: %r"%(v,))
        self.assertDictionaryMatch(t.get_values(), v)
        return t

    def _check_default_entity_context_fields(self, response, 
            action="",
            num_fields=4,
            view_id="(?view_id)", 
            view_label="(?view_label)",
            view_help="(?view_help)",
            view_record_type="(?view_record_type)",
            view_url="(?view_url)",
            view_uri="(?view_uri)",
            field_options=[]
            ):
        r = response
        # log.info("******\n"+repr(r.context['fields']))
        # Common structure
        self.assertEqual(r.context['entity_id'],        view_id)
        self.assertEqual(r.context['orig_id'],          view_id)
        self.assertEqual(r.context['type_id'],          '_view')
        self.assertEqual(r.context['orig_type'],        '_view')
        self.assertEqual(r.context['coll_id'],          'testcoll')
        self.assertEqual(r.context['action'],           action)
        self.assertEqual(r.context['view_id'],          'View_view')
        # Fields
        #
        # NOTE: context['fields'][i]['field_id'] comes from FieldDescription instance via
        #       bound_field, so type prefix is stripped.  This does not apply to the field
        #       ids actually coming from the view form.
        #
        self.assertEqual(len(r.context['fields']), 6)
        # 1st field - Id
        view_id_help = (
            "A short identifier that distinguishes this view from all other views in the same collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'],           'View_id')
        self.assertEqual(r.context['fields'][0]['field_name'],         'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'],        'Id')
        self.assertEqual(r.context['fields'][0]['field_help'],         view_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'],  "(view id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][0]['field_target_type'],  "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value'],        view_id)
        self.assertEqual(r.context['fields'][0]['options'],            self.no_options)
        # 2nd field - Label
        view_label_help = (
            "Short string used to describe view when displayed"
            )
        self.assertEqual(r.context['fields'][1]['field_id'],           'View_label')
        self.assertEqual(r.context['fields'][1]['field_name'],         'View_label')
        self.assertEqual(r.context['fields'][1]['field_label'],        'Label')
        self.assertEqual(r.context['fields'][1]['field_help'],         view_label_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'],  "(view label)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][1]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][1]['field_target_type'],  "annal:Text")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][1]['field_value'],         view_label)
        self.assertEqual(r.context['fields'][1]['options'],             self.no_options)
        # 3rd field - comment
        # log.info("******\n"+repr(r.context['fields'][2]))
        self.assertEqual(r.context['fields'][2]['field_id'],           'View_comment')
        self.assertEqual(r.context['fields'][2]['field_name'],         'View_comment')
        self.assertEqual(r.context['fields'][2]['field_label'],        'Help')
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][2]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][2]['field_target_type'],  "annal:Richtext")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value'],        view_help)
        self.assertEqual(r.context['fields'][2]['options'],            self.no_options)
        # 4th field - type of entity for view
        # log.info("******\n"+repr(r.context['fields'][3]))
        self.assertEqual(r.context['fields'][3]['field_id'],           'View_target_type')
        self.assertEqual(r.context['fields'][3]['field_name'],         'View_target_type')
        self.assertEqual(r.context['fields'][3]['field_label'],        'Record type')
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "annal:record_type")
        self.assertEqual(r.context['fields'][3]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][3]['field_target_type'],  "annal:Identifier")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value'],        view_record_type)
        self.assertEqual(r.context['fields'][3]['options'],            self.no_options)
        # 5th field - add field
        # log.info("******\n"+repr(r.context['fields'][4]))
        self.assertEqual(r.context['fields'][4]['field_id'],           'View_edit_view')
        self.assertEqual(r.context['fields'][4]['field_name'],         'View_edit_view')
        self.assertEqual(r.context['fields'][4]['field_label'],        'Editable view?')
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:open_view")
        self.assertEqual(r.context['fields'][4]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][4]['field_target_type'],  "annal:Boolean")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][4]['field_value'],        True)
        self.assertEqual(r.context['fields'][4]['options'],            self.no_options)
        # 6th field - field list
        expect_field_data = (
            [ { 'annal:field_placement': 'small:0,12;medium:0,6'
              , 'annal:field_id':        '_field/Entity_id'
              }
            , { 'annal:field_placement': 'small:0,12;medium:6,6'
              , 'annal:field_id':        '_field/Entity_type'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/Entity_label'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/Entity_comment'
              }
            ])
        self.assertEqual(r.context['fields'][5]['field_id'],           'View_fields')
        self.assertEqual(r.context['fields'][5]['field_name'],         'View_fields')
        self.assertEqual(r.context['fields'][5]['field_label'],        'Fields')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:view_fields")
        self.assertEqual(r.context['fields'][5]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][5]['field_target_type'],  "annal:Field_group")
        self.assertEqual(r.context['fields'][5]['field_value'],        expect_field_data)
        self.assertEqual(len(r.context['fields'][5]['field_value']),   num_fields)
        self.assertEqual(r.context['fields'][5]['options'],            self.no_options)
        return

    # The View_view test case checks descriptions of repeat-field-groups that are not 
    # covererd by the Default_view case.
    def _check_record_view_context_fields(self, response, action="", num_fields=6):
        r = response
        # log.info("r.context['fields']: %r"%(r.context['fields'],))
        # Common structure
        view_url = collection_entity_view_url("testcoll", "_view", "View_view")
        self.assertEqual(r.context['entity_id'],        'View_view')
        self.assertEqual(r.context['orig_id'],          'View_view')
        self.assertEqual(r.context['type_id'],          '_view')
        self.assertEqual(r.context['orig_type'],        '_view')
        self.assertEqual(r.context['coll_id'],          'testcoll')
        self.assertEqual(r.context['entity_uri'],       "annal:display/View_view")
        self.assertEqual(r.context['action'],           action)
        self.assertEqual(r.context['view_id'],          'View_view')
        # Fields
        # NOTE: context['fields'][i]['field_id'] comes from FieldDescription instance via
        #       bound_field, so type prefix is stripped.  This does not apply to the field
        #       ids actually coming from the view form.
        self.assertEqual(len(r.context['fields']), 6)        
        # 1st field - Id
        self.assertEqual(r.context['fields'][0]['field_id'],    'View_id')
        self.assertEqual(r.context['fields'][0]['field_name'],  'entity_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        # 2nd field - Label
        self.assertEqual(r.context['fields'][1]['field_id'],    'View_label')
        self.assertEqual(r.context['fields'][1]['field_name'],  'View_label')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Label')
        # 3rd field - comment
        self.assertEqual(r.context['fields'][2]['field_id'],    'View_comment')
        self.assertEqual(r.context['fields'][2]['field_name'],  'View_comment')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Help')
        # 4th field - rview recoird type
        # log.info("******\n"+repr(r.context['fields'][3]))
        self.assertEqual(r.context['fields'][3]['field_id'],    'View_target_type')
        self.assertEqual(r.context['fields'][3]['field_name'],  'View_target_type')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Record type')
        # 5th field - add field
        # log.info("******\n"+repr(r.context['fields'][3]))
        self.assertEqual(r.context['fields'][4]['field_id'],    'View_edit_view')
        self.assertEqual(r.context['fields'][4]['field_name'],  'View_edit_view')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Editable view?')
        # 6th field - field list
        expect_field_data = (
            [
              { 'annal:field_placement': 'small:0,12;medium:0,6'
              , 'annal:field_id':        '_field/View_id'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/View_label'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/View_comment'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/View_target_type'
              }
            , { 'annal:field_placement': 'small:0,12;medium:0,6'
              , 'annal:field_id':        '_field/View_edit_view'
              }
            , { 'annal:field_placement': 'small:0,12'
              , 'annal:field_id':        '_field/View_fields'
              }
            ])
        if num_fields == 7:
            # New blank field, if selected
            expect_field_data.append(
                { 'annal:property_uri': None
                , 'annal:field_placement': None
                , 'annal:field_id': None
                })
            # log.info(repr(r.context['fields'][5]['field_value']))
        self.assertEqual(r.context['fields'][5]['field_id'],           'View_fields')
        self.assertEqual(r.context['fields'][5]['field_name'],         'View_fields')
        self.assertEqual(r.context['fields'][5]['field_label'],        'Fields')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:view_fields")
        self.assertEqual(r.context['fields'][5]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][5]['field_target_type'],  "annal:Field_group")
        self.assertEqual(len(r.context['fields'][5]['field_value']),   num_fields)
        self.assertEqual(r.context['fields'][5]['field_value'],        expect_field_data)
        self.assertEqual(r.context['fields'][5]['options'],            self.no_options)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        field_vals = default_fields(coll_id="testcoll", type_id="_view", entity_id="00000001")
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(view id)" value="%(entity_id)s"/>
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
                  <input type="text" size="64" name="View_label"
                         placeholder="(view label)" 
                         value="%(default_label_esc)s"/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Help</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="View_comment" 
                            class="small-rows-4 medium-rows-8"
                            placeholder="(description of record view)">
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Editable view?</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="checkbox" name="View_edit_view" value="Yes" checked="checked" />
                   <span class="value-placeholder">(edit view from edit entity form)</span>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow5 = ("""
            <div class="small-12 medium-4 columns">
              <div class="row show-for-small-only">
                <div class="view-label small-12 columns">
                  <span>Field id</span>
                </div>
              </div>
              <div class="row view-value-col">
                <div class="view-value small-12 columns">
                """+
                  render_select_options(
                    "View_fields__0__Field_id", "Field id",
                    no_selection("(field sel)") + get_site_default_entity_fields_sorted(),
                    "_field/Entity_id")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=4)
        formrow6 = """
            <div class="small-1 columns checkbox-in-edit-padding">
              <input type="checkbox" class="select-box right" 
                     name="View_fields__select_fields"
                     value="0" />
            </div>        
            """
        # log.info("*** View content: "+r.content)
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        self.assertContains(r, formrow6, html=True)
        return

    def test_get_form_rendering_view_bibentry(self):
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="BibEntry_view", 
            view_id="View_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>Collection testcoll</title>")
        field_vals = default_fields(coll_id="testcoll", type_id="_view", entity_id="BibEntry_view")
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Id</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(view id)" value="%(entity_id)s"/>
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
                  <input type="text" size="64" name="View_label"
                         placeholder="(view label)" 
                         value="Bibliographic metadata"/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Help</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="View_comment" 
                            class="small-rows-4 medium-rows-8"
                            placeholder="(description of record view)">
                      Bibliography entries each contain some subset of standard data entries.
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Editable view?</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="checkbox" name="View_edit_view" value="Yes" checked="checked" />
                   <span class="value-placeholder">(edit view from edit entity form)</span>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow5 = ("""
            <div class="small-12 medium-4 columns">
              <div class="row show-for-small-only">
                <div class="view-label small-12 columns">
                  <span>Field id</span>
                </div>
              </div>
              <div class="row view-value-col">
                <div class="view-value small-12 columns">
                """+
                  render_select_options(
                    "View_fields__0__Field_id", "Field id",
                    no_selection("(field sel)") + get_site_bibentry_fields_sorted(),
                    "_field/Entity_id")+
                """
                </div>
              </div>
            </div>
            """)%field_vals(width=4)
        formrow6 = """
            <div class="small-1 columns checkbox-in-edit-padding">
              <input type="checkbox" class="select-box right" 
                     name="View_fields__select_fields"
                     value="0" />
            </div>        
            """
        # log.info("*** BibEntry_view content: "+r.content)
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        self.assertContains(r, formrow6, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        view_url = collection_entity_view_url(coll_id="testcoll", type_id="_view", entity_id="00000001")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['edit_view_button'],   False)
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields initially created
        self._check_default_entity_context_fields(r, 
            action="new",
            num_fields=4,
            view_id="00000001",
            view_label="", # default_label("testcoll", "_view", "00000001"),
            view_help="", # default_comment("testcoll", "_view", "00000001"),
            view_record_type="",
            view_url=recordview_url("testcoll", "00000001"),
            field_options = self.field_options_no_special
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_url(
            "copy", "testcoll", "_view", entity_id="Default_view", view_id="View_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        view_url = collection_entity_view_url(coll_id="testcoll", type_id="_view", entity_id="Default_view")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "Default_view")
        self.assertEqual(r.context['orig_id'],          "Default_view")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['edit_view_button'],   False)
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_default_entity_context_fields(r, 
            action="copy",
            view_id="Default_view",
            view_label="Default record view",
            view_help="Default record view, applied when no view is specified when creating a record.",
            view_url=view_url,
            view_uri=None,
            view_record_type="",
            field_options=self.field_options_no_special
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_url("copy", "testcoll", "_view", entity_id="noview", view_id="View_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", "_view", "noview")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", "_view", entity_id="Default_view", view_id="View_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        view_url = collection_entity_view_url(
            coll_id="testcoll", type_id="_view", entity_id="Default_view"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "Default_view")
        self.assertEqual(r.context['orig_id'],          "Default_view")
        self.assertEqual(r.context['entity_uri'],       "annal:display/Default_view")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['edit_view_button'],   False)
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_default_entity_context_fields(r, 
            action="edit",
            view_id="Default_view",
            view_label="Default record view",
            view_help="Default record view, applied when no view is specified when creating a record.",
            view_url=view_url,
            view_uri="annal:display/Default_view",
            view_record_type="",
            field_options=self.field_options_no_special
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url("edit", "testcoll", "_view", entity_id="noview", view_id="View_view")
        r = self.client.get(u)
        # log.info(r.content)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        err_label = error_label("testcoll", "_view", "noview")
        self.assertContains(r, "<p>Entity %s does not exist</p>"%(err_label), status_code=404)
        return

    # Test rendering of view with repeated field structure - in this case, View_view
    def test_get_recordview_edit(self):
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="View_view", 
            view_id="View_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        view_url = collection_entity_view_url(
            coll_id="testcoll", type_id="_view", entity_id="View_view"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "View_view")
        self.assertEqual(r.context['orig_id'],          "View_view")
        self.assertEqual(r.context['entity_uri'],       "annal:display/View_view")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_record_view_context_fields(r, action="edit")
        return

    def test_get_recordview_edit_add_field(self):
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="View_view", 
            view_id="View_view"
            )
        u = uri_with_params(u, {'add_field': 'View_fields'})
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        view_url = collection_entity_view_url(
            coll_id="testcoll", type_id="_view", entity_id="View_view"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "View_view")
        self.assertEqual(r.context['orig_id'],          "View_view")
        self.assertEqual(r.context['entity_uri'],       "annal:display/View_view")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_record_view_context_fields(r, action="edit", num_fields=7)
        return

    # Test view rendering of BibEntry_view: field selectors should include Bib_* fields
    def test_get_recordview_edit_bibentry(self):
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="BibEntry_view", 
            view_id="View_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        view_url = collection_entity_view_url("testcoll", "_view", "BibEntry_view")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_view")
        self.assertEqual(r.context['entity_id'],        "BibEntry_view")
        self.assertEqual(r.context['orig_id'],          "BibEntry_view")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['edit_view_button'],   False)
        self.assertEqual(r.context['continuation_url'], "")
        # Skip checking fields 0-4 - that's already been covered
        # log.info("*** fields[5]['options']:     "+repr(r.context['fields'][5]['options']))
        # log.info("*** fields[5]['field_value']: "+repr(r.context['fields'][5]['field_value']))
        # @@TODO: revise for more useful BibEntry structure
        expect_field_data = (
            [ { 'annal:field_placement':    'small:0,12;medium:0,6'
              , 'annal:field_id':           '_field/Entity_id'
              }
            , { 'annal:field_placement':    'small:0,12;medium:6,6'
              , 'annal:field_id':           '_field/Bib_type'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_title'
              }
            , { 'annal:field_placement':    'small:0,12;medium:0,6'
              , 'annal:field_id':           '_field/Bib_month'
              }
            , { 'annal:field_placement':    'small:0,12;medium:6,6'
              , 'annal:field_id':           '_field/Bib_year'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_authors'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_editors'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_journal'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_bookentry'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_publication_details'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_identifiers'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_license'
              }
            , { 'annal:field_placement':    'small:0,12'
              , 'annal:field_id':           '_field/Bib_note'
              }
            ])
        # NOTE: context['fields'][i]['field_id'] comes from FieldDescription instance via
        #       bound_field, so type prefix is stripped.  This does not apply to the field
        #       ids actually coming from the view form.
        self.assertEqual(r.context['fields'][5]['field_id'],           'View_fields')
        self.assertEqual(r.context['fields'][5]['field_name'],         'View_fields')
        self.assertEqual(r.context['fields'][5]['field_label'],        'Fields')
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:view_fields")
        self.assertEqual(r.context['fields'][5]['field_value_mode'],   "Value_direct")
        self.assertEqual(r.context['fields'][5]['field_target_type'],  "annal:Field_group")
        self.assertEqual(r.context['fields'][5]['field_value'],        expect_field_data)
        self.assertEqual(r.context['fields'][5]['options'],            self.no_options)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new view --------

    def test_post_new_view(self):
        self.assertFalse(RecordView.exists(self.testcoll, "newview"))
        f = recordview_entity_view_form_data(view_id="newview", action="new", update="NewView")
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_recordview_values("newview", update="NewView", num_fields=0)
        return

    def test_post_new_view_cancel(self):
        self.assertFalse(RecordView.exists(self.testcoll, "newview"))
        f = recordview_entity_view_form_data(
            view_id="newview",
            action="new", cancel="Cancel", update="Updated RecordView"
            )
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type still does not exist
        self.assertFalse(RecordView.exists(self.testcoll, "newview"))
        return

    def test_post_new_view_missing_id(self):
        f = recordview_entity_view_form_data(
            view_id=None,
            action="new", update="RecordView"
            )
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        # Test context
        expect_context = recordview_entity_view_context_data(
            view_id=None,
            action="new", update="RecordView",
            )
        # print repr(r.context[-1]['fields'][-1]['field_value'])
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_new_view_invalid_id(self):
        f = recordview_entity_view_form_data(
            view_id="!badview", orig_id="orig_view_id", 
            action="new", update="RecordView"
            )
        u = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        # log.info("u %s, f %r"%(u,f))
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        # Test context
        expect_context = recordview_entity_view_context_data(
            view_id="!badview", orig_id="orig_view_id", 
            action="new", update="RecordView"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- copy view --------

    def test_post_copy_view(self):
        self.assertFalse(RecordView.exists(self.testcoll, "copyview"))
        f = recordview_entity_view_form_data(
            view_id="copyview", orig_id="Default_view", action="copy", update="RecordView"
            )
        u = entitydata_edit_url("copy", "testcoll", "_view", entity_id="Default_view", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record type exists
        self._check_recordview_values("copyview", update="RecordView")
        return

    def test_post_copy_view_cancel(self):
        self.assertFalse(RecordView.exists(self.testcoll, "copyview"))
        f = recordview_entity_view_form_data(
                view_id="copyview", orig_id="Default_view", 
                action="copy", cancel="Cancel", update="RecordView"
                )
        u = entitydata_edit_url("copy", "testcoll", "_view", entity_id="Default_view", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record view still does not exist
        self.assertFalse(RecordView.exists(self.testcoll, "copyview"))
        return

    def test_post_copy_view_missing_id(self):
        f = recordview_entity_view_form_data(
            view_id=None, orig_id="Default_view", 
            action="copy", update="Updated RecordView"
            )
        u = entitydata_edit_url("copy", "testcoll", "_view", entity_id="Default_view", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        expect_context = recordview_entity_view_context_data(
            view_id=None, orig_id="Default_view", 
            action="copy", update="Updated RecordView"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_copy_view_invalid_id(self):
        f = recordview_entity_view_form_data(
            view_id="!badview", orig_id="Default_view", action="copy", update="Updated RecordView"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "_view", entity_id="Default_view", view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        expect_context = recordview_entity_view_context_data(
            view_id="!badview",
             orig_id="Default_view", 
            action="copy", 
            update="Updated RecordView"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    #   -------- edit view --------

    def test_post_edit_view(self):
        self._create_record_view("editview")
        self._check_recordview_values("editview")
        f = recordview_entity_view_form_data(
            view_id="editview", orig_id="editview", 
            action="edit", 
            target_record_type="annal:View",
            update="Updated RecordView"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="editview", view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record view exists
        self._check_recordview_values("editview", update="Updated RecordView")
        return

    def test_post_edit_view_new_id(self):
        self._create_record_view("editview1")
        self._check_recordview_values("editview1")
        f = recordview_entity_view_form_data(
            view_id="editview2", orig_id="editview1", 
            action="edit", 
            target_record_type="annal:View",
            update="Updated RecordView"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="editview1", view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record view exists and old does not
        self.assertFalse(RecordView.exists(self.testcoll, "editview1"))
        self._check_recordview_values("editview2", update="Updated RecordView")
        return

    def test_post_edit_view_cancel(self):
        self._create_record_view("editview")
        self._check_recordview_values("editview")
        f = recordview_entity_view_form_data(
            view_id="editview", orig_id="editview", 
            action="edit", cancel="Cancel", 
            target_record_type="annal:View",
            update="Updated RecordView"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="editview", view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that target record view still does not exist and unchanged
        self._check_recordview_values("editview")
        return

    def test_post_edit_view_missing_id(self):
        self._create_record_view("editview")
        self._check_recordview_values("editview")
        # Form post with ID missing
        f = recordview_entity_view_form_data(
            view_id=None, orig_id="editview", 
            action="edit", 
            target_record_type="annal:View",
            update="Updated RecordView"
            )
        u = entitydata_edit_url("edit", "testcoll", "_view", entity_id="editview", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        # Test context for re-rendered form
        expect_context = recordview_entity_view_context_data(
            orig_id="editview",
            action="edit", 
            target_record_type="annal:View",
            update="Updated RecordView"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_recordview_values("editview")
        return

    def test_post_edit_view_invalid_id(self):
        self._create_record_view("editview")
        self._check_recordview_values("editview")
        # Form post with invalid ID
        f = recordview_entity_view_form_data(
            view_id="!badview", orig_id="editview", action="edit", update="Updated RecordView"
            )
        u = entitydata_edit_url("edit", "testcoll", "_view", entity_id="editview", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with record view identifier</h3>")
        # Test context
        expect_context = recordview_entity_view_context_data(
            view_id="!badview", 
            orig_id="editview", 
            action="edit",
            update="Updated RecordView"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check original data is unchanged
        self._check_recordview_values("editview")
        return

    def test_post_edit_view_field_placement_missing(self):
        self._create_record_view("editview")
        self._check_recordview_values("editview")
        f = recordview_entity_view_form_data(
            view_id="editview", orig_id="editview", 
            action="edit", update="Updated RecordView",
            field3_placement=""
            )
        u = entitydata_edit_url("edit", "testcoll", "_view", entity_id="editview", view_id="View_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], self.continuation_url)
        # Check that new record view exists
        self._check_recordview_values("editview", update="Updated RecordView", field3_placement="")
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests for view descriptions with repeating fields
    #   -----------------------------------------------------------------------------

    def test_post_add_field(self):
        self._create_record_view("addfieldview")
        self._check_recordview_values("addfieldview")
        f = recordview_entity_view_form_data(
            view_id="addfieldview", orig_id="addfieldview", 
            action="edit",
            target_record_type="annal:View",
            add_field=True
            )
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", type_id="_view", entity_id="addfieldview", 
            view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + u + "?continuation_url=" + self.continuation_path
        self.assertEqual(v, r['location'])
        # Retrieve from redirect location, and test result
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        expect_context = recordview_entity_view_context_data(
            view_id="addfieldview", orig_id="addfieldview", 
            action="edit",
            target_record_type="annal:View",
            add_field=True
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_remove_field(self):
        self._create_record_view("removefieldview")
        self._check_recordview_values("removefieldview")
        f = recordview_entity_view_form_data(
            view_id="removefieldview", orig_id="removefieldview", 
            action="edit",
            remove_fields=['3']
            )
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", type_id="_view", entity_id="removefieldview", 
            view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + u + "?continuation_url=" + self.continuation_path
        self.assertEqual(v, r['location'])
        # Retrieve from redirect location, and test result
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        expect_context = recordview_entity_view_context_data(
            view_id="removefieldview", orig_id="removefieldview", 
            action="edit",
            remove_field=True
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_remove_no_field_selected(self):
        self._create_record_view("removefieldview")
        self._check_recordview_values("removefieldview")
        f = recordview_entity_view_form_data(
            view_id="removefieldview", orig_id="removefieldview", 
            action="edit",
            remove_fields="no-selection"
            )
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", type_id="_view", entity_id="removefieldview", 
            view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with remove field(s) request</h3>")
        self.assertContains(r, "<p>No field(s) selected</p>")
        expect_context = recordview_entity_view_context_data(
            view_id="removefieldview", orig_id="removefieldview", 
            action="edit",
            remove_field=False
            )
        # log.info("r.context: %r"%(r.context))
        # log.info("expect_context: %r"%(expect_context))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_move_up_fields(self):
        self._create_record_view("movefieldview")
        self._check_recordview_values("movefieldview")
        f = recordview_entity_view_form_data(
            view_id="movefieldview", orig_id="movefieldview", 
            action="edit",
            target_record_type="annal:View",
            move_up_fields=["2","3"]
            )
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", type_id="_view", entity_id="movefieldview", 
            view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + u + "?continuation_url=" + self.continuation_path
        self.assertEqual(v, r['location'])
        # Retrieve from redirect location, and test result
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        expect_context = recordview_entity_view_context_data(
            view_id="movefieldview", orig_id="movefieldview", 
            action="edit",
            target_record_type="annal:View",
            move_up=[2,3]
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    def test_post_move_down_fields(self):
        self._create_record_view("movefieldview")
        self._check_recordview_values("movefieldview")
        f = recordview_entity_view_form_data(
            view_id="movefieldview", orig_id="movefieldview", 
            action="edit",
            target_record_type="annal:View",
            move_down_fields=["1"]
            )
        u = entitydata_edit_url(
            action="edit", coll_id="testcoll", type_id="_view", entity_id="movefieldview", 
            view_id="View_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + u + "?continuation_url=" + self.continuation_path
        self.assertEqual(v, r['location'])
        # Retrieve from redirect location, and test result
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        expect_context = recordview_entity_view_context_data(
            view_id="movefieldview", orig_id="movefieldview", 
            action="edit",
            target_record_type="annal:View",
            move_down=[1]
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return


#   -----------------------------------------------------------------------------
#
#   ConfirmRecordViewDeleteTests tests for completion of record deletion
#
#   -----------------------------------------------------------------------------

class ConfirmRecordViewDeleteTests(AnnalistTestCase):
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
        self.assertEqual(RecordViewDeleteConfirmedView.__name__, "RecordViewDeleteConfirmedView", "Check RecordViewDeleteConfirmedView class name")
        return

    # NOTE:  test_collection checks the appropriate response from clicking the delete button, 
    # so here only need to test completion code.
    def test_post_confirmed_remove_view(self):
        t = RecordView.create(self.testcoll, "deleteview", recordview_create_values("deleteview"))
        self.assertTrue(RecordView.exists(self.testcoll, "deleteview"))
        # Submit positive confirmation
        u = TestHostUri + recordview_edit_url("delete", "testcoll")
        f = recordview_delete_confirm_form_data("deleteview")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,     302)
        self.assertEqual(r.reason_phrase,   "FOUND")
        self.assertEqual(r.content,         "")
        self.assertMatch(r['location'],    
            "^"+TestHostUri+
            collection_edit_url("testcoll")+
            r"\?info_head=.*&info_message=.*deleteview.*testcoll.*$"
            )
        # Confirm deletion
        self.assertFalse(RecordView.exists(self.testcoll, "deleteview"))
        return

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
