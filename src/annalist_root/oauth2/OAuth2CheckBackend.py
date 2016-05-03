"""
Authentication backend using Credential object returned by oauth2client flow exchange
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import json
import copy
import re

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
        profile = None
        if profile_uri is not None and password and not password.invalid:
            # Use access token to retrieve profile information
            http = httplib2.Http()
            http = password.authorize(http)
            (resp, data) = http.request(profile_uri, method="GET")
            status   = resp.status
            reason   = resp.reason
            assert status == 200, "status: %03d, reason %s"%(status, reason)
            if status == 200:
                profile = json.loads(data)
                # Construct authenticated user ID from email local part
                email_local_part = profile['email'].split('@', 1)[0]
                auth_username = re.sub(r"\.", "_", email_local_part)
                auth_username = re.sub(r"[^a-zA-Z0-9_]", "", auth_username)
                auth_username = auth_username[:32]

        # @@@ define separate paths for username defined and not defined @@@
        user = None
        if username:
            ...
            # username Exists?
            # if so, return to caller (who checks email adrs)
            # if not, create new using profile or password.id_token
        elif auth_username:
            ...
            # (profile must exist)
            # auth_username Exists?
            # if so, return to caller (who checks email adrs)
            # if not, create new using profile
        else:
            ...
            # Nothing to return



        if username:
            try:
                old_user = User.objects.get(username=username)
                if old_user.email == profile['email']:
                    user = old_user
            except User.DoesNotExist:
                pass
        elif auth_username:
            try:
                user = User.objects.get(username=auth_username)
            except User.DoesNotExist:
                pass
        if user:
            log.info("Found user record for %s"%(user.username))
        else:
            # NOTE: when a new User record is created, it is important
            # that it is saved to the local Django database before
            # returning it to the caller, to ensure that a suitable
            # primary key value is created.  The authentication return
            # path makes further changes to the User record which cause
            # the Django ORM to force an update rather than insert of the
            # new record, which in turn generates an error if no primary
            # key is defined.
            if profile is not None:
                create_username = username or auth_username
                log.info("Create new user record for %s"%(create_username))
                user = User(username=create_username, password='Not specified')
                user.is_staff     = True
                user.is_superuser = False
                user.first_name   = profile['given_name']
                user.last_name    = profile['family_name']
                user.email        = profile['email']
                user.save()
            elif username and not old_user:
                log.info("Create new user record for %s"%(username))
                # No profile provided: Try to load email address from id_token
                user = User(username=username, password='Not specified')
                user.is_staff     = True
                user.is_superuser = False
                user.first_name   = ""
                user.last_name    = ""
                user.email        = ""
                if password.id_token:
                    user.email      = password.id_token['email']
                user.save()
        if user:
            log.info("user.username:   "+user.username)
            log.info("user.first_name: "+user.first_name)
            log.info("user.last_name:  "+user.last_name)
            log.info("user.email:      "+user.email)
            return user
        # No username or credentials provided
        log.info("No user id or no credentials provided")
        return None

        # if username or auth_username:
        #     # Retrieve details for authenticated user, or create a new user.
        #     # Note that for externally authenticated users, we can set the password 
        #     # to anything, because it won't be checked.
        #     try:
        #         user = User.objects.get(username=username)
        #         if user.email != profile['email']:
        #             user = None
        #             if auth_username:
        #                 user = User.objects.get(username=auth_username)
        #         log.info("Found user record for %s"%(user.username))
        #     except User.DoesNotExist:
        #         user = None
        #     if user is None:
        #         # NOTE: when a new User record is created, it is important
        #         # that it is saved to the local Django database before
        #         # returning it to the caller, to ensure that a suitable
        #         # primary key value is created.  The authentication return
        #         # path makes further changes to the User record which cause
        #         # the Django ORM to force an update rather than insert of the
        #         # new record, which in turn generates an error if no primary
        #         # key is defined.
        #         log.info("Create new user record for %s"%(username))
        #         if profile is not None:
        #             user = User(username=auth_username, password='Not specified')
        #             user.is_staff     = True
        #             user.is_superuser = False
        #             user.first_name   = profile['given_name']
        #             user.last_name    = profile['family_name']
        #             user.email        = profile['email']
        #         else:
        #             # No profile provided: Try to load email address from id_token
        #             user = User(username=username, password='Not specified')
        #             user.is_staff     = True
        #             user.is_superuser = False
        #             user.first_name   = ""
        #             user.last_name    = ""
        #             user.email        = ""
        #             if password.id_token:
        #                 user.email      = password.id_token['email']
        #         user.save()


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# End.
