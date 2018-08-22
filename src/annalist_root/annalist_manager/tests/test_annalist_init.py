from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Test module for annalist-manager initialization commands
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

class AnnalistManagerInitTest(AnnalistTestCase):

    def setUp(self):
        self.userhome    = os.path.os.path.expanduser("~")
        self.userconfig  = os.path.os.path.expanduser("~/.annalist")
        self.src_root    = get_source_root()
        self.testhome    = os.path.join(self.src_root, "sampledata/data")
        self.sitehome    = os.path.join(self.testhome, "annalist_site")
        self.settingsdir = os.path.join(self.src_root, "annalist_site/settings")
        removetree(self.sitehome)
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_initialize(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
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

# End.
