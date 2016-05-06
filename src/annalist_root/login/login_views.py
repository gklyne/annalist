"""
Login and authentication views and related authentication setup logic
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# @@TODO: define a view decorator to apply authentication requirement

import os
import re
import json
import markdown
import copy
import uuid
import urllib
from urlparse import urlparse, urljoin
from importlib import import_module

import logging
log = logging.getLogger(__name__)

from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from utils.http_errors import error400values

from login.auth_django_client   import django_flow_from_user_id
from auth_oidc_client           import (
    oauth2_flow_from_provider_details, oauth2_flow_to_dict, oauth2_get_state_token, 
    SCOPE_DEFAULT
    )
from login_utils                import HttpResponseRedirectWithQuery, HttpResponseRedirectLogin
from models                     import CredentialsModel, get_user_credential
import login_message

# Per-instance generated secret key for CSRF protection via OAuth2 state value.
# Regenerated each time this service is started.

PROVIDER_FILES = None

PROVIDER_DETAILS = None

settings = import_module(os.environ["DJANGO_SETTINGS_MODULE"])

def collect_provider_details():
    global PROVIDER_FILES, PROVIDER_DETAILS
    if PROVIDER_DETAILS is None:
        PROVIDER_DETAILS = {}
        PROVIDER_FILES   = {}
        clientsecrets_dirname = os.path.join(settings.CONFIG_BASE, "providers/")
        if os.path.isdir(clientsecrets_dirname):
            clientsecrets_files   = os.listdir(clientsecrets_dirname)
            for f in clientsecrets_files:
                if f.endswith(".json"):
                    p = os.path.join(clientsecrets_dirname,f)
                    j = json.load(open(p, "r"))
                    n = j['web']['provider']
                    PROVIDER_FILES[n]   = p
                    PROVIDER_DETAILS[n] = j['web']
                    if 'provider_label' not in PROVIDER_DETAILS[n]:
                        PROVIDER_DETAILS[n]['provider_label'] = n
    return

def _untested_authentication_required(
        login_form_url=None, login_post_url=None, login_done_url=None, 
        continuation_url=None):
    """
    Decorator for view handler function that activates authentication flow
    if the current request is not already associated with an authenticated user.
    """
    # @@NOTE: not tested; the mix of static and dynamic parameters required makes
    #         the in-line form easier to use than a decorator.
    def decorator(func):
        def guard(view, values):
            return (
                confirm_authentication(view, 
                    login_form_url, login_post_url, login_done_url, 
                    continuation_url)
            or
                func(view, values)
            )
        return guard
    return decorator

def confirm_authentication(view, 
        login_form_url=None, login_post_url=None, login_done_url=None, 
        user_profile_url=None, continuation_url=None, 
        help_path="annalist/views/help/"):
    """
    Return None if required authentication is present, otherwise
    a login redirection response to the supplied URI

    view.credential is set to credential that can be used to access resource

    Five URL parameters are passed in from the calling application:

    login_form_url      Page to gather information to initiate login process
    login_post_url      URL to which login information is posted
    login_done_url      URL retrieved with additional parameters when authentication
                        is complete (maybe failed). In the OAuth2 flow, this triggers
                        retrieval of user profile information.  Not used for local
                        authentication.
    user_profile_url    URL retrieved when user profile details have been set up.
    continuation_url    URL from which the login process was initiated.
    """
    if view.request.user.is_authenticated():
        view.credential = get_user_credential(view.request.user)
        # log.info("view.credential %r"%(view.credential,))
        if view.credential is not None:
            if not view.credential.invalid:
                return None         # Valid credential present: proceed...
        else:
            # Django login with local credential: check for user email address
            #
            # @@TODO: is this safe?
            # 
            # NOTE: currently, view.credential is provided by the oauth2 and used
            # only for the .invalid test above.  If it is ever used by other 
            # application components, it may be necessary to construct a
            # credential for local logins.  In the long run, if credentials will
            # be used to access third party services or resources, it may not be 
            # possible to use non-Oauth2 credentials here.  In the meanwhile,
            # allowing local Django user credentials provides an easier route for
            # getting a software instance installed for evaluation purposes.
            #
            if view.request.user.email:
                return None        # Assume valid login: proceed...
            else:
                return error400values(view, "Local user has no email address")
    if not login_form_url:
        return error400values(view, "No login form URI specified")
    if not login_done_url:
        return error400values(view, "No login completion URI specified")
    if not login_post_url:
        login_post_url = login_form_url
    if not continuation_url:
        continuation_url = view.request.path
    # Redirect to initiate login sequence 
    view.request.session['login_form_url']   = login_form_url
    view.request.session['login_post_url']   = login_post_url
    view.request.session['login_done_url']   = login_done_url
    view.request.session['user_profile_url'] = user_profile_url
    view.request.session['continuation_url'] = continuation_url
    view.request.session['help_dir']         = os.path.join(settings.SITE_SRC_ROOT, help_path)
    userid = view.request.POST.get("userid", 
        view.request.GET.get("userid",
            view.request.session.get('recent_userid', "")
            )
        ) 
    query_params = (
        { "userid":           userid
        , "continuation_url": continuation_url
        })
    query_params.update(view.get_message_data())
    return HttpResponseRedirectWithQuery(login_form_url, query_params)

class LoginUserView(generic.View):
    """
    View class to present login form to gather user id and other login information.

    The login page solicits a user id and an identity provider

    The login page supports the following request parameters:

    continuation_url={uri}
    - a URL for a page that is displayed when the login process is complete.
    """

    def get(self, request):
        collect_provider_details()
        # @@TODO: check PROVIDER_FILES, report error if none here
        # Retrieve request parameters
        continuation_url  = request.GET.get("continuation_url",     "/no-login-continuation/")
        # Check required values in session - if missing, restart sequence from original URI
        # This is intended to avoid problems if this view is invoked out of sequence
        login_post_url    = request.session.get("login_post_url",   None)
        login_done_url    = request.session.get("login_done_url",   None)
        user_profile_url  = request.session.get("user_profile_url", None)
        help_dir          = request.session.get("help_dir",         None)
        recent_userid     = request.session.get("recent_userid",    "")
        if ( (login_post_url is None) or 
             (login_done_url is None) or 
             (user_profile_url is None) or 
             (help_dir is None) ):
            log.warning(
                "LoginUserView: missing details "+
                "login_post_url %s, login_done_url %s, user_profile_url %s, help_dir %s"%
                (login_post_url, login_done_url, user_profile_url, help_dir)
                )
            return HttpResponseRedirect(continuation_url)
        # Display login form
        default_provider = ""
        provider_labels  = map( 
            lambda pair: pair[1], 
            sorted(
                [ ( p.get('provider_order', 5),
                    (k, p.get('provider_label', k), p.get('provider_image', None))
                  )
                    for k, p in PROVIDER_DETAILS.items()
                ])
            )
        for p in PROVIDER_DETAILS:
            if "default" in PROVIDER_DETAILS[p]:            
                default_provider = PROVIDER_DETAILS[p]["default"]
        logindata = (
            { "login_post_url":     login_post_url
            , "login_done_url":     login_done_url
            , "user_profile_url":   user_profile_url
            , "continuation_url":   continuation_url
            , "provider_keys":      PROVIDER_DETAILS.keys()
            , "provider_labels":    provider_labels
            , "provider":           default_provider
            , "suppress_user":      True
            , "help_filename":      "login-help"
            , "userid":             request.GET.get("userid", recent_userid)
            , "info_head":          request.GET.get("info_head", None)
            , "info_message":       request.GET.get("info_message", None)
            , "error_head":         request.GET.get("error_head", None)
            , "error_message":      request.GET.get("error_message", None)
            })
        # Load help text if available
        if "help_filename" in logindata:
            help_filepath = help_dir + "%(help_filename)s.md"%(logindata)
            if os.path.isfile(help_filepath):
                with open(help_filepath, "r") as helpfile:
                    logindata["help_markdown"] = helpfile.read()
        if "help_markdown" in logindata:
            logindata["help_text"] = markdown.markdown(logindata["help_markdown"])
        # Render form & return control to browser
        template = loader.get_template("login.html")
        context  = RequestContext(self.request, logindata)
        return HttpResponse(template.render(context))

class LoginPostView(generic.View):
    """
    View class to initiate an authentication flow, typically on  POST 
    of the login form.

    It saves the supplied user id in a session value, and redirects the user to the 
    identity provider, which in due course returns control to the application along 
    with a suitable authorization grant.

    The login form provides the following values:

    userid={string}
    - a user identifying string that will be associated with the external service
      login credentials.
    provider={string}
    - a string that identifies a provider selectred to perform authentication
      of the indicated user.  This string is an index to PROVIDER_FILES,
      which in turn contains filenames for client secrets to user when accessing
      the indicated identity provider.
    login_done={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
      Used to obtain user information following completion of authentication.
      Communicated via a hidden form value.
    user_profile_url={uri}
    - a URI that is retrieved, when user information has been obtained.  Expected use
      is to display user information, thenm continue tyo the page from which the
      login sequence was invoked.  Communicated via a hidden form value.
    continuation_url={uri}
    - URL of page from which logon sequence was invoked, and to which control is
      eventually returned.  Communicated via a hidden form value.
    """

    def post(self, request):
        # Retrieve request parameters
        userid            = request.POST.get("userid",            "")
        provider          = request.POST.get("provider",          "No_provider")
        provider          = request.POST.get("login",             provider)
        login_done_url    = request.POST.get("login_done_url",    "/no_login_done_url_in_form/")
        user_profile_url  = request.POST.get("user_profile_url",  "/no_user_profile_url_in_form/")
        continuation_url  = request.POST.get("continuation_url",  "/no_continuation_url_in_form/")
        if request.POST.get("login", None):
            collect_provider_details()
            provider_details      = PROVIDER_DETAILS[provider]
            provider_details_file = PROVIDER_FILES[provider]
            provider_mechanism    = provider_details.get("mechanism", "OIDC")
            provider_scope        = provider_details.get("scope", SCOPE_DEFAULT)
            if userid and not re.match(r"\w+$", userid):
                return HttpResponseRedirectLogin(
                    request, 
                    login_message.USER_ID_SYNTAX%(userid)
                    )
            request.session['recent_userid']    = userid
            request.session['provider_details'] = provider_details
            request.session['continuation_url'] = continuation_url
            if provider_mechanism == "OIDC":
                # Create and initialize flow object
                flow = oauth2_flow_from_provider_details(
                    provider_details_file,
                    scope=provider_scope,
                    redirect_uri=request.build_absolute_uri(login_done_url)
                    )
                flow.params['state']            = oauth2_get_state_token(request.user)
                flow.params['userid']           = userid
                # Save flow object in Django session
                request.session['oauth2flow']   = oauth2_flow_to_dict(flow)
                # Initiate OAuth2 dance
                auth_uri = flow.step1_get_authorize_url()
                return HttpResponseRedirect(auth_uri)
            if provider_mechanism == "django":
                flow = django_flow_from_user_id(
                    provider_details,
                    userid=userid,
                    auth_uri=reverse("LocalUserPasswordView"),
                    redirect_uri=request.build_absolute_uri(user_profile_url)
                    )
                # Initiate django authentication
                auth_uri = flow.step1_get_authorize_url()
                return HttpResponseRedirect(auth_uri)
            return HttpResponseRedirectLogin(
                request,
                login_message.UNRECOGNIZED_PROVIDER%(provider_mechanism, provider_details_file)
                )
        # Login cancelled: redirect to continuation
        # (which may just redisplay the login page)
        return HttpResponseRedirect(continuation_url)

class LogoutUserView(generic.View):
    """
    View class to handle logout
    """

    def get(self, request):
        recent_userid = request.session.get('recent_userid', "")
        logout(request)
        request.session['recent_userid'] = recent_userid
        continuation_url = request.GET.get("continuation_url", 
            urljoin(urlparse(request.path).path, "../")
            )
        return HttpResponseRedirect(continuation_url)

# End.
