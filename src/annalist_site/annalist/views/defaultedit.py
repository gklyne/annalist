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

# from annalist                       import layout
from annalist                       import message

# from annalist.models.sitedata       import SiteData
# from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
# from annalist.models.recordtype     import RecordType
# from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap
from annalist.fields.render_utils   import get_renderer, get_placement_class

class EntityDefaultEditView(EntityEditBaseView):
    """
    View class for default record edit view
    """
    # These values are referenced via instances...
    _entityformtemplate = 'annalist_entity_edit.html'
    _entityclass        = None          # to be supplied dynamically

    def __init__(self):
        super(EntityDefaultEditView, self).__init__()
        self._view_id       = "Default_view"
        self._entityclass   = EntityData
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.debug("defaultedit.get: coll_id %s, type_id %s, entity_id %s, action %s"%
            (coll_id, type_id, entity_id, action)
            )
        http_response = (
            self.get_coll_type_data(coll_id, type_id, host=self.get_request_host()) or
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
        self.get_form_entityvaluemap(self._view_id)
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            orig_id             = entity_id
            )
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
            self.get_coll_type_data(coll_id, type_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.recordtypedata._entityuri)
            )
        if http_response:
            return http_response
        # Get key POST values
        entity_id            = request.POST.get('Entity_id', None)
        orig_entity_id       = request.POST.get('orig_id', None)
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
