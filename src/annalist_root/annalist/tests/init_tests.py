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
import datetime

# from django.test import TestCase
from django.conf import settings

from annalist                       import layout
from annalist.util                  import replacetree, removetree
from annalist.collections           import installable_collections
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData
from annalist.models.collectiondata import initialize_coll_data, copy_coll_data, migrate_coll_data

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
    sitedatatgt = os.path.join(tgt, test_layout.SITEDATA_BASE_DIR)
    global sitedata_target_reset
    if sitedata_target_reset == "all":
        replacetree(src, tgt)
        for sdir in layout.COLL_DIRS:
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
    # Reset id generator counters
    EntityData._last_id   = 0
    RecordType._last_id   = 0
    RecordView._last_id   = 0
    RecordList._last_id   = 0
    RecordField._last_id  = 0
    AnnalistUser._last_id = 0
    return testsite

def entitydata_create_values(coll, etype, entity_id, update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s %s/%s/%s'%(update, coll._entityid, etype._entityid, entity_id)
        , 'rdfs:comment': '%s coll %s, type %s, entity %s'%(update, coll._entityid, etype._entityid, entity_id)
        })

def install_annalist_named_coll(coll_id):
    coll_src_dir = installable_collections[coll_id]['data_dir']
    site         = Site(TestBaseUri, TestBaseDir)
    # Install collection now
    src_dir = os.path.join(settings.SITE_SRC_ROOT, "annalist/data", coll_src_dir)
    log.debug("Installing collection '%s' from data directory '%s'"%(coll_id, src_dir))
    coll_metadata = installable_collections[coll_id]['coll_meta']
    date_time_now = datetime.datetime.now().replace(microsecond=0)
    coll_metadata[ANNAL.CURIE.comment] = (
        "Initialized at %s by `annalist.tests.init_tests.install_annalist_named_coll`"%
        date_time_now.isoformat()
        )
    coll = site.add_collection(coll_id, coll_metadata)
    # print "@@ src_dir %s"%src_dir
    # print "@@ coll_id %s, coll_dir %s"%(coll_id, coll._entitydir)
    msgs = initialize_coll_data(src_dir, coll)
    if msgs:
        for msg in msgs:
            log.warning(msg)
        assert False, "\n".join(msgs)
    return coll

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
    # Reset id generator counters
    EntityData._last_id   = 0
    RecordType._last_id   = 0
    RecordView._last_id   = 0
    RecordList._last_id   = 0
    RecordField._last_id  = 0
    AnnalistUser._last_id = 0
    return testcoll

def create_test_coll_inheriting(
        base_coll_id=None, coll_id="testcoll", type_id="testtype"):
    """
    Similar to init_annalist_test_coll, but collection also
    inherits from named collection.
    """
    testsite  = Site(TestBaseUri, TestBaseDir)
    basecoll  = Collection.load(testsite, base_coll_id)
    if not basecoll:
        msg = "Base collection %s not found"%base_coll_id
        log.warning(msg)
        assert False, msg
    testcoll  = Collection.create(testsite, coll_id, collection_create_values(coll_id))
    testcoll.set_alt_entities(basecoll)
    testcoll._save()
    testtype  = RecordType.create(testcoll, type_id, recordtype_create_values(coll_id, type_id))
    testdata  = RecordTypeData.create(testcoll, type_id, {})
    teste     = EntityData.create(
        testdata, "entity1", 
        entitydata_create_values(testcoll, testtype, "entity1")
        )
    testcoll.generate_coll_jsonld_context()
    return testcoll

def init_annalist_named_test_coll(
        base_coll_id=None, coll_id="testcoll", type_id="testtype"):
    """
    Similar to init_annalist_test_coll, but collection also installs and 
    inherits from named collection definitions.
    """
    # @@TODO: DRY: use create_test_coll_inheriting
    # @@TODO: rename: install_create_test_coll_inheriting
    log.debug("init_annalist_named_test_coll")
    testsite  = Site(TestBaseUri, TestBaseDir)
    namedcoll = install_annalist_named_coll(base_coll_id)
    testcoll  = Collection.create(testsite, coll_id, collection_create_values(coll_id))
    testcoll.set_alt_entities(namedcoll)
    testcoll._save()
    testtype  = RecordType.create(testcoll, type_id, recordtype_create_values(coll_id, type_id))
    testdata  = RecordTypeData.create(testcoll, type_id, {})
    teste     = EntityData.create(
        testdata, "entity1", 
        entitydata_create_values(testcoll, testtype, "entity1")
        )
    testcoll.generate_coll_jsonld_context()
    return testcoll

# End.
