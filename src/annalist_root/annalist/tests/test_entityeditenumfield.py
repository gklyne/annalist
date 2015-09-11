"""
Entity editing tests for enumerated value fields
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

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site, resetSitedata
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    collection_create_values,
    continuation_url_param,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_create_values, 
    )
from entity_testviewdata            import (
    recordview_url, 
    recordview_create_values, recordview_values,
    recordview_entity_view_form_data, 
    )
from entity_testentitydata          import (
    entity_url, entitydata_edit_url, 
    entitydata_value_keys, entitydata_create_values, entitydata_values,
    entitydata_default_view_form_data,
    )

#   -----------------------------------------------------------------------------
#
#   Entity edit enumerated value field tests
#
#   -----------------------------------------------------------------------------

class EntityEditEnumFieldTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testtype"))
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})

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

    def _create_record_view(self, view_id):
        "Helper function creates record view entry with supplied view_id"
        t = RecordView.create(
            self.testcoll, view_id, 
            recordview_create_values(view_id=view_id, target_record_type="annal:View")
            )
        return t

    def _check_record_view_values(
            self, view_id, view_uri=None, update="RecordView", 
            num_fields=4,
            update_dict=None,
            ):
        "Helper function checks content of record view entry with supplied view_id"
        self.assertTrue(RecordView.exists(self.testcoll, view_id))
        t = RecordView.load(self.testcoll, view_id)
        self.assertEqual(t.get_id(), view_id)
        self.assertEqual(t.get_view_url(), TestHostUri + recordview_url("testcoll", view_id))
        v = recordview_values(
            view_id=view_id, view_uri=view_uri, 
            target_record_type="annal:View",
            update=update, 
            num_fields=num_fields,
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

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

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
        self.assertFalse(EntityData.exists(self.testdata, "entitynewtype"))
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

    def test_post_new_entity_enum_type_new(self):
        self.assertFalse(EntityData.exists(self.testdata, "entitynewtype"))
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="new", update="Updated entity", 
                new_enum="entity_type__new_edit"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # v = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        v = entitydata_edit_url("edit", "testcoll", "_type", "testtype", view_id="Type_view")
        w = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
        c = continuation_url_param(w)
        self.assertIn(TestHostUri+v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_new_entity_enum_type_new_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="new", update="Updated entity", 
                new_enum="entity_type__new_edit"
                )
        u = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit entity --------

    def test_post_edit_entity_new_view(self):
        self._create_entity_data("entitynewview")
        e1 = self._check_entity_data_values("entitynewview")
        f  = entitydata_default_view_form_data(
                entity_id="entitynewview", action="edit", update="Updated entity", 
                new_view="New view"
                )
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewview", 
            view_id="Default_view"
            )
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
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewview", 
            view_id="Default_view"
            )
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
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewfield", 
            view_id="Default_view"
            )
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
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewfield", 
            view_id="Default_view"
            )
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
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
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
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    def test_post_edit_entity_enum_type_new(self):
        self._create_entity_data("entitynewtype")
        e1 = self._check_entity_data_values("entitynewtype")
        f  = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="edit", update="Updated entity", 
                new_enum="entity_type__new_edit"
                )
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # v = entitydata_edit_url("new", "testcoll", "_type", view_id="Type_view")
        v = entitydata_edit_url("edit", "testcoll", "_type", "testtype", view_id="Type_view")
        w = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
        c = continuation_url_param(w)
        self.assertIn(TestHostUri+v, r['location'])
        self.assertIn(c, r['location'])
        self._check_entity_data_values("entitynewtype", update="Updated entity")
        return

    def test_post_edit_entity_enum_type_new_no_login(self):
        self.client.logout()
        f = entitydata_default_view_form_data(
                entity_id="entitynewtype", action="edit", update="Updated entity", 
                new_enum="entity_type__new_edit"
                )
        u  = entitydata_edit_url(
            "edit", "testcoll", "testtype", entity_id="entitynewtype", 
            view_id="Default_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit view: tests 'new' button on enumeration in repeated value --------

    def test_post_edit_view_enum_field_new(self):
        self._create_record_view("editview")
        self._check_record_view_values("editview")
        f = recordview_entity_view_form_data(
            view_id="editview", orig_id="editview", 
            action="edit", update="Updated RecordView",
            new_enum="View_fields__3__Field_id__new_edit"
            )
        u = entitydata_edit_url(
            "edit", "testcoll", "_view", 
            entity_id="editview", view_id="View_view"
            )
        r = self.client.post(u, f)
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        # v = entitydata_edit_url("new", "testcoll", "_field", view_id="Field_view")
        v = entitydata_edit_url("edit", "testcoll", "_field", "Entity_comment", view_id="Field_view")
        w = entitydata_edit_url(
            "edit", "testcoll", "_view", entity_id="editview", 
            view_id="View_view"
            )
        c = continuation_url_param(w)
        self.assertIn(TestHostUri+v, r['location'])
        self.assertIn(c, r['location'])
        self._check_record_view_values("editview", update="Updated RecordView")
        return

# End.
