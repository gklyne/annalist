"""
Definitions to support porting to Python 3

The intent is to abstract here those API calls used by Annalist that are 
sensitive to string vs unicode parameters.

To use this module, include something like this in the original source:

    from utils.py3porting import is_string, to_unicode

Also, for URL handling, use:

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

"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

from builtins import str as unicode_str

def is_string(val):
    """
    Is the supplied value a string or unicode string?

    See: https://stackoverflow.com/a/33699705/324122
    """
    return isinstance(val, ("".__class__, u"".__class__))

def to_unicode(val):
    """
    Converts a supplied string value to Unicode
    """
    return unicode_str(val)

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
