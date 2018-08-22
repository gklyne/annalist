from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Test module for annalist-manager user management
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import StringIO
import json

import logging
log = logging.getLogger(__name__)

import annalist
from annalist.util       import replacetree, removetree

from utils.StdoutContext import SwitchStdout, SwitchStderr, SwitchStdin

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

class AnnalistManagerUserTest(AnnalistTestCase):

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
        if os.path.isdir(cls.sitehome):
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
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def createuser(self, username):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO.StringIO("password\npassword\n")
                with SwitchStdin(stdinbuf):
                    runCommand(self.userhome, self.userconfig, 
                        [ "annalist-manager", "createlocal"
                        , username, username+"@example.org", "Test", username
                        , "--config=runtests"
                        ])
        return

    def userdir(self, username):
        usertypedir = os.path.join(self.sitehome, "c/_annalist_site/d/_user/")
        return os.path.join(usertypedir, username)

    def check_user_permissions(self, username, permissions):
        userfile = os.path.join(self.userdir(username), "user_meta.jsonld")
        with open(userfile) as f:
            userdata = json.load(f)
        self.assertEqual(userdata["annal:user_permissions"], permissions.split())
        return

    #   -----------------------------------------------------------------------------
    #   Tests
    #   -----------------------------------------------------------------------------

    def test_createlocaluser(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO.StringIO("password\npassword\n")
                with SwitchStdin(stdinbuf):
                    runCommand(self.userhome, self.userconfig, 
                        [ "annalist-manager", "createlocaluser"
                        , "testlocaluser", "testlocaluser@example.org", "Test", "LocalUser"
                        , "--config=runtests"
                        ])
        userexists = os.path.isdir(self.userdir("testlocaluser"))
        self.assertTrue(userexists, "testlocaluser created OK?")
        return

    def test_createadminuser(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO.StringIO("password\npassword\n")
                with SwitchStdin(stdinbuf):
                    runCommand(self.userhome, self.userconfig, 
                        [ "annalist-manager", "createadminuser"
                        , "testadminuser", "testadminuser@example.org", "Test", "LocalUser"
                        , "--config=runtests"
                        ])
        userexists = os.path.isdir(self.userdir("testadminuser"))
        self.assertTrue(userexists, "testadminuser created OK?")
        return

    def test_defaultadminuser(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO.StringIO("password\npassword\n")
                with SwitchStdin(stdinbuf):
                    runCommand(self.userhome, self.userconfig, 
                        [ "annalist-manager", "defaultadminuser"
                        , "--config=runtests"
                        ])
        userexists = os.path.isdir(self.userdir("admin"))
        self.assertTrue(userexists, "admin created OK?")
        return

    def test_updateadminuser(self):
        self.createuser("testupdateuser")
        userexists = os.path.isdir(self.userdir("testupdateuser"))
        self.assertTrue(userexists, "testupdateuser created OK?")
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "updateadminuser"
                    , "testupdateuser"
                    , "--config=runtests"
                    ])
        self.check_user_permissions("testupdateuser", "VIEW CREATE UPDATE DELETE CONFIG ADMIN")
        return

    def test_setuserpermissions(self):
        self.createuser("testupdateuser")
        userexists = os.path.isdir(self.userdir("testupdateuser"))
        self.assertTrue(userexists, "testupdateuser created OK?")
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "setuserpermissions"
                    , "testupdateuser"
                    , "CREATE_COLLECTION DELETE_COLLECTION VIEW CREATE UPDATE DELETE CONFIG"
                    , "--config=runtests"
                    ])
        self.check_user_permissions(
            "testupdateuser", 
            "CREATE_COLLECTION DELETE_COLLECTION VIEW CREATE UPDATE DELETE CONFIG"
            )
        return

    def test_setdefaultpermissions(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "setdefaultpermissions"
                    , "CREATE_COLLECTION VIEW CREATE"
                    , "--config=runtests"
                    ])
        self.check_user_permissions(
            "_default_user_perms", 
            "CREATE_COLLECTION VIEW CREATE"
            )
        return

    def test_setpublicpermissions(self):
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "setpublicpermissions"
                    , "VIEW CREATE"
                    , "--config=runtests"
                    ])
        self.check_user_permissions(
            "_unknown_user_perms", 
            "VIEW CREATE"
            )
        return

    def test_deleteuser(self):
        self.createuser("testdeleteuser")
        userexists = os.path.isdir(self.userdir("testdeleteuser"))
        self.assertTrue(userexists, "testdeleteuser created OK?")
        stderrbuf  = StringIO.StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO.StringIO()
            with SwitchStdout(stdoutbuf):
                runCommand(self.userhome, self.userconfig, 
                    [ "annalist-manager", "deleteuser"
                    , "testdeleteuser"
                    , "--config=runtests"
                    ])
        # print("stderrbuf:")
        # stderrbuf.seek(0)
        # print(stderrbuf.read())
        userexists = os.path.isdir(self.userdir("testdeleteuser"))
        self.assertFalse(userexists, "testdeleteuser deleted OK?")
        return

# End.
