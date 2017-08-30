"""
Collection resource access (JSON-LD context and maybe more)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import logging
log = logging.getLogger(__name__)

from django.http                        import HttpResponse

from annalist                           import message
from annalist                           import layout

import annalist.models.entitytypeinfo as entitytypeinfo
from annalist.models.entityresourceaccess import (
    collection_fixed_json_resources,
    find_fixed_resource,
    entity_resource_file,
    json_resource_file,
    turtle_resource_file, 
    make_turtle_resource_info
    )

from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

class CollectionResourceAccess(AnnalistGenericView):
    """
    View class for collection resource access

    This view class returns a collection data resource.
    """

    # NOTE: the logic of this view is modelled on `entityresource`, but currently
    #       the only resource recognized is the JSON-LD context.

    # @TODO: define common superclass with `entityresource` to share common logic.

    def __init__(self):
        super(CollectionResourceAccess, self).__init__()
        return

    # GET

    def get(self, request, 
            coll_id=None, resource_ref=None, view_id=None):
        """
        Access specified entity resource
        """
        log.debug(
            "CollectionResourceAccess.get: coll_id %s, resource_ref %s"%
            (coll_id, resource_ref)
            )
        viewinfo = self.view_setup(
            coll_id, request.GET.dict()
            )
        if viewinfo.http_response:
            return viewinfo.http_response

        coll = viewinfo.collection 
        if coll is None:
            return self.error(
                dict(self.error404values(),
                    message=message.COLLECTION_NOT_EXISTS%{'id': coll_id}
                    )
                )

        # Locate resource
        resource_info = find_fixed_resource(collection_fixed_json_resources, resource_ref)
        log.debug("CollectionResourceAccess.get: resource_info %r"%(resource_info,))
        if resource_info is None:
            return self.error(
                dict(self.error404values(),
                    message=message.COLL_RESOURCE_NOT_DEFINED%
                        { 'id':  coll_id
                        , 'ref': resource_ref
                        }
                    )
                )
        coll_baseurl = viewinfo.reqhost + self.get_collection_base_url(coll_id)
        # log.info("@@@@ coll_baseurl %s, coll_id %s, resource_ref %s"%(coll_baseurl, coll_id, resource_ref))
        if "resource_access" in resource_info:
            # Use indicated resource access renderer
            jsondata      = coll.get_values()
            resource_file = resource_info["resource_access"](coll_baseurl, jsondata, resource_info)
        else:
            # Return resource data direct from storage
            resource_file = entity_resource_file(coll, resource_info)
        # resource_file = (
        #     coll.resource_file(resource_info["resource_path"]) or
        #     viewinfo.site.resource_file(resource_info["resource_path"])
        #     )
        if resource_file is None:
            return self.error(
                dict(self.error404values(),
                    message=message.COLL_RESOURCE_NOT_EXIST%
                        { 'id':  coll_id
                        , 'ref': resource_ref
                        }
                    )
                )

        # Return resource
        try:
            response = self.resource_response(resource_file, resource_info["resource_type"])
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

    def view_setup(self, coll_id, request_dict):
        """
        Assemble display information for view request handler
        """
        action                        = "view"
        self.default_continuation_url = None
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_request_type_info(entitytypeinfo.COLL_ID)
        viewinfo.check_authorization(action)
        return viewinfo

    def resource_response(self, resource_file, resource_type):
        """
        Construct response containing body of referenced resource,
        with supplied resoure_type as its content_type
        """
        # @@TODO: assumes response can reasonably be held in memory;
        #         consider 'StreamingHttpResponse'?
        response = HttpResponse(content_type=resource_type)
        response.write(resource_file.read())
        return response

# End.
