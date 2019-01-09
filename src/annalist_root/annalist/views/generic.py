"""
Annalist generic view definition
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import os.path
import json
import markdown
import traceback

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import loader
from django.views                   import generic
from django.views.decorators.csrf   import csrf_exempt
from django.core.urlresolvers       import resolve, reverse
from django.conf                    import settings

import login.login_views

from utils.py3porting               import urljoin
from utils.ContentNegotiationView   import ContentNegotiationView

import annalist
from annalist                       import message
from annalist                       import layout
from annalist                       import util
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.models.site           import Site
from annalist.models.annalistuser   import (
    AnnalistUser, 
    site_default_user_id, site_default_user_uri, 
    default_user_id, default_user_uri, 
    unknown_user_id, unknown_user_uri
    )

from annalist.views.uri_builder     import uri_with_params, continuation_params, uri_params

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
        self._sitebaseuri      = reverse("AnnalistHomeView")
        # self._sitebasedir      = os.path.join(settings.BASE_DATA_DIR, layout.SITE_DIR)
        self._sitebasedir      = settings.BASE_SITE_DIR
        self._site             = None
        self._site_data        = None
        self._user_perms       = {}
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

    def error(self, values, continuation_url=None):
        """
        Construct HTTP error response.

        This is an application-specific override of a method defined 
        in ContentNegotiationView.

        values      is a dictionary of values to be passed as a context to the
                    error display page.  Typically, this contains more details
                    about the error (cf. ContentNegotiationView.errorvalues)
        continutation_url
                    is a URL to (re)display when any error is dismissed or has 
                    otherwise been handled.
        """
        # log.info(
        #     "AnnalistGenericView.error: values %r, continuation_url %s"%(values, continuation_url)
        #     )
        template = loader.get_template('annalist_error.html')
        context = dict(values)
        if continuation_url:
            context['continuation_url']   = continuation_url
            context['continuation_param'] = uri_params({ 'continuation_url': continuation_url })
        return HttpResponse(template.render(context), status=values['status'], reason=values['reason'])

    def view_uri(self, viewname, **kwargs):
        """
        Return view URI given view name and any additional arguments
        """
        return reverse(viewname, kwargs=kwargs)

    def get_collection_view_url(self, coll_id):
        """
        Return view (root) URL for specified collection
        """
        return self.view_uri(
            "AnnalistCollectionView", 
            coll_id=coll_id
            )

    def get_site_base_url(self):
        """
        Return base URL for current site
        """
        return self.view_uri("AnnalistHomeView")

    def get_collection_base_url(self, coll_id):
        """
        Return base URL for specified collection
        """
        return urljoin(self.get_collection_view_url(coll_id), layout.COLL_BASE_REF)

    def get_entity_base_url(self, coll_id, type_id, entity_id):
        """
        Return base URL for specified entity
        """
        return self.view_uri(
            "AnnalistEntityAccessView", 
            coll_id=coll_id, type_id=type_id, entity_id=entity_id
            )

    def get_list_base_url(self, coll_id, type_id, list_id):
        """
        Return base URL for specified list, which is one of:

            .../coll_id/d/
            .../coll_id/d/type_id/
            .../coll_id/l/list_id/
            .../coll_id/l/list_id/type_id/
        """
        if list_id is None:
            if type_id is None:
                list_url = self.view_uri(
                    "AnnalistEntityDefaultListAll", 
                    coll_id=coll_id
                    )
            else:
                list_url = self.view_uri(
                    "AnnalistEntityDefaultListType", 
                    coll_id=coll_id, type_id=type_id
                    )
        else:
            list_url = self.view_uri(
                "AnnalistEntityGenericList", 
                coll_id=coll_id, list_id=list_id, type_id=type_id
                )
        return list_url

    def resource_response(self, resource_file, resource_type, links={}):
        """
        Construct response containing body of referenced resource (or list),
        with supplied resource_type as its content_type
        """
        # @@TODO: assumes response can reasonably be held in memory;
        #         consider 'StreamingHttpResponse'?
        response = HttpResponse(content_type=resource_type)
        response = self.add_link_header(response, links)
        response.write(resource_file.read())
        return response

    def continuation_next(self, request_dict={}, default_cont=None):
        """
        Returns a continuation URL to be used when returning from the current view,
        or the supplied default if no continuation is specified for the current view.
        """
        return request_dict.get("continuation_url") or default_cont or None

    def continuation_here(self, request_dict={}, default_cont="", base_here=None):
        """
        Returns a URL that returns control to the current page, to be passed as a
        continuation_uri parameter to any subsidiary pages invoked.  Such continuation 
        URIs are cascaded, so that the return URI includes a the `continuation_url` 
        for the current page.

        request_dict    is a request dictionary that is expected to contain the 
                        continuation_url value to use, and other parameters to 
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

    def redirect_error(self, 
        viewuri, view_params={}, error_message=None, error_head=message.INPUT_ERROR
        ):
        """
        Redirect to a specified view with an error message for display

        (see templates/base_generic.html for display details)
        """
        redirect_uri = uri_with_params(
            viewuri, view_params, self.error_params(error_message, error_head=error_head)
            )
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

    # Authentication and authorization
    def authenticate(self, continuation_url):
        """
        Return None if required authentication is present, otherwise
        an appropriate login redirection response.

        continuation_url    is a URL that to be retrieved and processed 
                            when the authentication process completes
                            (or is aborted).

        self.credential is set to credential that can be used to access resource
        """
        # Cache copy of URIs to use with login
        global LOGIN_URIS
        if LOGIN_URIS is None:
            LOGIN_URIS = (
                { "login_form_url":     self.view_uri('LoginUserView')
                , "login_post_url":     self.view_uri('LoginPostView')
                , "login_done_url":     self.view_uri('OIDC_AuthDoneView')
                , "user_profile_url":   self.view_uri('AnnalistProfileView')
                })
        return login.login_views.confirm_authentication(self, 
            continuation_url=continuation_url,
            **LOGIN_URIS
            )

    def get_user_identity(self):
        """
        returns the username and authenticated URI for the user making the 
        current request, as a pair (username, URI)
        """
        user = self.request.user
        if user.is_authenticated:
            return (user.username, "mailto:"+user.email)
        return ("_unknown_user_perms", "annal:User/_unknown_user_perms")

    def get_user_permissions(self, collection, user_id, user_uri):
        """
        Get a user permissions record (AnnalistUser).

        To return a value, both the user_id and the user_uri (typically a mailto: URI, but
        may be any *authenticated* identifier) must match.  This is to prevent access to 
        records of a deleted account being granted to a new account created with the 
        same user_id (username).

        This function includes any collection- or site- default permissions in the 
        set of permissions returned.

        Permissions are cached in the view object so that the permissions record is read at 
        most once for any HTTP request. 

        collection      the collection for which permissions are required.
        user_id         local identifier for the user permnissions to retrieve.
        user_uri        authenticated identifier associated with the user_id.  That is,
                        the authentication service used is presumed to confirm that
                        the identifier belongs to the user currently logged in with
                        the supplied username.

        returns an AnnalistUser object containing permissions for the identified user.
        """
        coll_id = collection.get_id() if collection else layout.SITEDATA_ID
        if coll_id not in self._user_perms:
            # if collection:
            #     log.info("user_id %s (%s), coll_id %s, %r"%
            #         (user_id, user_uri, collection.get_id(), collection.get_user_permissions(user_id, user_uri))
            #         )
            parentcoll = collection or self.site()
            if user_id == unknown_user_id:
                # Don't apply collection default-user permissions if no authenticated user
                user_perms = parentcoll.get_user_permissions(unknown_user_id, unknown_user_uri)
            else:
                # Combine user permissions with default-user permissions for collection
                default_perms = parentcoll.get_user_permissions(site_default_user_id, default_user_uri)
                if not default_perms:
                    default_perms = parentcoll.get_user_permissions(default_user_id, default_user_uri)
                user_perms    = parentcoll.get_user_permissions(user_id, user_uri) or default_perms
                user_perms[ANNAL.CURIE.user_permission] = list(
                    set(user_perms[ANNAL.CURIE.user_permission]) | 
                    set(default_perms[ANNAL.CURIE.user_permission])
                    ) 
            self._user_perms[coll_id] = user_perms
            # log.debug("get_user_permissions %r"%(self._user_perms,))
        return self._user_perms[coll_id]

    def get_permissions(self, collection):
        """
        Get permissions for the current user
        """
        user_id, user_uri = self.get_user_identity()
        return self.get_user_permissions(collection, user_id, user_uri)

    def get_message_data(self):
        """
        Returns a dictionary of message data that can be passed inthe request parameters
        to be displayed on a different page.
        """
        messagedata = {}
        def uri_param_val(msg_name, hdr_name, hdr_default):
            """
            Incorporate values from the incoming URI into the message data.
            """
            message = self.request.GET.get(msg_name, None)
            if message:
                messagedata[msg_name] = message
                messagedata[hdr_name] = self.request.GET.get(hdr_name, hdr_default)
            return
        uri_param_val("info_message",  "info_head",  message.ACTION_COMPLETED)
        uri_param_val("error_message", "error_head", message.INPUT_ERROR) 
        return messagedata

    def authorize(self, scope, collection, continuation_url=None):
        """
        Return None if user is authorized to perform the requested operation,
        otherwise appropriate 401 Authorization Required or 403 Forbidden response.
        May be called with or without an authenticated user.

        scope       indication of the operation  requested to be performed.
                    e.g. "VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", ...
        collection  is the collection to which the requested action is directed,
                    or None if the test is against site-level permissions.
        continutation_url
                    is a URL to (re)display when any error is dismissed or has 
                    otherwise been handled.
        """
        user_id, user_uri = self.get_user_identity()
        coll_id = collection.get_id() if collection else "(site)"
        if not util.valid_id(user_id):
            log.warning("Invalid user_id %s, URI %s"%(user_id, user_uri))
            message="Bad request to %(request_uri)s: invalid user_id: '"+user_id+"'"
            return self.error(self.error400values(message=message), continuation_url=continuation_url)
        user_perms = self.get_user_permissions(collection, user_id, user_uri)
        if not user_perms:
            log.warning("No user permissions found for user_id %s, URI %s"%(user_id, user_uri))
            log.warning("".join(traceback.format_stack()))
            return self.error(self.error403values(scope=scope), continuation_url=continuation_url)
        # log.info("Authorize %s in %s, %s, %r"%(user_id, coll_id, scope, user_perms[ANNAL.CURIE.user_permission]))
        # user_perms is an AnnalistUser object
        coll_id = collection.get_id() if collection else "(No coll)"
        if scope not in user_perms[ANNAL.CURIE.user_permission]:
            if user_id == unknown_user_id:
                err = self.error401values(scope=scope)
            else:
                err = self.error403values(scope=scope)
            return self.error(err, continuation_url=continuation_url)
        return None

    def form_action_auth(self, action, auth_collection, perm_required, continuation_url=None):
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
        continutation_url
                        is a URL to (re)display when any error is dismissed or has 
                        otherwise been handled.

        Returns None if the desired action is authorized for the current user, otherwise
        an HTTP response value to return an error condition.
        """
        if action in perm_required:
            auth_scope = perm_required[action]
        else:
            log.warning("form_action_auth: unknown action: %s"%(action))
            log.warning("perm_required: %r"%(perm_required,))
            auth_scope = "UNKNOWN"
        return self.authorize(auth_scope, auth_collection, continuation_url=continuation_url)

    # Entity access

    def get_entity(self, entity_id, typeinfo, action):
        """
        Create local entity object or load values from existing.

        entity_id       entity id to create or load
        typeinfo        EntityTypeInfo object for the entity
        action          is the requested action: new, edit, copy, view

        Returns an object of the appropriate type.

        If an existing entity is accessed, values are read from storage, 

        If the identified entity does not exist and `action` is "new" then 
        a new entity is initialized (but not saved), otherwise the entity 
        value returned is None.
        """
        # log.info(
        #     "AnnalistGenericView.get_entity id %s, parent %s, action %s, altparent %s"%
        #     (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
        #     )
        entity = typeinfo.get_entity(entity_id, action)
        if entity is None:
            # Log diagnostics for missing entity
            parent_id    = typeinfo.entityparent.get_id()
            altparent_id = (
                typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent 
                else "(none)"
                )
            log.info(
                "AnnalistGenericView.get_entity id %s, parent %s, action %s, altparent %s"%
                (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
                )
            log.info(
                "Entity not found: parent %s, altparent %s, entity_id %s"%
                (parent_id, altparent_id, entity_id)
                )
        return entity

    # HTML rendering

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata, template_name, links=[]):
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
        if 'help_markdown' in resultdata:
            resultdata['help_text'] = markdown.markdown(resultdata['help_markdown'])
        template = loader.get_template(template_name)
        context  = resultdata
        # log.debug("render_html - data: %r"%(resultdata))
        response = HttpResponse(template.render(context, request=self.request))
        if "entity_data_ref" in resultdata:
            alt_link = [ { "ref": resultdata["entity_data_ref"], "rel": "alternate" } ]
        else:
            alt_link = []
        response = self.add_link_header(response, links=alt_link+links)
        return response

    # JSON and Turtle content negotiation and redirection

    @ContentNegotiationView.accept_types(["application/json", "application/ld+json"])
    def redirect_json(self, jsonref, links=[]):
        """
        Construct a redirect response to access JSON data at the designated URL.

        jsonref     is the URL from which JSON data may be retrieved.
        links       is an optional array of link values to be added to the HTTP response
                    (see method add_link_header for description).

        Returns an HTTP redirect response object if the current request is for JSON data,
        otherwise None.
        """
        response = HttpResponseRedirect(jsonref)
        response = self.add_link_header(response, links=links)
        return response

    @ContentNegotiationView.accept_types(["text/turtle", "application/x-turtle", "text/n3"])
    def redirect_turtle(self, turtleref, links=[]):
        """
        Construct a redirect response to access Turtle data at the designated URL.

        turtleref   is the URL from which Turtle data may be retrieved.
        links       is an optional array of link values to be added to the HTTP response
                    (see method add_link_header for description).

        Returns an HTTP redirect response object if the current request is for Turtle data,
        otherwise None.
        """
        response = HttpResponseRedirect(turtleref)
        response = self.add_link_header(response, links=links)
        return response

    def add_link_header(self, response, links=[]):
        """
        Add HTTP link header to response, and return the updated response.

        response    response to be returned
        links       is an optional array of link valuyes to be added to the HTTP response, 
                    where each link is specified as:
                      { "rel": <relation-type>
                      , "ref": <target-url>
                      }
        """
        link_headers = []
        for l in links:
            link_headers.append('''<%(ref)s>; rel="%(rel)s"'''%l)
        if len(link_headers) > 0:
            response["Link"] = ",".join(link_headers)
        return response

    # Default view methods return 405 Forbidden

    def get(self, request, *args, **kwargs):
        return self.error(self.error405values())

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.error(self.error405values())

    def post(self, request, *args, **kwargs):
        return self.error(self.error405values())

    def delete(self, request, *args, **kwargs):
        return self.error(self.error405values())


# End.
