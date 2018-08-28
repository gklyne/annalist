"""
Test module for annalist-manager site data management commands
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import os

from utils.py3porting           import StringIO
from utils.StdoutContext        import SwitchStdout, SwitchStderr

import annalist
from annalist.util              import replacetree, removetree

from annalist_manager.tests     import get_source_root
from annalist_manager.tests     import test_annalist_base
from annalist_manager.am_main   import runCommand

#   -----------------------------------------------------------------------------
#
#   Tests
#
#   -----------------------------------------------------------------------------

class AnnalistManagerSiteTest(test_annalist_base.AnnalistManagerTestBase):

    @classmethod
    def setUpTestData(cls):
        cls.setup_annalist_manager_test()
        return

    def setUp(self):
        if os.path.isdir(self.sitehome):
            removetree(self.sitehome)
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_createsitedata(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "createsitedata", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], "Initializing Annalist site in "+self.sitehome)
        siteexists = os.path.isdir(self.sitehome)
        collexists = os.path.isfile(os.path.join(self.sitehome, "c/_annalist_site/d/coll_meta.jsonld"))
        self.assertTrue(siteexists, "Annalist site directory exists?")
        self.assertTrue(collexists, "Annalist site collection metadata exists?")
        return

    def test_updatesitedata(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "createsitedata", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "updatesitedata", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], "Copy Annalist site data")
        siteexists = os.path.isdir(self.sitehome)
        collexists = os.path.isfile(os.path.join(self.sitehome, "c/_annalist_site/d/coll_meta.jsonld"))
        self.assertTrue(siteexists, "Annalist site directory exists?")
        self.assertTrue(collexists, "Annalist site collection metadata exists?")
        return

# End.
