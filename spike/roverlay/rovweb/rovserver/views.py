# Views for roveraly server

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne and University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import random
import logging
import uuid
import rdflib
import os.path
import json

import httplib2

from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from miscutils.HttpSession   import HTTP_Error, HTTP_Session
from miscutils.ro_namespaces import RDF, RO, ORE, AO

from rovserver.ContentNegotiationView import ContentNegotiationView
from rovserver.models import ResearchObject, AggregatedResource, CredentialsModel

from OAuth2CheckBackend import flow_to_dict, dict_to_flow

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
# This is not persistent, so restartingthe service will flush any saved URI mappings.
HTTP_REDIRECTS = {}

# Per-instance generated secret key for CSRF protection via OAuth2 state value.
# Regenerated each time this service is started.
FLOW_SECRET_KEY = str(uuid.uuid1())

CONFIG_BASE = "/etc/roverlay/"
CONFIG_BASE = os.path.join(os.path.expanduser("~"), ".roverlay/")

# @@TODO: generate this dynamically
PROVIDER_LIST = (
    { "Google": "google_oauth2_client_secrets.json"
    })

# @@TODO: generate this dynamically, from client secrets?
PROVIDER_PROFILE_URI = (
    { "Google": "https://www.googleapis.com/plus/v1/people/me/openIdConnect"
    })

class RovServerLoginUserView(ContentNegotiationView):
    """
    View class to handle login: form to gather user id and other login information.

    The login page solicits a user id (and, in due course, an identity provider)

    The login page supports the following request parameters:

    continuation={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
    scope={string}
    - requested or required access scope
    """
    # @@TODO: use Django form API
    def get(self, request):
        # Retrieve request parameters
        continuation = request.GET.get("continuation", "/")
        scope        = request.GET.get("scope",        "openid profile email")
        # data populate form
        logindata = (
            # @@TODO: avoid duplication with urls.py
            { "logincomplete":  "/rovserver/login/complete/"
            , "continuation":   request.GET.get("continuation", "/rovserver/")
            , "userid":         request.GET.get("userid", "")
            , "providers":      PROVIDER_LIST.keys()
            , "provider":       PROVIDER_LIST.keys()[0]
            , "scope":          scope
            })
        # Render form & return control to browser
        template = loader.get_template('login.html')
        context  = RequestContext(self.request, logindata)
        return HttpResponse(template.render(context))

class RovServerLoginAuthView(ContentNegotiationView):
    """
    View class initiate an OAuth2 authorization (or similar) flow

    It saves the supplied user id in a session value, and redirects the user to the 
    identity provider, which in due course returns control to the application along 
    with a suitable authorization grant.

    The login form provides the following values:

    userid={string}
    - a user identifying string that will be associated with the external service
      login credentials.
    provider={string}
    - a string that identifiues a provioder selectred to proviode authentication/
      authorization for the indicated user.  This string is an index to PROVIDER_LIST,
      which in turn contains filenames for client secrets to user when using the 
      indicated identity provider.
    logincomplete={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
      Communicated via a hidden form value.
    continuation={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
      Communicated via a hidden form value.
    scope={string}
    - Requested or required access scope, communicated via a hidden form value.
    """

    def post(self, request):
        # Retrieve request parameters
        userid        = request.POST.get("userid",        "")
        provider      = request.POST.get("provider",      "Google")
        logincomplete = request.POST.get("logincomplete", "/rovserver/login/complete/")
        continuation  = request.POST.get("continuation",  "/rovserver/")
        scope         = request.POST.get("scope",         "")
        if scope == "":
            scope = "openid profile email offline_access"
        # Access or create flow object for this session
        if request.POST["login"] == "Login":
            # Create and initialize flow object
            clientsecrets_filename = os.path.join(
                CONFIG_BASE, "providers/", PROVIDER_LIST[provider]
                )
            flow = flow_from_clientsecrets(
                clientsecrets_filename,
                scope=scope,
                redirect_uri=request.build_absolute_uri(logincomplete)
                )
            flow.params['state']        = xsrfutil.generate_token(FLOW_SECRET_KEY, request.user)
            flow.params['provider']     = provider
            flow.params['userid']       = userid
            # flow.params['scope']        = scope
            flow.params['continuation'] = continuation
            # Save flow object in Django session
            request.session['oauth2flow'] = flow_to_dict(flow)
            # Initiate OAuth2 dance
            auth_uri = flow.step1_get_authorize_url()
            return HttpResponseRedirect(auth_uri)
        # Login cancelled: redirect to continuation
        # (which may just redisplay the login page)
        return HttpResponseRedirect(continuation)

class RovServerLoginCompleteView(ContentNegotiationView):
    """
    View class used to complete login process with authorization grant provided by
    authorization server.
    """
    def get(self, request):
        # Look for authorization grant
        flow       = dict_to_flow(request.session['oauth2flow'])
        credential = flow.step2_exchange(request.REQUEST) # Raises FlowExchangeError if a problem occurs
        user = authenticate(
            username=flow.params['userid'], password=credential, 
            profile_uri=PROVIDER_PROFILE_URI[flow.params['provider']]
            )
        assert user
        login(request, user)
        # Save credentials
        storage    = Storage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
        print "credential: "+repr(credential.to_json())
        print "id_token:   "+repr(credential.id_token)
        print "user.username:   "+user.username
        print "user.first_name: "+user.first_name
        print "user.last_name:  "+user.last_name
        print "user.email:      "+user.email
        return HttpResponseRedirect(flow.params['continuation'])

class RovServerLogoutUserView(ContentNegotiationView):
    """
    View class to handle logout
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/rovserver/")

class RovServerHomeView(ContentNegotiationView):
    """
    View class to handle requests to the rovserver home URI
    """
    def __init__(self):
        super(RovServerHomeView, self).__init__()
        self.credential = None
        return

    def error(self, values):
        template = loader.get_template('rovserver_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'])

    # Authentication and authorization
    def authenticate(self):
        """
        Return None if required authentication is present, otherwise
        an appropriate login redirection response.

        self.credential is set to credential that can me used to access resource

        # self.userid is set to a URI that identifies the authenticated user

        # self.useraccount, self.userfullname may be set to user account name
        # and user full name strings if information is available.
        """
        if self.request.user.is_authenticated():
            storage         = Storage(CredentialsModel, 'id', self.request.user, 'credential')
            self.credential = storage.get()
            if not ( (self.credential is None) or self.credential.invalid ):
                return None         # Valid credential present: proceed...
        # Initiate OAuth/OIDC login sequence 
        # @@TODO: avoid duplication with urls.py
        return HttpResponseRedirect("login/")

    def authorize(self, scope):
        """
        Return None if user is authorized to perform the requested operation,
        otherwise appropriate 403 Forbidden response.

        @@TODO interface details; scope at least will be needed
        """
        return None

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
        def resultdata():
            return {'rouris': ResearchObject.objects.all()}
        return (
            self.authenticate() or 
            self.render_uri_list(resultdata()) or
            self.render_html(resultdata()) or 
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
        return (
            self.authenticate() or 
            self.post_uri_list({}) or 
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

