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
# from annalist.identifiers       import ANNAL
# from annalist                   import util
# from annalist.entity            import Entity

from annalist.site              import Site
from annalist.collection        import Collection
from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

from annalist.views             import AnnalistGenericView

class TypeEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist type edit URI
    """
    def __init__(self):
        super(TypeEditView, self).__init__()
        return

    # GET

    def get(self, request, coll_id=None, type_id=None, action=None):
        """
        Create a form for editing a type.
        """
        def resultdata():
            context = (
                { 'title':          self.site_data()["title"]
                , 'coll_id':        coll_id
                , 'type_id':        type_id
                # @@TODO
                })
            return context
        if not Collection.exists(self.site(), coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        coll     = Collection(self.site(), coll_id)
        if action == "new":
            typedesc = RecordType(coll, "<new>")
        elif not RecordType.exists(coll, type_id):
            return self.error(self.error404values().update(
                message="Record type %s/%s does not exist"%(coll_id, type_id)))
            typedesc = RecordType.load(coll, type_id)
        return (
            self.render_html(resultdata(), 'annalist_type_edit.html') or 
            self.error(self.error406values())
            )

#     # POST

#     # DELETE

# End.
