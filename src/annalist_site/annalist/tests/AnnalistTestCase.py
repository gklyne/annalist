"""
Test case with additional test methods used by some Annalist tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import re

import logging
log = logging.getLogger(__name__)

from django.test import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions

class AnnalistTestCase(TestCase):
    """
    Additonal test methods for Annalist test cases
    """

    def assertMatch(self, string, pattern, msg=None):
        """
        Throw an exception if the regular expresson pattern is matched
        """
        m = re.search(pattern, string)
        if not m or not m.group(0):
            raise self.failureException(
                (msg or "'%s' does not match /%s/"%(string, pattern)))

    def assertDictionaryMatch(self, actual_dict, expect_dict, prefix=""):
        """
        Check that the expect_dictr values are all present in actual_dict.

        If a dictionary element contains a list, the listed values are assumed to
        to be dictionaries which are matched recursively. (This logic is used when 
        checking sub-contexts used to render data-defined forms.)
        """
        for k in expect_dict:
            self.assertTrue(k in actual_dict, prefix+"Expected key %s not found in actual"%(k))
            if isinstance(expect_dict[k],list):
                for i in range(len(expect_dict[k])):
                    self.assertDictionaryMatch(actual_dict[k][i], expect_dict[k][i], prefix="Index %d, "%i)
            else:
                self.assertEqual(actual_dict[k], expect_dict[k], 
                    prefix+"Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        return

# End.
