"""
Annalist record type views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import util

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType

from annalist.views.generic         import AnnalistGenericView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView

class RecordTypeEditView(EntityEditBaseView):
    """
    View class to handle requests to an Annalist record type edit URI
    """

    entityclass        = RecordType

    _entityformtemplate = 'annalist_recordtype_edit.html'
    _entityvaluemap     = (
        [ SimpleValueMap(c='title',            e=None,           f=None               )
        , SimpleValueMap(c='coll_id',          e=None,           f=None               )
        , StableValueMap(c='type_id',          e='annal:id',     f='type_id'          )
        , StableValueMap(c=None,               e='annal:type',   f=None               )
        , SimpleValueMap(c='type_label',       e='rdfs:label',   f='type_label'       )
        , SimpleValueMap(c='type_help',        e='rdfs:comment', f='type_help'        )
        , SimpleValueMap(c='type_uri',         e='annal:uri',    f='type_class'       )
        # Form and interaction control (hidden fields)
        , SimpleValueMap(c='orig_id',          e=None,           f='orig_id'   )
        , SimpleValueMap(c='action',           e=None,           f='action'           )
        , SimpleValueMap(c='continuation_uri', e=None,           f='continuation_uri' )
        ])

    def __init__(self):
        super(RecordTypeEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing a type.
        """
        # @@TODO: replace by data-driven generic form => eliminate this module
        # Check collection
        http_response = (
            self.get_coll_data(coll_id, host=self.get_request_host()) or
            self.form_edit_auth(action, self.collection._entityuri) or
            self.get_type_data("_type")
            )
        if http_response:
            return http_response
        # Set up RecordType-specific values
        type_id              = self.get_entityid(action, self.collection, type_id)
        initial_type_values  = (
            { "rdfs:label":   message.RECORD_TYPE_LABEL%(type_id, coll_id)
            , "rdfs:comment": ""
            })
        context_extra_values = (
            { 'coll_id':    coll_id
            , 'orig_id':    type_id
            })
        return self.form_render(request,
            action, self.collection, type_id, 
            initial_type_values, 
            context_extra_values
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, action=None):
        """
        Handle response to record type edit form
        """
        log.debug("views.recordtype.post %s"%(self.get_request_path()))
        # log.info("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.info("  form data %r"%(request.POST))
        type_id              = request.POST.get('type_id', None)
        orig_type_id         = request.POST.get('orig_id', None)
        collection_edit_uri  = self.view_uri('AnnalistCollectionEditView', coll_id=coll_id)
        continuation_uri     = request.POST.get('continuation_uri', collection_edit_uri)
        http_response = self.get_coll_data(coll_id, self.get_request_host())
        if http_response:
            return http_response
        context_extra_values = (
            { 'coll_id':          coll_id
            , 'continuation_uri': continuation_uri
            })
        message_vals = {'id': type_id, 'type_id': "_type", 'coll_id': coll_id}
        messages = (
            { 'parent_heading':    message.COLLECTION_ID
            , 'parent_missing':    message.COLLECTION_NOT_EXISTS%message_vals
            , 'entity_heading':    message.RECORD_TYPE_ID
            , 'entity_invalid_id': message.RECORD_TYPE_ID_INVALID
            , 'entity_exists':     message.RECORD_TYPE_EXISTS%message_vals
            , 'entity_not_exists': message.RECORD_TYPE_NOT_EXISTS%message_vals
            })
        return self.form_response(
            request, action, self.collection, 
            type_id, orig_type_id, 
            coll_id, coll_id,
            messages, context_extra_values
            )


class RecordTypeDeleteConfirmedView(EntityDeleteConfirmedBaseView):
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
            http_response = (
                self.get_coll_data(coll_id, self.get_request_host()) or
                self.form_edit_auth("delete", self.collection.get_uri())
                )
            if http_response:
                return http_response
            type_id   = request.POST['typelist']
            message_vals = {'id': type_id, 'coll_id': coll_id}
            messages  = (
                { 'entity_removed': message.RECORD_TYPE_REMOVED%message_vals
                })
            continuation_uri = self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.confirm_form_respose(
                request, type_id, 
                self.collection.remove_type, messages, continuation_uri
                )
        return self.error(self.error400values())

# End.
