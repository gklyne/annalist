"""
Display Annalist server help messages.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess

log = logging.getLogger(__name__)

import am_errors

command_summary_help = ("\n"+
    "Commands:\n"+
    "\n"+
    "  %(prog)s help [command]\n"+
    "  %(prog)s runtests\n"+
    "  %(prog)s initialize [ CONFIG ]\n"+
    # "  %(prog)s idprovider ...\n"+  #@@ TODO
    "  %(prog)s createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]\n"+
    "  %(prog)s defaultadminuser [ CONFIG ]\n"+
    "  %(prog)s updateadminuser [ username ] [ CONFIG ]\n"+
    "  %(prog)s setdefaultpermissions [ permissions ] [ CONFIG ]\n"+
    "  %(prog)s setpublicpermissions [ permissions ] [ CONFIG ]\n"+
    "  %(prog)s deleteuser [ username ] [ CONFIG ]\n"+
    "  %(prog)s createsitedata [ CONFIG ]\n"+
    "  %(prog)s updatesitedata [ CONFIG ]\n"+
    "  %(prog)s runserver [ CONFIG ]\n"+
    "  %(prog)s sitedirectory [ CONFIG ]\n"+
    "  %(prog)s serverlog [ CONFIG ]\n"+
    "  %(prog)s version\n"+
    "")

config_options_help = (
    "Annalist can be run in a number of configurations, notably\n"+
    "'development', 'personal' and 'shared'.\n"+
    "\n"+
    "A configuration can be selected by using one of the following options:\n"+
    "--devel    selects the 'development' configuration, which stores all site data\n"+
    "           within the source code tree, and configuration data in the user's\n"+
    "           home directory ('~/.annalist/')\n"+
    "--personal selects the 'personal' configuration, which stores all site data\n"+
    "           and configuration data in the activating user's home directory\n"+
    "           ('~/annalist_site/' and '~/.annalist/')\n"+
    "--shared   selects the 'shared' configuration, which stores all site and configuration\n"+
    "           data in system directories '/var/annalist_site', and configuration.\n"+
    "           data in '/etc/annalist/'\n"+
    "--configuration=NAME\n"+
    "           allows selection of any named configuration, where configuration files\n"+
    "           are stored in the Annalist source tree as '.../annalist_site/settings/NAME.py'\n"+
    "\n"+
    "The above options may be abbreviated as '-d', '-p', '-s' and '-c' respectively.\n"+
    "If no configuration is explicitly specified, '--personal' is used.\n"+
    "")

permissions_help = (
    "The 'permissions' parameter is a list of space-separated permission keywords,\n"+
    "or may be empty.  If multiple permissions are specified, some form of command-line\n"+
    "quoting should be used so they are presented as a single argument (e.g. enclose\n"+
    "the list of keywords in double quoted).\n"+
    "If not specified on the command line, the user will be prompted for default permissions.\n"+
    "\n"+
    "Initially defined permissions are:\n"+
    "CREATE_COLLECTION   site-level permission required to create new collection (or ADMIN).\n"+
    "DELETE_COLLECTION   site-level permission required to delete a collection (or ADMIN).\n"+
    "VIEW                permission to view or list data in a collection\n"+
    "CREATE              permission to create new data in a collection\n"+
    "UPDATE              permission to update existing data in a collection\n"+
    "DELETE              permission to delete data from a collection\n"+
    "CONFIG              permission to add or modify configuration data for a collection\n"+
    "                    (i.e. types, views, lists, fields, and field groups)\n"+
    "ADMIN               permission to add or modify user permissions\n"+
    "")

def am_help(options, progname):
    """
    Display annalist-manager command help

    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    if len(options.args) > 1:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    if len(options.args) == 0:
        help_text = (
            command_summary_help+
            "\n"+
            "For more information about command options, use:\n"+
            "\n"+
            "  %(prog)s --help\n"+
            "")
    elif options.args[0].startswith("runt"):
        help_text = ("\n"+
            "  %(prog)s runtests\n"+
            "\n"+
            "Runs annalist test suite using installed software\n"+
            "\n"+
            "")
    elif options.args[0].startswith("init"):
        help_text = ("\n"+
            "  %(prog)s initialize [ CONFIG ]\n"+
            "\n"+
            "Initializes the installed software for an indicated configuration.\n"+
            "Mainly, this involves creating the internal database used to manage users, etc.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("createa"):
        help_text = ("\n"+
            "  %(prog)s createadminuser [ CONFIG ]\n"+
            "\n"+
            "Creates an Annalist administrative user.\n"+
            "\n"+
            "The software will prompt for a username, email address and password.\n"+
            "\n"+
            "The administrative user details can be used to log in to Annalist using\n"+
            "the 'Local user credentials: login' link at the bottom of the login page.\n"+
            "An administrative user can then use the 'Admin' link at the bottom of other\n"+
            "Annalist pages to create, modify or delete other local user credentials.\n"+
            "\n"+
            "Annalist is intended to be used with a federated authentication service,\n"+
            "such as Google+, but setting up such a service can be tricky, and for evaluation\n"+
            "or personal-only use it may be quicker to use locally managed user credentials\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("defaulta"):
        help_text = ("\n"+
            "  %(prog)s defaultadminuser [ CONFIG ]\n"+
            "\n"+
            "Creates a default Annalist administrative user.\n"+
            "\n"+
            "The software uses default values for a username and email address, prompts for\n"+
            "a password, and creates a new admin user with username 'admin'.\n"+
            "\n"+
            "The administrative user details can be used to log in to Annalist using\n"+
            "the 'Local user credentials: login' link at the bottom of the login page.\n"+
            "An administrative user can then use the 'Admin' link at the bottom of other\n"+
            "Annalist pages to create, modify or delete other local user credentials.\n"+
            "\n"+
            "Annalist is intended to be used with a federated authentication service,\n"+
            "such as Google+, but setting up such a service can be tricky, and for evaluation\n"+
            "or personal-only use it may be quicker to use locally managed user credentials\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("updatea"):
        help_text = ("\n"+
            "  %(prog)s updateadminuser [ username ] [ CONFIG ]\n"+
            "\n"+
            "Updates an existing Django user to admin status; i.e. they are assigned 'staff'\n"+
            "and 'superuser' attributes in the Django user database, and assigned site-wide\n"+
            "ADMIN permissions in the Annalist site indicated by CONFIG.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("setdef"):
        help_text = ("\n"+
            "  %(prog)s setdefaultpermissions [ permissions ] [ CONFIG ]\n"+
            "\n"+
            "Sets site-wide default permissions for logged-in users in the\n"+
            "Annalist site indicated by CONFIG.  These permissions are superseded by\n"+
            "any permissions defined specifically for a logged-in user, or by\n"+
            "user '_default_user_perms' entry defined for any collection.\n"+
            "\n"+
            permissions_help+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("setpub"):
        help_text = ("\n"+
            "  %(prog)s setpublicpermissions [ permissions ] [ CONFIG ]\n"+
            "\n"+
            "Sets site-wide public access permissions (i.e. for requests where there is no active login)\n"+
            "in the Annalist site indicated by CONFIG.  These permissions may be superseded by\n"+
            "'_unknown_user_perms' permissions defined for any specific collection.\n"+
            "\n"+
            permissions_help+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("deleteu"):
        help_text = ("\n"+
            "  %(prog)s deleteuser [ username ] [ CONFIG ]\n"+
            "\n"+
            "Deletes the specified Django user, and also removes any site-wide permissions defined\n"+
            "for that user in he Annalist site indicated by CONFIG.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("creates"):
        help_text = ("\n"+
            "  %(prog)s createsite [ CONFIG ] [ --force | -f ]\n"+
            "\n"+
            "Creates Annalist empty site data.\n"+
            "\n"+
            "Creates empty site data (i.e. with no collections) for an Annalist service.\n"+
            "\n"+
            "If the site already exists, the command is refused unless the '--force' or '-f'\n"+
            "option is given.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("updates"):
        help_text = ("\n"+
            "  %(prog)s updatesite [ CONFIG ]\n"+
            "\n"+
            "Updates the site-wide data in an existing annalist site.\n"+
            "\n"+
            "\nExisting collection data is left untouched.\n"+
            "\n"+
            "If the site does not exist, the command fails.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("runs"):
        help_text = ("\n"+
            "  %(prog)s runserver [ CONFIG ]\n"+
            "\n"+
            "Starts an Annalist server running.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("site"):
        help_text = ("\n"+
            "  %(prog)s sitedirectory [ CONFIG ]\n"+
            "\n"+
            "Sends the name of Annalist site directory to standard output.\n"+
            "\n"+
            "This is a convenience function to locate the site data directory, which\n"+
            "may be buried deep in the Python virtual environment files.\n"+
            "\n"+
            config_options_help+
            "\n"+
            "")
    elif options.args[0].startswith("ver"):
        help_text = ("\n"+
            "  %(prog)s version\n"+
            "\n"+
            "Sends the Annalist software version string to standard output.\n"+
            "\n"+
            "")
    else:
        help_text = "Unrecognized command for %s: (%s)"%(options.command, options.args[0])
        status = am_errors.AM_UNKNOWNCMD
    print(help_text%{'prog': progname}, file=sys.stderr)
    return status

# End.
