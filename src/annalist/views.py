"""
Annalist view definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path
import json
import random
import logging
import uuid

import rdflib
import httplib2

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

import oauth2.views

from utils.ContentNegotiationView import ContentNegotiationView

LOGIN_URIS = None

# Create your views here.

class AnnalistGenericView(ContentNegotiationView):
    """
    Common base class for Annalist views
    """

    def __init__(self):
        super(AnnalistGenericView, self).__init__()
        self.credential = None
        return

    def error(self, values):
        template = loader.get_template('annalist_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'])

    # Authentication and authorization
    def authenticate(self):
        """
        Return None if required authentication is present, otherwise
        an appropriate login redirection response.

        self.credential is set to credential that can be used to access resource
        """
        # Cache copy of URIs to use with OAuth2 login
        global LOGIN_URIS
        if LOGIN_URIS is None:
            LOGIN_URIS = (
                { "login_form_uri": reverse('LoginUserView')
                , "login_post_uri": reverse('LoginPostView')
                , "login_done_uri": reverse('LoginDoneView')
                })
        # Initiate OAuth2 login sequence, if neded
        return oauth2.views.confirm_authentication(self, 
            continuation_uri=self.get_request_uri(),
            **LOGIN_URIS
            )

    def authorize(self, scope):
        """
        Return None if user is authorized to perform the requested operation,
        otherwise appropriate 403 Forbidden response.

        @@TODO interface details; scope at least will be needed
        """
        return None

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata, template_name):
        template = loader.get_template(template_name)
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

class AnnalistHomeView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist home URI
    """
    def __init__(self):
        super(AnnalistHomeView, self).__init__()
        return

    # GET

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata):
        template = loader.get_template('annalist_home.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        def resultdata():
            return { 'collections': { 'foo': 'foo-colllection', 'bar': 'bar-colllection' } }
        return (
            self.authenticate() or 
            self.render_html(resultdata()) or 
            self.error(self.error406values())
            )


class AnnalistProfileView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist user profile URI
    """
    def __init__(self):
        super(AnnalistProfileView, self).__init__()
        return

    # GET

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata):
        template = loader.get_template('annalist_profile.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        def resultdata():
            return { 'user': request.user }
        return (
            self.authenticate() or 
            self.render_html(resultdata()) or 
            self.error(self.error406values())
            )

# End.



