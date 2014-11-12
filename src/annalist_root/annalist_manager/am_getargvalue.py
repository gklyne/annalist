"""
am_getargvalue.py - read command value if not already defined
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2013-2014, Graham Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import getpass

# raw_input and getpass:
#   http://packetforger.wordpress.com/2014/03/26/using-pythons-getpass-module/
#   https://docs.python.org/2/library/getpass.html

def getarg(args, index):
    """
    Helper to retrieve value from command line args
    """
    return args[index] if index < len(args) else None

def getargvalue(val, prompt):
    """
    Prompt and read value if not defined
    """
    if not val:
        if sys.stdin.isatty():
            val = raw_input(prompt)
        else:
            val = sys.stdin.readline()
            if val[-1] == '\n': val = val[:-1]
    return val

def getsecret(prompt):
    """
    Prompt and read secret value without echo
    """
    return getpass.getpass(prompt)

# End.