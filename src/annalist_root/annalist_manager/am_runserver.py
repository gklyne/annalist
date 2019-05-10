"""
Run Annalist server.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os, os.path
import sys
import importlib
import subprocess
import signal
import time
import shutil

import logging
log = logging.getLogger(__name__)

from utils.SetcwdContext            import ChangeCurrentDir
from utils.SuppressLoggingContext   import SuppressLogging
from annalist                       import __version__

from .                              import am_errors
from .am_settings                   import (
    am_get_settings, am_get_site_settings, am_get_site
    )
from .am_getargvalue                import getarg, getargvalue

def am_runserver(annroot, userhome, options):
    """
    Run Annalist production server asynchronously; writes procdss id to stdout.

    This uses the gunicorn HTTP/WSGI server.
    Provide HTTPS access by proxying via Apache or Nginx.

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
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitedirectory = sitesettings.BASE_SITE_DIR
    pidfilename   = os.path.join(sitedirectory, "annalist.pid")
    try:
        with open(pidfilename, "r") as pidfile:
            pid = int(pidfile.readline())
            print("Server already started with pid %d"%(pid,), file=sys.stderr)
            if options.force:
                print("Stopping pid %d"%(pid,), file=sys.stderr)
                os.kill(pid, signal.SIGTERM)
            else:
                print("Use '--force' to force restart", file=sys.stderr)
                return am_errors.AM_SERVERALREADYRUN
    except IOError as e:
        # No saved process id - continue
        pass
    except OSError as e:
        # Process Id not found for kill
        print("Process pid %d not found"%(pid,), file=sys.stderr)
        pass
    status = am_errors.AM_SUCCESS
    with ChangeCurrentDir(annroot):
        gunicorn_command = (
            "gunicorn --workers=1 --threads=2 "+
            "    --bind=0.0.0.0:8000 "+
            "    --env DJANGO_SETTINGS_MODULE=%s "%(settings.modulename,)+
            "    --env ANNALIST_KEY=%s "%(sitesettings.SECRET_KEY,)+
            "    --access-logfile %s "%(sitesettings.ACCESS_LOG_PATH,)+
            "    --error-logfile  %s "%(sitesettings.ERROR_LOG_PATH,)+
            "    --timeout 300 "+
            "    annalist_site.wsgi:application"+
            "")
        log.debug("am_runserver subprocess: %s"%gunicorn_command)
        p   = subprocess.Popen(gunicorn_command.split())
        pid = p.pid
        with open(pidfilename, "w") as pidfile:
            pidfile.write(str(pid)+"\n")
        time.sleep(1.0) # Allow server to start and log initial messages
        print(str(pid), file=sys.stdout)
        log.debug("am_runserver subprocess pid: %s"%pid)
    return status

def am_stopserver(annroot, userhome, options):
    """
    Stop Annalist production server.

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
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitedirectory = sitesettings.BASE_SITE_DIR
    pidfilename   = os.path.join(sitedirectory, "annalist.pid")
    status = am_errors.AM_SUCCESS
    try:
        with open(pidfilename, "r") as pidfile:
            pid = int(pidfile.readline())
            print("Stopping pid %d"%(pid,), file=sys.stderr)
            os.kill(pid, signal.SIGTERM)
        os.remove(pidfilename)
    except IOError as e:
        # print("PID file %s not found (%s)"%(pidfilename, e), file=sys.stderr)
        print("No server running", file=sys.stderr)
        return am_errors.AM_NOSERVERPIDFILE
    except OSError as e:
        print("Process %d not found (%s)"%(pid, e), file=sys.stderr)
        return am_errors.AM_PIDNOTFOUND
    return status

def am_pidserver(annroot, userhome, options):
    """
    Display running Annalist server PID on stdout

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if PID is displayed, or a non-zero status code.
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
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitedirectory = sitesettings.BASE_SITE_DIR
    pidfilename   = os.path.join(sitedirectory, "annalist.pid")
    status = am_errors.AM_SUCCESS
    try:
        with open(pidfilename, "r") as pidfile:
            pid = int(pidfile.readline())
            print("%d"%(pid,), file=sys.stdout)
    except IOError as e:
        # print("PID file %s not found (%s)"%(pidfilename, e), file=sys.stderr)
        print("No server running", file=sys.stderr)
        return am_errors.AM_NOSERVERPIDFILE
    return status

def am_rundevserver(annroot, userhome, options):
    """
    Run Annalist developent server.

    This uses the Django developm,ent server (via manage.py).
    For production deployment, use `runserver`.

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
        log.debug("am_rundevserver subprocess: %s"%subprocess_command)
        status = subprocess.call(subprocess_command.split())
        log.debug("am_rundevserver subprocess status: %s"%status)
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
    logfilename = sitesettings.ANNALIST_LOG_PATH
    print(logfilename)
    return status

def am_accesslog(annroot, userhome, options):
    """
    Print name of WSGI access log to standard output.

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
    logfilename = sitesettings.ACCESS_LOG_PATH
    print(logfilename)
    return status

def am_errorlog(annroot, userhome, options):
    """
    Print name of WSGI access log to standard output.

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
    logfilename = sitesettings.ERROR_LOG_PATH
    print(logfilename)
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

def am_settingsmodule(annroot, userhome, options):
    """
    Print name of Annalist settings module to standard output

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
    settingsmodule = settings.modulename
    print(settingsmodule)
    return status

def am_settingsfile(annroot, userhome, options):
    """
    Print name of Annalist settings file to standard output

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
    settingsfile, ext = os.path.splitext(sitesettings.__file__)
    print(settingsfile)
    return status

def am_settingsdir(annroot, userhome, options):
    """
    Print name of Annalist settings file to standard output

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
    settingsdir, file = os.path.split(sitesettings.__file__)
    print(settingsdir)
    return status

def am_version(annroot, userhome, options):
    """
    Print software version string to standard output.

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
