# HTTP session class and supporting utilites.

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import re   # Used for link header parsing
import httplib2
import urlparse
import rdflib
import logging

# Logger for this module
log = logging.getLogger(__name__)

RDF_CONTENT_TYPES = (
    { "application/rdf+xml":    "xml"
    , "text/turtle":            "n3"
    , "text/n3":                "n3"
    , "text/nt":                "nt"
    , "application/json":       "jsonld"
    , "application/xhtml":      "rdfa"
    })

ACCEPT_RDF_CONTENT_TYPES = "application/rdf+xml, text/turtle"

def splitValues(txt, sep=",", lq='"<', rq='">'):
    """
    Helper function returns list of delimited values in a string,
    where delimiters in quotes are protected.

    sep is string of separator
    lq is string of opening quotes for strings within which separators are not recognized
    rq is string of corresponding closing quotes
    """
    result = []
    cursor = 0
    begseg = cursor
    while cursor < len(txt):
        if txt[cursor] in lq:
            # Skip quoted or bracketed string
            eq = rq[lq.index(txt[cursor])]  # End quote/bracket character
            cursor += 1
            while cursor < len(txt) and txt[cursor] != eq:
                if txt[cursor] == '\\': cursor += 1 # skip '\' quoted-pair
                cursor += 1
            if cursor < len(txt):
                cursor += 1 # Skip closing quote/bracket
        elif txt[cursor] in sep:
            result.append(txt[begseg:cursor])
            cursor += 1
            begseg = cursor
        else:
            cursor += 1
    # append final segment
    result.append(txt[begseg:cursor])
    return result

def testSplitValues():
    assert splitValues("a,b,c") == ['a','b','c']
    assert splitValues('a,"b,c",d') == ['a','"b,c"','d']
    assert splitValues('a, "b, c\\", c1", d') == ['a',' "b, c\\", c1"',' d']
    assert splitValues('a,"b,c",d', ";") == ['a,"b,c",d']
    assert splitValues('a;"b;c";d', ";") == ['a','"b;c"','d']
    assert splitValues('a;<b;c>;d', ";") == ['a','<b;c>','d']
    assert splitValues('"a;b";(c;d);e', ";", lq='"(', rq='")') == ['"a;b"','(c;d)','e']

def parseLinks(headerlist):
    """
    Helper function to parse 'link:' headers,
    returning a dictionary of links keyed by link relation type
    
    headerlist is a list of header (name,value) pairs
    """
    linkheaders = [ v for (h,v) in headerlist if h.lower() == "link" ]
    log.debug("parseLinks linkheaders %s"%(repr(linkheaders)))
    links = {}
    for linkheader in linkheaders:
        for linkval in splitValues(linkheader, ","):
            linkparts = splitValues(linkval, ";")
            linkmatch = re.match(r'''\s*<([^>]*)>\s*''', linkparts[0])
            if linkmatch:
                linkuri   = linkmatch.group(1)
                for linkparam in linkparts[1:]:
                    linkmatch = re.match(r'''\s*rel\s*=\s*"?(.*?)"?\s*$''', linkparam)  # .*? is non-greedy
                    if linkmatch:
                        linkrel = linkmatch.group(1)
                        log.debug("parseLinks links[%s] = %s"%(linkrel, linkuri))
                        links[linkrel] = linkuri
    return links

def testParseLinks():
    links = (
        ('Link', '<http://example.org/foo>; rel=foo'),
        ('Link', ' <http://example.org/bar> ; rel = bar '),
        ('Link', '<http://example.org/bas>; rel=bas; par = zzz , <http://example.org/bat>; rel = bat'),
        ('Link', ' <http://example.org/fie> ; par = fie '),
        ('Link', ' <http://example.org/fum> ; rel = "http://example.org/rel/fum" '),
        ('Link', ' <http://example.org/fas;far> ; rel = "http://example.org/rel/fas" '),
        )
    assert str(parseLinks(links)['foo']) == 'http://example.org/foo'
    assert str(parseLinks(links)['bar']) == 'http://example.org/bar'
    assert str(parseLinks(links)['bas']) == 'http://example.org/bas'
    assert str(parseLinks(links)['bat']) == 'http://example.org/bat'
    assert str(parseLinks(links)['http://example.org/rel/fum']) == 'http://example.org/fum'
    assert str(parseLinks(links)['http://example.org/rel/fas']) == 'http://example.org/fas;far'


# Class for exceptions raised by HTTP session

class HTTP_Error(Exception):

    def __init__(self, msg="HTTP_Error", value=None, uri=None):
        self._msg   = msg
        self._value = value
        self._uri   = uri
        return

    def __str__(self):
        txt = self._msg
        if self._uri:   txt += " for "+str(self._uri)
        if self._value: txt += ": "+repr(self._value)
        return txt

    def __repr__(self):
        return ( "HTTP_Error(%s, value=%s, uri=%s)"%
                 (repr(self._msg), repr(self._value), repr(self._uri)))


# Class for handling Access in an HTTP session

class HTTP_Session(object):
    
    """
    Client access class for HTTP session.

    Creates a session to access a single HTTP endpoint,
    and provides methods to issue requests on this session

    This class is primarily designed to access a specific endpoint, and 
    by default refuses requests for different endpoints.  But the request
    methods accept an additional "exthost" parameter that can be used to
    override this behaviour.  Specifying "exthost=True" causes the request 
    to allow URIs that use different scheme, hostname or port than the original
    request, but such requests are not issued using the access key of the HTTP
    session.
    """

    def __init__(self, baseuri, accesskey=None):
        log.debug("HTTP_Session.__init__: baseuri "+baseuri)
        self._baseuri = baseuri
        self._key     = accesskey
        parseduri     = urlparse.urlsplit(baseuri)
        self._scheme  = parseduri.scheme
        self._host    = parseduri.netloc
        self._path    = parseduri.path
        self._http2   = httplib2.Http()
        return

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return

    def close(self):
        self._key   = None
        self._http2 = None
        return

    def baseuri(self):
        return self._baseuri

    def getpathuri(self, uripath):
        # str used here so rdflib.URIRef values can be accepted
        return urlparse.urljoin(self._baseuri, str(uripath))

    def error(self, msg, value=None):
        return HTTP_Error(msg=msg, value=value, uri=self._baseuri)

    def parseLinks(self, headers):
        """
        Parse link header(s), return dictionary of links keyed by link relation type
        """
        return parseLinks(headers["_headerlist"])

    def doRequest(self, uripath,
            method="GET", body=None, ctype=None, accept=None, reqheaders=None, exthost=False):
        """
        Perform HTTP request.

        Parameters:
            uripath     URI reference of resource to access, resolved against the base URI of
                        the current HTTP_Session object.
            method      HTTP method to use (default GET)
            body        request body to use (default none)
            ctype       content-type of request body (default none)
            accept      string containing list of content types for HTTP accept header
            reqheaders  dictionary of additional header fields to send with the HTTP request
            exthost     True if a request to a URI with a scheme and/or host different than 
                        the session base URI is to be respected (default False).

        Return:
             status, reason(text), response headers, response body

        Note: relies on to,meout or object deallocation to close connections:
        see http://stackoverflow.com/questions/16687033/is-this-a-bug-of-httplib2.
        Python's reference counting should ensure Http objects amnd referenced connections
        are deallocated promptly.
        """
        # Construct request path
        urifull  = self.getpathuri(uripath)
        uriparts = urlparse.urlsplit(urifull)
        path     = uriparts.path
        if uriparts.query: path += ("?"+uriparts.query)
        # Sort out HTTP connection to use: session or new
        if ( (uriparts.scheme and uriparts.scheme != self._scheme) or
             (uriparts.netloc and uriparts.netloc != self._host) ):
            if exthost:
                usescheme  = uriparts.scheme
                usekey     = None
            elif (uriparts.scheme and uriparts.scheme != self._scheme):
                raise HTTP_Error(
                    "URI scheme mismatch",
                    value=uriparts.scheme,
                    uri=self._baseuri)
            elif (uriparts.netloc and uriparts.netloc != self._host):
                raise HTTP_Error(
                    "URI host:port mismatch",
                    value=uriparts.netloc,
                    uri=self._baseuri)
        else:
            usescheme  = self._scheme
            usekey     = self._key
        # Assemble request headers
        if not reqheaders:
            reqheaders = {}
        if usekey:
            reqheaders["authorization"] = "Bearer "+usekey
        if ctype:
            reqheaders["content-type"] = ctype
        if accept:
            reqheaders["accept"] = accept
        # Execute request
        log.debug("HTTP_Session.doRequest method:     "+method)
        log.debug("HTTP_Session.doRequest path:       "+path)
        log.debug("HTTP_Session.doRequest reqheaders: "+repr(reqheaders))
        log.debug("HTTP_Session.doRequest body:       "+repr(body))
        (resp, data) = self._http2.request(urifull, 
            method=method, body=body, headers=reqheaders)
        # Pick out elements of response
        try:
            status   = resp.status
            reason   = resp.reason
            headerlist = [ (hn.lower(),resp[hn]) for hn in resp ]
            headers  = dict(headerlist)   # dict(...) keeps last result of multiple keys
            headers["_headerlist"] = headerlist
            log.debug("HTTP_Session.doRequest response:   "+str(status)+" "+reason)
            log.debug("HTTP_Session.doRequest rspheaders: "+repr(headers))
        except Exception, e:
            log.warn("HTTP_Session error %r accessing %s with request headers %r"%(e, uripath, reqheaders))
            status = 900
            reason = str(e)
            headers = {"_headerlist": []}
            data = None
        ###log.debug("HTTP_Session.doRequest data:     "+repr(data))
        return (status, reason, headers, data)

    def doRequestFollowRedirect(self, uripath, 
            method="GET", body=None, ctype=None, accept=None, reqheaders=None, exthost=False):
        """
        Perform HTTP request, following any redirect returned.

        Parameters:
            uripath     URI reference of resource to access, resolved against the base URI of
                        the current HTTP_Session object.
            method      HTTP method to use (default GET)
            body        request body to use (default none)
            ctype       content-type of request body (default none)
            accept      string containing list of content types for HTTP accept header
            reqheaders  dictionary of additional header fields to send with the HTTP request
            exthost     True if a request to a URI with a scheme and/or host different than 
                        the session base URI is to be respected (default False).

        Return:
             status, reason(text), response headers, final URI, response body

        """
        (status, reason, headers, data) = self.doRequest(uripath,
            method=method, accept=accept,
            body=body, ctype=ctype, reqheaders=reqheaders, 
            exthost=exthost)
        return (status, reason, headers, headers['content-location'], data)

    def doRequestRDFFollowRedirect(self, uripath, 
            method="GET", body=None, ctype=None, reqheaders=None, exthost=False, graph=None):
        """
        Perform HTTP request with RDF response, following any redirect returned

        If the request succeeds, return response as an RDF graph,
        or return fake 9xx status if RDF cannot be parsed.
        Otherwise return response and content per request.
        Thus, only 2xx responses include RDF data.

        Parameters:
            uripath     URI reference of resource to access, resolved against the base URI of
                        the current HTTP_Session object.
            method      HTTP method to use (default GET)
            body        request body to use (default none)
            ctype       content-type of request body (default none)
            reqheaders  dictionary of additional header fields to send with the HTTP request
            exthost     True if a request to a URI with a scheme and/or host different than 
                        the session base URI is to be respected (default False).
            graph       an rdflib.Graph object to which any RDF read is added.  If not
                        provided, a new RDF graph is created and returmned.

        Return:
             status, reason(text), response headers, final URI, response graph or body
        """
        (status, reason, headers, finaluri, data) = self.doRequestFollowRedirect(uripath,
            method=method, body=body,
            ctype=ctype, accept=ACCEPT_RDF_CONTENT_TYPES, reqheaders=reqheaders, 
            exthost=exthost)
        if status >= 200 and status < 300:
            content_type = headers["content-type"].split(";",1)[0].strip().lower()
            if content_type in RDF_CONTENT_TYPES:
                rdfgraph   = graph if graph != None else rdflib.graph.Graph()
                baseuri    = self.getpathuri(uripath)
                bodyformat = RDF_CONTENT_TYPES[content_type]
                # log.debug("HTTP_Session.doRequestRDF data:\n----\n"+data+"\n------------")
                try:
                    # rdfgraph.parse(data=data, location=baseuri, format=bodyformat)
                    rdfgraph.parse(data=data, publicID=baseuri, format=bodyformat)
                    data = rdfgraph
                except Exception, e:
                    log.info("HTTP_Session.doRequestRDF: %s"%(e))
                    log.info("HTTP_Session.doRequestRDF parse failure: '%s', '%s'"%(content_type, bodyformat))
                    # log.debug("HTTP_Session.doRequestRDF data:\n----\n"+data[:200]+"\n------------")
                    status   = 902
                    reason   = "RDF (%s) parse failure"%bodyformat
            else:
                status   = 901
                reason   = "Non-RDF content-type returned"
        return (status, reason, headers, finaluri, data)

    def doRequestRDF(self, uripath, 
            method="GET", body=None, ctype=None, reqheaders=None, exthost=False, graph=None):
        """
        Perform HTTP request with RDF response.

        If the request succeeds, return response as RDF graph,
        or return fake 9xx status if RDF cannot be parsed.
        Otherwise return response and content per request.
        Thus, only 2xx responses include RDF data.

        Parameters:
            uripath     URI reference of resource to access, resolved against the base URI of
                        the current HTTP_Session object.
            method      HTTP method to use (default GET)
            body        request body to use (default none)
            ctype       content-type of request body (default none)
            reqheaders  dictionary of additional header fields to send with the HTTP request
            exthost     True if a request to a URI with a scheme and/or host different than 
                        the session base URI is to be respected (default False).
            graph       an rdflib.Graph object to which any RDF read is added.  If not
                        provided, a new RDF graph is created and returmned.

        Return:
             status, reason(text), response headers, response graph or body

        """
        (status, reason, headers, finaluri, data) = self.doRequestRDFFollowRedirect(uripath,
            method=method, body=body,
            ctype=ctype, accept=ACCEPT_RDF_CONTENT_TYPES, reqheaders=reqheaders, 
            exthost=exthost)
        return (status, reason, headers, data)

# End.
