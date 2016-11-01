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

from django.http                        import HttpResponse

from annalist                           import message
from annalist                           import layout

from annalist.models.entitytypeinfo     import EntityTypeInfo

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
        typeinfo     = viewinfo.entitytypeinfo
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
        resource_file = entity.resource_file(resource_info["resource_path"])
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
            response = self.resource_response(resource_file, return_type)
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

    def find_resource(self, viewinfo, entity, resource_ref):
        """
        Return a description for the indicated entity resource, or None
        """
        log.debug(
            "EntityResourceAccess.find_resource %s/%s/%s"%
            (entity.get_type_id(), entity.get_id(), resource_ref)
            )
        fixed_resources = (
            [ { "resource_name": layout.COLL_META_FILE,        "resource_dir": layout.COLL_BASE_DIR,     "resource_type": "application/ld+json" }
            , { "resource_name": layout.COLL_PROV_FILE,        "resource_dir": layout.COLL_BASE_DIR,     "resource_type": "application/ld+json" }
            , { "resource_name": layout.COLL_CONTEXT_FILE,     "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.TYPE_META_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.TYPE_PROV_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.LIST_META_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.LIST_PROV_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.VIEW_META_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.VIEW_PROV_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.GROUP_META_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.GROUP_PROV_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.FIELD_META_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.FIELD_PROV_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.VOCAB_META_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.VOCAB_PROV_FILE,       "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.USER_META_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.USER_PROV_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.ENUM_META_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.ENUM_PROV_FILE,        "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.TYPEDATA_META_FILE,    "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.ENTITY_DATA_FILE,      "resource_dir": ".",                      "resource_type": "application/ld+json" }
            , { "resource_name": layout.ENTITY_PROV_FILE,      "resource_dir": ".",                      "resource_type": "application/ld+json" }
            ])
        for fr in fixed_resources:
            if fr["resource_name"] == resource_ref:
                fr = dict(fr, resource_path=os.path.join(fr["resource_dir"]+"/", resource_ref))
                return fr
        for t, f in entity.enum_fields():
            # log.debug("find_resource: t %s, f %r"%(t,f))
            if isinstance(f, dict):
                if f.get("resource_name", None) == resource_ref:
                    f = dict(f, resource_path=resource_ref)
                    return f
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
