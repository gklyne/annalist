"""
Test module for annalist-manager initialization commands
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

class AnnalistManagerInitTest(test_annalist_base.AnnalistManagerTestBase):

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

    def test_initialize(self):
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    ["annalist-manager", "init", "--config=runtests"]
                    )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], "Operations to perform:")
        self.assertEqual(stdoutlines[1], "  Apply all migrations: admin, auth, contenttypes, sessions")
        self.assertEqual(stdoutlines[2], "Running migrations:")
        self.assertEqual(stdoutlines[3], "  Applying contenttypes.0001_initial... OK")
        self.assertEqual(stdoutlines[4], "  Applying auth.0001_initial... OK")
        self.assertEqual(stdoutlines[5], "  Applying admin.0001_initial... OK")
        self.assertEqual(stdoutlines[6], "  Applying admin.0002_logentry_remove_auto_add... OK")
        # ... etc
        siteexists = os.path.isdir(self.sitehome)
        dbexists   = os.path.isfile(os.path.join(self.sitehome, "db.sqlite3"))
        self.assertTrue(siteexists, "Annalist site directory exists?")
        self.assertTrue(dbexists,   "Annalist site Django database exists?")
        return

    def test_collectstatic(self):
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    ["annalist-manager", "collect", "--config=runtests"]
                    )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        linestart   = stdoutlines[0][:8]
        self.assertEqual(linestart, "Copying ")
        # for i in range(len(stdoutlines)):
        #     if "static files copied" in stdoutlines[i]:
        #         break
        # self.assertEqual(stdoutlines[i], "271 static files copied to '/Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_test/static'.")
        # ... etc
        siteexists   = os.path.isdir(self.sitehome)
        staticexists = os.path.isdir(os.path.join(self.sitehome, "static"))
        cssexists    = os.path.isfile(os.path.join(self.sitehome, "static/css/annalist.css"))
        self.assertTrue(siteexists,   "Annalist site directory exists?")
        self.assertTrue(staticexists, "Annalist static resources directory exists?")
        self.assertTrue(cssexists,    "Annalist CSS resource exists?")
        return

# End.
