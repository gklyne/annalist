# Utilities to mock HTTP resources for testing.
#
#     with MockHttpFileResources(baseuri, path):
#         # test code here
# or
#     with @HttpMockDictResources(baseuri, 
#         { 'rel_path_1': body_1
#         , 'rel_path_2': body_2
#           (etc.)
#         }):
#         # test_stuff(...)
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import urllib
import urlparse
import httpretty
import ScanDirectories

from FileMimeTypes import FileMimeTypes

FileType_MimeType = dict([ (ft,ct) for (ct, fts) in FileMimeTypes
                                   for ft in fts ])

def HttpContentType(filename):
    fsplit = filename.rsplit(".", 1)
    if len(fsplit) == 2 and fsplit[1] in FileType_MimeType:
        return FileType_MimeType[fsplit[1]]
    return "application/octet-stream"

class MockHttpFileResources(object):

    def __init__(self, baseuri, path):
        self._baseuri = baseuri
        self._path    = path
        return

    def __enter__(self):
        httpretty.enable()
        # register stuff...
        refs = ScanDirectories.CollectDirectoryContents(self._path, baseDir=self._path, 
            listDirs=False, listFiles=True, recursive=True)
        for r in refs:
            ru = self._baseuri + urllib.pathname2url(r)
            rt = HttpContentType(r)
            # log.info("MockHttpFileResource uri %s, file %s"%(ru, self._path+r))
            with open(self._path+r, 'r') as cf:
                httpretty.register_uri(httpretty.GET,  ru, status=200, content_type=rt,
                    body=cf.read())
                httpretty.register_uri(httpretty.HEAD, ru, status=200, content_type=rt)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        suppress_exc = False
        httpretty.disable()
        return suppress_exc

class MockHttpDictResources(object):

    def __init__(self, baseuri, resourcedict):
        self._baseuri = baseuri
        self._dict    = resourcedict
        return

    def __enter__(self):
        httpretty.enable()
        # register stuff...
        for r in self._dict.keys():
            ru = urlparse.urljoin(self._baseuri, r)
            rt = HttpContentType(r)
            # print "@@ MockHttpDictResources: registering: %s"%ru
            httpretty.register_uri(httpretty.GET,  ru, status=200, content_type=rt,
                body=self._dict[r])
            httpretty.register_uri(httpretty.HEAD, ru, status=200, content_type=rt)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        suppress_exc = False
        httpretty.disable()
        return suppress_exc

# End.
