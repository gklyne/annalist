import os

import logging
log = logging.getLogger(__name__)

from rdflib import Graph, URIRef, Literal

from identifiers import RDF, RDFS, ANNAL

def read_jsonld():
    g = Graph()
    r = os.path.dirname(os.path.abspath(__file__))
    b = os.path.join(r, "testcoll/d/testtype/entity2/")
    print("***** b:")
    print(repr(b))
    f = os.path.join(b, "entity-data.jsonld")
    s = open(f, "rt")
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    print("***** g:")
    print(g.serialize(format='turtle', indent=4))

def _exists_path(path, base=None):
    """
    Tests for existence of supplied path resolved against a supplied base,
    (or current directory if base is not supplied), and returns a fully 
    qualified path, or None.
    """
    if base is None:
        base = os.getcwd()
    # print "**** base:"+base
    # print "**** path:"+path
    p = os.path.join(base, path)
    # print "**** join:"+p
    d = os.path.dirname(p)
    if d and os.path.isdir(d):
        if p and os.path.isfile(p):
            return p
    return None

def _read_stream(path):
    """
    Opens a (file-like) stream to read JSON-LD data.

    Returns the stream object, which implements the context protocol to
    close the stream on exit from a containign with block; e.g.

        with _read_stream(path) as f:
            // read data from f
        // f is closed here
    """
    f_stream  = None
    if path:
        try:
            f_stream = open(path, "rt")
        except IOError, e:
            if e.errno != errno.ENOENT:
                raise
            log.error("EntityRoot._read_stream: no file %s"%(path))
    return f_stream

def test_jsonld_site():
    """
    Read site data as JSON-LD, and check resulting RDF triples
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/_annalist_site/_annalist_collection/coll_meta.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** site metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath, "../"))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("_annalist_site")
    ann_type         = URIRef(ANNAL.SiteData)
    ann_type_id      = Literal("_coll")
    label            = Literal("Annalist data notebook test site")
    comment          = Literal("Annalist test site metadata and site-wide values.")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    assert (subj, URIRef(RDFS.comment),  comment    ) in g
    print "test_jsonld_site: OK"
    return

def test_jsonld_collection():
    """
    Read new collection data as JSON-LD, and check resulting RDF triples
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/_annalist_collection/coll_meta.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** collection metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath, "../"))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("testcoll")
    ann_type         = URIRef(ANNAL.Collection)
    ann_type_id      = Literal("_coll")
    label            = Literal("Collection testcoll")
    comment          = Literal("Description of Collection testcoll")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    assert (subj, URIRef(RDFS.comment),  comment    ) in g
    print "test_jsonld_collection: OK"
    return

def test_jsonld_entity1():
    """
    Read entity data as JSON-LD, and check resulting RDF triples
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/d/testtype/entity1/entity-data.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** entity1 metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("entity1")
    ann_type         = URIRef(ANNAL.EntityData)
    ann_type_id      = Literal("testtype")
    label            = Literal("Entity testcoll/testtype/entity1")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    print "test_jsonld_entity1: OK"
    return

def test_jsonld_site_type():
    """
    Read site type data as JSON-LD, and check resulting RDF triples
    """
    # Generate collection JSON-LD context data
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/_annalist_site/_annalist_collection/types/Default_type/type_meta.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** site Default_type metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("Default_type")
    ann_type         = URIRef(ANNAL.Type)
    ann_type_id      = Literal("_type")
    label            = Literal("Default record")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    print "test_jsonld_site_type: OK"
    return

def test_jsonld_coll_type():
    """
    Read collection type data as JSON-LD, and check resulting RDF triples
    """
    # Generate collection JSON-LD context data
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/_annalist_collection/types/testtype/type_meta.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** site Default_type metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("testtype")
    ann_type         = URIRef(ANNAL.Type)
    ann_type_id      = Literal("_type")
    label            = Literal("RecordType testcoll/testtype")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    print "test_jsonld_coll_type: OK"
    return

def test_jsonld_entity2():
    """
    Read entity data as JSON-LD, and check resulting RDF triples

    entity2 is very similar to entity1, but is coded with an absolute path base URI:

        "@context": [
          { "@base": "/testsite/c/testcoll/d/" },
          "file:////Users/graham/workspace/github/gklyne/annalist/spike/jsonld_context/testsite/c/testcoll/d/coll_context.jsonld"
        ]

    NOTE: this test case is not portable.
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/d/testtype/entity2/entity-data.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "http://example.org" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** entity2 metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef(
        "http://example.org" + 
        "/testsite/c/testcoll/d/testtype/entity2" +
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("entity2")
    ann_type         = URIRef(ANNAL.EntityData)
    ann_type_id      = Literal("testtype")
    label            = Literal("Entity testcoll/testtype/entity2")
    testbase         = "http://example.org/test/#"
    assert (subj, URIRef(ANNAL.id),        ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),      ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id),   ann_type_id) in g
    assert (subj, URIRef(RDFS.label),      label      ) in g
    print "test_jsonld_entity2: OK"
    return

def test_jsonld_entity3():
    """
    Read entity data as JSON-LD, and check resulting RDF triples

    entity3 is very similar to entity1, but also includes a test for a
    URI with empty fragment id.
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/d/testtype/entity3/entity-data.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+repr(s)
    # print "***** s.read:\n"+s.read()
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** entity3 metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("entity3")
    ann_type         = URIRef(ANNAL.EntityData)
    ann_type_id      = Literal("testtype")
    ann_uri          = URIRef(ANNAL._baseUri)
    # print "***** ann_uri:"+repr(ann_uri)
    label            = Literal("Entity testcoll/testtype/entity3")
    assert (subj, URIRef(ANNAL.id),      ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),    ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id), ann_type_id) in g
    assert (subj, URIRef(ANNAL.uri),     ann_uri    ) in g
    assert (subj, URIRef(RDFS.label),    label      ) in g
    print "test_jsonld_entity3: OK"
    return

def test_jsonld_entity4():
    """
    Read entity data as JSON-LD, and check resulting RDF triples

    entity4 is very similar to entity1, but uses a namespace prefix
    test:, defined as "http://example.org/test/#"
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testcoll/d/testtype/entity4/entity-data.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+s.read()
    # s.seek(0)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** entity4 metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    subj             = URIRef("file://" + 
        os.path.dirname(os.path.normpath(os.path.join(testbasedir, testpath))) + 
        "/"
        )
    # print "***** subj:"+repr(subj)
    ann_id           = Literal("entity4")
    ann_type         = URIRef(ANNAL.EntityData)
    ann_type_id      = Literal("testtype")
    label            = Literal("Entity testcoll/testtype/entity4")
    testbase         = "http://example.org/test/#"
    assert (subj, URIRef(ANNAL.id),        ann_id     ) in g
    assert (subj, URIRef(ANNAL.type),      ann_type   ) in g
    assert (subj, URIRef(ANNAL.type_id),   ann_type_id) in g
    assert (subj, URIRef(RDFS.label),      label      ) in g
    assert (subj, URIRef(testbase+"prop"), URIRef(testbase+"obj")) in g
    print "test_jsonld_entity4: OK"
    return

def test_jsonld_testzywv():
    """
    Read entity data as JSON-LD, and check resulting RDF triples

    This follows the logic of test entity1, but uses a data collection generated 
    by the Annalist test suite, which is proving problematic.
    """
    testbasedir = os.path.join(os.getcwd(), "testsite")
    testpath    = "c/testzywv/d/testreftype/refentity/entity_data.jsonld"
    p = _exists_path(testpath, base=testbasedir)
    b = "file://" + os.path.dirname(p) + "/"
    s = _read_stream(p)
    g = Graph()
    # print "***** p:"+repr(p)
    # print "***** b:"+repr(b)
    # print "***** s:"+s.read()
    # s.seek(0)
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    # print "***** refentity metadata:"
    # print(g.serialize(format='turtle', indent=4))
    # Check the resulting graph contents
    zywvbase         = "http://example.org/zywv/yyy#"
    imageref         = "file:///Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/test-image.jpg"
    subj = URIRef("file://" + os.path.dirname(p))
    ann_id           = Literal("refentity")
    ann_type_id      = Literal("testreftype")
    ann_type         = URIRef(zywvbase+"type/test_reference_type")
    label            = Literal("test_ref_image label")
    # print "***** subj: "+repr(subj)
    # print "***** ann_type: "+repr(ann_type)
    assert (subj, URIRef(RDF.type),        URIRef(ANNAL.EntityData) ) in g
    assert (subj, URIRef(RDF.type),        ann_type                 ) in g
    assert (subj, URIRef(ANNAL.id),        ann_id                   ) in g
    assert (subj, URIRef(ANNAL.type_id),   ann_type_id              ) in g
    assert (subj, URIRef(ANNAL.type),      ann_type                 ) in g
    assert (subj, URIRef(RDFS.label),      label                    ) in g
    assert (subj, URIRef(zywvbase+"reference"), URIRef(imageref)    ) in g
    print "test_jsonld_testzywv: OK"
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # read_jsonld()
    test_jsonld_site()
    test_jsonld_collection()
    test_jsonld_entity1()
    test_jsonld_site_type()
    test_jsonld_coll_type()
    test_jsonld_entity2()     # Non-portable test case
    test_jsonld_entity3()     # Non-portable test case
    test_jsonld_entity4()     # Test case using additional prefix
    test_jsonld_testzywv()    # Test case failing in main Annalist test suite

