import os
from rdflib import Graph, URIRef, Literal

def read_jsonld():
    g = Graph()
    r = os.path.dirname(os.path.abspath(__file__))
    b = os.path.join(r, "testcoll/d/testtype/entity1/")
    print("***** b:")
    print(repr(b))
    f = os.path.join(b, "entity-data.jsonld")
    s = open(f, "rt")
    result = g.parse(source=s, publicID=b, format="json-ld")
    # print "*****"+repr(result)
    print("***** g:")
    print(g.serialize(format='turtle', indent=4))

if __name__ == "__main__":
    read_jsonld()

