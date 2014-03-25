# TestHttpSession.py
#
# Test test runner utiltities
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import logging
import unittest

sys.path.append("../..")

from miscutils import TestUtils
from miscutils import HttpSession


# Test class
class TestHttpSession(unittest.TestCase):

    def setUp(self):
        self._session = HttpSession.HTTP_Session("http://www.example.com")
        return

    def tearDown(self):
        self._session.close()
        return

    # Test cases

    def testSimpleGet(self):
        (status, reason, respheaders, respbody) = self._session.doRequest("/test")
        self.assertEquals(status, 404)
        self.assertEquals(respheaders['content-type'],   "text/html")
        self.assertEquals(respheaders['content-length'], "1270")
        self.assertEquals(int(respheaders['content-length']), len(respbody))
        return

    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "No pending test"

# Assemble test suite

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit": 
            [ "testUnits"
            , "testSimpleGet"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestHttpSession, testdict, select=select)

# Run unit tests directly from command line
if __name__ == "__main__":
    TestUtils.runTests("TestHttpSession", getTestSuite, sys.argv)

# End.
