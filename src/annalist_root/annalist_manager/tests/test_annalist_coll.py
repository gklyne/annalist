from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Test module for annalist-manager collection data management commands
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

class AnnalistManagerCollTest(AnnalistTestCase):

    @classmethod
    def setUpTestData(cls):
        # See https://stackoverflow.com/questions/29653129/
        # Regenerate Analist site data and Django database, once-only for all tests
        cls.userhome    = os.path.os.path.expanduser("~")
        cls.userconfig  = os.path.os.path.expanduser("~/.annalist")
        cls.src_root    = get_source_root()
        cls.testhome    = os.path.join(cls.src_root, "sampledata/data")
        cls.sitehome    = os.path.join(cls.testhome, "annalist_site")
        cls.settingsdir = os.path.join(cls.src_root, "annalist_site/settings")
        removetree(cls.sitehome)
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(cls.userhome, cls.userconfig, 
                    ["annalist-manager", "init", "--config=runtests"]
                    )
        stdoutbuf  = StringIO.StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(cls.userhome, cls.userconfig, 
                ["annalist-manager", "createsitedata", "--config=runtests"]
                )
        return

    def setUp(self):
        coll_dir = self.colldir("Resource_defs")
        if os.path.isdir(coll_dir):
            removetree(coll_dir)
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def collsrc(self, coll_id):
        return self.src_root + "/annalist/data/%s"%(coll_id,)

    def colldir(self, coll_id):
        return os.path.join(self.sitehome, "c/%s"%(coll_id,))

    def installcoll(self, coll_id):
        stdoutbuf  = StringIO.StringIO()
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
        stdoutbuf  = StringIO.StringIO()
        with SwitchStdout(stdoutbuf):
            runCommand(self.userhome, self.userconfig, 
                [ "annalist-manager", "copycollection"
                , coll_id1, coll_id2
                , "--config=runtests"
                ])
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_installcollection(self):
        coll_id = "Resource_defs"
        stdoutbuf  = StringIO.StringIO()
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
        stdoutbuf  = StringIO.StringIO()
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
        stdoutbuf  = StringIO.StringIO()
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
        stdoutbuf  = StringIO.StringIO()
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
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "migrateallcollections"
                    , "--config=runtests"
                    ])
        stdoutbuf.seek(0)
        stdoutlines = stdoutbuf.read().split("\n")
        self.assertEqual(
            stdoutlines[0], 
            "Apply data migrations in all collections:"
            )
        self.assertEqual(
            stdoutlines[1], 
            "---- Processing '%s'"%(coll_id3,)
            )
        self.assertEqual(
            stdoutlines[2], 
            "---- Processing '%s'"%(coll_id4,)
            )
        self.assertEqual(
            stdoutlines[3], 
            "---- Processing '%s'"%(coll_id1,)
            )
        self.assertEqual(
            stdoutlines[4], 
            "---- Processing '%s'"%(coll_id2,)
            )
        self.assertEqual(
            stdoutlines[5], 
            "Data migrations complete."
            )
        return



#   annalist-manager installcollection coll_id [--force] [ CONFIG ]
#   annalist-manager copycollection old_coll_id new_coll_id [ CONFIG ]
#   annalist-manager migratecollection coll_id [ CONFIG ]
#   annalist-manager migrateallcollections [ CONFIG ]
#   annalist-manager migrationreport old_coll_id new_coll_id [ CONFIG ]


# End.
