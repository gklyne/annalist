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
    type_view_context_data, 
    type_view_form_data,
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, 
    entitydata_list_type_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    default_view_context_data, 
    default_view_form_data, entitydata_delete_confirm_form_data,
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
                label="RecordType testcoll/_type/testtype",
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
        expect_context = default_view_context_data(
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
        return

    def test_get_edit(self):
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="entity1")
        r = self.client.get(u+"?continuation_url=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, "<title>Entity testcoll/testtype/entity1 - Default record view - Collection testcoll</title>")
        # Test context
        expect_context = default_view_context_data(
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
        f = default_view_form_data(entity_id="newentity", action="new")
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
        f = default_view_form_data(entity_id="newentity", action="new", cancel="Cancel")
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
        f = default_view_form_data(action="new", entity_id="")
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = default_view_context_data(
            coll_id="testcoll", type_id="testtype", 
            entity_id="", orig_id="orig_entity_id",
            type_ref="", type_choices=self.type_ids,
            action="new"
            )
        self.assertEqual(len(r.context['fields']), 3) # 4 fields over 3 rows
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_new_entity_invalid_id(self):
        f = default_view_form_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        u = entitydata_edit_url("new", "testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context
        expect_context = default_view_context_data(
            coll_id="testcoll", type_id="testtype", 
            entity_id="!badentity", orig_id="orig_entity_id",
            type_ref="_type/testtype", type_choices=self.type_ids,
            action="new"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = default_view_form_data(entity_id="newentity", type_id="Default_type", action="new")
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
        f = type_view_form_data(action="new",
            coll_id="testcoll", 
            type_entity_id="newtype",            
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
        f = default_view_form_data(entity_id="newentity", type_id="newtype", action="new")
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
        f = default_view_form_data(entity_id="copytype", action="copy")
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
        f = default_view_form_data(entity_id="copytype", action="copy", cancel="Cancel")
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
        f = default_view_form_data(action="copy", entity_id="", orig_id="entity1")
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = default_view_context_data(
            action="copy", orig_id="entity1",
            type_ref="", type_choices=self.type_ids
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    def test_post_copy_entity_invalid_id(self):
        f = default_view_form_data(
            entity_id="!badentity", orig_id="entity1", action="copy"
            )
        u = entitydata_edit_url("copy", "testcoll", "testtype", entity_id="entity1")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        expect_context = default_view_context_data(
            action="copy", entity_id="!badentity", orig_id="entity1",
            type_ref="_type/testtype", type_choices=self.type_ids,
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        return

    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_entity_data("entityedit")
        self._check_entity_data_values("entityedit")
        f  = default_view_form_data(entity_id="entityedit", action="edit", update="Updated entity")
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
        f  = default_view_form_data(entity_id="entityeditid2", orig_id="entityeditid1", action="edit")
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
        f = default_view_form_data(
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
        f = default_view_form_data(entity_id="edittype", action="edit", cancel="Cancel", update="Updated entity")
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
        f = default_view_form_data(
            action="edit", 
            entity_id="", orig_id="edittype",
            update="Updated entity"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = default_view_context_data(
            action="edit", update="Updated entity",
            orig_id="edittype",
            type_ref="", type_choices=self.type_ids,
            record_type="/testsite/c/testcoll/d/_type/testtype/"
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
        f = default_view_form_data(
            entity_id="!badentity", orig_id="edittype", action="edit"
            )
        u = entitydata_edit_url("edit", "testcoll", "testtype", entity_id="edittype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        # Test context for re-rendered form
        expect_context = default_view_context_data(
            entity_id="!badentity", orig_id="edittype", action="edit",
            type_ref="_type/testtype", type_choices=self.type_ids,
            record_type="/testsite/c/testcoll/d/_type/testtype/"
            )
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)
        # Check stored entity is unchanged
        self._check_entity_data_values("edittype")
        return

# End.
