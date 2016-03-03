"""
Collection migration helpers
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess
import importlib
import shutil

log = logging.getLogger(__name__)

from annalist.identifiers           import ANNAL, RDFS
from annalist.models.collection     import Collection

# from utils.SetcwdContext            import ChangeCurrentDir
# from utils.SuppressLoggingContext   import SuppressLogging
# from annalist                       import __version__

import am_errors
from am_settings                    import am_get_settings, am_get_site_settings, am_get_site
from am_getargvalue                 import getarg, getargvalue

def am_migratecollection(annroot, userhome, options):
    """
    Migrate collection helper

        annalist_manager migratecollection old_coll new_coll

    Generates a report of changes to data needed to match type and property 
    URI changes moving from old_coll to new_coll.

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
    if len(options.args) > 2:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    sitesettings = am_get_site_settings(annroot, userhome, options)
    if not sitesettings:
        print("Site settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    site        = am_get_site(sitesettings)
    old_coll_id = getargvalue(getarg(options.args, 0), "Old collection Id: ")
    old_coll    = Collection.load(site, old_coll_id)
    if not (old_coll and old_coll.get_values()):
        print("Old collection not found: %s"%(old_coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    new_coll_id = getargvalue(getarg(options.args, 1), "New collection Id: ")
    new_coll    = Collection.load(site, new_coll_id)
    if not (new_coll and new_coll.get_values()):
        print("New collection not found: %s"%(new_coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    status      = am_errors.AM_SUCCESS
    new_coll    = Collection(site, new_coll_id)

    # Scan and report on type URI changes
    print("Type URI changes from %s to %s:"%(old_coll_id, new_coll_id))
    for new_type in new_coll.types():
        type_id  = new_type.get_id()
        old_type = old_coll.get_type(type_id)
        if old_type:
            old_uri  = old_type[ANNAL.CURIE.uri]
            if old_uri != new_type[ANNAL.CURIE.uri]:
                print("  Type %s, URI changed from %s to %s"%(type_id, old_uri, new_type[ANNAL.CURIE.uri]))
                supertype_uris = [ u[ANNAL.CURIE.supertype_uri] for u in new_type.get(ANNAL.CURIE.supertype_uris,[]) ]
                if old_uri not in supertype_uris:
                    print("  >> Add supertype '%s' to type '%s' in collection '%s'"%(old_uri, type_id, new_coll_id))
    return status

# End.
