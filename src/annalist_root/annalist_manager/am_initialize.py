"""
Initialize Annalist server data.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess

log = logging.getLogger(__name__)

import am_errors
from am_settings        import am_get_settings

def am_initialize(annroot, userhome, userconfig, options):
    """
    Initialize Annalist server data, database, etc.

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the initialize command.
    userconfig  is the directory used for user-specific configuration files.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) != 0:
        print("Unexpected arguments for initialize: (%s)"%(" ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    subprocess_command = "django-admin migrate --pythonpath=%s --settings=%s"%(annroot, settings.modulename)
    log.debug("am_initialize subprocess: %s"%subprocess_command)
    # OLD: status = os.system(subprocess_command)
    status = subprocess.call(subprocess_command.split())
    log.debug("am_initialize subprocess status: %s"%status)
    return status

# End.
