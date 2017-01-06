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

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    collection_create_values,
    site_dir, collection_dir, 
    continuation_url_param,
    collection_view_url,
    collection_edit_url,
    collection_entity_view_url,
    site_title,
    render_select_options,
    render_choice_options,
    create_test_user,
    context_view_field,
    check_type_view_context_fields
    )
from entity_testtypedata    import (
    recordtype_dir, 
    recordtype_edit_url,
    recordtype_create_values, 
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values,
    entitydata_delete_confirm_form_data,
    entitydata_default_view_form_data,
    entitydata_recordtype_view_context_data, entitydata_recordtype_view_form_data,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testsitedata    import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from entity_testviewdata    import recordview_url
from entity_testlistdata    import recordlist_url

#   -----------------------------------------------------------------------------
#
#   GenericEntityViewView tests
#
#   -----------------------------------------------------------------------------

class GenericEntityViewViewTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
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
        typeinfo = EntityTypeInfo(self.testcoll, type_id)
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
    #   Form rendering and response tests
    #   -----------------------------------------------------------------------------

    def test_get_default_form_no_login(self):
        self.client.logout()
        u = entity_url("testcoll", "testtype", "entity1")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    def test_post_default_form_use_view(self):
        self._create_entity_data("entityuseview")
        self.assertTrue(EntityData.exists(self.testdata, "entityuseview"))
        f = entitydata_default_view_form_data(
                entity_id="entityuseview", action="view",
                use_view="_view/Type_view", 
                )
        f.pop('entity_id', None)
        u = entitydata_edit_url(
            "view", "testcoll", "testtype", "entityuseview", view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + entitydata_edit_url(
            "view", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view"
            )
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview")
        return

    def test_post_default_form_default_view(self):
        # Set default entity view, then ensure collection view redirects to it
        self._create_entity_data("entitydefaultview")
        f = entitydata_default_view_form_data(
                entity_id="entitydefaultview", action="view",
                default_view="default_view", 
                )
        f.pop('entity_id', None)
        u = entitydata_edit_url(
            action="view", view_id="Default_view",
            coll_id="testcoll", type_id="testtype", entity_id="entitydefaultview"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        v = TestHostUri + u
        self.assertIn(v, r['location'])
        ih = "info_head=Action%20completed"
        im = (
            "info_message="+
            "Default%20view%20for%20collection%20testcoll%20changed%20to%20"+
            "Default_view/testtype/entitydefaultview"
            )
        self.assertIn(ih, r['location'])
        self.assertIn(im, r['location'])
        # Get collection root and check redirect to entity view
        u2 = collection_view_url(coll_id="testcoll")
        r2 = self.client.get(u2)
        self.assertEqual(r2.status_code,   302)
        self.assertEqual(r2.reason_phrase, "FOUND")
        self.assertEqual(r2.content,       "")
        v2 = TestHostUri + entitydata_edit_url(
            coll_id="testcoll", view_id="Default_view", type_id="testtype", entity_id="entitydefaultview"
            )
        self.assertEqual(v2, r2['location'])
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
        # log.info(r.content)     #@@
        entity_label = """Entity testcoll/testtype/entity1"""
        view_label   = """Type definition"""
        permalink    = """<a href="./" class="permalink">&#x1F517;</a>"""
        entity_title = "%s - %s - Collection testcoll"%(entity_label, view_label)
        self.assertContains(r, "<title>%s</title>"%(entity_title,))
        self.assertContains(r, '<h2 class="page-heading">%s %s</h2>'%(view_label, permalink), html=True)
        cont_uri = "?continuation_url=%s"%u + "%3Fcontinuation_url=/xyzzy/"
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
            entity_url       = "/testsite/c/testcoll/d/testtype/entity1/" + cont_uri,
            default_view_url = "/testsite/c/testcoll/d/_view/Default_view/" + cont_uri,
            default_list_url = "/testsite/c/testcoll/d/_list/Default_list/" + cont_uri,
            tooltip1="", # 'title="%s"'%r.context['fields'][0]['field_help'],
            tooltip2="", # 'title="%s"'%r.context['fields'][1]['field_help'],
            tooltip3="", # 'title="%s"'%r.context['fields'][2]['field_help'],
            tooltip4="", # 'title="%s"'%r.context['fields'][3]['field_help'],
            tooltip5="", # 'title="%s"'%r.context['fields'][4]['field_help'],
            tooltip6="", # 'title="%s"'%r.context['fields'][5]['field_help'],
            tooltip7="", # 'title="%s"'%r.context['fields'][6]['field_help'],
            )
        formrow1 = """
            <div class="small-12 medium-6 columns" %(tooltip1)s>
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Type Id</span>
                </div>
                <div class="%(input_classes)s">
                  <a href="%(entity_url)s">entity1</a>
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow2 = """
            <div class="small-12 columns" %(tooltip2)s>
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
            <div class="small-12 columns" %(tooltip3)s>
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
            <div class="small-12 columns" %(tooltip4)s>
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Type URI</span>
                </div>
                <div class="%(input_classes)s">
                  <span>&nbsp;</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow5 = """
            <div class="small-12 columns" %(tooltip5)s>
              <div class="row">
                <div class="%(group_label_classes)s">
                  <span>Supertype URIs</span>
                </div>
                <div class="%(group_placeholder_classes)s">
                  <span>(None)</span>
                </div>
              </div>
            </div>
            """%field_vals(width=12)
        formrow6 = """
            <div class="small-12 medium-6 columns" %(tooltip6)s>
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
        formrow7 = """
            <div class="small-12 medium-6 columns" %(tooltip7)s>
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
        formrow8a = """
            <div class="%(space_classes)s">
              <div class="row">
                <div class="small-12 columns">
                  &nbsp;
                </div>
              </div>
            </div>
            """%field_vals(width=2)
        formrow8b = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_left_classes)s">
                  <input type="submit" name="edit"  value="Edit"
                         title="Edit entity data." />
                  <input type="submit" name="copy"  value="Copy"
                         title="Copy, then edit entity data as new entity." />
                  <input type="submit" name="close" value="Close"
                         title="Return to previous page." />
                </div>
              </div>
            </div>
            """%field_vals(width=4)
        formrow8c = """
            <div class="%(button_wide_classes)s">
              <div class="row">
                <div class="%(button_r_med_up_classes)s">
                  <!-- <input type="submit" name="open_view"    value="View description" /> -->
                  <input type="submit" name="default_view" value="Set default view"
                         title="Select this display as the default view for collection 'testcoll'." />
                  <input type="submit" name="customize"    value="Customize"
                         title="Open 'Customize' view for collection 'testcoll'." />
                </div>
              </div>
            </div>
            """%field_vals(width=6)
        formrow9 = ("""
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
        formrow10 = """
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
        # log.info(r.content)     #@@
        self.assertContains(r, formrow1,  html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5,  html=True)
        self.assertContains(r, formrow6,  html=True)
        self.assertContains(r, formrow7,  html=True)
        self.assertContains(r, formrow8a, html=True)
        self.assertContains(r, formrow8b, html=True)
        self.assertContains(r, formrow8c, html=True)
        self.assertContains(r, formrow9,  html=True)
        # New buttons hidden (for now)
        # self.assertContains(r, formrow10, html=True)
        return

    def test_get_view(self):
        # Note - this test uses Type_view to display en entity of type "testtype"
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        check_type_view_context_fields(self, r, 
            action="edit",
            entity_id="entity1", orig_entity_id=None,
            type_id="testtype",
            type_label="Entity testcoll/testtype/entity1",
            type_comment="Entity coll testcoll, type testtype, entity entity1",
            type_uri="",
            type_supertype_uris=[],
            type_view="Default_view", type_view_options=self.no_view_id + self.view_options,
            type_list="Default_list", type_list_options=self.no_list_id + self.list_options,
            type_aliases=[],
            )
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
