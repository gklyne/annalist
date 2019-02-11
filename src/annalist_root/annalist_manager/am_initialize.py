"""
Initialize Annalist server data.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import importlib
import subprocess

log = logging.getLogger(__name__)

from utils.SuppressLoggingContext   import SuppressLogging
from utils.py3porting               import bytes_to_str 

from annalist.util                  import ensure_dir

from .                              import am_errors
from .am_settings                   import am_get_settings

def am_initialize(annroot, userhome, userconfig, options):
    """
    Initialize Annalist server data, database, etc.

    annroot     is the root directory for the annalist software installation.
    userhome    is the home directory for the host system user issuing the initialize command.
    userconfig  is the directory used for user-specific configuration files.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings_obj = am_get_settings(annroot, userhome, options)
    if not settings_obj:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) != 0:
        print("Unexpected arguments for initialize: (%s)"%(" ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    # Get config base directory from settings, and make sure it exists
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings_obj.modulename)

    # For unknown reason, the database path in DATABASES gets zapped, 
    # so code changed to use separately saved DATABASE_PATH.
    providersdir = os.path.join(sitesettings.CONFIG_BASE, "providers")
    databasedir  = os.path.dirname(sitesettings.DATABASE_PATH)
    ensure_dir(providersdir)
    ensure_dir(databasedir)
    # Initialze the database
    status = am_errors.AM_SUCCESS
    subprocess_command = (
        "django-admin migrate --pythonpath=%s --settings=%s"%
        (annroot, settings_obj.modulename)
        )
    log.debug("am_initialize subprocess: %s"%subprocess_command)
    # status = subprocess.call(
    #     subprocess_command.split(), 
    #     #stdout=sys.stdout, stderr=sys.stderr
    #     )
    # Allow stdout and stderr to be captured for testing
    p = subprocess.Popen(
        subprocess_command.split(), 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    out, err = p.communicate(None)
    status = p.returncode
    sys.stdout.write(bytes_to_str(out))
    sys.stderr.write(bytes_to_str(err))
    log.debug("am_initialize subprocess status: %s"%status)
    return status

def am_collectstatic(annroot, userhome, userconfig, options):
    """
    Collect Annalist statis data to (e.g.) `annalist_site/static`

    annroot     is the root directory for the annalist software installation.
    userhome    is the home directory for the host system user issuing the initialize command.
    userconfig  is the directory used for user-specific configuration files.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings_obj = am_get_settings(annroot, userhome, options)
    if not settings_obj:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) != 0:
        print("Unexpected arguments for collectstatic: (%s)"%(" ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    # Get config base directory from settings, and make sure it exists
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings_obj.modulename)

    # Assemble static data
    status = am_errors.AM_SUCCESS
    subprocess_command = (
        "django-admin collectstatic --pythonpath=%s --settings=%s --clear --noinput"%
        (annroot, settings_obj.modulename)
        )
    log.debug("am_collectstatic subprocess: %s"%subprocess_command)
    # Allow stdout and stderr to be captured for testing
    p = subprocess.Popen(
        subprocess_command.split(), 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    out, err = p.communicate(None)
    status = p.returncode
    sys.stdout.write(bytes_to_str(out))
    sys.stderr.write(bytes_to_str(err))
    log.debug("am_collectstatic subprocess status: %s"%status)
    return status

# End.
