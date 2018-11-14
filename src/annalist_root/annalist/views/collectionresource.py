from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

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
    find_entity_resource,
    get_resource_file
    )

from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

class CollectionResourceAccess(AnnalistGenericView):
    """
    View class for collection resource access

    This view class returns a collection data resource.
    """

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
        resource_info = find_entity_resource(
            viewinfo.site, resource_ref, fixed_resources=collection_fixed_json_resources
            )
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
        resource_file, resource_type = get_resource_file(
            coll, resource_info, coll_baseurl
            )
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

# End.
