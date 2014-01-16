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

from django.test import TestCase

import annalist.util

# Create your tests here.

# def suite():
#     log.info("tests")
#     suite = unittest.TestSuite()
#     suite.addTest(doctest.DocTestSuite(annalist.util))
#     return suite

# See http://stackoverflow.com/questions/2380527/django-doctests-in-views-py

def init_annalist_tests():
    log.info("init_annalist_tests")
    # @@TODO: make copy of test site data and update settings module?
    return

def load_tests(loader, tests, ignore):
    init_annalist_tests()
    tests.addTests(doctest.DocTestSuite(annalist.util))
    return tests

# End.
