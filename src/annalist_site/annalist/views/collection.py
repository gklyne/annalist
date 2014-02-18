"""
Annalist collection views
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
from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import resolve, reverse

# from annalist                   import layout
from annalist                   import message
from annalist.exceptions        import Annalist_Error
# from annalist.identifiers       import ANNAL
# from annalist                   import util
# from annalist.entity            import Entity

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

from annalist.views             import AnnalistGenericView

class CollectionEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection edit URI
    """
    def __init__(self):
        super(CollectionEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id):
        """
        Create a rendering of the current collection.
        """
        def resultdata():
            coll = Collection(self.site(), coll_id)
            context = (
                { 'title':          self.site_data()["title"]
                , 'coll_id':        coll_id
                , 'types':          sorted( [t.get_id() for t in coll.types()] )
                , 'lists':          sorted( [l.get_id() for l in coll.lists()] )
                , 'views':          sorted( [v.get_id() for v in coll.views()] )
                , 'select_rows':    "6"
                })
            return context
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        return (
            self.render_html(resultdata(), 'annalist_collection_edit.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id):
        """
        Update some aspect of the current collection
        """
        redirect_uri = None
        type_id = request.POST.get('typelist', None)
        if "type_new" in request.POST:
            redirect_uri = reverse(
                "AnnalistTypeNewView", 
                kwargs={'coll_id': coll_id, 'action': "new"}
                )
        if "type_copy" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_COPY) or
                reverse("AnnalistTypeCopyView", 
                    kwargs={'coll_id': coll_id, 'type_id': type_id, 'action': "copy"})
                )
        if "type_edit" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_EDIT) or
                reverse("AnnalistTypeEditView", 
                    kwargs={'coll_id': coll_id, 'type_id': type_id, 'action': "edit"})
                )
        if "type_delete" in request.POST:
            redirect_uri = (
                self.check_value_supplied(type_id, message.NO_TYPE_FOR_DELETE) or
                reverse("AnnalistTypeDeleteView", 
                    kwargs={'coll_id': coll_id, 'type_id': type_id, 'action': "delete"})
                )
        if redirect_uri:
            return HttpResponseRedirect(redirect_uri)
        raise Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())

#     # DELETE

# End.
