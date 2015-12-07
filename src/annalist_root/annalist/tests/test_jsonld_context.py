"""
Test JSONB-LD context generation logic
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse
import unittest

import logging
log = logging.getLogger(__name__)

from rdflib                         import Graph, URIRef, Literal

from django.test.client             import Client

import annalist
from annalist                       import layout
from annalist.identifiers           import makeNamespace, RDF, RDFS, ANNAL

from annalist.models.site           import Site
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.recordvocab    import RecordVocab
from annalist.models.annalistuser   import AnnalistUser
from annalist.models.entitydata     import EntityData
from annalist.models.entitytypeinfo import EntityTypeInfo

# from annalist.views.form_utils.fieldchoice  import FieldChoice

from miscutils.MockHttpResources    import MockHttpFileResources, MockHttpDictResources

from AnnalistTestCase       import AnnalistTestCase
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from init_tests             import init_annalist_test_site, init_annalist_test_coll, resetSitedata
from entity_testutils       import (
    site_dir, collection_dir,
    site_view_url, collection_view_url,
    collection_create_values,
    create_test_user
    )
from entity_testtypedata            import (
    recordtype_url
    )
from entity_testentitydata          import (
    entity_url, entity_resource_url
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
    while head != URIRef(RDF.nil):
        yield property_value(graph, head, RDF.first)
        head = property_value(graph, head, RDF.rest)
    return

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

test_test_vocab_create_values = (
    { "annal:type":     "annal:Vocabulary"
    , "rdfs:label":     "Vocabulary namespace for test terms"
    , "rdfs:comment":   "Vocabulary namespace for URIs that are used internally by Annalist to identify application types and properties."
    , "annal:uri":      "http://example.org/test/#"
    })

test_image_ref_type_create_values = (
    { 'annal:type':                 "annal:Type"
    , 'rdfs:label':                 "test_reference_type label"
    , 'rdfs:comment':               "test_reference_type comment"
    , 'annal:uri':                  "test:type/test_reference_type"
    , 'annal:type_view':            "test_reference_view"
    , 'annal:type_list':            "test_reference_list"
    })

test_image_ref_view_create_values = (
    { 'annal:type':                 "annal:View"
    , 'rdfs:label':                 "test_image_view label"
    , 'rdfs:comment':               "test_image_view comment"
    , 'annal:record_type':          ""
    , 'annal:add_field':            "yes"
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
    , 'annal:property_uri':             "test:reference"
    , 'annal:field_render_type':        "RefImage"
    , 'annal:field_value_mode':         "Value_direct"
    , 'annal:field_target_type':        "annal:Identifier"
    , 'annal:placeholder':              "(Image reference)"
    , 'annal:default_value':            ""
    })

def test_ref_entity_create_values(image_uri):
    return (
        { 'rdfs:label':                 "test_ref_image label"
        , 'rdfs:comment':               "test_ref_image comment"
        , 'test:reference':             image_uri
        })

#   -----------------------------------------------------------------------------
#
#   RDFLib input source from file-like object
#
#   -----------------------------------------------------------------------------

# @@ not used for now.  Originally created for use with HTTPResponse object to 
#    read content returned.

from rdflib.parser import InputSource

class StreamInputSource(InputSource):

    def __init__(self, stream, system_id):
        super(StreamInputSource, self).__init__(system_id)
        self.file = stream
        self.setByteStream(stream)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return repr(self.file)


#   -----------------------------------------------------------------------------
#
#   JSON-LD context generation tests
#
#   -----------------------------------------------------------------------------

class JsonldContextTest(AnnalistTestCase):
    """
    Tests site/collection data interpreted as JSON-LD
    """

    def setUp(self):
        self.testsite = init_annalist_test_site()
        self.testcoll = init_annalist_test_coll()
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
    def tearDownClass(cls):
        resetSitedata()
        return

    def get_coll_url(self, coll):
        return ("file://" + 
            os.path.normpath(
                os.path.join(
                    TestBaseDir, 
                    layout.SITE_COLL_PATH%{'id': self.testcoll.get_id()}
                    )
                ) + "/"
            )

    #   -----------------------------------------------------------------------------
    #   JSON-LD context tests
    #   -----------------------------------------------------------------------------

    def test_jsonld_site(self):
        """
        Read site data as JSON-LD, and check resulting RDF triples
        """
        # Generate site-level JSON-LD context data
        # self.testsite.generate_site_jsonld_context()

        # Read site data as JSON-LD
        g = Graph()
        s = self.testsite.site_data_stream()
        # b = self.testsite.get_url()
        b = "file://" + os.path.join(TestBaseDir, layout.SITEDATA_META_DIR) + "/"
        # print "*****"+repr(b)
        # print "*****"+repr(s)
        # print "*****"+repr(b)
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print "***** site:"
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj             = URIRef(self.testsite.get_url())
        subj             = URIRef("file://" + TestBaseDir + "/")
        subj             = URIRef(
            "file://" + os.path.join(TestBaseDir, layout.SITEDATA_DIR) + "/"
            )
        site_data        = self.testsite.site_data()
        ann_id           = Literal(layout.SITEDATA_ID)
        ann_type         = URIRef(ANNAL.SiteData)
        ann_type_id      = Literal(SiteData._entitytypeid)
        software_version = Literal(annalist.__version_data__)
        label            = Literal(site_data[RDFS.CURIE.label])
        comment          = Literal(site_data[RDFS.CURIE.comment])
        self.assertIn((subj, URIRef(ANNAL.id),      ann_id),      g)
        self.assertIn((subj, URIRef(ANNAL.type),    ann_type),    g)
        self.assertIn((subj, URIRef(ANNAL.type_id), ann_type_id), g)
        self.assertIn((subj, URIRef(RDFS.label),    label),       g)
        self.assertIn((subj, URIRef(RDFS.comment),  comment),     g)
        self.assertIn((subj, URIRef(ANNAL.software_version), software_version), g)
        return

    def test_jsonld_collection(self):
        """
        Read new collection data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Read collection data as JSON-LD
        g = Graph()
        s = self.testcoll._read_stream()
        b = "file://" + os.path.join(
            TestBaseDir,
            layout.SITE_COLL_CONTEXT_PATH%{'id': self.testcoll.get_id()}
            )
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print "***** coll:"
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj      = self.get_coll_url(self.testcoll)
        coll_data = self.testcoll._load_values()
        for (s, p, o) in (
            [ (subj, RDFS.label,             Literal(coll_data[RDFS.CURIE.label])       )
            , (subj, RDFS.comment,           Literal(coll_data[RDFS.CURIE.comment])     )
            , (subj, ANNAL.id,               Literal(coll_data[ANNAL.CURIE.id])         )
            , (subj, ANNAL.type_id,          Literal(coll_data[ANNAL.CURIE.type_id])    )
            , (subj, ANNAL.type,             URIRef(ANNAL.Collection)                   )
            , (subj, ANNAL.software_version, Literal(annalist.__version_data__)         )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_jsonld_entity1(self):
        """
        Read default entity data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")

        # Read entity data as JSON-LD
        g = Graph()
        s = entity1._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITE_ENTITY_PATH%
                  { 'coll_id': self.testcoll.get_id()
                  , 'type_id': testdata.get_id()
                  , 'id':      entity1.get_id()
                  }
                ) + 
              "/"
            )
        # print("***** b: (entity1)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj        = b #@@ entity1.get_url()
        entity_data = entity1.get_values()
        for (s, p, o) in (
            [ (subj, RDFS.label,             Literal(entity_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,           Literal(entity_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,               Literal(entity_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,          Literal(entity_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type,             URIRef(ANNAL.EntityData)                  )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_jsonld_type_vocab(self):
        """
        Read type data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        type_vocab = self.testcoll.get_type("_vocab")

        # Read type data as JSON-LD
        g = Graph()
        s = type_vocab._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITEDATA_DIR,
                layout.SITE_TYPE_PATH%{ 'id': type_vocab.get_id() }
                ) + 
              "/"
            )
        # print("***** b: (type_vocab)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (type_vocab)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj            = b #@@ type_vocab.get_url()
        type_vocab_data = type_vocab.get_values()
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                              )
            , (subj, RDFS.label,      Literal(type_vocab_data[RDFS.CURIE.label])      )
            , (subj, RDFS.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])    )
            , (subj, ANNAL.id,        Literal(type_vocab_data[ANNAL.CURIE.id])        )
            , (subj, ANNAL.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id])   )
            , (subj, ANNAL.type_list, Literal(type_vocab_data[ANNAL.CURIE.type_list]) )
            , (subj, ANNAL.type_view, Literal(type_vocab_data[ANNAL.CURIE.type_view]) )
            , (subj, ANNAL.uri,       URIRef(ANNAL.Vocabulary)                        )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_jsonld_view_user(self):
        """
        Read view data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        view_user = self.testcoll.get_view("User_view")

        # Read view data as JSON-LD
        g = Graph()
        s = view_user._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITEDATA_DIR,
                layout.SITE_TYPE_PATH%{ 'id': view_user.get_id() }
                ) + 
              "/"
            )
        # print("***** b: (view_user)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (view_user)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj           = b #@@ view_user.get_url()
        view_user_data = view_user.get_values()
        view_uri       = ANNAL.to_uri(view_user_data[ANNAL.CURIE.uri])
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.View)                           )
            , (subj, RDFS.label,        Literal(view_user_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(view_user_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(view_user_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(view_user_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.uri,         URIRef(view_uri)                             )
            , (subj, ANNAL.open_view,   Literal(False)                               )
            , (subj, ANNAL.record_type, URIRef(ANNAL.User)                           )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )

        # # Check field list contents
        # fields = view_user_data[ANNAL.CURIE.view_fields]
        # nextfn = g.value(URIRef(subj), URIRef(ANNAL.view_fields))
        # for f in fields:
        #     fi  = Literal(f[ANNAL.CURIE.field_id])
        #     fp  = Literal(f[ANNAL.CURIE.field_placement])
        #     fn  = g.value(nextfn, URIRef(RDF.first))
        #     fni = g.value(fn, URIRef(ANNAL.field_id))
        #     fnp = g.value(fn, URIRef(ANNAL.field_placement))
        #     self.assertEqual(fni, fi)
        #     self.assertEqual(fnp, fp)
        #     nextfn = g.value(nextfn, URIRef(RDF.rest))
        # self.assertEqual(nextfn, URIRef(RDF.nil))

        # Check field list contents
        fields = view_user_data[ANNAL.CURIE.view_fields]
        head   = property_value(g, URIRef(subj), ANNAL.view_fields)
        items  = scan_list(g, head)
        for f in fields:
            fi  = Literal(f[ANNAL.CURIE.field_id])
            fp  = Literal(f[ANNAL.CURIE.field_placement])
            fn  = items.next()
            fni = property_value(g, fn, ANNAL.field_id)
            fnp = property_value(g, fn, ANNAL.field_placement)
            self.assertEqual(fni, fi)
            self.assertEqual(fnp, fp)
        # self.assertRaises as context manager, see http://stackoverflow.com/a/28223420/324122
        with self.assertRaises(StopIteration):
            items.next()
        return

    def test_jsonld_user_default(self):
        """
        Read user view data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        user_default = AnnalistUser.load(
            self.testcoll, "_default_user_perms", altscope="all"
            )

        # Read user data as JSON-LD
        g = Graph()
        s = user_default._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITEDATA_DIR,
                layout.SITE_TYPE_PATH%{ 'id': user_default.get_id() }
                ) + 
              "/"
            )
        # print("***** b: (user_default)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (user_default)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj              = b #@@ user_default.get_url()
        user_default_data = user_default.get_values()
        user_uri          = ANNAL.to_uri(user_default_data[ANNAL.CURIE.user_uri])
        user_perms        = user_default_data[ANNAL.CURIE.user_permissions]
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.User)                              )
            , (subj, RDFS.label,        Literal(user_default_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(user_default_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(user_default_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(user_default_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.user_uri,    URIRef(user_uri)                                )
            , (subj, ANNAL.user_permissions, Literal(user_perms[0])                     )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )

        return

    def test_jsonld_image_ref(self):
        """
        Read image reference data as JSON-LD, and check resulting RDF triples
        """
        # Populate collection with record type, view and field
        # filepath  = "%s/README.md"%TestBaseDir
        # fileuri   = "file://"+self.filepath
        imagepath = "%s/test-image.jpg"%TestBaseDir
        imageuri  = "file://"+imagepath

        test_ref_type = RecordVocab.create(
            self.testcoll, "test", test_test_vocab_create_values
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
            self.testsite, self.testcoll, "testreftype", create_typedata=True
            )
        test_ref_type_info.create_entity("refentity", test_ref_entity_create_values(imageuri))

        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Create entity object to access image reference data 
        testdata  = RecordTypeData.load(self.testcoll, "testreftype")
        ref_image = EntityData.load(testdata, "refentity")

        # Read user data as JSON-LD
        g = Graph()
        s = ref_image._read_stream()
        b = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITE_ENTITY_PATH%
                  { 'coll_id': self.testcoll.get_id()
                  , 'type_id': testdata.get_id()
                  , 'id':      ref_image.get_id()
                  }
                ) + 
              "/"
            )
        # print("***** b: (ref_image)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (ref_image)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj           = b #@@ ref_image.get_url()
        ref_image_data = ref_image.get_values()
        # print "***** ref_image_data:"
        # print repr(ref_image_data)
        testns = makeNamespace("test", "http://example.org/test/#", ["reference"])
        type_uri       = testns.to_uri(ref_image_data['@type'][0]) 
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.EntityData)                     )
            , (subj, RDF.type,          URIRef(type_uri)                             )
            , (subj, RDFS.label,        Literal(ref_image_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(ref_image_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(ref_image_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(ref_image_data[ANNAL.CURIE.type_id]) )
            , (subj, testns.reference,  URIRef(imageuri)                             )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )

        return

    def get_context_mock_dict(self, base_path):
        """
        Uses Django test client results to create a dictionary of mock results for 
        accessing JSONLD context resources.  Works with MockHttpDictResources.
        """
        mock_refs = (
            [ "../../coll_context.jsonld"
            # , "../../site_context.jsonld" 
            ])
        mock_dict = {}
        for mock_ref in mock_refs:
            mu = urlparse.urljoin(base_path, mock_ref)
            # log.debug(
            #     "get_context_mock_dict: base_path %s, mock_ref %s, mu %s"%
            #     (base_path, mock_ref, mu)
            #     )
            mr = self.client.get(mu)
            if mr.status_code != 200:
                log.error(
                    "get_context_mock_dict: uri %s, status_code %d, reason_phrase %s"%
                    (mu, mr.status_code, mr.reason_phrase)
                    )
            self.assertEqual(mr.status_code,   200)
            mock_dict[mock_ref] = mr.content
        # print "***** mu: %s, mock_dict: %r"%(mu, mock_dict.keys())
        return mock_dict

    def test_http_jsonld_entity1(self):
        """
        Read default entity data as JSON-LD using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")

        # Read entity data as JSON-LD
        v = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="testtype", entity_id="entity1",
            resource_ref=layout.ENTITY_DATA_FILE
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** u: (entity1)")
        # print(repr(u))
        # print("***** c: (entity1)")
        # print r.content
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            result = g.parse(data=r.content, publicID=u, base=u, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj        = entity1.get_url()
        entity_data = entity1.get_values()
        for (s, p, o) in (
            [ (subj, RDFS.label,             Literal(entity_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,           Literal(entity_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,               Literal(entity_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,          Literal(entity_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type,             URIRef(ANNAL.EntityData)                  )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    def test_http_jsonld_type_vocab(self):
        """
        Read type data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        type_vocab = self.testcoll.get_type("_vocab")

        # Read type data as JSON-LD
        v = recordtype_url(coll_id="testcoll", type_id=type_vocab.get_id())
        p = v + layout.TYPE_META_FILE
        u = TestHostUri + p
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** u: (type_vocab)")
        # print(repr(u))
        # print("***** c: (type_vocab)")
        # print r.content

        # Read graph data with HTTP mocking for context references
        with MockHttpDictResources(u, self.get_context_mock_dict(p)):
            result = g.parse(data=r.content, publicID=u, base=u, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (type_vocab)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj            = TestHostUri + v
        type_vocab_data = type_vocab.get_values()
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                              )
            , (subj, RDFS.label,      Literal(type_vocab_data[RDFS.CURIE.label])      )
            , (subj, RDFS.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])    )
            , (subj, ANNAL.id,        Literal(type_vocab_data[ANNAL.CURIE.id])        )
            , (subj, ANNAL.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id])   )
            , (subj, ANNAL.type_list, Literal(type_vocab_data[ANNAL.CURIE.type_list]) )
            , (subj, ANNAL.type_view, Literal(type_vocab_data[ANNAL.CURIE.type_view]) )
            , (subj, ANNAL.uri,       URIRef(ANNAL.Vocabulary)                        )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_http_jsonld_type_new(self):
        """
        Create new type in collection, then read type data as JSON-LD, 
        and check resulting RDF triples
        """
        # Create new type in collection
        test_new_type_create_values = (
            { 'annal:type':                 "annal:Type"
            , 'rdfs:label':                 "test_new_type label"
            , 'rdfs:comment':               "test_new_type comment"
            , 'annal:uri':                  "test:type/test_new_type"
            , 'annal:type_view':            "Default_view"
            , 'annal:type_list':            "Default_list"
            })
        new_type = RecordType.create(
            self.testcoll, "newtype", test_new_type_create_values
            )

        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        type_new = self.testcoll.get_type("newtype")

        # Read type data as JSON-LD
        v = recordtype_url(coll_id="testcoll", type_id=type_new.get_id())
        p = v + layout.TYPE_META_FILE
        u = TestHostUri + p
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** u: (type_new)")
        # print(repr(u))
        # print("***** c: (type_new)")
        # print r.content

        # Read graph data with HTTP mocking for context references
        with MockHttpDictResources(u, self.get_context_mock_dict(p)):
            result = g.parse(data=r.content, publicID=u, base=u, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (type_new)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj            = TestHostUri + v
        type_new_data = type_new.get_values()
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                            )
            , (subj, RDFS.label,      Literal(type_new_data[RDFS.CURIE.label])      )
            , (subj, RDFS.comment,    Literal(type_new_data[RDFS.CURIE.comment])    )
            , (subj, ANNAL.id,        Literal(type_new_data[ANNAL.CURIE.id])        )
            , (subj, ANNAL.type_id,   Literal(type_new_data[ANNAL.CURIE.type_id])   )
            , (subj, ANNAL.type_list, Literal(type_new_data[ANNAL.CURIE.type_list]) )
            , (subj, ANNAL.type_view, Literal(type_new_data[ANNAL.CURIE.type_view]) )
            , (subj, ANNAL.uri,       URIRef(type_new_data[ANNAL.CURIE.uri])        )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

# End.
