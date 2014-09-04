# $Id: TestScanFiles.py 1058 2009-01-26 10:39:19Z graham $
#
# Unit testing for WebBrick library functions (Functions.py)
# See http://pyunit.sourceforge.net/pyunit.html
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import unittest
import re
from os.path import normpath

sys.path.append("../..")
from MiscUtils.ScanFiles import *
from MiscUtils.Functions import compareLists

class TestScanFiles(unittest.TestCase):
    def setUp(self):
        self.testpath = "resources/"
        self.testpatt = re.compile( r'^TestScanFiles.*\.txt$' )
        return

    def tearDown(self):
        return

    # Actual tests follow

    def testCollectShallow(self):
        files    = CollectFiles(self.testpath,self.testpatt,recursive=False)
        expected = [ (self.testpath,"TestScanFiles1.txt")
                   , (self.testpath,"TestScanFiles2.txt")
                   ]
        c = compareLists(files, expected)
        assert c == None, "Wrong file list: "+repr(c)

    def testCollectRecursive(self):
        files    = CollectFiles(self.testpath,self.testpatt)
        expected = [ (self.testpath,"TestScanFiles1.txt")
                   , (self.testpath,"TestScanFiles2.txt")
                   , (self.testpath+"TestScanFilesSubDir","TestScanFiles31.txt")
                   , (self.testpath+"TestScanFilesSubDir","TestScanFiles32.txt")
                   ]
        c = compareLists(files, expected)
        assert c == None, "Wrong file list: "+repr(c)

    def testJoinDirName(self):
        # normpath used here to take care of dir separator issues.
        n = joinDirName("/root/sub","name")
        assert n==normpath("/root/sub/name"), "JoinDirName failed: "+n
        n = joinDirName("/root/sub/","name")
        assert n==normpath("/root/sub/name"), "JoinDirName failed: "+n
        n = joinDirName("/root/sub/","/name")
        assert n==normpath("/name"), "JoinDirName failed: "+n

    def testReadDirNameFile(self):
        assert readDirNameFile(self.testpath,"TestScanFiles1.txt"), "Read dir,file 'TestScanFiles1.txt' failed"

    def testReadFile(self):
        assert readFile(self.testpath+"TestScanFiles1.txt"), "Read file 'TestScanFiles1.txt' failed"


# Code to run unit tests directly from command line.
# Constructing the suite manually allows control over the order of tests.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestScanFiles("testCollectShallow"))
    suite.addTest(TestScanFiles("testCollectRecursive"))
    suite.addTest(TestScanFiles("testJoinDirName"))
    suite.addTest(TestScanFiles("testReadDirNameFile"))
    suite.addTest(TestScanFiles("testReadFile"))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(getTestSuite())
    