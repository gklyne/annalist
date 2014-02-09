"""
Annalist collection

A collection is represented by:
- an ID (slug)
- a URI
- a name/label
- a description
- a set of record types
- a set of list views
- a set of record views
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

# from annalist.recordtype    import RecordType
# from annalist.views         import AnnalistGenericView

class Collection(Entity):

    _entitytype = ANNAL.CURIE.Collection
    _entityfile = layout.COLL_META_FILE
    _entityref  = layout.META_COLL_REF

    def __init__(self, parent, coll_id):
        """
        Initialize a new Collection object, without metadta (yet).

        parent      is the parent site from which the new collection is descended.
        coll_id     the collection identifier for the collection
        """
        super(Collection, self).__init__(parent, coll_id)
        return

    # @@TODO...
    def record_types(self):
        """
        Generator enumerates and returns record types that may be stored
        """
        type_dir = os.path.join(self._basedir, settings.COLL_TYPES_DIR)
        if os.path.isdir(type_dir):
            try_types = os.listdir(type_dir)
        else:
            try_types = []
        for type_fil in try_types:
            type_id = util.slug_from_name(type_fil)
            t = os.path.join(type_dir, typ)
            # if os.path.isfile(t):
            #     with open(t, "r") as tf:
            #         type_meta = json.load(tf)
            #     yield RecordType(type_id, type_meta, self._baseuri, self._basedir)
            raise "@@TODO"
        return

    # def add_type(self, type_id, type_meta):
    #     """
    #     Add a new record type to the current collection

    #     type_id     identifier for the new type, as a string
    #                 with a form that is valid as URI path segment.
    #     type_meta   a dictionary providing additional information about
    #                 the type to be created.

    #     returns a Collection object for the newly created collection.
    #     """
    #     c = RecordType.create(type_id, type_meta, self._baseuri, self._basedir)
    #     #@@@ create type description
    #     return c

# class CollectionView(AnnalistGenericView):
#     """
#     View class to handle requests to an Annalist collection URI
#     """
#     def __init__(self):
#         super(CollectionView, self).__init__()
#         return

#     # GET

#     def get(self, request):
#         """
#         Create a rendering of the current collection.
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
