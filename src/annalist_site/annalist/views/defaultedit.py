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

# from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap


class EntityDefaultEditView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can be generated dynamically per-instance...

    _entityformtemplate = 'annalist_default_edit.html'
    _entityclass        = None          # to be supplied dynamically
    _entityvaluemap     = (             # to be supplied dynamically, based on this:
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v=None,           c='type_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='entity_id',        f='entity_id'        )
        # Normal fields
        # , EntityValueMap(e=None,          v='annal:type',   c=None,               f=None               )
        # , EntityValueMap(e='rdfs:label',  v='rdfs:label',   c='entity_label',     f='entity_label'     )
        # , EntityValueMap(e='rdfs:comment',v='rdfs:comment', c='entity_comment',   f='entity_comment'   )
        # Form and interaction control (hidden fields)
        , EntityValueMap(e=None,          v=None,           c='orig_entity_id',   f='orig_entity_id'   )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(EntityDefaultEditView, self).__init__()
        self._entityclass    = None
        self._entityvaluemap = None
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
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
        recordtype     = RecordType(coll, type_id)
        recordtypedata = RecordTypeData(coll, type_id)
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, recordtypedata, entity_id)
        # Locate and read view description
        view_id    = "Default_view"
        entityview = RecordView.load(coll, view_id)
        # load values for form
        viewdata = entityview.get_values()
        valuemap = EntityDefaultEditView._entityvaluemap.copy()
        viewcontext = (
            {
            # ...
            })
        for f in viewdata['annal:view_fields']:
            # { 'annal:field_id':         "Id"
            # , 'annal:field_placement':  "small:0,12;medium:0,4"
            # }
            field_id  = f['annal:field_id']
            viewfield = RecordField(coll, field_id)
            # { '@id':                "annal:fields/Id"
            # , 'annal:id':           "Id"
            # , 'annal:type':         "annal:Field"
            # , 'rdfs:label':         "Id"
            # , 'rdfs:comment':       "..."
            # , 'annal:field_render': "annal:field_render/Slug"
            # , 'annal:value_type':   "annal:Slug"
            # , 'annal:placeholder':  "(record id)"
            # , 'annal:property_uri': "annal:id"
            # }
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    f['annal:field_placement']
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_render':       viewfield['annal:field_render']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_value':        viewfield['...']
                , 'field_placeholder':  viewfield['annal:placeholder']
                , 'field_property_uri': viewfield['annal:property_uri']
                })


        initial_entity_values  = (
            { "annal:id":     entity_id
            , "annal:type":   type_id
            , "annal:uri":    coll._entityuri+type_id+"/"+entity_id+"/"
            , "rdfs:label":   "Record type %s in collection %s"%(type_id, coll_id)
            , "rdfs:comment": ""
            })





        # generate form data

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
