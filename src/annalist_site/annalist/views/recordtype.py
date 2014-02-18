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
            recordtype_local_uri = typedesc.get_uri(self.get_request_uri())
            recordtype_default_label = "Record type %s in collection %s"%(type_id, coll_id)
            context = (
                { 'title':              self.site_data()["title"]
                , 'coll_id':            coll_id
                , 'continuation_uri':   request.GET.get('continuation_uri', None)
                , 'orig_type_id':       typedesc.get_id()
                , 'type_id':            typedesc.get_id()
                , 'type_label':         typedesc.get(RDFS.CURIE.label, recordtype_default_label)
                , 'type_help':          typedesc.get(RDFS.CURIE.comment, "")
                , 'type_uri':           typedesc.get(ANNAL.CURIE.uri, recordtype_local_uri)
                })
            return context
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        coll     = Collection(self.site(), coll_id)
        if action == "new":
            type_id  = RecordType.allocate_new_id(coll)
            typedesc = RecordType(coll, type_id)
            typedesc.set_values(
                { "annal:id": type_id
                , "annal:type": "annal:RecordType"
                , "annal:uri": coll._entityuri+type_id+"/"
                , "rdfs:label": "Type %s/%s"%(coll_id, type_id)
                , "rdfs:comment": ""
                })
        elif RecordType.exists(coll, type_id):
            typedesc = RecordType.load(coll, type_id)
        else:
            return self.error(self.error404values().update(
                message="Record type %s/%s does not exist"%(coll_id, type_id)))
        return (
            self.render_html(resultdata(), 'annalist_recordtype_edit.html') or 
            self.error(self.error406values())
            )

#     # POST

#     # DELETE

# End.
