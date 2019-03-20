"""
OAuth2 / OpenID Connect authentication related view handler and
supporting utilities.

NOTE: for Google provider, set up via 
https://console.developers.google.com/apis/dashboard
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import json
import re
import traceback
import logging
log = logging.getLogger(__name__)

from requests_oauthlib import OAuth2Session

from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from utils.http_errors import error400values

from .                  import login_message
from .login_utils       import (
    HttpResponseRedirectWithQuery, 
    HttpResponseRedirectLogin
    )

SCOPE_DEFAULT = ["openid", "profile", "email"]

#   ---------------------------------------------------------------------------
#
#   Factory function
#
#   ---------------------------------------------------------------------------

def oauth2_flow_from_provider_data(provider_data, redirect_uri=None, state=None):
    """
    Create an OpenId connect Oauth2 flow object from a supplied provider details file.

    provider_data
            dictionary containing provider details (including oauth2 client secrets).
    redirect_uri
            URI to which control is transferred when the OAuth2 authetication dance 
            is completed.  If specified, overrides value from provider-file.
    """
    return oauth2_flow(provider_data, redirect_uri=redirect_uri, state=state)

#   ---------------------------------------------------------------------------
#
#   Oauth2 flow object (based loosely on oauth2client flow object)
#
#   ---------------------------------------------------------------------------

class oauth2_flow(object):
    """
    Choreographs the oauth2 dance used to obtain a user authentication credential.
    """

    def __init__(self, provider_data, scope=None, state=None, redirect_uri=None):
        """
        Initialize a flow object with supplied provider data (provided as a dictionary)
        """
        self._provider_data = provider_data
        self._scope         = scope or provider_data.get("scope", SCOPE_DEFAULT)
        assert redirect_uri, "Redirect URI not specified"
        self._redirect_uri  = redirect_uri
        session             = OAuth2Session(
                                client_id=provider_data["client_id"],
                                scope=self._scope,
                                state=state,
                                redirect_uri=self._redirect_uri
                                )
        auth_uri, state     = session.authorization_url(provider_data["auth_uri"])
        self._session       = session
        self._auth_uri      = auth_uri
        self._state         = state
        # log.debug("oauth2_flow: provider_data %r"%(self._provider_data,))
        log.debug("oauth2_flow: scope         %r"%(self._scope,))
        log.debug("oauth2_flow: redirect_uri  %r"%(self._redirect_uri,))
        log.debug("oauth2_flow: session       %r"%(self._session,))
        log.debug("oauth2_flow: auth_uri      %r"%(self._auth_uri,))
        log.debug("oauth2_flow: state         %r"%(self._state,))
        return

    def step1_get_state_token(self):
        return self._state

    def step1_get_authorize_url(self):
        log.info("step1_get_authorize_url: auth_uri %r", self._auth_uri)
        return self._auth_uri

    def step2_exchange(self, request):
        """
        Using a credentials provided in the supplied redirect request value,
        requests an access token for user authentication.
        """
        auth_resp     = request.build_absolute_uri()
        token_uri     = self._provider_data['token_uri']
        client_secret = self._provider_data['client_secret']
        log.debug("step2_exchange: token_uri     %r", token_uri)
        log.debug("step2_exchange: auth_resp     %r", auth_resp)
        # For debugging onlky.  Don't log this in a running system!
        # log.debug("step2_exchange: client_secret %r", client_secret)
        try:
            token = self._session.fetch_token(token_uri, 
                client_secret=client_secret,
                authorization_response=auth_resp,
                timeout=5
                )
        except Exception as e:
            log.error("Failed to fetch token: %s"%(e,))
            # log.info(json.dumps(
            #     self._provider_data,
            #     sort_keys=True,
            #     indent=4,
            #     separators=(',', ': ')
            #     ))
            raise
        return token

    def step3_get_profile(self, token):
        """
        Uses saved credentials from `step2_exchange` to access the user profile,
        which is returned as a dictionary.  The content is determined by the identity
        provider service, but is expected to contain at least:

            { "verified_email": true,
              "email":          "...",
              "given_name":     "...",
              "family_name":    "...",
            }
        """
        r = self._session.get(self._provider_data["profile_uri"])
        profile = json.loads(r.content)
        return profile

class OIDC_AuthDoneView(generic.View):
    """
    View class used to complete login process with authorization grant provided by
    OAuth2 authorization server.

    The calling application must set up the URL routing for this handler to be invoked.
    """

    def get(self, request):
        # Look for authorization grant
        provider_data  = request.session['login_provider_data']
        state          = request.session['oauth2_state']
        userid         = request.session['oauth2_userid']
        # session value "login_done_url" is set by login_views.confirm_authentication
        if 'login_done_url' not in request.session:
            return HttpResponseRedirectLogin(request, login_message.SESSION_INTERRUPTED)
        login_done_url = request.build_absolute_uri(request.session['login_done_url'])
        provider       = provider_data['provider']
        flow = oauth2_flow_from_provider_data(
                provider_data, 
                redirect_uri=login_done_url, 
                state=state
                )
        # Get authenticated user details
        try:
            credential = flow.step2_exchange(request)
            profile    = flow.step3_get_profile(credential)
            log.debug("auth_oidc_client: userid %s, profile %r"%(userid, profile))
            authuser = authenticate(
                username=userid, profile=profile
                )
        except Exception as e:
            log.error("Exception %r"%(e,))
            # For debugging only: don't log in running system
            # log.error("provider_data %r"%(provider_data,))
            ex_type, ex, tb = sys.exc_info()
            log.error("".join(traceback.format_exception(ex_type, ex, tb)))
            # log.error("".join(traceback.format_stack()))
            return HttpResponseRedirectLogin(request, str(e))
        # Check authenticated details for user id match any previous values.
        #
        # The user id is entered by the user on the login form, and is used as a key to
        # access authenticated user details in the Django user database.  The user id 
        # itself is not checked by the Oauth2 login flow, other than for checking that
        # it contains only work characters
        #
        # Instead, we trust that the associated email address has been confirmed by the 
        # OAuth2 provider, and don't allow login where the email adress differs from any 
        # currently saved email address for the user id used..  This aims to  prevent a 
        # new set of OAuth2 credentials being used for a previously created Django user id.
        #
        if not authuser:
            return HttpResponseRedirectLogin(request, 
                login_message.USER_NOT_AUTHENTICATED%(userid, provider)
                )
        if not userid:
            # Get generated username
            userid = authuser.username
        if not re.match(r"\w+$", userid):
            return HttpResponseRedirectLogin(
                request, 
                login_message.USER_ID_SYNTAX%(userid)
                )
        if not authuser.email:
            return HttpResponseRedirectLogin(request, 
                login_message.USER_NO_EMAIL%(userid)
                )
        try:
            olduser = User.objects.get(username=userid)
        except User.DoesNotExist:
            olduser = None
        if olduser:
            if authuser.email != olduser.email:
                return HttpResponseRedirectLogin(request, 
                    login_message.USER_WRONG_EMAIL%(userid, authuser.email, olduser.email)
                    )
        # Complete the login and save details
        authuser.save()
        login(request, authuser)
        request.session['login_recent_userid'] = userid
        log.info("OIDC_AuthDoneView: user.username:   "+authuser.username)
        log.info("OIDC_AuthDoneView: user.first_name: "+authuser.first_name)
        log.info("OIDC_AuthDoneView: user.last_name:  "+authuser.last_name)
        log.info("OIDC_AuthDoneView: user.email:      "+authuser.email)
        return HttpResponseRedirectLogin(request)

# End.
