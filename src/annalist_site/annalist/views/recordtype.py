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

# from annalist                   import layout
from annalist                   import message
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import util
# from annalist.entity            import Entity

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

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

class RecordTypeEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist record type edit URI
    """
    def __init__(self):
        super(RecordTypeEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing a type.
        """
        # Function to generate form data
        def form_context_data():
            recordtype_local_uri     = record_type.get_uri(self.get_request_uri())
            context = (
                { 'title':              self.site_data()["title"]
                , 'coll_id':            coll_id
                , 'type_id':            record_type.get_id()
                , 'type_label':         record_type.get(RDFS.CURIE.label, default_type_label)
                , 'type_help':          record_type.get(RDFS.CURIE.comment, "")
                , 'type_uri':           record_type.get(ANNAL.CURIE.uri, recordtype_local_uri)
                , 'orig_type_id':       record_type.get_id()
                , 'continuation_uri':   request.GET.get('continuation_uri', None)
                , 'action':             action
                })
            return context
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        coll = Collection(self.site(), coll_id)
        # Sort access mode, type_id and authorization
        if action == "new":
            type_id    = RecordType.allocate_new_id(coll)
            auth_scope = "CREATE"
        else:
            auth_scope = "UPDATE"
        auth_required = self.authorize(auth_scope)
        if auth_required:
                return auth_required
        default_type_label = "Record type %s in collection %s"%(type_id, coll_id)
        # Create local record type object or load values from existing
        if action == "new":
            record_type    = RecordType(coll, type_id)
            record_type.set_values(
                { "annal:id": type_id
                , "annal:type": "annal:RecordType"
                , "annal:uri": coll._entityuri+type_id+"/"
                , "rdfs:label": default_type_label
                , "rdfs:comment": ""
                })
        elif RecordType.exists(coll, type_id):
            record_type = RecordType.load(coll, type_id)
        else:
            return self.error(
                dict(self.error404values(), 
                    message=message.DOES_NOT_EXIST%(default_type_label)
                    )
                )
        return (
            self.render_html(form_context_data(), 'annalist_recordtype_edit.html') or 
            self.error(self.error406values())
            )

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

# End.
