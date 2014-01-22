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
import copy

import logging
log = logging.getLogger(__name__)

import rdflib
import httplib2

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import RequestContext, loader
from django.views                   import generic
from django.views.decorators.csrf   import csrf_exempt
from django.core.urlresolvers       import resolve, reverse

from django.conf import settings

import oauth2.views

from utils.ContentNegotiationView import ContentNegotiationView
from annalist                     import message

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

    def redirect_error(self, viewname, error_message=None, error_head=message.INPUT_ERROR):
        """
        Redirect to a specified view with an error message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = reverse(viewname)+"?error_head=%s&error_message=%s"%(error_head, error_message)
        return HttpResponseRedirect(redirect_uri)

    def get_base_dir_zzz(self):
        """
        Utility function returns base directory for Annalist site,
        without trailing "/"
        """
        return settings.SITE_BASE

    # Authentication and authorization
    def authenticate(self):
        """
        Return None if required authentication is present, otherwise
        an appropriate login redirection response.

        self.credential is set to credential that can be used to access resource
        """
        # @@TODO: move logic to oauth2 app
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
        otherwise appropriate 403 Forbidden response.  May be called with or 
        without an authenticated user.

        scope       indication of the operation  requested to be performed.
                    e.g. "VIEW", "CREATE", "UPDATE", "DELETE", ...

        @@TODO interface details; scope at least will be needed.  

        For now, require authentication for anything other than VIEW scope.
        """
        if scope != "VIEW":
            if not self.request.user.is_authenticated():
                return self.error(self.error403values())
        return None

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata, template_name):
        resultdata["error_head"]    = self.request.GET.get("error_head",      message.INPUT_ERROR) 
        resultdata["error_message"] = self.request.GET.get("error_message",  None)
        template  = loader.get_template(template_name)
        context   = RequestContext(self.request, resultdata)
        log.info("render_html - data: %r"%(resultdata))
        return HttpResponse(template.render(context))

    # Default view methods return 405 Forbidden

    def get(self, request):
        return self.error(self.error405values())

    def head(self, request):
        return self.error(self.error405values())

    def put(self, request):
        return self.error(self.error405values())

    def post(self, request):
        return self.error(self.error405values())

    def delete(self, request):
        return self.error(self.error405values())

class AnnalistHomeView(AnnalistGenericView):
    """
    View class for home view
    """
    def __init__(self):
        super(AnnalistHomeView, self).__init__()
        return

    def get(self, request):
        return HttpResponseRedirect(reverse("AnnalistSiteView"))


# End.
