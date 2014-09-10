#!/usr/bin/python

"""
Context manager for switching the current working directory
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2014, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os

class ChangeCurrentDir:
    """
    Context handler class that swiches the current working directory for some controlled code.
    """
    
    def __init__(self, usecwd):
        self._usecwd = usecwd
        self._oldcwd = None
        return
    
    def __enter__(self):
        self._oldcwd = os.getcwd()
        os.chdir(os.path.join(self._oldcwd, self._usecwd))
        return 

    def __exit__(self, exctype, excval, exctraceback):
        if self._oldcwd:
            os.chdir(self._oldcwd)
        return False

if __name__ == "__main__":
    print os.getcwd()
    oldcwd = os.getcwd()
    with ChangeCurrentDir("test"):
        print os.getcwd()
        assert os.getcwd() == oldcwd+"/test"
    print os.getcwd()
    assert os.getcwd() == oldcwd

# End.
