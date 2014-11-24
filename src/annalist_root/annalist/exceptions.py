"""
Annalist errors and exceptio s module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class Annalist_Error(Exception):
    """
    General Annalist error
    """

    def __init__(self, value=None, msg="Annalist error"):
        self._msg   = msg
        self._value = value
        return

    def __str__(self):
        txt = self._msg
        if self._value: txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "Annalist_Error(%s, value=%s)"%
                 (repr(self._msg), repr(self._value)))


class EntityNotFound_Error(Annalist_Error):
    """
    Annalist entity (resource) not found error.

    Typically raised when a required file is missing.  
    The offending filename should be used for the exception value.
    """

    def __init__(self, value=None, msg="Entity not found"):
        super(EntityNotFound_Error, self).__init__(value, msg)
        return

# End.
