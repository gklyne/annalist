"""
Create Annalist/Django site data.
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess
import importlib
import shutil

log = logging.getLogger(__name__)

from utils.SetcwdContext            import ChangeCurrentDir
from utils.SuppressLoggingContext   import SuppressLogging

from annalist.identifiers           import ANNAL, RDFS
from annalist.layout                import Layout
from annalist.util                  import removetree, replacetree, updatetree

import am_errors
from am_settings                    import am_get_settings

def am_createsite(annroot, userhome, options):
    """
    Create Annalist empty site data.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    options.configuration = "runtests"
    testsettings = am_get_settings(annroot, "/nouser/", options)
    if not testsettings:
        print("Settings not found (%s)"%("runtests"), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status       = am_errors.AM_SUCCESS
    emptysitedir = os.path.join(annroot, "sampledata/empty/annalist_site")
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitebasedir  = os.path.join(sitesettings.BASE_DATA_DIR, "annalist_site")
    # Test if old site exists
    if os.path.exists(sitebasedir):
        if options.force:
            # --- Remove old site data from target area
            print("Removing old Annalist site at %s"%(sitebasedir))
            log.info("rmtree: %s"%(sitebasedir))
            removetree(sitebasedir)
        else:
            print("Old data already exists at %s (use --force lor -f to overwrite)"%(sitebasedir), file=sys.stderr)
            return am_errors.AM_EXISTS
    # --- Copy empty site data to target area
    print("Initializing Annalist site in %s"%(sitebasedir))
    log.info("copytree: %s to %s"%(emptysitedir, sitebasedir))
    shutil.copytree(emptysitedir, sitebasedir)
    # --- Copy built-in types and views data to target area
    site_layout = Layout(sitesettings.BASE_DATA_DIR)
    sitedatasrc = os.path.join(annroot, "annalist/sitedata")
    sitedatatgt = os.path.join(sitebasedir, site_layout.SITEDATA_DIR)
    print("Copy Annalist site data from %s to %s"%(sitedatasrc, sitedatatgt))
    for sdir in ("types", "lists", "views", "groups", "fields", "enums", "users"):
        s = os.path.join(sitedatasrc, sdir)
        d = os.path.join(sitedatatgt, sdir)
        print("- %s -> %s"%(sdir, d))
        shutil.copytree(s, d)
    return status

def am_updatesite(annroot, userhome, options):
    """
    Update site data, leaving user data alone

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    settings = am_get_settings(annroot, userhome, options)
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    status = am_errors.AM_SUCCESS
    with SuppressLogging(logging.INFO):
        sitesettings = importlib.import_module(settings.modulename)
    sitebasedir  = os.path.join(sitesettings.BASE_DATA_DIR, "annalist_site")
    # Test if site exists
    if not os.path.exists(sitebasedir):
        print("Site %s not found"%(sitebasedir), file=sys.stderr)
        return am_errors.AM_NOTEXISTS
    # --- Copy built-in types and views data to target area
    site_layout = Layout(sitesettings.BASE_DATA_DIR)
    sitedatasrc = os.path.join(annroot, "annalist/sitedata")
    sitedatatgt = os.path.join(sitebasedir, site_layout.SITEDATA_DIR)
    print("Copy Annalist site data from %s to %s"%(sitedatasrc, sitedatatgt))
    for sdir in ("types", "lists", "views", "groups", "fields", "enums"):
        s = os.path.join(sitedatasrc, sdir)
        d = os.path.join(sitedatatgt, sdir)
        print("- %s => %s"%(sdir, d))
        replacetree(s, d)
    for sdir in ("users",):
        s = os.path.join(sitedatasrc, sdir)
        d = os.path.join(sitedatatgt, sdir)
        print("- %s +> %s"%(sdir, d))
        updatetree(s, d)
    return status

# End.
