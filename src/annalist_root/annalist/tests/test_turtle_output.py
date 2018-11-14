"""
Test Turtle generation logic
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import unittest
import traceback

from django.test.client             import Client

from rdflib                         import Graph, URIRef, Literal

from utils.py3porting               import urljoin
from utils.SuppressLoggingContext   import SuppressLogging
from miscutils.MockHttpResources    import MockHttpFileResources, MockHttpDictResources

import annalist
from annalist                       import layout
from annalist.identifiers           import makeNamespace, RDF, RDFS, ANNAL
from annalist.util                  import make_resource_url, extract_entity_id

from annalist.models.site           import Site
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.recordvocab    import RecordVocab
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.recordenum     import RecordEnumFactory
from annalist.models.entitydata     import EntityData
from annalist.models.entitytypeinfo import EntityTypeInfo

from .AnnalistTestCase import AnnalistTestCase
from .tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from .init_tests import (
    init_annalist_test_site, 
    init_annalist_test_coll,
    resetSitedata
    )
from .entity_testutils import (
    site_dir, collection_dir,
    site_view_url, collection_view_url,
    collection_resource_url,
    collection_entity_view_url,
    collection_create_values,
    create_test_user
    )
from .entity_testcolldata import (
    collectiondata_url
    )
from .entity_testtypedata import (
    recordtype_url
    )
from .entity_testentitydata import (
    entity_url, entity_resource_url, entity_uriref,
    entitydata_list_type_url, entitydata_list_all_url
    )
from .entity_testsitedata import (
    get_site_types, get_site_types_sorted, get_site_types_linked,
    )

#   -----------------------------------------------------------------------------
#
#   RDF graph utilities
#
#   -----------------------------------------------------------------------------

def property_value(graph, item, prop):
    """
    Returns property value associated with a node in a graph, or None
    """
    return graph.value(item, URIRef(prop))

def scan_list(graph, head):
    """
    Returns an iterator over a list whose head node is supplied.
    """
    while head != URIRef(RDF.URI.nil):
        yield property_value(graph, head, RDF.URI.first)
        head = property_value(graph, head, RDF.URI.rest)
    return

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

_test_test_vocab_create_values = (
    { "annal:type":     "annal:Vocabulary"
    , "rdfs:label":     "Vocabulary namespace for test terms"
    , "rdfs:comment":   "Vocabulary namespace for URIs that are used internally by Annalist to identify application types and properties."
    , "annal:uri":      "http://example.org/test/#"
    })

test_blob_vocab_create_values = (
    { "annal:type":     "annal:Vocabulary"
    , "rdfs:label":     "Vocabulary namespace for test terms"
    , "rdfs:comment":   "Vocabulary namespace for URIs that are used internally by Annalist to identify application types and properties."
    , "annal:uri":      "http://example.org/blob/yyy#"
    })

test_image_ref_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_reference_type label"
    , 'rdfs:comment':               "test_reference_type comment"
    , 'annal:uri':                  "blob:type/test_reference_type"
    , 'annal:type_view':            "test_reference_view"
    , 'annal:type_list':            "test_reference_list"
    })

test_image_ref_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_image_view label"
    , 'rdfs:comment':               "test_image_view comment"
    , 'annal:view_entity_type':     ""
    , 'annal:view_fields':
      [ { 'annal:field_id':             "Entity_id"
        , 'annal:field_placement':      "small:0,12;medium:0,6"
        }
      , { 'annal:field_id':             "Entity_label"
        , 'annal:field_placement':      "small:0,12"
        }
      , { 'annal:field_id':             "Entity_comment"
        , 'annal:field_placement':      "small:0,12"
        }
      , { 'annal:field_id':             "Test_image_ref"
        , 'annal:field_placement':      "small:0,12"
        }
      ]
    })

test_image_ref_field_create_values = (
    { 'annal:type':                     "annal:Field"
    , 'annal:field_name':               "ref_image"
    , 'rdfs:label':                     "test_image_ref_field label"
    , 'rdfs:comment':                   "test_image_ref_field comment"
    , 'annal:property_uri':             "blob:reference"
    , 'annal:field_render_type':        "RefImage"
    , 'annal:field_value_mode':         "Value_direct"
    , 'annal:field_value_type':        "annal:Identifier"
    , 'annal:placeholder':              "(Image reference)"
    , 'annal:default_value':            ""
    })

def test_ref_entity_create_values(image_uri):
    return (
        { 'rdfs:label':                 "test_ref_image label"
        , 'rdfs:comment':               "test_ref_image comment"
        , 'blob:reference':             image_uri
        })

#   -----------------------------------------------------------------------------
#
#   Turtle generation tests
#
#   -----------------------------------------------------------------------------

class TurtleOutputTest(AnnalistTestCase):
    """
    Tests site/collection data interpreted as Turtle
    """

    def setUp(self):
        self.testsite    = init_annalist_test_site()
        self.testcoll    = init_annalist_test_coll()
        self.sitebasedir = TestBaseDir
        self.collbasedir = os.path.join(
            self.sitebasedir, layout.SITEDATA_DIR, layout.COLL_BASE_DIR
            )
        # Login and permissions
        create_test_user(self.testcoll, "testuser", "testpassword")
        self.client = Client(HTTP_HOST=TestHost)
        loggedin = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def setUpClass(cls):
        super(TurtleOutputTest, cls).setUpClass()
        return

    @classmethod
    def tearDownClass(cls):
        super(TurtleOutputTest, cls).tearDownClass()
        resetSitedata()
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def coll_basedir(self, coll_id):
        return os.path.normpath(os.path.join(self.collbasedir, "../../%s/d/"%coll_id))

    def entity_basedir(self, coll_id, type_id, entity_id):
        return os.path.join(
            self.sitebasedir, 
            layout.SITE_ENTITY_PATH%{'coll_id': coll_id, 'type_id': type_id, 'id': entity_id}
            )

    def dir_base_url(self, b):
        return "file://"+b+"/"

    def coll_baseurl(self, coll_id):
        return self.dir_base_url(self.coll_basedir(coll_id))

    def entity_baseurl(self, coll_id, type_id, entity_id):
        return self.dir_base_url(self.entity_basedir(coll_id, type_id, entity_id))

    def coll_url(self, coll_id):
        return urljoin(self.coll_baseurl(coll_id), layout.META_COLL_REF)

    def entity_url(self, coll_id, type_id, entity_id):
        return "file://" + self.entity_basedir(coll_id, type_id, entity_id)

    def resolve_coll_url(self, coll, ref):
        coll_base    = urljoin(self.testcoll.get_url(), layout.COLL_BASE_REF)
        resolved_url = urljoin(coll_base, ref)
        return resolved_url

    def scan_rdf_list(self, graph, head):
        """
        Iterate over nodes in an RDF list
        """
        next = head
        while (next is not None) and (next != URIRef(RDF.URI.nil)):
            item = graph.value(subject=next, predicate=URIRef(RDF.URI.first))
            yield item
            next = graph.value(subject=next, predicate=URIRef(RDF.URI.rest))
        return

    def assertTripleIn(self, t, g):
        """
        Assert that triple exists in graph, where None values are wildcard
        """
        ts = list(g.triples(t))
        self.assertNotEqual(len(ts), 0, "Triple %r not in graph"%(t,))
        return

    def get_context_mock_dict(self, base_path, context_path="../../"):
        """
        Uses Django test client results to create a dictionary of mock results for 
        accessing JSONLD context resources.  Works with MockHttpDictResources.
        """
        mock_refs = (
            [ context_path+"coll_context.jsonld"
            ])
        mock_dict = {}
        for mock_ref in mock_refs:
            mu = urljoin(base_path, mock_ref)
            log.debug(
                "get_context_mock_dict: base_path %s, mock_ref %s, mu %s"%
                (base_path, mock_ref, mu)
                )
            mr = self.client.get(mu)
            if mr.status_code != 200:
                log.error(
                    "get_context_mock_dict: uri %s, status_code %d, reason_phrase %s"%
                    (mu, mr.status_code, mr.reason_phrase)
                    )
                # log.error("".join(traceback.format_stack()))
            self.assertEqual(mr.status_code,   200)
            mock_dict[mock_ref] = mr.content
        # print "***** get_context_mock_dict: mu: %s, mock_dict: %r"%(mu, mock_dict.keys())
        return mock_dict

    #   -----------------------------------------------------------------------------
    #   Turtle output tests
    #   -----------------------------------------------------------------------------

    # Site data view (check data links)
    def test_get_site_data_view(self):
        site_url = site_view_url()
        site_url = collection_view_url(layout.SITEDATA_ID)
        u = collectiondata_url(coll_id=layout.SITEDATA_ID)
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        layout.SITEDATA_ID)
        self.assertEqual(r.context['orig_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['action'],           "view")
        self.assertEqual(r.context['continuation_url'], "")
        self.assertEqual(
            r.context['entity_data_ref'],      
            site_url+layout.COLL_META_REF
            )
        self.assertEqual(
            r.context['entity_turtle_ref'], 
            site_url+layout.COLL_TURTLE_REF
            )
        return

    # Site data content negotiation
    def test_get_site_data_turtle(self):
        """
        Request site data as Turtle
        """
        site_url = site_view_url()
        site_url = collection_view_url(layout.SITEDATA_ID)
        u = collectiondata_url(coll_id=layout.SITEDATA_ID)
        r = self.client.get(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        v = r['Location']
        self.assertEqual(v, TestHostUri+site_url+layout.COLL_TURTLE_REF)
        w = site_url + layout.COLL_BASE_REF
        mock_resource_dict = self.get_context_mock_dict(w, layout.META_COLL_BASE_REF)
        with MockHttpDictResources(v, mock_resource_dict):
            r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    def test_head_site_data_turtle(self):
        """
        Request HEAD for site data as Turtle
        """
        site_url = site_view_url()
        site_url = collection_view_url(layout.SITEDATA_ID)
        u = collectiondata_url(coll_id=layout.SITEDATA_ID)
        r = self.client.head(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = r['Location']
        self.assertEqual(v, TestHostUri+site_url+layout.COLL_TURTLE_REF)
        return

    def test_http_turtle_site(self):
        """
        Read site data as Turtle, and check resulting RDF triples
        """
        # Read collection data as Turtle
        site_url = site_view_url()
        site_url = collection_view_url(layout.SITEDATA_ID)
        v = site_url + layout.COLL_BASE_REF
        u = TestHostUri + site_url + layout.COLL_TURTLE_REF
        mock_resource_dict = self.get_context_mock_dict(v, layout.META_COLL_BASE_REF)
        with MockHttpDictResources(u, mock_resource_dict):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print "*****"+repr(result)
        # print "***** site:"
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj             = TestHostUri + site_url
        site_data        = self.testsite.site_data()
        ann_id           = Literal(layout.SITEDATA_ID)
        ann_type         = URIRef(ANNAL.URI.SiteData)
        ann_type_id      = Literal(SiteData._entitytypeid)
        software_version = Literal(annalist.__version_data__)
        label            = Literal(site_data[RDFS.CURIE.label])
        comment          = Literal(site_data[RDFS.CURIE.comment])
        for (s, p, o) in (
            [ (subj, RDFS.URI.label,             label              )
            , (subj, RDFS.URI.comment,           comment            )
            , (subj, ANNAL.URI.id,               ann_id             )
            , (subj, ANNAL.URI.type,             ann_type           )
            , (subj, ANNAL.URI.type_id,          ann_type_id        )
            , (subj, ANNAL.URI.software_version, software_version   )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_http_turtle_collection(self):
        """
        Read new collection data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read collection data as Turtle
        collection_url = collection_view_url(coll_id="testcoll")
        v = collection_url + layout.COLL_BASE_REF
        u = TestHostUri + collection_url + layout.COLL_TURTLE_REF
        mock_resource_dict = self.get_context_mock_dict(v, layout.META_COLL_BASE_REF)
        with MockHttpDictResources(u, mock_resource_dict):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print "*****"+repr(result)
        # print "***** coll:"
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj      = TestHostUri + collection_url
        coll_data = self.testcoll._load_values()
        for (s, p, o) in (
            [ (subj, RDFS.URI.label,             Literal(coll_data[RDFS.CURIE.label])       )
            , (subj, RDFS.URI.comment,           Literal(coll_data[RDFS.CURIE.comment])     )
            , (subj, ANNAL.URI.id,               Literal(coll_data[ANNAL.CURIE.id])         )
            , (subj, ANNAL.URI.type_id,          Literal(coll_data[ANNAL.CURIE.type_id])    )
            , (subj, ANNAL.URI.type,             URIRef(ANNAL.URI.Collection)               )
            , (subj, ANNAL.URI.software_version, Literal(annalist.__version_data__)         )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return




    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@







    # Collection data view
    def test_get_collection_data_view(self):
        collection_url = collection_view_url(coll_id="testcoll")
        u = collectiondata_url(coll_id="testcoll")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertEqual(r.context['coll_id'],          layout.SITEDATA_ID)
        self.assertEqual(r.context['type_id'],          layout.COLL_TYPEID)
        self.assertEqual(r.context['entity_id'],        "testcoll")
        self.assertEqual(r.context['orig_id'],          "testcoll")
        self.assertEqual(r.context['action'],           "view")
        self.assertEqual(r.context['continuation_url'], "")
        self.assertEqual(
            r.context['entity_data_ref'],      
            collection_url+layout.COLL_META_REF
            )
        self.assertEqual(
            r.context['entity_turtle_ref'], 
            collection_url+layout.COLL_TURTLE_REF
            )
        return

    # Collection data content negotiation
    def test_get_collection_data_turtle(self):
        """
        Request collection data as Turtle
        """
        collection_url = collection_view_url(coll_id="testcoll")
        u = collectiondata_url(coll_id="testcoll")
        r = self.client.get(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        v = r['Location']
        self.assertEqual(v, TestHostUri+collection_url+layout.COLL_TURTLE_REF)
        w = collection_url + layout.COLL_BASE_REF
        mock_resource_dict = self.get_context_mock_dict(w, layout.META_COLL_BASE_REF)
        with MockHttpDictResources(v, mock_resource_dict):
            r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        return

    def test_http_turtle_collection(self):
        """
        Read new collection data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read collection data as Turtle
        collection_url = collection_view_url(coll_id="testcoll")
        v = collection_url + layout.COLL_BASE_REF
        u = TestHostUri + collection_url + layout.COLL_TURTLE_REF
        mock_resource_dict = self.get_context_mock_dict(v, layout.META_COLL_BASE_REF)
        with MockHttpDictResources(u, mock_resource_dict):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print "*****"+repr(result)
        # print "***** coll:"
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj      = TestHostUri + collection_url
        coll_data = self.testcoll._load_values()
        for (s, p, o) in (
            [ (subj, RDFS.URI.label,             Literal(coll_data[RDFS.CURIE.label])       )
            , (subj, RDFS.URI.comment,           Literal(coll_data[RDFS.CURIE.comment])     )
            , (subj, ANNAL.URI.id,               Literal(coll_data[ANNAL.CURIE.id])         )
            , (subj, ANNAL.URI.type_id,          Literal(coll_data[ANNAL.CURIE.type_id])    )
            , (subj, ANNAL.URI.type,             URIRef(ANNAL.URI.Collection)               )
            , (subj, ANNAL.URI.software_version, Literal(annalist.__version_data__)         )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_turtle_enum_list_type_grid(self):
        """
        Read enumeration value as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        Enum_list_type = RecordEnumFactory(layout.ENUM_LIST_TYPE_ID, layout.ENUM_LIST_TYPE_ID)
        list_type_grid = Enum_list_type.load(
            self.testcoll, "Grid", altscope="all"
            )
        # Read enumerated value list data as Turtle
        type_id = list_type_grid.get_type_id()
        enum_id = list_type_grid.get_id()
        v = entity_url(coll_id="testcoll", type_id=type_id, entity_id=enum_id)
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id=type_id, entity_id=enum_id,
            resource_ref=layout.VOCAB_META_TURTLE
            )
        # print("@@@@ v: (list_type_grid)")
        # print(repr(v))
        # print("@@@@ u: (list_type_grid)")
        # print(repr(u))
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Check the resulting graph contents
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print("@@@@ g: (list_type_grid)")
        # print(g.serialize(format='turtle', indent=4))
        subj                = TestHostUri + v.rstrip("/")
        list_type_grid_data = list_type_grid.get_values()
        list_type_url       = ANNAL.to_uri(list_type_grid_data[ANNAL.CURIE.uri])
        for (s, p, o) in (
            [ (subj, RDF.URI.type,          URIRef(ANNAL.URI.Enum)                            )
            , (subj, RDF.URI.type,          URIRef(ANNAL.URI.Enum_list_type)                  )
            , (subj, RDFS.URI.label,        Literal(list_type_grid_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,      Literal(list_type_grid_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,          Literal(list_type_grid_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,     Literal(list_type_grid_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.uri,         URIRef(list_type_url)                             )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_http_turtle_entity1(self):
        """
        Read default entity data as Turtle using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read entity data as Turtle, with HTTP mocking for context references
        v = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="testtype", entity_id="entity1",
            resource_ref=layout.ENTITY_DATA_TURTLE
            )
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # Check the resulting graph contents
        subj          = TestHostUri + v.rstrip("/")
        testtype_data = RecordTypeData.load(self.testcoll, "testtype")
        entity1       = EntityData.load(testtype_data, "entity1")
        entity_data   = entity1.get_values()
        for (s, p, o) in (
            [ (subj, RDFS.URI.label,     Literal(entity_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,   Literal(entity_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,       Literal(entity_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,  Literal(entity_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.type,     URIRef(ANNAL.URI.EntityData)              )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_http_turtle_type_vocab(self):
        """
        Read type data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read type data as Turtle, with HTTP mocking for context references
        type_vocab = self.testcoll.get_type("_vocab")
        v = recordtype_url(coll_id="testcoll", type_id=type_vocab.get_id())
        p = v + layout.TYPE_META_TURTLE
        u = TestHostUri + p
        with MockHttpDictResources(u, self.get_context_mock_dict(p)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse graph data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # Check the resulting graph contents
        subj            = TestHostUri + v.rstrip("/")
        type_vocab_data = type_vocab.get_values()
        vocab_list_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_list])
        vocab_view_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.URI.type,        URIRef(ANNAL.URI.Type)                        )
            , (subj, RDFS.URI.label,      Literal(type_vocab_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,        Literal(type_vocab_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.type_list, URIRef(vocab_list_url)                        )
            , (subj, ANNAL.URI.type_view, URIRef(vocab_view_url)                        )
            , (subj, ANNAL.URI.uri,       URIRef(ANNAL.URI.Vocabulary)                  )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_http_turtle_type_new(self):
        """
        Create new type in collection, then read type data as Turtle, 
        and check resulting RDF triples
        """
        # Create new type in collection
        test_new_type_create_values = (
            { 'annal:type':                 "annal:Type"
            , 'rdfs:label':                 "test_new_type label"
            , 'rdfs:comment':               "test_new_type comment"
            , 'annal:uri':                  "blob:type/test_new_type"
            , 'annal:type_view':            "Default_view"
            , 'annal:type_list':            "Default_list"
            })
        new_type = RecordType.create(
            self.testcoll, "newtype", test_new_type_create_values
            )
        blob_vocab = RecordVocab.create(
            self.testcoll, "blob", test_blob_vocab_create_values
            )
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read type data as Turtle, with HTTP mocking for context references
        type_new = self.testcoll.get_type("newtype")
        v = recordtype_url(coll_id="testcoll", type_id=type_new.get_id())
        p = v + layout.TYPE_META_TURTLE
        u = TestHostUri + p
        with MockHttpDictResources(u, self.get_context_mock_dict(p)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse graph data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print "*****"+repr(result)
        # print("***** g: (type_new_data)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj          = TestHostUri + v.rstrip("/")
        type_new_data = type_new.get_values()
        new_list_url  = self.resolve_coll_url(self.testcoll, type_new_data[ANNAL.CURIE.type_list])
        new_view_url  = self.resolve_coll_url(self.testcoll, type_new_data[ANNAL.CURIE.type_view])
        # type_new_uri  = type_new_data[ANNAL.CURIE.uri]  # "blob:type/test_new_type"
        blobns         = makeNamespace("blob", "http://example.org/blob/yyy#", ["reference"])
        type_new_uri   = blobns.to_uri(type_new_data[ANNAL.CURIE.uri]) 
        for (s, p, o) in (
            [ (subj, RDF.URI.type,        URIRef(ANNAL.URI.Type)                        )
            , (subj, RDFS.URI.label,      Literal(type_new_data[RDFS.CURIE.label])      )
            , (subj, RDFS.URI.comment,    Literal(type_new_data[RDFS.CURIE.comment])    )
            , (subj, ANNAL.URI.id,        Literal(type_new_data[ANNAL.CURIE.id])        )
            , (subj, ANNAL.URI.type_id,   Literal(type_new_data[ANNAL.CURIE.type_id])   )
            , (subj, ANNAL.URI.type_list, URIRef(new_list_url)                          )
            , (subj, ANNAL.URI.type_view, URIRef(new_view_url)                          )
            , (subj, ANNAL.URI.uri,       URIRef(type_new_uri)                          )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_http_turtle_vocab_annal(self):
        """
        Read annal: vocabulary data as Turtle using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read vocabulary data as Turtle
        v = entity_url(coll_id="testcoll", type_id="_vocab", entity_id="annal")
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="_vocab", entity_id="annal",
            resource_ref=layout.VOCAB_META_TURTLE
            )
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")

        # Parse vocabulary data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")

        # Check the resulting graph contents
        subj          = TestHostUri + v.rstrip("/")
        vocabtypeinfo = EntityTypeInfo(self.testcoll, "_vocab")
        annalvocab    = vocabtypeinfo.get_entity("annal")
        annal_data    = annalvocab.get_values()
        seeAlso_1     = "https://github.com/gklyne/annalist/blob/master/src/annalist_root/annalist/identifiers.py"
        for (s, p, o) in (
            [ (subj, RDF.URI.type,      URIRef(ANNAL.URI.EntityData)             )
            , (subj, RDF.URI.type,      URIRef(ANNAL.URI.Vocabulary)             )
            , (subj, RDFS.URI.label,    Literal(annal_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,  Literal(annal_data[RDFS.CURIE.comment])  )
            , (subj, RDFS.URI.seeAlso,  URIRef(seeAlso_1)                        )            
            , (subj, ANNAL.URI.id,      Literal(annal_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id, Literal(annal_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.type,    URIRef(ANNAL.URI.Vocabulary)             )
            , (subj, ANNAL.URI.uri,     URIRef(ANNAL._baseUri)                   )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_http_turtle_user_view(self):
        """
        Read user view data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Read vocabulary data as Turtle
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="_view", entity_id="User_view",
            resource_ref=layout.VIEW_META_TURTLE
            )
        v = entity_url(coll_id="testcoll", type_id="_view", entity_id="User_view")
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")

        # Parse view data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")

        # Check the resulting graph contents
        subj           = TestHostUri + v.rstrip("/")
        viewtypeinfo   = EntityTypeInfo(self.testcoll, "_view")
        view_user      = viewtypeinfo.get_entity("User_view")
        view_user_data = view_user.get_values()
        view_uri       = ANNAL.to_uri(view_user_data[ANNAL.CURIE.uri])
        for (s, p, o) in (
            [ (subj, RDF.URI.type,          URIRef(ANNAL.URI.View)                       )
            , (subj, RDFS.URI.label,        Literal(view_user_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,      Literal(view_user_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,          Literal(view_user_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,     Literal(view_user_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.uri,         URIRef(view_uri)                             )
            , (subj, ANNAL.URI.open_view,   Literal(False)                               )
            , (subj, ANNAL.URI.view_entity_type, URIRef(ANNAL.URI.User)                       )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        # Check field list contents
        fields = view_user_data[ANNAL.CURIE.view_fields]
        head   = property_value(g, URIRef(subj), ANNAL.URI.view_fields)
        items  = scan_list(g, head)
        for f in fields:
            fi  = URIRef(
                TestHostUri + collection_entity_view_url(
                    type_id="_field", 
                    entity_id=extract_entity_id(f[ANNAL.CURIE.field_id])
                    ).rstrip("/")
                )
            fp  = Literal(f[ANNAL.CURIE.field_placement])
            fn  = next(items)
            fni = property_value(g, fn, ANNAL.URI.field_id)
            fnp = property_value(g, fn, ANNAL.URI.field_placement)
            self.assertEqual(fni, fi)
            self.assertEqual(fnp, fp)
        # self.assertRaises as context manager, see http://stackoverflow.com/a/28223420/324122
        with self.assertRaises(StopIteration):
            next(items)
        return

    def test_http_turtle_user_default(self):
        """
        Read default user data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Read vocabulary data as Turtle
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="_user", entity_id="_default_user_perms",
            resource_ref=layout.USER_META_TURTLE
            )
        v = entity_url(coll_id="testcoll", type_id="_user", entity_id="_default_user_perms")
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")

        # Parse view data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")

        # Check the resulting graph contents
        subj              = TestHostUri + v.rstrip("/")
        usertypeinfo      = EntityTypeInfo(self.testcoll, "_user")
        user_default_data = usertypeinfo.get_entity("_default_user_perms")
        user_uri          = ANNAL.to_uri(user_default_data[ANNAL.CURIE.user_uri])
        user_perms        = user_default_data[ANNAL.CURIE.user_permission]
        for (s, p, o) in (
            [ (subj, RDF.URI.type,          URIRef(ANNAL.URI.User)                          )
            , (subj, RDFS.URI.label,        Literal(user_default_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,      Literal(user_default_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,          Literal(user_default_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,     Literal(user_default_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.user_uri,    URIRef(user_uri)                                )
            , (subj, ANNAL.URI.user_permission, Literal(user_perms[0])                      )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_http_turtle_image_ref(self):
        """
        Read image reference data as Turtle, and check resulting RDF triples
        """
        # Populate collection with record type, view and field
        imageurl = TestHostUri + "/test-image.jpg" 
        test_ref_type = RecordVocab.create(
            self.testcoll, "blob", test_blob_vocab_create_values
            )
        test_ref_type = RecordType.create(
            self.testcoll, "testreftype", test_image_ref_type_create_values
            )
        test_ref_view = RecordView.create(
            self.testcoll, "testrefview", test_image_ref_view_create_values
            )
        test_ref_field = RecordField.create(
            self.testcoll, "Test_image_ref", test_image_ref_field_create_values
            )
        # Create data records for testing image references:
        test_ref_type_info = EntityTypeInfo(
            self.testcoll, "testreftype", create_typedata=True
            )
        test_ref_type_info.create_entity("refentity", test_ref_entity_create_values(imageurl))
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Read data as Turtle, with HTTP mocking for context references
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="testreftype", entity_id="refentity",
            resource_ref=layout.ENTITY_DATA_TURTLE
            )
        v = entity_url(coll_id="testcoll", type_id="testreftype", entity_id="refentity")
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=u, format="turtle")
        # print "*****"+repr(result)
        # print("***** g: (ref_image_data)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj              = TestHostUri + v.rstrip("/")
        testdata       = RecordTypeData.load(self.testcoll, "testreftype")
        ref_image      = EntityData.load(testdata, "refentity")
        ref_image_data = ref_image.get_values()
        blobns         = makeNamespace("blob", "http://example.org/blob/yyy#", ["reference"])
        type_uri       = blobns.to_uri(ref_image_data['@type'][0]) 
        for (s, p, o) in (
            [ (subj, RDF.URI.type,          URIRef(ANNAL.URI.EntityData)                 )
            , (subj, RDF.URI.type,          URIRef(type_uri)                             )
            , (subj, RDFS.URI.label,        Literal(ref_image_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,      Literal(ref_image_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,          Literal(ref_image_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,     Literal(ref_image_data[ANNAL.CURIE.type_id]) )
            , (subj, blobns.URI.reference,  URIRef(imageurl)                             )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    #   -----------------------------------------------------------------------------
    #   Entity content negotiation tests
    #   -----------------------------------------------------------------------------

    def test_http_conneg_turtle_entity1(self):
        """
        Read default entity data as Turtle using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")
        # Read entity data as Turtle
        u = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        # print "@@ test_http_conneg_turtle_entity1: uri %s"%u
        r = self.client.get(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.ENTITY_DATA_TURTLE)
        with MockHttpDictResources(v, self.get_context_mock_dict(v)):
            r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** v: (entity1)")
        # print(repr(v))
        # print("***** c: (entity1)")
        # print r.content
        result = g.parse(data=r.content, publicID=v, format="turtle")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj        = entity1.get_url().rstrip("/")
        entity_data = entity1.get_values()
        for (s, p, o) in (
            [ (subj, RDFS.URI.label,     Literal(entity_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,   Literal(entity_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,       Literal(entity_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,  Literal(entity_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.type,     URIRef(ANNAL.URI.EntityData)              )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_http_conneg_head_turtle_entity1(self):
        """
        HEAD request to entity with content negotiation for Turtle
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")
        # Read entity data as Turtle
        u = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        r = self.client.head(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        self.assertEqual(r.content,       b"")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.ENTITY_DATA_TURTLE)
        return

    def test_http_conneg_turtle_type_vocab(self):
        """
        Read type data as Turtle, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        type_vocab = self.testcoll.get_type("_vocab")
        # Read type data as Turtle, with HTTP mocking for context references
        u = recordtype_url(coll_id="testcoll", type_id=type_vocab.get_id())
        r = self.client.get(u, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.TYPE_META_TURTLE)
        with MockHttpDictResources(v, self.get_context_mock_dict(v)):
            r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Parse graph data as Turtle
        g = Graph()
        result = g.parse(data=r.content, publicID=v, format="turtle")
        # Check the resulting graph contents
        subj            = TestHostUri + u.rstrip("/")
        type_vocab_data = type_vocab.get_values()
        vocab_list_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_list])
        vocab_view_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.URI.type,        URIRef(ANNAL.URI.Type)                        )
            , (subj, RDFS.URI.label,      Literal(type_vocab_data[RDFS.CURIE.label])    )
            , (subj, RDFS.URI.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.URI.id,        Literal(type_vocab_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.URI.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.URI.type_list, URIRef(vocab_list_url)                        )
            , (subj, ANNAL.URI.type_view, URIRef(vocab_view_url)                        )
            , (subj, ANNAL.URI.uri,       URIRef(ANNAL.URI.Vocabulary)                  )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    #   -----------------------------------------------------------------------------
    #   Entity list content negotiation tests
    #   -----------------------------------------------------------------------------

    def get_list_turtle(self, list_url, subj_ref, coll_id="testcoll", type_id=None, context_path=""):
        """
        Return list of entity nodes from Turtle list
        """
        self.testcoll.generate_coll_jsonld_context()
        r = self.client.get(list_url, HTTP_ACCEPT="text/turtle")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "Found")
        turtle_url        = TestHostUri + r['Location']
        expect_turtle_url = make_resource_url(TestHostUri, list_url, layout.ENTITY_LIST_TURTLE)
        self.assertEqual(turtle_url, expect_turtle_url)
        with MockHttpDictResources(turtle_url, self.get_context_mock_dict(turtle_url, context_path=context_path)):
            r = self.client.get(turtle_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # print("***** turtle_url: "+turtle_url)
        # print("***** c: (testcoll/_type list):")
        # print r.content
        g = Graph()
        result = g.parse(data=r.content, publicID=turtle_url, format="turtle")
        # Check the resulting graph contents
        subj = urljoin(turtle_url, subj_ref)
        for (s, p, o) in (
            [ (subj, ANNAL.URI.entity_list, None)
            ]):
            self.assertTripleIn( (URIRef(s), URIRef(p), o), g)
        list_head  = g.value(subject=URIRef(subj), predicate=URIRef(ANNAL.URI.entity_list))
        list_items = list(self.scan_rdf_list(g, list_head))
        return (turtle_url, list_items)

    def test_http_conneg_turtle_list_coll_type(self):
        """
        Content negotiate for Turtle version of a list of collection-defined types
        """
        list_url = entitydata_list_type_url(
            "testcoll", "_type",
            scope=None
            )
        subj_ref = entitydata_list_type_url(
            "testcoll", "_type",
            list_id="Type_list",
            scope=None
            )
        (turtle_url, list_items) = self.get_list_turtle(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../"
            )
        t_uri = urljoin(
            turtle_url, 
            entity_uriref(coll_id="testcoll", type_id="_type", entity_id="testtype")
            )
        self.assertEqual(len(list_items), 1)
        self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_turtle_list_coll_all(self):
        """
        Content negotiate for Turtle version of a list of collection-defined entities of all types
        """
        list_url = entitydata_list_all_url("testcoll", scope=None)
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Default_list_all", scope=None
            )
        (turtle_url, list_items) = self.get_list_turtle(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path=""
            )
        t_uri = urljoin(
            turtle_url, 
            entity_uriref(coll_id="testcoll", type_id="_type", entity_id="testtype")
            )
        e1uri = urljoin(
            turtle_url, 
            entity_uriref(coll_id="testcoll", type_id="testtype", entity_id="entity1")
            )
        self.assertEqual(len(list_items), 2)
        self.assertIn(URIRef(t_uri), list_items)
        self.assertIn(URIRef(e1uri), list_items)
        return

    def test_http_conneg_turtle_list_coll_all_list(self):
        """
        Content negotiate for Turtle version of a list of collection-defined entities of all types
        """
        list_url = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope=None
            )
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope=None
            )
        (turtle_url, list_items) = self.get_list_turtle(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../../d/"
            )
        t_uri = urljoin(
            turtle_url, 
            entity_uriref(coll_id="testcoll", type_id="_type", entity_id="testtype")
            )
        e1uri = urljoin(
            turtle_url, 
            entity_uriref(coll_id="testcoll", type_id="testtype", entity_id="entity1")
            )
        self.assertEqual(len(list_items), 1)
        self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_turtle_list_site_type(self):
        """
        Content negotiate for Turtle version of a list of collection-defined types
        """
        list_url = entitydata_list_type_url(
            "testcoll", "_type",
            scope="all"
            )
        subj_ref = entitydata_list_type_url(
            "testcoll", "_type",
            list_id="Type_list",
            scope="all"
            )
        (turtle_url, list_items) = self.get_list_turtle(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../"
            )
        # print "@@ "+repr(list_items)
        expect_type_ids = get_site_types()
        expect_type_ids.add("testtype")
        self.assertEqual(len(list_items), len(expect_type_ids))
        for entity_id in expect_type_ids:
            t_uri = urljoin(
                turtle_url, 
                entity_uriref(coll_id="testcoll", type_id="_type", entity_id=entity_id)
                )
            self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_turtle_list_site_all_list(self):
        """
        Content negotiate for Turtle version of a list of 
        collection-defined entities of all types
        """
        list_url = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope="all"
            )
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope="all"
            )
        (turtle_url, list_items) = self.get_list_turtle(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../../d/"
            )
        expect_type_ids = get_site_types()
        expect_type_ids.add("testtype")
        self.assertEqual(len(list_items), len(expect_type_ids))
        for entity_id in expect_type_ids:
            t_uri = urljoin(
                turtle_url, 
                entity_uriref(coll_id="testcoll", type_id="_type", entity_id=entity_id)
                )
            self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_turtle_list_coll_wrongname(self):
        """
        This is a test of the regular expression used to access list resources,
        to ensure the '.' must be a literal '.' and not a wildcard.
        """
        list_url = entitydata_list_type_url(
            "testcoll", "_type",
            scope=None
            )
        wrong_name     = layout.ENTITY_LIST_FILE.replace('.', '*')
        wrong_turtle_url = make_resource_url(TestHostUri, list_url, wrong_name)
        with SuppressLogging(logging.WARNING):
            r = self.client.get(wrong_turtle_url)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        return

# End.
