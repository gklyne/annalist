"""
Create Annalist/Django site data.

Note: uses data in `sampledata/empty/annalist_site`
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
# import shutil

log = logging.getLogger(__name__)

from annalist.identifiers           import ANNAL, RDFS
from annalist                       import layout
from annalist.util                  import removetree, replacetree, updatetree

from annalist.models.site           import Site

import am_errors
from am_settings                    import am_get_settings, am_get_site_settings

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
    status       = am_errors.AM_SUCCESS
    sitesettings = am_get_site_settings(annroot, userhome, options) 
    if not sitesettings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print(
            "Unexpected arguments for %s: (%s)"%
            (options.command, " ".join(options.args)), 
            file=sys.stderr
            )
        return am_errors.AM_UNEXPECTEDARGS
    site_layout = layout.Layout(sitesettings.BASE_DATA_DIR)
    sitebasedir = site_layout.SITE_PATH
    sitebaseurl = "/annalist/"     # @@TODO: figure more robust way to define this
    # --- If old site exists and --force option given, remove it
    if os.path.exists(os.path.join(sitebasedir, site_layout.SITEDATA_DIR)):
        if options.force:
            print("Removing old Annalist site at %s"%(sitebasedir))
            log.info("rmtree: %s"%(sitebasedir))
            removetree(sitebasedir)
        else:
            print(
                "Old data already exists at %s (use --force or -f to overwrite)"%
                (sitebasedir), file=sys.stderr
                )
            return am_errors.AM_EXISTS
    # --- Initialize empty site data in target directory
    print("Initializing Annalist site in %s"%(sitebasedir))
    site = Site.create_empty_site_data(
        sitebaseurl, sitebasedir,
        label="Annalist site (%s configuration)"%options.configuration, 
        description="Annalist %s site metadata and site-wide values."%options.configuration
        )
    sitedata = site.site_data_collection()
    Site.create_site_readme(site)
    site_data_src = os.path.join(annroot, "annalist/data/sitedata")     # @@TODO: more robust definition
    site_data_tgt, site_data_file = sitedata._dir_path()
    print("Copy Annalist site data")
    print("from %s"%site_data_src)
    for sdir in layout.COLL_DIRS:
        print("- %s -> %s"%(sdir, site_data_tgt))
        Site.replace_site_data_dir(sitedata, sdir, site_data_src)
    print("Generating %s"%(site_layout.SITEDATA_CONTEXT_DIR))
    sitedata.generate_coll_jsonld_context()
    print("Now run 'annalist-manager initialize' to create site admin database")
    return status

def migrate_old_data(old_site_dir, old_data_dir, new_site_dir, new_data_dir):
    """
    Migrate data from a single old-site directory to the new site
    """
    old_dir        = os.path.join(old_site_dir, old_data_dir)
    old_dir_backup = os.path.join(old_site_dir, "backup_"+old_data_dir)
    new_dir        = os.path.join(new_site_dir, new_data_dir)
    if os.path.isdir(old_dir):
        print("- %s +> %s (migrating)"%(old_dir, new_dir))
        updatetree(old_dir, new_dir)
        archive_old_data(old_site_dir, old_data_dir)
        # print("- %s >> %s (rename)"%(old_dir, old_dir_backup))
        # os.rename(old_dir, old_dir_backup)
    return

def archive_old_data(site_dir, data_dir):
    """
    Archive old data no longer required.
    """
    old_dir     = os.path.join(site_dir, data_dir)
    arc_dir     = "old_"+data_dir
    old_dir_arc = os.path.join(site_dir, arc_dir)
    if os.path.isdir(old_dir):
        print("- %s >> %s (rename)"%(old_dir, arc_dir))
        os.rename(old_dir, old_dir_arc)
    return

def remove_old_data(site_dir, data_dir):
    """
    Remove old data no longer required.
    """
    old_dir = os.path.join(site_dir, data_dir)
    if os.path.isdir(old_dir):
        print("- %s (remove)"%(old_dir,))
        removetree(old_dir)
    return

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
    status       = am_errors.AM_SUCCESS
    sitesettings = am_get_site_settings(annroot, userhome, options) 
    if not sitesettings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        return am_errors.AM_NOSETTINGS
    if len(options.args) > 0:
        print(
            "Unexpected arguments for %s: (%s)"%
            (options.command, " ".join(options.args)), 
            file=sys.stderr
            )
        return am_errors.AM_UNEXPECTEDARGS
    site_layout   = layout.Layout(sitesettings.BASE_DATA_DIR)
    sitebasedir   = site_layout.SITE_PATH
    sitebaseurl   = "/annalist/"                # @@TODO: figure more robust way to define this
    site          = Site(sitebaseurl, site_layout.SITE_PATH)
    sitedata      = site.site_data_collection(test_exists=False)
    if sitedata is None:
        print("Initializing Annalist site metadata in %s (migrating to new layout)"%(sitebasedir))
        site = Site.create_empty_site_data(
            sitebaseurl, sitebasedir,
            label="Annalist site (%s configuration)"%options.configuration, 
            description="Annalist %s site metadata and site-wide values."%options.configuration
            )
        sitedata      = site.site_data_collection()
    site_data_src = os.path.join(annroot, "annalist/data/sitedata")  # @@TODO: more robust definition
    site_data_tgt, site_data_file = sitedata._dir_path()
    # --- Migrate old site data to new site directory
    site_data_old = os.path.join(sitebasedir, site_layout.SITEDATA_OLD_DIR)
    old_users     = os.path.join(site_data_old, layout.USER_DIR_PREV)
    old_vocabs    = os.path.join(site_data_old, layout.VOCAB_DIR_PREV)
    if os.path.isdir(old_users) or os.path.isdir(old_vocabs):
        print("Copy Annalist old user and/or vocab data from %s"%site_data_old)
        migrate_old_data(site_data_old, layout.USER_DIR_PREV,  site_data_tgt, layout.USER_DIR )
        migrate_old_data(site_data_old, layout.VOCAB_DIR_PREV, site_data_tgt, layout.VOCAB_DIR)
    #@@
    # if os.path.isdir(old_users) or os.path.isdir(old_vocabs):
    #     print("Copy Annalist old user and/or vocab data from %s"%site_data_old)
    #     for sdir in ("users", "vocabs"):
    #         s     = os.path.join(site_data_old, sdir)
    #         old_s = os.path.join(site_data_old, "old_"+sdir)
    #         d     = os.path.join(site_data_tgt, sdir)
    #         if os.path.isdir(s):
    #             print("- %s +> %s (migrating)"%(sdir, d))
    #             updatetree(s, d)
    #             print("- %s >> %s (rename)"%(sdir, old_s))
    #             os.rename(s, old_s)
    #@@
    # --- Copy latest site data to target directory
    print("Copy Annalist site data")
    print("from %s"%site_data_src)
    for sdir in layout.DATA_DIRS:
        print("- %s -> %s"%(sdir, site_data_tgt))
        Site.replace_site_data_dir(sitedata, sdir, site_data_src)
    for sdir in (layout.USER_DIR, layout.VOCAB_DIR):
        print("- %s +> %s"%(sdir, site_data_tgt))
        Site.update_site_data_dir(sitedata, sdir, site_data_src)
    for sdir in layout.COLL_DIRS_PREV:
        remove_old_data(site_data_tgt, sdir)
    print("Generating %s"%(site_layout.SITEDATA_CONTEXT_DIR))
    sitedata.generate_coll_jsonld_context()
    # --- Copy provider data to site config provider directory
    provider_dir_tgt = os.path.join(sitesettings.CONFIG_BASE, "providers")
    provider_dir_src = os.path.join(annroot, "annalist/data/identity_providers")
    print("Copy identity provider data:")
    print("- from: %s"%(provider_dir_src,))
    print("-   to: %s"%(provider_dir_tgt,))
    updatetree(provider_dir_src, provider_dir_tgt)
    return status

# End.
