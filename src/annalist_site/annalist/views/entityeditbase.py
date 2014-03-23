"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy
import collections

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import layout
from annalist                       import message
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import util

from annalist.models.site           import Site
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

from annalist.views.generic         import AnnalistGenericView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.fieldvaluemap   import FieldValueMap
from annalist.views.grouprepeatmap  import GroupRepeatMap

from annalist.fields.render_utils   import bound_field, get_placement_classes
from annalist.fields.render_utils   import get_edit_renderer, get_view_renderer
from annalist.fields.render_utils   import get_head_renderer, get_item_renderer
# from annalist.fields.render_utils   import get_grid_renderer


# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        [ SimpleValueMap(c='title',            e=None,           f=None               )
        , SimpleValueMap(c='coll_id',          e=None,           f=None               )
        , SimpleValueMap(c='type_id',          e=None,           f=None               )
        , StableValueMap(c='entity_id',        e='annal:id',     f='entity_id'        )
        , SimpleValueMap(c='entity_uri',       e='annal:uri',    f='entity_uri'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='orig_id',          e=None,           f='orig_id'   )
        , SimpleValueMap(c='action',           e=None,           f='action'           )
        , SimpleValueMap(c='continuation_uri', e=None,           f='continuation_uri' )
        ])

# Table used as basis, or initial values, for a dynamically generated entity-value map
listentityvaluemap  = (
        [ SimpleValueMap(c='title',            e=None,           f=None               )
        , SimpleValueMap(c='coll_id',          e=None,           f=None               )
        , SimpleValueMap(c='type_id',          e=None,           f=None               )
        , SimpleValueMap(c='list_id',          e=None,           f=None               )
        , SimpleValueMap(c='list_ids',         e=None,           f=None               )
        , SimpleValueMap(c='list_selected',    e=None,           f=None               )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='continuation_uri', e=None,           f='continuation_uri' )
        ])

class EntityEditBaseView(AnnalistGenericView):
    """
    View class base for handling entity edits (new, copy, edit, delete logic)

    This class contains shared logic, and must be subclassed to provide specific
    details for an entity type.
    """
    def __init__(self):
        super(EntityEditBaseView, self).__init__()
        return

    def get_coll_data(self, coll_id, host=""):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        self.sitedata = SiteData(self.site(host=host), layout.SITEDATA_DIR)
        # Check collection
        if not Collection.exists(self.site(host=host), coll_id):
            return self.error(
                dict(self.error404values(), 
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        self.collection = Collection.load(self.site(host=host), coll_id)
        return None

    def get_coll_type_data(self, coll_id, type_id, host=""):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection
            self.recordtype
            self.recordtypedata
            self._entityclass

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        self.sitedata = SiteData(self.site(host=host), layout.SITEDATA_DIR)
        # Check collection
        if not Collection.exists(self.site(host=host), coll_id):
            return self.error(
                dict(self.error404values(), 
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        self.collection = Collection.load(self.site(host=host), coll_id)
        # Check type
        if not RecordType.exists(self.collection, type_id):
            return self.error(
                dict(self.error404values(),
                    message=message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
                    )
                )
        self.recordtype     = RecordType(self.collection, type_id)
        self.recordtypedata = RecordTypeData(self.collection, type_id)
        return None

    def get_field_context(self, field):
        """
        Creates a field description value to use in a context value when
        rendering a form.  Values used here are also mentioned in field
        rendering templates.

        field    is the field description from a view or list description.

        Also uses values self.sitedata and self.collection.

        See also: fields.render_utils.bound_field.
        """
        field_id    = field['annal:field_id']
        recordfield = RecordField.load(self.collection, field_id, altparent=True)
        log.debug("recordfield   %r"%(recordfield and recordfield.get_values()))
        return_property_uri = (
            recordfield['annal:property_uri'] if recordfield['annal:return_value'] 
            else None
            )
        field_context = (
            { 'field_id':               field_id
            , 'field_placement':        get_placement_classes(field['annal:field_placement'])
            , 'field_name':             field_id    # Assumes same field can't repeat in form
            , 'field_render_head':      get_head_renderer(recordfield['annal:field_render'])
            , 'field_render_item':      get_item_renderer(recordfield['annal:field_render'])
            , 'field_render_view':      get_view_renderer(recordfield['annal:field_render'])
            , 'field_render_edit':      get_edit_renderer(recordfield['annal:field_render'])
            , 'field_label':            recordfield['rdfs:label']
            , 'field_help':             recordfield['rdfs:comment']
            , 'field_value_type':       recordfield['annal:value_type']
            , 'field_placeholder':      recordfield['annal:placeholder']
            , 'field_property_uri':     recordfield['annal:property_uri']
            , 'return_property_uri':    return_property_uri
            })
        return field_context

    def get_fields_entityvaluemap(self, entityvaluemap, fields):
        for f in fields:
            log.debug("get_fields_entityvaluemap: field %r"%(f))
            field_context = self.get_field_context(f)
            entityvaluemap.append(
                FieldValueMap(c='fields', f=field_context)
                )
        return entityvaluemap

    def get_form_entityvaluemap(self, view_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions.
        """
        # Locate and read view description
        entitymap  = copy.copy(baseentityvaluemap)
        entityview = RecordView.load(self.collection, view_id)
        log.debug("entityview   %r"%entityview.get_values())
        self.get_fields_entityvaluemap(
            entitymap,
            entityview.get_values()['annal:view_fields']
            )
        return entitymap

    def get_list_entityvaluemap(self, list_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for the indicated list display.
        """
        # Locate and read view description
        entitymap  = copy.copy(listentityvaluemap)
        entitylist = RecordList.load(self.collection, list_id)
        log.debug("entitylist %r"%entitylist.get_values())
        groupmap = []
        self.get_fields_entityvaluemap(
            groupmap,
            entitylist.get_values()['annal:list_fields']
            )
        entitymap.extend(groupmap)  # for field headings
        entitymap.append(
            GroupRepeatMap(c='entities', e='annal:list_entities', g=groupmap)
            )
        return entitymap

    def map_value_to_context(self, entity_values, **kwargs):
        """
        Map data from entity values to view context for rendering.

        Values defined in the supplied entity take priority, and the keyword arguments provide
        values when the entity does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            kmap.map_entity_to_context(context, entity_values, defaults=kwargs)
        return context

    def map_form_data_to_context(self, form_data, **kwargs):
        """
        Map values from form data to view context for form re-rendering.

        Values defined in the supplied form data take priority, and the keyword arguments provide
        values where the form data does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            kmap.map_form_to_context(context, form_data, defaults=kwargs)
        return context

    def map_form_data_to_values(self, form_data, **kwargs):
        log.debug("map_form_data_to_values: form_data %r"%(form_data))
        values = {}
        for kmap in self._entityvaluemap:
            kmap.map_form_to_entity(values, form_data)
        return values

    def get_entityid(self, action, parent, entityid):
        if action == "new":
            entityid = self._entityclass.allocate_new_id(parent)
        return entityid

    def form_edit_auth(self, action, auth_resource):
        """
        Check that the requested form action is authorized for the current user.

        action          is the requested action: new, edit, copy, etc.
        auth_resource   is the resource URI to which the requested action is directed.
                        NOTE: This may be the URI of the parent of the resource
                        being accessed or manipulated.
        """
        action_scope = (
            { "view":   "VIEW"
            , "list":   "VIEW"
            , "search": "VIEW"
            , "new":    "CREATE"
            , "copy":   "CREATE"
            , "edit":   "UPDATE"
            , "delete": "DELETE"
            , "config": "CONFIG"    # or UPDATE?
            , "admin":  "ADMIN"
            })
        if action in action_scope:
            auth_scope = action_scope[action]
        else:
            auth_scope = "UNKNOWN"
        # return self.authorize(auth_scope, auth_resource)
        return self.authorize(auth_scope)

    def get_entity(self, action, parent, entityid, entity_initial_values):
        """
        Create local entity object or load values from existing.

        action          is the requested action: new, edit, copy
        parent          is tghe parent of the entity to be accessed or created
        entityid        is the local id (slug) of the entity to be accessed or created
        entity_initial_values  is a dictionary of initial values used when a new entity
                        is created

        self._entityclass   is the class of the entity to be acessed or created.

        returns an object of the appropriate type.  If an existing entity is accessed, values
        are read from storage, otherwise a new entity object is created but not yet saved.
        """
        log.debug("get_entity id %s, parent %s, action %s"%(entityid, parent._entitydir, action))
        entity = None
        if action == "new":
            entity = self._entityclass(parent, entityid)
            entity.set_values(entity_initial_values)
        elif self._entityclass.exists(parent, entityid):
            entity = self._entityclass.load(parent, entityid)
        return entity

    def form_render(self, request, action, parent, entityid, entity_initial_values, context_extra_values):
        """
        Return rendered form for entity edit, or error response.
        """
        # Sort access mode and authorization
        auth_required = self.form_edit_auth(action, parent._entityuri)
        if auth_required:
                return auth_required
        # Create local entity object or load values from existing
        entity = self.get_entity(action, parent, entityid, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(), 
                    message=message.DOES_NOT_EXIST%(entity_initial_values['rdfs:label'])
                    )
                )
        context = self.map_value_to_context(entity,
            title            = self.site_data()["title"],
            continuation_uri = request.GET.get('continuation_uri', None),
            action           = action,
            **context_extra_values
            )
        return (
            self.render_html(context, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def form_re_render(self, request, context_extra_values={}, error_head=None, error_message=None):
        """
        Returns re-rendering of form with current values and error message displayed.
        """
        form_data = self.map_form_data_to_context(request.POST,
            title=self.site_data()["title"],
            **context_extra_values
            )
        form_data['error_head']    = error_head
        form_data['error_message'] = error_message
        return (
            self.render_html(form_data, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    def form_response(self, request, action, parent, entityid, orig_entityid, messages, context_extra_values):
        """
        Handle POST response from entity edit form.
        """
        log.debug("form_response: action %s"%(request.POST['action']))
        continuation_uri = context_extra_values['continuation_uri']
        if 'cancel' in request.POST:
            # log.debug("form_response: cancel")
            return HttpResponseRedirect(continuation_uri)
        # Check authorization
        auth_required = self.form_edit_auth(action, parent._entityuri)
        if auth_required:
            # log.debug("form_response: auth_required")            
            return auth_required
        # Check parent exists (still)
        if not parent._exists():
            # log.debug("form_response: not parent._exists()")
            return self.form_re_render(request, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )
        # Check response has valid type id
        if not util.valid_id(entityid):
            # log.debug("form_response: not util.valid_id('%s')"%entityid)
            return self.form_re_render(request, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        # Process response
        entityid_changed = (request.POST['action'] == "edit") and (entityid != orig_entityid)
        if 'save' in request.POST:
            log.debug(
                "form_response: save, action %s, entity_id %s, orig_entityid %s"
                %(request.POST['action'], entityid, orig_entityid)
                )
            # Check existence of type to save according to action performed
            if (request.POST['action'] in ["new", "copy"]) or entityid_changed:
                if self._entityclass.exists(parent, entityid):
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_exists']
                        )
            else:
                if not self._entityclass.exists(parent, entityid):
                    # This shouldn't happen, but just incase...
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_not_exists']
                        )
            # Create/update data now
            entity_initial_values = self.map_form_data_to_values(request.POST)
            self._entityclass.create(parent, entityid, entity_initial_values)
            # Remove old type if rename
            if entityid_changed:
                if self._entityclass.exists(parent, entityid):    # Precautionary
                    self._entityclass.remove(parent, orig_entityid)
            return HttpResponseRedirect(continuation_uri)
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(continuation_uri+err_values)


class EntityDeleteConfirmedBaseView(AnnalistGenericView):
    """
    View class to perform completion of confirmed entity deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(EntityDeleteConfirmedBaseView, self).__init__()
        return

    def confirm_form_respose(self, request, parent, entityid, remove_fn, messages, continuation_uri):
        """
        Process options to complete action to remove an entity
        """
        auth_required = self.authorize("DELETE")
        if auth_required:
            return auth_required
        err     = remove_fn(entityid)
        if err:
            return self.redirect_error(continuation_uri, str(err))
        return self.redirect_info(continuation_uri, messages['entity_removed'])

# End.
