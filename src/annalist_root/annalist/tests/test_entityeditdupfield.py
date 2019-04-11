from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Entity editing tests for duplicated fields
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

from annalist.views.form_utils.fieldchoice  import FieldChoice

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    test_layout,
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from .entity_testfielddesc import get_field_description, get_bound_field
from .entity_testutils import (
    collection_create_values,
    continuation_url_param,
    create_test_user,
    context_view_field,
    context_bind_fields,
    context_field_row
    )
from .entity_testtypedata import (
    recordtype_url,
    recordtype_edit_url,
    recordtype_create_values,
    )
from .entity_testviewdata import (
    recordview_url, 
    recordview_create_values, recordview_values, recordview_values_add_field,
    )
from .entity_testentitydata import (
    entity_url, entitydata_edit_url, 
    entitydata_value_keys,
    entitydata_create_values, entitydata_values, entitydata_values_add_field, 
    default_view_form_data, entitydata_form_add_field,
    default_view_context_data,
    default_comment
    )
from .entity_testsitedata import (
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
#   Helper function to buiold tyest context value
#
#   -----------------------------------------------------------------------------

def dupfield_view_context_data(
        entity_id=None, orig_id=None, 
        coll_id="testcoll", type_id="testtype", 
        type_ref=None, type_choices=None, type_ids=[],
        entity_label=None,
        entity_descr=None,
        entity_descr2=None,
        entity_descr3=None,
        record_type="annal:EntityData",
        action=None, update="Entity", view_label="RecordView testcoll/DupField_view",
        continuation_url=None
    ):
    context_dict = default_view_context_data(
        entity_id=entity_id, orig_id=orig_id, 
        coll_id=coll_id, type_id=type_id, 
        type_ref=type_ref, type_choices=type_choices, type_ids=type_ids,
        entity_label=entity_label, entity_descr=entity_descr,
        record_type=record_type,
        action=action, update=update, view_label=view_label,
        continuation_url=continuation_url
        )
    context_dict['fields'].append(
        context_field_row(
            get_bound_field("Entity_comment", entity_descr2, 
                name="Entity_comment__2",
                prop_uri="rdfs:comment__2"
                )
            )
        )
    context_dict['fields'].append(
        context_field_row(
            get_bound_field("Entity_comment", entity_descr3, 
                name="Entity_comment__3",
                prop_uri="rdfs:comment_alt"
                )
            )
        )
    return context_dict

#   -----------------------------------------------------------------------------
#
#   Entity edit duplicated field tests
#
#   -----------------------------------------------------------------------------

class EntityEditDupFieldTest(AnnalistTestCase):

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", 
            collection_create_values("testcoll")
            )
        self.testtype = RecordType.create(self.testcoll, "testtype", 
            recordtype_create_values("testcoll", "testtype")
            )
        self.testdata = RecordTypeData.create(self.testcoll, "testtype", {})
        # Create view with repeated field id
        self.viewdata = recordview_create_values(view_id="DupField_view")
        recordview_values_add_field(
            self.viewdata, 
            field_id="Entity_comment", 
            field_placement="small:0,12"
            )
        recordview_values_add_field(
            self.viewdata, 
            field_id="Entity_comment",
            field_property_uri="rdfs:comment_alt",
            field_placement="small:0,12"
            )
        self.testview = RecordView.create(self.testcoll, "DupField_view", self.viewdata)
        # Other data
        self.type_ids = get_site_types_linked("testcoll")
        self.type_ids.append(FieldChoice("_type/testtype", 
                label="RecordType testcoll/_type/testtype",
                link=recordtype_url("testcoll", "testtype")
            ))
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        return

    @classmethod
    def tearDownClass(cls):
        super(EntityEditDupFieldTest, cls).tearDownClass()
        resetSitedata(scope="collections") #@@checkme@@
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _check_record_view_values(self, view_id, view_values):
        "Helper function checks content of record view entry with supplied view_id"
        self.assertTrue(RecordView.exists(self.testcoll, view_id))
        t = RecordView.load(self.testcoll, view_id)
        self.assertEqual(t.get_id(), view_id)
        self.assertDictionaryMatch(t.get_values(), view_values)
        return t

    def _create_entity_data(self, 
        entity_id, type_id="testtype", update="Entity", 
        comment2="Comment field 2",
        comment3="Comment field 3"
        ):
        "Helper function creates entity data with supplied entity_id"
        v = entitydata_create_values(entity_id, type_id=type_id, update=update)
        v = entitydata_values_add_field(v, "rdfs:comment", 2, comment2)
        v = entitydata_values_add_field(v, "rdfs:comment_alt", 3, comment3)
        e = EntityData.create(self.testdata, entity_id, v)
        return e    

    def _check_entity_data_values(self, 
        entity_id, type_id="testtype", update="Entity", 
        comment2="Comment field 2",
        comment3="Comment field 3"
        ):
        "Helper function checks content of form-updated record type entry with supplied entity_id"
        # log.info("_check_entity_data_values: type_id %s, entity_id %s"%(type_id, entity_id))
        typeinfo = EntityTypeInfo(self.testcoll, type_id)
        self.assertTrue(typeinfo.entityclass.exists(typeinfo.entityparent, entity_id))
        e = typeinfo.entityclass.load(typeinfo.entityparent, entity_id)
        self.assertEqual(e.get_id(), entity_id)
        v = entitydata_values(entity_id, type_id=type_id, update=update)
        v = entitydata_values_add_field(v, "rdfs:comment", 2, comment2)
        v = entitydata_values_add_field(v, "rdfs:comment_alt", 3, comment3)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    def test_view_dup_field_values(self):
        self._check_record_view_values("DupField_view", self.viewdata)
        return

    def test_dup_field_display(self):
        # Create entity with duplicate fields
        self._create_entity_data("entitydupfield")
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Entity", 
            comment2="Comment field 2",
            comment3="Comment field 3"
            )
        # Display entity in view with duplicate fields
        u = entitydata_edit_url(
            "edit", "testcoll", "testtype", 
            entity_id="entitydupfield",
            view_id="DupField_view"
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check display context
        expect_context = dupfield_view_context_data(
            coll_id="testcoll", type_id="testtype", 
            entity_id="entitydupfield", orig_id=None,
            type_ref="testtype", type_choices=self.type_ids,
            entity_label="Entity testcoll/testtype/entitydupfield",
            entity_descr="Entity coll testcoll, type testtype, entity entitydupfield",
            entity_descr2="Comment field 2",
            entity_descr3="Comment field 3",
            record_type="/testsite/c/testcoll/d/_type/testtype/",
            action="edit", 
            update="Entity",
            continuation_url=""
            )
        self.assertEqual(len(r.context['fields']), 5)
        self.assertDictionaryMatch(context_bind_fields(r.context), expect_context)

    def test_dup_field_update(self):
        # Create entity with duplicate fields
        self._create_entity_data("entitydupfield")
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Entity", 
            comment2="Comment field 2",
            comment3="Comment field 3"
            )
        # Post form data to update entity
        u = entitydata_edit_url(
                "edit", "testcoll", "testtype", 
                entity_id="entitydupfield",
                view_id="DupField_view"
                )
        f = default_view_form_data(
                entity_id="entitydupfield",
                type_id="testtype",
                coll_id="testcoll", 
                action="edit", update="Updated Entity"
                )
        f = entitydata_form_add_field(f, "Entity_comment", 2, "Update comment 2")
        f = entitydata_form_add_field(f, "Entity_comment", 3, "Update comment 3")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        # Test resulting entity value
        self._check_entity_data_values(
            "entitydupfield", type_id="testtype", update="Updated Entity", 
            comment2="Update comment 2",
            comment3="Update comment 3"
            )
        return

# End.
