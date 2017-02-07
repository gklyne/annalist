"""
Installable collections data.  This is used by annalist-manager and by some test code.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# Collection data
#
# NOTE: when updating this, src/setup.py and src/MANIFEST.in also need to be updated.
#       Also, am_help.py
#
# @@TODO: consider ways to discover these details by scanning the file system?
#
installable_collections = (
    { "Namespace_defs":      
        { 'data_dir': "namedata"
        , 'coll_meta':
            { "rdfs:label":     "Namespace definitions"
            , "rdfs:comment":   "# Namespace definitions"+
                                "\r\n\r\n"+
                                "Defines some common vocabulary namespaces "+
                                "not included in the base site data."+
                                "\r\n"
            , "annal:comment":  "Initialized by: `annalist-manager installcollection`"
            }
        } 
    , "Concept_defs":   
        { 'data_dir': "Concept_defs"
        , 'coll_meta':
            { "rdfs:label":     "Concept definitions"
            , "rdfs:comment":   "# Concept definitions\r\n\r\n"+
                                "This collection defines types, views and fields that can be used "+
                                "to associate concepts (based on the SKOS vocabulary) with entities."+
                                "\r\n"
            , "annal:comment":  "Initialized by: `annalist-manager installcollection`"
            , "annal:default_view_type":    "Concept"
            }
        }
    , "Journal_defs":   
        { 'data_dir': "Journal_defs"
        , 'coll_meta':
            { "rdfs:label":     "Journal and resource definitions"
            , "rdfs:comment":   "# Journal and resource definitions"+
                                "\r\n\r\n"+
                                "This collection defines types, views and fields that "+
                                "can be used to incorporate references to uploaded, "+
                                "imported or linked media resources into entity views."+
                                "\r\n\r\n"+
                                "Also defines a \"Journal\" type that can be used to record "+
                                "(mostly) unstructured information about some process, "+
                                "along with associated resources."+
                                "\r\n"
            , "annal:inherit_from":         "_coll/Concept_defs"
            , "annal:comment":              "Initialized by: `annalist-manager installcollection`"
            , "annal:default_view_id":      "Journal_note_view"
            , "annal:default_view_type":    "Journal"
            , "annal:default_view_entity":  "01_journal_resources"
            }
        }
    , "Bibliography_defs":   
        { 'data_dir': "Bibliography_defs"
        , 'coll_meta':
            { "rdfs:label":     "Bibliography definitions"
            , "rdfs:comment":   "# Bibliography definitions"+
                                "\r\n\r\n"+
                                "Defines types and views for bibliographic definitions, "+
                                "based loosely on BibJSON."
            , "annal:comment":  "Initialized by `annalist-manager installcollection`"
            }
        }
    , "RDF_schema_defs":   
        { 'data_dir': "RDF_schema_defs"
        , 'coll_meta':
            { "rdfs:label":     "RDF schema terms for defining vocabularies"
            , "rdfs:comment":   "# Definitions for defining RDF schema for vocabularies"+
                                "\r\n\r\n"+
                                "This Annalist collection contains definitions that may "+
                                "be imported to creaing RDF schema definitions as an "+
                                "Annalist collection."+
                                "\r\n\r\n"+
                                "NOTE: current limitations of Annalist mean that the "+
                                "exported JSON-LD does not directly use standard "+
                                "RDF schema terms for everything.  "+
                                "For example, subclasses are referenced using a "+
                                "local URI reference rather than the global "+
                                "absolute URI, which can be obtained by defererencing "+
                                "the given reference and extracting the `annal:uri` "+
                                "value from there."+
                                "\r\n"
            , "annal:comment":  "Initialized by: `annalist-manager installcollection`"
            }
        }
    , "Annalist_schema":   
        { 'data_dir': "Annalist_schema"
        , 'coll_meta':
            { "rdfs:label":     "Schema definitions for terms in the Annalist namespace"
            , "rdfs:comment":   "# Schema definitions for terms in the Annalist namespace"+
                                "\r\n\r\n"+
                                "This is an Annalist collection which describes terms "+
                                "in the Annalist (`annal:`) namespace."+
                                "\r\n\r\n"+
                                "It uses definitions from collection `RDF_schema_defs`."+
                                "\r\n"
            , "annal:comment":  "Initialized by `annalist-manager installcollection`"
            , "annal:inherit_from": "_coll/RDF_schema_defs"
            , "annal:default_list": "Classes"
            }
        }
    # , "...":   
    #     { 'data_dir': "..."
    #     , 'coll_meta':
    #         { "rdfs:label":     "..."
    #         , "rdfs:comment":   "# ...\r\n\r\n"+
    #                             "... "+
    #                             "..."
    #         , "annal:comment":  "Initialized by `annalist-manager installcollection`"
    #         }
    #     }
    })

# End.
