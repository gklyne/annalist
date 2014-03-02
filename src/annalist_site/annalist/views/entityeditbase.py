"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import resolve, reverse

from annalist                   import message
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import util

from annalist.models.site       import Site

from annalist.views.generic     import AnnalistGenericView


class EntityValueMap(object):
    """
    Define an entry in an entity value mapping table, where each entry has a key
    used to:
    e: specify an initial value when creating/updating an entity,
    v: access a given value in an entity values record,
    c: access a given value in a view render context, and
    f: access a given value in form data.
    """
    def __init__(self, e=None, v=None, c=None, f=None):
        self.e = e
        self.v = v
        self.c = c
        self.f = f
        return

    def __str__(self):
        return "{v:%s, c:%s, f:%s)"%(self.v, self.c, self.f)

    def __repr__(self):
        return "EntityValueMap(v=%r, c=%r, f=%r)"%(self.v, self.c, self.f)


class EntityEditBaseView(AnnalistGenericView):
    """
    View class base for handling entity edits (new, copy, edit, delete logic)

    This class contains shared logic, and must be subclassed to provide specific
    details for an entity type.
    """
    def __init__(self):
        super(EntityEditBaseView, self).__init__()
        return

    def map_value_to_context(self, entity, **kwargs):
        """
        Map data from entity values to view context for rendering.

        Values defined in the supplied entity take priority, and the keyword arguments provide
        values when the entity does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            if kmap.c:
                if kmap.v and kmap.v in entity.keys():
                    context[kmap.c] = entity[kmap.v]    # Copy value -> context
                elif kmap.c in kwargs:
                    context[kmap.c] = kwargs[kmap.c]    # Copy supplied argument -> context
        return context

    def map_form_data_to_context(self, form_data, **kwargs):
        """
        Map values from form data to view context for form re-rendering.

        Values defined in the supplied entity take priority, and the keyword arguments provide
        values where the form data does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            if kmap.c:
                if kmap.f and kmap.f in form_data:
                    context[kmap.c] = form_data[kmap.f]
                elif kmap.c in kwargs:
                    context[kmap.c] = kwargs[kmap.c]
        return context

    def map_form_data_to_values(self, form_data, **kwargs):
        values = {}
        for kmap in self._entityvaluemap:
            if kmap.e:
                if kmap.f and kmap.f in form_data:
                    values[kmap.e] = form_data[kmap.f]
                elif kmap.c in kwargs:
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
        continuation_uri = context_extra_values['continuation_uri']
        if 'cancel' in request.POST:
            return HttpResponseRedirect(continuation_uri)
        # Check authorization
        auth_required = self.form_edit_auth(action, parent._entityuri)
        if auth_required:
                return auth_required
       # Check parent exists (still)
        if not parent._exists():
            return self.form_re_render(request, context_extra_values,
                error_head=messages['parent_heading'],
                error_message=messages['parent_missing']
                )
        # Check response has valid type id
        if not util.valid_id(entityid):
            return self.form_re_render(request, context_extra_values,
                error_head=messages['entity_heading'],
                error_message=messages['entity_invalid_id']
                )
        # Process response
        entityid_changed = (request.POST['action'] == "edit") and (entityid != orig_entityid)
        if 'save' in request.POST:
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
            # Create/update record type now
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
        type_id = request.POST['typelist']
        err     = remove_fn(entityid)
        if err:
            return self.redirect_error(continuation_uri, str(err))
        return self.redirect_info(continuation_uri, messages['entity_removed'])

# End.
