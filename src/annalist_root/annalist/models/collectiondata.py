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
from annalist.util                  import replacetree, updatetree

from annalist.models.site           import Site
from annalist.models.entityfinder   import EntityFinder
from annalist.models.entitytypeinfo import EntityTypeInfo

def initialize_coll_data(src_data_dir, tgt_coll):
    """
    Initialize data in the specified target collection using definitions in
    the specified source directory.

    returns     list of error messages; an empty list indicates success.
    """
    tgt_data_dir, data_file = tgt_coll._dir_path()
    log.info("Copy Annalist collection data from %s to %s"%(src_data_dir, tgt_data_dir))
    for sdir in ("enums", "fields", "groups", "lists", "types", "views", "vocabs"):
        expand_sdir = os.path.join(src_data_dir, sdir)
        if os.path.isdir(expand_sdir):
            log.info("- %s -> %s"%(sdir, tgt_data_dir))
            Site.replace_site_data_dir(tgt_coll, sdir, src_data_dir)
    # Copy entity data to target collection.
    #
    # @TODO: This is hacky: it would be cleaner if the source directory were just
    #        an exact copy of what ends up in the target collection directory.
    #
    expand_sdir = os.path.join(src_data_dir, "entitydata" )
    expand_tdir = os.path.join(
        tgt_data_dir, layout.META_COLL_REF+layout.COLL_ENTITYDATA_PATH
        )
    if os.path.isdir(expand_sdir):
        log.info("- %s -> %s"%(sdir, expand_tdir))
        replacetree(expand_sdir, expand_tdir)
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

def migrate_coll_data(coll):
    """
    Migrate collection data for specified collection

    returns     list of error messages; an empty list indicates success.
    """
    log.info("Migrate Annalist collection data for %s"%(coll.get_id()))
    entityfinder = EntityFinder(coll)
    for e in entityfinder.get_entities():
        e._save()
    return []

# End.
