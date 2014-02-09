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

class Collection_Types(Entity):

    _entitytype = ANNAL.CURIE.Collection_Types
    _entityfile = None
    _entityref  = None

class Collection_Views(Entity):

    _entitytype = ANNAL.CURIE.Collection_Views
    _entityfile = None
    _entityref  = None

class Collection_Lists(Entity):

    _entitytype = ANNAL.CURIE.Collection_Lists
    _entityfile = None
    _entityref  = None

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
        self._types = Collection_Types(self, "types")
        self._views = Collection_Views(self, "views")
        self._lists = Collection_Lists(self, "lists")
        return

    def types(self):
        """
        Generator enumerates and returns record types that may be stored
        """
        for f in self:
            t = RecordType.load(self, f)
            if t:
                yield t
        return

    def add_type(self, type_id, type_meta):
        """
        Add a new record type to the current collection

        type_id     identifier for the new type, as a string
                    with a form that is valid as URI path segment.
        type_meta   a dictionary providing additional information about
                    the type to be created.

        returns a RecordType object for the newly created type.
        """
        t = RecordType.create(self._types, type_id, type_meta)
        return t

    def get_type(self, type_id):
        """
        Retrieve identified type description

        type_id     local identifier for the type to retrieve.

        returns a RecordType object for the newly created type, or None.
        """
        t = RecordType.load(self._types, type_id)
        return t

    def remove_type(self, type_id):
        """
        Remove identified type description

        type_id     local identifier for the type to remove.

        Returns a non-False status code if the type is not removed.
        """
        t = RecordType.remove(self._types, type_id)
        return t

    # @@TODO:
    #   views
    #   add_view
    #   get_view
    #   remove_view
    #   lists
    #   add_list
    #   get_list
    #   remove_list



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
