"""
Default record view/edit
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import copy

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
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap


class EntityDefaultEditView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can also be generated dynamically per-instance...
    _entityformtemplate = 'annalist_entity_edit.html'
    _entityclass        = None          # to be supplied dynamically
    _entityvaluemap     = (             # to be supplied dynamically, based on this:
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v=None,           c='type_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='entity_id',        f='entity_id'        )
        # Normal record fields
        # -- these are filled in from the entity view description used
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
        self._entityclass = EntityData
        # Sort access mode and authorization
        auth_required = self.form_edit_auth(action, recordtypedata._entityuri)
        if auth_required:
            return auth_required
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, recordtypedata, entity_id)
        # Create local entity object or load values from existing
        entity_initial_values  = (
            { "annal:id":     entity_id
            , "annal:type":   type_id
            , "annal:uri":    coll._entityuri+type_id+"/"+entity_id+"/"
            , "rdfs:label":   "Record '%s' of type '%s' in collection '%s'"%(entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(action, recordtypedata, entity_id, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(), 
                    message=message.DOES_NOT_EXIST%(entity_initial_values['rdfs:label'])
                    )
                )
        # Set up initial value map and view context
        self._entityvaluemap    = copy.copy(EntityDefaultEditView._entityvaluemap)
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            orig_entity_id      = entity_id
            )
        # Locate and read view description
        view_id    = "Default_view"
        entityview = RecordView.load(coll, view_id)
        # Process view desription, updating value map and
        for f in entityview.get_values()['annal:view_fields']:
            field_id   = f['annal:field_id']
            viewfield  = RecordField(coll, field_id)
            fieldvalue = entity.get_values()[viewfield['annal:property_uri']]
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    f['annal:field_placement']
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_render':       get_renderer(viewfield['annal:field_render'])
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_value':        fieldvalue
                , 'field_placeholder':  viewfield['annal:placeholder']
                , 'field_property_uri': viewfield['annal:property_uri']
                })


        # generate form data

        # ------------------------------------------------------



        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )


# End.
