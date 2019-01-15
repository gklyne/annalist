"""
Authentication backend using Credential object returned by oauth2client flow exchange
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

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

from utils.py3porting import is_string, to_unicode

class OAuth2CheckBackend(object):
    """
    Authenticate using credential object from OAuth2 exchange

    username is a local user id that keys the local user database
    password is a Credential object obtained via the OAuth2 dance
    profile  is a user profile information dictionary

    NOTE: when this method returns a User record on completion of a third
    party authentication process, it does not guarantee that it is the same
    as any record that may have been previously associated with the supplied
    username.  It becomes the responsibility of the calling view code to check 
    that the user details match any previously associated with the user id.

    The returned user object is created or copied from the Django user base,
    but if it already exists the email address is replaced with the one
    returned by the OIDC authentication exchange.
    """

    def authenticate(self, username=None, profile=None):
        log.debug(
            "OAuth2CheckBackend.authenticate: username %s, profile %r"%
            (username, profile)
            )
        if is_string(profile):
            # Not oauth2 exchange:
            # @TODO: can we be more specific about what type this should be?
            return None
        auth_email      = None
        return_user     = None
        create_username = None
        verified_email  = False
        if profile:
            # It looks like this was changed in Google profile
            verified_email = (
                profile.get("verified_email", False) or 
                profile.get("email_verified", False)
                )
        if verified_email:
            # Use access token to retrieve profile information
            # Construct authenticated user ID from email local part
            auth_email       = profile['email']
            email_local_part = auth_email.split('@', 1)[0]
            auth_username    = re.sub(r"\.", "_", email_local_part)
            auth_username    = re.sub(r"[^a-zA-Z0-9_]", "", auth_username)
            auth_username    = auth_username[:32]
        if username:
            try:
                return_user       = User.objects.get(username=username)
                return_user.email = auth_email
            except User.DoesNotExist:
                create_username = username
        elif auth_username:
            try:
                return_user = User.objects.get(username=auth_username)
            except User.DoesNotExist:
                create_username = auth_username
        if create_username:
            # NOTE: when a new User record is created, it is important
            # that it is saved to the local Django database before
            # returning it to the caller, to ensure that a suitable
            # primary key value is created.  The authentication return
            # path makes further changes to the User record which cause
            # the Django ORM to force an update rather than insert of the
            # new record, which in turn generates an error if no primary
            # key is defined.
            log.info("Create new user record for %s"%(create_username))
            return_user = User(username=create_username, password='Not specified')
            if profile is not None:
                return_user.is_staff     = True
                return_user.is_superuser = False
                #@@ For testing: fake old-style Google profile
                # if ("given_name" in profile) and ("family_name" in profile):
                #     profile["name"] = profile["given_name"] + " " + profile["family_name"]
                #     del profile["given_name"]
                #     del profile["family_name"]
                #@@
                if ("given_name" in profile) and ("family_name" in profile):
                    given_name  = profile["given_name"]
                    family_name = profile["family_name"]
                else:
                    # Older Google profiles have just "name" value, apparently
                    n = profile.get("name", "").split(None, 1)
                    given_name  = ""
                    family_name = ""
                    if len(n) >= 1:
                        given_name  = n[0]
                    if len(n) >= 2:
                        family_name = n[1]
                return_user.first_name   = given_name
                return_user.last_name    = family_name
                return_user.email        = profile["email"]
            elif password.id_token:
                # No profile provided: Try to load email address from id_token
                return_user.is_staff     = True
                return_user.is_superuser = False
                return_user.first_name   = ""
                return_user.last_name    = ""
                return_user.email        = password.id_token["email"]
            else:
                return_user = None
            if return_user:
                return_user.save()
        if return_user:
            log.info("user.username:   %s"%(return_user.username,))
            log.info("user.first_name: %s"%(return_user.first_name,))
            log.info("user.last_name:  %s"%(return_user.last_name,))
            log.info("user.email:      %s"%(return_user.email,))
            return return_user
        # No username or credentials provided
        log.info("No user id or no credentials provided")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# End.
