from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Test module for annalist-manager site data management commands
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import StringIO

import logging
log = logging.getLogger(__name__)

import annalist
from annalist.util       import replacetree, removetree

from utils.StdoutContext import SwitchStdout, SwitchStderr

from annalist.tests.AnnalistTestCase import AnnalistTestCase

from annalist_manager.tests   import get_source_root

from annalist_manager.am_main import runCommand


#   -----------------------------------------------------------------------------
#
#   Helper functions
#
#   -----------------------------------------------------------------------------

#   -----------------------------------------------------------------------------
#
#   Tests
#
#   -----------------------------------------------------------------------------

class AnnalistManagerSiteTest(AnnalistTestCase):

    def setUp(self):
        self.userhome    = os.path.os.path.expanduser("~")
        self.userconfig  = os.path.os.path.expanduser("~/.annalist")
        self.src_root    = get_source_root()
        self.testhome    = os.path.join(self.src_root, "sampledata/data")
        self.sitehome    = os.path.join(self.testhome, "annalist_site")
        self.settingsdir = os.path.join(self.src_root, "annalist_site/settings")
        if os.path.isdir(self.sitehome):
            removetree(self.sitehome)
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_createsitedata(self):
        stdoutbuf  = StringIO.StringIO()
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
        stdoutbuf  = StringIO.StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "createsitedata", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutbuf  = StringIO.StringIO()
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
