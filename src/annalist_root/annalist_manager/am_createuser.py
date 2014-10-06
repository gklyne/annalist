"""
Create Annalist/Django superuser.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import importlib
import re
import logging
# import subprocess

log = logging.getLogger(__name__)

import django

from annalist.models.annalistuser   import AnnalistUser

import am_errors
from am_settings                    import am_get_settings, am_get_site
from am_getargvalue                 import getarg, getargvalue, getsecret

def create_user_permissions(site, user_id, user_email, user_name, user_permissions):
    user_values = (
        { 'annal:type':             "annal:User"
        , 'rdfs:label':             user_name
        , 'rdfs:comment':           "User %s: site permissions for %s"%(user_id, user_name)
        , 'annal:uri':              "mailto:%s"%(user_email)
        , 'annal:user_permissions': user_permissions
        })
    user = AnnalistUser.create(site, user_id, user_values, use_altpath=True)
    return user


def am_createadminuser(annroot, userhome, options):
    """
    Create Annalistr/Django superuser account.  

    Once created, this can be used to create additional users through the 
    site 'admin' link.

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    # see:
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#django.contrib.auth.models.User
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#manager-methods
    #   https://docs.python.org/2/library/getpass.html
    #   raw_input and getpass:  http://packetforger.wordpress.com/2014/03/26/using-pythons-getpass-module/
    status   = am_errors.AM_SUCCESS
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 4:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    os.environ['DJANGO_SETTINGS_MODULE'] = settings.modulename
    django.setup()
    sitesettings = importlib.import_module(settings.modulename)
    from django.contrib.auth.models import User     # import deferred until after sitesettings import
    #
    user_name_regex        = r"^[a-zA-Z0-9@.+_-]+$"
    user_email_regex       = r"^[A-Za-z0-9.+_-]+@([A-Za-z0-9_-]+)(\.[A-Za-z0-9_-]+)*$"
    user_name_prompt       = "Admin user name:       "
    user_email_prompt      = "Admin user email:      "
    user_first_name_prompt = "Admin user first name: "
    user_last_name_prompt  = "Admin user last name:  "
    user_password_prompt   = "Admin user password:   "
    user_password_c_prompt = "Re-enter password:     "
    user_name = getargvalue(getarg(options.args, 0), user_name_prompt)
    while not re.match(user_name_regex, user_name):
        print("Invalid username %s - re-enter"%user_name, file=sys.stderr)
        user_name = getargvalue(None, user_name_prompt)
    # Check username doesn't already exist
    if User.objects.filter(username=user_name):
        print("User %s already exists"%user_name, file=sys.stderr)
        return am_errors.AM_USEREXISTS
    # Get other values
    user_email = getargvalue(getarg(options.args, 1), user_email_prompt)
    while not re.match(user_email_regex, user_email):
        print("Invalid email address %s - re-enter"%user_email, file=sys.stderr)
        user_email = getargvalue(None, user_email_prompt)
    user_first_name = getargvalue(getarg(options.args, 2), user_first_name_prompt)
    user_last_name  = getargvalue(getarg(options.args, 3), user_last_name_prompt)
    user_password   = getsecret(user_password_prompt)
    user_password_c = getsecret(user_password_c_prompt)
    while user_password != user_password_c:
        print("Password values mismatch - try again", file=sys.stderr)
        user_password   = getsecret(user_password_prompt)
        user_password_c = getsecret(user_password_c_prompt)
    # Have all the details - now create the user in the Django user database
    # see:
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#django.contrib.auth.models.User
    #   https://docs.djangoproject.c om/en/1.7/ref/contrib/auth/#manager-methods    
    user = User.objects.create_user(user_name, user_email, user_password)
    user.first_name   = user_first_name
    user.last_name    = user_last_name
    user.is_active    = True
    user.is_staff     = True
    user.is_superuser = True
    user.save()
    #@@
    # status = am_errors.AM_SUCCESS
    # cmd = "createsuperuser"
    # # --username=joe --email=joe@example.com
    # subprocess_command = "django-admin %s --pythonpath=%s --settings=%s"%(cmd, annroot, settings.modulename)
    # log.debug("am_initialize subprocess: %s"%subprocess_command)
    # status = subprocess.call(subprocess_command.split())
    # log.debug("am_initialize subprocess status: %s"%status)
    #@@
    # Create permissions record for admin user
    site = am_get_site(sitesettings)
    user = create_user_permissions(
        site, user_name, user_email, 
        "%s %s"%(user_first_name, user_last_name), 
        ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        )
    return status

# End.
