"""
Helper functions for manipulasting and testing URIs and URI-related 
file paths, and for accessing or testing data at a URI reference.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import httplib

try:
    # Python3
    from urllib.parse       import (
        urlparse, urljoin, 
        urlsplit, urlunsplit, 
        quote, unquote,
        SplitResult
        )
    from urllib.request     import urlopen, Request, pathname2url
    from urllib.error       import HTTPError
except ImportError:
    # Python2
    from urlparse           import (
        urlparse, urljoin, 
        urlsplit, urlunsplit, 
        SplitResult
        )
    from urllib2            import urlopen, Request, HTTPError
    from urllib             import quote, unquote, pathname2url

import logging
log = logging.getLogger(__name__)

fileuribase = "file://"

def isFileUri(uri):
    return uri.startswith(fileuribase)

def resolveUri(uriref, base, path=""):
    """
    Resolve a URI reference against a supplied base URI and path (supplied as strings).
    (The path is a local file system path, and may need converting to use URI conventions)
    """
    upath = pathname2url(path)
    if os.path.isdir(path) and not upath.endswith('/'):
        upath = upath + '/'
    return urljoin(urljoin(base, upath), uriref)

def resolveFileAsUri(path):
    """
    Resolve a filename reference against the current working directory, and return the
    corresponding file:// URI.
    
    If the supplied string is already a URI, it is returned unchanged
    (for idempotency and non-file URIs)
    """
    if urlsplit(path).scheme == "":
        path = resolveUri("", fileuribase, os.path.abspath(path))
    return path

def getFilenameFromUri(uri):
    """
    Convert a file:// URI into a local file system reference
    """
    uriparts = urlsplit(uri)
    assert uriparts.scheme == "file", "RO %s is not in local file system"%uri
    uriparts = SplitResult("","",uriparts.path,uriparts.query,uriparts.fragment)
    return url2pathname(urlunsplit(uriparts))

def isLiveUri(uriref):
    """
    Test URI reference to see if it refers to an accessible resource
    
    Relative URI references are assumed to be local file system references,
    relartive to the current working directory.
    """
    islive  = False
    fileuri = resolveFileAsUri(uriref)
    if isFileUri(fileuri):
        islive = os.path.exists(getFilenameFromUri(fileuri))
    else:
        parseduri = urlsplit(uriref)
        scheme    = parseduri.scheme
        host      = parseduri.netloc
        path      = parseduri.path
        if parseduri.query: path += "?"+parseduri.query
        httpcon   = httplib.HTTPConnection(host, timeout=5)
        # Extra request headers
        # ... none for now
        # Execute request
        try:
            httpcon.request("HEAD", path)
            response = httpcon.getresponse()
            status   = response.status
        except:
            status   = 900
        # Pick out elements of response
        islive = (status >= 200) and (status <= 299)
    return islive

def retrieveUri(uriref):
    # @@TODO: revise to use httplib2, or delete this method
    uri = resolveUri(uriref, fileuribase, os.getcwd())
    request  = Request(uri)
    try:
        response = urlopen(request)
        result   = response.read()
    except:
        result = None
    return result

# End.
