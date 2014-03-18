"""
Annalist record view description views

@@TODO: currently just a placeholder module
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
from annalist.models.recordview     import RecordView

from annalist.views.generic         import AnnalistGenericView
from annalist.views.simplevaluemap  import SimpleValueMap, StableValueMap
from annalist.views.entityeditbase  import EntityEditBaseView, EntityDeleteConfirmedBaseView


class RecordViewEditView(EntityEditBaseView):
    """
    View class to handle requests to an Annalist record type edit URI
    """

    _entityclass        = RecordView
    _entityformtemplate = 'annalist_recordview_edit.html'
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
        super(RecordViewEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing a type.
        """
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(
                dict(self.error404values(),
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        coll = Collection(self.site(), coll_id)
        # Set up RecordView-specific values
        type_id              = self.get_entityid(action, coll, type_id)
        initial_type_values  = (
            { "rdfs:label":   message.RECORD_TYPE_LABEL%(type_id, coll_id)
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

    def post(self, request, coll_id=None, type_id=None, action=None):
        """
        Handle response to record type edit form
        """
        log.debug("views.recordview.post %s"%(self.get_request_path()))
        # log.debug("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.debug("  form data %r"%(request.POST))
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


class RecordViewDeleteConfirmedView(EntityDeleteConfirmedBaseView):
    """
    View class to perform completion of confirmed record type deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(RecordViewDeleteConfirmedView, self).__init__()
        return

    # POST

    def post(self, request, coll_id):
        """
        Process options to complete action to remove a record type from a collection
        """
        log.debug("RecordViewDeleteConfirmedView.post: %r"%(request.POST))
        if "type_delete" in request.POST:
            coll      = self.collection(coll_id)
            type_id   = request.POST['typelist']
            messages  = (
                { 'entity_removed': message.RECORD_TYPE_REMOVED%(type_id, coll_id)
                })
            continuation_uri = self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.confirm_form_respose(request, coll, type_id, coll.remove_type, messages, continuation_uri)
        return self.error(self.error400values())

# End.
