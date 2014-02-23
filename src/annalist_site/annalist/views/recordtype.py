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

from annalist.site                  import Site
from annalist.collection            import Collection
from annalist.recordtype            import RecordType

from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityValueMap, EntityEditBaseView, EntityDeleteConfirmedBaseView


class RecordTypeEditView(EntityEditBaseView):
    """
    View class to handle requests to an Annalist record type edit URI
    """

    _entityclass        = RecordType
    _entityformtemplate = 'annalist_recordtype_edit.html'
    _entityvaluemap     = (
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='type_id',          f='type_id'          )
        # Normal fields
        , EntityValueMap(e=None,          v='annal:type',   c=None,               f=None               )
        , EntityValueMap(e='rdfs:label',  v='rdfs:label',   c='type_label',       f='type_label'       )
        , EntityValueMap(e='rdfs:comment',v='rdfs:comment', c='type_help',        f='type_help'        )
        , EntityValueMap(e='annal:uri',   v='annal:uri',    c='type_uri',         f='type_class'       )
        # Form and interaction control
        , EntityValueMap(e=None,          v=None,           c='orig_type_id',     f='orig_type_id'     )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(RecordTypeEditView, self).__init__()
        return

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
            coll      = self.collection(coll_id)
            type_id   = request.POST['typelist']
            messages  = (
                { 'entity_removed': message.RECORD_TYPE_REMOVED%(type_id, coll_id)
                })
            continuation_uri = self.view_uri("AnnalistCollectionEditView", coll_id=coll_id)
            return self.confirm_form_respose(request, coll, type_id, coll.remove_type, messages, continuation_uri)
        return self.error(self.error400values())

# End.
