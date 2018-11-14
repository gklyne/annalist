"""
am_getargvalue.py - read command value if not already defined
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2013-2014, Graham Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import getpass
from utils.py3porting import input

# raw_input and getpass:
#   http://packetforger.wordpress.com/2014/03/26/using-pythons-getpass-module/
#   https://docs.python.org/2/library/getpass.html
# Also, for Python 2/3:
#   http://python-future.org/compatible_idioms.html#raw-input

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
            val = input(prompt)
        else:
            val = sys.stdin.readline()
            if val[-1] == '\n': val = val[:-1]
    return val

def getsecret(prompt):
    """
    Prompt and read secret value without echo, or read from stdin.
    """
    if sys.stdin.isatty():
        val = getpass.getpass(prompt)
    else:
        val = sys.stdin.readline()
        if val[-1] == '\n': val = val[:-1]
    return val

# End.