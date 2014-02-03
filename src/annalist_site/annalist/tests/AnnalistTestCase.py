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


# End.
