"""
Tests for RecordView module and view with inherited bibliographic definitioins
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, 2015 G. Klyne"
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

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site, init_annalist_bib_site, 
    init_annalist_test_coll, init_annalist_bib_coll, 
    resetSitedata
    )
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    render_select_options,
    create_test_user
    )
from entity_testviewdata    import (
    recordview_dir,
    recordview_coll_url, recordview_site_url, recordview_url, recordview_edit_url,
    recordview_value_keys, recordview_load_keys, 
    recordview_create_values, recordview_values, recordview_read_values,
    recordview_entity_view_context_data, recordview_entity_view_form_data, 
    # recordview_view_context_data, recordview_view_form_data, 
    recordview_delete_confirm_form_data
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    get_site_default_entity_fields_sorted,
    get_site_bibentry_fields_sorted
    ) 

#   -----------------------------------------------------------------------------
#
#   RecordView edit view tests
#
#   -----------------------------------------------------------------------------

class BibRecordViewEditViewTest(AnnalistTestCase):
    """
    Tests for record view edit views
    """

    def setUp(self):
        self.testsite  = init_annalist_bib_site()
        self.testcoll  = init_annalist_bib_coll()
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
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, altscope="all") 
                  if fid != "_initial_values"
            ])
        self.field_options_no_bibentry = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, altscope="all") 
                  if fid != "_initial_values" and not fid.startswith("Bib_")
            ])
        self.field_options_bib_no_special = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, altscope="all") 
                  if fid != "_initial_values" and not special_field(fid)
            ])
        self.field_options_no_special = sorted(
            [ fid for fid in self.testcoll.child_entity_ids(RecordField, altscope="all") 
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
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

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
                    "_field/Entity_id",
                    placeholder="(field sel)"
                    )+
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

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
