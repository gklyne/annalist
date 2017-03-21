"""
Tests for EntityData list view with additional inherited bibliography data
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
# from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from utils.SuppressLoggingContext   import SuppressLogging

from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.uri_builder             import uri_params, uri_with_params, continuation_params_url
from annalist.views.entitylist              import EntityGenericListView
from annalist.views.form_utils.fieldchoice  import FieldChoice

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import (
    init_annalist_test_site,
    init_annalist_test_coll,
    install_annalist_named_coll,
    create_test_coll_inheriting,
    init_annalist_named_test_coll,
    resetSitedata
    )
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url,
    collection_view_url, collection_edit_url,
    continuation_url_param,
    confirm_delete_params,
    collection_create_values,
    site_title,
    create_test_user, create_user_permissions,
    context_view_field,
    context_list_entities,
    context_list_head_fields, context_list_item_fields,
    context_list_item_field, context_list_item_field_value,
    check_context_field, check_context_field_value, check_context_list_field_value,
    check_field_list_context_fields,
    )
from entity_testtypedata    import (
    recordtype_dir, 
    recordtype_url,
    recordtype_create_values, 
    )
from entity_testentitydata  import (
    recorddata_dir,  entitydata_dir,
    entity_url, entitydata_edit_url, entitydata_delete_confirm_url,
    entitydata_list_type_url, entitydata_list_all_url,
    entitydata_value_keys, entitydata_create_values, entitydata_values, 
    entitydata_context_data, entitydata_form_data, entitydata_delete_confirm_form_data,
    entitylist_form_data
    )
from entity_testsitedata    import (
    make_field_choices, no_selection,
    get_site_bib_types, get_site_bib_types_sorted, get_site_bib_types_linked,
    get_site_bib_lists, get_site_bib_lists_sorted, get_site_bib_lists_linked,
    get_site_schema_types, get_site_schema_types_sorted, get_site_schema_types_linked,
    get_site_schema_lists, get_site_schema_lists_sorted, get_site_schema_lists_linked,
    )
from entity_testlistdata    import recordlist_url

#   -----------------------------------------------------------------------------
#
#   EntityDefaultListView tests
#
#   -----------------------------------------------------------------------------

class EntityInheritListViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        self.testsite  = init_annalist_test_site()
        self.testcoll  = init_annalist_named_test_coll(layout.BIBDATA_ID)
        self.testdata  = RecordTypeData.load(self.testcoll, "testtype")
        self.testtype2 = RecordType.create(
            self.testcoll, "testtype2", recordtype_create_values("testcoll", "testtype2")
            )
        self.testdata2 = RecordTypeData.create(self.testcoll, "testtype2", {})
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        e1 = self._create_entity_data("entity1")
        e2 = self._create_entity_data("entity2")
        e3 = self._create_entity_data("entity3")
        e4 = EntityData.create(self.testdata2, "entity4", 
            entitydata_create_values("entity4", type_id="testtype2")
            )
        self.list_ids = get_site_bib_lists_linked("testcoll")
        return

    def tearDown(self):
        resetSitedata()
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

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    #@@ ee also: text_upload_file.py


# End.
