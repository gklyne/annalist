"""
Test module for annalist-manager user management
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
import json

from utils.py3porting           import StringIO
from utils.StdoutContext        import SwitchStdout, SwitchStderr, SwitchStdin

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

class AnnalistManagerUserTest(test_annalist_base.AnnalistManagerTestBase):

    @classmethod
    def setUpTestData(cls):
        cls.setup_annalist_manager_test()
        cls.init_site_database()
        cls.create_site_data()
        return

    def setUp(self):
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def createuser(self, username):
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO("password\npassword\n")
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO("password\npassword\n")
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO("password\npassword\n")
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
            with SwitchStdout(stdoutbuf):
                stdinbuf = StringIO("password\npassword\n")
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
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
        stderrbuf  = StringIO()
        with SwitchStderr(stderrbuf):
            stdoutbuf  = StringIO()
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
