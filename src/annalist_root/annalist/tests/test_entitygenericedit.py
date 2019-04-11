from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

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
from annalist                       import message

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

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    test_layout,
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from .entity_testutils import (
    make_message, make_quoted_message,
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
    context_bind_fields,
    check_type_view_context_fields
    )
from .entity_testtypedata import (
    recordtype_dir, 
    recordtype_edit_url,
    recordtype_create_values, 
    type_view_context_data, 
    type_view_form_data,
    )

from .entity_testentitydata import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values,
    default_view_form_data, 
    entitydata_delete_confirm_form_data,
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
#   GenericEntityEditView tests
#
#   -----------------------------------------------------------------------------

class GenericEntityEditViewTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        init_annalist_test_coll()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", 
            recordtype_create_values("testtype", type_uri="test:testtype")
            )
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        self.no_options = [ FieldChoice('', label="(no options)") ]
        self.no_view_id = [ FieldChoice('', label="(view id)") ]
        self.no_list_id = [ FieldChoice('', label="(list id)") ]
        self.view_options = get_site_views_linked("testcoll")
        self.list_options = get_site_lists_linked("testcoll")
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
        return

    @classmethod
    def setUpClass(cls):
        super(GenericEntityEditViewTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(GenericEntityEditViewTest, cls).tearDownClass()
        # resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_entity_data(self, entity_id, update="Entity"):
        "Helper function creates entity data with supplied entity_id"
        type_uri = "test:testtype"
        e = EntityData.create(self.testdata, entity_id, 
            entitydata_create_values(
                entity_id, update=update, coll_id="testcoll", type_id="testtype",
                type_uri=type_uri, supertype_uris=[type_uri+"/super1", type_uri+"/super2"],
                )
            )
        return e

    def _check_entity_data_values(self, 
            entity_id=None, type_id="testtype", type_uri=None, 
            update="Entity", 
            update_dict=None
            ):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        # log.info("_check_entity_data_values: type_id %s, entity_id %s"%(type_id, entity_id))
        typeinfo = EntityTypeInfo(self.testcoll, type_id)
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, entity_id))
        e = typeinfo.entityclass.load(typeinfo.entityparent, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(
            e.get_view_url(""), 
            TestHostUri + entity_url("testcoll", type_id, entity_id)
            )
        if type_uri is None:
            type_uri = "test:"+type_id
        v = entitydata_values(
            entity_id, type_id=type_id, update=update, 
            type_uri=type_uri, supertype_uris=[type_uri+"/super1", type_uri+"/super2"]
            )
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
        f = default_view_form_data(action="new", 
            entity_id="entityuseview", 
            update="Updated entity", 
            use_view="_type/Type_view", 
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
        self.assertContains(r, "<title>Type definition - Collection testcoll</title>")
        field_vals = default_fields(
            coll_id="testcoll", type_id="testtype", entity_id="00000001",
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
                  <span>Type Id</span>
                </div>
                <div class="%(input_classes)s">
                    <input type="text" size="64" name="entity_id" 
                           placeholder="(type id)" value="00000001"/>
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
                  <input type="text" size="64" name="Type_label"
                  placeholder="(label)"  
                  value="%(default_label_esc)s"/>
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
            <div class="small-12 columns" title="%(tooltip4)s">
              <div class="row view-value-row">
                <div class="%(label_classes)s">
                  <span>Type URI</span>
                </div>
                <div class="%(input_classes)s">
                  <input type="text" size="64" name="Type_uri"
                         placeholder="(Type URI or CURIE)"  
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
                  <input type="submit" name="save"      value="Save"   title="%(button_save_tip)s"/>
                  <input type="submit" name="view"      value="View"   title="%(button_view_tip)s"/>
                  <input type="submit" name="cancel"    value="Cancel" title="%(button_cancel_tip)s"/>
                </div>
              </div>
            </div>
            """%field_vals(width=4)
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
        check_type_view_context_fields(self, r, 
            action="new",
            entity_id="00000001", orig_entity_id=None,
            type_id="testtype",
            type_label=default_label("testcoll", "testtype", "00000001"),
            type_comment=default_comment("testcoll", "testtype", "00000001"),
            type_uri="",
            type_supertype_uris=[],
            type_view="Default_view", type_view_options=self.no_view_id + self.view_options,
            type_list="Default_list", type_list_options=self.no_list_id + self.list_options,
            type_aliases=[],
            )
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
        self.assertEqual(r.context['orig_id'],          None)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_url'], "")
        return

    def test_get_edit(self):
        # Note - this test uses Type_view to display en entity of type "testtype"
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        check_type_view_context_fields(self, r, 
            action="edit",
            entity_id="entity1", orig_entity_id="entity1",
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

    def test_get_copy(self):
        # Note - this test uses Type_view to display en entity of type "testtype"
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        check_type_view_context_fields(self, r, 
            action="copy",
            entity_id="entity1_01", orig_entity_id="entity1",
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
        u = entitydata_edit_url("edit", "no_collection", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        msg_text = make_message(message.COLLECTION_NOT_EXISTS, id="no_collection")
        self.assertContains(r, msg_text, status_code=404)
        return

    def test_get_view_no_type(self):
        u = entitydata_edit_url("edit", "testcoll", "no_type", entity_id="entity1", view_id="Type_view")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        msg_text = make_message(message.RECORD_TYPE_NOT_EXISTS, id="no_type")
        self.assertContains(r, msg_text, status_code=404)
        return

    def test_get_view_no_view(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1", view_id="no_view")
        with SuppressLogging(logging.WARNING):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        msg_text = make_message(message.RECORD_VIEW_NOT_EXISTS, id="no_view")
        self.assertContains(r, msg_text)
        return

    def test_get_edit_no_entity(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynone", view_id="Type_view")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.check_entity_not_found_response(r, 
            err_msg=make_message(
                message.ENTITY_DOES_NOT_EXIST, 
                id="entitynone", 
                label=error_label("testcoll", "testtype", "entitynone")
                ),
            redirect_url="/xyzzy/"
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    # @@TODO: consider changing Type_view to Default_view in the following

    #   -------- new entity --------

    def test_post_new_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = type_view_form_data(action="new", 
            type_type_id="testtype", 
            type_entity_id="newentity"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", update="RecordType")
        return

    def test_post_new_entity_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="new", 
            type_type_id="testtype", 
            type_entity_id="newentity"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_no_continuation(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = type_view_form_data(action="new", 
            type_type_id="testtype", 
            type_entity_id="newentity"
            )
        f['continuation_url'] = ""
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", update="RecordType")
        return

    def test_post_new_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="newentity", 
            cancel="Cancel"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(
            r['location'], entitydata_list_type_url("testcoll", "testtype")
            )
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    def test_post_new_entity_id_with_leading_treailing_spaces(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = type_view_form_data(action="new", 
            type_type_id="testtype", 
            type_entity_id="  newentity  "
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check new entity data created, except label, comment
        self._check_entity_data_values("newentity", 
            update_dict={'rdfs:label': None, 'rdfs:comment': None}
            )
        return

    def test_post_new_entity_blank_id(self):
        f = type_view_form_data(action="new", 
            type_type_id="testtype", 
            type_entity_id=""
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = type_view_context_data(action="new", 
            type_type_id="testtype",
            record_type=None
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_new_entity_missing_id(self):
        self.assertFalse(EntityData.exists(self.testdata, "orig_entity_id"))
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id=None, orig_id="orig_entity_id"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(
            r['location'], entitydata_list_type_url("testcoll", "testtype")
            )
        # Check that new record type exists with default id
        self.assertTrue(EntityData.exists(self.testdata, "orig_entity_id"))
        return

    def test_post_new_entity_invalid_id(self):
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="!badentity", orig_id="orig_entity_id"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = type_view_context_data(action="new",
            type_type_id="testtype", 
            type_entity_id="!badentity", orig_id="orig_entity_id", 
            record_type="annal:EntityData"
            )
        # log.info(repr(context_bind_fields(r.context)['fields'][1]))
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = type_view_form_data(action="new",
            type_type_id="Default_type", 
            type_entity_id="newentity", 
            )
        u = entitydata_edit_url("new", "testcoll", "Default_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "Default_type"))
        # Check new entity data created
        self._check_entity_data_values("newentity", 
            type_id="Default_type", type_uri="annal:Default_type",
            update="RecordType",
            update_dict=
                { '@type':          ['annal:Default_type', 'annal:EntityData']
                , 'annal:uri':      f['Type_uri']   # because using Type_view
                }
            )
        return

    def create_new_type(self, coll_id, type_id):
        self.assertFalse(RecordType.exists(self.testcoll, type_id))
        f = type_view_form_data(action="new", 
            coll_id=coll_id, 
            type_entity_id=type_id, type_entity_uri="test:"+type_id,
            update="RecordType"
            )
        u = entitydata_edit_url("new", coll_id, type_id="_type", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url(coll_id, "_type"))
        self.assertTrue(RecordType.exists(self.testcoll, type_id))
        return

    def test_new_entity_new_recorddata(self):
        # Checks logic for creating an entity which may require creation of new recorddata
        self.create_new_type("testcoll", "newtype")
        # Create new entity
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = default_view_form_data(action="new", entity_id="newentity", type_id="newtype")
        u = entitydata_edit_url("new", "testcoll", "newtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "newtype"))
        # Check new entity data created
        self._check_entity_data_values("newentity", type_id="newtype")
        return

    def test_new_entity_builtin_type(self):
        # Create new entity
        self.assertFalse(RecordField.exists(self.testcoll, "newfield", altscope="all"))
        f = default_view_form_data(action="new", 
            type_id="_field", orig_type="Default_type",
            entity_id="newfield",
            )
        u = entitydata_edit_url("new", "testcoll", "Default_type", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "Default_type"))
        # Check new entity data created
        self.assertTrue(RecordField.exists(self.testcoll, "newfield", self.testsite))
        self._check_entity_data_values(
            "newfield", type_id="_field", type_uri="annal:Field",
            update_dict={ '@type': ['annal:Field'] }
            )
        return

    def test_post_new_entity_add_view_field(self):
        self.assertFalse(EntityData.exists(self.testdata, "entityaddfield"))
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entityaddfield", 
            add_view_field="View_fields"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        c = continuation_url_param(w)
        a = "add_field=View_fields"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(a, r['location'])
        self._check_entity_data_values("entityaddfield", update="RecordType")
        return

    def test_post_new_entity_add_view_field_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entityaddfield", 
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
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entityeditview", 
            open_view="Edit view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url(
            "edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view"
            )
        w = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view"
            )
        c = continuation_url_param(w)
        a = "add_field="
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertNotIn(a, r['location'])
        self._check_entity_data_values("entityeditview", update="RecordType")
        return

    def test_post_new_entity_edit_view_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entityeditview", 
            open_view="Edit view"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_use_view(self):
        self.assertFalse(EntityData.exists(self.testdata, "entityuseview"))
        f = default_view_form_data(action="new", 
            entity_id="entityuseview", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view"
            )
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview", update="Updated entity")
        return

    def test_post_new_entity_use_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="new", 
            entity_id="entityuseview", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_view(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewview"))
        f = default_view_form_data(action="new", 
            entity_id="entitynewview", 
            update="Updated entity", 
            new_view="New view"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview", update="Updated entity")
        return

    def test_post_new_entity_new_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="new", 
            entity_id="entitynewview", 
            update="Updated entity", 
            new_view="New view"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_field(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewfield"))
        f = default_view_form_data(action="new", 
            entity_id="entitynewfield", 
            update="Updated entity", 
            new_field="New field"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield", update="Updated entity")
        return

    def test_post_new_entity_new_field_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="new", 
            entity_id="entitynewfield", 
            update="Updated entity", 
            new_field="New field"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_new_type(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewview"))
        f = default_view_form_data(action="new", 
            entity_id="entitynewtype", 
            update="Updated entity", 
            new_type="New type"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_new_entity_new_type_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="new", 
            entity_id="entitynewtype", 
            update="Updated entity", 
            new_type="New type"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_new_entity_default_view(self):
        # Set default entity view, then ensure collection view redirects to it
        f = default_view_form_data(action="new", 
            entity_id="entity1",
            default_view="default_view", 
            )
        u = entitydata_edit_url(
            action="view", view_id="Default_view",
            coll_id="testcoll", type_id="testtype", entity_id="entity1"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertIn(u, r['location'])
        ih = "info_head=Action%20completed"
        im = (
            "info_message="+
            "Default%20view%20for%20collection%20testcoll%20changed%20to%20"+
            "Default_view/testtype/entity1"
            )
        self.assertIn(ih, r['location'])
        self.assertIn(im, r['location'])
        # Get collection root and check redirect to entity view
        u2 = collection_view_url(coll_id="testcoll")
        r2 = self.client.get(u2)
        self.assertEqual(r2.status_code,   302)
        self.assertEqual(r2.reason_phrase, "Found")
        self.assertEqual(r2.content,       b"")
        v2 = entitydata_edit_url(
            coll_id="testcoll", view_id="Default_view", type_id="testtype", entity_id="entity1"
            )
        self.assertEqual(v2, r2['location'])
        return

    def test_post_new_entity_customize(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitycustomize"))
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entitycustomize", 
            customize="Customize"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = collection_edit_url(coll_id="testcoll")
        w = entitydata_edit_url(
            action="edit", 
            coll_id="testcoll", 
            type_id="testtype", 
            entity_id="entitycustomize", 
            view_id="Type_view"
            )
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitycustomize", update="RecordType")
        return

    def test_post_new_entity_customize_no_config_permission(self):
        self.client.logout()
        create_test_user(
            self.testcoll, "noconfiguser", "testpassword",
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE"]
            )
        loggedin = self.client.login(username="noconfiguser", password="testpassword")
        self.assertTrue(loggedin)
        f = type_view_form_data(action="new",
            type_type_id="testtype", 
            type_entity_id="entitycustomize", 
            customize="Customize"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   403)
        self.assertEqual(r.reason_phrase, "Forbidden")
        # print r.content
        self._check_entity_data_values("entitycustomize", update="RecordType")
        return

    #   -------- copy type --------

    def test_post_copy_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = type_view_form_data(action="copy", 
            type_type_id="testtype",
            type_entity_id="copytype"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists
        self._check_entity_data_values("copytype", update="RecordType")
        return

    def test_post_copy_entity_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="copy", 
            type_type_id="testtype", 
            type_entity_id="copytype"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = type_view_form_data(action="copy",
            type_type_id="testtype", 
            type_entity_id="copytype",
            cancel="Cancel"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    def test_post_copy_entity_blank_id(self):
        f = type_view_form_data(action="copy", 
            type_type_id="testtype", 
            type_entity_id="", orig_id="entity1"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = type_view_context_data(
            action="copy", type_type_id="testtype",
            orig_id="entity1",
            record_type="annal:EntityData"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_missing_id(self):
        # self.assertFalse(EntityData.exists(self.testdata, "orig_entity_id"))
        f = type_view_form_data(action="copy",
            type_type_id="testtype", 
            type_entity_id=None, orig_id="orig_entity_id",
            update="updated1"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(
            r['location'], entitydata_list_type_url("testcoll", "testtype")
            )
        # Check that new record type exists with default id
        self.assertTrue(EntityData.exists(self.testdata, "entity1"))
        self._check_entity_data_values(entity_id="orig_entity_id", update="updated1")
        return

    def test_post_copy_entity_invalid_id(self):
        f = type_view_form_data(action="copy",
            type_type_id="testtype", 
            type_entity_id="!badentity", orig_id="entity1",
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = type_view_context_data(action="copy",
            type_type_id="testtype",
            type_entity_id="!badentity", orig_id="entity1",
            record_type="annal:EntityData"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_add_view_field(self):
        self._create_entity_data("entyity1")
        self._check_entity_data_values("entyity1")
        f = type_view_form_data(action="copy",
            type_type_id="testtype",
            type_entity_id="entityaddfield",
            update="Updated entity", 
            add_view_field="View_fields"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
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
        f = type_view_form_data(action="copy",
            type_type_id="testtype",
            type_entity_id="entityaddfield",
            update="Updated entity", 
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
        f = type_view_form_data(action="copy",
            type_type_id="testtype",
            type_entity_id="entityeditview", 
            update="Updated entity", 
            open_view="Edit view"
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url(
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
        f = type_view_form_data(action="copy",
            type_type_id="testtype",
            type_entity_id="entityeditview", 
            update="Updated entity", 
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
        f = default_view_form_data(action="copy", 
            entity_id="entityuseview1", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview1", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview1", update="Updated entity")
        return

    def test_post_copy_entity_use_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="copy", 
            entity_id="entityuseview1", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_copy_entity_new_view(self):
        self._create_entity_data("entitynewview")
        self._check_entity_data_values("entitynewview")
        f = default_view_form_data(action="copy", 
            entity_id="entitynewview1", 
            update="Updated entity", 
            new_view="New view"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview1", update="Updated entity")
        return

    def test_post_copy_entity_new_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="copy", 
            entity_id="entitynewview1", 
            update="Updated entity", 
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
        f = default_view_form_data(action="copy", 
            entity_id="entitynewfield1", 
            update="Updated entity", 
            new_field="New field"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield1", update="Updated entity")
        return

    def test_post_copy_entity_new_field_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="copy", 
            entity_id="entitynewfield1", 
            update="Updated entity", 
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
        f = default_view_form_data(action="copy", 
            entity_id="entitynewtype1", 
            update="Updated entity", 
            new_type="New type"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        w = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype1", view_id="Default_view")
        c = continuation_url_param(w)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype1", update="Updated entity")
        return

    def test_post_copy_entity_new_type_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="copy", 
            entity_id="entitynewtype1", 
            update="Updated entity", 
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
        f  = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityedit", 
            update="Updated entity"
            )
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityedit", view_id="Type_view"
            )
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        self._check_entity_data_values("entityedit", update="Updated entity")
        return

    def test_post_edit_entity_blank_label_comment(self):
        self._create_entity_data("entityedit")
        e1 = self._check_entity_data_values("entityedit")
        f  = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityedit", 
            update="Updated entity"
            )
        f['Type_label']   = ""
        f['Type_comment'] = ""
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entityedit", view_id="Type_view"
            )
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(
            r['location'], entitydata_list_type_url("testcoll", "testtype")
            )
        self._check_entity_data_values("entityedit", update="Updated entity", 
            update_dict=
                { 'rdfs:label':   "Entityedit"
                , 'rdfs:comment': "Entityedit"
                }
            )
        return

    def test_post_edit_entity_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="edit", type_entity_id="edittype")
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
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
        f  = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityeditid2", orig_id="entityeditid1"
            )
        f['continuation_url'] = c1
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditid1", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        c2 = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityeditid2", view_id="Type_view")
        self.assertEqual(r['location'], c2)
        # self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "entityeditid1"))
        self._check_entity_data_values("entityeditid2", update="RecordType")
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
        f = type_view_form_data(action="edit", 
            type_entity_id="entityedittype", orig_id="entityedittype", 
            type_type_id="newtype", orig_type="testtype"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedittype", view_id="Default_view")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(EntityData.exists(newtypedata, "entityedittype"))
        return

    def test_post_edit_entity_new_builtin_type(self):
        # Test logic for changing type to built-in type (_field)
        self._create_entity_data("entityedittype")
        self._check_entity_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id set to "_field"
        f = type_view_form_data(action="edit", 
            type_entity_id="entityedittype", orig_id="entityedittype", 
            type_type_id="_field", orig_type="testtype"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityedittype", view_id="Default_view")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "_field"))
        self.assertFalse(EntityData.exists(self.testdata, "entityedittype"))
        self.assertTrue(RecordField.exists(self.testcoll, "entityedittype"))
        return

    def test_post_edit_entity_cancel(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Post from cancelled edit form
        f = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="edittype", 
            update="Updated entity",
            cancel="Cancel"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(r['location'], entitydata_list_type_url("testcoll", "testtype"))
        # Check that target record type still does not exist and unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_blank_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID missing
        f = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="", orig_id="edittype",
            update="Updated entity"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = type_view_context_data(action="edit", 
            type_type_id="testtype", 
            orig_id="edittype",
            record_type="test:testtype",
            update="Updated entity"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_missing_id(self):
        self.assertTrue(EntityData.exists(self.testdata, "entity1"))
        f = type_view_form_data(action="edit", 
            type_type_id="testtype",
            type_entity_id=None, orig_id="entity1", 
            update="updated1"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entity1", view_id="Type_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertEqual(
            r['location'], entitydata_list_type_url("testcoll", "testtype")
            )
        # Check that new record type exists with default id
        self._check_entity_data_values(entity_id="entity1", update="updated1")
        return

    def test_post_edit_entity_invalid_id(self):
        self._create_entity_data("edittype")
        self._check_entity_data_values("edittype")
        # Form post with ID malformed
        f = type_view_form_data(action="edit", 
            type_type_id="testtype",
            type_entity_id="!badentity", orig_id="edittype"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype", view_id="Type_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = type_view_context_data(action="edit",
            type_type_id="testtype", 
            type_entity_id="!badentity", orig_id="edittype",
            record_type="test:testtype"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

    def test_post_edit_entity_add_view_field(self):
        self._create_entity_data("entityaddfield")
        e1 = self._check_entity_data_values("entityaddfield")
        f  = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityaddfield", 
            update="Updated entity", 
            add_view_field="View_fields"
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityaddfield", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        c = continuation_url_param(u)
        a = "add_field=View_fields"
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self.assertIn(a, r['location'])
        self._check_entity_data_values("entityaddfield", update="Updated entity")
        return

    def test_post_edit_entity_add_view_field_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityaddfield", 
            update="Updated entity", 
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
        f  = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityeditview", 
            update="Updated entity", 
            open_view="Edit view"
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Type_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "_view", view_id="View_view", entity_id="Type_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityeditview", update="Updated entity")
        return

    def test_post_edit_entity_edit_view_no_login(self):
        self.client.logout()
        f = type_view_form_data(action="edit", 
            type_type_id="testtype", 
            type_entity_id="entityeditview", 
            update="Updated entity", 
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
        f  = default_view_form_data(action="edit", 
            entity_id="entityuseview", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview", update="Updated entity")
        return

    def test_post_edit_entity_use_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="edit", 
            entity_id="entityuseview", 
            update="Updated entity", 
            use_view="_view/Type_view", 
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_new_view(self):
        self._create_entity_data("entitynewview")
        e1 = self._check_entity_data_values("entitynewview")
        f  = default_view_form_data(action="edit", 
            entity_id="entitynewview", 
            update="Updated entity", 
            new_view="New view"
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_view", view_id="View_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewview", update="Updated entity")
        return

    def test_post_edit_entity_new_view_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="edit", 
            entity_id="entitynewview", 
            update="Updated entity", 
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
        f  = default_view_form_data(action="edit", 
            entity_id="entitynewfield", 
            update="Updated entity", 
            new_field="New field"
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewfield", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewfield", update="Updated entity")
        return

    def test_post_edit_entity_new_field_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="edit", 
            entity_id="entitynewfield", 
            update="Updated entity", 
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
        f  = default_view_form_data(action="edit", 
            entity_id="entitynewtype", 
            update="Updated entity", 
            new_type="New type"
            )
        u  = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entitynewtype", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        c = continuation_url_param(u)
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_edit_entity_new_type_no_login(self):
        self.client.logout()
        f = default_view_form_data(action="edit", 
            entity_id="entitynewtype", 
            update="Updated entity", 
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
        f = default_view_form_data(action="edit", entity_id="entityeditview", view="View")
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entityeditview", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e = entitydata_edit_url(
            "view", "testcoll", "testtype", entity_id="entityeditview", view_id="Default_view"
            )
        l = continuation_url_param(entitydata_list_type_url("testcoll", "testtype"))
        c = continuation_url_param(u, prev_cont=l)
        self.assertIn(e, r['location'])
        self.assertIn(c, r['location'])
        return

    #   -------- view type --------

    def test_post_view_entity_use_view(self):
        self._create_entity_data("entityuseview")
        e1 = self._check_entity_data_values("entityuseview")
        # View doesn't return form entry field values...
        f  = default_view_form_data(action="view",
            type_id="testtype",
            entity_id="entityuseview",
            use_view="_view/Type_view", 
            )
        u  = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityuseview", view_id="Default_view")
        r  = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("view", "testcoll", "testtype", entity_id="entityuseview", view_id="Type_view")
        c = continuation_url_param("/testsite/c/testcoll/d/testtype/")
        self.assertIn(v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entityuseview")
        return

# End.
