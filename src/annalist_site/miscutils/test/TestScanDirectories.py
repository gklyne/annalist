# $Id: TestScanDirectories.py 1058 2009-01-26 10:39:19Z graham $
#
# Unit testing for ScanDirectory functions
# See http://pyunit.sourceforge.net/pyunit.html
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import unittest
import re
import logging
from os.path import normpath, abspath

sys.path.append("../..")
from MiscUtils.ScanDirectories import CollectDirectoryContents
from MiscUtils.Functions import compareLists
from MiscUtils import TestUtils

class TestScanDirectories (unittest.TestCase):

    def setUp(self):
        self.srcPath = abspath("./resources/")
        self.basePath = abspath(".") #+"/"
        return

    def tearDown(self):
        return

    # Actual tests follow

    def testCollectDirsShallow(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath, recursive=False)
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir2"
                   , "resources/TestScanFilesSubDir"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectDirsRecursive(self):
        dirs     = CollectDirectoryContents(self.srcPath,self.basePath)
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir1/SubDir1a"
                   , "resources/TestScanDir1/SubDir1b"
                   , "resources/TestScanDir2"
                   , "resources/TestScanDir2/SubDir2"
                   , "resources/TestScanFilesSubDir"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectDirsRecursiveBaseEndswithSep(self):
        dirs     = CollectDirectoryContents(self.srcPath,self.basePath+"/")
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir1/SubDir1a"
                   , "resources/TestScanDir1/SubDir1b"
                   , "resources/TestScanDir2"
                   , "resources/TestScanDir2/SubDir2"
                   , "resources/TestScanFilesSubDir"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectDirsRecursiveEmptyBase(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir="")
        expected = [ self.basePath+"/resources/TestScanDir1"
                   , self.basePath+"/resources/TestScanDir1/SubDir1a"
                   , self.basePath+"/resources/TestScanDir1/SubDir1b"
                   , self.basePath+"/resources/TestScanDir2"
                   , self.basePath+"/resources/TestScanDir2/SubDir2"
                   , self.basePath+"/resources/TestScanFilesSubDir"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectFilesShallow(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath, 
                        listDirs=False, listFiles=True, recursive=False)
        expected = [ "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectFilesRecursive(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath,
                        listDirs=False, listFiles=True, recursive=True)
        expected = [ "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectFilesRecursiveBaseEndswithSep(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath+"/",
                        listDirs=False, listFiles=True, recursive=True)
        expected = [ "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectFilesRecursiveEmptyBase(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir="",
                        listDirs=False, listFiles=True, recursive=True)
        expected = [ self.basePath+"/resources/TestDomHelpers.xml"
                   , self.basePath+"/resources/TestScanFiles1.txt"
                   , self.basePath+"/resources/TestScanFiles2.txt"
                   , self.basePath+"/resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , self.basePath+"/resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectAllShallow(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath, 
                        listDirs=True, listFiles=True, recursive=False)
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir2"
                   , "resources/TestScanFilesSubDir"
                   , "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectAllRecursive(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath,
                        listDirs=True, listFiles=True, recursive=True)
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir1/SubDir1a"
                   , "resources/TestScanDir1/SubDir1b"
                   , "resources/TestScanDir2"
                   , "resources/TestScanDir2/SubDir2"
                   , "resources/TestScanFilesSubDir"
                   , "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectAllRecursiveBaseEndswithSep(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir=self.basePath+"/",
                        listDirs=True, listFiles=True, recursive=True)
        expected = [ "resources/TestScanDir1"
                   , "resources/TestScanDir1/SubDir1a"
                   , "resources/TestScanDir1/SubDir1b"
                   , "resources/TestScanDir2"
                   , "resources/TestScanDir2/SubDir2"
                   , "resources/TestScanFilesSubDir"
                   , "resources/TestDomHelpers.xml"
                   , "resources/TestScanFiles1.txt"
                   , "resources/TestScanFiles2.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , "resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    def testCollectAllRecursiveEmptyBase(self):
        dirs     = CollectDirectoryContents(self.srcPath, baseDir="",
                        listDirs=True, listFiles=True, recursive=True)
        expected = [ self.basePath+"/resources/TestScanDir1"
                   , self.basePath+"/resources/TestScanDir1/SubDir1a"
                   , self.basePath+"/resources/TestScanDir1/SubDir1b"
                   , self.basePath+"/resources/TestScanDir2"
                   , self.basePath+"/resources/TestScanDir2/SubDir2"
                   , self.basePath+"/resources/TestScanFilesSubDir"
                   , self.basePath+"/resources/TestDomHelpers.xml"
                   , self.basePath+"/resources/TestScanFiles1.txt"
                   , self.basePath+"/resources/TestScanFiles2.txt"
                   , self.basePath+"/resources/TestScanFilesSubDir/TestScanFiles31.txt"
                   , self.basePath+"/resources/TestScanFilesSubDir/TestScanFiles32.txt"
                   ]
        c = compareLists(dirs, expected)
        assert c == None, "Wrong directory list: "+repr(c)

    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

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
            , "testCollectDirsShallow"
            , "testCollectDirsRecursive"
            , "testCollectDirsRecursiveBaseEndswithSep"
            , "testCollectDirsRecursiveEmptyBase"
            , "testCollectFilesShallow"
            , "testCollectFilesRecursive"
            , "testCollectFilesRecursiveBaseEndswithSep"
            , "testCollectFilesRecursiveEmptyBase"
            , "testCollectAllShallow"
            , "testCollectAllRecursive"
            , "testCollectAllRecursiveBaseEndswithSep"
            , "testCollectAllRecursiveEmptyBase"
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
    return TestUtils.getTestSuite(TestScanDirectories, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestScanDirectories.log", getTestSuite, sys.argv)
    #logging.basicConfig(level=logging.DEBUG)
    #runner = unittest.TextTestRunner()
    #runner.run(getTestSuite())
    