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
import annalist.fields.render_utils
from annalist.layout        import Layout

test_layout     = Layout(settings.BASE_DATA_DIR)
TestBaseDir     = test_layout.SITE_PATH
TestHost        = settings.TEST_HOST        # e.g. "test.example.com"
TestBasePath    = settings.TEST_BASE_PATH   # e.g. "testsite"
TestHostUri     = settings.TEST_HOST_URI    # e.g. "http://test.example.com"
TestBaseUri     = settings.TEST_BASE_URI    # e.g. "http://test.example.com/testsite"

def createSiteData(src, tgt):
    """
    Creates a set of Annalist site data by making a copy of a specified
    source tree.

    src     source directory containing site data to be copied
    tgt     target directory in which the site data is created
    """
    # Confirm existence of target directory
    log.debug("createSiteData: src %s"%(src))
    log.debug("createSiteData: tgt %s"%(tgt))
    assert os.path.exists(src), "Check source directory (%s)"%(src)
    assert tgt.startswith(TestBaseDir)
    shutil.rmtree(tgt, ignore_errors=True)
    shutil.copytree(src, tgt)
    # Confirm existence of target directory
    assert os.path.exists(tgt), "checking target directory created (%s)"%(tgt)
    return tgt

def init_annalist_test_site():
    log.debug("init_annalist_test_site")
    createSiteData(settings.SITE_SRC_ROOT+"/test/init/"+test_layout.SITE_DIR, TestBaseDir)
    return

def load_tests(loader, tests, ignore):
    log.debug("load_tests")
    #init_annalist_test_site()
    # See http://stackoverflow.com/questions/2380527/django-doctests-in-views-py
    tests.addTests(doctest.DocTestSuite(annalist.util))
    tests.addTests(doctest.DocTestSuite(annalist.fields.render_utils))
    return tests

# Test helper functions

def unicode_to_str(u):
    return str(u) if isinstance(u, unicode) else u

def tuple_to_str(t):
    return tuple((unicode_to_str(v) for v in t))

def dict_to_str(d):
    return dict(map(tuple_to_str, d.items()))

# End.
