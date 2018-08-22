from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Entity list data views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import json

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect

from annalist                           import message
from annalist                           import layout
from annalist.identifiers               import RDFS, ANNAL
from annalist.util                      import make_type_entity_id

from annalist.models.entityfinder       import EntityFinder
from annalist.models.entityresourceaccess import (
    find_list_resource,
    json_resource_file
    )

from annalist.views.entitylist          import EntityGenericListView

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityListDataView(EntityGenericListView):
    """
    View class for generic entity list returned as JSON-LD
    """

    def __init__(self):
        super(EntityListDataView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None, list_ref=None):
        """
        Return a list of entities as a JSON-LD object

        NOTE: The current implementation returns a full copy of each of the 
        selected entities.
        """
        scope      = request.GET.get('scope',  None)
        search_for = request.GET.get('search', "")
        log.info(
            "views.entitylistdata.get: coll_id %s, type_id %s, list_id %s, list_ref %s, scope %s, search %s"%
            (coll_id, type_id, list_id, list_ref, scope, search_for)
            )
        listinfo    = self.list_setup(coll_id, type_id, list_id, request.GET.dict())
        if listinfo.http_response:
            return listinfo.http_response
        # print "@@@@ listinfo.type_id %s, type_id %s"%(listinfo.type_id, type_id)
        # log.debug("@@ listinfo.list_id %s, coll base_url %s"%(listinfo.list_id, base_url))
        # Prepare list data for rendering
        try:
            jsondata = self.assemble_list_data(listinfo, scope, search_for)
        except Exception as e:
            log.exception(str(e))
            return self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        entity_list_info = find_list_resource(type_id, list_id, list_ref)
        if entity_list_info is None:
            return self.error(
                dict(self.error404values(),
                    message=message.LIST_NOT_DEFINED%
                        { 'list_id':  list_id
                        , 'type_id':  type_id
                        , 'list_ref': list_ref
                        }
                    )
                )

        coll_baseurl = listinfo.reqhost + self.get_collection_base_url(coll_id)
        list_baseurl = listinfo.reqhost + self.get_list_base_url(coll_id, type_id, list_id)
        if "resource_access" in entity_list_info:
            # Use indicated resource access renderer
            list_file_access = entity_list_info["resource_access"]
        else:
            list_file_access = json_resource_file
        list_file = list_file_access(list_baseurl, jsondata, entity_list_info)
        if list_file is None:
            return self.error(
                dict(self.error404values(),
                    message=message.LIST_NOT_ACCESSED%
                        { 'list_id':  list_id
                        , 'type_id':  type_id
                        , 'list_ref': list_ref
                        }
                    )
                )

        # Construct and return list response
        try:
            return_type = entity_list_info["resource_type"]
            # URL parameter ?type=mime/type overrides specified content type
            #
            # @@TODO: this is to allow links to return different content-types:
            #         is there a cleaner way?
            if "type" in listinfo.request_dict:
                return_type = listinfo.request_dict["type"]
            links=[
                { "rel": "canonical"
                , "ref": list_baseurl
                }]
            response = self.resource_response(list_file, return_type, links=links)
        except Exception as e:
            log.exception(str(e))
            response = self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        finally:
            list_file.close()

        return response

# End.
