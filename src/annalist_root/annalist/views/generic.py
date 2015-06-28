"""
Annalist generic view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
# import json
# import random
# import uuid
# import copy
# import httplib2

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
from annalist                       import util
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.models.site           import Site
from annalist.models.annalistuser   import AnnalistUser

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
        self._user_perms  = None
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

    def continuation_next(self, request_dict={}, default_cont=None):
        """
        Returns a continuation URL to be used when returning from the current view,
        or the supplied default if no continuation is specified for the current view.
        """
        return request_dict.get("continuation_url") or default_cont or None

    def continuation_here(self, request_dict={}, default_cont="", base_here=None):
        """
        Returns a URL that returns control to the current page, to be passed as a
        contionuation_uri parameter to any subsidiary pages invoked.  Such continuation 
        URIs are cascaded, so that the return URI includes a the `continuation_url` 
        for the current page.

        request_dict    is a request dictionary that is expected to contain a 
                        to continuation_url value to use, and other parameters to 
                        be included an any continuation back to the current page.
        default_cont    is a default continuation URI to be used for returning from 
                        the current page if the current POST request does not specify
                        a continuation_url query parameter.
        base_here       if specified, overrides the current request path as the base URI
                        to be used to return to the currently displayed page (e.g. when
                        current request URI is non-idempotent, such as creating a new 
                        entity).
        """
        # Note: use default if request/form parameter is present but blank:
        if not base_here:
            base_here = self.get_request_path()
        continuation_next = self.continuation_next(request_dict, default_cont)
        return uri_with_params(base_here, 
            continuation_params({"continuation_url": continuation_next}, request_dict)
            )

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

    def check_site_data(self):
        """
        Check that site data is present and accessible.  If not, return an HTTP error
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

    def check_value_supplied(self, val, msg, continuation_url=None, testfn=(lambda v: v)):
        """
        Test if a supplied value is specified (not None) and passes a supplied test,
        returning a URI to display a supplied error message if the test fails.

        NOTE: this function works with the generic base template base_generic.html, which
        is assumed to provide an underlay for the currently viewed page.

        val                 value that is required to be not None and not empty or False
        msg                 message to display if the value evaluated to False
        continuation_url    a continuation URL for the resdiplayed page.
        testfn              is a function to test the value (if not None).  If not specified, 
                            the default test checks that the value does not evaluate as false
                            (e.g. is a non-empty string, list or collection).

        returns a URI string for use with HttpResponseRedirect to redisplay the 
        current page with the supplied message, or None if the value passes the test.
        """
        redirect_uri = None
        continuation_url_dict = {}
        if continuation_url:
            continuation_url_dict = {'continuation_url': continuation_url}
        if (val is None) or not testfn(val):
            redirect_uri = uri_with_params(
                self.get_request_path(), 
                self.error_params(msg),
                continuation_url_dict
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

    def get_user_identity(self):
        """
        returns the username and authenticated URI for the user making the 
        current request, as a pair (username, URI)
        """
        user = self.request.user
        if user.is_authenticated():
            return (user.username, "mailto:"+user.email)
        return ("_unknown_user_perms", "annal:User/_unknown_user_perms")

    def get_user_permissions(self, collection, user_id, user_uri):
        """
        Get a user permissions record (AnnalistUser).

        To return a value, both the user_id and the user_uri (typically a mailto: URI, but
        may be any *authenticated* identifier) must match.  This is to prevent access to 
        records of a deleted account being granted to a new account created with the 
        same user_id (username).

        This function returns default permissions if the user details supplied cannot be matched.

        Permissions are cached in the view object so that tghe prmissions ecord is read at 
        most once for any HTTP request. 

        collection      the collection for which permissions are required.
        user_id         local identifier for the type to retrieve.
        user_uri        authenticated identifier associated with the user_id.  That is,
                        the authentication service used is presumed to confirm that
                        the identifier belongs to the user currently logged in with
                        the supplied username.

        returns an AnnalistUser object containing permissions for the identified user.
        """
        if not self._user_perms:
            # if collection:
            #     log.info("user_id %s (%s), coll_id %s, %r"%
            #         (user_id, user_uri, collection.get_id(), collection.get_user_permissions(user_id, user_uri))
            #         )
            user_perms = (
                (collection and collection.get_user_permissions(user_id, user_uri)) or
                self.site().get_user_permissions(user_id, user_uri) or
                self.site().get_user_permissions("_default_user_perms", "annal:User/_default_user_perms")
                )
            self._user_perms = user_perms
            log.debug("get_user_permissions %r"%(self._user_perms,))
        return self._user_perms

    def get_permissions(self, collection):
        """
        Get permissions for the current user
        """
        user_id, user_uri = self.get_user_identity()
        return self.get_user_permissions(collection, user_id, user_uri)

    def authorize(self, scope, collection):
        """
        Return None if user is authorized to perform the requested operation,
        otherwise appropriate 401 Authorization Required or 403 Forbidden response.
        May be called with or without an authenticated user.

        scope       indication of the operation  requested to be performed.
                    e.g. "VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", ...
        collection  is the collection to which the requested action is directed,
                    or None if the test is against site-level permissions.
        """
        user_id, user_uri = self.get_user_identity()
        coll_id = collection.get_id() if collection else "(site)"
        if not util.valid_id(user_id):
            log.warning("Invalid user_id %s, URI %s"%(user_id, user_uri))
            message="Bad request to %(request_uri)s: invalid user_id: '"+user_id+"'"
            return self.error(self.error400values(message=message))
        user_perms = self.get_user_permissions(collection, user_id, user_uri)
        if not user_perms:
            log.warning("No user permissions found for user_id %s, URI %s"%(user_id, user_uri))
            return self.error(self.error403values(scope=scope))
        # log.info("Authorize %s in %s, %s, %r"%(user_id, coll_id, scope, user_perms[ANNAL.CURIE.user_permissions]))
        # user_perms is an AnnalistrUser object
        coll_id = collection.get_id() if collection else "(No coll)"
        if scope not in user_perms[ANNAL.CURIE.user_permissions]:
            if user_id == "_unknown_user_perms":
                err = self.error401values(scope=scope)
            else:
                err = self.error403values(scope=scope)
            return self.error(err)
        return None

    def form_action_auth(self, action, auth_collection, perm_required):
        """
        Check that the requested form action is authorized for the current user.

        action          is the requested action: new, edit, copy, etc.
        auth_collection is the collection to which the requested action is directed,
                        or None if the test is against site-level permissions
                        (which should be stricter than all collections).
        perm_required   is a data dependent dictionary that maps from action to
                        permissions required to perform the action.  The structure
                        is similar to that of 'action_scope' (below) that provides
                        a fallback mapping.

        Returns None if the desired action is authorized for the current user, otherwise
        an HTTP response value to return an error condition.
        """
        # @@TODO: in due course, eliminate action_scope.
        action_scope = (
            { "view":   "VIEW"      # View data record
            , "list":   "VIEW"      # ..
            , "search": "VIEW"      # ..
            , "new":    "CREATE"    # Create data record
            , "copy":   "CREATE"    # ..
            , "edit":   "UPDATE"    # Update data record
            , "delete": "DELETE"    # Delete datra record
            , "config": "CONFIG"    # Change collection configuration
            , "admin":  "ADMIN"     # Change users or permissions
            })
        if action in perm_required:
            auth_scope = perm_required[action]
        elif action in action_scope:
            auth_scope = action_scope[action]
        else:
            log.warning("form_action_auth: unknown action: %s"%(action))
            auth_scope = "UNKNOWN"
        # return self.authorize(auth_scope, auth_resource)
        return self.authorize(auth_scope, auth_collection)

    # Entity access

    def get_entity(self, entity_id, typeinfo, action):
        """
        Create local entity object or load values from existing.

        entity_id       entity id to create or load
        typeinfo        EntityTypeInfo object for the entity
        action          is the requested action: new, edit, copy, view

        returns an object of the appropriate type.

        If an existing entity is accessed, values are read from storage, 
        otherwise a new entity object is created but not yet saved.
        """
        # log.info(
        #     "get_entity id %s, parent %s, action %s, altparent %s"%
        #     (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
        #     )
        entity = typeinfo.get_entity(entity_id, action)
        if entity is None:
            parent_id    = typeinfo.entityparent.get_id()
            altparent_id = (
                typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent 
                else "(none)"
                )
            log.debug(
                "Entity not found: parent %s, altparent %s, entity_id %s"%
                (parent_id, altparent_id, entity_id)
                )
        return entity

    # HTML rendering

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
        # log.debug("render_html - data: %r"%(resultdata))
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
