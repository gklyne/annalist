# Create your views here.

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import random
import logging
import rdflib

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from miscutils.HttpSession   import HTTP_Error, HTTP_Session
from miscutils.ro_namespaces import RDF, RO, ORE, AO

from rovserver.ContentNegotiationView import ContentNegotiationView
from rovserver.models import ResearchObject, AggregatedResource

# Logger for this module
log = logging.getLogger(__name__)

# Start RO IDs from random value to reduce chance of conflict when service is restarted
RO_generator = random.randint(0x00000000,0x7FFFFFFF)

RDF_serialize_formats = (
    { "application/rdf+xml":    "xml"
    , "text/turtle":            "turtle"
    })

# Used to optimize HTTP redirects.
# In particular to avoid multiple hits on sites like purl.org.
# This is not persistent, so restartingthe servoce will flush any saved URI mappings.
HTTP_REDIRECTS = {}

class RovServerHomeView(ContentNegotiationView):
    """
    View class to handle requests to the rovserver home URI
    """

    def error(self, values):
        template = loader.get_template('rovserver_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'])

    # GET

    @ContentNegotiationView.accept_types(["text/uri-list"])
    def render_uri_list(self, resultdata):
        resp = HttpResponse(status=200, content_type="text/uri-list")
        for ro in resultdata['rouris']:
            resp.write(str(ro)+"\n")
        return resp

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata):
        template = loader.get_template('rovserver_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        resultdata = {'rouris': ResearchObject.objects.all()}
        return (
            self.render_uri_list(resultdata) or
            self.render_html(resultdata) or 
            self.error(self.error406values())
            )

    # POST

    def generate_ro_uri(self):
        global RO_generator
        RO_generator = (RO_generator+1) & 0x7FFFFFFF
        return self.get_request_uri() + "ROs/%08x/"%RO_generator 

    def make_resource(self, ro, uri):
        log.debug("RovServerHomeView.make_resource: uri '%s'"%(uri))
        if uri in HTTP_REDIRECTS:
            uri = HTTP_REDIRECTS[uri]
        log.debug("- updated uri '%s'"%(uri))
        finaluri = uri
        is_rdf   = False
        retry_count = 0
        while retry_count < 5:
            retry_count += 1
            try:
                httpsession = HTTP_Session(uri)
                (status, reason, headers, finaluri, body) = httpsession.doRequestFollowRedirect(
                    uri, method="HEAD", exthost=True)
                if status == 200:
                    if str(finaluri) != uri:
                        log.info("- <%s> redirected to <%s>"%(uri, finaluri))
                        HTTP_REDIRECTS[uri] = str(finaluri)
                    is_rdf = headers["content-type"] in RDF_serialize_formats.iterkeys()
                else:
                    log.warning("HTTP resppnse %03d %s accessing %s, attempt %d"%
                                (status, reason, uri, retry_count))
                httpsession.close()
                break
            except Exception, e:
                log.warning("HTTPSession exception (%s) accessing %s, attempt %d"%(e, uri, retry_count))
        return AggregatedResource(ro=ro, uri=finaluri, is_rdf=is_rdf)

    @ContentNegotiationView.content_types(["text/uri-list"])
    def post_uri_list(self, values):
        # Extract URI list
        def hascontent(s):
            return s and (not s.startswith("#"))
        uri_list = filter(hascontent, unicode(self.request.body).splitlines())
        # Allocate URI
        ro_uri = self.generate_ro_uri()
        # Add to ResearchObjects model
        ro = ResearchObject(uri=ro_uri)
        ro.save()
        # Add aggregated URIs
        for u in uri_list:
            r = self.make_resource(ro, u)
            r.save()
            # print "resource: uri %s, ro %s, rdf %s "%(r.uri, r.ro.uri, r.is_rdf)
        # Assemble and return response
        template = loader.get_template('rovserver_created.html')
        context = RequestContext(self.request, { 'uri': ro_uri })
        resp = HttpResponse(template.render(context), status=201)
        resp['Location'] = ro_uri
        return resp

    def post(self, request):
        self.request = request      # For clarity: generic.View does this anyway
        return ( self.post_uri_list({}) or 
            self.error(self.error415values()) )


class ResearchObjectView(ContentNegotiationView):
    """
    View class to handle requests to a research obect URI
    """

    def error404values(self):
        return self.errorvalues(404, "Not found (No such RO)", 
            "Research object %(request_uri)s not found"
            )

    # GET

    @ContentNegotiationView.accept_types(RDF_serialize_formats.keys())
    def render_rdf(self, resultdata):
        ct = resultdata["accept_type"]
        log.debug("RO accept_type: %s"%(ct))
        sf = RDF_serialize_formats[ct]
        resp = HttpResponse(status=200, content_type=ct)
        resultdata['ro_manifest'].serialize(resp, format=sf, base=self.get_request_uri())
        return resp

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata):
        template = loader.get_template('research_object_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def getManifestGraph(self, ro, ro_resources):
        manifestgr = rdflib.Graph()
        rosub = rdflib.URIRef(ro.uri)
        manifestgr.add( (rosub, RDF.type, RO.ResearchObject) )
        for res in ro_resources:
            resuri = rdflib.URIRef(res.uri)
            manifestgr.add( (rosub, ORE.aggregates, resuri) )
            if res.is_rdf:
                # Annotation...
                astub = rdflib.BNode()
                manifestgr.add( (rosub, ORE.aggregates, astub) )
                manifestgr.add( (astub, RDF.type, RO.AggregatedAnnotation) )
                manifestgr.add( (astub, RDF.type, RO.AggregatedAnnotation) )
                manifestgr.add( (astub, RO.annotatesAggregatedResource, rosub) )
                manifestgr.add( (astub, AO.body, resuri) )
        return manifestgr

    def get(self, request, roslug):
        log.debug("ResearchObjectView.get: RO slug %s"%(roslug))
        self.request = request      # For clarity: generic.View does this anyway
        ro_uri       = self.get_request_uri()
        try:
            ro = ResearchObject.objects.get(uri=ro_uri)
        except ResearchObject.DoesNotExist, e:
            return self.error(self.error404values())
        ro_resources = AggregatedResource.objects.filter(ro=ro)
        resultdata = (
            { 'ro_uri':         ro_uri
            , 'ro_resources':   ro_resources
            , 'ro_manifest':    self.getManifestGraph(ro, ro_resources)
            })
        return (
            self.render_rdf(resultdata) or
            self.render_html(resultdata) or 
            self.error(self.error406values())
            )

    # DELETE

    def delete(self, request, roslug):
        log.debug("ResearchObjectView.delete: RO slug %s"%(roslug))
        self.request = request      # For clarity: generic.View does this anyway
        ro_uri       = self.get_request_uri()
        try:
            ro = ResearchObject.objects.get(uri=ro_uri)
        except ResearchObject.DoesNotExist, e:
            return self.error(self.error404values())
        ro.delete()
        return HttpResponse(None, status=204)

# End.

