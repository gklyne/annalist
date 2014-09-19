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

import annalist
from annalist                       import message
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData
from annalist.models.entitytypeinfo import EntityTypeInfo

from annalist.views.uri_builder     import uri_with_params, continuation_params

#   -------------------------------------------------------------------------------------------
#
#   Utility methods and data
#
#   -------------------------------------------------------------------------------------------

LOGIN_URIS = None   # Populated by first call of `authenticate`

#   -------------------------------------------------------------------------------------------
#
#   Generic Annalist view (contains logic applicable to all pages)
#
#   -------------------------------------------------------------------------------------------

# @@TODO:   refactor this class out of existence?  Or at least dramatically slimmed.
#           Focus content on message display and auth* functions.
#           There is logic here that really belongs in view- or list- classes.
#           Maybe move logic when hand-coded pasges are replaced with data-driven pages.

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

    # @@TODO: make host parameter required in the following?

    def site(self, host=""):
        if not self._site:
            self._site = Site(self._sitebaseuri, self._sitebasedir, host=host)
        return self._site

    def site_data(self, host=""):
        if not self._site_data:
            self._site_data = self.site(host=host).site_data()
        if not self._site_data:
            log.error("views.generic.site_data: failed to load site data (%s)"%
                      self.site(host=host)._dir_path_uri()[1])
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

    def view_uri(self, viewname, **kwargs):
        """
        Return view URI given view name and any additional arguments
        """
        return reverse(viewname, kwargs=kwargs)

    def continuation_urls(self, request_dict, default_cont, base_here=None):
        """
        Returns a tuple of two continuation URI dictionary values:

        [0] { 'continuation_url': continuation_next }
        [1] { 'continuation_url': continuation_here }

        where:

        `continuation_next` is the URI to use after the current page has completed
        processing, which is either supplied as a parameter to the current page or 
        set to an indicated default.

        `continuation_here` is a URI that returns control to the current page, to be passed
        as a contionuation_uri parameter to any subsidiary pages invoked.  Such continuation 
        URIs are cascaded, so that the return URI includes a the `continuation_url` for the 
        current page.

        request_dict    is a request dictionary that is expected to contain a 
                        to continuation_url value to use, other parameters to be 
                        included an any continuation back to the current page.
        default_cont    is a default continuation URI to be used for returning from 
                        the current page if the current POST request does not specify
                        a continuation_url query parameter.
        base_here       if specified, overrides the current request path as the base URI
                        to be used to return to the currently displayed page (e.g. when
                        current request URI is non-idempotent, such as creating a new 
                        entity).
        """
        # Note: use default if request/form parameter is present but blank:
        continuation_url    = request_dict.get("continuation_url") or default_cont or None
        if not base_here:
            base_here = self.get_request_path()
        if continuation_url:
            continuation_next = { "continuation_url": continuation_url }
        else:
            continuation_next = {}
        continuation_here = uri_with_params(base_here, 
            continuation_params(continuation_next, request_dict.dict())
            )
        # continuation_here   = uri_with_continuation_params(
        #     base_here, continuation_next, request_dict.dict()
        #     )
        return (continuation_next, {"continuation_url": continuation_here})

    def info_params(self, info_message, info_head=message.ACTION_COMPLETED):
        """
        Returns a URI query parameter dictionary with details that are used to generate an
        information message.
        """
        return {"info_head": info_head, "info_message": info_message}

    def redirect_info(self, viewuri, view_params={}, info_message=None, info_head=message.ACTION_COMPLETED):
        """
        Redirect to a specified view with an information/confirmation message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = uri_with_params(viewuri, view_params, self.info_params(info_message, info_head))
        return HttpResponseRedirect(redirect_uri)

    def error_params(self, error_message, error_head=message.INPUT_ERROR):
        """
        Returns a URI query parameter string with details that are used to generate an
        error message.
        """
        return {"error_head": error_head, "error_message": error_message}

    def redirect_error(self, viewuri, view_params={}, error_message=None, error_head=message.INPUT_ERROR):
        """
        Redirect to a specified view with an error message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = uri_with_params(viewuri, view_params, self.error_params(error_head, error_message))
        return HttpResponseRedirect(redirect_uri)

    def form_action_auth(self, action, auth_resource):
        """
        Check that the requested form action is authorized for the current user.

        action          is the requested action: new, edit, copy, etc.
        auth_resource   is the resource URI to which the requested action is directed.
                        NOTE: This may be the URI of the parent of the resource
                        being accessed or manipulated.

        Returns None if the desired action is authorized for the current user, otherwise
        an HTTP response value to return an error condition.
        """
        action_scope = (
            { "view":   "VIEW"
            , "list":   "VIEW"
            , "search": "VIEW"
            , "new":    "CREATE"
            , "copy":   "CREATE"
            , "edit":   "UPDATE"
            , "delete": "DELETE"
            , "config": "CONFIG"
            , "admin":  "ADMIN"
            })
        if action in action_scope:
            auth_scope = action_scope[action]
        else:
            log.warning("form_action_auth: unknown action: %s"%(action))
            auth_scope = "UNKNOWN"
        # return self.authorize(auth_scope, auth_resource)
        return self.authorize(auth_scope)

    def check_site_data(self):
        """
        Check thaty site data is present and accessible.  If not, return an HTTP error
        response, otherwise None.
        """
        site_data = self.site_data()
        if not site_data:
            return self.error(
                self.errorvalues(500, "Internal server error", 
                    "Resource %(request_uri)s: Unable to load Annalist site data"
                    )
                )
        return None

    def check_value_supplied(self, val, msg, continuation_url={}, testfn=(lambda v: v)):
        """
        Test a supplied value is specified (not None) and passes a supplied test,
        returning a URI to display a supplied error message if the test fails.

        NOTE: this function works with the generic base template base_generic.html, which
        is assumed to provide an underlay for the currently viewed page.

        val         value that is required to be not None and not empty or False
        msg         message to display if the value evaluated to False
        testfn      is a function to test the value (if not None).  If not specified, 
                    the default test checks that the value does not evaluate as false
                    (e.g. is a non-empty string, list or collection).

        returns a URI string for use with HttpResponseRedirect to redisplay the 
        current page with the supplied message, or None if the value passes the test.
        """
        redirect_uri = None
        if (val is None) or not testfn(val):
            redirect_uri = uri_with_params(
                self.get_request_path(), 
                self.error_params(msg),
                continuation_url
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
            continuation_url=self.get_request_uri(),
            **LOGIN_URIS
            )

    def authorize(self, scope):
        """
        Return None if user is authorized to perform the requested operation,
        otherwise appropriate 401 Authorization Required or 403 Forbidden response.
        May be called with or without an authenticated user.

        scope       indication of the operation  requested to be performed.
                    e.g. "VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", ...

        @@TODO add resource parameter

        @@TODO proper authorization framework

        For now, require authentication for anything other than VIEW scope.
        """
        log.debug("Authorize %s"%(scope))
        if scope != "VIEW":
            if not self.request.user.is_authenticated():
                log.debug("Authorize %s denied"%(scope))
                return self.error(self.error401values(scope=scope))
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
        resultdata["auth_config"]   = self.authorize("CONFIG") is None
        resultdata["annalist_version"] = annalist.__version__
        if 'help_filename' in resultdata:
            help_filepath = os.path.join(
                settings.SITE_SRC_ROOT, 
                "annalist/views/help/%s.html"%resultdata['help_filename']
                )
            if os.path.isfile(help_filepath):
                with open(help_filepath, "r") as helpfile:
                    resultdata['help_text'] = helpfile.read()
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
