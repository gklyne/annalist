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
    "  %(prog)s createadminuser [ username [ email [ firstname [ lastname ] ] ] ]\n"+
    "  %(prog)s deleteuser [ username ]\n"+
    "  %(prog)s createsitedata [ CONFIG ]\n"+
    "  %(prog)s updatesitedata [ CONFIG ]\n"+
    "  %(prog)s runserver [ CONFIG ]\n"+
    "")

config_options_help = (
    "Annalist can be run in a number of configurations, notably\n"+
    " 'development', 'personal' and 'shared'.\n"+
    "\n"+
    "A configuration can be selected by using one of the following options:\n"+
    "--devel    selects the 'development' configuration, which stores all site data\n"+
    "           within the source code tree, and configuration data in the user's\n"+
    "           home directory ('~/.annalist/')\n"+
    "--personal selects the 'personal' configuration, which stores all site data\n"+
    "           and configuration data in the activating user's home directory\n"+
    "           ('~/annalist_site/ and ~/.annalist/')\n"+
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
            "Creates a Annalist administrative user.\n"+
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
    else:
        help_text = "Unrecognized command for %s: (%s)"%(options.command, options.args[0])
        status = am_errors.AM_UNKNOWNCMD
    print(help_text%{'prog': progname}, file=sys.stderr)
    return status

# End.
