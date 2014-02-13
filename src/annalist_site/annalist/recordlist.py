"""
Annalist record list

A record type is represented by:
- an ID (slug)
- a URI
- a name/label
- a description
- ...

@@TODO: currently just a placeholder class
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.entity            import Entity

# from annalist.views         import AnnalistGenericView

class RecordList(Entity):

    _entitytype = ANNAL.CURIE.RecordList
    _entityfile = layout.LIST_META_FILE
    _entityref  = layout.META_LIST_REF

    def __init__(self, parent, list_id):
        """
        Initialize a new RecordList object, without metadta (yet).

        parent      is the parent entity from which the list is descended.
        list_id     the local identifier for the record list
        """
        super(RecordList, self).__init__(parent, list_id)
        return

# class RecordListView(AnnalistGenericView):
#     """
#     View class to handle requests to an Annalist record list description URI
#     """
#     def __init__(self):
#         super(RecordListView, self).__init__()
#         return

#     # GET

#     def get(self, request):
#         """
#         Create a rendering of the current record list description.
#         """
#         def resultdata():
#             coll = Collection(self.get_request_uri(), self.get_base_dir())
#             return coll.get_values()
#         return (
#             self.render_html(resultdata(), 'annalist_collection.html') or 
#             self.error(self.error406values())
#             )

#     # POST

#     # DELETE

# End.
