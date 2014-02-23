"""
Annalist record type views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os
# import os.path
# import urlparse
# import shutil

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

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
# from annalist.recordview        import RecordView
# from annalist.recordlist        import RecordList

from annalist.views.generic     import AnnalistGenericView

class EntityValueMap(object):
    """
    Define an entry in an entity value mapping table, where each entry has a key
    used to:
    i: specify an initial value when creating a new entity,
    v: access a given value in an entity values record,
    c: access a given value in a view render context, and
    f: access a given value in form data.
    """
    def __init__(self, i=None, v=None, c=None, f=None):
        self.i = i
        self.v = v
        self.c = c
        self.f = f
        return

    def __str__(self):
        return "{v:%s, c:%s, f:%s)"%(self.v, self.c, self.f)

    def __repr__(self):
        return "EntityValueMap(v=%r, c=%r, f=%r)"%(self.v, self.c, self.f)


def context_from_record_type_form(site_data, coll_id, form_data, **kwargs):
    """
    Local helper function builds a record type form rendering context
    from supplied site data, RecordType object and optional form data overrides.
    """
    context = (
        { 'title':              site_data["title"]
        , 'coll_id':            coll_id
        })
    # Note: context and form_data keys can be different
    def context_update(key, form_key):
        if form_key in form_data:
            context[key] = form_data[form_key]
    context_update('type_id',           'type_id')
    context_update('type_label',        'type_label')
    context_update('type_help',         'type_help')
    context_update('type_uri',          'type_class')
    context_update('orig_type_id',      'orig_type_id')
    context_update('continuation_uri',  'continuation_uri')
    context_update('action',            'action')
    if kwargs:
        context.update(kwargs)
    return context

class RecordTypeEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist record type edit URI
    """

    _entityclass        = RecordType
    _entityformtemplate = 'annalist_recordtype_edit.html'
    _entityvaluemap     = (
        # Special fields
        [ EntityValueMap(i=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(i=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(i=None,          v='annal:id',     c='type_id',          f='type_id'          )
        # Normal fields
        , EntityValueMap(i=None,          v='annal:type',   c=None,               f=None               )
        , EntityValueMap(i='rdfs:label',  v='rdfs:label',   c='type_label',       f='type_label'       )
        , EntityValueMap(i='rdfs:comment',v='rdfs:comment', c='type_help',        f='type_help'        )
        , EntityValueMap(i='annal:uri',   v='annal:uri',    c='type_uri',         f='type_class'       )
        # Form and interaction control
        , EntityValueMap(i=None,          v=None,           c='orig_type_id',     f='orig_type_id'     )
        , EntityValueMap(i=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(i=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(RecordTypeEditView, self).__init__()
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

    def map_form_data_to_init_values(self, form_data, **kwargs):
        values = {}
        for kmap in self._entityvaluemap:
            if kmap.i:
                if kmap.f and kmap.f in form_data:
                    values[kmap.i] = form_data[kmap.f]
                elif kmap.c in kwargs:
                    values[kmap.i] = kwargs[kmap.i]
        return values

    def get_entityid(self, action, parent, entityid):
        if action == "new":
            entityid = self._entityclass.allocate_new_id(parent)
        return entityid

    def form_render(self, request, action, parent, entityid, entity_initial_values, context_extra_values):
        """
        Return rendered form for entity edit, or error response.
        """
        # Sort access mode and authorization
        if action == "new":
            auth_scope = "CREATE"
        else:
            auth_scope = "UPDATE"
        auth_required = self.authorize(auth_scope)
        if auth_required:
                return auth_required
        # Create local entity object or load values from existing
        if action == "new":
            entity = self._entityclass(parent, entityid)
            entity.set_values(entity_initial_values)
        elif self._entityclass.exists(parent, entityid):
            entity = self._entityclass.load(parent, entityid)
        else:
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

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing a type.
        """
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        coll = Collection(self.site(), coll_id)
        # Set up RecordType-specific values
        type_id              = self.get_entityid(action, coll, type_id)
        # default_type_label   = "Record type %s in collection %s"%(type_id, coll_id)
        initial_type_values  = (
            { "annal:id":     type_id
            , "annal:type":   "annal:RecordType"
            , "annal:uri":    coll._entityuri+type_id+"/"
            , "rdfs:label":   "Record type %s in collection %s"%(type_id, coll_id)
            , "rdfs:comment": ""
            })
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'orig_type_id':     type_id
            })
        return self.form_render(request,
            action, coll, type_id, 
            initial_type_values, 
            context_extra_values
            )

    # POST

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
        if action == "new":
            auth_scope = "CREATE"
        else:
            auth_scope = "UPDATE"
        auth_required = self.authorize(auth_scope)
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
            entity_initial_values = self.map_form_data_to_init_values(request.POST)
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


    def post(self, request, coll_id=None, type_id=None, action=None):
        """
        Handle response to record type edit form
        """
        log.debug("views.recordtype.post %s"%(self.get_request_path()))
        # log.info("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.info("  form data %r"%(request.POST))
        type_id              = request.POST.get('type_id', None)
        orig_type_id         = request.POST.get('orig_type_id', None)
        collection_edit_uri  = self.view_uri('AnnalistCollectionEditView', coll_id=coll_id)
        continuation_uri     = request.POST.get('continuation_uri', collection_edit_uri)
        coll                 = self.collection(coll_id)
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'continuation_uri': continuation_uri
            })
        messages = (
            { 'parent_heading':    message.COLLECTION_ID
            , 'parent_missing':    message.COLLECTION_NOT_EXISTS%(coll_id)
            , 'entity_heading':    message.RECORD_TYPE_ID
            , 'entity_invalid_id': message.RECORD_TYPE_ID_INVALID
            , 'entity_exists':     message.RECORD_TYPE_EXISTS%(type_id, coll_id)
            , 'entity_not_exists': message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)        
            })
        return self.form_response(request, action, coll, type_id, orig_type_id, messages, context_extra_values)


class RecordTypeDeleteConfirmedView(AnnalistGenericView):
    """
    View class to perform completion of confirmed record type deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordTypeDeleteConfirmedView, self).__init__()
        return

    # POST

    def form_respose(self, request, parent, entityid, remove_fn, messages, continuation_uri):
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


    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record type from a collection
        """
        log.debug("RecordTypeDeleteConfirmedView.post: %r"%(request.POST))
        if "type_delete" in request.POST:
            coll      = self.collection(coll_id)
            type_id   = request.POST['typelist']
            messages  = (
                { 'entity_removed': message.RECORD_TYPE_REMOVED%(type_id, coll_id)
                })
            continuation_uri = self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.form_respose(request, coll, type_id, coll.remove_type, messages, continuation_uri)

            # auth_required = self.authorize("DELETE")
            # if auth_required:
            #     return auth_required
            # coll    = self.collection(coll_id)
            # type_id = request.POST['typelist']
            # err     = coll.remove_type(type_id)
            # if err:
            #     return self.redirect_error(
            #         self.view_uri("AnnalistCollectionEditView", coll_id=coll_id), 
            #         str(err))
            # return self.redirect_info(
            #         self.view_uri("AnnalistCollectionEditView", coll_id=coll_id), 
            #         message.RECORD_TYPE_REMOVED%(type_id, coll_id)
            #         )

        return self.error(self.error400values())

# End.
