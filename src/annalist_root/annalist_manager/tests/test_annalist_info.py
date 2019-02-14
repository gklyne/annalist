"""
Test module for annalist-manager information commands
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

from annalist_manager.tests     import get_source_root
from annalist_manager.tests     import test_annalist_base
from annalist_manager.am_main   import runCommand

#   -----------------------------------------------------------------------------
#
#   Tests
#
#   -----------------------------------------------------------------------------

class AnnalistManagerInfoTest(test_annalist_base.AnnalistManagerTestBase):

    @classmethod
    def setUpTestData(cls):
        cls.setup_annalist_manager_test()
        return

    def setUp(self):
        # self.userhome    = os.path.os.path.expanduser("~")
        # self.userconfig  = os.path.os.path.expanduser("~/.annalist")
        # self.src_root    = get_source_root()
        # self.testhome    = os.path.join(self.src_root, "sampledata/data")
        # self.settingsdir = os.path.join(self.src_root, "annalist_site/settings")
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_Version(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "version"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], annalist.__version__)
        return

    def test_Help(self):
        stdoutbuf  = StringIO()
        with SwitchStderr(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "help"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[1], "Commands:")
        self.assertEqual(stdoutlines[3], "  annalist-manager help [command]")
        self.assertEqual(stdoutlines[4], "  annalist-manager runtests [testlabel]")
        self.assertEqual(stdoutlines[5], "  annalist-manager initialize [ CONFIG ]")
        stdoutbuf.seek(0)
        with SwitchStderr(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "help", "init"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[1], "  annalist-manager initialize [ CONFIG ]")
        self.assertEqual(stdoutlines[3], "Initializes the installed software for an indicated configuration.")
        self.assertEqual(stdoutlines[4], "Mainly, this involves creating the internal database used to manage users, etc.")
        self.assertEqual(stdoutlines[6], "Annalist can be run in a number of configurations, notably")
        self.assertEqual(stdoutlines[7], "'development', 'personal' and 'shared'.")
        return

    def test_SiteDirectory(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "sitedirectory"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.userhome+"/annalist_site")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "sitedirectory", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.sitehome)
        return

    def test_SettingsModule(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsmodule"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], "annalist_site.settings.personal")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsmodule", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], "annalist_site.settings.runtests")
        return

    def test_SettingsDirectory(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsdirectory"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.settingsdir)
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsdirectory", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.settingsdir)
        return

    def test_SettingsFile(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsfile"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.settingsdir+"/personal")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "settingsfile", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.settingsdir+"/runtests")
        return

    def test_ServerLog(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "serverlog"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.userhome+"/annalist_site/annalist.log")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "serverlog", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.src_root+"/annalist.log")
        return

    def test_AccessLog(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "accesslog"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.userhome+"/annalist_site/annalist-wsgi-access.log")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "accesslog", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.src_root+"/annalist-wsgi-access.log")
        return

    def test_ErrorLog(self):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "errorlog"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.userhome+"/annalist_site/annalist-wsgi-error.log")
        stdoutbuf.seek(0)
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                ["annalist-manager", "errorlog", "--config=runtests"]
                )
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(stdoutlines[0], self.src_root+"/annalist-wsgi-error.log")
        return

# End.
