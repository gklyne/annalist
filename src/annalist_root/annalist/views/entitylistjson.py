"""
Entity list JSON view
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

from annalist                           import layout
from annalist.identifiers               import RDFS, ANNAL
from annalist.util                      import make_type_entity_id

from annalist.models.entityfinder       import EntityFinder

from annalist.views.entitylist          import EntityGenericListView

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityGenericListJsonView(EntityGenericListView):
    """
    View class for generic entity list returned as JSON-LD
    """

    def __init__(self):
        super(EntityGenericListJsonView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Return a list of entities as a JSON-LD object

        NOTE: The current implementation returns a full copy of each of the 
        selected entities.
        """
        scope      = request.GET.get('scope',  None)
        search_for = request.GET.get('search', "")
        log.info(
            "views.entitylistjson.get: coll_id %s, type_id %s, list_id %s, scope %s, search %s"%
            (coll_id, type_id, list_id, scope, search_for)
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
        # @@TODO: use render_json here; generalize module to support different formats
        return_type = "application/ld+json"
        if "type" in listinfo.request_dict:
            return_type = listinfo.request_dict["type"]
        response = HttpResponse(
            json.dumps(jsondata, indent=2, separators=(',', ': '), sort_keys=True),
            content_type=return_type
            )
        response = self.add_link_header(response, [{"rel": "canonical", "ref": jsondata['@id']}] )
        return response

# End.
