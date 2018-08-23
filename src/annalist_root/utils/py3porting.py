"""
Definitions to support porting to Python 3

The intent is to abstract here those API calls used by Annalist that are 
sensitive to string vs unicode parameters, and changes to the Python library
structure between Python versions 2 and 3.  It also serves to identify code
features for which there isn't a natural idiom that works across versions.

To use this module, include something like this in the original source:

    from utils.py3porting import is_string, to_unicode, urljoin
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

try:
    # Python3
    from urllib.parse       import (
        urlparse, urljoin, 
        urlsplit, urlunsplit, 
        quote, unquote
        )
    from urllib.request     import urlopen, Request, pathname2url
    from urllib.error       import HTTPError
except ImportError:
    # Python2
    from urlparse           import urlparse, urljoin, urlsplit, urlunsplit
    from urllib2            import urlopen, Request, HTTPError
    from urllib             import quote, unquote, pathname2url

from six import text_type, StringIO

def is_string(val):
    """
    Is the supplied value a string or unicode string?

    See: https://stackoverflow.com/a/33699705/324122
    """
    return isinstance(val, (str, u"".__class__))

def to_unicode(val):
    """
    Converts a supplied string value to Unicode text
    """
    return text_type(val)

def encode_str(ustr):
    """
    Return string value for supplied Unicode
    """
    return ustr.encode('ascii', 'ignore')

str_space = encode_str(' ')

def isoformat_space(datetime):
    """
    Return ISO-formatted date with space to separate date and time.
    """
    return datetime.isoformat(str_space)

