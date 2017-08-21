"""
Entity resource access (imported and uploaded files)

Resources are associated with a field, and are located via the entity data.
Resource URLs are based on the entity URL and a resource name that is defined
by an entity field.  The MIME content type is obtained from the same entity
field.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import json
import StringIO
import logging
log = logging.getLogger(__name__)

# from rdflib                             import Graph, URIRef, Literal

from django.http                        import HttpResponse

from annalist                           import message
from annalist                           import layout

# from annalist.models.entitytypeinfo     import EntityTypeInfo

from annalist.models.entityresourceaccess import (
    find_entity_resource,
    entity_resource_file,
    json_resource_file,
    turtle_resource_file, 
    make_turtle_resource_info
    )

from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

# Resource info data for built-in entity data

# fixed_json_resources = (
#     [ { "resource_name": layout.COLL_META_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
#                                                     "resource_type": "application/ld+json" }
#     , { "resource_name": layout.COLL_PROV_FILE,     "resource_dir": layout.COLL_BASE_DIR, 
#                                                     "resource_type": "application/ld+json" }
#     , { "resource_name": layout.COLL_CONTEXT_FILE,  "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.TYPE_META_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.TYPE_PROV_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.LIST_META_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.LIST_PROV_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.VIEW_META_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.VIEW_PROV_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.GROUP_META_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.GROUP_PROV_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.FIELD_META_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.FIELD_PROV_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.VOCAB_META_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.VOCAB_PROV_FILE,    "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.USER_META_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.USER_PROV_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.ENUM_META_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.ENUM_PROV_FILE,     "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.TYPEDATA_META_FILE, "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.ENTITY_DATA_FILE,   "resource_dir": ".", "resource_type": "application/ld+json" }
#     , { "resource_name": layout.ENTITY_PROV_FILE,   "resource_dir": ".", "resource_type": "application/ld+json" }
#     ])

# # Helpter functions

# def entity_resource_file(entity, resource_info):
#     """
#     Return a file object that reads out the content of a resource attached to a specified entity.
#     """
#     return entity.resource_file(resource_info["resource_path"])

# def json_resource_file(baseurl, jsondata, resource_info):
#     """
#     Return a file object that reads out a JSON version of the supplied entity values data. 
#     """
#     response_file = StringIO.StringIO()
#     json.dump(jsondata, response_file, indent=2, separators=(',', ': '), sort_keys=True)
#     response_file.seek(0)
#     return response_file

# def turtle_resource_file(baseurl, jsondata, resource_info):
#     """
#     Return a file object that reads out a Turtle version of the supplied entity values data. 

#     baseurl     base URL for resolving relative URI references for Turtle output.
#     jsondata    is the data to be formatted and returned.
#     links       is an optional array of link values to be added to the HTTP response
#                 (see method add_link_header for description).
#     """
#     # log.debug("@@ turtle_resource_file - data: %r"%(jsondata))
#     # log.info("@@ baseurl %s"%(baseurl,))
#     jsondata_file = json_resource_file(baseurl, jsondata, resource_info)
#     response_file = StringIO.StringIO()
#     g = Graph()
#     g = g.parse(source=jsondata_file, publicID=baseurl, format="json-ld")
#     g.serialize(destination=response_file, format='turtle', indent=4)
#     response_file.seek(0)
#     return response_file

#         # # Read entity data as JSON-LD
#         # g = Graph()
#         # s = entity1._read_stream()
#         # b = ( "file://" + 
#         #       os.path.join(
#         #         TestBaseDir, 
#         #         layout.SITE_ENTITY_PATH%
#         #           { 'coll_id': self.testcoll.get_id()
#         #           , 'type_id': testdata.get_id()
#         #           , 'id':      entity1.get_id()
#         #           }
#         #         )
#         #     )
#         # # print "***** b: "+repr(b)
#         # # print "***** s: "+s.read()
#         # # s.seek(0)
#         # result = g.parse(source=s, publicID=b+"/", format="json-ld")
#         # # print "*****"+repr(result)
#         # # print("***** g: (entity1)")
#         # # print(g.serialize(format='turtle', indent=4))

# def make_turtle_resource_info(json_resource):
#     """
#     Return Turtle resource description for fixed JSON resource
#     """
#     turtle_resource = (
#         { "resource_name":      json_resource["resource_name"][0:-7]+".ttl"
#         , "resource_dir":       json_resource["resource_dir"]
#         , "resource_type":      "text/turtle"
#         , "resource_access":    turtle_resource_file
#         })
#     return turtle_resource

# Entity resource access view

class EntityResourceAccess(AnnalistGenericView):
    """
    View class for entity resource access

    This view class returns a data resource, not a browser form, which may be based on the
    entity data itself (from the internally stored JSON), or the content of an attached
    data resource (e.g. image, audio, etc.)

    This view may be used as thye target of content negotiation redirects, and no
    further content negotiation is attempted.  Rather, the URI is expected to reference 
    the form of the resource to be returned (cf. 'find_resource' function).  This allows links
    to specific resource formats to be obtained for use by clients that don't have access to
    set HTTP content negotiation headers.
    """

    def __init__(self):
        super(EntityResourceAccess, self).__init__()
        return

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, resource_ref=None, view_id=None):
        """
        Access specified entity resource
        """
        log.info(
            "get: coll_id %s, type_id %s, entity_id %s, resource_ref %s"%
            (coll_id, type_id, entity_id, resource_ref)
            )
        viewinfo = self.view_setup(
            coll_id, type_id, entity_id, request.GET.dict()
            )
        if viewinfo.http_response:
            return viewinfo.http_response

        # Load values from entity
        typeinfo     = viewinfo.curr_typeinfo
        entity       = self.get_entity(viewinfo.src_entity_id, typeinfo, "view")
        entity_label = (message.ENTITY_MESSAGE_LABEL%
            { 'coll_id':    viewinfo.coll_id
            , 'type_id':    viewinfo.type_id
            , 'entity_id':  viewinfo.src_entity_id
            })
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.ENTITY_DOES_NOT_EXIST%{'id': entity_label}
                    )
                )
        # Locate and open resource file
        resource_info = find_entity_resource(entity, resource_ref)
        if resource_info is None:
            return self.error(
                dict(self.error404values(),
                    message=message.RESOURCE_NOT_DEFINED%
                        { 'id':  entity_label
                        , 'ref': resource_ref
                        }
                    )
                )
        entity_baseurl = viewinfo.reqhost + self.get_entity_base_url(coll_id, type_id, entity_id)
        if "resource_access" in resource_info:
            # Use indicated resource access renderer
            jsondata = entity.get_values()
            resource_file = resource_info["resource_access"](entity_baseurl, jsondata, resource_info)
        else:
            # Return resource data direct from storage
            resource_file = entity_resource_file(entity, resource_info)
        if resource_file is None:
            return self.error(
                dict(self.error404values(),
                    message=message.RESOURCE_DOES_NOT_EXIST%
                        { 'id':  entity_label
                        , 'ref': resource_info["resource_path"]
                        }
                    )
                )
        # Return resource
        try:
            return_type = resource_info["resource_type"]
            # URL parameter ?type=mime/type overrides specified content type
            #
            # @@TODO: this is to allow links to return different content-types:
            #         is there a cleaner way?
            if "type" in viewinfo.request_dict:
                return_type = viewinfo.request_dict["type"]
            links=[
                { "rel": "canonical"
                , "ref": entity_baseurl
                }]
            response = self.resource_response(resource_file, return_type, links=links)
        except Exception as e:
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        finally:
            resource_file.close()
        return response

    def view_setup(self, coll_id, type_id, entity_id, request_dict):
        """
        Assemble display information for entity view request handler
        """
        action                        = "view"
        #@@ self.site_view_url            = self.view_uri("AnnalistSiteView")
        #@@ self.collection_view_url      = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        self.default_continuation_url = None
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.get_entity_info(action, entity_id)
        # viewinfo.get_entity_data()
        viewinfo.check_authorization(action)
        return viewinfo

    # def find_resource(self, entity, resource_ref):
    #     """
    #     Return a description for the indicated entity resource, or None
    #     """
    #     log.debug(
    #         "EntityResourceAccess.find_resource %s/%s/%s"%
    #         (entity.get_type_id(), entity.get_id(), resource_ref)
    #         )
    #     for fj in fixed_json_resources:
    #         if fj["resource_name"] == resource_ref:
    #             fr = dict(fj, resource_path=os.path.join(fj["resource_dir"]+"/", resource_ref))
    #             return fr
    #         ft = make_turtle_resource_info(fj)
    #         if ft["resource_name"] == resource_ref:
    #             fr = dict(ft, resource_path=os.path.join(ft["resource_dir"]+"/", resource_ref))
    #             return fr
    #     for t, f in entity.enum_fields():
    #         # log.debug("find_resource: t %s, f %r"%(t,f))
    #         if isinstance(f, dict):
    #             if f.get("resource_name", None) == resource_ref:
    #                 f = dict(f, resource_path=resource_ref)
    #                 return f
    #     return None

    def resource_response(self, resource_file, resource_type, links={}):
        """
        Construct response containing body of referenced resource,
        with supplied resource_type as its content_type
        """
        # @@TODO: assumes response can reasonably be held in memory;
        #         consider 'StreamingHttpResponse'?
        response = HttpResponse(content_type=resource_type)
        response = self.add_link_header(response, links)
        response.write(resource_file.read())
        return response

# End.
