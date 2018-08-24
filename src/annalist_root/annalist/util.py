# pylint: disable=broad-except, wrong-import-order

"""
Various utilities for Annalist common functions
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import os.path
import errno
import traceback
import re
import stat
import time
import json
import shutil

from django.conf            import settings

from utils.py3porting       import (
    is_string, to_unicode, StringIO, 
    urlparse, urljoin, urlsplit, 
    urlopen, Request, get_message_type
    )

from annalist.identifiers   import ANNAL

def valid_id(id_string, reserved_ok=False):
    """
    Checks the supplied id is valid as an Annalist identifier.

    The main requirement is that it is valid as a URI path segment, so it can be used
    in the creation of URIs for Annalist resources.  Also, filters out reserved Annalist
    identifiers unless reserved_ok=True parameter is provided.

    >>> valid_id("abcdef_1234")
    True
    >>> valid_id("abcdef/1234")
    False
    >>> valid_id("_annalist_collection")
    False
    >>> valid_id("_annalist_collection", reserved_ok=True)
    True
    >>> valid_id("")
    False
    """
    reserved = (
        [ "_annalist_collection"
        # , "_annalist_site"
        ])
    # cf. urls.py:
    if id_string and re.match(r"\w{1,128}$", id_string):
        return reserved_ok or (id_string not in reserved)
    # log.warning("util.valid_id: id %s"%(id_string))
    return False

def split_type_entity_id(eid, default_type_id=None):
    """
    Returns (type_id,entyity_id) pair for supplied string "type_id/entity_id".
    The supplied `eid` may be a bare "entity_id" then the supplied default 
    type_id is used.

    >>> split_type_entity_id("type_id/entity_id") == ('type_id', 'entity_id')
    True
    >>> split_type_entity_id("t/e", "f") == ('t', 'e')
    True
    >>> split_type_entity_id("entity_id", "def_type_id") == ('def_type_id', 'entity_id')
    True
    >>> split_type_entity_id(None, "def_type_id") == ('def_type_id', None)
    True
    """
    if eid is not None:
        sub_ids = eid.split("/")
        if len(sub_ids) == 2:
            return (sub_ids[0], sub_ids[1])
        if len(sub_ids) == 1:
            return (default_type_id, sub_ids[0])
        return (default_type_id, "")
    return (default_type_id, None)

def extract_entity_id(eid):
    """
    Accepts an entity id which may be have `type_id/entity_id` form, and returns
    the bare `entity_id` value.

    >>> extract_entity_id("type_id/entity_id") == "entity_id"
    True
    >>> extract_entity_id("entity_id") == "entity_id"
    True
    """
    _type_id, entity_id = split_type_entity_id(eid)
    return entity_id

def fill_type_entity_id(eid, default_type_id=None):
    """
    Assemble a type+entity composite identifier based on a supplied id string.
    If the string does not already include a type_id value, the supplied default
    is used.

    >>> fill_type_entity_id("entity_id", default_type_id="def_type_id") == "def_type_id/entity_id"
    True
    >>> fill_type_entity_id("type_id/entity_id", default_type_id="def_type_id") == "type_id/entity_id"
    True
    """
    type_id, entity_id = split_type_entity_id(eid, default_type_id=default_type_id)
    return make_type_entity_id(type_id, entity_id)

def make_type_entity_id(type_id=None, entity_id=None):
    """
    Assemble a type_id and entity_id and return a composite identifier.

    If the entity Id is blank, ignore the supplied type id

    >>> make_type_entity_id(type_id="type_id", entity_id="entity_id") == "type_id/entity_id"
    True
    >>> make_type_entity_id(type_id="type_id", entity_id="") == ""
    True
    """
    assert type_id is not None,   "make_type_entity_id: no type id (%s, %s)"%(type_id, entity_id)
    assert entity_id is not None, "make_type_entity_id: no entity id (%s, %s)"%(type_id, entity_id)
    if entity_id != "":
        return type_id + "/" + entity_id
    return ""

def make_entity_base_url(url):
    """
    Returns an entity URL with a trailing "/" so that it can be used consistently
    with urljoin to obtain URLs for specific resources associated with the entity.

    >>> make_entity_base_url("/example/path/") == '/example/path/'
    True
    >>> make_entity_base_url("/example/path") == '/example/path/'
    True
    """
    return url if url.endswith("/") else url + "/"

def label_from_id(id_string):
    """
    Returns a label string constructed from the suppliued Id string

    Underscore characters in the Id are replaced by spaces.
    The first character may be capirtalized.

    >>> label_from_id("entity_id") == "Entity id"
    True
    """
    temp  = id_string.replace('_', ' ').strip()
    label = temp[0].upper() + temp[1:] 
    return label

def slug_from_name(filename):
    """
    Extracts a slug (id) value from a filename

    >>> slug_from_path("bar.baz") == 'bar'
    True
    >>> slug_from_path("bar") == 'bar'
    True
    >>> slug_from_path(".baz") == '.baz'
    True
    """
    slug = os.path.splitext(filename)[0]
    return slug

def slug_from_path(path):
    """
    Extracts a slug (id) value from a file path

    >>> slug_from_path("/foo/bar.baz") == 'bar'
    True
    >>> slug_from_path("/bar") == 'bar'
    True
    >>> slug_from_path("bar") == 'bar'
    True
    >>> slug_from_path("/example.org/foo/bar/.baz") == '.baz'
    True
    >>> slug_from_path("/foo/bar.baz") == 'bar'
    True
    >>> slug_from_path("/example.org/foo/bar/")+"$" == '$'
    True
    """
    return slug_from_name(os.path.basename(path))

def slug_from_uri(uri):
    """
    Extracts a slug (id) value from a URI

    >>> slug_from_uri("http:/example.org/foo/bar") == 'bar'
    True
    >>> slug_from_uri("/example.org/foo/bar") == 'bar'
    True
    >>> slug_from_uri("/foo/bar") == 'bar'
    True
    >>> slug_from_uri("/bar") == 'bar'
    True
    >>> slug_from_uri("bar") == 'bar'
    True
    >>> slug_from_uri("/example.org/foo/bar/")+"$" == '$'
    True
    >>> slug_from_uri("http:/example.org/foo/bar.baz") == 'bar'
    True
    >>> slug_from_uri("http:/example.org/foo/bar;baz") == 'bar;baz'
    True
    >>> slug_from_uri("http:/example.org/foo/bar?baz") == 'bar'
    True
    >>> slug_from_uri("http:/example.org/foo/bar#baz") == 'bar'
    True
    """
    return slug_from_path(urlsplit(uri).path)

def ensure_dir(dirname):
    """
    Ensure that a named directory exists; if it does not, attempt to create it.
    """
    try:
        os.makedirs(dirname)
    except OSError as e:
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
                This value may be absent (an empty list).
    filename    is a file name for the data resource to be read.

    Returns a pair containing the full directory and path names for the entity file.

    >>> entity_dir_path("/base/dir/","sub","file.ext") == ('/base/dir/sub', '/base/dir/sub/file.ext')
    True
    >>> entity_dir_path("/base/dir/",["sub"],"file.ext") == ('/base/dir/sub', '/base/dir/sub/file.ext')
    True
    >>> entity_dir_path("/base/dir/",[],"file.ext") == ('/base/dir', '/base/dir/file.ext')
    True
    >>> entity_dir_path("/base/dir/",["sub1","sub2"],"file.ext") == ('/base/dir/sub1/sub2', '/base/dir/sub1/sub2/file.ext')
    True
    >>> entity_dir_path("/base/dir",["sub"],"file.ext") == ('/base/dir/sub', '/base/dir/sub/file.ext')
    True
    >>> entity_dir_path("/base/dir",[],"sub/file.ext") == ('/base/dir/sub', '/base/dir/sub/file.ext')
    True
    """
    # log.debug("util.entity_dir_path %s, %r, %s"%(base_dir, path, filename))
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

    >>> entity_path('.',[],"file.ext") == './file.ext'
    True
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

    >>> entity_url_host("http://example.org/basepath/", "/path/to/entity") == 'example.org'
    True
    >>> entity_url_host("http://example.org:80/basepath/", "/path/to/entity") == 'example.org:80'
    True
    >>> entity_url_host("http://userinfo@example.org:80/basepath/", "/path/to/entity") == 'example.org:80'
    True
    >>> entity_url_host("http://base.example.org:80/basepath/", "http://ref.example.org/path/to/entity") == 'ref.example.org'
    True
    """
    uri = urljoin(baseuri, entityref)
    p   = urlparse(uri)
    h   = p.hostname or ""
    if p.port:
        h += ":" + str(p.port)
    return h

def entity_url_path(baseuri, entityref):
    """
    Return absolute path part from an entity URI, excluding query or fragment.

    >>> entity_url_path("http://example.org/basepath/", "/path/to/entity") == '/path/to/entity'
    True
    >>> entity_url_path("http://example.org/basepath/", "relpath/to/entity") == '/basepath/relpath/to/entity'
    True
    >>> entity_url_path("http://example.org/basepath/", "/path/to/entity?query") == '/path/to/entity'
    True
    >>> entity_url_path("http://example.org/basepath/", "/path/to/entity#frag") == '/path/to/entity'
    True
    >>> entity_url_path("/basepath/", "relpath/to/entity") == '/basepath/relpath/to/entity'
    True
    """
    uri = urljoin(baseuri, entityref)
    return urlparse(uri).path

def make_resource_url(baseuri, entityref, resourceref):
    """
    Build a URL for an entity resource that is based on a supplied base URI
    and entity reference, but including the supplied resource name reference
    (i.e. filename)

    This function preserves any query parameters from the supplied entityref.

    >>> make_resource_url("http://example.org/foo/", "/bar/stuff", "entity.ref") == 'http://example.org/bar/entity.ref'
    True
    >>> make_resource_url("http://example.org/foo/", "/bar/stuff?query=val", "entity.ref") == 'http://example.org/bar/entity.ref?query=val'
    True
    """
    url          = urljoin(baseuri, entityref)
    resource_url = urljoin(url, make_resource_ref_query(entityref, resourceref))
    return resource_url

def make_resource_ref_query(entityref, resourceref):
    """
    Returns `resourceref` with the query component (if any) from entityref.

    This is used to generate a resource reference that is the supplied resource ref
    treated as relative to the supplied entityref, including any query parameters
    included in entityref.

    >>> make_resource_ref_query("http://example.com/foo?query=value", "http://example.org/bar") == "http://example.org/bar?query=value"
    True
    """
    query = urlsplit(entityref).query
    if query != "":
        query = "?" + query
    return urljoin(resourceref, query)

def strip_comments(f):
    """
    Returns a file-like object that returns content from the supplied file-like
    object, but with comment lines replaced with blank lines.

    >>> f1 = StringIO("// comment\\ndata\\n// another comment\\n\\n")
    >>> f2 = strip_comments(f1)
    >>> f2.read() == '\\ndata\\n\\n\\n'
    True
    """
    fnc = StringIO()
    sof = fnc.tell()
    for line in f:
        if re.match(r"^\s*//", line):
            fnc.write("\n")
        else:
            fnc.write(to_unicode(line))
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
                log.warning("util.renametree_temp: %s EACCES, retrying", tmp)
                continue    # Try another temp name
            if e.errno == errno.ENOTEMPTY:
                log.warning("util.renametree_temp: %s ENOTEMPTY, retrying", tmp)
                continue    # Try another temp name
            if e.errno == errno.EEXIST:
                log.warning("util.renametree_temp: %s EEXIST, retrying", tmp)
                shutil.rmtree(tmp, ignore_errors=True)  # Try to clean up old files
                continue    # Try another temp name
            if e.errno == errno.ENOENT:
                log.warning("util.renametree_temp: %s ENOENT, skipping", tmp)
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
        """
        figure out recovery based on error...
        """
        e = execinfo[1]
        if e.errno == errno.ENOENT or not os.path.exists(path):
            return          # path does not exist
        if func in (os.rmdir, os.remove) and e.errno == errno.EACCES:
            try:
                os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
            except Exception as che:
                log.warning("util.removetree: chmod failed: %s", che)
            try:
                func(path)
            except Exception as rfe:
                log.warning("util.removetree: 'func' retry failed: %s", rfe)
                if not os.path.exists(path):
                    return      # Gone, assume all is well
                raise
        if e.errno == errno.ENOTEMPTY:
            log.warning("util.removetree: Not empty: %s, %s", path, tgt)
            time.sleep(1)
            removetree(path)    # Retry complete removal
            return
        log.warning("util.removetree: rmtree path: %s, error: %r", path, execinfo)
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
    # print "@@ replacetree src %s"%(src,)
    # print "@@ replacetree tgt %s"%(tgt,)
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
        """
        Local helper to extract filename from content disposition header or URL
        """
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            # cd = dict(map(
            #     lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
            #     openUrl.info()['Content-Disposition'].split(';')))
            cd = dict(
                    [ x.strip().split('=') if '=' in x else (x.strip(),'')
                      for x in openUrl.info()['Content-Disposition'].split(';')
                    ])
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: 
                    return filename
        return os.path.basename(urlsplit(url)[2])
    r = urlopen(Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r, f)
    finally:
        r.close()
    return

def __unused__download_url_to_fileobj(url, fileobj=None):
    """
    Download resource at given URL and write the data to to a supplied
    file stream object.
    """
    r = urlopen(Request(url))
    try:
        shutil.copyfileobj(r, fileobj)
    finally:
        r.close()
    return

# Update MIME types returned by open_url when opening a file
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
    r = urlopen(Request(url))
    u = r.geturl()
    t = get_message_type(r.info())
    return (r, u, t)

def copy_resource_to_fileobj(srcobj, dstobj):
    """
    Copies data from a supplied source file object to a supplied destination object.

    Specifically, this is used when downloading a web resource to a local stored entity.
    """
    #@@TODO: timeout / size limit?  (Potential DoS?)
    shutil.copyfileobj(srcobj, dstobj)
    return

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
