"""
Various utilities for Annalist common functions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
import os.path
import urlparse
import json

def valid_id(id):
    """
    Checks the supplied id is valid as an Annalist identifier.

    The main requirement is that it is valid as a URI path segment, so it can be used
    in the creation of URIs for Annalist resources.  Also, filters out reserved Annalist
    identifiers.

    >>> valid_id("abcdef_1234")
    True
    >>> valid_id("abcdef/1234")
    False
    >>> valid_id("_annalist_collection")
    False
    """
    reserved = (
        [ "_annalist_site"
        , "_annalist_collection"
        ])
    if re.match(r"\w+$", id):
        return id not in reserved
    return False

def slug_from_name(filename):
    """
    Extracts a slug (id) value from a filename

    >>> slug_from_path("bar.baz")
    'bar'
    >>> slug_from_path("bar")
    'bar'
    >>> slug_from_path(".baz")
    '.baz'
    """
    slug = os.path.splitext(filename)[0]
    return slug

def slug_from_path(path):
    """
    Extracts a slug (id) value from a file path

    >>> slug_from_path("/foo/bar.baz")
    'bar'
    >>> slug_from_path("/bar")
    'bar'
    >>> slug_from_path("bar")
    'bar'
    >>> slug_from_path("/example.org/foo/bar/.baz")
    '.baz'
    >>> slug_from_path("/foo/bar.baz")
    'bar'
    >>> slug_from_path("/example.org/foo/bar/")+"$"
    '$'
    """
    return slug_from_name(os.path.basename(path))

def slug_from_uri(uri):
    """
    Extracts a slug (id) value from a URI

    >>> slug_from_uri("http:/example.org/foo/bar")
    'bar'
    >>> slug_from_uri("/example.org/foo/bar")
    'bar'
    >>> slug_from_uri("/foo/bar")
    'bar'
    >>> slug_from_uri("/bar")
    'bar'
    >>> slug_from_uri("bar")
    'bar'
    >>> slug_from_uri("/example.org/foo/bar/")+"$"
    '$'
    >>> slug_from_uri("http:/example.org/foo/bar.baz")
    'bar'
    >>> slug_from_uri("http:/example.org/foo/bar;baz")
    'bar;baz'
    >>> slug_from_uri("http:/example.org/foo/bar?baz")
    'bar'
    >>> slug_from_uri("http:/example.org/foo/bar#baz")
    'bar'
    """
    return slug_from_path(urlparse.urlsplit(uri).path)

def read_data(base_dir, path, data_dir, data_file):
    """
    Read (meta)data record and return as dictionary, or `None` if no data
    resource is present.

    base_dir    is the fully qualified base directory for the site or collection
                from which data is to be read
    path        is a relative path or list of path segments within the site or 
                resource for the site or collection from which data is to be read.
                This value may be absent.
    data_dir    is a subdirectory from which data is to be read; also used as sentinel
                to indicate presence of the desired data: if it does not exist as a
                directory, None is returned.
    data_file   is a file name for the data resource to be read.  If the file does not 
                exist or has malformed content, an exception is raised.
    """
    log.info("read_data %s, %r, %s, %s"%(base_dir, path, data_dir, data_file))
    if path:
        if isinstance(path, (list, tuple)):
            p = os.path.join(base_dir, *path)
        else:
            p = os.path.join(base_dir, path)
    else:
        p = base_dir
    if os.path.isdir(p):
        p2 = os.path.join(p, data_dir)
        if os.path.isdir(p2):
            p3 = os.path.join(p2, data_file)
            with open(p3, "r") as f:
                return json.load(f)
    return None

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
