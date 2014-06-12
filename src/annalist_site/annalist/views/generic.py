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
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData
from annalist.views.entitytypeinfo  import EntityTypeInfo

#   -------------------------------------------------------------------------------------------
#
#   Utility methods and data
#
#   -------------------------------------------------------------------------------------------

LOGIN_URIS = None   # Populated by first call of `authenticate`

# ENTITY_MESSAGES = (
#     { 'parent_heading':         message.RECORD_TYPE_ID
#     , 'parent_missing':         message.RECORD_TYPE_NOT_EXISTS
#     , 'entity_heading':         message.ENTITY_DATA_ID
#     , 'entity_invalid_id':      message.ENTITY_DATA_ID_INVALID
#     , 'entity_exists':          message.ENTITY_DATA_EXISTS
#     , 'entity_not_exists':      message.ENTITY_DATA_NOT_EXISTS
#     , 'entity_type_heading':    message.ENTITY_TYPE_ID
#     , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
#     , 'entity_removed':         message.ENTITY_DATA_REMOVED
#     })

# TYPE_MESSAGES = (
#     { 'parent_heading':         message.COLLECTION_ID
#     , 'parent_missing':         message.COLLECTION_NOT_EXISTS
#     , 'entity_heading':         message.RECORD_TYPE_ID
#     , 'entity_invalid_id':      message.RECORD_TYPE_ID_INVALID
#     , 'entity_exists':          message.RECORD_TYPE_EXISTS
#     , 'entity_not_exists':      message.RECORD_TYPE_NOT_EXISTS
#     , 'entity_removed':         message.RECORD_TYPE_REMOVED
#     , 'entity_type_heading':    message.ENTITY_TYPE_ID
#     , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
#     })

# VIEW_MESSAGES = (
#     { 'parent_heading':         message.COLLECTION_ID
#     , 'parent_missing':         message.COLLECTION_NOT_EXISTS
#     , 'entity_heading':         message.RECORD_VIEW_ID
#     , 'entity_invalid_id':      message.RECORD_VIEW_ID_INVALID
#     , 'entity_exists':          message.RECORD_VIEW_EXISTS
#     , 'entity_not_exists':      message.RECORD_VIEW_NOT_EXISTS
#     , 'entity_removed':         message.RECORD_VIEW_REMOVED
#     , 'entity_type_heading':    message.ENTITY_TYPE_ID
#     , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
#     })

# LIST_MESSAGES = (
#     { 'parent_heading':         message.COLLECTION_ID
#     , 'parent_missing':         message.COLLECTION_NOT_EXISTS
#     , 'entity_heading':         message.RECORD_LIST_ID
#     , 'entity_invalid_id':      message.RECORD_LIST_ID_INVALID
#     , 'entity_exists':          message.RECORD_LIST_EXISTS
#     , 'entity_not_exists':      message.RECORD_LIST_NOT_EXISTS
#     , 'entity_removed':         message.RECORD_LIST_REMOVED
#     , 'entity_type_heading':    message.ENTITY_TYPE_ID
#     , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
#     })

# FIELD_MESSAGES = (
#     { 'parent_heading':         message.COLLECTION_ID
#     , 'parent_missing':         message.COLLECTION_NOT_EXISTS
#     , 'entity_heading':         message.RECORD_FIELD_ID
#     , 'entity_invalid_id':      message.RECORD_FIELD_ID_INVALID
#     , 'entity_exists':          message.RECORD_FIELD_EXISTS
#     , 'entity_not_exists':      message.RECORD_FIELD_NOT_EXISTS
#     , 'entity_removed':         message.RECORD_FIELD_REMOVED
#     , 'entity_type_heading':    message.ENTITY_TYPE_ID
#     , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
#     })

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
        return self._site_data

    def get_coll_data(self, coll_id, host=""):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        # Check collection
        if not Collection.exists(self.site(host=host), coll_id):
            return self.error(
                dict(self.error404values(), 
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        self.collection = Collection.load(self.site(host=host), coll_id)
        return None

    def get_type_data(self, type_id):
        """
        Check type identifiers, and set up objects for:
            self.entitytypeinfo

        Must be called after method 'get_coll_data' has returned.

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        if type_id:
            self.entitytypeinfo = EntityTypeInfo(self.site(), self.collection, type_id)
            if not self.entitytypeinfo.entityparent:
                log.warning("get_type_data: RecordType %s not found"%type_id)
                return self.error(
                    dict(self.error404values(),
                        message=message.RECORD_TYPE_NOT_EXISTS%(
                            {'id': type_id, 'coll_id': self.collection.get_id()})
                        )
                    )
        else:
            self.entitytypeinfo = None
        return None

    def get_view_data(self, view_id):
        if not RecordView.exists(self.collection, view_id, self.site()):
            log.warning("get_view_data: RecordView %s not found"%view_id)
            coll_id = self.collection.get_id()
            return self.error(
                dict(self.error404values(),
                    message=message.RECORD_VIEW_NOT_EXISTS%(view_id, coll_id)
                    )
                )
        self.recordview = RecordView.load(self.collection, view_id, self.site())
        log.debug("recordview %r"%(self.recordview.get_values()))
        return None

    def get_list_data(self, list_id):
        if not RecordList.exists(self.collection, list_id, self.site()):
            log.info("get_list_data: RecordList %s not found"%list_id)
            coll_id = self.collection.get_id()
            return self.error(
                dict(self.error404values(),
                    message=message.RECORD_LIST_NOT_EXISTS%(list_id, coll_id)
                    )
                )
        self.recordlist = RecordList.load(self.collection, list_id, self.site())
        log.debug("recordlist %r"%(self.recordlist.get_values()))
        return None

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

    def continuation_uris(self, request_dict, default_cont):
        """
        Returns a tuple of two continuation URI values:
        [0] a URI query parameter value passed forward for returning to the current page:
            this is intended to be appended to a bare URI (without query parameters) of
            any new page invocations.
        [1] a URI for continuation after the current page is complete, which can
            be returned as a redirect URI when processing of the current page is 
            complete.

        Continuation URIs are cascaded, so that the return URI includes the 
        continuation URI parameter for the current page.

        request_dict    is a request dictionary that is expected to contain a 
                        continuation_uri value to use
        default_cont    is a default continuation URI to be used for returning from 
                        the current page if the current POST request does not specify
                        a continuation_uri query parameter.
        """
        continuation_uri  = request_dict.get("continuation_uri", default_cont)
        continuation_prev = "%3Fcontinuation_uri=" + continuation_uri
        continuation_path = self.get_request_path().split("?", 1)[0] + continuation_prev
        continuation_here = "?continuation_uri=" + continuation_path
        return (continuation_here, continuation_uri)

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

    def form_edit_auth(self, action, auth_resource):
        """
        Check that the requested form action is authorized for the current user.

        action          is the requested action: new, edit, copy, etc.
        auth_resource   is the resource URI to which the requested action is directed.
                        NOTE: This may be the URI of the parent of the resource
                        being accessed or manipulated.
        """
        action_scope = (
            { "view":   "VIEW"
            , "list":   "VIEW"
            , "search": "VIEW"
            , "new":    "CREATE"
            , "copy":   "CREATE"
            , "edit":   "UPDATE"
            , "delete": "DELETE"
            , "config": "CONFIG"    # or UPDATE?
            , "admin":  "ADMIN"
            })
        if action in action_scope:
            auth_scope = action_scope[action]
        else:
            auth_scope = "UNKNOWN"
        # return self.authorize(auth_scope, auth_resource)
        return self.authorize(auth_scope)

    def check_value_supplied(self, val, msg, continuation_uri="", testfn=(lambda v: v)):
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
            redirect_uri = (
                self.get_request_path()+
                self.error_params(msg)
                ) + continuation_uri
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
