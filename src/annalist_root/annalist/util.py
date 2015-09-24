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
import traceback
import stat
import time
import urlparse
import urllib2
import json
import shutil
import StringIO

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
    >>> valid_id("")
    False
    """
    reserved = (
        [ "_annalist_site"
        , "_annalist_collection"
        ])
    # cf. urls.py:
    if id and re.match(r"\w{1,32}$", id):
        return id not in reserved
    return False

def split_type_entity_id(eid, default_type_id=None):
    """
    Returns (type_id,entyity_id) pair for supplied string "type_id/entity_id".
    The supplied `eid` may be a bare "entity_id" then the supplied default 
    type_id is used.

    >>> split_type_entity_id("type_id/entity_id")
    ('type_id', 'entity_id')
    >>> split_type_entity_id("t/e", "f")
    ('t', 'e')
    >>> split_type_entity_id("entity_id", "def_type_id")
    ('def_type_id', 'entity_id')
    >>> split_type_entity_id(None, "def_type_id")
    ('def_type_id', None)
    """
    if eid is not None:
        sub_ids = eid.split("/")
        if len(sub_ids) == 2:
            return (sub_ids[0], sub_ids[1])
        elif len(sub_ids) == 1:
            return (default_type_id, sub_ids[0])
        else:
            return (default_type_id, "")
    return (default_type_id, None)

def extract_entity_id(eid):
    """
    Accepts an entity id which may be have `type_id/entity_id` form, and returns
    the bare `entity_id` value.
    """
    type_id, entity_id = split_type_entity_id(eid)
    return entity_id

def fill_type_entity_id(eid, default_type_id=None):
    """
    Assemble a type+entity compisite identifier based on a supplied id string.
    If the string does not alreadyt include a type_id value, thne supplied default
    is used.
    """
    type_id, entity_id = split_type_entity_id(eid, default_type_id=default_type_id)
    return make_type_entity_id(type_id, entity_id)

def make_type_entity_id(type_id=None, entity_id=None):
    """
    Assemble a type_id and entity_id and return a composite identifier.

    If the entity Id is blank, ignore the supplied type id
    """
    assert type_id is not None,   "make_type_entity_id: no type id (%s, %s)"%(type_id, entity_id)
    assert entity_id is not None, "make_type_entity_id: no entity id (%s, %s)"%(type_id, entity_id)
    if entity_id != "":
        return type_id + "/" + entity_id
    return ""

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

def strip_comments(f):
    """
    Returns a file-like object that returns content from the supplied file-like
    but with comments removed.

    >>> f1 = StringIO.StringIO("// coment\\ndata\\n// another comment\\n\\n")
    >>> f2 = strip_comments(f1)
    >>> f2.read()
    '\\ndata\\n\\n\\n'
    """
    fnc = StringIO.StringIO()
    sof = fnc.tell()
    for line in f:
        if re.match("^\s*//", line):
            fnc.write("\n")
        else:
            fnc.write(line)
    fnc.seek(sof)
    return fnc

def renametree_temp(src):
    """
    Rename tree to temporary name, and return that name, or 
    None if the source directory does not exist.
    """
    count = 0 
    while count < 10:      # prevents indefinite loop
        count += 1
        tmp = os.path.join(os.path.dirname(src),"_removetree_tmp_%d"%(count))
        try:
            os.rename(src, tmp)
            return tmp      # Success!
        # except WindowsError as e:
        #     log.warning(
        #         "util.renametree_temp: WindowsError: winerror %d, strerror %s, errno %d"%
        #         (e.winerror, e.strerror, e.errno)
        #         )
        #     continue        # Try another temp name
        except OSError as e:
            time.sleep(1)
            if e.errno == errno.EACCES:
                log.warning("util.renametree_temp: %s EACCES, retrying"%tmp)
                continue    # Try another temp name
            if e.errno == errno.ENOTEMPTY:
                log.warning("util.renametree_temp: %s ENOTEMPTY, retrying"%tmp)
                continue    # Try another temp name
            if e.errno == errno.EEXIST:
                log.warning("util.renametree_temp: %s EEXIST, retrying"%tmp)
                shutil.rmtree(tmp, ignore_errors=True)  # Try to clean up old files
                continue    # Try another temp name
            if e.errno == errno.ENOENT:
                log.warning("util.renametree_temp: %s ENOENT, skipping"%tmp)
                break       # 'src' does not exist(?)
            raise           # Other error: propagaee
    return None

def removetree(tgt):
    """
    Work-around for python problem with shutils tree remove functions on Windows.
    See:
        http://stackoverflow.com/questions/23924223/
        http://stackoverflow.com/questions/1213706/
        http://stackoverflow.com/questions/1889597/
        http://bugs.python.org/issue19643
    """
    # shutil.rmtree error handler that attempts recovery on Windows from 
    # attempts to remove a read-only file or directory (see links above).
    def error_handler(func, path, execinfo):
        # figure out recovery based on error...
        e = execinfo[1]
        if e.errno == errno.ENOENT or not os.path.exists(path):
            return          # path does not exist
        if func in (os.rmdir, os.remove) and e.errno == errno.EACCES:
            try:
                os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
            except Exception as che:
                log.warning("util.removetree: chmod failed: %s"%che)
            try:
                func(path)
            except Exception as rfe:
                log.warning("util.removetree: 'func' retry failed: %s"%rfe)
                if not os.path.exists(path):
                    return      # Gone, assume all is well
                raise
        if e.errno == errno.ENOTEMPTY:
            log.warning("util.removetree: Not empty: %s, %s"%(path, tgt))
            time.sleep(1)
            removetree(path)    # Retry complete removal
            return
        log.warning("util.removetree: rmtree path: %s, error: %s"%(path, repr(execinfo)))
        raise e
    # Workaround for problems on Windows: it appears that the directory
    # removal does not complete immediately, causing subsequent failures.
    # Try renaming to a new directory first, so that the tgt is immediately 
    # available for re-use.
    tmp = renametree_temp(tgt)
    if tmp:
        shutil.rmtree(tmp, onerror=error_handler)
    return

def replacetree(src, tgt):
    """
    Work-around for python problem with shutils tree copy functions on Windows.
    See: http://stackoverflow.com/questions/23924223/
    """
    if os.path.exists(tgt):
        removetree(tgt)
    shutil.copytree(src, tgt)
    return

def updatetree(src, tgt):
    """
    Like replacetree, except that existing files are not removed unless replaced 
    by a file of the name name in the source tree.

    NOTE: can't use shutil.copytree for this, as that requires that the 
    destination tree does not exist.
    """
    files = os.listdir(src)
    for f in files:
        sf = os.path.join(src, f)
        if os.path.exists(sf) and not os.path.islink(sf):   # Ignore symlinks
            if os.path.isdir(sf):
                tf = os.path.join(tgt, f)
                if not os.path.isdir(tf):
                    os.makedirs(tf)
                updatetree(sf, tf)                          # Recursive dir copy
            else:
                shutil.copy2(sf, tgt)                       # Copy single file, may overwrite
    return

def download_url_to_file(url, fileName=None):
    """
    Download resource at given URL to a specified file, or to a a filename 
    based on any Content-disposition header present, or on the URL itself.

    This code lifted from a contribution by [Michael Waterfall](http://michael.typify.io/) 
    at [http://stackoverflow.com/questions/862173/]().  (Thanks!)
    """
    def getFileName(url, openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])
    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r, f)
    finally:
        r.close()
    return

def download_url_to_fileobj(url, fileobj=None):
    """
    Download resource at given URL and write the data to to a supplied
    file stream object.
    """
    r = urllib2.urlopen(urllib2.Request(url))
    try:
        shutil.copyfileobj(r, fileobj)
    finally:
        r.close()
    return (resource_url, resource_type)

# Update MIME typesreturned by open_url when opening a file
# @@TODO: unify logic with resourcetypes module, and do all MIME type wrangling there
import mimetypes
mimetypes.init()
mimetypes.add_type("text/markdown", ".md")

def open_url(url):
    """
    Opens a file-like object to access resource contents at a URL, and
    returns the access object, actual URL (following any redirect), and 
    resource type (MIME content-type string)
    """
    r = urllib2.urlopen(urllib2.Request(url))
    u = r.geturl()
    t = r.info().gettype()
    return (r, u, t)

def copy_resource_to_fileobj(srcobj, dstobj):
    """
    Copies data from a supplied souyrce file object to a supplied destination object.

    Specifically, this is used when downloading a web resource to a local stored entity.
    """
    #@@TODO: timeout / size limit?  (Potential DoS?)
    shutil.copyfileobj(srcobj, dstobj)
    return

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
