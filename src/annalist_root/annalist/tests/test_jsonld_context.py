"""
Test JSON-LD and context generation logic
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

from utils.SuppressLoggingContext   import SuppressLogging

import annalist
from annalist                       import layout
from annalist.identifiers           import makeNamespace, RDF, RDFS, ANNAL
from annalist.util                  import make_resource_url

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
    entity_url, entity_resource_url,
    entitydata_list_type_url, entitydata_list_all_url
    )
from entity_testsitedata    import (
    # make_field_choices, no_selection,
    get_site_types, get_site_types_sorted, get_site_types_linked,
    # get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    # get_site_views, get_site_views_sorted, get_site_views_linked,
    # get_site_list_types, get_site_list_types_sorted,
    # get_site_field_groups, get_site_field_groups_sorted, 
    # get_site_fields, get_site_fields_sorted, 
    # get_site_field_types, get_site_field_types_sorted, 
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
#   JSON-LD and context generation tests
#
#   -----------------------------------------------------------------------------

class JsonldContextTest(AnnalistTestCase):
    """
    Tests site/collection data interpreted as JSON-LD
    """

    def setUp(self):
        self.testsite    = init_annalist_test_site()
        self.testcoll    = init_annalist_test_coll()
        self.sitebasedir = TestBaseDir
        self.collbasedir = os.path.join(self.sitebasedir, layout.SITEDATA_DIR, layout.COLL_BASE_DIR)
        self.collbaseurl = "file://" + self.collbasedir + "/"
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
        return urlparse.urljoin(self.coll_baseurl(coll_id), layout.META_COLL_REF)

    def entity_url(self, coll_id, type_id, entity_id):
        return "file://" + self.entity_basedir(coll_id, type_id, entity_id)

    def resolve_coll_url(self, coll, ref):
        coll_base    = urlparse.urljoin(self.testcoll.get_url(), layout.COLL_BASE_REF)
        resolved_url = urlparse.urljoin(coll_base, ref)
        return resolved_url

    def scan_rdf_list(self, graph, head):
        """
        Iterate over nodes in an RDF list
        """
        next = head
        while (next is not None) and (next != URIRef(RDF.nil)):
            item = graph.value(subject=next, predicate=URIRef(RDF.first))
            yield item
            next = graph.value(subject=next, predicate=URIRef(RDF.rest))
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
            mu = urlparse.urljoin(base_path, mock_ref)
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
            self.assertEqual(mr.status_code,   200)
            mock_dict[mock_ref] = mr.content
        # print "***** get_context_mock_dict: mu: %s, mock_dict: %r"%(mu, mock_dict.keys())
        return mock_dict

    #   -----------------------------------------------------------------------------
    #   JSON-LD and context tests
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
        b = "file://" + os.path.join(TestBaseDir, layout.SITEDATA_BASE_DIR) + "/"
        # print "***** b: "+repr(b)
        # print "***** s: "+repr(s)
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
        b = self.coll_baseurl(self.testcoll.get_id())
        # print "***** b: "+repr(b)
        # print "***** s: "+s.read()
        # s.seek(0)
        result = g.parse(source=s, publicID=b, format="json-ld")
        # print "*****"+repr(result)
        # print "***** coll:"
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj      = self.coll_url(self.testcoll.get_id())
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
                )
            )
        # print "***** b: "+repr(b)
        # print "***** s: "+s.read()
        # s.seek(0)
        result = g.parse(source=s, publicID=b+"/", format="json-ld")
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
        b = urlparse.urljoin(
                self.collbaseurl, 
                layout.COLL_BASE_TYPE_REF%{ 'id': type_vocab.get_id() }
                )
        # print("***** b: (type_vocab)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b+"/", format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (type_vocab)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj            = b
        type_vocab_data = type_vocab.get_values()
        vocab_list_url  = urlparse.urljoin(self.collbaseurl, type_vocab_data[ANNAL.CURIE.type_list])
        vocab_view_url  = urlparse.urljoin(self.collbaseurl, type_vocab_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                            )
            , (subj, RDFS.label,      Literal(type_vocab_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,        Literal(type_vocab_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type_list, URIRef(vocab_list_url)                        )
            , (subj, ANNAL.type_view, URIRef(vocab_view_url)                        )
            , (subj, ANNAL.uri,       URIRef(ANNAL.Vocabulary)                      )
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
        b = urlparse.urljoin(
                self.collbaseurl, 
                layout.COLL_BASE_VIEW_REF%{ 'id': view_user.get_id() }
                )
        # print("***** b: (view_user)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b+"/", format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (view_user)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj           = b    # b #@@ view_user.get_url()
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
        # Check field list contents
        fields = view_user_data[ANNAL.CURIE.view_fields]
        head   = property_value(g, URIRef(subj), ANNAL.view_fields)
        items  = scan_list(g, head)
        for f in fields:
            fi  = URIRef(urlparse.urljoin(self.collbaseurl, f[ANNAL.CURIE.field_id]))
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
        b = urlparse.urljoin(
                self.collbaseurl, 
                layout.COLL_BASE_USER_REF%{ 'id': user_default.get_id() }
                )
        # print("***** b: (user_default)")
        # print(repr(b))
        result = g.parse(source=s, publicID=b+"/", format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (user_default)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj              = b #@@ user_default.get_url()
        user_default_data = user_default.get_values()
        user_uri          = ANNAL.to_uri(user_default_data[ANNAL.CURIE.user_uri])
        user_perms        = user_default_data[ANNAL.CURIE.user_permission]
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.User)                              )
            , (subj, RDFS.label,        Literal(user_default_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(user_default_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(user_default_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(user_default_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.user_uri,    URIRef(user_uri)                                )
            , (subj, ANNAL.user_permission, Literal(user_perms[0])                      )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_jsonld_enum_list_type_list(self):
        """
        Read enumeration data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        Enum_list_type = RecordEnumFactory(layout.ENUM_LIST_TYPE_ID, layout.ENUM_LIST_TYPE_ID)
        list_type_list = Enum_list_type.load(
            self.testcoll, "Grid", altscope="all"
            )
        # Read user data as JSON-LD
        g = Graph()
        s = list_type_list._read_stream()
        b = urlparse.urljoin(
                self.collbaseurl,
                layout.COLL_BASE_ENUM_REF%
                    { 'type_id': list_type_list.get_type_id()
                    , 'id': list_type_list.get_id() 
                    }
                )
        # print("***** b: (list_type_list)")
        # print(repr(b))
        # print("***** s.read()"+s.read())
        # s.seek(0)
        result = g.parse(source=s, publicID=b+"/", format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (list_type_list)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        # @@TODO: currently have to deal here with inconsistency between file and URL layouts
        subj                = b #@@ list_type_list.get_url()
        subj                = ( "file://" + 
              os.path.join(
                TestBaseDir, 
                layout.SITEDATA_DIR,        # site-wide data collection
                layout.COLL_BASE_DIR,       # collection base directory
                layout.COLL_BASE_ENUM_REF%{ 'type_id': list_type_list.get_type_id(), 'id': list_type_list.get_id() }
                )
            )
        list_type_list_data = list_type_list.get_values()
        list_type_url       = ANNAL.to_uri(list_type_list_data[ANNAL.CURIE.uri])
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.Enum)                                )
            , (subj, RDF.type,          URIRef(ANNAL.Enum_list_type)                      )
            , (subj, RDFS.label,        Literal(list_type_list_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(list_type_list_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(list_type_list_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(list_type_list_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.uri,         URIRef(list_type_url)                             )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    def test_jsonld_image_ref(self):
        """
        Read image reference data as JSON-LD, and check resulting RDF triples
        """
        # Populate collection with record type, view and field
        imagepath = "%s/test-image.jpg"%TestBaseDir
        imageurl  = "file://"+imagepath
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
        # Create entity object to access image reference data 
        testdata  = RecordTypeData.load(self.testcoll, "testreftype")
        ref_image = EntityData.load(testdata, "refentity")
        # Read user data as JSON-LD
        g = Graph()
        s = ref_image._read_stream()
        b = self.entity_basedir("testcoll", "testreftype", "refentity")
        f = os.path.join(b, layout.ENTITY_DATA_FILE)
        # print("***** b: (ref_image)")
        # print(repr(b))
        # print("***** s.read()"+s.read())
        # s.seek(0)
        result = g.parse(source=s, publicID="file://"+b+"/", format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (ref_image)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj           = self.entity_url("testcoll", "testreftype", "refentity")
        ref_image_data = ref_image.get_values()
        blobns         = makeNamespace("blob", "http://example.org/blob/yyy#", ["reference"])
        type_uri       = blobns.to_uri(ref_image_data['@type'][0]) 
        for (s, p, o) in (
            [ (subj, RDF.type,          URIRef(ANNAL.EntityData)                     )
            , (subj, RDF.type,          URIRef(type_uri)                             )
            , (subj, RDFS.label,        Literal(ref_image_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,      Literal(ref_image_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,          Literal(ref_image_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,     Literal(ref_image_data[ANNAL.CURIE.type_id]) )
            , (subj, blobns.reference,  URIRef(imageurl)                             )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

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
        subj        = TestHostUri + v.rstrip("/")
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
        subj            = TestHostUri + v.rstrip("/")
        type_vocab_data = type_vocab.get_values()
        # vocab_list_url  = urlparse.urljoin(self.collbaseurl, type_vocab_data[ANNAL.CURIE.type_list])
        # vocab_view_url  = urlparse.urljoin(self.collbaseurl, type_vocab_data[ANNAL.CURIE.type_view])
        vocab_list_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_list])
        vocab_view_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                            )
            , (subj, RDFS.label,      Literal(type_vocab_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,        Literal(type_vocab_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type_list, URIRef(vocab_list_url)                        )
            , (subj, ANNAL.type_view, URIRef(vocab_view_url)                        )
            , (subj, ANNAL.uri,       URIRef(ANNAL.Vocabulary)                      )
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
            , 'annal:uri':                  "blob:type/test_new_type"
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
        subj          = TestHostUri + v.rstrip("/")
        type_new_data = type_new.get_values()
        # new_list_url  = urlparse.urljoin(self.collbaseurl, type_new_data[ANNAL.CURIE.type_list])
        # new_view_url  = urlparse.urljoin(self.collbaseurl, type_new_data[ANNAL.CURIE.type_view])
        new_list_url  = self.resolve_coll_url(self.testcoll, type_new_data[ANNAL.CURIE.type_list])
        new_view_url  = self.resolve_coll_url(self.testcoll, type_new_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                            )
            , (subj, RDFS.label,      Literal(type_new_data[RDFS.CURIE.label])      )
            , (subj, RDFS.comment,    Literal(type_new_data[RDFS.CURIE.comment])    )
            , (subj, ANNAL.id,        Literal(type_new_data[ANNAL.CURIE.id])        )
            , (subj, ANNAL.type_id,   Literal(type_new_data[ANNAL.CURIE.type_id])   )
            , (subj, ANNAL.type_list, URIRef(new_list_url)                          )
            , (subj, ANNAL.type_view, URIRef(new_view_url)                          )
            , (subj, ANNAL.uri,       URIRef(type_new_data[ANNAL.CURIE.uri])        )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    # @@@ test case for set/list conflicts
    #     create data with multiple rdfs:seeAlso values
    #     annal:user_permission declared as set (how?)
    #     rdfs:seeAlso declared as list, should be set

    def test_http_jsonld_vocab_annal(self):
        """
        Read annal: vocabulary data as JSON-LD using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()

        # Create object to access vocabulary data 
        vocabtypeinfo = EntityTypeInfo(self.testcoll, "_vocab")
        annalvocab    = vocabtypeinfo.get_entity("annal")

        # Read vocabulary data as JSON-LD
        v = entity_url(coll_id="testcoll", type_id="_vocab", entity_id="annal")
        u = TestHostUri + entity_resource_url(
            coll_id="testcoll", type_id="_vocab", entity_id="annal",
            resource_ref=layout.VOCAB_META_FILE
            )
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** u: (_vocab/annal)")
        # print(repr(u))
        # print("***** c: (_vocab/annal)")
        # print r.content
        with MockHttpDictResources(u, self.get_context_mock_dict(v)):
            result = g.parse(data=r.content, publicID=u, base=u, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (_vocab/annal)")
        # print(g.serialize(format='turtle', indent=4))

        # Check the resulting graph contents
        subj       = TestHostUri + v.rstrip("/")
        annal_data = annalvocab.get_values()
        seeAlso_1  = "https://github.com/gklyne/annalist/blob/master/src/annalist_root/annalist/identifiers.py"
        for (s, p, o) in (
            [ (subj, RDF.type,      URIRef(ANNAL.EntityData)                 )
            , (subj, RDF.type,      URIRef(ANNAL.Vocabulary)                 )
            , (subj, RDFS.label,    Literal(annal_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,  Literal(annal_data[RDFS.CURIE.comment])  )
            , (subj, RDFS.seeAlso,  URIRef(seeAlso_1)                        )            
            , (subj, ANNAL.id,      Literal(annal_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id, Literal(annal_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type,    URIRef(ANNAL.Vocabulary)                 )
            , (subj, ANNAL.uri,     URIRef(ANNAL._baseUri)                   )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g)
        return

    #   -----------------------------------------------------------------------------
    #   Entity content negotiation tests
    #   -----------------------------------------------------------------------------

    def test_http_conneg_jsonld_entity1(self):
        """
        Read default entity data as JSON-LD using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")
        # Read entity data as JSON-LD
        u = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        # print "@@ test_http_conneg_jsonld_entity1: uri %s"%u
        r = self.client.get(u, HTTP_ACCEPT="application/ld+json")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.ENTITY_DATA_FILE)
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** v: (entity1)")
        # print(repr(v))
        # print("***** c: (entity1)")
        # print r.content
        with MockHttpDictResources(v, self.get_context_mock_dict(v)):
            result = g.parse(data=r.content, publicID=v, base=v, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj        = entity1.get_url().rstrip("/")
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

    def test_http_conneg_json_entity1(self):
        """
        Read default entity data as JSON-LD using HTTP, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        # Create entity object to access entity data 
        testdata = RecordTypeData.load(self.testcoll, "testtype")
        entity1  = EntityData.load(testdata, "entity1")
        # Read entity data as JSON-LD
        u = entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1")
        r = self.client.get(u, HTTP_ACCEPT="application/json")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.ENTITY_DATA_FILE)
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** v: (entity1)")
        # print(repr(v))
        # print("***** c: (entity1)")
        # print r.content
        with MockHttpDictResources(v, self.get_context_mock_dict(v)):
            result = g.parse(data=r.content, base=v, format="json-ld")
            # result = g.parse(data=r.content, publicID=v, base=v, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (entity1)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj        = entity1.get_url().rstrip("/")
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

    def test_http_conneg_jsonld_type_vocab(self):
        """
        Read type data as JSON-LD, and check resulting RDF triples
        """
        # Generate collection JSON-LD context data
        self.testcoll.generate_coll_jsonld_context()
        type_vocab = self.testcoll.get_type("_vocab")
        # Read type data as JSON-LD
        u = recordtype_url(coll_id="testcoll", type_id=type_vocab.get_id())
        r = self.client.get(u, HTTP_ACCEPT="application/ld+json")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        v = r['Location']
        self.assertEqual(v, TestHostUri+u+layout.TYPE_META_FILE)
        r = self.client.get(v)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        g = Graph()
        # print("***** u: (type_vocab)")
        # print(repr(u))
        # print("***** c: (type_vocab)")
        # print r.content
        # Read graph data with HTTP mocking for context references
        with MockHttpDictResources(v, self.get_context_mock_dict(v)):
            result = g.parse(data=r.content, publicID=v, base=v, format="json-ld")
        # print "*****"+repr(result)
        # print("***** g: (type_vocab)")
        # print(g.serialize(format='turtle', indent=4))
        # Check the resulting graph contents
        subj            = TestHostUri + u.rstrip("/")
        type_vocab_data = type_vocab.get_values()
        vocab_list_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_list])
        vocab_view_url  = self.resolve_coll_url(self.testcoll, type_vocab_data[ANNAL.CURIE.type_view])
        for (s, p, o) in (
            [ (subj, RDF.type,        URIRef(ANNAL.Type)                            )
            , (subj, RDFS.label,      Literal(type_vocab_data[RDFS.CURIE.label])    )
            , (subj, RDFS.comment,    Literal(type_vocab_data[RDFS.CURIE.comment])  )
            , (subj, ANNAL.id,        Literal(type_vocab_data[ANNAL.CURIE.id])      )
            , (subj, ANNAL.type_id,   Literal(type_vocab_data[ANNAL.CURIE.type_id]) )
            , (subj, ANNAL.type_list, URIRef(vocab_list_url)                        )
            , (subj, ANNAL.type_view, URIRef(vocab_view_url)                        )
            , (subj, ANNAL.uri,       URIRef(ANNAL.Vocabulary)                      )
            ]):
            self.assertIn( (URIRef(s), URIRef(p), o), g )
        return

    #   -----------------------------------------------------------------------------
    #   Entity list content negotiation tests
    #   -----------------------------------------------------------------------------

    def get_list_json(self, list_url, subj_ref, coll_id="testcoll", type_id=None, context_path=""):
        """
        Return list of entity nodes from JSON list
        """
        #@@
        # list_url_abs    = urlparse.urljoin(TestHostUri, list_url)
        # list_url_query = urlparse.urlsplit(list_url).query
        # if list_url_query != "":
        #     list_url_query = "?" + list_url_query
        # expect_json_url = list_url_abs + layout.ENTITY_LIST_FILE + list_url_query
        #@@
        self.testcoll.generate_coll_jsonld_context()
        r = self.client.get(list_url, HTTP_ACCEPT="application/ld+json")
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        json_url = r['Location']
        expect_json_url = make_resource_url(TestHostUri, list_url, layout.ENTITY_LIST_FILE)
        self.assertEqual(json_url, expect_json_url)
        r = self.client.get(json_url)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # print("***** json_url: "+json_url)
        # print("***** c: (testcoll/_type list)")
        # print r.content
        g = Graph()
        with MockHttpDictResources(json_url, self.get_context_mock_dict(json_url, context_path=context_path)):
            result = g.parse(data=r.content, publicID=json_url, base=json_url, format="json-ld")
        # print("***** g: (testcoll/_type list)")
        # print(g.serialize(format='turtle', indent=4))
        # print("*****")
        # for t in g.triples((None, None, None)):
        #     print repr(t)
        # print("*****")
        subj = urlparse.urljoin(json_url, subj_ref)
        for (s, p, o) in (
            [ (subj, ANNAL.entity_list, None)
            ]):
            self.assertTripleIn( (URIRef(s), URIRef(p), o), g)
        list_head  = g.value(subject=URIRef(subj), predicate=URIRef(ANNAL.entity_list))
        list_items = list(self.scan_rdf_list(g, list_head))
        return (json_url, list_items)

    def test_http_conneg_jsonld_list_coll_type(self):
        """
        Content negotiate for JSON-LD version of a list of collection-defined types
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
        (json_url, list_items) = self.get_list_json(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../"
            )
        t_uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="_type", entity_id="testtype"))
        self.assertEqual(len(list_items), 1)
        self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_jsonld_list_coll_all(self):
        """
        Content negotiate for JSON-LD version of a list of collection-defined entities of all types
        """
        list_url = entitydata_list_all_url("testcoll", scope=None)
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Default_list_all", scope=None
            )
        (json_url, list_items) = self.get_list_json(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path=""
            )
        t_uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="_type", entity_id="testtype"))
        e1uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1"))
        self.assertEqual(len(list_items), 2)
        self.assertIn(URIRef(t_uri), list_items)
        self.assertIn(URIRef(e1uri), list_items)
        return

    def test_http_conneg_jsonld_list_coll_all_list(self):
        """
        Content negotiate for JSON-LD version of a list of collection-defined entities of all types
        """
        list_url = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope=None
            )
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope=None
            )
        (json_url, list_items) = self.get_list_json(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../../d/"
            )
        t_uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="_type", entity_id="testtype"))
        e1uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity1"))
        self.assertEqual(len(list_items), 1)
        self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_jsonld_list_site_type(self):
        """
        Content negotiate for JSON-LD version of a list of collection-defined types
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
        (json_url, list_items) = self.get_list_json(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../"
            )
        # print "@@ "+repr(list_items)
        expect_type_ids = get_site_types()
        expect_type_ids.add("testtype")
        self.assertEqual(len(list_items), len(expect_type_ids))
        for entity_id in expect_type_ids:
            t_uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="_type", entity_id=entity_id))
            self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_jsonld_list_site_all_list(self):
        """
        Content negotiate for JSON-LD version of a list of 
        collection-defined entities of all types
        """
        list_url = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope="all"
            )
        subj_ref = entitydata_list_all_url(
            "testcoll", list_id="Type_list", scope="all"
            )
        (json_url, list_items) = self.get_list_json(
            list_url, subj_ref, coll_id="testcoll", type_id=None, context_path="../../d/"
            )
        expect_type_ids = get_site_types()
        expect_type_ids.add("testtype")
        self.assertEqual(len(list_items), len(expect_type_ids))
        for entity_id in expect_type_ids:
            t_uri = urlparse.urljoin(json_url, entity_url(coll_id="testcoll", type_id="_type", entity_id=entity_id))
            self.assertIn(URIRef(t_uri), list_items)
        return

    def test_http_conneg_jsonld_list_coll_wrongname(self):
        """
        This is a test of the regular expression used to access list resources,
        to ensure the '.' must be a literal '.' and not a wildcard.
        """
        list_url = entitydata_list_type_url(
            "testcoll", "_type",
            scope=None
            )
        wrong_name     = layout.ENTITY_LIST_FILE.replace('.', '*')
        wrong_json_url = make_resource_url(TestHostUri, list_url, wrong_name)
        with SuppressLogging(logging.WARNING):
            r = self.client.get(wrong_json_url)
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "NOT FOUND")
        return

# End.
