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
# from annalist.collection            import Collection
# from annalist.recordtype            import RecordType

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap


class EntityDefaultListView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can be generated dynamically per-instance...

    _entityformtemplate = 'annalist_default_list.html'

    _entityclass        = None          # to be supplied dynamically
    _entityvaluemap     = (             # to be supplied dynamically, but looking something like this...
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='entity_id',        f='entity_id'        )
        # Normal fields
        , EntityValueMap(e=None,          v='annal:type',   c=None,               f=None               )
        , EntityValueMap(e='rdfs:label',  v='rdfs:label',   c='entity_label',     f='entity_label'     )
        , EntityValueMap(e='rdfs:comment',v='rdfs:comment', c='entity_comment',   f='entity_comment'   )
        # Form and interaction control
        , EntityValueMap(e=None,          v=None,           c='orig_entity_id',   f='orig_entity_id'   )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(EntityDefaultListView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message=message.COLLECTION_NOT_EXISTS%(coll_id)))
        coll = Collection(self.site(), coll_id)
        # Check type
        if not RecordType.exists(coll, type_id):
            return self.error(self.error404values().update(
                message=message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)))
        recordtype = RecordType(coll, type_id)
        entitydata = EntityData(coll, type_id)

        # locate form description
        list_id    = "Default_list"
        entitylist = EntityList(coll, list_id)

        # load form description
        # load values for form
        # generate form data

        # initial_type_values  = (
        #     { "annal:id":     type_id
        #     , "annal:type":   "annal:RecordType"
        #     , "annal:uri":    coll._entityuri+type_id+"/"
        #     , "rdfs:label":   "Record type %s in collection %s"%(type_id, coll_id)
        #     , "rdfs:comment": ""
        #     })
        # context_extra_values = (
        #     { 'coll_id':          coll_id
        #     , 'orig_type_id':     type_id
        #     })
        return self.form_render(request,
            action, coll, type_id, 
            initial_type_values, 
            context_extra_values
            )

# End.
