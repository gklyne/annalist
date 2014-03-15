"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy

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
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData

from annalist.views.generic         import AnnalistGenericView
from annalist.fields.render_utils   import get_renderer, get_placement_class


class EntityValueMap(object):
    """
    Define an entry in an entity value mapping table, where each entry has a key
    used to:
    v: access a given value in an entity values record
    c: access a given value in a view render context
    s: sub-context (name, context)
    f: access a given value in form data
    e: value key when updating an entity from form data
    """
    def __init__(self, v=None, c=None, s=None, f=None, e=None):
        self.v = v      # value field to populate context
        self.c = c      # context field to populate
        self.s = s      # sub-context for template iteration over context
        self.f = f      # field name for value
        self.e = e      # entity value field for retrieved value
        return

    def __str__(self):
        return "{v:%s, c:%s, f:%s, e:%s)"%(self.v, self.c, self.f, self.e)

    def __repr__(self):
        return "EntityValueMap(v=%r, c=%r, f=%r, e=%r, s=%r)"%(self.v, self.c, self.f, self.e, self.s)

# Table used as basis, or initial values, for a dynamically generated entity-value map
baseentityvaluemap  = (
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v=None,           c='type_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='entity_id',        f='entity_id'        )
        , EntityValueMap(e='annal:uri',   v='annal:uri',    c='entity_uri',       f='entity_uri'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , EntityValueMap(e=None,          v=None,           c='orig_id',          f='orig_id'   )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
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
        self.collection = Collection(self.site(host=host), coll_id)
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

    def get_form_entityvaluemap(self, view_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions.
        """
        # Locate and read view description
        entitymap  = copy.copy(baseentityvaluemap)
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
                , 'field_property_uri': viewfield['annal:property_uri']
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

    def map_entry_to_context(self,
            context, subcontext, contextkey, valuekey, entity_values, 
            **kwargs):
        """
        Helper function maps a single entry from a dictionary of entity values
        (incoming values or form data) to an entry in a context used for rendering
        an editing form.
        """
        if subcontext:
            # Create sub-context and select that (used for data-described form fields)
            subcontextname, subcontextdata = subcontext
            if subcontextname not in context:
                context[subcontextname] = []
            subcontextdata = copy.copy(subcontextdata)
            context[subcontextname].append(subcontextdata)
            usecontext = subcontextdata
        else:
            usecontext = context
        if contextkey:
            if valuekey and valuekey in entity_values.keys():
                usecontext[contextkey] = entity_values[valuekey]    # Copy value -> context
            elif contextkey in kwargs:
                usecontext[contextkey] = kwargs[contextkey]         # Supplied argument -> context
        return

    def map_value_to_context(self, entity_values, **kwargs):
        """
        Map data from entity values to view context for rendering.

        Values defined in the supplied entity take priority, and the keyword arguments provide
        values when the entity does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            self.map_entry_to_context(
                context, kmap.s, kmap.c, kmap.v, entity_values, 
                **kwargs
                )
        return context

    def map_form_data_to_context(self, form_data, **kwargs):
        """
        Map values from form data to view context for form re-rendering.

        Values defined in the supplied form data take priority, and the keyword arguments provide
        values where the form data does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            self.map_entry_to_context(
                context, kmap.s, kmap.c, kmap.f, form_data, 
                **kwargs
                )
        return context

    def map_form_data_to_values(self, form_data, **kwargs):
        log.debug("map_form_data_to_values: form_data %r"%(form_data))
        values = {}
        for kmap in self._entityvaluemap:
            if kmap.e:
                if kmap.f and kmap.f in form_data:
                    values[kmap.e] = form_data[kmap.f]
                elif kmap.e in kwargs:
                    values[kmap.e] = kwargs[kmap.e]
        return values

    def get_entityid(self, action, parent, entityid):
        if action == "new":
            entityid = self._entityclass.allocate_new_id(parent)
        return entityid

    def form_edit_auth(self, action, auth_resource):
        """
        Check that the requested form action is authorized for the current user.

        action          is the requested action: new, edit, copy
        auth_resource   is the resource URI to which the requested action is directed.
                        NOTE: This may be the URI of the parent of the resource
                        being accessed or manipulated.
        """
        if action == "view":
            auth_scope = "VIEW"
        elif action in ["new", "copy"]:
            auth_scope = "CREATE"
        elif action == "edit":
            auth_scope = "UPDATE"
        elif action == "delete":
            auth_scope = "DELETE"
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
