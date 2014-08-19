"""
Various utilities for Annalist common functions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
import os
import os.path
import errno
import urlparse
import json

from django.conf import settings

from annalist.identifiers import ANNAL

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
    if id and re.match(r"\w+$", id):
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

def ensure_dir(dirname):
    """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
    try:
        os.makedirs(dirname)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    return

def entity_dir_path(base_dir, path, filename):
    """
    Assemble full entity description directory and file names from supplied components.

    base_dir    is the fully qualified base directory for the site or collection
                from which data is to be read
    path        is a relative path or list of path segments within the site or 
                resource for the site or collection from which data is to be read.
                This value may be absent.
    filename    is a file name for the data resource to be read.

    Returns a pair containing the full directory and path names for the entity file.

    >>> entity_dir_path("/base/dir/","sub","file.ext")
    ('/base/dir/sub', '/base/dir/sub/file.ext')
    >>> entity_dir_path("/base/dir/",["sub"],"file.ext")
    ('/base/dir/sub', '/base/dir/sub/file.ext')
    >>> entity_dir_path("/base/dir/",[],"file.ext")
    ('/base/dir', '/base/dir/file.ext')
    >>> entity_dir_path("/base/dir/",["sub1","sub2"],"file.ext")
    ('/base/dir/sub1/sub2', '/base/dir/sub1/sub2/file.ext')
    >>> entity_dir_path("/base/dir",["sub"],"file.ext")
    ('/base/dir/sub', '/base/dir/sub/file.ext')
    >>> entity_dir_path("/base/dir",[],"sub/file.ext")
    ('/base/dir/sub', '/base/dir/sub/file.ext')
    """
    log.debug("entity_dir_path %s, %r, %s"%(base_dir, path, filename))
    if path:
        if isinstance(path, (list, tuple)):
            d = os.path.join(base_dir, *path)
        else:
            d = os.path.join(base_dir, path)
    else:
        d = base_dir
    p = os.path.join(d, filename)
    d = os.path.dirname(p)
    return (d, p)

def entity_path(base_dir, path, filename):
    """
    Assemble full entity description file names from supplied components.

    base_dir    is the fully qualified base directory for the site or collection
                from which data is to be read
    path        is a relative path or list of path segments within the site or 
                resource for the site or collection from which data is to be read.
                This value may be absent.
    filename    is a file name for the data resource to be read.

    Returns the full path name for the entity file if the intermediate directories 
    all exist, otherwise None if any directories are missing.  No test is made for 
    existence of the filename.

    >>> entity_path('.',[],"file.ext")
    './file.ext'
    >>> entity_path('.',["nopath"],"file.ext") is None
    True
    """
    (d, p) = entity_dir_path(base_dir, path, filename)
    # log.debug("entity_path: d %s, p %s"%(d,p))
    if d and os.path.isdir(d):
        return p
    return None

def entity_url_host(baseuri, entityref):
    """
    Return host part (as appears in an HTTP host: header) from an entity URI.

    >>> entity_url_host("http://example.org/basepath/", "/path/to/entity")
    'example.org'
    >>> entity_url_host("http://example.org:80/basepath/", "/path/to/entity")
    'example.org:80'
    >>> entity_url_host("http://userinfo@example.org:80/basepath/", "/path/to/entity")
    'example.org:80'
    >>> entity_url_host("http://base.example.org:80/basepath/", "http://ref.example.org/path/to/entity")
    'ref.example.org'
    """
    uri = urlparse.urljoin(baseuri, entityref)
    p   = urlparse.urlparse(uri)
    h   = p.hostname or ""
    if p.port:
        h += ":" + str(p.port)
    return h

    """
    Return absolute path part from an entity URI, excluding query or fragment.

    >>> entity_url_host("http://example.org/basepath/", "/path/to/entity")
    '/path/to/entity'
    >>> entity_url_host("http://example.org/basepath/", "relpath/to/entity")
    '/basepath/relpath/to/entity'
    >>> entity_url_host("http://example.org/basepath/", "/path/to/entity?query")
    '/path/to/entity'
    >>> entity_url_host("http://example.org/basepath/", "/path/to/entity#frag")
    '/path/to/entity'
    >>> entity_url_host("/basepath/", "relpath/to/entity")
    '/basepath/relpath/to/entity'
    """
def entity_url_path(baseuri, entityref):
    uri = urlparse.urljoin(baseuri, entityref)
    return urlparse.urlparse(uri).path

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
