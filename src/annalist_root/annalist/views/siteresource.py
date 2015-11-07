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

from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

class SiteResourceAccess(AnnalistGenericView):
    """
    View class for site resource access

    This view class returns a site data resource.
    """

    # NOTE: the logic of this view is modelled on `entityresource`, but currently
    #       the only resource recognized is the JSON-LD context.

    # @TODO: define common superclass with `entityresource` to share common logic.

    def __init__(self):
        super(SiteResourceAccess, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, resource_ref=None, view_id=None):
        """
        Access specified entity resource
        """
        log.info("SiteResourceAccess.get: resource_ref %s"%(resource_ref,))
        viewinfo = self.view_setup(request.GET.dict())
        if viewinfo.http_response:
            return viewinfo.http_response

        # Locate resource
        resource_info = self.find_resource(viewinfo, resource_ref)
        if resource_info is None:
            return self.error(
                dict(self.error404values(),
                    message=message.SITE_RESOURCE_NOT_DEFINED%
                        { 'ref': resource_ref
                        }
                    )
                )
        resource_file = viewinfo.site.resource_file(resource_info["resource_name"])
        if resource_file is None:
            return self.error(
                dict(self.error404values(),
                    message=message.SITE_RESOURCE_NOT_EXIST%
                        { 'ref': resource_ref
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

    def view_setup(self, request_dict):
        """
        Assemble display information for view request handler
        """
        action                        = "view"
        self.default_continuation_url = None
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.check_authorization(action)
        return viewinfo

    def find_resource(self, viewinfo, resource_ref):
        """
        Return a description for the indicated site resource, or None
        """
        #@@TODO: still needed?
        log.info("SiteResourceAccess.find_resource %s"%(resource_ref))
        if resource_ref == layout.COLL_CONTEXT_FILE:
            return (
                { 'resource_type': "application/ld+json"
                , 'resource_name': resource_ref
                })
        return None

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
