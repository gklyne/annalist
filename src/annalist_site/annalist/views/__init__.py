"""
Annalist view definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import json
import random
import logging
import uuid
import copy

import httplib2

# Needed when importing django.views.generic - default to development settings
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'annalist_site.settings.devel'

import logging
log = logging.getLogger(__name__)

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import RequestContext, loader
from django.views                   import generic
from django.views.decorators.csrf   import csrf_exempt
from django.core.urlresolvers       import resolve, reverse

from django.conf import settings

import oauth2.views

from utils.ContentNegotiationView   import ContentNegotiationView

from annalist                       import message
from annalist                       import layout
from annalist.site                  import Site

LOGIN_URIS = None

# Create your views here.

class AnnalistGenericView(ContentNegotiationView):
    """
    Common base class for Annalist views
    """

    def __init__(self):
        super(AnnalistGenericView, self).__init__()
        self._sitebaseuri = reverse("AnnalistHomeView") 
        self._sitebasedir = os.path.join(settings.BASE_DATA_DIR, layout.SITE_DIR)
        self._site        = None
        self._site_data   = None
        ## self.credential = None
        return

    def site(self):
        if not self._site:
            self._site = Site(self._sitebaseuri, self._sitebasedir)
        return self._site

    def site_data(self):
        if not self._site_data:
            self._site_data = self.site().site_data()
        return self._site_data

    def error(self, values):
        """
        Construct HTTP error response.

        This is an application-specific override of a method defined 
        in ContentNegotiationView.
        """
        template = loader.get_template('annalist_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'], reason=values['reason'])

    def redirect_info(self, viewname, info_message=None, info_head=message.ACTION_COMPLETED):
        """
        Redirect to a specified view with an information/confirmation message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = reverse(viewname)+"?info_head=%s&info_message=%s"%(info_head, info_message)
        return HttpResponseRedirect(redirect_uri)

    def error_params(self, error_message, error_head=message.INPUT_ERROR):
        """
        Returns a URI query parameter string with details that are used to generate an
        error message.
        """
        return "?error_head=%s&error_message=%s"%(error_head, error_message)

    def redirect_error(self, viewname, error_message=None, error_head=message.INPUT_ERROR):
        """
        Redirect to a specified view with an error message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = reverse(viewname)+self.error_params(error_head, error_message)
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
        otherwise appropriate 401 Authorization Required or 403 Forbidden response.
        May be called with or without an authenticated user.

        scope       indication of the operation  requested to be performed.
                    e.g. "VIEW", "CREATE", "UPDATE", "DELETE", ...

        @@TODO proper authorization framework

        For now, require authentication for anything other than VIEW scope.
        """
        if scope != "VIEW":
            if not self.request.user.is_authenticated():
                return self.error(self.error401values())
        return None

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata, template_name):
        """
        Construct an HTML response based on supplied data and template name.

        Also contains logic to interpolate message values from the incoming URI,
        for error and confirmation message displays.  These additional message
        displays are commonly handled by the "base_generic.html" underlay template.
        """
        resultdata["info_head"]     = self.request.GET.get("info_head",      message.ACTION_COMPLETED) 
        resultdata["info_message"]  = self.request.GET.get("info_message",   None)
        resultdata["error_head"]    = self.request.GET.get("error_head",     message.INPUT_ERROR) 
        resultdata["error_message"] = self.request.GET.get("error_message",  None)
        resultdata["auth_create"]   = self.authorize("CREATE") is None
        resultdata["auth_update"]   = self.authorize("UPDATE") is None
        resultdata["auth_delete"]   = self.authorize("DELETE") is None
        template  = loader.get_template(template_name)
        context   = RequestContext(self.request, resultdata)
        log.debug("render_html - data: %r"%(resultdata))
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
