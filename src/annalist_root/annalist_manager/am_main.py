# !/usr/bin/env python
#
# am_main.py - command line tool to perform Annalist installation management
#

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2013-2014, Graham Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import argparse
import logging
import errno

log = logging.getLogger(__name__)

# if __name__ == "__main__":
dirhere = os.path.dirname(os.path.realpath(__file__))
annroot = os.path.dirname(os.path.join(dirhere))
sys.path.insert(0, annroot)
# sys.path.insert(0, dirhere)

import annalist

# from annalist_manager       import am_errors
import am_errors
from am_runtests            import am_runtests
from am_runserver           import am_runserver, am_serverlog, am_sitedirectory, am_version
from am_initialize          import am_initialize
from am_createuser          import (
    am_createadminuser, am_defaultadminuser, am_updateadminuser, 
    am_setdefaultpermissions, am_setpublicpermissions,
    am_deleteuser
    )
from am_createsite          import am_createsite, am_updatesite
from am_help                import am_help, command_summary_help

VERSION = annalist.__version__

def progname(args):
    return os.path.basename(args[0])

def parseCommandArgs(argv):
    """
    Parse command line arguments

    argv            argument list from command line

    Returns a pair consisting of options specified as returned by
    OptionParser, and any remaining unparsed arguments.
    """
    # create a parser for the command line options
    parser = argparse.ArgumentParser(
                description="Annalist site management utility",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=command_summary_help
                )
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument("-c", "--configuration",
                        action='store',
                        dest="configuration", metavar="CONFIG",
                        default="personal",
                        #choices=['personal', 'shared', 'devel', 'runtests'],
                        help="Select site configuration by name (e.g. personal, shared, devel, runtests.")
    parser.add_argument("-p", "--personal",
                        action='store_true',
                        dest="config_p", # metavar="PERSONAL",
                        help="Select personal site configuration.")
    parser.add_argument("-d", "--development",
                        action='store_true',
                        dest="config_d", # metavar="DEVELOPMENT",
                        help="Select development site configuration.")
    parser.add_argument("-s", "--shared",
                        action='store_true',
                        dest="config_s", # metavar="SHARED",
                        help="Select shared site configuration.")
    parser.add_argument("-f", "--force",
                        action='store_true',
                        dest="force",
                        help="Force overwrite of existing site data.")
    parser.add_argument("--debug",
                        action="store_true", 
                        dest="debug", 
                        default=False,
                        help="Run with full debug output enabled")
    parser.add_argument("command", metavar="COMMAND",
                        nargs=None,
                        help="sub-command, one of the options listed below."
                        )
    parser.add_argument("args", metavar="ARGS",
                        nargs="*",
                        help="Additional arguments, depending on the command used."
                        )
    # parse command line now
    options = parser.parse_args(argv)
    if options:
        if options.config_d: options.configuration = "devel"
        if options.config_p: options.configuration = "personal"
        if options.config_s: options.configuration = "shared"
        if options and options.command:
            return options
    print("No valid usage option given.", file=sys.stderr)
    parser.print_usage()
    return None

def run(userhome, userconfig, options, progname):
    """
    Command line tool to create and submit deposit information packages
    """
    if options.command.startswith("runt"):                  # runtests
        return am_runtests(annroot, options)
    if options.command.startswith("init"):                  # initialize (intsllaation, django database)
        return am_initialize(annroot, userhome, userconfig, options)
    if options.command.startswith("createa"):               # createadminuser
        return am_createadminuser(annroot, userhome, options)
    if options.command.startswith("defaulta"):              # defaultadminuser
        return am_defaultadminuser(annroot, userhome, options)
    if options.command.startswith("updatea"):               # updateadminuser
        return am_updateadminuser(annroot, userhome, options)
    if options.command.startswith("setdef"):                # setdefaultpermissions
        return am_setdefaultpermissions(annroot, userhome, options)
    if options.command.startswith("setpub"):                # setpublicpermissions
        return am_setpublicpermissions(annroot, userhome, options)
    if options.command.startswith("deleteu"):               # deleteuser
        return am_deleteuser(annroot, userhome, options)
    if options.command.startswith("creates"):               # createsitedata
        return am_createsite(annroot, userhome, options)
    if options.command.startswith("updates"):               # updatesitedata
        return am_updatesite(annroot, userhome, options)
    if options.command.startswith("runs"):                  # runserver
        return am_runserver(annroot, userhome, options)
    if options.command.startswith("serv"):                  # serverlog
        return am_serverlog(annroot, userhome, options)
    if options.command.startswith("site"):                  # sitedir
        return am_sitedirectory(annroot, userhome, options)
    if options.command.startswith("ver"):                   # version
        return am_version(annroot, userhome, options)
    if options.command.startswith("help"):
        return am_help(options, progname)
    print("Un-recognised sub-command: %s"%(options.command), file=sys.stderr)
    print("Use '%s --help' to see usage summary"%(progname), file=sys.stderr)        
    return am_errors.AM_BADCMD

def runCommand(userhome, userconfig, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    options = parseCommandArgs(argv[1:])
    if options and options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    # log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
    # log.debug("Options: %s"%(repr(options)))
    # else:
    #     logging.basicConfig()
    if options:
        progname = os.path.basename(argv[0])
        status   = run(userhome, userconfig, options, progname)
    else:
        status = am_errors.AM_BADCMD
    return status

def runMain():
    """
    Main program transfer function for setup.py console script
    """
    userhome   = os.path.expanduser("~")
    userconfig = os.path.join(userhome, ".annalist")
    return runCommand(userhome, userconfig, sys.argv)

if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, p)
    status = runMain()
    sys.exit(status)

# Tests
#
# python am_main.py runtests
# python am_main.py --config=runtests initialize
# python am_main.py --config=runtests createadminuser testtestadmin testestadmin@localhost
# python am_main.py --config=runtests createadminuser testtestadmin testestadmin@localhost
# python am_main.py --config=runtests deleteuser testtestadmin
# python am_main.py --config=runtests deleteuser testtestadmin
# python am_main.py --config=runtests updateadminuser gklyne
# python am_main.py --config=runtests setdefaultpermissions "VIEW CREATE TEST"
# python am_main.py --config=runtests setpublicpermissions "VIEW TEST"
# python am_main.py --config=runtests updatesitedata

# End.

