"""
Entity resource access (imported and uploaded files)

Resources are associated with a field, and are located via the entity data.
Resource URLs are based on the entity URL and a resource name that is defined
by an entity field.  The MIME content type is obtained from the same entity
field.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import os
import json

# from rdflib                             import Graph, URIRef, Literal

from django.http                        import HttpResponse

from annalist                           import message
from annalist                           import layout

from annalist.models.entityresourceaccess import (
    find_entity_resource,
    # entity_resource_file,
    # json_resource_file,
    # turtle_resource_file, 
    # make_turtle_resource_info,
    get_resource_file
    )

from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

class EntityResourceAccess(AnnalistGenericView):
    """
    View class for entity resource access

    This view class returns a data resource, not a browser form, which may be based on 
    the entity data itself (from the internally stored JSON), or the content of an 
    attached data resource (e.g. image, audio, etc.)

    This view may be used as the target of content negotiation redirects, and no
    further content negotiation is attempted.  Rather, the URI is expected to reference 
    the form of the resource to be returned (cf. 'find_entity_resource' function).  
    This allows links to specific resource formats to be obtained for use by clients 
    that don't have access to set HTTP content negotiation headers.
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
                    message=message.ENTITY_DOES_NOT_EXIST%
                        { 'type_id': viewinfo.type_id
                        , 'id':      viewinfo.src_entity_id
                        , 'label':   entity_label
                        }
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
        resource_file, resource_type = get_resource_file(entity, resource_info, entity_baseurl)
        if resource_file is None:
            msg = (message.RESOURCE_DOES_NOT_EXIST%
                { 'id':  entity_label
                , 'ref': resource_info["resource_path"]
                })
            log.debug("EntityResourceAccess.get: "+msg)
            return self.error(dict(self.error404values(), message=msg))
        # Return resource
        try:
            return_type = resource_type
            # URL parameter ?type=mime/type overrides specified content type
            #
            # @@TODO: this is to allow links to return different content-types
            #         (e.g., JSON as text/plain so it is displayed in the browser):
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
        self.default_continuation_url = None
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_request_type_info(type_id)
        viewinfo.get_entity_info(action, entity_id)
        # viewinfo.get_entity_data()
        viewinfo.check_authorization(action)
        return viewinfo

# End.
