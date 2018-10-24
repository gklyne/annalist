"""
Test base module for annalist-manager test suites
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

from utils.py3porting       import StringIO
from utils.StdoutContext    import SwitchStdout, SwitchStderr

import annalist
from annalist.util                      import replacetree, removetree
from annalist.tests.AnnalistTestCase    import AnnalistTestCase

from annalist_manager.tests             import get_source_root
from annalist_manager.am_main           import runCommand

#   -----------------------------------------------------------------------------
#
#   Tests
#
#   -----------------------------------------------------------------------------

class AnnalistManagerTestBase(AnnalistTestCase):

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    @classmethod
    def setup_annalist_manager_test(cls):
        # See https://stackoverflow.com/questions/29653129/
        # Regenerate Analist site data and Django database, once-only for all tests
        cls.userhome    = os.path.os.path.expanduser("~")
        cls.userconfig  = os.path.os.path.expanduser("~/.annalist")
        cls.src_root    = get_source_root()
        cls.testhome    = os.path.join(cls.src_root, "sampledata/data")
        cls.sitehome    = os.path.join(cls.testhome, "annalist_test")
        cls.settingsdir = os.path.join(cls.src_root, "annalist_site/settings")
        return

    @classmethod
    def init_site_database(cls):
        if os.path.isdir(cls.sitehome):
            removetree(cls.sitehome)
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(cls.userhome, cls.userconfig, 
                    ["annalist-manager", "init", "--config=runtests"]
                    )
        return

    @classmethod
    def create_site_data(cls):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(cls.userhome, cls.userconfig, 
                ["annalist-manager", "createsitedata", "--config=runtests"]
                )
        return

    def collsrc(self, coll_id):
        return self.src_root + "/annalist/data/%s"%(coll_id,)

    def colldir(self, coll_id):
        return os.path.join(self.sitehome, "c/%s"%(coll_id,))

    def installcoll(self, coll_id):
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "installcollection"
                , coll_id
                , "--config=runtests"
                ])
        return

    def copycoll(self, coll_id1, coll_id2):
        coll_dir = self.colldir(coll_id2)
        if os.path.isdir(coll_dir):
            return # Copy already exists
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "copycollection"
                , coll_id1, coll_id2
                , "--config=runtests"
                ])
        return

# End.
