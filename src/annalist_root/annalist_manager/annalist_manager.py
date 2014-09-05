# !/usr/bin/env python
#
# dip.py - command line tool to create and submit deposit information packages
#

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2013-2014, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import argparse
import logging
import errno

log = logging.getLogger(__name__)

if __name__ == "__main__":
    p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, p)

from dipcmd             import diperrors
from dipcmd.dipconfig   import dip_get_dip_dir, dip_set_default_dir
from dipcmd.dipconfig   import dip_get_service_details, dip_set_service_details, dip_save_service_details
from dipcmd.dipconfig   import dip_show_config
from dipcmd.diplocal    import dip_create, dip_use, dip_show, dip_remove
from dipcmd.diplocal    import dip_add_files, dip_remove_files
from dipcmd.diplocal    import dip_set_attributes, dip_show_attributes, dip_remove_attributes
from dipcmd.dipdeposit  import dip_package, dip_deposit

VERSION = "0.1"

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
                description="Create, manipulate or submit deposit information package",
                epilog=("\n"+
                    "On successful creation of a new DIP, its directory is written to standard output.\n"+
                    "On successful deposit of a DIP, its URI is written to standard output."
                    )
                )
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument("-d", "--dip",
                        dest="dip", metavar="DIP",
                        default=None,
                        help="Directory of DIP")
    parser.add_argument("-p", "--package",
                        dest="package", metavar="PACKAGE",
                        default=None,
                        help="Package for deposit (or other operation...)")
    parser.add_argument("-c", "--collection_uri",
                        dest="collection_uri", metavar="COLLECTON_URI",
                        default=None,
                        help="Collection URI for deposit")
    parser.add_argument("-s", "--servicedoc_uri",
                        dest="servicedoc_uri", metavar="SERVICEDOC_URI",
                        default=None,
                        help="SWORD (AtomPub) service document")
    parser.add_argument("-u", "--username",
                        dest="username", metavar="USERNAME",
                        default=None,
                        help="Username to use for deposit (saved per-collection)")
    parser.add_argument("-w", "--password",
                        dest="password", metavar="PASSWORD",
                        default=None,
                        help="Password to use for deposit (saved per-collection)")
    parser.add_argument("-r", "--recursive",
                        action="store_true", 
                        dest="recursive", 
                        default=False,
                        help="Add or remove files recursively (i.e. scan subdirectories)")
    parser.add_argument("--debug",
                        action="store_true", 
                        dest="debug", 
                        default=False,
                        help="Run with full debug output enabled")
    parser.add_argument("command", metavar="COMMAND",
                        nargs=None,
                        help="sub-command, which is one of: "+
                             "create, use, show, remove-dip, "+
                             "add-files, add-metadata, remove-file, "+
                             "add-attribute, show-attribute, remove-attribute, "+
                             "package, deposit"
                       )
    parser.add_argument("files", metavar="FILES",
                        nargs="*",
                        help="Zero, one or more files that are added to a DIP "+
                             "(add-files and add-metadata sub-commands only).\n"+
                             "Zero, one or more attribute-value pairs that are added to a DIP "+
                             "(add-attributes sub-command only).\n"+
                             "Zero, one or more attribute names that are displayed or removed from a DIP "+
                             "(show-attributes or remove-attributes sub-commands only)."
                        )
    # parse command line now
    options = parser.parse_args(argv)
    if options and options.command:
        return options
    print("No valid usage option given.", file=sys.stderr)
    parser.print_usage()
    return None

def run(configbase, filebase, options, progname):
    """
    Command line tool to create and submit deposit information packages
    """
    status = diperrors.DIP_SUCCESS

    if options.command in ["config", "configure"]:
        # dip_config = readconfig(configbase)
        if (options.dip or options.collection_uri):
            if options.dip:
                (status, dipdir) = dip_get_dip_dir(configbase, filebase, options)
            if options.collection_uri:
                status = dip_set_service_details(configbase, filebase, options)
        else:
            dip_show_config(configbase, filebase)
        if options.dip and status == 0:
            status = dip_set_default_dir(configbase, filebase, dipdir, display=True)

    elif options.command == "create":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options)
        if status == 0:
            status = dip_create(dipdir)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "use":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            status = dip_use(dipdir)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "show":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            status = dip_show(dipdir)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "remove":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=False)
        if status == 0:
            status = dip_remove(dipdir)
        if status == 0:
            dip_set_default_dir(configbase, filebase, None)

    elif options.command in ["add-file","add-files"]:
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            if not options.files:
                print("No files specified for add_files to %s"%dipdir, file=sys.stderr)
                status = diperrors.DIP_NOFILES
            else:
                status = dip_add_files(dipdir, options.files, recursive=options.recursive)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "add-metadata":
        raise NotImplementedError("@@TODO add-metadata")

    elif options.command in  ["remove-file", "remove-files", "remove-metadata"]:
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            if not options.files:
                print("No files specified for remove-file from %s"%dipdir, file=sys.stderr)
                status = diperrors.DIP_NOFILES
            else:
                status = dip_remove_files(dipdir, options.files, recursive=options.recursive)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command in ["add-attribute", "add-attributes"]:
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            if not options.files:
                print("No attributes specified for add-attributes to %s"%dipdir, file=sys.stderr)
                status = diperrors.DIP_NOATTRIBUTES
            else:
                status = dip_set_attributes(dipdir, options.files)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command in ["show-attribute", "show-attributes"]:
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            if not options.files:
                print("No attributes specified for show-attributes from %s"%dipdir, file=sys.stderr)
                status = diperrors.DIP_NOATTRIBUTES
            else:
                status = dip_show_attributes(dipdir, options.files)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command in ["remove-attribute", "remove-attributes"]:
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            if not options.files:
                print("No attributes specified for remove-attributes from %s"%dipdir, file=sys.stderr)
                status = diperrors.DIP_NOATTRIBUTES
            else:
                status = dip_remove_attributes(dipdir, options.files)
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "package":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            # @@TODO: add format option
            status = dip_package(dipdir, basedir=os.getcwd())
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)

    elif options.command == "deposit":
        (status, dipdir) = dip_get_dip_dir(configbase, filebase, options, default=True)
        if status == 0:
            (status, ss) = dip_get_service_details(configbase, filebase, options)
            # log.info("ss: %r"%([ss]))
        if status == 0:
            # @@TODO: add format option
            status = dip_deposit(
                dipdir, 
                collection_uri=ss.collection_uri, servicedoc_uri=ss.servicedoc_uri, 
                username=ss.username, password=ss.password,
                basedir=os.getcwd()
                )
        if status == 0:
            dip_set_default_dir(configbase, filebase, dipdir)
            dip_save_service_details(configbase, filebase, ss)

    else:
        print("Un-recognised sub-command: %s"%(options.command), file=sys.stderr)
        print("Use '%s --help' to see usage summary"%(progname), file=sys.stderr)        
        status = diperrors.DIP_BADCMD
    # Exit
    return status

def runCommand(configbase, filebase, argv):
    """
    Run program with supplied configuration base directory, Base directory
    from which to start looking for research objects, and arguments.

    This is called by main function (below), and also by test suite routines.

    Returns exit status.
    """
    options = parseCommandArgs(argv[1:])
    if options and options.debug:
        logging.basicConfig(level=logging.DEBUG)
    # log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
    # log.debug("Options: %s"%(repr(options)))
    # else:
    #     logging.basicConfig()
    if options:
        progname = os.path.basename(argv[0])
        status   = run(configbase, filebase, options, progname)
    else:
        status = diperrors.DIP_BADCMD
    return status

def runMain():
    """
    Main program transfer function for setup.py console script
    """
    userhome = os.path.join(os.path.expanduser("~"), ".dip_ui")
    filebase = os.getcwd()
    return runCommand(userhome, filebase, sys.argv)

if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, p)
    status = runMain()
    sys.exit(status)

    # End.

