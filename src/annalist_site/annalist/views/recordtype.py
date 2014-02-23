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

class EntityValueMap(object):
    """
    Define an entry in an entity value mapping table, where each entry has a key
    used to access a given value in an entity values record, a view render context
    and in form data respectively.
    """
    def __init__(self, v=None, c=None, f=None):
        self.v = v
        self.c = c
        self.f = f
        return

    def __str__(self):
        return "{v:%s, c:%s, f:%s)"%(self.v, self.c, self.f)

    def __repr__(self):
        return "EntityValueMap(v=%r, c=%r, f=%r)"%(self.v, self.c, self.f)


class RecordTypeEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist record type edit URI
    """

    _entityclass    = RecordType
    _entityvaluemap = (
        # Special fields
        [ EntityValueMap(v=None,           c='title',            f=None               )
        , EntityValueMap(v=None,           c='coll_id',          f=None               )
        , EntityValueMap(v='annal:id',     c='type_id',          f='type_id'          )
        # Normal fields
        , EntityValueMap(v='annal:type',   c=None,               f=None               )
        , EntityValueMap(v='rdfs:label',   c='type_label',       f='type_label'       )
        , EntityValueMap(v='rdfs:comment', c='type_help',        f='type_help'        )
        , EntityValueMap(v='annal:uri',    c='type_uri',         f='type_class'       )
        # Form and interaction control
        , EntityValueMap(v=None,           c='orig_type_id',     f='orig_type_id'     )
        , EntityValueMap(v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(RecordTypeEditView, self).__init__()
        return

    def map_value_to_context(self, entity, **kwargs):
        """
        Map data from entioty values to view context for renering.

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

    def get_entityid(self, parent, entityid, action):
        if action == "new":
            entityid = self._entityclass.allocate_new_id(parent)
        return entityid

    def form_render(self, request, action, parent, entityid, entity_initial_values, context_extra_values, form_template):
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
            self.render_html(context, form_template) or 
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
        type_id              = self.get_entityid(coll, type_id, action)
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
            context_extra_values, 
            'annalist_recordtype_edit.html'
            )

        # # Sort access mode and authorization
        # if action == "new":
        #     auth_scope = "CREATE"
        # else:
        #     auth_scope = "UPDATE"
        # auth_required = self.authorize(auth_scope)
        # if auth_required:
        #         return auth_required

        # # Create local record type object or load values from existing
        # if action == "new":
        #     record_type    = self._entityclass(coll, type_id)
        #     record_type.set_values(initial_type_values)
        # elif self._entityclass.exists(coll, type_id):
        #     record_type = self._entityclass.load(coll, type_id)
        # else:
        #     return self.error(
        #         dict(self.error404values(), 
        #             message=message.DOES_NOT_EXIST%(initial_type_values['rdfs:label'])
        #             )
        #         )
        # context = self.map_value_to_context(record_type,
        #     title            = self.site_data()["title"],
        #     continuation_uri = request.GET.get('continuation_uri', None),
        #     action           = action,
        #     **context_extra_values
        #     )
        # return (
        #     self.render_html(context, 'annalist_recordtype_edit.html') or 
        #     self.error(self.error406values())
        #     )

    # POST

    def post(self, request, coll_id=None, type_id=None, action=None):
        """
        Handle response to record type edit form
        """
        log.debug("views.recordtype.post %s"%(self.get_request_path()))
        # log.info("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.info("  form data %r"%(request.POST))
        continuation_uri    = request.POST['continuation_uri']
        collection_edit_uri = self.view_uri('AnnalistCollectionEditView', coll_id=coll_id)
        continuation_uri    = request.POST.get('continuation_uri', collection_edit_uri)
        if 'cancel' in request.POST:
            return HttpResponseRedirect(request.POST['continuation_uri'])
        # Check authorization
        if action == "new":
            auth_scope = "CREATE"
        else:
            auth_scope = "UPDATE"
        auth_required = self.authorize(auth_scope)
        if auth_required:
            return auth_required
        # Check collection exists (still)
        coll = self.collection(coll_id)
        if not coll._exists():
            form_data = context_from_record_type_form(
                self.site_data(), coll_id, request.POST,
                error_head=message.COLLECTION_ID,
                error_message=message.COLLECTION_NOT_EXISTS%(coll_id)
                )
            return (
                self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                self.error(self.error406values())
                )
        # Check response has valid type id
        type_id      = request.POST.get('type_id', None)
        orig_type_id = request.POST.get('orig_type_id', None)
        if not util.valid_id(type_id):
            form_data = context_from_record_type_form(
                self.site_data(), coll_id, request.POST,
                error_head=message.RECORD_TYPE_ID,
                error_message=message.RECORD_TYPE_ID_INVALID
                )
            return (
                self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                self.error(self.error406values())
                )
        # Process response
        type_id_changed = (request.POST['action'] == "edit") and (type_id != orig_type_id)
        if 'save' in request.POST:
            # Check existence of type to save according to action performed
            if (request.POST['action'] in ["new", "copy"]) or type_id_changed:
                if RecordType.exists(coll, type_id):
                    form_data = context_from_record_type_form(
                        self.site_data(), coll_id, request.POST,
                        error_head=message.RECORD_TYPE_ID,
                        error_message=message.RECORD_TYPE_EXISTS%(type_id, coll_id)
                        )
                    return (
                        self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                        self.error(self.error406values())
                        )
            else:
                if not RecordType.exists(coll, type_id):
                    # This shouldn't happen, but just incase...
                    form_data = context_from_record_type_form(
                        self.site_data(), coll_id, request.POST,
                        error_head=message.RECORD_TYPE_ID,
                        error_message=message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
                        )
                    return (
                        self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                        self.error(self.error406values())
                        )
            # Create/update record type now
            RecordType.create(coll, type_id,
                { 'rdfs:label':   request.POST['type_label']
                , 'rdfs:comment': request.POST['type_help']
                , 'annal:uri':    request.POST['type_class']
                })
            # Remove old type if rename
            if type_id_changed:
                if RecordType.exists(coll, type_id):    # Precautionary
                    RecordType.remove(coll, orig_type_id)
            return HttpResponseRedirect(request.POST['continuation_uri'])
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        return HttpResponseRedirect(request.POST['continuation_uri']+err_values)

class RecordTypeDeleteConfirmedView(AnnalistGenericView):
    """
    View class to perform completion of confirmed record type deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordTypeDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record type from a collection
        """
        log.debug("RecordTypeDeleteConfirmedView.post: %r"%(request.POST))
        if "type_delete" in request.POST:
            auth_required = self.authorize("DELETE")
            if auth_required:
                return auth_required
            coll    = self.collection(coll_id)
            type_id = request.POST['typelist']
            err     = coll.remove_type(type_id)
            if err:
                return self.redirect_error(
                    self.view_uri("AnnalistCollectionEditView", coll_id=coll_id), 
                    str(err))
            return self.redirect_info(
                    self.view_uri("AnnalistCollectionEditView", coll_id=coll_id), 
                    message.RECORD_TYPE_REMOVED%(type_id, coll_id)
                    )
        return self.error(self.error400values())

# End.
