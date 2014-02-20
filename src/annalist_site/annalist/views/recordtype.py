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

from django.conf import settings

# from annalist                   import layout
from annalist                   import message
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import RDF, RDFS, ANNAL
# from annalist                   import util
# from annalist.entity            import Entity

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

from annalist.views             import AnnalistGenericView

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
        def resultdata():
            recordtype_local_uri     = typedesc.get_uri(self.get_request_uri())
            context = (
                { 'title':              self.site_data()["title"]
                , 'coll_id':            coll_id
                , 'type_id':            typedesc.get_id()
                , 'type_label':         typedesc.get(RDFS.CURIE.label, default_type_label)
                , 'type_help':          typedesc.get(RDFS.CURIE.comment, "")
                , 'type_uri':           typedesc.get(ANNAL.CURIE.uri, recordtype_local_uri)
                , 'orig_type_id':       typedesc.get_id()
                , 'continuation_uri':   request.GET.get('continuation_uri', None)
                , 'action':             action
                })
            return context
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        coll = Collection(self.site(), coll_id)
        if action == "new":
            type_id     = RecordType.allocate_new_id(coll)
        default_type_label = "Record type %s in collection %s"%(type_id, coll_id)
        if action == "new":
            typedesc    = RecordType(coll, type_id)
            typedesc.set_values(
                { "annal:id": type_id
                , "annal:type": "annal:RecordType"
                , "annal:uri": coll._entityuri+type_id+"/"
                , "rdfs:label": default_type_label
                , "rdfs:comment": ""
                })
        elif RecordType.exists(coll, type_id):
            typedesc = RecordType.load(coll, type_id)
        else:
            return self.error(
                dict(self.error404values(), 
                    message=message.DOES_NOT_EXIST%(default_type_label)
                    )
                )
        return (
            self.render_html(resultdata(), 'annalist_recordtype_edit.html') or 
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
        if request.POST['cancel'] == "Cancel":
            return HttpResponseRedirect(request.POST['continuation_uri'])

        coll = self.collection(coll_id)
        if request.POST['save'] == "Save":
            if request.POST['action'] in ["new", "copy"]:
                if RecordType.exists(coll, type_id):
                    form_data = request.POST.copy()
                    form_data['error_head']    = message.RECORD_TYPE_ID
                    form_data['error_message'] = message.RECORD_TYPE_EXISTS%(type_id, coll_id)
                    return (
                        self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                        self.error(self.error406values())
                        )
                RecordType.create(coll, type_id,
                    { 
                    , 'rdfs:label':   request.POST['type_label']
                    , 'rdfs:comment': request.POST['type_help']
                    , 'annal:uri':    request.POST['type_class']
                    })
                return HttpResponseRedirect(request.POST['continuation_uri'])
            if request.POST['action'] == "edit":
                if request.POST['type_id'] != request.POST['orig_type_id']:
                    if RecordType.exists(coll, type_id):
                        form_data = request.POST.copy()
                        form_data['error_head']    = message.RECORD_TYPE_ID
                        form_data['error_message'] = message.RECORD_TYPE_EXISTS%(type_id, coll_id)
                        return (
                            self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                            self.error(self.error406values())
                            )
                    RecordType.create(coll, type_id,
                        { 
                        , 'rdfs:label':   request.POST['type_label']
                        , 'rdfs:comment': request.POST['type_help']
                        , 'annal:uri':    request.POST['type_class']
                        })
                    RecordType.delete(coll, orig_type_id,                   
                    return HttpResponseRedirect(request.POST['continuation_uri'])
                else:
                    if not RecordType.exists(coll, type_id):
                        # This shouldn't happen, but just incase...
                        form_data = request.POST.copy()
                        form_data['error_head']    = message.RECORD_TYPE_ID
                        form_data['error_message'] = message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
                        return (
                            self.render_html(form_data, 'annalist_recordtype_edit.html') or 
                            self.error(self.error406values())
                            )
                RecordType.create(coll, type_id,
                    { 
                    , 'rdfs:label':   request.POST['type_label']
                    , 'rdfs:comment': request.POST['type_help']
                    , 'annal:uri':    request.POST['type_class']
                    })
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
