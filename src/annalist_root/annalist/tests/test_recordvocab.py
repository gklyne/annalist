"""
Tests for RecordVocab module and view

Note: this module tests for rendering specifically for RecordVocab values, using
type description sitedata files, and as such duplicates some tests covered by
module test_entitygenericedit.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import unittest
import markdown

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.contrib.auth.models         import User
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                 import Client

from annalist.util                      import valid_id, extract_entity_id
from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist                           import message

from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.entitydata         import EntityData
from annalist.models.recordvocab        import RecordVocab

from annalist.views.form_utils.fieldchoice  import FieldChoice
from annalist.views.displayinfo             import apply_substitutions

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site,
    init_annalist_test_coll,
    resetSitedata
    )
from .entity_testfielddesc import get_field_description, get_bound_field
from .entity_testutils import (
    make_message, make_quoted_message,
    site_dir, collection_dir,
    site_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_test_user, create_user_permissions,
    context_view_field,
    context_bind_fields,
    check_context_field, check_context_field_value,
    )
from .entity_testvocabdata import (
    recordvocab_dir,
    recordvocab_coll_url, recordvocab_url, recordvocab_edit_url,
    recordvocab_value_keys, recordvocab_load_keys, 
    recordvocab_create_values, recordvocab_values, recordvocab_read_values,
    vocab_view_context_data, 
    vocab_view_form_data, # recordvocab_delete_confirm_form_data
    )
from .entity_testentitydata import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from .entity_testsitedata import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from .entity_testviewdata import recordview_url
from .entity_testlistdata import recordlist_url

#   -----------------------------------------------------------------------------
#
#   RecordVocab tests
#
#   -----------------------------------------------------------------------------

class RecordVocabTest(AnnalistTestCase):
    """
    Tests for RecordVocab object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.sitedata = SiteData(self.testsite)
        self.testcoll = Collection(self.testsite, "testcoll")
        self.layout = (
            { 'enum_field_placement_id':    layout.ENUM_FIELD_PLACEMENT_ID
            , 'enum_list_type_id':          layout.ENUM_LIST_TYPE_ID
            , 'enum_render_type_id':        layout.ENUM_RENDER_TYPE_ID
            , 'enum_value_type_id':         layout.ENUM_VALUE_TYPE_ID
            , 'enum_value_mode_id':         layout.ENUM_VALUE_MODE_ID
            , 'field_typeid':               layout.FIELD_TYPEID
            , 'group_typeid':               layout.GROUP_TYPEID
            , 'list_typeid':                layout.LIST_TYPEID
            , 'type_typeid':                layout.TYPE_TYPEID
            , 'user_typeid':                layout.USER_TYPEID
            , 'view_typeid':                layout.VIEW_TYPEID
            , 'vocab_typeid':               layout.VOCAB_TYPEID
            , 'field_dir':                  layout.FIELD_DIR
            , 'group_dir':                  layout.GROUP_DIR
            , 'list_dir':                   layout.LIST_DIR
            , 'type_dir':                   layout.TYPE_DIR
            , 'user_dir':                   layout.USER_DIR
            , 'view_dir':                   layout.VIEW_DIR
            , 'vocab_dir':                  layout.VOCAB_DIR
            })
        return

    def tearDown(self):
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata(scope="collections")
        return

    # @classmethod
    # def setUpClass(cls):
    #     super(zzzzzz, cls).setUpClass()
    #     return

    # @classmethod
    # def tearDownClass(cls):
    #     super(zzzzzz, cls).tearDownClass()
    #     return

    def test_RecordVocabTest(self):
        self.assertEqual(RecordVocab.__name__, "RecordVocab", "Check RecordVocab class name")
        return

    def test_recordvocab_init(self):
        t = RecordVocab(self.testcoll, "testvocab")
        u = recordvocab_coll_url(self.testsite, coll_id="testcoll", vocab_id="testvocab")
        self.assertEqual(t._entitytype,     ANNAL.CURIE.Vocabulary)
        self.assertEqual(t._entityfile,     layout.VOCAB_META_FILE)
        self.assertEqual(t._entityref,      layout.COLL_BASE_VOCAB_REF%{'id': "testvocab"})
        self.assertEqual(t._entityid,       "testvocab")
        self.assertEqual(t._entityurl,      u)
        self.assertEqual(t._entitydir,      recordvocab_dir(vocab_id="testvocab"))
        self.assertEqual(t._values,         None)
        return

    def test_recordvocab1_data(self):
        t = RecordVocab(self.testcoll, "vocab1")
        self.assertEqual(t.get_id(), "vocab1")
        self.assertEqual(t.get_type_id(), layout.VOCAB_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(vocab_dir)s/vocab1/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(vocab_typeid)s/vocab1/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordvocab_create_values(vocab_id="vocab1"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordvocab_value_keys()))
        v = recordvocab_values(vocab_id="vocab1")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordvocab2_data(self):
        t = RecordVocab(self.testcoll, "vocab2")
        self.assertEqual(t.get_id(), "vocab2")
        self.assertEqual(t.get_type_id(), layout.VOCAB_TYPEID)
        self.assertIn(
            "/c/testcoll/d/%(vocab_dir)s/vocab2/"%self.layout, 
            t.get_url()
            )
        self.assertEqual(
            TestBaseUri + "/c/testcoll/d/%(vocab_typeid)s/vocab2/"%self.layout, 
            t.get_view_url()
            )
        t.set_values(recordvocab_create_values(vocab_id="vocab2"))
        td = t.get_values()
        self.assertEqual(set(td.keys()), set(recordvocab_value_keys()))
        v = recordvocab_values(vocab_id="vocab2")
        self.assertDictionaryMatch(td, v)
        return

    def test_recordvocab_create_load(self):
        t  = RecordVocab.create(self.testcoll, "vocab1", recordvocab_create_values(vocab_id="vocab1"))
        td = RecordVocab.load(self.testcoll, "vocab1").get_values()
        v  = recordvocab_read_values(vocab_id="vocab1")
        self.assertKeysMatch(td, v)
        self.assertDictionaryMatch(td, v)
        return

#   -----------------------------------------------------------------------------
#
#   RecordVocabEditView tests
#
#   -----------------------------------------------------------------------------

class RecordVocabEditViewTest(AnnalistTestCase):
    """
    Tests for vocabulary record edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite   = Site(TestBaseUri, TestBaseDir)
        self.testcoll   = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.annalcoll  = Collection.load(self.testsite, layout.SITEDATA_ID)
        self.no_options = [ FieldChoice('', label="(no options)") ]
        # For checking Location: header values...
        self.continuation_url = (
            entitydata_list_type_url(coll_id="testcoll", type_id=layout.VOCAB_TYPEID)
            )
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        create_user_permissions(self.annalcoll, "testuser", user_permissions=["VIEW"])
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata(scope="collections")
        return

    @classmethod
    def setUpClass(cls):
        super(RecordVocabEditViewTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(RecordVocabEditViewTest, cls).tearDownClass()
        # @@checkme@@ resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_record_vocab(self, vocab_id):
        "Helper function creates namespace vocabulary entry with supplied vocab_id"
        ve = RecordVocab.create(
            self.testcoll, vocab_id, recordvocab_create_values(vocab_id=vocab_id)
            )
        return ve

    def _check_record_vocab_values(self, vocab_id, 
            update="RecordVocab", 
            vocab_uri=None,
            extra_values=None
            ):
        "Helper function checks content of record type entry with supplied vocab_id"
        self.assertTrue(RecordVocab.exists(self.testcoll, vocab_id))
        ve = RecordVocab.load(self.testcoll, vocab_id)
        self.assertEqual(ve.get_id(), vocab_id)
        self.assertEqual(ve.get_view_url(), TestHostUri + recordvocab_url("testcoll", vocab_id))
        vv = recordvocab_values(
            vocab_id=vocab_id,
            update=update,
            vocab_uri=vocab_uri
            )
        if extra_values:
            vv.update(extra_values)
        # print "ve: "+repr(ve.get_values())
        # print "vv: "+repr(v)
        self.assertDictionaryMatch(ve.get_values(), vv)
        return ve

    def _check_context_fields(self, response, 
            action="",
            vocab_id="", orig_vocab_id=None,
            vocab_label=None,
            vocab_descr=None,
            vocab_uri=None,
            vocab_seealso=[],
            update="RecordVocab",
            continuation_url=None
            ):
        expect_context = vocab_view_context_data(
            coll_id="testcoll", vocab_id=vocab_id, orig_id=orig_vocab_id, action=action, 
            vocab_label=vocab_label,
            vocab_descr=vocab_descr,
            vocab_uri=vocab_uri,
            vocab_seealso=[{"@id": v} for v in vocab_seealso],
            update=update,
            continuation_url=continuation_url
            )
        actual_context = context_bind_fields(response.context)
        self.assertEqual(len(response.context['fields']), 5)
        self.assertDictionaryMatch(actual_context, expect_context)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_form_rendering(self):
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.VOCAB_TYPEID, entity_id="00000001",
            default_label="",
            default_comment=context_view_field(r.context, 2, 0)['field_value'],
            default_label_esc="",
            default_comment_esc=context_view_field(r.context, 2, 0)['field_value'],
            tooltip1=context_view_field(r.context, 0, 0)['field_tooltip'],
            tooltip2=context_view_field(r.context, 1, 0)['field_tooltip'],
            tooltip3=context_view_field(r.context, 2, 0)['field_tooltip'],
            tooltip4=context_view_field(r.context, 3, 0)['field_tooltip'],
            button_save_tip="Save values and return to previous view.",
            button_view_tip="Save values and switch to entity view.",
            button_cancel_tip="Discard unsaved changes and return to previous view.",
            )
        formrow1 = """
            <div class="small-12 medium-6 columns" title="%(tooltip1)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Prefix</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="entity_id" 
                         placeholder="(vocabulary id)" value="00000001"/>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns" title="%(tooltip2)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Entity_label" 
                         placeholder="(label)" 
                         value="%(default_label_esc)s" />
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow3 = """
            <div class="small-12 columns" title="%(tooltip3)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Comment</span>
                </div>
                <div class="%(input_classes)s">
                  <textarea cols="64" rows="6" name="Entity_comment" 
                            class="small-rows-4 medium-rows-8"
                            placeholder="(description)"
                            >
                      %(default_comment_esc)s
                  </textarea>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns" title="%(tooltip4)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Vocabulary URI</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Vocab_uri" 
                         placeholder="(Vocabulary namespace URI)"
                         value=""/>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        return

    def test_get_view_rendering(self):
        # Test view rendering
        # This checks for namespace prefix expansion in URL links.
        # Add test namespace
        vocab_id     = "test_vocab"
        vocab_curie  = "annal:test_vocab"
        annal_uri    = ANNAL.mk_uri("")
        vocab_entity = RecordVocab.create(
            self.testcoll, vocab_id, 
            recordvocab_create_values(vocab_id=vocab_id, vocab_uri=vocab_curie)
            )
        # View new namespace entity
        u = entitydata_edit_url(
            "view", "testcoll", layout.VOCAB_TYPEID, entity_id=vocab_id, view_id="Vocab_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        default_comment = context_view_field(r.context, 2, 0)['field_value']
        field_vals = default_fields(
            coll_id="testcoll", type_id=layout.VOCAB_TYPEID, entity_id=vocab_id,
            entity_view_url=u,
            rendered_label=context_view_field(r.context, 1, 0)['field_value'],
            rendered_comment=markdown.markdown(apply_substitutions(r.context, default_comment)),
            vocab_id=vocab_id,
            vocab_curie=vocab_curie,
            vocab_uri=annal_uri+vocab_id,
            urie=annal_uri+vocab_id,
            )
        formrow1 = """
            <div class="small-12 medium-6 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Prefix</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(default_entity_url)s?continuation_url=%(entity_view_url)s">%(vocab_id)s</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)

            #           <div class="small-12 medium-6 columns">
            #   <div class="row view-value-row">
            #     <div class="view-label small-12 medium-4 columns">
            #       <span>Prefix</span>
            #     </div>
            #     <div class="view-value small-12 medium-8 columns">
            # <a href="/testsite/c/testcoll/d/_vocab/test_vocab/
            # ?continuation_url=/testsite/c/testcoll/v/Vocab_view/_vocab/test_vocab/!view">test_vocab</a>
            #     </div>
            #   </div>
 


        formrow2 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Label</span>
                </div>
                <div class="%(input_classes)s">
                  <span>%(rendered_label)s</span>
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
                    %(rendered_comment)s
                  </span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Vocabulary URI</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(vocab_uri)s" target="_blank">%(vocab_curie)s</a>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)   #@@
        self.assertContains(r, formrow1, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.VOCAB_TYPEID, entity_id="00000001"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.VOCAB_TYPEID)
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['entity_uri'],       "")
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            action="new",
            vocab_id="00000001", orig_vocab_id=None,
            vocab_label="",
            vocab_descr="",
            vocab_uri="",
            continuation_url="/xyzzy/"
            )
        return

    def test_get_copy(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, entity_id="annal", view_id="Vocab_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.VOCAB_TYPEID, entity_id="annal"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.VOCAB_TYPEID)
        self.assertEqual(r.context['entity_id'],        "annal_01")
        self.assertEqual(r.context['orig_id'],          "annal")
        self.assertEqual(r.context['entity_uri'],       None)
        self.assertEqual(r.context['action'],           "copy")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            action="copy",
            vocab_id="annal_01", orig_vocab_id="annal",
            vocab_label="Vocabulary namespace for Annalist-defined terms",
            vocab_uri="",
            vocab_seealso=["https://github.com/gklyne/annalist/blob/master/src/annalist_root/annalist/identifiers.py"],
            continuation_url=""
            )
        return

    def test_get_copy_not_exists(self):
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, 
            entity_id="novocab", view_id="Vocab_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.check_entity_not_found_response(r, 
            err_msg=make_message(
                message.ENTITY_DOES_NOT_EXIST, 
                type_id=layout.VOCAB_TYPEID, 
                id="novocab", 
                label=error_label("testcoll", layout.VOCAB_TYPEID, "novocab")
                )
            )
        return

    def test_get_edit(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.VOCAB_TYPEID, entity_id="annal", view_id="Vocab_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context (values read from test data fixture)
        type_url = collection_entity_view_url(
            coll_id="testcoll", type_id=layout.VOCAB_TYPEID, entity_id="annal"
            )
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          layout.VOCAB_TYPEID)
        self.assertEqual(r.context['entity_id'],        "annal")
        self.assertEqual(r.context['orig_id'],          "annal")
        self.assertEqual(r.context['entity_uri'],       "http://purl.org/annalist/2014/#")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        # Fields
        self._check_context_fields(r, 
            action="edit",
            vocab_id="annal", orig_vocab_id="annal",
            vocab_label="Vocabulary namespace for Annalist-defined terms",
            vocab_uri="http://purl.org/annalist/2014/#",
            vocab_seealso=["https://github.com/gklyne/annalist/blob/master/src/annalist_root/annalist/identifiers.py"],
            continuation_url=""
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_url(
            "edit", "testcoll", layout.VOCAB_TYPEID, 
            entity_id="novocab", view_id="Vocab_view"
            )
        r = self.client.get(u)
        # log.info(r.content)
        self.check_entity_not_found_response(r, 
            err_msg=make_message(
                message.ENTITY_DOES_NOT_EXIST, 
                type_id=layout.VOCAB_TYPEID, 
                id="novocab", 
                label=error_label("testcoll", layout.VOCAB_TYPEID, "novocab")
                )
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new type --------

    def test_post_new_vocab(self):
        self.assertFalse(RecordVocab.exists(self.testcoll, "newvocab"))
        f = vocab_view_form_data(
            vocab_id="newvocab", action="new",
            vocab_uri="test:newvocab",
            update="RecordVocab"
            )
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that new record type exists
        self._check_record_vocab_values("newvocab", update="RecordVocab", vocab_uri="test:newvocab")
        return

    def test_post_new_vocab_cancel(self):
        self.assertFalse(RecordVocab.exists(self.testcoll, "newvocab"))
        f = vocab_view_form_data(
            vocab_id="newvocab", action="new", cancel="Cancel", update="Updated RecordVocab"
            )
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that new record type still does not exist
        self.assertFalse(RecordVocab.exists(self.testcoll, "newvocab"))
        return

    def test_post_new_vocab_missing_id(self):
        f = vocab_view_form_data(action="new", update="RecordVocab")
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context
        self._check_context_fields(r, 
            action="new",
            vocab_id=None, orig_vocab_id="orig_vocab_id",
            vocab_label=None,
            vocab_descr=None,
            vocab_uri=None,
            )
        return

    def test_post_new_vocab_invalid_id(self):
        f = vocab_view_form_data(
            vocab_id="!badvocab", orig_id="orig_vocab_id", action="new", update="RecordVocab"
            )
        u = entitydata_edit_url("new", "testcoll", layout.VOCAB_TYPEID, view_id="Vocab_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context
        self._check_context_fields(r, 
            action="new",
            vocab_id="!badvocab", orig_vocab_id="orig_vocab_id",
            vocab_label=None,
            vocab_descr=None,
            vocab_uri=None,
            )
        return

    #   -------- copy namespace vocabulary --------

    def test_post_copy_vocab(self):
        self.assertFalse(RecordVocab.exists(self.testcoll, "copyvocab"))
        f = vocab_view_form_data(
            vocab_id="copyvocab", 
            orig_id="annal", orig_coll="_annalist_site", action="copy", 
            update="RecordVocab",
            vocab_uri=" test:copyvocab "  # Tests space stripping
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, entity_id="annal", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that new record type exists
        self._check_record_vocab_values("copyvocab", update="RecordVocab", vocab_uri="test:copyvocab")
        return

    def test_post_copy_vocab_cancel(self):
        self.assertFalse(RecordVocab.exists(self.testcoll, "copyvocab"))
        f = vocab_view_form_data(
            vocab_id="copyvocab", orig_id="annal", action="copy", cancel="Cancel", update="RecordVocab"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, entity_id="annal", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that target record vocab still does not exist
        self.assertFalse(RecordVocab.exists(self.testcoll, "copytype"))
        return

    def test_post_copy_vocab_missing_id(self):
        self._create_record_vocab("Default_vocab")
        f = vocab_view_form_data(
            action="copy", 
            orig_id="Default_vocab", 
            update="Updated RecordVocab"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, entity_id="Default_vocab", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context
        self._check_context_fields(r, 
            action="copy",
            vocab_id="", orig_vocab_id="Default_vocab",
            update="Updated RecordVocab"
            )
        return

    def test_post_copy_vocab_invalid_id(self):
        self._create_record_vocab("Default_vocab")
        f = vocab_view_form_data(
            action="copy", 
            vocab_id="!badvocab", orig_id="Default_vocab", 
            update="Updated RecordVocab"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", layout.VOCAB_TYPEID, entity_id="Default_vocab", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context
        self._check_context_fields(r, 
            action="copy",
            vocab_id="!badvocab", orig_vocab_id="Default_vocab",
            update="Updated RecordVocab"
            )
        return

    #   -------- edit type --------

    def test_post_edit_vocab(self):
        self._create_record_vocab("editvocab")
        self._check_record_vocab_values("editvocab")
        f = vocab_view_form_data(
            vocab_id="editvocab", orig_id="editvocab", 
            action="edit", update="Updated RecordVocab"
            )
        u = entitydata_edit_url("edit", "testcoll", layout.VOCAB_TYPEID, entity_id="editvocab", view_id="Vocab_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that new record type exists
        self._check_record_vocab_values("editvocab", update="Updated RecordVocab")
        return

    def test_post_edit_vocab_cancel(self):
        self._create_record_vocab("editvocab")
        self._check_record_vocab_values("editvocab")
        f = vocab_view_form_data(
            vocab_id="editvocab", orig_id="editvocab", 
            action="edit", cancel="Cancel", update="Updated RecordVocab"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.VOCAB_TYPEID, entity_id="editvocab", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'],   self.continuation_url)
        # Check that target record type still does not exist and unchanged
        self._check_record_vocab_values("editvocab")
        return

    def test_post_edit_vocab_missing_id(self):
        self._create_record_vocab("editvocab")
        self._check_record_vocab_values("editvocab")
        # Form post with ID missing
        f = vocab_view_form_data(
            action="edit",
            orig_id="editvocab", 
            update="Updated RecordVocab"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.VOCAB_TYPEID, entity_id="editvocab", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context for re-rendered form
        self._check_context_fields(r, 
            action="edit",
            vocab_id="", orig_vocab_id="editvocab",
            update="Updated RecordVocab"
            )
        # Check original data is unchanged
        self._check_record_vocab_values("editvocab")
        return

    def test_post_edit_vocab_invalid_id(self):
        self._create_record_vocab("editvocab")
        self._check_record_vocab_values("editvocab")
        # Form post with invalid ID
        f = vocab_view_form_data(
            vocab_id="!badvocab", orig_id="editvocab", action="edit", update="Updated RecordVocab"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", layout.VOCAB_TYPEID, entity_id="editvocab", view_id="Vocab_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%(message.RECORD_VOCAB_ID))
        # Test context
        self._check_context_fields(r, 
            action="edit",
            vocab_id="!badvocab", orig_vocab_id="editvocab",
            update="Updated RecordVocab"
            )
        # Check original data is unchanged
        self._check_record_vocab_values("editvocab")
        return

# End.
