from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Tests for EntityData default list view
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

from annalist                       import layout
from annalist                       import message
from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.uri_builder             import uri_params, uri_with_params, uri_quote_param
from annalist.views.form_utils.fieldchoice  import FieldChoice

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    test_layout,
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, init_annalist_test_coll, resetSitedata
    )
from .entity_testutils       import (
    make_message, make_quoted_message,
    site_dir, collection_dir, 
    collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user,
    context_view_field,
    context_list_entities,
    context_list_head_fields,
    context_list_item_fields, context_list_item_field_value
    )
from .entity_testfielddesc import (
    get_field_description, get_bound_field
    )
from .entity_testtypedata import (
    recordtype_dir, 
    recordtype_url,
    recordtype_create_values
    )
from .entity_testentitydata import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_delete_confirm_form_data,
    entitylist_form_data
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
from .entity_testlistdata import recordlist_url


#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------


class EntityDefaultListViewTest(AnnalistTestCase):
    """
    Tests for default list views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite  = Site(TestBaseUri, TestBaseDir)
        self.testcoll  = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        self.testtype  = RecordType.create(self.testcoll, "testtype", recordtype_create_values("testcoll", "testtype"))
        self.testtype2 = RecordType.create(self.testcoll, "testtype2", recordtype_create_values("testcoll", "testtype2"))
        self.testdata  = RecordTypeData.create(self.testcoll, "testtype", {})
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        e1 = self._create_entity_data("entity1")
        e2 = self._create_entity_data("entity2")
        e3 = self._create_entity_data("entity3")
        e4 = EntityData.create(self.testdata2, "entity4", 
            entitydata_create_values("entity4", type_id="testtype2")
            )
        self.type_ids = get_site_types_linked("testcoll")
        self.type_ids.append(FieldChoice("_type/testtype", 
                label="RecordType testcoll/_type/testtype",
                link=recordtype_url("testcoll", "testtype")
            ))
        self.type_ids.append(FieldChoice("_type/testtype2", 
                label="RecordType testcoll/_type/testtype2",
                link=recordtype_url("testcoll", "testtype2")
            ))
        self.list_ids = get_site_lists_linked("testcoll")
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
    def setUpClass(cls):
        super(EntityDefaultListViewTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(EntityDefaultListViewTest, cls).tearDownClass()
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

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_get_default_all_list(self):
        u = entitydata_list_all_url("testcoll") + "?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, '<h2 class="page-heading">List entities with type information</h2>', html=True)
        self.assertMatch(r.content, r'<input.type="hidden".name="continuation_url".+value="/xyzzy/"/>')
        cont = uri_params({"continuation_url": u})
        tooltip1 = "" # 'title="%s"'%r.context['fields'][0]['field_help']
        tooltip2 = "" # 'title="%s"'%r.context['fields'][1]['field_help']
        tooltip3 = "" # 'title="%s"'%r.context['fields'][2]['field_help']
        rowdata = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="testtype/entity1" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/testtype/entity1/%(cont)s">entity1</a>
                  </div>
                  <div class="view-value small-2 columns" %(tooltip2)s>
                    <a href="/testsite/c/testcoll/d/_type/testtype/%(cont)s">RecordType testcoll/_type/testtype</a>
                  </div>
                  <div class="view-value small-7 columns" %(tooltip3)s>
                    <span>Entity testcoll/testtype/entity1</span>
                  </div>
                </div>
              </div>
            </div>
            """%(
                { 'base':     TestBasePath
                , 'cont':     cont
                , 'tooltip1': tooltip1
                , 'tooltip2': tooltip2
                , 'tooltip3': tooltip3
                }
            )
        # log.info(r.content)
        self.assertContains(r, rowdata, html=True)

        # Test context
        #@@TODO: use new function to create list context for comparison,
        #        like entity view context tests, rather than pick out the fields.
        #
        # self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['title'],            "List entities with type information - Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          None)
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),    set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list_all")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Field descriptions
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 3 cols..
        self.assertEqual(len(head_fields[0].description['row_field_descs']), 3)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        f2 = context_view_field(r.context, 0, 2)
        #  1st field
        self.assertDictionaryMatch(f0, 
            get_bound_field("Entity_id", "", placement="small:0,3")
            )
        #  2nd field
        self.assertDictionaryMatch(f1, 
            get_bound_field("Entity_type", "", 
                placement="small:3,2",
                options=self.type_ids
                )
            )
        # 3rd field
        self.assertDictionaryMatch(f2, 
            get_bound_field("Entity_label", "", placement="small:5,7")
            )
        # Entities and bound fields
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 6)
        entity_fields = (
            [ {'entity_type_id': "_type",     'annal:id': "testtype",  'rdfs:label': "RecordType testcoll/_type/testtype"}
            , {'entity_type_id': "_type",     'annal:id': "testtype2", 'rdfs:label': "RecordType testcoll/_type/testtype2"}
            , {'entity_type_id': "testtype",  'annal:id': "entity1",   'rdfs:label': "Entity testcoll/testtype/entity1"}
            , {'entity_type_id': "testtype",  'annal:id': "entity2",   'rdfs:label': "Entity testcoll/testtype/entity2"}
            , {'entity_type_id': "testtype",  'annal:id': "entity3",   'rdfs:label': "Entity testcoll/testtype/entity3"}
            , {'entity_type_id': "testtype2", 'annal:id': "entity4",   'rdfs:label': "Entity testcoll/testtype2/entity4"}
            ])
        field_keys = ('annal:id', 'entity_type_id', 'rdfs:label')
        for eid in range(6):
            item_fields = context_list_item_fields(r.context, entities[eid])
            for fid in range(3):
                item_field = item_fields[fid]
                head_field = head_fields[0].description['row_field_descs'][fid]
                # log.info("Item field: %r"%(item_field,))
                # log.info("Head field: %r"%(head_field,))
                # Check that row field descriptions match corresponding heading feld descriptions
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_type',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field.description[fkey], head_field[fkey])
                # Check row field values
                fkey = field_keys[fid]
                self.assertEqual(item_field['field_value'],    entity_fields[eid][fkey])
                self.assertEqual(item_field['entity_type_id'], entity_fields[eid]['entity_type_id'])
        return

    def test_get_default_type_list(self):
        u = entitydata_list_type_url("testcoll", "testtype") + "?continuation_url=/xyzzy/"
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<title>List entities - Collection testcoll</title>")
        self.assertContains(r, '<h2 class="page-heading">List entities</h2>', html=True)
        cont = uri_params({"continuation_url": u})
        # cont = ""
        # log.info(r.content)
        tooltip1 = ""
        tooltip2 = ""
        rowdata = """
            <div class="tbody row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right" name="entity_select"
                       value="testtype/entity1" />
              </div>
              <div class="small-11 columns">
                <div class="row view-listrow">
                  <div class="view-value small-3 columns" %(tooltip1)s>
                    <a href="%(base)s/c/testcoll/d/testtype/entity1/%(cont)s">entity1</a>
                  </div>
                  <div class="view-value small-9 columns" %(tooltip2)s>
                    <span>Entity testcoll/testtype/entity1</span>
                  </div>
                </div>
              </div>
            </div>
            """%(
                { 'base':     TestBasePath
                , 'cont':     cont
                , 'tooltip1': tooltip1
                , 'tooltip2': tooltip2
                }
            )
        self.assertContains(r, rowdata, html=True)
        # Test context
        # self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['title'],            "List entities - Collection testcoll")
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "testtype")
        list_choices = r.context['list_choices']
        self.assertEqual(set(list_choices.options),     set(self.list_ids))
        self.assertEqual(list_choices['field_value'],   "Default_list")
        self.assertEqual(r.context['continuation_url'], "/xyzzy/")
        # Fields
        head_fields = context_list_head_fields(r.context)
        self.assertEqual(len(head_fields), 1)       # One row of 2 cols..
        self.assertEqual(len(head_fields[0].description['row_field_descs']), 2)
        f0 = context_view_field(r.context, 0, 0)
        f1 = context_view_field(r.context, 0, 1)
        self.assertDictionaryMatch(f0, 
            get_bound_field("Entity_id", "", placement="small:0,3")
            )
        self.assertDictionaryMatch(f1, 
            get_bound_field("Entity_label", "", placement="small:3,9")
            )
        # Entities
        entities = context_list_entities(r.context)
        self.assertEqual(len(entities), 3)
        field_val = ("entity%d", "Entity testcoll/testtype/entity%d")
        for eid in range(3):
            item_fields = context_list_item_fields(r.context, entities[eid])
            for fid in range(2):
                item_field = item_fields[fid]
                head_field = head_fields[0].description['row_field_descs'][fid]
                for fkey in (
                        'field_id', 'field_name', 'field_label', 
                        'field_property_uri', 'field_render_type',
                        'field_placement', 'field_value_type'):
                    self.assertEqual(item_field.description[fkey], head_field[fkey])
                self.assertEqual(item_field['field_value'], field_val[fid]%(eid+1))
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new --------

    def test_post_new_type_entity(self):
        f = entitylist_form_data("new")
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "testtype", view_id="Default_view")
        self.assertIn(v, r['location'])
        return

    def test_post_new_all_entity(self):
        f = entitylist_form_data("new")
        u = entitydata_list_all_url("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "Default_type", 
            view_id="Default_view"
            )
        self.assertIn(v, r['location'])
        return

    def test_post_new_type_entity_select_one(self):
        f = entitylist_form_data("new", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("new", "testcoll", "testtype", 
            view_id="Default_view"
            )
        self.assertIn(v, r['location'])
        return

    def test_post_new_type_entity_select_many(self):
        f = entitylist_form_data("new", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e1 = u
        e2 = "error_head=%s"%(uri_quote_param(message.INPUT_ERROR),)
        e3 = "error_message="
        self.assertIn(e1, r['location'])
        self.assertIn(e2, r['location'])
        self.assertIn(e3, r['location'])
        return

    #   -------- copy --------

    def test_post_copy_type_entity(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("copy", "testcoll", "testtype", "entity1")
        self.assertIn(v, r['location'])
        return

    def test_post_copy_all_entity(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_all_url("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("copy", "testcoll", "testtype", "entity1")
        self.assertIn(v, r['location'])
        return

    def test_post_copy_type_entity_select_none(self):
        f = entitylist_form_data("copy")
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e1 = u
        e2 = "error_head=%s"%(uri_quote_param(message.INPUT_ERROR),)
        e3 = "error_message=%s"%(uri_quote_param(message.NO_ENTITY_FOR_COPY),)
        self.assertIn(e1, r['location'])
        self.assertIn(e2, r['location'])
        self.assertIn(e3, r['location'])
        return

    def test_post_copy_type_entity_select_many(self):
        f = entitylist_form_data("copy", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e1 = u
        e2 = "error_head=%s"%(uri_quote_param(message.INPUT_ERROR),)
        e3 = "error_message="
        self.assertIn(e1, r['location'])
        self.assertIn(e2, r['location'])
        self.assertIn(e3, r['location'])
        return

    def test_post_copy_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("copy", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- edit --------

    def test_post_edit_type_entity(self):
        f = entitylist_form_data("edit", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "testtype", "entity1")
        self.assertIn(v, r['location'])
        return

    def test_post_edit_all_entity(self):
        f = entitylist_form_data("edit", entities=["testtype/entity1"])
        u = entitydata_list_all_url("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = entitydata_edit_url("edit", "testcoll", "testtype", "entity1")
        self.assertIn(v, r['location'])
        return

    def test_post_edit_type_entity_select_none(self):
        f = entitylist_form_data("edit")
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e1 = u
        e2 = "error_head=%s"%(uri_quote_param(message.INPUT_ERROR),)
        e3 = "error_message="
        self.assertIn(e1, r['location'])
        self.assertIn(e2, r['location'])
        self.assertIn(e3, r['location'])
        return

    def test_post_edit_type_entity_select_many(self):
        f = entitylist_form_data("edit", entities=["testtype/entity1", "testtype/entity2"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        e1 = u
        e2 = "error_head=%s"%(uri_quote_param(message.INPUT_ERROR),)
        e3 = "error_message="
        self.assertIn(e1, r['location'])
        self.assertIn(e2, r['location'])
        self.assertIn(e3, r['location'])
        return

    def test_post_edit_type_entity_no_login(self):
        self.client.logout()
        f = entitylist_form_data("edit", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        return

    #   -------- delete --------

    def test_post_delete_type_entity(self):
        f = entitylist_form_data("delete", entities=["testtype/entity1"])
        u = entitydata_list_type_url("testcoll", "testtype")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%message.CONFIRM_REQUESTED_ACTION)
        msg_text = make_message(message.REMOVE_ENTITY_DATA, 
            type_id="testtype", 
            id="entity1"
            )
        self.assertContains(r, msg_text + ": " + message.ARE_YOU_SURE)
        self.assertContains(r, message.CONFIRM_OR_CANCEL)
        self.assertContains(r,
            '<input type="hidden" name="confirmed_action" value="/testsite/c/testcoll/d/testtype/!delete_confirmed"/>',
            html=True
            )
        self.assertEqual(r.context['action_description'], msg_text)
        self.assertEqual(r.context['confirmed_action'], 
            '/testsite/c/testcoll/d/testtype/!delete_confirmed')
        self.assertEqual(r.context['action_params'], 
            confirm_delete_params(button_id="entity_delete", entity_id="entity1", type_id="testtype")
            )
        self.assertEqual(r.context['cancel_action'], 
            '/testsite/c/testcoll/d/testtype/')
        return

    def test_post_delete_all_entity(self):
        f = entitylist_form_data("delete", entities=["testtype/entity1"])
        u = entitydata_list_all_url("testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, "<h3>%s</h3>"%message.CONFIRM_REQUESTED_ACTION)
        # print "**********"
        # print r.content
        # print "**********"
        msg_text = make_message(message.REMOVE_ENTITY_DATA, 
            type_id="testtype", 
            id="entity1"
            )
        self.assertContains(r, msg_text + ": " + message.ARE_YOU_SURE)
        self.assertContains(r, message.CONFIRM_OR_CANCEL)
        self.assertContains(r, 
            '<input type="hidden" name="confirmed_action"  value="/testsite/c/testcoll/d/testtype/!delete_confirmed"/>',
            html=True
            )
        self.assertEqual(r.context['action_description'], msg_text)
        self.assertEqual(r.context['confirmed_action'], 
            '/testsite/c/testcoll/d/testtype/!delete_confirmed')
        self.assertEqual(r.context['action_params'], 
            confirm_delete_params(button_id="entity_delete", entity_id="entity1", type_id=None)
            )
        self.assertEqual(r.context['cancel_action'], 
            '/testsite/c/testcoll/d/')
        return

# End.
