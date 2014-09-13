"""
Initialize Annalist server data.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import logging
import subprocess

log = logging.getLogger(__name__)

from annalist_manager               import am_errors
from annalist_manager.am_errors     import Annalist_Manager_Error

from utils.SetcwdContext            import ChangeCurrentDir

class AnnalistSettings(object):
    """
    Access Annalist settings indicated by command line options.

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the current user.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """

    def __init__(self, annroot, userhome, options):
        """
        Initialise AnnalistSettings object
        """
        self.configname = options.configuration
        self.filename   = os.path.join(annroot, "annalist_site/settings", "%s.py"%(self.configname))
        self.modulename = "annalist_site.settings.%s"%(self.configname)
        log.debug("annalist_root %s"%annroot)
        log.debug("settings module filename %s"%self.filename)
        if not os.path.isfile(self.filename):
            raise Annalist_Manager_Error(
                errno=am_errors.AM_NOSETTINGS, value=self.configname, 
                msg="Annalist settings not found"
                )
        return

def am_get_settings(annroot, userhome, options):
    """
    Access Annalist settings indicated by command line options.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the current user.
    options     contains options parsed from the command line.

    returns     an AnnalistSettings object if settings are successfully located,
                othetrwise None.
    """
    try:
        am_settings = AnnalistSettings(annroot, userhome, options)
    except Annalist_Manager_Error:
        return None
    return am_settings

# End.
