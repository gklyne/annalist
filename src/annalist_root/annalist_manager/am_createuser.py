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

from annalist.identifiers           import ANNAL, RDFS
from annalist.models.annalistuser   import AnnalistUser

from utils.SuppressLoggingContext   import SuppressLogging

import am_errors
from am_settings                    import am_get_settings, am_get_site
from am_getargvalue                 import getarg, getargvalue, getsecret

def create_user_permissions(site, user_id, user_uri, user_name, user_comment, user_permissions):
    user_values = (
        { ANNAL.CURIE.type:             ANNAL.CURIE.User
        , RDFS.CURIE.label:             user_name
        , RDFS.CURIE.comment:           user_comment
        , ANNAL.CURIE.user_uri:         "%s"%(user_uri)
        , ANNAL.CURIE.user_permissions: user_permissions
        })
    user = AnnalistUser.create(site, user_id, user_values, use_altpath=True)
    return user

def delete_user_permissions(site, user_id):
    AnnalistUser.remove(site, user_id, use_altpath=True)
    return

def get_site_settings(annroot, userhome, options):
    """
    Access site settings, set up correspondingh django configuration and return the settings module
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return None
    with SuppressLogging(logging.INFO):
        os.environ['DJANGO_SETTINGS_MODULE'] = settings.modulename
        django.setup()
        site_settings = importlib.import_module(settings.modulename)
    return site_settings

def get_user_name(options, prompt_prefix):
    user_name_regex         = r"^[a-zA-Z0-9@.+_-]+$"
    user_name_prompt        = "%s name:        "%prompt_prefix
    user_name = getargvalue(getarg(options.args, 0), user_name_prompt)
    while not re.match(user_name_regex, user_name):
        print("Invalid username %s - re-enter"%user_name, file=sys.stderr)
        user_name = getargvalue(None, user_name_prompt)
    return user_name

def get_user_details(user_name, options, prompt_prefix):
    """
    Get user details (email, first name, last name)

    Returns a dictionary of user details, including the supplied user_name.
    """
    user_email_regex        = r"^[A-Za-z0-9.+_-]+@([A-Za-z0-9_-]+)(\.[A-Za-z0-9_-]+)*$"
    user_email_prompt       = "%s email:       "%prompt_prefix
    user_first_name_prompt  = "%s first name:  "%prompt_prefix
    user_last_name_prompt   = "%s last name:   "%prompt_prefix
    # Get other values
    user_email = getargvalue(getarg(options.args, 1), user_email_prompt)
    while not re.match(user_email_regex, user_email):
        print("Invalid email address %s - re-enter"%user_email, file=sys.stderr)
        user_email = getargvalue(None, user_email_prompt)
    user_first_name = getargvalue(getarg(options.args, 2), user_first_name_prompt)
    user_last_name  = getargvalue(getarg(options.args, 3), user_last_name_prompt)
    return (
        { 'name':       user_name
        , 'email':      user_email
        , 'uri':        "mailto:%s"%user_email
        , 'first_name': user_first_name
        , 'last_name':  user_last_name
        })

def get_user_permissions(options, pos, prompt_prefix):
    """
    Get user permissions to apply
    """
    user_permissions_regex  = r"^([A-Za-z0-9_-]+(\s+[A-Za-z0-9_-]+)*)?$"
    user_permissions_prompt = "%s permissions: "%prompt_prefix
    user_permissions = getargvalue(getarg(options.args, pos), user_permissions_prompt)
    while not re.match(user_permissions_regex, user_permissions):
        print("Invalid permissions %s - re-enter"%user_permissions, file=sys.stderr)
        user_permissions = getargvalue(None, user_permissions_prompt)
    return user_permissions

def create_django_user(user_type, user_details):
    """
    Create Django user (prompts for password)
    """
    # Get password
    user_password_prompt    = "Password: "
    user_password_c_prompt  = "Re-enter password: "
    user_password   = getsecret(user_password_prompt)
    user_password_c = getsecret(user_password_c_prompt)
    while user_password != user_password_c:
        print("Password values mismatch - try again", file=sys.stderr)
        user_password   = getsecret(user_password_prompt)
        user_password_c = getsecret(user_password_c_prompt)
    # Have all the details - create djano user now
    # Create the user in the Django user database
    # see:
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#django.contrib.auth.models.User
    #   https://docs.djangoproject.c om/en/1.7/ref/contrib/auth/#manager-methods
    from django.contrib.auth.models import User     # import deferred until after sitesettings import
    user = User.objects.create_user(user_details['name'], user_details['email'], user_password)
    user.first_name   = user_details['first_name']
    user.last_name    = user_details['last_name']
    user.is_active    = True
    user.is_staff     = user_type in ["staff", "superuser"]
    user.is_superuser = user_type in ["superuser"]
    user.save()
    return am_errors.AM_SUCCESS

def create_site_permissions(sitesettings, user_details, permissions):
    site   = am_get_site(sitesettings)
    if not 'label' in user_details:
        user_details['label'] = (
            "%(first_name)s %(last_name)s"%user_details
            )
    if not 'comment' in user_details:
        user_details['comment'] = (
            "User %(name)s: site permissions for %(first_name)s %(last_name)s"%user_details
            )
    user = create_user_permissions(
        site, user_details['name'], user_details['uri'], 
        user_details['label'],
        user_details['comment'], 
        permissions
        )
    return am_errors.AM_SUCCESS

def am_createadminuser(annroot, userhome, options):
    """
    Create Annalist/Django admin/superuser account.  

    Once created, this can be used to create additional users through the 
    site 'admin' link, and can also create collections and

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    prompt_prefix = "Admin user"
    if len(options.args) > 4:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    user_name = get_user_name(options, prompt_prefix)
    #
    from django.contrib.auth.models import User     # import deferred until after sitesettings import
    if User.objects.filter(username=user_name):
        print("User %s already exists"%user_name, file=sys.stderr)
        return am_errors.AM_USEREXISTS
    user_details = get_user_details(user_name, options, prompt_prefix)
    status = create_django_user("superuser", user_details)
    if status == am_errors.AM_SUCCESS:
        status = create_site_permissions(
            sitesettings, user_details, 
            ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
    return status

def am_defaultadminuser(annroot, userhome, options):
    """
    Create default Annalist/Django admin/superuser account.  

    Creates an admin accoubnt with default values:
        username:   admin
        email:      admin@localhost
        firstname:  Admin
        lastname:   User

    Prompts for password as before

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    default_admin = (
        { 'name':       "admin"
        , 'email':      "admin@localhost"
        , 'uri':        "mailto:admin@localhost"
        , 'first_name': "Admin"
        , 'last_name':  "User"
        })
    print("Creating user %(name)s"%default_admin, file=sys.stderr)
    status = create_django_user("superuser", default_admin)
    if status == am_errors.AM_SUCCESS:
        status = create_site_permissions(
            sitesettings, default_admin, 
            ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
            )
    return status

def am_updateadminuser(annroot, userhome, options):
    """
    Update existing Django user to admin status

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    # see:
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#django.contrib.auth.models.User
    prompt_prefix = "Update user"
    if len(options.args) > 1:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    user_name = get_user_name(options, prompt_prefix)
    #
    from django.contrib.auth.models import User     # import deferred until after sitesettings import
    userqueryset = User.objects.filter(username=user_name)
    if not userqueryset:
        print("User %s does not exist"%user_name, file=sys.stderr)
        return am_errors.AM_USERNOTEXISTS
    # Have all the details - now update the user in the Django user database
    # see:
    #   https://docs.djangoproject.com/en/1.7/ref/contrib/auth/#django.contrib.auth.models.User
    #   https://docs.djangoproject.c om/en/1.7/ref/contrib/auth/#manager-methods
    user = userqueryset[0]
    user.is_staff     = True
    user.is_superuser = True
    user.save()
    # Create site permissions record for admin user
    user_details = (
        { 'name':       user_name
        , 'email':      user.email
        , 'uri':        "mailto:%s"%user.email
        , 'first_name': user.first_name
        , 'last_name':  user.last_name
        })
    status = create_site_permissions(
        sitesettings, user_details, 
        ["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        )
    return status

def am_setdefaultpermissions(annroot, userhome, options):
    """
    Set site-wide default permissions for logged in users

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    prompt_prefix = "Default "
    if len(options.args) > 1:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    user_permissions = get_user_permissions(options, 0, prompt_prefix)
    user_details = (
        { 'name':       "_default_user_perms"
        , 'uri':        "annal:User/_default_user_perms"
        , 'label':      "Default permissions"
        , 'comment':    "Default permissions for authenticated user."
        })
    status = create_site_permissions(sitesettings, user_details, user_permissions)
    return status

def am_setpublicpermissions(annroot, userhome, options):
    """
    Set site-wide default permissions for unauthenticated public access

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    prompt_prefix = "Public access "
    if len(options.args) > 1:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    user_permissions = get_user_permissions(options, 0, prompt_prefix)
    user_details = (
        { 'name':       "_unknown_user_perms"
        , 'uri':        "annal:User/_unknown_user_perms"
        , 'label':      "Unknown user"
        , 'comment':    "Permissions for unauthenticated user."
        })
    status = create_site_permissions(sitesettings, user_details, user_permissions)
    return status

def am_deleteuser(annroot, userhome, options):
    """
    Delete Annalist/Django user account.  

    annroot     is the root directory for theannalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    prompt_prefix = "Delete user"
    if len(options.args) > 1:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = get_site_settings(annroot, userhome, options)
    if not sitesettings:
        return am_errors.AM_NOSETTINGS
    user_name = get_user_name(options, prompt_prefix)
    #
    from django.contrib.auth.models import User     # import deferred until after sitesettings import
    userqueryset = User.objects.filter(username=user_name)
    if not userqueryset:
        print("User %s does not exist"%user_name, file=sys.stderr)
        return am_errors.AM_USERNOTEXISTS
    userqueryset.delete()
    site = am_get_site(sitesettings)
    delete_user_permissions(site, user_name)
    return am_errors.AM_SUCCESS

# End.
