# ro_namespaces.py

"""
Research Object manifest read, write, decode functions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

#import sys
#import os
#import os.path
#import re
#import urlparse
#import logging

import rdflib
import rdflib.namespace

class Namespace(object):
    def __init__(self, baseUri):
        self.baseUri = baseUri
        return

def makeNamespace(baseUri, names):
    ns = Namespace(baseUri)
    for name in names:
        setattr(ns, name, rdflib.URIRef(baseUri+name))
    return ns

ao      = rdflib.URIRef("http://purl.org/ao/")
ore     = rdflib.URIRef("http://www.openarchives.org/ore/terms/")
foaf    = rdflib.URIRef("http://xmlns.com/foaf/0.1/")
ro      = rdflib.URIRef("http://purl.org/wf4ever/ro#")
roevo   = rdflib.URIRef("http://purl.org/wf4ever/roevo#")
roterms = rdflib.URIRef("http://purl.org/wf4ever/roterms#")
wfprov  = rdflib.URIRef("http://purl.org/wf4ever/wfprov#")
wfdesc  = rdflib.URIRef("http://purl.org/wf4ever/wfdesc#")
wf4ever = rdflib.URIRef("http://purl.org/wf4ever/wf4ever#")
dcterms = rdflib.URIRef("http://purl.org/dc/terms/")

RDF     = makeNamespace(rdflib.namespace.RDF.uri,
            [ "Seq", "Bag", "Alt", "Statement", "Property", "XMLLiteral", "List", "PlainLiteral"
            , "subject", "predicate", "object", "type", "value", "first", "rest"
            , "nil"
            ])
RDFS    = makeNamespace(rdflib.namespace.RDFS.uri,
            [ "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label"
            , "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container"
            , "ContainerMembershipProperty", "member", "Datatype"
            ])
RO = makeNamespace(ro, 
            [ "ResearchObject", "AggregatedAnnotation"
            , "annotatesAggregatedResource"
            ])
ROEVO = makeNamespace(roevo, 
            [ "LiveRO","SnapshotRO","ArchivedRO","isFinalized"
            ])
ORE = makeNamespace(ore,
            [ "Aggregation", "AggregatedResource", "Proxy"
            , "aggregates", "proxyFor", "proxyIn"
            , "isDescribedBy"
            ])
AO = makeNamespace(ao, 
            [ "Annotation"
            , "body"
            , "annotatesResource"
            ])
DCTERMS = makeNamespace(dcterms, 
            [ "identifier", "description", "title", "creator", "created"
            , "subject", "format", "type"
            ])
ROTERMS = makeNamespace(roterms, 
            [ "note", "resource", "defaultBase"
            ])

# End.
