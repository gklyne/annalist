"""
Annalist test initialization support
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import unittest
# import doctest
import os.path
import shutil

# from django.test import TestCase
from django.conf import settings

from annalist                       import layout
from annalist.util                  import replacetree, removetree

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import test_layout
from entity_testutils               import collection_create_values
from entity_testtypedata            import recordtype_create_values

sitedata_target_reset = "all"

def resetSitedata(scope="all"):
    """
    Set flag to reset site and/or collection data at next test initialization
    """
    global sitedata_target_reset
    if sitedata_target_reset != "all":
        if scope != "collections":
            scope="all"
        sitedata_target_reset = scope
    return

def copySitedata(src, sitedatasrc, tgt):
    """
    Creates a set of Annalist site data by making a copy of a specified
    source tree.

    src         source directory containing site collection test data to be copied
    sitedatasrc source directory containing standard site data to be copied
    tgt         target directory in which the site data is created
    """
    # Confirm existence of target directory
    log.debug("copySitedata: src %s"%(src))
    log.debug("copySitedata: tgt %s"%(tgt))
    assert os.path.exists(src), "Check source directory (%s)"%(src)
    assert os.path.exists(sitedatasrc), "Check site data source directory (%s)"%(sitedatasrc)
    assert tgt.startswith(TestBaseDir)
    # Site data is not updated by the tests, so initialize it just once for each test suite run
    sitedatatgt = os.path.join(tgt, test_layout.SITEDATA_META_DIR)
    global sitedata_target_reset
    if sitedata_target_reset == "all":
        replacetree(src, tgt)
        for sdir in ("users", "types", "lists", "views", "groups", "fields", "vocabs", "enums"):
            s = os.path.join(sitedatasrc, sdir)
            d = os.path.join(sitedatatgt, sdir)
            replacetree(s, d)
    elif sitedata_target_reset == "collections":
        ds = os.path.join(src, "c")
        dt = os.path.join(tgt, "c")
        # Update collections, not site data; first remove old collections
        for coll_id in os.listdir(dt):
            if coll_id != layout.SITEDATA_ID:
                d = os.path.join(dt, coll_id)
                removetree(d)
        for coll_id in os.listdir(ds):
            if coll_id != layout.SITEDATA_ID:
                s = os.path.join(ds, coll_id)
                d = os.path.join(dt, coll_id)
                shutil.copytree(s, d)
    sitedata_target_reset = "none"
    # Confirm existence of target directories
    assert os.path.exists(tgt), "checking target directory created (%s)"%(tgt)
    assert os.path.exists(sitedatatgt), "checking target sitedata directory created (%s)"%(sitedatatgt)
    return tgt

def init_annalist_test_site():
    log.debug("init_annalist_test_site")
    copySitedata(
        settings.SITE_SRC_ROOT+"/sampledata/testinit/"+test_layout.SITE_DIR, 
        settings.SITE_SRC_ROOT+"/annalist/data/sitedata",
        TestBaseDir)
    testsite = Site(TestBaseUri, TestBaseDir)
    testsite.generate_site_jsonld_context()
    return testsite

def init_annalist_bib_site():
    log.debug("init_annalist_bib_site")
    copySitedata(
        settings.SITE_SRC_ROOT+"/sampledata/bibtestinit/"+test_layout.SITE_DIR, 
        settings.SITE_SRC_ROOT+"/annalist/data/sitedata",
        TestBaseDir)
    testsite = Site(TestBaseUri, TestBaseDir)
    testsite.generate_site_jsonld_context()
    return testsite

def entitydata_create_values(coll, etype, entity_id, update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s %s/%s/%s'%(update, coll._entityid, etype._entityid, entity_id)
        , 'rdfs:comment': '%s coll %s, type %s, entity %s'%(update, coll._entityid, etype._entityid, entity_id)
        })

def init_annalist_test_coll(coll_id="testcoll", type_id="testtype"):
    log.debug("init_annalist_test_coll")
    testsite = Site(TestBaseUri, TestBaseDir)
    testcoll = Collection.create(testsite, coll_id, collection_create_values(coll_id))
    testtype = RecordType.create(testcoll, type_id, recordtype_create_values(coll_id, type_id))
    testdata = RecordTypeData.create(testcoll, type_id, {})
    teste    = EntityData.create(
        testdata, "entity1", 
        entitydata_create_values(testcoll,testtype,"entity1")
        )
    testcoll.generate_coll_jsonld_context()
    return testcoll

def init_annalist_bib_coll(coll_id="testcoll", type_id="testtype"):
    """
    Similar to init_annalist_test_coll, but collection also inherits bibliographic structure definitions.
    """
    log.debug("init_annalist_bib_coll")
    testsite = Site(TestBaseUri, TestBaseDir)
    bib_coll = Collection.load(testsite, layout.BIBDATA_ID)
    testcoll = Collection.create(testsite, coll_id, collection_create_values(coll_id))
    testcoll.set_alt_entities(bib_coll)
    testcoll._save()
    testtype = RecordType.create(testcoll, type_id, recordtype_create_values(coll_id, type_id))
    testdata = RecordTypeData.create(testcoll, type_id, {})
    teste    = EntityData.create(
        testdata, "entity1", 
        entitydata_create_values(testcoll,testtype,"entity1")
        )
    testcoll.generate_coll_jsonld_context()
    return testcoll

# End.
