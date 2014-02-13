"""
Annalist record view

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

class RecordView(Entity):

    _entitytype = ANNAL.CURIE.RecordView
    _entityfile = layout.VIEW_META_FILE
    _entityref  = layout.META_VIEW_REF

    def __init__(self, parent, view_id):
        """
        Initialize a new RecordView object, without metadta (yet).

        parent      is the parent entity from which the view is descended.
        view_id     the local identifier for the record view
        """
        super(RecordView, self).__init__(parent, view_id)
        return

# class RecordViewView(AnnalistGenericView):
#     """
#     View class to handle requests to an Annalist record view description URI
#     """
#     def __init__(self):
#         super(RecordViewView, self).__init__()
#         return

#     # GET

#     def get(self, request):
#         """
#         Create a rendering of the current record view description.
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
