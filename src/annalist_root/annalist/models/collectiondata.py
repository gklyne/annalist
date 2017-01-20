"""
Annalist collection data management utilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil
import json
import datetime
from collections    import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                       import layout
from annalist                       import message
from annalist.identifiers           import ANNAL
from annalist.util                  import replacetree, updatetree

from annalist.models.site           import Site
from annalist.models.entityfinder   import EntityFinder
from annalist.models.entitytypeinfo import EntityTypeInfo

def initialize_coll_data(src_data_dir, tgt_coll):
    """
    Initialize data in the specified target collection using definitions in
    the specified source directory.  This is used for copying installable
    data collections from the Annalist installed software into the site
    data area.

    returns     list of error messages; an empty list indicates success.
    """
    tgt_data_dir, data_file = tgt_coll._dir_path()
    log.info("Copy Annalist collection data from %s to %s"%(src_data_dir, tgt_data_dir))
    for sdir in layout.DATA_VOCAB_DIRS:     # Don't copy user permissions
        if os.path.isdir(os.path.join(src_data_dir, sdir)):
            log.info("- %s -> %s"%(sdir, tgt_data_dir))
            Site.replace_site_data_dir(tgt_coll, sdir, src_data_dir)
    # Copy entity data to target collection.
    expand_entitydata = os.path.join(src_data_dir, "entitydata" )
    if os.path.isdir(expand_entitydata):
        log.info("- Copy entitydata/...")
        for edir in os.listdir(expand_entitydata):
            if os.path.isdir(os.path.join(expand_entitydata, edir)):
                log.info("- %s -> %s"%(edir, tgt_data_dir))
                Site.replace_site_data_dir(tgt_coll, edir, expand_entitydata)
    # Generate initial JSON-LD context data
    tgt_coll.generate_coll_jsonld_context()
    return []

def copy_coll_data(src_coll, tgt_coll):
    """
    Copy collection data from specified source to target collection.

    returns     list of error messages; an empty list indicates success.
    """
    log.info("Copying collection '%s' to '%s'"%(src_coll.get_id(), tgt_coll.get_id()))
    msgs = []
    entityfinder = EntityFinder(src_coll)
    for e in entityfinder.get_entities():
        entity_id  = e.get_id()
        typeinfo   = EntityTypeInfo(
            tgt_coll, e.get_type_id(), create_typedata=True
            )
        new_entity = typeinfo.create_entity(entity_id, e.get_values())
        if not typeinfo.entity_exists(entity_id):
            msg = (
                "Collection.copy_coll_data: Failed to create entity %s/%s"%
                    (typeinfo.type_id, entity_id)
                )
            log.warning(msg)
            msgs.append(msg)
        msgs += new_entity._copy_entity_files(e)
    return msgs

def migrate_collection_dir(coll, prev_dir, curr_dir):
    """
    Migrate (rename) a single directory belonging to the indicated collection.

    Returns list of errors or empty list.
    """
    errs = []
    if not prev_dir:
        return errs
    coll_base_dir, coll_meta_file = coll._dir_path()
    # log.debug(
    #     "collectiondata.migrate_collection_dir %s: %s -> %s"%
    #     (coll_base_dir, prev_dir, curr_dir)
    #     )
    expand_prev_dir = os.path.join(coll_base_dir, prev_dir)
    expand_curr_dir = os.path.join(coll_base_dir, curr_dir)
    # log.debug("  prev %s"%(expand_prev_dir,))
    # log.debug("  curr %s"%(expand_curr_dir,))
    if (curr_dir != prev_dir) and os.path.isdir(expand_prev_dir):
        log.info("migrate_coll_base_dir: %s"%coll_base_dir)
        log.info("               rename: %s -> %s"%(prev_dir, curr_dir))
        # print "@@ rename %s -> %s"%(expand_prev_dir, expand_curr_dir)
        try:
            os.rename(expand_prev_dir, expand_curr_dir)
        except Exception as e:
            msg = message.COLL_MIGRATE_DIR_FAILED%(coll.get_id(), prev_dir, curr_dir, e)
            # print "@@ "+msg
            log.error("migrate_collection_dir: "+msg)
            errs.append(msg)
    return errs

def migrate_coll_config_dirs(coll):
    """
    Migrate (rename) collection configuration directories.

    Returns list of errors or empty list.
    """
    errs = []
    for curr_dir, prev_dir in layout.COLL_DIRS_CURR_PREV:
        # print "@@ migrate coll dir %s -> %s"%(prev_dir, curr_dir)
        e = migrate_collection_dir(coll, prev_dir, curr_dir)
        if e:
            errs.extend(e)
    return errs

def migrate_coll_data(coll):
    """
    Migrate collection data for specified collection

    Returns list of errors or empty list.
    """
    log.info("Migrate Annalist collection data for %s"%(coll.get_id()))
    errs = migrate_coll_config_dirs(coll)
    if errs:
        return errs
    entityfinder = EntityFinder(coll)
    for e in entityfinder.get_entities():
        coll.update_entity_types(e)
        log.info("migrate_coll_data: %s/%s"%(e[ANNAL.CURIE.type_id], e[ANNAL.CURIE.id]))
        e._save(post_update_flags={"nocontext"})
    coll.generate_coll_jsonld_context()    
    return errs

# End.
