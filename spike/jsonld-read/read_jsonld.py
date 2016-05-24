#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Jay O'Donnel's challenge per https://twitter.com/djdonnell/status/734964072953745408

import os

import logging
log = logging.getLogger(__name__)

from rdflib import Graph, URIRef, Literal

sourceurl = "https://gist.githubusercontent.com/jaydonnell/fff70642cbb7ad243701c1249337273e/raw/d47c6b61df69d1a7df76af78d09fc4a431cfe8d2/jsonld.json"
sourcedata = u"""
{
    "@id" : "https://en.wikipedia.org/wiki/Frozen_(2013_film)",
    "@type" : [ "http://schema.org/Movie" ],
    "http://schema.org/releasedEvent" : [ {
      "@value" : "2013-11-27"
    }],
    "http://schema.org/copyrightYear" : [ {
      "@type" : "http://www.w3.org/2001/XMLSchema#integer",
      "@value" : "2013"
    }],
    "http://schema.org/name" : [ {
          "@language" : "pt-pt",
          "@value" : "Frozen - O Reino do Gelo"
        }, {
          "@language" : "de",
          "@value" : "Die Eiskönigin - Völlig unverfroren"
        }, {
          "@language" : "en-us",
          "@value" : "Frozen"
        }],
    "http://schema.org/genre" : [ {
          "@value" : "Family"
        }, {
          "@value" : "Adventure"
        } ],
    "http://schema.org/image" : [ {
      "@id" : "https://en.wikipedia.org/wiki/Frozen_(2013_film)#/media/File:Frozen_(2013_film)_poster.jpg"
    }]
}
"""

def read_jsonld():
    g = Graph()
    result = g.parse(location=sourceurl, format="json-ld")
    # print "*****"+repr(result)
    # print("***** g:")
    # print(g.serialize(format='turtle', indent=4))
    return g

def f(g, doc, property_name, lang=None):
    # Assuming 'doc' here is the URL of the film to query
    for v in g.objects(URIRef(doc), URIRef(property_name)):
        if not lang or (isinstance(v, Literal) and v.language == lang):
            return v
    return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    g = read_jsonld()
    d = "https://en.wikipedia.org/wiki/Frozen_(2013_film)"
    assert str(f(g, d, "http://schema.org/releasedEvent")) == "2013-11-27"
    assert str(f(g, d, "http://schema.org/copyrightYear")) == "2013"
    assert unicode(f(g, d, "http://schema.org/name", "pt-pt")) == u"Frozen - O Reino do Gelo"
    assert unicode(f(g, d, "http://schema.org/name", "de"))    == u"Die Eiskönigin - Völlig unverfroren"
    # etc.

