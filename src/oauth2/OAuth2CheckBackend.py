"""
Authentication backend using Credential object returned by oauth2client flow exchange
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import json
import copy

import httplib2

from django.contrib.auth.models import User

class OAuth2CheckBackend(object):
    """
    Authenticate using credential object from OAuth2 exchange

    username is a local user id that keys the local user database
    password is a Credential object obtained via the OAuth2 dance
    profile_uri is a URI from which user profile imnformation is retrieved
    """
    def authenticate(self, username=None, password=None, profile_uri=None):
        if username and password and not password.invalid:
            save_required = False
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked.
                user = User(username=username, password='Not specified')
                user.is_staff = True
                user.is_superuser = False
                save_required = True
            if profile_uri:
                # Use access token to retrieve profile information
                http = httplib2.Http()
                http = password.authorize(http)
                (resp, data) = http.request(profile_uri, method="GET")
                status   = resp.status
                reason   = resp.reason
                assert status == 200, "status: %03d, reason %s"%(status, reason)
                if status == 200:
                    # Extract and save user profile details
                    profile = json.loads(data)
                    user.first_name = profile['given_name']
                    user.last_name  = profile['family_name']
                    user.email      = profile['email']
                    save_required = True
            if save_required: user.save()
            return user
        return None

    # @@TODO: remove this method?
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# End.
