"""
Annalist tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import unittest
import doctest
import os.path

from django.conf import settings

import utils

from annalist.layout import Layout

import annalist.util

import annalist.views.fields.find_renderers
import annalist.views.fields.render_placement

test_layout     = Layout(settings.BASE_DATA_DIR)    # e.g. ".../sampledata/data/"
TestBaseDir     = test_layout.SITE_PATH             # e.g. ".../sampledata/data/annalist_site"
TestHost        = settings.TEST_HOST                # e.g. "test.example.com"
TestBasePath    = "/" + settings.TEST_BASE_PATH     # e.g. "/testsite"
TestHostUri     = settings.TEST_HOST_URI            # e.g. "http://test.example.com"
TestBaseUri     = settings.TEST_BASE_URI            # e.g. "http://test.example.com/testsite"

def load_tests(loader, tests, ignore):
    log.debug("load_tests")
    #init_annalist_test_site()
    # See http://stackoverflow.com/questions/2380527/django-doctests-in-views-py
    if os.name == "posix":
        # The doctest stuff doesn't seem to work on Windows
        # (These add a total of 12 tests to the overall test)
        tests.addTests(doctest.DocTestSuite(utils.uri_builder))
        tests.addTests(doctest.DocTestSuite(annalist.util))
        tests.addTests(doctest.DocTestSuite(annalist.identifiers))
        tests.addTests(doctest.DocTestSuite(annalist.views.uri_builder))
        tests.addTests(doctest.DocTestSuite(annalist.views.displayinfo))
        tests.addTests(doctest.DocTestSuite(annalist.views.form_utils.fieldchoice))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.find_renderers))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.bound_field))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.render_placement))
        tests.addTests(doctest.DocTestSuite(annalist.models.entityfinder))
        # For some reason, this won't load in the full test suite
        # tests.addTests(doctest.DocTestSuite(annalist.tests.entity_testutils))
    else:
        log.warning("Skipping doctests for non-posix system")
    return tests

# End.
