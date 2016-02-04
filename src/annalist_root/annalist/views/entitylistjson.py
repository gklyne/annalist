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
# from django.core.urlresolvers           import resolve, reverse

from annalist                           import layout
# from annalist                           import message
# from annalist.exceptions                import Annalist_Error
from annalist.identifiers               import RDFS, ANNAL
from annalist.util                      import make_type_entity_id

# import annalist.models.entitytypeinfo as entitytypeinfo
# from annalist.models.collection         import Collection
# from annalist.models.recordtype         import RecordType
# from annalist.models.recordtypedata     import RecordTypeData
# from annalist.models.entitytypeinfo     import EntityTypeInfo, CONFIG_PERMISSIONS
from annalist.models.entityfinder       import EntityFinder

# from annalist.views.uri_builder         import uri_with_params
# from annalist.views.displayinfo         import DisplayInfo
# from annalist.views.confirm             import ConfirmView, dict_querydict
# from annalist.views.generic             import AnnalistGenericView
from annalist.views.entitylist            import EntityGenericListView

# from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field
# from annalist.views.entityvaluemap      import EntityValueMap
# from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
# from annalist.views.fieldlistvaluemap   import FieldListValueMap
# from annalist.views.fieldvaluemap       import FieldValueMap
# from annalist.views.repeatvaluesmap     import RepeatValuesMap

# from annalist.views.fields.bound_field  import bound_field, get_entity_values

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
        # log.debug("listinfo.list_id %s"%listinfo.list_id)
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
        #@@ NOTE: temporary code with absolute URIs until newer JSON-LD parser is released
        jsondata = (
            { '@id':            list_url
            , '@context': [
                { "@base":  request.build_absolute_uri(base_url) },
                base_url+layout.COLL_CONTEXT_FILE
                ]
            # , ANNAL.CURIE.type_id:      "_list"
            , ANNAL.CURIE.entity_list:  entityvallist
            })
        response = HttpResponse(
            json.dumps(jsondata, indent=2, separators=(',', ': ')),
            content_type="application/ld+json"
            )
        response = self.add_link_header(response, [{"rel": "canonical", "ref": list_url}] )
        return response

# End.
