"""
Run Annalist server tests.
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

from utils.SetcwdContext    import ChangeCurrentDir

import am_errors
from am_settings            import am_get_settings

def am_runtests(annroot, options):
    """
    Run Annalist server tests.

    annroot     is the root directory for the annalist software installation.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    options.configuration = "runtests"
    testsettings = am_get_settings(annroot, "/nouser/", options)
    if not testsettings:
        print("Settings not found (%s)"%("runtests"), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    log.debug("annalist_root: %s"%(annroot))
    with ChangeCurrentDir(annroot):
        # For some reason, tests are not discovered unless run from here
        cmd = "test"
        subprocess_command = (
            "django-admin %s --pythonpath=%s --settings=%s --top-level-directory=%s"%
            (cmd, annroot, testsettings.modulename, annroot)
            )
        log.debug("am_initialize subprocess: %s"%subprocess_command)
        # OLD: status = os.system(subprocess_command)
        status = subprocess.call(subprocess_command.split())
        log.debug("am_initialize subprocess status: %s"%status)
    return status

# End.
