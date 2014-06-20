"""
Defines Annalist built-in identifier values (URIs)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class Curiespace(object):
    """
    Placeholder class for CURIE values in namespace.
    """
    def __init__(self):
        return


class Namespace(object):
    """
    Class represents namespace of URI identifiers.

    Provides expressions for URI and CURIE values of each identrifier in the namespace.
    """

    def __init__(self, prefix, baseUri):
        """
        Initialise a namespace.

        prefix      a CURIE prefix to be associated with this namespace.
        _baseUri    a base URI for all names in this namespace
        """
        self._prefix  = prefix
        self._baseUri = baseUri
        self.CURIE    = Curiespace()
        return

    def mk_curie(self, name):
        """
        Make a CURIE string for an identifier in this namespace
        """
        return self._prefix+":"+name

    def mk_uri(self, name):
        """
        Make a URI string for an identifier in this namespace
        """
        return self._baseUri+name

def makeNamespace(prefix, baseUri, names):
    """
    Create a namespace with given prefix, base URI and set of local names.

    Returns the namespace value.  Attributes of the namespace value are URIs
    for the corresponding identifier (e.g. ANNAL.Site, cf. below).  Attributes of
    the CURIE attribute are CURIES (e.g. ANNAL.CURIE.Site).
    """
    ns = Namespace(prefix, baseUri)
    for name in names:
        setattr(ns, name, ns.mk_uri(name))
        setattr(ns.CURIE, name, ns.mk_curie(name))
    return ns

"""
Partial enumeration of RDF namespace - add others as needed
"""
RDF = makeNamespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    [ "Property", "Statement", "List"
    , "type", "value"
    , "first", "rest", "nil"
    ])

"""
Partial enumeration of RDFS namespace - add others as needed
"""
RDFS = makeNamespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#",
    [ "Resource", "Class", "Literal", "Container", "Datatype"
    , "label", "comment", "member", "seeAlso"
    ])

"""
Annalist namespace terms
"""
ANNAL = makeNamespace("annal", "http://purl.org/annalist/2014/",
    [ "EntityRoot", "Entity"
    , "Site", "SiteData", "Collection", "Type", "View", "List", "Entity"
    , "Collection_Types", "Collection_Views", "Collection_Lists"
    , "Type", "View", "List", "Field"
    , "Type_Data", "EntityData"
    , "id", "type", "label", "help", "uri", "urihost", "uripath"
    ])

# End.
