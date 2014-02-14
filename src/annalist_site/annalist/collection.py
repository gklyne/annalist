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

from annalist.recordtype        import RecordType
from annalist.recordview        import RecordView
from annalist.recordlist        import RecordList

from annalist.views         import AnnalistGenericView

class Collection_Types(Entity):

    _entitytype = ANNAL.CURIE.Collection_Types
    _entityfile = layout.TYPES_META_FILE
    _entityref  = layout.META_TYPES_REF

class Collection_Views(Entity):

    _entitytype = ANNAL.CURIE.Collection_Views
    _entityfile = layout.VIEWS_META_FILE
    _entityref  = layout.META_VIEWS_REF

class Collection_Lists(Entity):

    _entitytype = ANNAL.CURIE.Collection_Lists
    _entityfile = layout.LISTS_META_FILE
    _entityref  = layout.META_LISTS_REF

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
        self._types = Collection_Types.create(self, "types", 
            { 'rdfs:label':   "Record types for collection %s"%(coll_id)
            , 'rdfs:comment': "Record types for collection %s"%(coll_id)
            })
        self._views = Collection_Views.create(self, "views",
            { 'rdfs:label':   "Record views for collection %s"%(coll_id)
            , 'rdfs:comment': "Record views for collection %s"%(coll_id)
            })
        self._lists = Collection_Lists.create(self, "lists",
            { 'rdfs:label':   "Record list views for collection %s"%(coll_id)
            , 'rdfs:comment': "Record list views for collection %s"%(coll_id)
            })
        return

    # Record types

    def types(self):
        """
        Generator enumerates and returns record types that may be stored
        """
        for f in self._types:
            t = RecordType.load(self._types, f)
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

        returns a RecordType object for the identified type, or None.
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

    # Record views

    def views(self):
        """
        Generator enumerates and returns record views that may be stored
        """
        for f in self._views:
            t = RecordView.load(self._views, f)
            if t:
                yield t
        return

    def add_view(self, view_id, view_meta):
        """
        Add a new record view to the current collection

        view_id     identifier for the new view, as a string
                    with a form that is valid as URI path segment.
        view_meta   a dictionary providing additional information about
                    the view to be created.

        returns a RecordView object for the newly created view.
        """
        t = RecordView.create(self._views, view_id, view_meta)
        return t

    def get_view(self, view_id):
        """
        Retrieve identified view description

        view_id     local identifier for the view to retrieve.

        returns a RecordView object for the identified view, or None.
        """
        t = RecordView.load(self._views, view_id)
        return t

    def remove_view(self, view_id):
        """
        Remove identified view description

        view_id     local identifier for the view to remove.

        Returns a non-False status code if the view is not removed.
        """
        t = RecordView.remove(self._views, view_id)
        return t

    # Record lists

    def lists(self):
        """
        Generator enumerates and returns record lists that may be stored
        """
        for f in self._lists:
            t = RecordList.load(self._lists, f)
            if t:
                yield t
        return

    def add_list(self, list_id, list_meta):
        """
        Add a new record list to the current collection

        list_id     identifier for the new list, as a string
                    with a form that is valid as URI path segment.
        list_meta   a dictionary providing additional information about
                    the list to be created.

        returns a RecordList object for the newly created list.
        """
        t = RecordList.create(self._lists, list_id, list_meta)
        return t

    def get_list(self, list_id):
        """
        Retrieve identified list description

        list_id     local identifier for the list to retrieve.

        returns a RecordList object for the identified list, or None.
        """
        t = RecordList.load(self._lists, list_id)
        return t

    def remove_list(self, list_id):
        """
        Remove identified list description

        list_id     local identifier for the list to remove.

        Returns a non-False status code if the list is not removed.
        """
        t = RecordList.remove(self._lists, list_id)
        return t

class CollectionEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection edit URI
    """
    def __init__(self):
        super(CollectionEditView, self).__init__()
        self._site      = Site(self._sitebaseuri, self._sitebasedir)
        self._site_data = None
        return

    # GET

    def get(self, request, coll_id):
        """
        Create a rendering of the current collection.
        """
        def resultdata():
            coll = Collection(self._site, coll_id)
            context = (
                { 'coll_id':    coll_id
                , 'types':      sorted(coll.types())
                , 'lists':      sorted(coll.lists())
                , 'views':      sorted(coll.views())
                })
            return coll.get_values()
        if not Collection.exists(self._site, coll_id):
            return self.error(self.error404values().update(
                message="Collection %s does not exist"%(coll_id)))
        return (
            self.render_html(resultdata(), 'annalist_collection_edit.html') or 
            self.error(self.error406values())
            )

#     # POST

#     # DELETE

# End.
