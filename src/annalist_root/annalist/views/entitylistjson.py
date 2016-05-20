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

    # Helper function returns selected values from entity data

    def strip_context_values(self, entity, base_url):
        """
        Return selected values from entity data
        """
        entityvals = entity.get_values()
        entityvals.pop('@context', None)
        entityref = make_type_entity_id(
            entityvals[ANNAL.CURIE.type_id], entityvals[ANNAL.CURIE.id]
            )
        entityvals['@id'] = base_url+entityref+"/"
        return entityvals

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        """
        Return a list of entities as a JSON-LD object

        NOTE: The current implementation returns a full copy of each of the 
        selected entities.  If this proves too much, a future implementation 
        may want to consider ways of pruning the result.
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
        base_url = self.get_collection_base_url()
        # log.debug("@@ listinfo.list_id %s, coll base_url %s"%(listinfo.list_id, base_url))
        # Prepare list and entity IDs for rendering form
        try:
            selector    = listinfo.recordlist.get_values().get(ANNAL.CURIE.list_entity_selector, "")
            user_perms  = self.get_permissions(listinfo.collection)
            entity_list = (
                EntityFinder(listinfo.collection, selector=selector)
                    .get_entities_sorted(
                        user_perms, type_id=type_id, altscope=scope,
                        context=listinfo.recordlist, search=search_for
                        )
                )
            typeinfo      = listinfo.entitytypeinfo
            entityvallist = [ self.strip_context_values(e, base_url) for e in entity_list ]
        except Exception as e:
            log.exception(str(e))
            return self.error(
                dict(self.error500values(),
                    message=str(e)+" - see server log for details"
                    )
                )
        # Generate and return JSON data
        list_url = self.get_list_url(
            coll_id, listinfo.list_id,
            type_id=type_id,
            scope=scope,
            search=search_for
            )
        log.info(
            "EntityGenericListJsonView.get: list_url %s, base_url %s, context_url %s"%
            (list_url, base_url, base_url+layout.COLL_CONTEXT_FILE)
            )
        jsondata = (
            { '@id':            list_url
            , '@context': [
                { "@base":  base_url },
                base_url+layout.COLL_CONTEXT_FILE
                ]
            , ANNAL.CURIE.entity_list:  entityvallist
            })
        return_type = "application/ld+json"
        if "type" in listinfo.request_dict:
            return_type = listinfo.request_dict["type"]
        response = HttpResponse(
            json.dumps(jsondata, indent=2, separators=(',', ': ')),
            content_type=return_type
            )
        response = self.add_link_header(response, [{"rel": "canonical", "ref": list_url}] )
        return response

# End.
