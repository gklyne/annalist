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
import logging
log = logging.getLogger(__name__)

from annalist.models.entitytypeinfo     import EntityTypeInfo, get_built_in_type_ids
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

class EntityResourceAccess(AnnalistGenericView):
    """
    View class for entity resource access

    This view class returns a data resource, not a browser form.
    """

    def __init__(self):
        super(EntityResourceAccess, self).__init__()
        return

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, resource_ref=None):
        """
        Access specified entity resource
        """
        log.info(
            "views.entityedit.get:  coll_id %s, type_id %s, entity_id %s, resource_ref %s"%
            (coll_id, type_id, entity_id, resource_ref)
            )

        viewinfo         = self.view_setup(
            action, coll_id, type_id, view_id, entity_id, request.GET.dict()
            )
        if viewinfo.http_response:
            return viewinfo.http_response

        # Load values from entity
        typeinfo     = viewinfo.entitytypeinfo
        entity       = self.get_entity(viewinfo.entity_id, typeinfo, "view")
        entity_label = (message.ENTITY_MESSAGE_LABEL%
            { 'coll_id':    viewinfo.coll_id
            , 'type_id':    viewinfo.type_id
            , 'entity_id':  viewinfo.entity_id
            })
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.ENTITY_DOES_NOT_EXIST%{'id': entity_label}
                    )
                )
        # Locate resource
        resource_info = self.find_resource(viewinfo, entity, resource_ref)
        if resource_info is None:
            return self.error(
                dict(self.error404values(),
                    message=message.RESOURCE_NOT_DEFINED%
                        { 'id':  entity_label
                        , 'ref': resource_ref
                        }
                    )
                )
        resource_file = self.access_resource(viewinfo, resource_info)
        if resource_file is None:
            return self.error(
                dict(self.error404values(),
                    message=message.RESOURCE_DOES_NOT_EXIST%
                        { 'id':  entity_label
                        , 'ref': resource_ref
                        }
                    )
                )
        # Return resource
        try:
            response = self.resource_response(resource_info, resource_file)
        except Exception as e:
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        return response

    def view_setup(self, coll_id, type_id, entity_id, request_dict):
        """
        Assemble display information for entity view request handler
        """
        action                        = "view"
        # self.site_view_url            = self.view_uri("AnnalistSiteView")
        # self.collection_view_url      = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        self.default_continuation_url = None
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.get_entity_info(action, entity_id)
        # viewinfo.get_entity_data()
        viewinfo.check_authorization(action)
        return viewinfo

# End.
