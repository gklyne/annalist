"""
Annalist generic view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import json
import random
import uuid
import copy

import httplib2

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
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

LOGIN_URIS = None

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

    def collection(self, coll_id):
        return Collection(self.site(), coll_id)

    def recordtype(self, coll_id, type_id):
        return RecordType(self.collection(coll_id), type_id)

    def recordtypedata(self, coll_id, type_id):
        return RecordTypeData(self.collection(coll_id), type_id)

    def error(self, values):
        """
        Construct HTTP error response.

        This is an application-specific override of a method defined 
        in ContentNegotiationView.
        """
        template = loader.get_template('annalist_error.html')
        context  = RequestContext(self.request, values)
        return HttpResponse(template.render(context), status=values['status'], reason=values['reason'])

    def view_uri(self, viewname, **kwargs):
        """
        Return view URI given view name and any additional arguments
        """
        return reverse(viewname, kwargs=kwargs)

    def info_params(self, info_message, info_head=message.ACTION_COMPLETED):
        """
        Returns a URI query parameter string with details that are used to generate an
        information message.
        """
        return "?info_head=%s&info_message=%s"%(info_head, info_message)

    def redirect_info(self, viewuri, info_message=None, info_head=message.ACTION_COMPLETED):
        """
        Redirect to a specified view with an information/confirmation message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = viewuri+self.info_params(info_message, info_head)
        return HttpResponseRedirect(redirect_uri)

    def error_params(self, error_message, error_head=message.INPUT_ERROR):
        """
        Returns a URI query parameter string with details that are used to generate an
        error message.
        """
        return "?error_head=%s&error_message=%s"%(error_head, error_message)

    def redirect_error(self, viewuri, error_message=None, error_head=message.INPUT_ERROR):
        """
        Redirect to a specified view with an error message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = viewuri+self.error_params(error_head, error_message)
        return HttpResponseRedirect(redirect_uri)

    def check_value_supplied(self, val, msg, testfn=(lambda v: v)):
        """
        Test a supplied value is specified (not None) and passes a supplied test,
        returning a URI to display a supplied error message if the test fails.

        NOTE: this function works with the generic base template base_generic.html, which
        is assumed to provide an underlay for thne currently viewed page.

        val         value that is required to be not None and not empty or False
        msg         message to display if the value evaluated to False
        testfn      is a function to test the value (if not None).  If not specified, 
                    the default test checks thatthe value does not evaluate as false
                    (e.g. is a non-empty string, list or collection).

        returns a URI string for use with HttpResponseRedirect to redisplay the 
        current page with the supplied message, or None if the value passes the test.
        """
        redirect_uri = None
        if (val is None) or not testfn(val):
            redirect_uri = (
                self.get_request_path()+
                self.error_params(msg)
                )
        return redirect_uri

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
                { "login_form_uri": self.view_uri('LoginUserView')
                , "login_post_uri": self.view_uri('LoginPostView')
                , "login_done_uri": self.view_uri('LoginDoneView')
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

        @@TODO add resource parameter

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
        def uri_param_val(name, default):
            """
            Incorporate values from the incoming URI into the result data, if not already defined.
            """
            if name not in resultdata:
                resultdata[name] = self.request.GET.get(name, default)
            return
        uri_param_val("info_head",       message.ACTION_COMPLETED)
        uri_param_val("info_message",    None)
        uri_param_val("error_head",      message.INPUT_ERROR) 
        uri_param_val("error_message",   None)
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


# End.
