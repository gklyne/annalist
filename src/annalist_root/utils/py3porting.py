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

import six
from six import text_type, StringIO, BytesIO, iteritems, iterlists
from six.moves import input

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

def text_to_str(ustr):
    """
    Return string value for supplied Unicode
    """
    return str(ustr)

def bytes_to_str(bstr):
    """
    Return string value for supplied bytes
    """
    # return bstr.encode('ascii', 'ignore')
    if six.PY3:
        return bstr.decode('ascii', 'ignore')
    return bstr

def text_to_bytes(ustr):
    """
    Return bytes value for supplied string.
    The intent is that the string may be an ASCII or unicode string, but not
    something that has already been encoded.
    """
    return ustr.encode('utf-8', 'ignore')

def bytes_to_unicode(bstr):
    """
    Return Unicode value for supplied (UTF-8 encoding) bytes.
    """
    return bstr.decode('utf-8')

str_space = text_to_str(' ')

def write_bytes(file, text):
    """
    Write supplied string to file as bytes
    """
    file.write(text_to_bytes(text))
    return

def isoformat_space(datetime):
    """
    Return ISO-formatted date with space to separate date and time.
    """
    return datetime.isoformat(str_space)

def get_message_type(msg_info):
    """
    Return content type of result returned by urlopen.

    The message info value returned by Python2's urllib2.urlopen has long been
    deprecated.  The newer methods return info() as an `email.message.Message`
    value, whose corresponding content-type method is `get_content_type`.
    """
    try:
        # Python3
        return msg_info.get_content_type()
    except AttributeError:
        # Python2
        return msg_info.gettype()

# End.
