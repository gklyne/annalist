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

from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

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

    # def __init__(self, view_id=None, entity_class=EntityData):
    def __init__(self):
        super(GenericEntityEditView, self).__init__()
        # self._view_id       = view_id
        # self._entityclass   = entity_class
        return

    def get_view_id(self, view_id):
        if not view_id:
            log.warning("GenericEntityEditView: No view identifier provided")
        return view_id

    # GET

    def get(self, request, 
            coll_id=None, type_id=None, entity_id=None, 
            view_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.debug("views.entityedit.get %s"%(self.get_request_path()))
        log.debug(
            "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
              (coll_id, type_id, entity_id, view_id, action)
            )
        http_response = (
            self.get_coll_data(coll_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.collection._entityuri) or
            self.get_type_data(type_id) or
            self.get_view_data(self.get_view_id(view_id))
            )
        if http_response:
            return http_response
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, self.entityparent, entity_id)
        # Create local entity object or load values from existing
        entity_initial_values = (
            { "rdfs:label":   "Entity '%s' of type '%s' in collection '%s'"%
                              (entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(action, self.entityparent, entity_id, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%(entity_initial_values['rdfs:label'])
                    )
                )
        type_ids = [ t.get_id() for t in self.collection.types() ]
        # Set up initial view context
        # @@TODO: move view access logic from get_form_entityvaluemap (see there for details)
        self._entityvaluemap = self.get_form_entityvaluemap(self.get_view_id(view_id))
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', ""),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            type_ids            = type_ids,
            orig_id             = entity_id,
            orig_type           = type_id
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
        http_response = (
            self.get_coll_data(coll_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.collection._entityuri) or
            self.get_type_data(type_id) or
            self.get_view_data(self.get_view_id(view_id))
            )
        if http_response:
            return http_response
        # Get key POST values; use values from URI when form does not have corresponding fields
        entity_id            = request.POST.get('Entity_id', entity_id)
        orig_entity_id       = request.POST.get('orig_id', entity_id)
        entity_type          = request.POST.get('Entity_type', type_id)
        orig_entity_type     = request.POST.get('orig_type', type_id)
        continuation_uri     = (request.POST.get('continuation_uri', None) or
            self.view_uri('AnnalistEntityDefaultListType', coll_id=coll_id, type_id=type_id)
            )
        # log.info(
        #     "    coll_id %s, type_id %s, entity_id %s, view_id %s, action %s"%
        #       (coll_id, type_id, entity_id, view_id, action)
        #     )
        # log.info("continuation_uri %s, type_id %s"%(continuation_uri, type_id))
        type_ids = [ t.get_id() for t in self.collection.types() ]
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'type_id':          type_id
            , 'type_ids':         type_ids
            , 'continuation_uri': continuation_uri
            })
        messages = (
            { 'parent_heading':         message.RECORD_TYPE_ID
            , 'parent_missing':         message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
            , 'entity_heading':         message.ENTITY_DATA_ID
            , 'entity_invalid_id':      message.ENTITY_DATA_ID_INVALID
            , 'entity_exists':          message.ENTITY_DATA_EXISTS%(entity_id, type_id, coll_id)
            , 'entity_not_exists':      message.ENTITY_DATA_NOT_EXISTS%(entity_id, type_id, coll_id)
            , 'entity_type_heading':    message.ENTITY_TYPE_ID
            , 'entity_type_invalid':    message.ENTITY_TYPE_ID_INVALID
            })
        # Process form response and respond accordingly
        self._entityvaluemap = self.get_form_entityvaluemap(self.get_view_id(view_id))
        if not self.entityparent._exists():
            # Create RecordTypeData when not already exists
            RecordTypeData.create(self.collection, self.entityparent.get_id(), {})
        # log.info(
        #     "self.form_response: entity_id %s, orig_entity_id %s, type_id %s, action %s"%
        #       (entity_id, orig_entity_id, type_id, action)
        #     )
        return self.form_response(
            request, action, self.entityparent, 
            entity_id, orig_entity_id, 
            entity_type, orig_entity_type,
            messages, context_extra_values
            )

# End.
