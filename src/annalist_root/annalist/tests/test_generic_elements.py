from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Tests for generic page elements not covered by other tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.core.urlresolvers   import resolve, reverse
from django.test.client         import Client

from annalist                   import layout
from annalist.models.site       import Site
from annalist.models.collection import Collection
from annalist.views.serverlog   import ServerLogView

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site,
    init_annalist_test_coll,
    resetSitedata
    )
from .entity_testutils import (
    collection_create_values,
    create_test_user, create_user_permissions, 
    )

class ServerLogTest(AnnalistTestCase):
    """
    Tests for user profile page
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        return

    def tearDown(self):
        return

    @classmethod
    def setUpClass(cls):
        super(ServerLogTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(ServerLogTest, cls).tearDownClass()
        return

    def test_ServerLogTest(self):
        self.assertEqual(ServerLogView.__name__, "ServerLogView", "Check ServerLogView class name")
        return

#   -----------------------------------------------------------------------------
#
#   ServerLogView tests
#
#   -----------------------------------------------------------------------------

class UserServerLogViewTest(AnnalistTestCase):
    """
    Tests for ServerLog views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(
            self.testsite, "testcoll", collection_create_values("testcoll")
            )
        self.sitecoll = Collection.load(self.testsite, layout.SITEDATA_ID)
        self.client   = Client(HTTP_HOST=TestHost)
        self.uri      = reverse("AnnalistServerLogView")
        self.homeuri  = reverse("AnnalistHomeView")
        return

    def tearDown(self):
        return

    def test_get(self):
        create_test_user(
            self.sitecoll, "adminuser", "adminpassword",
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
        loggedin = self.client.login(username="adminuser", password="adminpassword")
        self.assertTrue(loggedin)
        r = self.client.get(self.uri)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        site_title = "Annalist data notebook test site"
        self.assertEqual(r.context['title'], site_title)
        self.assertIn("serverlog", r.context)
        self.assertContains(r, site_title)
        return

    def test_get_no_admin(self):
        create_test_user(
            self.testcoll, "testuser", "testpassword",
            user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
            )
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        r = self.client.get(self.uri)
        self.assertEqual(r.status_code,   403)
        self.assertEqual(r.reason_phrase, "Forbidden")
        err_head    = "403: Forbidden"
        err_message = "No ADMIN access permission for resource http://test.example.com/testsite/serverlog/"
        self.assertEqual(r.context["message"], err_message)
        self.assertContains(r, err_head,    status_code=403)
        self.assertContains(r, err_message, status_code=403)
        return

    def test_get_no_login(self):
        self.client.logout()
        r = self.client.get(self.uri)
        self.assertEqual(r.status_code,   401)
        self.assertEqual(r.reason_phrase, "Unauthorized")
        err_head    = "401: Unauthorized"
        err_message = "Resource http://test.example.com/testsite/serverlog/ requires authentication for ADMIN access"
        self.assertEqual(r.context["message"], err_message)
        self.assertContains(r, err_head,    status_code=401)
        self.assertContains(r, err_message, status_code=401)
        return

# End.
