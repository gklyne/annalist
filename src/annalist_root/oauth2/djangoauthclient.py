"""
This module handles authentication by the local Django user database,
using an interface following that used by Google's oauth2client.

In due course, we may be able to use the same flow API to handle
diverse forms of third party authentication.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path
import urllib
import logging
log = logging.getLogger(__name__)

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from utils.uri_builder import uri_with_params

def HttpResponseRedirectWithQuery(redirect_uri, query_params):
    nq = "?"
    for pname in query_params.keys():
        redirect_uri += nq + pname + "=" + urllib.quote(query_params[pname])
        nq = "&"
    # log.info("redirect_uri: "+redirect_uri)
    return HttpResponseRedirect(redirect_uri)

def HttpResponseRedirectLoginWithMessage(request, message):
    user_profile_url = request.session['user_profile_url']
    log.info("user_profile_url: "+user_profile_url)
    query_params = (
        { "continuation_url": request.session['continuation_url']
        , "scope":            request.session['oauth2_scope']
        , "error_head":       "Login failed"
        , "error_message":    message
        , "userid":           request.POST.get("userid", request.GET.get("userid", ""))
        })
    return HttpResponseRedirectWithQuery(user_profile_url, query_params)

class LocalUserPasswordView(generic.View):
    """
    View class to present a form for entering a local user id and password.

    The local user password page supports the following request parameters:

    userid={string}
    - a local user id that is the defdault user id for which a password is solicited.
    continuation_url={uri}
    - a URL of pagve to be displayed when the authentication process is complete.
    message={string}
    - a message to be displayed on the page
    """

    def get(self, request):
        """
        Display the local user password page with values as supplied.
        """
        userid           = request.GET.get("userid",            "")
        user_profile_url = request.GET.get("user_profile_url",  "/no-login-user_profile_url/")
        continuation_url = request.GET.get("continuation_url",  "/no-login-continuation_url/")
        login_post_url   = request.session.get("login_post_url", None)
        user_profile_url = request.session.get("user_profile_url", None)
        help_dir         = request.session.get("help_dir", None)
        if (login_post_url is None) or (user_profile_url is None) or (help_dir is None):
            log.warning(
                "@@ redirect post_uri %s, done_uri %s, help_dir %s"%
                (login_post_url, user_profile_url, help_dir)
                )
            return HttpResponseRedirect(continuation_url)
        # Display login form
        localdata = (
            { "userid":             userid
            , "help_filename":      "local-help"
            , "user_profile_url":   user_profile_url
            , "continuation_url":   continuation_url
            , "info_head":          request.GET.get("info_head", None)
            , "info_message":       request.GET.get("info_message", None)
            , "error_head":         request.GET.get("error_head", None)
            , "error_message":      request.GET.get("error_message", None)
            })
        # Load help text if available
        if 'help_filename' in localdata:
            help_filepath = help_dir + "%(help_filename)s.md"%(localdata)
            if os.path.isfile(help_filepath):
                with open(help_filepath, "r") as helpfile:
                    localdata['help_markdown'] = helpfile.read()
        if 'help_markdown' in localdata:
            localdata['help_text'] = markdown.markdown(localdata['help_markdown'])
        # Render form & return control to browser
        template = loader.get_template('local_password.html')
        context  = RequestContext(self.request, localdata)
        return HttpResponse(template.render(context))

    def post(self, request):
        userid           = request.POST.get("userid",             "")
        password         = request.POST.get("password",           "")
        user_profile_url = request.POST.get("user_profile_url", "/no_user_profile_url_in_form/")
        continuation_url = request.POST.get("continuation_url",   "/no_continuation_url_in_form/")
        if request.POST.get("login", None) == "Login":
            if not userid:
                log.info("No User ID specified")
                return HttpResponseRedirectLoginWithMessage(request, "No User ID specified")
            log.info("djangoauthclient: userid %s"%userid)
            request.session['recent_userid'] = userid
            authuser = authenticate(username=userid, password=password)
            if authuser is None:
                return HttpResponseRedirectLoginWithMessage(request, 
                    "Login as %s: no such user or incorrect password"%(userid))
            if not authuser.is_active:
                return HttpResponseRedirectLoginWithMessage(request, 
                    "Account %s has been disabled"%(userid))
            if not authuser.email:
                return HttpResponseRedirectLoginWithMessage(request, 
                    "No email address associated with authenticated user %s"%(userid))
            # Complete the login
            login(request, authuser)
            log.info("LocalUserPasswordView: user.username:   "+authuser.username)
            log.info("LocalUserPasswordView: user.first_name: "+authuser.first_name)
            log.info("LocalUserPasswordView: user.last_name:  "+authuser.last_name)
            log.info("LocalUserPasswordView: user.email:      "+authuser.email)
            return HttpResponseRedirect(user_profile_url)
        # Login cancelled: redirect to continuation
        # (which may just redisplay the login page)
        return HttpResponseRedirect(continuation_url)

class DjangoWebServerFlow(object):
    """
    This class presents an interface similar to "oauth2client" for initiating
    a login using local Django user id and password.
    """

    def __init__(self, provider_details, redirect_uri=None, **kwargs):
        """
        Initialize a new authentication flow object.

        provider_details    is a dictionary of values and parameters
                            that control the authentication flow.
        redirect_uri        is the URI to which control is redirected
                            when authentication is complete.

        """
        super(DjangoWebServerFlow, self).__init__()
        self.params = { 'redirect_uri': redirect_uri }
        self.params.update(kwargs)
        return

    def step1_get_authorize_url(self):
        """
        Return a URL to a page that initiates the Django authentication process.
        """
        uri_base   = self.params['auth_uri']
        uri_params = (
            { 'userid':           self.params['userid']
            , 'continuation_url': self.params['continuation'] 
            })
        return uri_with_params(uri_base, uri_params)

def django_flow_from_user_id(provider_details, redirect_uri=None):
    """
    Initialize and returns a new authentication flow object.

    provider_details    is a dictionary of values and parameters
                        that control the authentication flow.
    redirect_uri        is the URI to which control is redirected
                        when authentication is complete.
    """
    return DjangoWebServerFlow(provider_details, redirect_uri=redirect_uri)

# End.


