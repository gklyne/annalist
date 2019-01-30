"""
Login and authentication views and related authentication setup logic
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import re
import traceback
import json
import markdown
import copy
import uuid
import urllib
from importlib import import_module

from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from utils.http_errors      import error400values
from utils.py3porting       import urlparse, urljoin

from .                      import login_message
from .auth_django_client    import django_flow_from_user_id
from .auth_oidc_client      import oauth2_flow_from_provider_data
from .login_utils           import (
    HttpResponseRedirectWithQuery, 
    HttpResponseRedirectLogin
    )

PROVIDER_FILES = None

PROVIDER_DETAILS = None

settings = import_module(os.environ["DJANGO_SETTINGS_MODULE"])

def collect_provider_data():
    global PROVIDER_FILES, PROVIDER_DETAILS
    if PROVIDER_DETAILS is None:
        PROVIDER_DETAILS = {}
        PROVIDER_FILES   = {}
        clientsecrets_dirname = os.path.join(settings.CONFIG_BASE, "providers/")
        if os.path.isdir(clientsecrets_dirname):
            clientsecrets_files   = os.listdir(clientsecrets_dirname)
            for f in clientsecrets_files:
                if f.endswith(".json"):
                    provider_path = os.path.join(clientsecrets_dirname,f)
                    with open(provider_path, "r") as f:
                        provider_data = json.load(f)
                    provider_name = provider_data['web']['provider']
                    PROVIDER_FILES[provider_name]   = provider_path
                    PROVIDER_DETAILS[provider_name] = provider_data['web']
                    if 'provider_label' not in PROVIDER_DETAILS[provider_name]:
                        PROVIDER_DETAILS[provider_name]['provider_label'] = provider_name
                    log.debug("login_views: collect_provider_data %s"%(provider_name,))
                    # For debugging only: don't log details in running system...
                    # log.debug(json.dumps(
                    #     PROVIDER_DETAILS[provider_name], 
                    #     sort_keys=True,
                    #     indent=4,
                    #     separators=(',', ': ')
                    #     ))
    return

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
    if view.request.user.is_authenticated:
        return None
    if not login_form_url:
        return error400values(view, "No login form URI specified")
    if not login_done_url:
        return error400values(view, "No login completion URI specified")
    if not login_post_url:
        login_post_url = login_form_url
    if not continuation_url:
        continuation_url = view.request.path
    # Redirect to initiate login sequence 
    # See: https://docs.djangoproject.com/en/2.0/topics/http/sessions/
    view.request.session['login_form_url']   = login_form_url
    view.request.session['login_post_url']   = login_post_url
    view.request.session['login_done_url']   = login_done_url
    view.request.session['user_profile_url'] = user_profile_url
    view.request.session['continuation_url'] = continuation_url
    view.request.session['help_dir']         = os.path.join(settings.SITE_SRC_ROOT, help_path)
    userid = view.request.POST.get("userid", 
        view.request.GET.get("userid",
            view.request.session.get('login_recent_userid', "")
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
        collect_provider_data()
        # @@TODO: check PROVIDER_FILES, report error if none here
        # Retrieve request parameters
        continuation_url  = request.GET.get("continuation_url", "/no-login-continuation/")
        # Check required values in session - if missing, restart sequence from original URI
        # This is intended to avoid problems if this view is invoked out of sequence
        login_post_url    = request.session.get("login_post_url",       None)
        login_done_url    = request.session.get("login_done_url",       None)
        user_profile_url  = request.session.get("user_profile_url",     None)
        help_dir          = request.session.get("help_dir",             None)
        recent_userid     = request.session.get("login_recent_userid",  "")
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
        provider_tuples = (
            [ ( p.get('provider_order', 5),
                (k, p.get('provider_label', k), p.get('provider_image', None))
              ) for k, p in PROVIDER_DETAILS.items()
            ])
        provider_labels = [ p[1] for p in sorted(provider_tuples) ]
        for p in PROVIDER_DETAILS:
            if "default" in PROVIDER_DETAILS[p]:            
                default_provider = PROVIDER_DETAILS[p]["default"]
        logindata = (
            { "login_post_url":     login_post_url
            , "login_done_url":     login_done_url
            , "user_profile_url":   user_profile_url
            , "continuation_url":   continuation_url
            , "provider_keys":      list(PROVIDER_DETAILS)
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
        return HttpResponse(template.render(logindata, request=self.request))

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
    - a string that identifies a provider selected to perform authentication
      of the indicated user.  This string is an index to PROVIDER_FILES,
      which in turn contains filenames for client secrets to use when accessing
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
        log.info("LoginPostView.post")
        try:
            response = self.post_main(request)
        except Exception as e:
            # -- This should be redundant, but...
            log.error("Exception in LoginPostView.post (%r)"%(e))
            log.error("".join(traceback.format_stack()))
            # --
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        log.info(
            "LoginPostView.post complete %d %s"%
            (response.status_code, response.reason_phrase)
            )
        return response

    def post_main(self, request):
        # Retrieve request parameters
        userid            = request.POST.get("userid",            "")
        provider          = request.POST.get("provider",          "No_provider")
        provider          = request.POST.get("login",             provider)
        login_done_url    = request.POST.get("login_done_url",    "/no_login_done_url_in_form/")
        user_profile_url  = request.POST.get("user_profile_url",  "/no_user_profile_url_in_form/")
        continuation_url  = request.POST.get("continuation_url",  "/no_continuation_url_in_form/")
        if request.POST.get("login", None):
            collect_provider_data()
            provider_data = PROVIDER_DETAILS[provider]
            provider_name = PROVIDER_FILES[provider]
            provider_mechanism = provider_data.get("mechanism", "OIDC")
            if userid and not re.match(r"\w+$", userid):
                return HttpResponseRedirectLogin(
                    request, 
                    login_message.USER_ID_SYNTAX%(userid)
                    )
            request.session['login_recent_userid']    = userid
            request.session['login_provider_data']    = provider_data
            request.session['login_continuation_url'] = continuation_url
            if provider_mechanism == "OIDC":
                # Create and initialize flow object
                log.debug("LoginPostView.post: SECURE_PROXY_SSL_HEADER %r"%(settings.SECURE_PROXY_SSL_HEADER,))
                log.debug("LoginPostView.post: scheme %s"%(request.scheme,))
                log.debug("LoginPostView.post: headers %r"%(request.META,))
                flow = oauth2_flow_from_provider_data(
                    provider_data,
                    redirect_uri=request.build_absolute_uri(login_done_url)
                    )
                request.session['oauth2_state']  = flow.step1_get_state_token()
                request.session['oauth2_userid'] = userid
                # Initiate OAuth2 dance
                # The response is handled by auth_oidc_client.OIDC_AuthDoneView
                return HttpResponseRedirect(flow.step1_get_authorize_url())
            if provider_mechanism == "django":
                flow = django_flow_from_user_id(
                    provider_data,
                    userid=userid,
                    auth_uri=reverse("LocalUserPasswordView"),
                    redirect_uri=request.build_absolute_uri(user_profile_url)
                    )
                # Initiate django authentication
                auth_uri = flow.step1_get_authorize_url()
                return HttpResponseRedirect(auth_uri)
            return HttpResponseRedirectLogin(
                request,
                login_message.UNRECOGNIZED_PROVIDER%(provider_mechanism, provider_name)
                )
        # Login cancelled: redirect to continuation
        # (which may just redisplay the login page)
        return HttpResponseRedirect(continuation_url)

class LogoutUserView(generic.View):
    """
    View class to handle logout
    """

    def get(self, request):
        recent_userid = request.session.get('login_recent_userid', "")
        logout(request)
        request.session['login_recent_userid'] = recent_userid
        continuation_url = request.GET.get("continuation_url", 
            urljoin(urlparse(request.path).path, "../")
            )
        return HttpResponseRedirect(continuation_url)

# End.
