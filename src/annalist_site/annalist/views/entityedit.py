"""
Generic entity edit view
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

from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.displayinfo     import DisplayInfo
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
# from annalist.views.fieldlistvaluemap   import FieldListValueMap
# from annalist.views.grouprepeatmap      import GroupRepeatMap

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='title',            e=None,                  f=None               )
        , SimpleValueMap(c='coll_id',          e=None,                  f=None               )
        , SimpleValueMap(c='type_id',          e=None,                  f=None               )
        , StableValueMap(c='entity_id',        e='annal:id',            f='entity_id'        )
        , SimpleValueMap(c='entity_uri',       e='annal:uri',           f='entity_uri'       )
        , SimpleValueMap(c='record_type',      e='annal:record_type',   f='record_type'      )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='view_id',          e=None,                  f='view_id'          )
        , SimpleValueMap(c='orig_id',          e=None,                  f='orig_id'          )
        , SimpleValueMap(c='orig_type',        e=None,                  f='orig_type'        )
        , SimpleValueMap(c='action',           e=None,                  f='action'           )
        , SimpleValueMap(c='continuation_uri', e=None,                  f='continuation_uri' )
        ])

#   -------------------------------------------------------------------------------------------
#
#   Entity edit view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class GenericEntityEditView(EntityEditBaseView):
    """
    View class for generic entity edit view

    The view to be displayted can be specified through the constructor
    (for predefined views) or through the HTTP request URTI parameters
    (for any view).
    """

    _entityformtemplate = 'annalist_entity_edit.html'

    def __init__(self):
        super(GenericEntityEditView, self).__init__()
        return

    # Helper functions

    def view_setup(self, action, coll_id, type_id, view_id, entity_id):
        """
        Assemble display information for entity view request handler
        """
        viewinfo = DisplayInfo(self)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.get_view_info(viewinfo.get_view_id(type_id, view_id))
        viewinfo.get_entity_info(action, entity_id)
        viewinfo.check_authorization(action)
        return viewinfo

    def get_view_entityvaluemap(self, viewinfo):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated view.
        """
        # Locate and read view description
        entitymap = copy.copy(baseentityvaluemap)
        log.debug("entityview %r"%viewinfo.recordview.get_values())
        self.get_fields_entityvaluemap(
            viewinfo.collection,
            entitymap,
            viewinfo.recordview.get_values()['annal:view_fields']
            )
        return entitymap

    def get_entity(self, viewinfo, action, entity_initial_values, entity_id=None):
        """
        Create local entity object or load values from existing.

        viewinfo        DisplaytInfo object for the current view
        action          is the requested action: new, edit, copy
        entity_initial_values
                        is a dictionary of initial values used when 
                        a new entity is created
        entity_id       If not None, overrides entity id to create or load

        returns an object of the appropriate type.

        If an existing entity is accessed, values are read from storage, 
        otherwise a new entity object is created but not yet saved.
        """
        entity_id   = entity_id or viewinfo.entity_id
        typeinfo    = viewinfo.entitytypeinfo
        entityclass = typeinfo.entityclass
        log.debug(
            "get_entity id %s, parent %s, action %s, altparent %s"%
            (entity_id, typeinfo.entityparent, action, typeinfo.entityaltparent)
            )
        entity = None
        if action == "new":
            entity = entityclass(typeinfo.entityparent, entity_id)
            entity.set_values(entity_initial_values)
        elif entityclass.exists(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent):
            entity = entityclass.load(typeinfo.entityparent, entity_id, altparent=typeinfo.entityaltparent)
        if entity is None:
            parent_id = typeinfo.entityaltparent.get_id() if typeinfo.entityaltparent else "(none)"
            log.debug(
                "Entity not found: parent %s, entity_id %s"%(parent_id, entity_id)
                )
        return entity

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.log(settings.TRACE_FIELD_VALUE,
            "views.entityedit.get %s"%(self.get_request_path())
            )
        log.log(settings.TRACE_FIELD_VALUE,
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response

        # Create local entity object or load values from existing
        entity_initial_values = (
            { "rdfs:label":   "Entity '%s' of type '%s' in collection '%s'"%
                              (viewinfo.entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(viewinfo, action, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%{'id': entity_initial_values['rdfs:label']}
                    )
                )
        type_ids = [ t.get_id() for t in viewinfo.collection.types() ]
        # Set up initial view context
        self._entityvaluemap = self.get_view_entityvaluemap(viewinfo)
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', ""),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            type_ids            = type_ids,
            orig_id             = viewinfo.entity_id,
            orig_type           = type_id,
            view_id             = viewinfo.view_id
            )
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request,
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Handle response from generic entity editing form.
        """
        log.debug("views.entityedit.post %s"%(self.get_request_path()))
        log.debug(
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        log.debug("  form data %r"%(request.POST))
        viewinfo = self.view_setup(action, coll_id, type_id, view_id, entity_id)
        if viewinfo.http_response:
            return viewinfo.http_response
        # Get key POST values
        # Except for entity_id, use values from URI when form does not have corresponding fields
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type          = request.POST.get('entity_type', type_id)
        orig_entity_type     = request.POST.get('orig_type', type_id)
        continuation_uri     = (request.POST.get('continuation_uri', None) or
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        view_id              = request.POST.get('view_id', view_id)
        action               = request.POST.get('action', action)
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        # log.info("continuation_uri %s, type_id %s"%(continuation_uri, type_id))
        typeinfo        = viewinfo.entitytypeinfo
        original_entity = self.get_entity(viewinfo, action, {}, entity_id=orig_entity_id)
        type_ids        = [ t.get_id() for t in viewinfo.collection.types() ]
        context_extra_values = (
            { 'title':            self.site_data()["title"]
            , 'heading':          "Entity '%s' of type '%s' in collection '%s'"%
                                  (entity_id, type_id, coll_id)
            , 'action':           action
            , 'continuation_uri': continuation_uri
            , 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'type_ids':         type_ids
            , 'orig_id':          orig_entity_id
            , 'orig_type':        orig_entity_type
            , 'view_id':          view_id
            })
        message_vals = {'id': entity_id, 'type_id': type_id, 'coll_id': coll_id}
        messages = (
            { 'parent_heading':         typeinfo.entitymessages['parent_heading']%message_vals
            , 'parent_missing':         typeinfo.entitymessages['parent_missing']%message_vals
            , 'entity_heading':         typeinfo.entitymessages['entity_heading']%message_vals
            , 'entity_invalid_id':      typeinfo.entitymessages['entity_invalid_id']%message_vals
            , 'entity_exists':          typeinfo.entitymessages['entity_exists']%message_vals
            , 'entity_not_exists':      typeinfo.entitymessages['entity_not_exists']%message_vals
            , 'entity_type_heading':    typeinfo.entitymessages['entity_type_heading']%message_vals
            , 'entity_type_invalid':    typeinfo.entitymessages['entity_type_invalid']%message_vals
            })
        # Process form response and respond accordingly
        self._entityvaluemap = self.get_view_entityvaluemap(viewinfo)
        if not typeinfo.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(viewinfo.collection, typeinfo.entityparent.get_id(), {})
        # log.info(
        #     "self.form_response: entity_id %s, orig_entity_id %s, type_id %s, action %s"%
        #       (entity_id, orig_entity_id, type_id, action)
        #     )
        return self.form_response(
            request, action, typeinfo.entityparent, original_entity,
            entity_id, orig_entity_id, 
            entity_type, orig_entity_type,
            messages, context_extra_values
            )

# End.
