"""
Annalist tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import unittest
import doctest
import os.path
import shutil

from django.test import TestCase
from django.conf import settings

import annalist.util
import annalist.views.fields.render_utils
import annalist.views.fields.render_placement

from annalist.layout import Layout

test_layout     = Layout(settings.BASE_DATA_DIR)
TestBaseDir     = test_layout.SITE_PATH
TestHost        = settings.TEST_HOST            # e.g. "test.example.com"
TestBasePath    = "/" + settings.TEST_BASE_PATH # e.g. "/testsite"
TestHostUri     = settings.TEST_HOST_URI        # e.g. "http://test.example.com"
TestBaseUri     = settings.TEST_BASE_URI        # e.g. "http://test.example.com/testsite"

sitedata_target_reset = "all"

def resetSitedata(scope="all"):
    """
    Set flag to reset site and/or collection data at next test initialization
    """
    global sitedata_target_reset
    if sitedata_target_reset != "all":
        if scope != "collections":
            scope="all"
        sitedata_target_reset = scope
    return

def copySitedata(src, sitedatasrc, tgt):
    """
    Creates a set of Annalist site data by making a copy of a specified
    source tree.

    src         source directory containing site collection test data to be copied
    sitedatasrc source directory containing standard site data to be copied
    tgt         target directory in which the site data is created
    """
    # Confirm existence of target directory
    log.debug("copySitedata: src %s"%(src))
    log.debug("copySitedata: tgt %s"%(tgt))
    assert os.path.exists(src), "Check source directory (%s)"%(src)
    assert os.path.exists(sitedatasrc), "Check site data source directory (%s)"%(sitedatasrc)
    assert tgt.startswith(TestBaseDir)
    # annalist.util.replacetree(src, tgt)
    # Site data is not updated by the tests, so initialize it just once for each test suite run
    sitedatatgt = os.path.join(tgt, test_layout.SITEDATA_DIR)
    global sitedata_target_reset
    if sitedata_target_reset == "all":
        annalist.util.replacetree(src, tgt)
        for sdir in ("users", "types", "lists", "views", "groups", "fields", "enums"):
            s = os.path.join(sitedatasrc, sdir)
            d = os.path.join(sitedatatgt, sdir)
            shutil.copytree(s, d)
    elif sitedata_target_reset == "collections":
        ds = os.path.join(src, "c")
        dt = os.path.join(tgt, "c")
        annalist.util.replacetree(ds, dt)
    sitedata_target_reset = "none"
    # Confirm existence of target directories
    assert os.path.exists(tgt), "checking target directory created (%s)"%(tgt)
    assert os.path.exists(sitedatatgt), "checking target sitedata directory created (%s)"%(sitedatatgt)
    return tgt

def init_annalist_test_site():
    log.debug("init_annalist_test_site")
    copySitedata(
        settings.SITE_SRC_ROOT+"/sampledata/init/"+test_layout.SITE_DIR, 
        settings.SITE_SRC_ROOT+"/annalist/sitedata",
        TestBaseDir)
    return

def load_tests(loader, tests, ignore):
    log.debug("load_tests")
    #init_annalist_test_site()
    # See http://stackoverflow.com/questions/2380527/django-doctests-in-views-py
    if os.name == "posix":
        # The doctest stuff doesn't seem to work on Windows
        # (These add a total of 12 tests to the overall test)
        tests.addTests(doctest.DocTestSuite(annalist.util))
        tests.addTests(doctest.DocTestSuite(annalist.views.uri_builder))
        tests.addTests(doctest.DocTestSuite(annalist.views.form_utils.fieldchoice))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.render_utils))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.bound_field))
        tests.addTests(doctest.DocTestSuite(annalist.views.fields.render_placement))
        tests.addTests(doctest.DocTestSuite(annalist.models.entityfinder))
        # tests.addTests(doctest.DocTestSuite(annalist.tests.entity_testutils))
    else:
        log.warning("Skipping doctests for non-posix system")
    return tests

# Test helper functions

def unicode_to_str(u):
    return str(u) if isinstance(u, unicode) else u

def tuple_to_str(t):
    return tuple((unicode_to_str(v) for v in t))

def dict_to_str(d):
    return dict(map(tuple_to_str, d.items()))

# End.
