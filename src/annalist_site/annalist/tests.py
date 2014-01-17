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
from annalist.layout        import Layout

dir_layout = Layout(settings.BASE_DATA_DIR)

def createSiteData(src, tgt):
    """
    Creeates a set of Annalist site data by making a copy of a specified
    source tree.

    src     source directory containing site data to be copied
    tgt     target directory in which the site data is created
    """
    # Confirm existence of target directory
    assert os.path.exists(src), "Check source directory (%s)"%(src)
    shutil.rmtree(tgt, ignore_errors=True)
    shutil.copytree(src, tgt)
    # Confirm existence of target directory
    assert os.path.exists(tgt), "checking target directory created (%s)"%(tgt)
    return tgt

def init_annalist_tests():
    log.info("init_annalist_tests")
    createSiteData(settings.SITE_SRC_ROOT+"/test/init/"+dir_layout.SITE_DIR, dir_layout.SITE_PATH)
    return

def load_tests(loader, tests, ignore):
    init_annalist_tests()
    # See http://stackoverflow.com/questions/2380527/django-doctests-in-views-py
    tests.addTests(doctest.DocTestSuite(annalist.util))
    return tests

# End.
