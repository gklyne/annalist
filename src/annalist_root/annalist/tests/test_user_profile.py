from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Tests for user profile page (also tests user identity access)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.db                  import models
from django.http                import QueryDict
from django.core.urlresolvers   import resolve, reverse
from django.contrib.auth.models import User
from django.test                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client         import Client

from annalist                   import layout
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist.models.site       import Site
from annalist.views.profile     import ProfileView

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, 
    init_annalist_test_coll,
    resetSitedata
    )
from .entity_testutils import site_title

class UserProfileTest(AnnalistTestCase):
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
        super(UserProfileTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(UserProfileTest, cls).tearDownClass()
        # @@checkme@@ resetSitedata(scope="all")
        return

    def test_UserProfileTest(self):
        self.assertEqual(ProfileView.__name__, "ProfileView", "Check ProfileView class name")
        return


#   -----------------------------------------------------------------------------
#
#   UserProfileView tests
#
#   -----------------------------------------------------------------------------

class UserProfileViewTest(AnnalistTestCase):
    """
    Tests for Site views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.user = User.objects.create_user(
            'testuser', 'user@test.example.com', 'testpassword',
            first_name="Test", last_name="User"
            )
        self.user.save()
        self.client     = Client(HTTP_HOST=TestHost)
        self.uri        = reverse("AnnalistProfileView")
        self.homeuri    = reverse("AnnalistHomeView")
        return

    def tearDown(self):
        return

    def test_UserProfileViewTest(self):
        self.assertEqual(ProfileView.__name__, "ProfileView", "Check ProfileView class name")
        return

    def test_get(self):
        # @@TODO: use reference to self.client, per 
        # https://docs.djangoproject.com/en/dev/topics/testing/tools/#default-test-client
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        u = reverse("AnnalistProfileView")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        row1 = """
            <div class="row view-value-row">
              <div class="view-label small-12 medium-2 columns">
                <span>User</span>
              </div>
              <div class="view-value small-12 medium-10 columns">
                <span>testuser</span>
              </div>
            </div>
            """
        row2 = """
            <div class="row view-value-row">
              <div class="view-label small-12 medium-2 columns">
                <span>Name</span>
              </div>
              <div class="view-value small-12 medium-10 columns">
                <span>Test User</span>
              </div>
            </div>
            """
        row3 = """
            <div class="row view-value-row">
              <div class="view-label small-12 medium-2 columns">
                <span>Email</span>
              </div>
              <div class="view-value small-12 medium-10 columns">
                <span><a href="mailto:user@test.example.com">user@test.example.com</a></span>
              </div>
            </div>
            """

        # log.info(r.content)
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, row1, html=True)
        self.assertContains(r, row2, html=True)
        self.assertContains(r, row3, html=True)
        return

    def test_get_no_login(self):
        u = reverse("AnnalistProfileView")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        self.assertIn("/testsite/login/", r['location'])
        self.assertIn("continuation_url=/testsite/", r['location'])
        return

# End.
