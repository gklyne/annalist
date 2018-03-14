"""
Tests for collection data viewing and editing.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import re
import json
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings
from django.db                              import models
from django.http                            import QueryDict
from django.core.urlresolvers               import resolve, reverse
from django.contrib.auth.models             import User
from django.test                            import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client                     import Client
from django.template                        import Template, Context

from utils.SuppressLoggingContext           import SuppressLogging

import annalist
from annalist                               import layout
from annalist.identifiers                   import RDF, RDFS, ANNAL
from annalist.util                          import valid_id

from annalist.models.site                   import Site
from annalist.models.sitedata               import SiteData
from annalist.models.collection             import Collection
from annalist.models.annalistuser           import AnnalistUser

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url, collection_view_url, collection_edit_url, 
    collection_entity_view_url,
    collection_create_values,
    create_user_permissions,
    create_test_user,
    context_view_field
    )
from entity_testentitydata  import (
    entity_url, entitydata_edit_url, entitydata_list_type_url,
    default_fields, default_label, default_comment, error_label,
    layout_classes
    )
from entity_testcolldata    import (
    collectiondata_url, collectiondata_resource_url,
    collectiondata_view_url, collectiondata_view_resource_url,
    collectiondata_value_keys, collectiondata_load_keys,
    collectiondata_create_values, collectiondata_values, collectiondata_read_values,
    coll_view_form_data
    )
from entity_testuserdata    import (
    user_view_form_data
    )


#   -----------------------------------------------------------------------------
#
#   Test collection data access and editing interfaces
#
#   -----------------------------------------------------------------------------

class CollectionDataEditViewTest(AnnalistTestCase):
    """
    Tests for collection data edit view
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # Login and permissions
        create_test_user(
            self.testsite.site_data_collection(),
            # self.testcoll, 
            "testuser", "testpassword",
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        resetSitedata(scope="all")
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _check_collection_data_values(self, coll_id=None, coll_label=None, coll_descr=None):
        """
        Helper function checks content of annalist collection data
        """
        self.assertTrue(Collection.exists(self.testsite, coll_id))
        c = Collection.load(self.testsite, coll_id)
        self.assertEqual(c.get_id(), coll_id)
        self.assertEqual(c.get_view_url_path(), collection_view_url(coll_id="testcoll"))
        v = collectiondata_values(
            coll_id=coll_id, coll_label=coll_label, coll_descr=coll_descr
            )
        self.assertDictionaryMatch(c.get_values(), v)
        return c

    def _check_annalist_user_perms(self, user_id, user_perms):
        self.assertTrue(AnnalistUser.exists(self.testcoll, user_id))
        u = AnnalistUser.load(self.testcoll, user_id)
        self.assertEqual(u.get_id(), user_id)
        self.assertEqual(u[ANNAL.CURIE.user_permission], user_perms)
        return

    #   -----------------------------------------------------------------------------
    #   Form rendering and access tests
    #   -----------------------------------------------------------------------------

    def test_get_collection_data_form_rendering(self):
        u = entitydata_edit_url("new", layout.SITEDATA_ID, layout.COLL_TYPEID, view_id="Collection_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        field_vals = default_fields(
            coll_id=layout.SITEDATA_ID, 
            type_id=layout.COLL_TYPEID, 
            entity_id="00000001", 
            sotware_ver=annalist.__version_data__,
            tooltip1a=context_view_field(r.context, 0, 0)['field_tooltip'],
            tooltip1b=context_view_field(r.context, 0, 1)['field_tooltip'],
            tooltip2 =context_view_field(r.context, 1, 0)['field_tooltip'],
            tooltip3 =context_view_field(r.context, 2, 0)['field_tooltip'],
            tooltip4 =context_view_field(r.context, 3, 0)['field_tooltip'],
            tooltip5a=context_view_field(r.context, 4, 0)['field_tooltip'],
            tooltip5b=context_view_field(r.context, 4, 1)['field_tooltip'],
            tooltip6a=context_view_field(r.context, 5, 0)['field_tooltip'],
            tooltip6b=context_view_field(r.context, 5, 1)['field_tooltip'],
            tooltip7 =context_view_field(r.context, 6, 0)['field_tooltip'],
            )
        formrow1a = """
            <div class="small-12 medium-6 columns" title="%(tooltip1a)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Id</span>
                    </div>
                    <div class="%(input_classes)s">
                        <input type="text" size="64" name="entity_id" 
                                   placeholder="(entity id)" 
                                   value="00000001" />
                    </div>
                </div>
            </div>
            """%field_vals(width=6)
        formrow1b = """
            <div class="small-12 medium-6 columns" title="%(tooltip1b)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>S/W version</span>
                    </div>
                    <div class="%(input_classes)s">
                        <span>&nbsp;</span>
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
                               value="" />
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
                        </textarea>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow4 = """
            <div class="small-12 columns" title="%(tooltip4)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Parent</span>
                    </div>
                    <div class="%(input_classes)s">
                        <select name="Coll_parent">
                            <option value="" selected="selected">(site)</option>
                            <option value="_coll/_annalist_site">Annalist data notebook test site</option>
                            <option value="_coll/coll1">Collection coll1</option>
                            <option value="_coll/coll2">Collection coll2</option>
                            <option value="_coll/coll3">Collection coll3</option>
                            <option value="_coll/testcoll">Collection testcoll</option>
                        </select>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        formrow5a = """
             <div class="small-12 medium-6 columns" title="%(tooltip5a)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Default list</span>
                    </div>
                    <div class="%(input_classes)s">
                        <span>&nbsp;</span>
                    </div>
                </div>
            </div>
           """%field_vals(width=6)
        formrow5b = """
            <div class="small-12 medium-6 columns" title="%(tooltip5b)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Default view</span>
                    </div>
                    <div class="%(input_classes)s">
                        <span>&nbsp;</span>
                    </div>
                </div>
            </div>
            """%field_vals(width=6)            
        formrow6a = """
             <div class="small-12 medium-6 columns" title="%(tooltip6a)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Default view type</span>
                    </div>
                    <div class="%(input_classes)s">
                        <span>&nbsp;</span>
                    </div>
                </div>
            </div>
           """%field_vals(width=6)
        formrow6b = """
            <div class="small-12 medium-6 columns" title="%(tooltip6b)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Default view entity</span>
                    </div>
                    <div class="%(input_classes)s">
                        <span>&nbsp;</span>
                    </div>
                </div>
            </div>
            """%field_vals(width=6)            
        formrow7 = """
            <div class="small-12 columns" title="%(tooltip7)s">
                <div class="row view-value-row">
                    <div class="%(label_classes)s">
                        <span>Collection metadata</span>
                    </div>
                    <div class="%(input_classes)s">
                        <textarea cols="64" rows="6" name="Coll_comment" 
                                  class="small-rows-4 medium-rows-8" 
                                  placeholder="(annal:meta_comment)"
                                  >
                        </textarea>
                    </div>
                </div>
            </div>
            """%field_vals(width=12)
        # log.info(r.content)
        self.assertContains(r, formrow1a, html=True)
        self.assertContains(r, formrow1b, html=True)
        self.assertContains(r, formrow2,  html=True)
        self.assertContains(r, formrow3,  html=True)
        self.assertContains(r, formrow4,  html=True)
        self.assertContains(r, formrow5a, html=True)
        self.assertContains(r, formrow5b, html=True)
        self.assertContains(r, formrow6a, html=True)
        self.assertContains(r, formrow6b, html=True)
        # self.assertContains(r, formrow_viewdata, html=True)
        return

    # Collection data view
    def test_get_collection_data_view(self):
        collection_url = collection_view_url(coll_id="testcoll")
        u = collectiondata_url(coll_id="testcoll")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        "testcoll")
        self.assertEqual(r.context['orig_id'],          "testcoll")
        self.assertEqual(r.context['action'],           "view")
        self.assertEqual(r.context['continuation_url'], "")
        self.assertEqual(
            r.context['entity_data_ref'],      
            collection_url+layout.COLL_META_REF
            )
        self.assertEqual(
            r.context['entity_data_ref_json'], 
            collection_url+layout.COLL_META_REF+"?type=application/json"
            )
        return

    # Collection data content negotiation
    def test_get_collection_data_json(self):
        """
        Request collection data as JSON-LD
        """
        collection_url = collection_view_url(coll_id="testcoll")
        u = collectiondata_url(coll_id="testcoll")
        r = self.client.get(u, HTTP_ACCEPT="application/ld+json")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        v = r['Location']
        self.assertEqual(v, TestHostUri+collection_url+layout.COLL_META_REF)
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    # Collection data view metadata access
    def test_get_collection_data_view_metadata(self):
        u = collectiondata_resource_url(coll_id="testcoll")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        colldata = json.loads(r.content)
        expected = (
            { "@id":                    "../"
            , "@type":                  [ "annal:Collection" ]
            , "@context":               [ {"@base": layout.META_COLL_BASE_REF}, "coll_context.jsonld" ]
            , "annal:id":               "testcoll"
            , "annal:type_id":          layout.COLL_TYPEID
            , "annal:type":             "annal:Collection"
            , "rdfs:label":             "Collection testcoll"
            , "rdfs:comment":           "Description of Collection testcoll"
            , "annal:software_version": annalist.__version_data__
            })
        self.assertEqual(colldata, expected)
        return

    # collection named view context
    def test_get_named_view(self):
        u = collectiondata_view_url(coll_id="testcoll", action="view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        "testcoll")
        self.assertEqual(r.context['orig_id'],          "testcoll")
        self.assertEqual(r.context['action'],           "view")
        self.assertEqual(r.context['continuation_url'], "")
        return

    # collection named view edit
    def test_get_named_edit(self):
        u = collectiondata_view_url(coll_id="testcoll", action="edit")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        "testcoll")
        self.assertEqual(r.context['orig_id'],          "testcoll")
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_url'], "")
        return

    # collection named view edit post update
    def test_post_named_edit(self):
        u = collectiondata_view_url(coll_id="testcoll", action="edit")
        f = coll_view_form_data(coll_id="testcoll", action="edit")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestBaseUri+"/c/_annalist_site/d/_coll/")
        # Check updated collection data
        self._check_collection_data_values(coll_id="testcoll")
        return

    # collection named view metadata access
    def test_get_named_view_metadata(self):
        u = collectiondata_view_resource_url(coll_id="testcoll")
        log.debug("test_get_named_view_metadata: collectiondata_view_resource_url: %s"%(u,))
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        colldata = json.loads(r.content)
        expected = (
            { "@id":                    "../"
            , "@type":                  [ "annal:Collection" ]
            , "@context":               [ {"@base": layout.META_COLL_BASE_REF}, "coll_context.jsonld" ]
            , "annal:id":               "testcoll"
            , "annal:type_id":          layout.COLL_TYPEID
            , "annal:type":             "annal:Collection"
            , "rdfs:label":             "Collection testcoll"
            , "rdfs:comment":           "Description of Collection testcoll"
            , "annal:software_version": annalist.__version_data__
            })
        self.assertEqual(colldata, expected)
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    def test_edit_collection_metadata(self):
        # This test performs a GET to retrieve values used in a form,
        # then a POST to save updated collection metadata.
        # This test is intended to test a problem encountered with updated 
        # entity copying logic that needs to take special account of collection
        # entities being presented as offspring of the site while being stored
        # as part of a collection.
        #
        coll_id = "testcoll"
        self.assertTrue(Collection.exists(self.testsite, coll_id))
        c = Collection.load(self.testsite, coll_id)
        self.assertEqual(c.get_id(), coll_id)
        self.assertEqual(c.get_view_url_path(), collection_view_url(coll_id="testcoll"))
        # GET collection metadata form data, and test values
        u = collectiondata_url(coll_id="testcoll")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        "testcoll")
        self.assertEqual(r.context['orig_id'],          "testcoll")
        self.assertEqual(r.context['orig_coll'],        layout.SITEDATA_ID)
        self.assertEqual(r.context['action'],           "view")
        self.assertEqual(r.context['continuation_url'], "")
        orig_coll = r.context['orig_coll']
        # Assemble and POST form data to =updated collection metadata
        new_label = "Updated collection metadata"
        f = coll_view_form_data(
            coll_id="testcoll", 
            action="edit", 
            coll_label=new_label,
            # orig_coll="None"
            orig_coll=layout.SITEDATA_ID
            )
        u = collectiondata_view_url(coll_id="testcoll", action="edit")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'],   TestBaseUri+"/c/_annalist_site/d/_coll/")
        # Check updated collection data
        self._check_collection_data_values(coll_id="testcoll", coll_label=new_label)
        return

    def test_post_copy_user(self):
        # The main purpose of this test is to check that user permissions are 
        # saved properly
        self.assertFalse(AnnalistUser.exists(self.testcoll, "copyuser"))
        f = user_view_form_data(
            action="copy", orig_id="_default_user_perms",
            user_id="copyuser",
            user_name="User copyuser",
            user_uri="mailto:copyuser@example.org",
            user_permissions="VIEW CREATE UPDATE DELETE",
            orig_coll=layout.SITEDATA_ID
            )
        u = entitydata_edit_url(
            "copy", "testcoll", "_user", entity_id="_default_user_perms", view_id="User_view"
            )
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestBaseUri+"/c/testcoll/d/_user/")
        # Check that new record type exists
        self.assertTrue(AnnalistUser.exists(self.testcoll, "copyuser"))
        self._check_annalist_user_perms("copyuser", ["VIEW", "CREATE", "UPDATE", "DELETE"])
        return

# End.
