# ro_uriutils.py

"""
Helper functions for manipulasting and testing URIs and URI-related file paths,
and for accessing or testing data at a URI reference.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import urllib
import urlparse
import httplib

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
    upath = urllib.pathname2url(path)
    if os.path.isdir(path) and not upath.endswith('/'):
        upath = upath + '/'
    return urlparse.urljoin(urlparse.urljoin(base, upath), uriref)

def resolveFileAsUri(path):
    """
    Resolve a filename reference against the current working directory, and return the
    corresponding file:// URI.
    
    If the supplied string is already a URI, it is returned unchanged
    (for idempotency and non-file URIs)
    """
    if urlparse.urlsplit(path).scheme == "":
        path = resolveUri("", fileuribase, os.path.abspath(path))
    return path

def getFilenameFromUri(uri):
    """
    Convert a file:// URI into a local file system reference
    """
    uriparts = urlparse.urlsplit(uri)
    assert uriparts.scheme == "file", "RO %s is not in local file system"%uri
    uriparts = urlparse.SplitResult("","",uriparts.path,uriparts.query,uriparts.fragment)
    return urllib.url2pathname(urlparse.urlunsplit(uriparts))

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
        parseduri = urlparse.urlsplit(uriref)
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
    request  = urllib2.Request(uri)
    try:
        response = urllib2.urlopen(request)
        result   = response.read()
    except:
        result = None
    return result

# End.
