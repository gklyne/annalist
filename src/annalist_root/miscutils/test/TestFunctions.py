# $Id: TestFunctions.py 1049 2009-01-15 15:09:21Z graham $
#
# Unit testing for WebBrick library functions (Functions.py)
# See http://pyunit.sourceforge.net/pyunit.html
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
from string import upper

sys.path.append("../..")
from MiscUtils.Functions import *

LibName = "MiscUtils"

class TestFunctions(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    def doAssert(self, cond, msg):
        assert cond , msg

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testSuff1(self):
        assert endsWith("xxx","xxx")

    def testSuff2(self):
        assert endsWith("yyyzzz","zzz")

    def testSuff3(self):
        assert not endsWith("xxxyyy","xxx")

    def testCwd(self):
        # Check test environment current directory)
        cwd = os.getcwd() 
        assert endsWith(cwd, LibName+os.sep+"tests"), "Cwd is " + cwd

    def testConcatMap1(self):
        assert concatMap(upper,["a","B","cDe","FgH"])=="ABCDEFGH"

    def testConcatMap2(self):
        assert concatMap(upper,["a"])=="A"

    def testConcatMap3(self):
        assert concatMap(upper,[])==""

    def testFstSnd1(self):
        pair=('a','b')
        assert (fst(pair)=='a') and (snd(pair)=='b')

    def testFstSnd2(self):
        pair=(1,None)
        assert (fst(pair)==1) and (snd(pair)==None)

    def testIterAll1(self):
        seq = ('a',2,'c')
        seqall = iterAll(seq)
        assert seqall.next()=='a'
        assert seqall.next()==2
        assert seqall.next()=='c'
        assert seqall.next()==None
        assert seqall.next()==None
        assert seqall.next()==None

    def testIterAll2(self):
        seq = ('a',2,'c')
        seqall = iterAll(seq,"foo")
        assert seqall.next()=='a'
        assert seqall.next()==2
        assert seqall.next()=='c'
        assert seqall.next()=="foo"
        assert seqall.next()=="foo"
        assert seqall.next()=="foo"

    def testZipAll1(self):
        # z = tuple( [x for x in zipAll((1,2,3), (4,5))] )
        z = tuple( zipAll((1,2,3), (4,5)) )
        e = ((1,4),(2,5),(3,None))
        assert z==e, z

    def testZipAll2(self):
        z = tuple( zipAll((1,2,3), (4,5), (6,7,8,9), ()) )
        e = ((1,4,6,None), (2,5,7,None), (3,None,8,None), (None,None,9,None))
        assert z==e, z

    def testAll1(self):
        assert(all(isEq(1),[1,1,1,1]))

    def testAll2(self):
        assert(not all(isEq(1),[1,1,0,1]))

    def testAny1(self):
        assert(any(isEq(1),[1,2,3,4]))

    def testAny2(self):
        assert(not any(isEq(0),[1,2,3,4]))

    def testAllEq1(self):
        assert allEq(2,[2,2,2,2])

    def testAllEq2(self):
        assert not allEq(2,[2,2,0,2])

    def testAllEq3(self):
        assert allEq(2,[])

    def testAllNe1(self):
        assert allNe(2,[0,1,3,4])

    def testAllNe2(self):
        assert not allNe(2,[0,1,2,3,4])

    def testAllNe3(self):
        assert allNe(2,[])

    def testFilterSplit1(self):
        def isOdd(v): return isEq(1)(v&1)
        vs = [1,2,3,4,5,6,7,5,3,2,1]
        (v1,v2) = filterSplit(isOdd,vs)
        assert v1 == [1,3,5,7,5,3,1], str(v1)
        assert v2 == [2,4,6,2]

    def testFilterSplit2(self):
        vs = [1,2,3,4,5,6,7,5,3,2,1]
        (v1,v2) = filterSplit(isEq(9),vs)
        assert v1 == []
        assert v2 == [1,2,3,4,5,6,7,5,3,2,1]

    def testFilterSplit3(self):
        vs = [1,2,3,4,5,6,7,5,3,2,1]
        (v1,v2) = filterSplit(isNe(9),vs)
        assert v1 == [1,2,3,4,5,6,7,5,3,2,1]
        assert v2 == []

    def testFormatIntList1(self):
        return self.assertEqual(
            "1,2,3,4,10,15,255",
            formatIntList([1,2,3,4,10,15,255]))

    def testFormatIntList2(self):
        return self.assertEqual(
            "01:02:03:04:0A:0F:FF",
            formatIntList([1,2,3,4,10,15,255],":",formatInt("%02X")))

    def testFormatList1(self):
        txt = formatList(('a','b','c'))
        assert txt=="( 'a'\n, 'b'\n, 'c'\n)", repr(txt)

    def testFormatList2(self):
        txt = formatList(('a','b','c'),left=2)
        assert txt=="( 'a'\n  , 'b'\n  , 'c'\n  )", repr(txt)

    def testFormatList3(self):
        txt = formatList(('a','b','c'),left=2,right=40)
        assert txt=="('a', 'b', 'c')", repr(txt)

    def testFormatList4(self):
        txt = formatList(('a','b',('c','d','e')),left=2,right=20)
        assert txt=="( 'a'\n  , 'b'\n  , ('c', 'd', 'e')\n  )", repr(txt)

    def testFormatDict1(self):
        txt = formatDict({'a':'foo','b':'bar'})
        assert txt=="{ 'a': 'foo'\n, 'b': 'bar'\n}", repr(txt)

    def testFormatDict9(self):
        dic = \
            { 'style': None
            , 'elems': 
              ( { 'Control': 
                  {'Selection': {'Values': {'Wb:Off': '0', 'Wb:On': '1'}, 'ctype': 'Wb:SwitchToggle'}}
                , 'source': {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'style': None
                , 'target': {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                , 'label': None
                }
              ,
              )
            , 'label': 'loose'
            }
        exp = (
            "{ 'style': None\n"+
            ", 'elems': \n"+
            "  ( { 'Control': \n"+
            "      { 'Selection': \n"+
            "        { 'Values': {'Wb:Off': '0', 'Wb:On': '1'}\n"+
            "        , 'ctype': 'Wb:SwitchToggle'\n"+
            "        }\n"+
            "      }\n"+
            "    , 'source': \n"+
            "      {'endpoint': 'WebBrick2', 'channel': 'DO2'}\n"+
            "    , 'style': None\n"+
            "    , 'target': \n"+
            "      {'endpoint': 'WebBrick2', 'channel': 'DI1'}\n"+
            "    , 'label': None\n"+
            "    }\n"+
            "  )\n"+
            ", 'label': 'loose'\n"+
            "}" )
        txt = formatDict(dic,left=0,right=60,pos=0)
        assert txt==exp, "\n"+txt # "\n"+txt  # repr(txt)

    def testCompareLists1(self):
        assert compareLists([],[])==None

    def testCompareLists2(self):
        assert compareLists(['a'],['a'])==None

    def testCompareLists3(self):
        assert compareLists(None,[])==None

    def testCompareLists4(self):
        assert compareLists(['a','b','c'],['d','e','f'])==(['a','b','c'],['d','e','f'])

    def testCompareLists5(self):
        assert compareLists(['a','b','c'],['b','d','c','e'])==(['a'],['d','e'])

    def testCompareLists6(self):
        assert compareLists(['a','b','a'],['b','d','b','d'])==(['a','a'],['d','d'])

    def testCompareLists7(self):
        assert compareLists(['a','b','c'],None)==(['a','b','c'],[])

    def testCompareDicts1(self):
        assert compareDicts({},{})==None

    def testCompareDicts2(self):
        assert compareDicts({'foo':'bar'},{'foo':'bar'})==None

    def testCompareDicts3(self):
        difs = compareDicts({'a':'foo','b':'bar'},{'a':'foo'})
        assert difs==({'b':'bar'},{}), repr(difs)

    def testCompareDicts4(self):
        assert compareDicts({'a':'foo','b':'bar'},{'a':'foo','b':'baz'})==({'b':'bar'},{'b':'baz'})

    def testCompareDicts5(self):
        assert compareDicts({'a':'foo','b':{'c':'bar'}},{'a':'foo','b':{'c':'bar'}})==None

    def testCompareDicts6(self):
        d1 = \
            { 'elems': 
              ( { 'Control': 
                  { 'source': {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                  , 'Selection': {'Values': {'Wb:Off': '0', 'Wb:On': '1'}, 'ctype': 'Wb:SwitchToggle'}
                  , 'target': {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                  }
                }
              ,
              )
            , 'label': 'Shower light'
            }
        d2 = \
            { 'style': None
            , 'elems': 
              ( { 'Control': 
                  {'Selection': {'Values': {'Wb:Off': '0', 'Wb:On': '1'}, 'ctype': 'Wb:SwitchToggle'}}
                , 'source': {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'style': None
                , 'target': {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                , 'label': None
                }
              ,
              )
            , 'label': 'loose'
            }
        dif1 = \
            { 'elems': 
                ( { 'Control': 
                    { 'source': {'endpoint': 'WebBrick2', 'channel': 'DO2'}, 
                      'target': {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                    }
                  }
                ,
                )
            , 'label': 'Shower light'
            }
        dif2 = \
            { 'elems': 
              ( { 'source': {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'target': {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                }
              ,
              )
            , 'label': 'loose'
            }
        (dd1,dd2) = compareDicts(d1,d2)
        assert dd1==dif1, "dif1:\n"+formatDict(dd1,0,60,0)
        assert dd2==dif2, "dif2:\n"+formatDict(dd2,0,60,0)
        #assert (dd1,dd2)==(dif1,dif2),"dif1:\n"+formatDict(dd1,0,60,0)+"\ndif2:\n"+formatDict(dd2,0,60,0)

    def testCompareDicts7(self):
        d1 = \
            { 'group': 'loose'
            , 'elems':
              ( { 'Control':
                  { 'Selection':
                    { 'Values': {'Wb:Off': '0', 'Wb:On': '1'}
                    , 'ctype': 'Wb:SwitchToggle'
                    }
                  }
                , 'source':
                  {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'target':
                  {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                }
              ,
              )
            , 'label': 'Shower light'
            }
        d2 = \
            { 'style': None
            , 'group': 'loose'
            , 'elems':
              ( { 'Control':
                  { 'Selection':
                    { 'Values': {'Wb:Off': '0', 'Wb:On': '1'}
                    , 'ctype': 'Wb:SwitchToggle'
                    }
                  }
                , 'source':
                  {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'style': None
                , 'target':
                  {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                , 'label': None
                }
              ,
              )
            , 'label': 'Shower light'
            }
        dd = compareDicts(d1,d2)
        if dd != None:
            (dd1,dd2) = dd
            assert dd1==None, "dd1:\n"+formatDict(dd1,0,60,0)
            assert dd2==None, "dd2:\n"+formatDict(dd2,0,60,0)

    def testCompareDicts8(self):
        d1 = \
            { 'group': 'loose'
            , 'elems':
              [ { 'Control':
                  { 'Selection':
                    { 'Values': {'Wb:Off': '0', 'Wb:On': '1'}
                    , 'ctype': 'Wb:SwitchToggle'
                    }
                  }
                , 'source':
                  {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'target':
                  {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                }
              ]
            , 'label': 'Shower light'
            }
        d2 = \
            { 'style': None
            , 'group': 'loose'
            , 'elems':
              [ { 'Control':
                  { 'Selection':
                    { 'Values': {'Wb:Off': '0', 'Wb:On': '1'}
                    , 'ctype': 'Wb:SwitchToggle'
                    }
                  }
                , 'source':
                  {'endpoint': 'WebBrick2', 'channel': 'DO2'}
                , 'style': None
                , 'target':
                  {'endpoint': 'WebBrick2', 'channel': 'DI1'}
                , 'label': None
                }
              ]
            , 'label': 'Shower light'
            }
        dd = compareDicts(d1,d2)
        if dd != None:
            (dd1,dd2) = dd
            assert dd1==None, "dd1:\n"+formatDict(dd1,0,60,0)
            assert dd2==None, "dd2:\n"+formatDict(dd2,0,60,0)

# Code to run unit tests directly from command line.
# Constructing the suite manually allows control over the order of tests.
def getTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestFunctions("testNull"))
    suite.addTest(TestFunctions("testSuff1"))
    suite.addTest(TestFunctions("testSuff2"))
    suite.addTest(TestFunctions("testSuff3"))
    suite.addTest(TestFunctions("testCwd"))
    suite.addTest(TestFunctions("testConcatMap1"))
    suite.addTest(TestFunctions("testConcatMap2"))
    suite.addTest(TestFunctions("testConcatMap3"))
    suite.addTest(TestFunctions("testFstSnd1"))
    suite.addTest(TestFunctions("testFstSnd2"))
    suite.addTest(TestFunctions("testIterAll1"))
    suite.addTest(TestFunctions("testIterAll2"))
    suite.addTest(TestFunctions("testZipAll1"))
    suite.addTest(TestFunctions("testZipAll2"))
    suite.addTest(TestFunctions("testAll1"))
    suite.addTest(TestFunctions("testAll2"))
    suite.addTest(TestFunctions("testAny1"))
    suite.addTest(TestFunctions("testAny2"))
    suite.addTest(TestFunctions("testAllEq1"))
    suite.addTest(TestFunctions("testAllEq2"))
    suite.addTest(TestFunctions("testAllEq3"))
    suite.addTest(TestFunctions("testAllNe1"))
    suite.addTest(TestFunctions("testAllNe2"))
    suite.addTest(TestFunctions("testAllNe3"))
    suite.addTest(TestFunctions("testFilterSplit1"))
    suite.addTest(TestFunctions("testFilterSplit2"))
    suite.addTest(TestFunctions("testFilterSplit3"))
    suite.addTest(TestFunctions("testFormatIntList1"))
    suite.addTest(TestFunctions("testFormatIntList2"))
    suite.addTest(TestFunctions("testFormatList1"))
    suite.addTest(TestFunctions("testFormatList2"))
    suite.addTest(TestFunctions("testFormatList3"))
    suite.addTest(TestFunctions("testFormatList4"))
    suite.addTest(TestFunctions("testFormatDict1"))
    suite.addTest(TestFunctions("testFormatDict9"))
    suite.addTest(TestFunctions("testCompareLists1"))
    suite.addTest(TestFunctions("testCompareLists2"))
    suite.addTest(TestFunctions("testCompareLists3"))
    suite.addTest(TestFunctions("testCompareLists4"))
    suite.addTest(TestFunctions("testCompareLists5"))
    suite.addTest(TestFunctions("testCompareLists6"))
    suite.addTest(TestFunctions("testCompareLists7"))
    suite.addTest(TestFunctions("testCompareDicts1"))
    suite.addTest(TestFunctions("testCompareDicts2"))
    suite.addTest(TestFunctions("testCompareDicts3"))
    suite.addTest(TestFunctions("testCompareDicts4"))
    suite.addTest(TestFunctions("testCompareDicts5"))
    suite.addTest(TestFunctions("testCompareDicts6"))
    suite.addTest(TestFunctions("testCompareDicts7"))
    suite.addTest(TestFunctions("testCompareDicts8"))
    return suite
    # suite = unittest.makeSuite(WidgetTestCase,'test')

if __name__ == "__main__":
    # unittest.main()
    runner = unittest.TextTestRunner()
    runner.run(getTestSuite())

# End.
