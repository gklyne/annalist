"""
Entity resource access (imported and uploaded files).

This module contains functions to help access resource data that is 
attached to an entity (or collection).

It contains logic for accessing raw JSON-LD data, or accessing that data converted to 
some other format (e.g. Turtle).
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import json
import StringIO
import logging
log = logging.getLogger(__name__)

from rdflib                             import Graph, URIRef, Literal

from annalist                           import message
from annalist                           import layout

from annalist.models.entitytypeinfo     import EntityTypeInfo

# Resource info data for built-in entity data

collection_fixed_json_resources = (
    [ { "resource_name": layout.COLL_META_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.COLL_PROV_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.COLL_CONTEXT_FILE,  "resource_dir": layout.COLL_BASE_DIR, 
                                                    "resource_type": "application/ld+json" }
    ])

entity_fixed_json_resources = (
    [ { "resource_name": layout.COLL_META_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.COLL_PROV_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.TYPE_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.TYPE_PROV_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.LIST_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.LIST_PROV_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.VIEW_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.VIEW_PROV_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.GROUP_META_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.GROUP_PROV_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.FIELD_META_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.FIELD_PROV_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.VOCAB_META_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.VOCAB_PROV_FILE,    "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.USER_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.USER_PROV_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.ENUM_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.ENUM_PROV_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.TYPEDATA_META_FILE, "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.ENTITY_DATA_FILE,   "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.ENTITY_PROV_FILE,   "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    ])

entity_list_json_resources = (
    # [ { "resource_name": layout.COLL_META_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
    #                                                 "resource_type": "application/ld+json" }
    # , { "resource_name": layout.COLL_PROV_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
    #                                                 "resource_type": "application/ld+json" }
    # , { "resource_name": layout.COLL_CONTEXT_FILE,  "resource_dir": layout.COLL_BASE_DIR, 
    #                                                 "resource_type": "application/ld+json" }
    [ { "resource_name": layout.ENTITY_LIST_FILE,   "resource_dir": ".", 
                                                    "resource_type": "application/ld+json" }
    ])

# Resource access functions

def entity_resource_file(entity, resource_info):
    """
    Return a file object that reads out the content of a resource attached to a specified entity.
    """
    return entity.resource_file(resource_info["resource_path"])

def json_resource_file(baseurl, jsondata, resource_info):
    """
    Return a file object that reads out a JSON version of the supplied entity values data. 
    """
    response_file = StringIO.StringIO()
    json.dump(jsondata, response_file, indent=2, separators=(',', ': '), sort_keys=True)
    response_file.seek(0)
    return response_file

def turtle_resource_file(baseurl, jsondata, resource_info):
    """
    Return a file object that reads out a Turtle version of the supplied entity values data.

    baseurl     base URL for resolving relative URI references for Turtle output.
    jsondata    is the data to be formatted and returned.
    links       is an optional array of link values to be added to the HTTP response
                (see method add_link_header for description).
    """
    jsondata_file = json_resource_file(baseurl, jsondata, resource_info)
    g = Graph()
    g = g.parse(source=jsondata_file, publicID=baseurl, format="json-ld")
    response_file = StringIO.StringIO()
    try:
        g.serialize(destination=response_file, format='turtle', indent=4)
    except Exception as e:
        reason = str(e)
        log.warning(message.TURTLE_SERIALIZE_ERROR)
        log.info(reason)
        response_file.write("\n\n***** ERROR ****\n\n")
        response_file.write(message.TURTLE_SERIALIZE_ERROR)
        response_file.write("\n\n%s:\n\n"%message.TURTLE_SERIALIZE_REASON)
        response_file.write(reason)
    response_file.seek(0)
    return response_file

def make_turtle_resource_info(json_resource):
    """
    Return Turtle resource description for fixed JSON resource
    """
    turtle_resource = (
        { "resource_name":      json_resource["resource_name"][0:-7]+".ttl"
        , "resource_dir":       json_resource["resource_dir"]
        , "resource_type":      "text/turtle"
        , "resource_access":    turtle_resource_file
        })
    return turtle_resource

def find_fixed_resource(fixed_json_resources, resource_ref):
    """
    Return a description for the indicated fixed resource from a supplied table,
    or None
    """
    # log.debug("CollectionResourceAccess.find_resource %s/d/%s"%(coll.get_id(), resource_ref))
    for fj in fixed_json_resources:
        if fj["resource_name"] == resource_ref:
            fr = dict(fj, resource_path=os.path.join(fj["resource_dir"]+"/", resource_ref))
            return fr
        ft = make_turtle_resource_info(fj)
        if ft["resource_name"] == resource_ref:
            fr = dict(ft, resource_path=os.path.join(ft["resource_dir"]+"/", resource_ref))
            return fr
    log.debug("EntityResourceAccess.find_fixed_resource: %s not found"%(resource_ref))
    return None

def find_entity_resource(entity, resource_ref):
    """
    Return a description for the indicated entity resource, or None
    """
    log.debug(
        "EntityResourceAccess.find_entity_resource %s/%s/%s"%
        (entity.get_type_id(), entity.get_id(), resource_ref)
        )
    fr = find_fixed_resource(entity_fixed_json_resources, resource_ref)
    if fr:
        return fr
    for t, f in entity.enum_fields():
        # log.debug("find_resource: t %s, f %r"%(t,f))
        if isinstance(f, dict):
            if f.get("resource_name", None) == resource_ref:
                f = dict(f, resource_path=resource_ref)
                return f
    return None

def find_list_resource(type_id, list_id, list_ref):
    """
    Return a description for the indicated entity resource, or None
    """
    log.debug(
        "EntityResourceAccess.find_list_resource %s/%s/%s"%
        (list_id, type_id, list_ref)
        )
    return find_fixed_resource(entity_list_json_resources, list_ref)

# End.
