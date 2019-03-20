"""
Entity resource access (imported and uploaded files).

This module contains functions to help access resource data that is 
attached to an entity (or collection).

It contains logic for accessing raw JSON-LD data, or accessing that data converted to 
some other format (e.g. Turtle).
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import os
import json

from rdflib                             import Graph, URIRef, Literal

# Used by `json_resource_file` below.
# See: https://stackoverflow.com/questions/51981089
from utils.py3porting import BytesIO, StringIO, write_bytes

from annalist                           import message
from annalist                           import layout

from annalist.models.entitytypeinfo     import EntityTypeInfo

# Resource info data for built-in entity data

site_fixed_json_resources = (
    [ { "resource_name": layout.SITE_META_FILE,     "resource_dir": layout.SITE_META_REF, 
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.SITE_CONTEXT_FILE,  "resource_dir": layout.SITE_META_REF, 
                                                    "resource_type": "application/ld+json" }
    ])

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
    , { "resource_name": layout.INFO_META_FILE,     "resource_dir": ".",
                                                    "resource_type": "application/ld+json" }
    , { "resource_name": layout.INFO_PROV_FILE,     "resource_dir": ".",
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

    baseurl         base URL for resolving relative URI references.
                    (Unused except for diagnostic purposes.)
    jsondata        is the data to be formatted and returned.
    resource_info   is a dictionary of values about the resource to be serialized.
                    (Unused except for diagnostic purposes.)
    """
    response_file = StringIO()
    json.dump(jsondata, response_file, indent=2, separators=(',', ': '), sort_keys=True)
    response_file.seek(0)
    return response_file

def turtle_resource_file(baseurl, jsondata, resource_info):
    """
    Return a file object that reads out a Turtle version of the supplied 
    entity values data.  The file object returns a byte stream, as this is
    what rdflib expects.

    baseurl         base URL for resolving relative URI references.
                    (Unused except for diagnostic purposes.)
    jsondata        is the data to be formatted and returned.
    resource_info   is a dictionary of values about the resource to be serialized.
                    (Unused except for diagnostic purposes.)
    """
    # NOTE:   under Python 2, "BytesIO" is implemented by "StringIO", which does
    #         not handle well a combination of str and unicode values, and may 
    #         raise an exception if the Turtle data contains non-ASCII characters.
    #         The problem manifests when an error occurs, and manifests as a 500 
    #         server error response.
    #
    #         On reflection, I think the prioblem arises because the `message.*`
    #         values are unicode (per `from __future__ import unicode_literals`),
    #         and are getting joined with UTF-encoded bytestring values, which
    #         results in the error noted.
    #
    #         The fix here is to encode everything as bytes before writing.
    jsondata_file = json_resource_file(baseurl, jsondata, resource_info)
    response_file = BytesIO()
    g = Graph()
    try:
        g = g.parse(source=jsondata_file, publicID=baseurl, format="json-ld")
    except Exception as e:
        reason = str(e)
        log.warning(message.JSONLD_PARSE_ERROR)
        log.info(reason)
        log.info("baseurl %s, resourceinfo %r"%(baseurl, resource_info))
        write_bytes(response_file, "\n\n***** ERROR ****\n")
        write_bytes(response_file, "%s"%message.JSONLD_PARSE_ERROR)
        write_bytes(response_file, "\n%s:\n"%message.JSONLD_PARSE_REASON)
        write_bytes(response_file, reason)
        write_bytes(response_file, "\n\n")
    try:
        g.serialize(destination=response_file, format='turtle', indent=4)
    except Exception as e:
        reason = str(e)
        log.warning(message.TURTLE_SERIALIZE_ERROR)
        log.info(reason)
        write_bytes(response_file, "\n\n***** ERROR ****\n")
        write_bytes(response_file, "%s"%message.TURTLE_SERIALIZE_ERROR)
        write_bytes(response_file, "\n%s:\n"%message.TURTLE_SERIALIZE_REASON)
        write_bytes(response_file, reason)
        write_bytes(response_file, "\n\n")
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
    Return a description for the indicated fixed (built-in) resource from 
    a supplied table, or None

    resource_ref    is the local name of the desired resource relative to the base
                    location of the entity (or collection or site data) to which it belongs.

    The description returned is a dictionary with the following keys:
        resource_name:      filename of resource (i.e. part of URI path after final "/")
        resource_dir:       directory of resource (i.e. part of URI path up to final "/")
        resource_path:      a file or URI path to the resource data relative to the
                            URI of the entity to which it belongs.
        resource_type:      content-type of resource
        resource_access:    optional: if present, specifies a function that returns an 
                            alternative representation of a JSON-LD data resource.
                            (e.g. see `turtle_resource_file`)
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

def find_entity_resource(entity, resource_ref, fixed_resources=entity_fixed_json_resources):
    """
    Return a description for the indicated entity resource, or None

    resource_ref    is the local name of the desired resource relative to the 
                    entity to which it belongs.
    fixed_resources is a table of fixed resource information, not necessarily 
                    referenced by the entity itself.

    The description returned is a dictionary with the following keys:
        resource_name:      filename of resource (i.e. part of URI path after final "/")
        resource_dir:       directory of resource (i.e. part of URI path up to final "/")
        resource_path:      a file or URI path to the resource data relative to the
                            URI of the entity to which it belongs.
        resource_type:      content-type of resource
        resource_access:    optional: if present, specifies a function that returns an 
                            alternative representation of a JSON-LD data resource.
                            (e.g. see `turtle_resource_file`)
    """
    log.debug(
        "EntityResourceAccess.find_entity_resource %s/%s/%s"%
        (entity.get_type_id(), entity.get_id(), resource_ref)
        )
    fr = find_fixed_resource(fixed_resources, resource_ref)
    if fr:
        return fr
    # Look for resource description in entity data
    # @@TESTME
    for t, f in entity.enum_fields():
        log.debug("find_resource: t %s, f %r"%(t,f))
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

def get_resource_file(entity, resource_info, base_url):
    """
    Create a file object from which resource data can be read.

    resource_info   is a value returned by `find_fixed_resource` or `find_entity_resource`
    base_url        is a base URL that may be used to resolving relative references in the
                    JSON-LD data.

    Returns a pair of values: the file object, and a content-type string.
    """
    if "resource_access" in resource_info:
        # Use indicated resource access renderer
        jsondata = entity.get_values()
        resource_file = resource_info["resource_access"](base_url, jsondata, resource_info)
    else:
        # Return resource data direct from storage
        resource_file = entity.resource_file(resource_info["resource_path"])
    return (resource_file, resource_info["resource_type"])

# End.
