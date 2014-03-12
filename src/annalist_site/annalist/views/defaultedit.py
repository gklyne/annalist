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

from annalist                       import layout
from annalist                       import message

from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap
from annalist.fields.render_utils   import get_renderer, get_placement_class

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
        , EntityValueMap(e='annal:uri',   v='annal:uri',    c='entity_uri',       f='entity_uri'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , EntityValueMap(e=None,          v=None,           c='orig_entity_id',   f='orig_entity_id'   )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(EntityDefaultEditView, self).__init__()
        self._view_id       = "Default_view"
        self._entityclass   = None
        return

    # Support

    def get_coll_type_data(self, coll_id, type_id):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection
            self.recordtype
            self.recordtypedata
            self._entityclass

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        self.sitedata = SiteData(self.site(), layout.SITEDATA_DIR)
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(
                dict(self.error404values(), 
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        self.collection = Collection(self.site(), coll_id)
        # Check type
        if not RecordType.exists(self.collection, type_id):
            return self.error(
                dict(self.error404values(),
                    message=message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
                    )
                )
        self.recordtype     = RecordType(self.collection, type_id)
        self.recordtypedata = RecordTypeData(self.collection, type_id)
        self._entityclass   = EntityData
        return None

    def get_form_entityvaluemap(self, view_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions.
        """
        # Locate and read view description
        entitymap  = copy.copy(EntityDefaultEditView._entityvaluemap)
        entityview = RecordView.load(self.collection, view_id, altparent=self.sitedata)
        log.debug("entityview   %r"%entityview.get_values())
        # Process fields referenced by the view desription, updating value map
        for f in entityview.get_values()['annal:view_fields']:
            field_id   = f['annal:field_id']
            viewfield  = RecordField.load(self.collection, field_id, altparent=self.sitedata)
            log.debug("viewfield   %r"%(viewfield and viewfield.get_values()))
            return_property_uri = (
                viewfield['annal:property_uri'] if viewfield['annal:return_value'] 
                else None
                )
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    get_placement_class(f['annal:field_placement'])
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_render':       get_renderer(viewfield['annal:field_render'])
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_placeholder':  viewfield['annal:placeholder']
                # 'field_value':        field value to be supplied
                })
            entitymap.append(
                EntityValueMap(
                    v=viewfield['annal:property_uri'],  # Entity value used to initialize context
                    c="field_value",                    # Key for value in (sub)context
                    s=("fields", field_context),        # Field sub-context
                    f=field_id,                         # Field name in form
                    e=return_property_uri               # Entity value returned from form
                    )
                )
        # log.debug("entitymap %r"%entitymap)
        self._entityvaluemap = entitymap
        return entitymap

    # GET

    def get(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.debug("defaultedit.get: coll_id %s, type_id %s, entity_id %s, action %s"%
            (coll_id, type_id, entity_id, action)
            )
        http_response = (
            self.get_coll_type_data(coll_id, type_id) or
            self.form_edit_auth(action, self.recordtypedata._entityuri)
            )
        if http_response:
            return http_response
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, self.recordtypedata, entity_id)
        # Create local entity object or load values from existing
        entity_initial_values  = (
            { "rdfs:label":   "Record '%s' of type '%s' in collection '%s'"%(entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(action, self.recordtypedata, entity_id, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%(entity_initial_values['rdfs:label'])
                    )
                )
        # Set up initial view context
        # @@TODO: use generic context mapping logic
        # view_id     = "Default_view"
        # self.get_form_entityvaluemap()
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            orig_entity_id      = entity_id
            )
        viewcontext['fields'] = []
        # Locate and read view description
        # @@TODO: error recovery for missing vierws/fields
        view_id     = "Default_view"
        entityview   = RecordView.load(self.collection, view_id, altparent=self.sitedata)
        entityvalues = entity.get_values()
        log.debug("entityvalues %r"%entityvalues)
        log.debug("entityview   %r"%entityview.get_values())
        # Process fields referenced by the view desription, updating value map and
        for f in entityview.get_values()['annal:view_fields']:
            field_id   = f['annal:field_id']             
            viewfield  = RecordField.load(self.collection, field_id, altparent=self.sitedata)
            log.debug("viewfield   %r"%(viewfield and viewfield.get_values()))
            fieldvalue = entityvalues[viewfield['annal:property_uri']]
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    get_placement_class(f['annal:field_placement'])
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_render':       get_renderer(viewfield['annal:field_render'])
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_placeholder':  viewfield['annal:placeholder']
                , 'field_property_uri': viewfield['annal:property_uri']
                , 'field_value':        fieldvalue
                })
            viewcontext['fields'].append(field_context)
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
        """
        Handle response from dynamically generatred entity editing form.
        """
        log.debug("views.defaultedit.post %s"%(self.get_request_path()))
        # log.debug("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.debug("  form data %r"%(request.POST))
        http_response = (
            self.get_coll_type_data(coll_id, type_id) or
            self.form_edit_auth(action, self.recordtypedata._entityuri)
            )
        if http_response:
            return http_response
        # Get key POST values
        entity_id            = request.POST.get('Entity_id', None)
        orig_entity_id       = request.POST.get('orig_entity_id', None)
        continuation_uri     = request.POST.get('continuation_uri', 
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'continuation_uri': continuation_uri
            })
        messages = (
            { 'parent_heading':    message.RECORD_TYPE_ID
            , 'parent_missing':    message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
            , 'entity_heading':    message.ENTITY_DATA_ID
            , 'entity_invalid_id': message.ENTITY_DATA_ID_INVALID
            , 'entity_exists':     message.ENTITY_DATA_EXISTS%(entity_id, type_id, coll_id)
            , 'entity_not_exists': message.ENTITY_DATA_NOT_EXISTS%(entity_id, type_id, coll_id)
            })
        # Process form response and respond accordingly
        self.get_form_entityvaluemap(self._view_id)
        return self.form_response(
            request, action, self.recordtypedata, entity_id, orig_entity_id, 
            messages, context_extra_values
            )


class EntityDataDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed entity data deletion,
    anticipated to be requested from a data list or record view.
    """
    def __init__(self):
        super(EntityDataDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id, type_id):
        """
        Process options to complete action to remove an entity data record.
        """
        log.debug("EntityDataDeleteConfirmedView.post: %r"%(request.POST))
        if "entity_delete" in request.POST:
            entity_id  = request.POST['entity_id']
            coll       = self.collection(coll_id)
            recordtype = self.recordtype(coll_id, type_id)
            recorddata = self.recordtypedata(coll_id, type_id)
            messages  = (
                { 'entity_removed': message.ENTITY_DATA_REMOVED%(entity_id, type_id, coll_id)
                })
            continuation_uri = (
                request.POST.get('continuation_uri', None) or
                self.view_uri("AnnalistEntityDefaultListType", coll_id=coll_id, type_id=type_id)
                )
            return self.confirm_form_respose(
                request, recorddata, entity_id, recorddata.remove_entity, 
                messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
