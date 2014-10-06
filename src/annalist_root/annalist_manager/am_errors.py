"""
am_errors.py - status codes returns by annalist_manager
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2013-2014, Graham Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

class Annalist_Manager_Error(Exception):
    """
    annalist-manager error
    """
    def __init__(self, errno=None, value=None, msg="Annalist manager error"):
        self._msg   = msg
        self._errno = errno
        self._value = value
        return

    def __str__(self):
        txt = self._msg
        if self._value: txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "Annalist_Manager_Error(%s, %s, value=%s)"%
                 (repr(self._msg), repr(self._value)))


# Status return codes

AM_SUCCESS         = 0      # Success
AM_BADCMD          = 2      # Command error
AM_EXISTS          = 5      # directory already exists
AM_NOTEXISTS       = 6      # Directory does not exist
AM_NOSETTINGS      = 7      # No configuration settings found (e.g. personal, shared, devel, etc.)
AM_UNEXPECTEDARGS  = 8      # Unexpected arguments supplied
AM_NOUSERPASS      = 9      # No username or password for createuser or creaeadminuser
AM_MISSINGEMAIL    = 10     # No email address for createuser or creaeadminuser
AM_UNKNOWNCMD      = 11     # Unknown command name for help
AM_USEREXISTS      = 12     # Username for creation already exists
AM_USERNOTEXISTS   = 13     # Username for deletion does not exist

# End.