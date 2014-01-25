# Utilities to mock HTTP resources for testing.
#
#     with HttpMockResources(baseuri, path):
#         # test code here
# or
#     @HttpMockResourcesZZZZ(baseuri, path)
#     def test_stuff(...)
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import urllib
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
            ru = self._baseuri + r
            rt = HttpContentType(r)
            httpretty.register_uri(httpretty.GET,  ru, status=200, content_type=rt,
                body=self._dict[r])
            httpretty.register_uri(httpretty.HEAD, ru, status=200, content_type=rt)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        suppress_exc = False
        httpretty.disable()
        return suppress_exc

# End.
