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
        , SimpleValueMap(c='orig_id',          e=None,           f='orig_id'          )
        , SimpleValueMap(c='orig_type',        e=None,           f='orig_type'          )
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

Type_Class_Map = (
    { '_type':  RecordType
    , '_list':  RecordList
    , '_view':  RecordView
    , '_field': RecordField
    })

def getEntityTypeClass(type_id):
    """
    Return entity class for supplied type id, to be used when scanning
    for instrances of the indicated type_id.
    """
    return Type_Class_Map.get(type_id, RecordTypeData)

def isEntityTypeMeta(type_id):
    """
    Return True if a supplied type id is site or collection metadata type,
    otherwise False.
    """
    return type_id in Type_Class_Map

class EntityEditBaseView(AnnalistGenericView):
    """
    View class base for handling entity edits (new, copy, edit, delete logic)

    This class contains shared logic, and must be subclassed to provide specific
    details for an entity type.
    """
    def __init__(self):
        super(EntityEditBaseView, self).__init__()
        return

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
        if recordfield is None:
            raise ValueError("Can't retrieve definition for field %s"%(field_id))
        log.debug("recordfield   %r"%(recordfield and recordfield.get_values()))
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
            , 'field_options':          recordfield.get('annal:options', None)
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
        information from the form field definitions for an indicated view.
        """
        # Locate and read view description
        # @@TODO: push responsibility to subclass to call get_view_data, and use resulting value
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
        information from the form field definitions for an indicated list display.
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
            kmap.map_entity_to_context(context, entity_values, extras=kwargs)
        return context

    def map_form_data_to_context(self, form_data, **kwargs):
        """
        Map values from form data to view context for form re-rendering.

        Values defined in the supplied form data take priority, and the keyword arguments provide
        values where the form data does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            kmap.map_form_to_context(context, form_data, extras=kwargs)
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

    def form_response(self, 
                request, action, orig_parent, 
                entity_id, orig_entity_id, 
                entity_type, orig_entity_type, 
                messages, context_extra_values
            ):
        """
        Handle POST response from entity edit form.
        """
        log.debug("form_response: action %s"%(request.POST['action']))
        continuation_uri = context_extra_values['continuation_uri']
        if 'cancel' in request.POST:
            return HttpResponseRedirect(continuation_uri)
        # Check authorization
        # @@TODO redundant?  Checked by calling POST handler?
        auth_required = self.form_edit_auth(action, orig_parent._entityuri)
        if auth_required:
            # log.debug("form_response: auth_required")            
            return auth_required
        # Check original parent exists (still)
        if not orig_parent._exists():
            log.warning("form_response: not orig_parent._exists()")
            return self.form_re_render(request, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )
        # Check response has valid id and type
        if not util.valid_id(entity_id):
            log.debug("form_response: entityid not util.valid_id('%s')"%entity_id)
            return self.form_re_render(request, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        if not util.valid_id(entity_type):
            log.debug("form_response: entitytype not util.valid_id('%s')"%entity_type)
            return self.form_re_render(request, context_extra_values,
                error_head=messages['entity_type_heading'],
                error_message=messages['entity_type_invalid']
                )
        # Process response
        entity_id_changed = (
            ( request.POST['action'] == "edit" ) and
            ( (entity_id != orig_entity_id) or (entity_type != orig_entity_type) )
            )
        if 'save' in request.POST:
            log.debug(
                "form_response: save, action %s, entity_id %s, orig_entity_id %s"
                %(request.POST['action'], entity_id, orig_entity_id)
                )
            log.debug(
                "                     entity_type %s, orig_entity_type %s"
                %(entity_type, orig_entity_type)
                )
            # Determine parent for saved entity
            if entity_type != orig_entity_type:
                log.debug("form_response: entity_type %s, orig_entity_type %s"%(entity_type, orig_entity_type))
                new_parent = RecordTypeData(self.collection, entity_type)
                if not new_parent._exists():
                    # Create RecordTypeData if not already existing
                    RecordTypeData.create(self.collection, entity_type, {})
            else:
                new_parent = orig_parent
            # Check existence of type to save according to action performed
            if (request.POST['action'] in ["new", "copy"]) or entity_id_changed:
                if self._entityclass.exists(new_parent, entity_id):
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_exists']
                        )
            else:
                if not self._entityclass.exists(orig_parent, entity_id):
                    # This shouldn't happen, but just in case...
                    log.warning("Expected %s/%s not found; action %s, entity_id_changed %r"%
                          (entity_type, entity_id, request.POST['action'], entity_id_changed)
                        )
                    return self.form_re_render(request, context_extra_values,
                        error_head=messages['entity_heading'],
                        error_message=messages['entity_not_exists']
                        )
            # Create/update data now
            entity_initial_values = self.map_form_data_to_values(request.POST)
            self._entityclass.create(new_parent, entity_id, entity_initial_values)
            # Remove old type if rename
            if entity_id_changed:
                if self._entityclass.exists(orig_parent, entity_id):    # Precautionary
                    self._entityclass.remove(orig_parent, orig_entity_id)
            log.debug("Continue to %s"%(continuation_uri))
            return HttpResponseRedirect(continuation_uri)
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        log.warning("Unexpected form data %s"%(err_values))
        log.warning("Continue to %s"%(continuation_uri))
        return HttpResponseRedirect(continuation_uri+err_values)


class EntityDeleteConfirmedBaseView(AnnalistGenericView):
    """
    View class to perform completion of confirmed entity deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(EntityDeleteConfirmedBaseView, self).__init__()
        return

    def confirm_form_respose(self, request, parent, entity_id, remove_fn, messages, continuation_uri):
        """
        Process options to complete action to remove an entity
        """
        # @@TODO consider eliding this class 
        auth_required = self.form_edit_auth("delete", parent.get_uri())
        if auth_required:
            return auth_required
        err     = remove_fn(entity_id)
        if err:
            return self.redirect_error(continuation_uri, str(err))
        return self.redirect_info(continuation_uri, messages['entity_removed'])

# End.
