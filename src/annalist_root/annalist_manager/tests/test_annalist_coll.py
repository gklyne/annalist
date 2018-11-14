"""
Test module for annalist-manager collection data management commands
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

from utils.py3porting    import StringIO
from utils.StdoutContext import SwitchStdout, SwitchStderr

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

class AnnalistManagerCollTest(test_annalist_base.AnnalistManagerTestBase):

    @classmethod
    def setUpTestData(cls):
        cls.setup_annalist_manager_test()
        cls.init_site_database()
        cls.create_site_data()
        return

    def setUp(self):
        coll_dir = self.colldir("Resource_defs")
        if os.path.isdir(coll_dir):
            removetree(coll_dir)
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_installcollection(self):
        coll_id = "Resource_defs"
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "installcollection"
                , coll_id
                , "--config=runtests"
                ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(
            stdoutlines[0], 
            "Installing collection '%s' from data directory '%s'"%
              (coll_id, self.collsrc(coll_id))
            )
        collexists = os.path.isdir(self.colldir(coll_id))
        self.assertTrue(collexists, "%s collection created?"%(coll_id))
        return

    def test_copycollection(self):
        coll_id1 = "Resource_defs"
        coll_id2 = "Resource_defs_copy"
        # Create source
        self.installcoll(coll_id1)
        collexists = os.path.isdir(self.colldir(coll_id1))
        self.assertTrue(collexists, "%s created?"%coll_id1)
        # Now copy
        coll_dir = self.colldir(coll_id2)
        if os.path.isdir(coll_dir):
            removetree(coll_id2)
        collexists = os.path.isdir(self.colldir(coll_id2))
        self.assertFalse(collexists, "%s absent?"%coll_id2)
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "copycollection"
                , coll_id1, coll_id2
                , "--config=runtests"
                ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(
            stdoutlines[0], 
            "Copying collection '%s' to '%s'"%(coll_id1, coll_id2)
            )
        collexists = os.path.isdir(self.colldir(coll_id2))
        self.assertTrue(os.path.isdir(self.colldir(coll_id1)), "%s created?"%coll_id2)
        return

    def test_migrationreport(self):
        coll_id1 = "Resource_defs"
        coll_id2 = "Resource_defs_copy"
        # Create sources
        self.installcoll(coll_id1)
        collexists = os.path.isdir(self.colldir(coll_id1))
        self.assertTrue(collexists, "%s created?"%coll_id1)
        self.copycoll(coll_id1, coll_id2)
        collexists = os.path.isdir(self.colldir(coll_id2))
        self.assertTrue(collexists, "%s created?"%coll_id2)
        # Now generate migration report
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "migrationreport"
                , coll_id1, coll_id2
                , "--config=runtests"
                ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(
            stdoutlines[0], 
            "# Migration report from collection '%s' to '%s' #"%(coll_id1, coll_id2)
            )
        return

    def test_migratecollection(self):
        coll_id = "Resource_defs"
        # Create source
        self.installcoll(coll_id)
        collexists = os.path.isdir(self.colldir(coll_id))
        self.assertTrue(collexists, "%s created?"%coll_id)
        # Now migrate
        stdoutbuf  = StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "migratecollection"
                , coll_id
                , "--config=runtests"
                ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(
            stdoutlines[0], 
            "Apply data migrations in collection '%s'"%(coll_id,)
            )
        return

    def test_migrateallcollections(self):
        coll_id1 = "Resource_defs"
        coll_id2 = "Resource_defs_copy"
        coll_id3 = "Concept_defs"
        coll_id4 = "Journal_defs"
        # Create sources
        self.installcoll(coll_id1)
        collexists = os.path.isdir(self.colldir(coll_id1))
        self.assertTrue(collexists, "%s created?"%coll_id1)
        self.copycoll(coll_id1, coll_id2)
        collexists = os.path.isdir(self.colldir(coll_id2))
        self.assertTrue(collexists, "%s created?"%coll_id2)
        self.installcoll(coll_id3)
        collexists = os.path.isdir(self.colldir(coll_id3))
        self.assertTrue(collexists, "%s created?"%coll_id3)
        self.installcoll(coll_id4)
        collexists = os.path.isdir(self.colldir(coll_id4))
        self.assertTrue(collexists, "%s created?"%coll_id4)
        # Now migrate
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "migrateallcollections"
                    , "--config=runtests"
                    ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        expectlines = (
            [ "---- Processing '%s'"%(cid) 
              for cid in (coll_id1, coll_id2, coll_id3, coll_id4)
            ])
        expectlines.append("")
        self.assertEqual(
            stdoutlines[0], 
            "Apply data migrations in all collections:"
            )
        self.assertIn(stdoutlines[1], expectlines)
        self.assertIn(stdoutlines[2], expectlines)
        self.assertIn(stdoutlines[3], expectlines)
        self.assertIn(stdoutlines[4], expectlines)
        self.assertEqual(
            stdoutlines[5], 
            "Data migrations complete."
            )
        return

# End.
