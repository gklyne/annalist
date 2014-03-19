"""
Default record view/edit
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message
# from annalist.exceptions            import Annalist_Error
# from annalist.identifiers           import RDF, RDFS, ANNAL
# from annalist                       import util

# from annalist.site                  import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView


class EntityDefaultListView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can be generated dynamically per-instance...

    _entityformtemplate = 'annalist_entity_list.html'
    _entityclass        = None          # to be supplied dynamically

    def __init__(self):
        super(EntityDefaultListView, self).__init__()
        self._list_id       = "Default_list"
        self._entityclass   = None
        return

    # GET

    def get(self, request, coll_id=None, type_id=None):
        """
        Create a form for listing entities.
        """
        log.debug("defaultedit.get: coll_id %s, type_id %s"%(coll_id, type_id))
        if type_id:
            http_response = self.get_coll_type_data(coll_id, type_id, host=self.get_request_host())
        else:
            http_response = self.get_coll_data(coll_id, host=self.get_request_host())
        if not http_response:
            http_response = self.form_edit_auth("list", self.recordtypedata._entityuri)
        if http_response:
            return http_response
        # Prepare context for rendering form
        list_ids      = [ l.get_id() for l in self.collection.lists() ]
        list_selected = self.collection.get_values().get("default_list", "Default_list")
        # @@TODO: apply selector logic here?
        entity_list   = self.recordtypedata.entities()
        entityval = { 'annal:list_entities': entity_list }
        # Set up initial view context
        self._entityvaluemap = self.get_list_entityvaluemap(self._list_id)
        viewcontext = self.map_value_to_context(entityval,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            ### heading             = entity_initial_values['rdfs:label'],
            coll_id             = coll_id,
            type_id             = type_id
            )
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

# End.
