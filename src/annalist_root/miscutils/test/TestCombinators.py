# $Id: TestCombinators.py 1047 2009-01-15 14:48:58Z graham $
#
# Unit testing for WebBrick library combinators
# See http://pyunit.sourceforge.net/pyunit.html
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import unittest

sys.path.append("../..")
from MiscUtils.Combinators import *

class TestCombinators(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Test cases

    def testApply(self):
        # Is function application like BCPL?  (fn can be a variable)
        def ap(f,v): return f(v)
        def inc(n): return n+1
        assert ap(inc,2)==3

    def testCurry(self):
        def f(a,b,c): return a+b+c
        g = curry(f,1,2)
        assert g(3) == 6

    def testCompose(self):
        def f(a,b,c): return a+b+c
        def g(a,b):   return a*b
        h = compose(f,g,1000,200)
        assert h(3,4) == 1212, "h(3,4) is "+str(h(3,4))

# Code to run unit tests directly from command line.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestCombinators("testApply"))
    suite.addTest(TestCombinators("testCurry"))
    suite.addTest(TestCombinators("testCompose"))
    return suite

if __name__ == "__main__":
    # unittest.main()
    runner = unittest.TextTestRunner()
    runner.run(getTestSuite())
