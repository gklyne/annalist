# Support functions for running different test suites
#
# Test suites are selected using a command line argument:
#
# Test classes are:
#   "unit"          These are stand-alone tests that all complete within a few 
#                   seceonds and do not depend on resources external to the 
#                   package being tested, (other than other libraries used).
#   "component"     These are tests that take loonger to run, or depend on 
#                   external resources, (files, etc.) but do not depend on 
#                   external services.
#   "integration"   These are tests that exercise interactions with seperate
#                   services.
#   "pending"       These are tests that have been designed and created, but 
#                   for which the corresponding implementation has not been
#                   completed.
#   "all"           return suite of unit, component and integration tests
#   name            a single named test to be run.
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import unittest
import logging

junitxml_present = False
try:
    import junitxml
    junitxml_present = True
except ImportError:
    pass

def getTestSuite(testclass, testdict, select="unit"):
    """
    Assemble test suite from supplied class, dictionary and selector
    
    testclass   is the test class whose methods are test cases
    testdict    is a dictionary of test cases in named test suite, 
                keyed by "unit", "component", etc., or by a named test.
    select      is the test suite selector:
                "unit"      return suite of unit tests only
                "component" return suite of component tests
                "integrate" return suite of integration tests
                "pending"   return suite of pending tests
                "all"       return suite of unit and component tests
                name        a single named test to be run
    """
    suite = unittest.TestSuite()
    # Named test only
    if select[0:3] not in ["uni","com","all","int","pen"]:
        if not hasattr(testclass, select):
            print "%s: no test named '%s'"%(testclass.__name__, select)
            return None
        suite.addTest(testclass(select))
        return suite
    # Select test classes to include
    if select[0:3] == "uni":
        testclasses = ["unit"]
    elif select[0:3] == "com":
        testclasses = ["component"]
    elif select[0:3] == "int":
        testclasses = ["integration"]
    elif select[0:3] == "pen":
        testclasses = ["pending"]
    elif select[0:3] == "all":
        testclasses = ["unit", "component"]
    else:
        testclasses = ["unit"]
    for c in testclasses:
        for t in testdict.get(c,[]):
            if not hasattr(testclass, t):
                print "%s: in '%s' tests, no test named '%s'"%(testclass.__name__, c, t)
                return None
            suite.addTest(testclass(t))
    return suite

def runTests(logname, getSuite, args):
    """
    Run unit tests based on supplied command line argument values
    
    logname     name for logging output file, if used
    getSuite    function to retrieve test suite, given selector value
    args        command line arguments (or equivalent values)
    """
    sel = "unit"
    vrb = 1
    if len(args) > 1:
        sel = args[1]
    if sel == "xml":
        # Run with XML test output for use in Jenkins environment
        if not junitxml_present:
            print "junitxml module not available for XML test output"
            raise ValueError, "junitxml module not available for XML test output"
        with open('xmlresults.xml', 'w') as report:
            result = junitxml.JUnitXmlResult(report)
            result.startTestRun()
            try:
                getSuite(select="unit").run(result)
            finally:
                result.stopTestRun()
    else:
        if sel[0:3] in ["uni","com","all","int","pen"]:
            logging.basicConfig(level=logging.WARNING)
            if sel[0:3] in ["com","all"]: vrb = 2
        else:
            # Run single test with elevated logging to file via new handler
            logging.basicConfig(level=logging.DEBUG)
            # Enable debug logging to a file
            fileloghandler = logging.FileHandler(logname,"w")
            fileloghandler.setLevel(logging.DEBUG)
            # Use this formatter for shorter log records
            ###filelogformatter = logging.Formatter('%(levelname)s %(message)s', "%H:%M:%S")
            # Use this formatter to display timing information:
            filelogformatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', "%H:%M:%S")
            fileloghandler.setFormatter(filelogformatter)
            logging.getLogger('').addHandler(fileloghandler)
            vrb = 2
        runner = unittest.TextTestRunner(verbosity=vrb)
        tests  = getSuite(select=sel)
        if tests: runner.run(tests)
    return

# End.
