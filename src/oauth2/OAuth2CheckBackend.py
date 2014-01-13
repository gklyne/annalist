"""
Authentication backend using Credential object returned by oauth2client flow exchange
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import json
import copy

import logging
log = logging.getLogger(__name__)

import httplib2

from django.contrib.auth.models import User

class OAuth2CheckBackend(object):
    """
    Authenticate using credential object from OAuth2 exchange

    username is a local user id that keys the local user database
    password is a Credential object obtained via the OAuth2 dance
    profile_uri is a URI from which user profile information is retrieved

    NOTE: when this method returns a User record on completion of a third
    party authentication process, it does not guarrantee that it is the same
    as any record that may have been previously associated with the supplied
    username.  It becomes the responsibility of the calling view code to check 
    that the user details match any previously associated with the user id.
    """
    def authenticate(self, username=None, password=None, profile_uri=None):
        if isinstance(password, unicode):
            return None
        if username and password and not password.invalid:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked.
            try:
                user = User.objects.get(username=username)
                log.info("Found user record for %s"%(username))
            except User.DoesNotExist:
                # NOTE: when a new User record is created, it is important
                # that it is saved to the local Django database before
                # returning it to the caller, to ensure that a suitable
                # primary key value is created.  The authentication return
                # path makes further changes to the User record which cause
                # the Django ORM to force an update rather than insert of the
                # new record, which in turn generates an error if no primary
                # key is defined.
                log.info("Create new user record for %s"%(username))
                user = User(username=username, password='Not specified')
                user.is_staff     = True
                user.is_superuser = False
                user.email        = ""
                user.save()
            if profile_uri is not None:
                # Use access token to retrieve profile information
                http = httplib2.Http()
                http = password.authorize(http)
                (resp, data) = http.request(profile_uri, method="GET")
                status   = resp.status
                reason   = resp.reason
                assert status == 200, "status: %03d, reason %s"%(status, reason)
                if status == 200:
                    profile = json.loads(data)
                    user.first_name = profile['given_name']
                    user.last_name  = profile['family_name']
                    user.email      = profile['email']
                else:
                    # Profile access failed
                    user = None
            elif password.id_token:
                # No userinfo endpoint: Load email address from id_token
                user.first_name = ""
                user.last_name  = ""
                user.email      = password.id_token['email']
            if user is not None:
                log.info("user.username:   "+user.username)
                log.info("user.first_name: "+user.first_name)
                log.info("user.last_name:  "+user.last_name)
                log.info("user.email:      "+user.email)
            return user
        # No username or credentials provided
        log.info("No user id or no credentials provided")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# End.
