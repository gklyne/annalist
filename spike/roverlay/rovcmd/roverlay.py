# !/usr/bin/env python
#
# roverlay.py - command line tool to interact with roverlay web service.
#

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import os.path
import re
import argparse
import logging
import csv
import socket
import errno

log = logging.getLogger(__name__)

# Make sure MiscUtils can be found on path
if __name__ == "__main__":
    sys.path.append(os.path.join(sys.path[0],"../.."))

from miscutils.HttpSession import HTTP_Session
from miscutils import ro_utils
from miscutils import ro_uriutils

VERSION = "0.1"

roweb_default = "http://localhost:8000/rovserver/"

def run(configbase, filebase, options, progname):
    """
    Command line tool to create and display ROs managed by the Overlay RO service.
    """
    status = 0
    # Create new Overlay RO and returns its URI
    with HTTP_Session(options.serviceuri) as rovsession:
        try:
            rovsession.doRequest(options.serviceuri, method="HEAD")
        except socket.error, e:
            (errnum, errstr) = e.args
            if errnum == errno.ECONNREFUSED:
                print "Connection to %s refused: is the Overlay RO server running?"%(options.serviceuri)
                return 2
            else:
                raise
        if options.list:
            (status, reason, respheaders, respbody) = rovsession.doRequest(
                options.serviceuri, method="GET", accept="text/uri-list")
            if status == 200:
                for u in respbody.splitlines():
                    if u: print u
            else:
                print "Failed to retrieve RO list (%03d %s)"%(status, reason)
                status = 2
        elif options.delete:
            (status, reason, respheaders, respbody) = rovsession.doRequest(
                options.delete, method="DELETE")
            if status == 204:
                # Created: write bare URI to standard output so it is easily used in other commands
                print "RO %s deleted."%(options.delete)
            else:
                print "Failed to delete RO %s (%03d %s)"%(options.delete, status, reason)
                status = 2
        elif len(options.uris) > 0:
            resolved_uris = [ ro_uriutils.resolveFileAsUri(u) for u in options.uris ]
            ro_uri_list   = "\n".join(resolved_uris)
            (status, reason, respheaders, respbody) = rovsession.doRequest(
                options.serviceuri,
                method="POST", body=ro_uri_list, ctype="text/uri-list")
            if status == 201:
                # Created: write bare URI to standard output so it is easily used in other commands
                print respheaders['location']
            else:
                print "Failed to create new RO (%03d %s)"%(status, reason)
                status = 2
        else:
            raise Exception("No valid usage option given.")
    # Exit
    return status

def parseCommandArgs(argv):
    """
    Parse command line arguments

    prog -- program name from command line
    argv -- argument list from command line

    Returns a pair consisting of options specified as returned by
    OptionParser, and any remaining unparsed arguments.
    """
    # create a parser for the command line options
    parser = argparse.ArgumentParser(
                description="Create or display Overlay RO through web service.",
                epilog="""
                    On successful creation of a new RO, its URI is written to standard output.
                    """,
                usage=(
                    "\n    %(prog)s [options] URI [URI ...]    # Create new RO"+
                    "\n    %(prog)s -d ROURI                   # Delete RO"+
                    "\n    %(prog)s -l                         # List available ROs"+
                    ""))
    parser.add_argument("uris", metavar="URI",
                        nargs="*",
                        help="One or more URIs that are aggregated in a created RO")
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument("-d", "--delete",
                        dest="delete", metavar="ROURI",
                        default=None,
                        help="Delete specified RO")
    parser.add_argument("-l", "--list",
                        action="store_true", 
                        dest="list",
                        default=False,
                        help="List available ROs art specified service")
    parser.add_argument("-s", "--service-uri",
                        dest="serviceuri",
                        default=roweb_default,
                        help="Overlay RO web service to access. Default %s"%(roweb_default))
    parser.add_argument("--debug",
                        action="store_true", 
                        dest="debug", 
                        default=False,
                        help="Run with full debug output enabled")
    # parse command line now
    options = parser.parse_args(argv)
    if len(options.uris) > 0 or options.delete or options.list:
        log.debug("Options: %s"%(repr(options)))
        return options
    print "No valid usage option given."
    parser.print_usage()
    return None

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
    log.debug("runCommand: configbase %s, filebase %s, argv %s"%(configbase, filebase, repr(argv)))
    # else:
    #     logging.basicConfig()
    status = 1
    if options:
        progname = ro_utils.progname(argv)
        status   = run(configbase, filebase, options, progname)
    return status

def runMain():
    """
    Main program transfer function for setup.py console script
    """
    userhome = os.path.expanduser("~")
    filebase = os.getcwd()
    return runCommand(userhome, filebase, sys.argv)

if __name__ == "__main__":
    """
    Program invoked from the command line.
    """
    status = runMain()
    sys.exit(status)

    # End.

