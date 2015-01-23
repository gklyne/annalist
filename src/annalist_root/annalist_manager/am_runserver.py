"""
Run Annalist server.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess
import importlib
import shutil

log = logging.getLogger(__name__)

from utils.SetcwdContext            import ChangeCurrentDir
from utils.SuppressLoggingContext   import SuppressLogging
from annalist                       import __version__

import am_errors
from am_settings                    import am_get_settings

def am_runserver(annroot, userhome, options):
    """
    Run Annalist server.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    with ChangeCurrentDir(annroot):
        cmd = "runserver 0.0.0.0:8000"
        subprocess_command = "django-admin %s --pythonpath=%s --settings=%s"%(cmd, annroot, settings.modulename)
        log.debug("am_initialize subprocess: %s"%subprocess_command)
        status = subprocess.call(subprocess_command.split())
        log.debug("am_initialize subprocess status: %s"%status)
    return status

def am_serverlog(annroot, userhome, options):
    """
    Print name of Annalist server log to standard output.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    logfilename = sitesettings.LOGGING_FILE
    print(logfilename)
    # with open(logfilename, "r") as logfile:
    #     shutil.copyfileobj(logfile, sys.stdout)
    return status

def am_sitedirectory(annroot, userhome, options):
    """
    Print name of Annalist site directory to standard output

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitedirectory = sitesettings.BASE_SITE_DIR
    print(sitedirectory)
    # with open(sitedirectory, "r") as logfile:
    #     shutil.copyfileobj(logfile, sys.stdout)
    return status

def am_version(annroot, userhome, options):
    """
    Print softwarte version string to standard output.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    print(sitesettings.ANNALIST_VERSION)
    # with open(logfilename, "r") as logfile:
    #     shutil.copyfileobj(logfile, sys.stdout)
    return status

# End.
