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
    """
    log.info("entity_dir_path %s, %r, %s"%(base_dir, path, filename))
    if path:
        if isinstance(path, (list, tuple)):
            d = os.path.join(base_dir, *path)
        else:
            d = os.path.join(base_dir, path)
    else:
        d = base_dir
    return (d, os.path.join(d, filename))

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
    """
    (d, p) = entity_dir_path(base_dir, path, filename)
    if d and os.path.isdir(d):
        return p
    return None

def read_entity(filename):
    """
    Read metadata or entity record and return as dictionary, or `None` if no data
    resource is present.

    filename    a full path name to the entity description to read.  If the file 
                does not exist or has malformed content, an exception is raised.
                If the supplied filename is None then None is returned.

    returns a dictionary value with data from the named file, and possibly some 
    additional details.
    """
    log.info("read_entity %s"%(filename))
    if filename:
        with open(filename, "r") as f:
            return json.load(f)
    return None

def write_entity(filename, ref, values, entityid=None, entitytype=None):
    """
    Write a description of an entity to a named file.

    filename    name of file to receive contents
    ref         reference to entity described (may be relative)
    entityid    local identifier (slug) for the described identity
    entitytype  primary type identifier of the described entity
    values      a dictionary value that populates the entity description

    @@TODO: think about capturing provenance metadata too.
    """
    values = values.copy()
    values["@id"] = ref
    if entityid:
        values[ANNAL.CURIE.id]   = entityid
    if entitytype:
        values[ANNAL.CURIE.type] = entitytype
    # Next is partial protection against code errors
    fullpath = os.path.join(settings.SITE_SRC_ROOT, filename)
    assert fullpath.startswith(settings.SITE_SRC_ROOT), "Attempt to create entity file outside Annalist site tree"
    with open(fullpath, "wt") as entity_io:
        json.dump(values, entity_io)
    return fullpath

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
