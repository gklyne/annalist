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

from annalist.models.entity     import Entity
from annalist.models.recordtype import RecordType
from annalist.models.recordview import RecordView
from annalist.models.recordlist import RecordList

class Collection(Entity):

    _entitytype     = ANNAL.CURIE.Collection
    _entitytypeid   = "_collection"
    _entityview     = layout.SITE_COLL_VIEW
    _entitypath     = layout.SITE_COLL_PATH
    _entityfile     = layout.COLL_META_FILE
    _entityref      = layout.META_COLL_REF

    def __init__(self, parentsite, coll_id):
        """
        Initialize a new Collection object, without metadta (yet).

        parentsite  is the parent site from which the new collection is descended.
        coll_id     the collection identifier for the collection
        """
        super(Collection, self).__init__(parentsite, coll_id)
        self._parentsite = parentsite
        return

    # Site

    def get_site(self):
        """
        Return site object for the site from which the current collection is accessed.
        """
        return self._parentsite

    # Record types

    def types(self, include_alt=True):
        """
        Generator enumerates and returns record types that may be stored
        """
        altparent = self._parentsite if include_alt else None
        for f in self._children(RecordType, altparent=altparent):
            t = self.get_type(f)
            if t and t.get_id() != "_initial_values":
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
        t = RecordType.create(self, type_id, type_meta)
        return t

    def get_type(self, type_id):
        """
        Retrieve identified type description

        type_id     local identifier for the type to retrieve.

        returns a RecordType object for the identified type, or None.
        """
        t = RecordType.load(self, type_id, altparent=self._parentsite)
        return t

    def remove_type(self, type_id):
        """
        Remove identified type description

        type_id     local identifier for the type to remove.

        Returns a non-False status code if the type is not removed.
        """
        s = RecordType.remove(self, type_id)
        return s

    # Record views

    def views(self, include_alt=True):
        """
        Generator enumerates and returns record views that may be stored
        """
        altparent = self._parentsite if include_alt else None
        for f in self._children(RecordView, altparent=altparent):
            v = self.get_view(f)
            if v and v.get_id() != "_initial_values":
                yield v
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
        v = RecordView.create(self, view_id, view_meta)
        return v

    def get_view(self, view_id):
        """
        Retrieve identified view description

        view_id     local identifier for the view to retrieve.

        returns a RecordView object for the identified view, or None.
        """
        v = RecordView.load(self, view_id, altparent=self._parentsite)
        return v

    def remove_view(self, view_id):
        """
        Remove identified view description

        view_id     local identifier for the view to remove.

        Returns a non-False status code if the view is not removed.
        """
        s = RecordView.remove(self, view_id)
        return s

    # Record lists

    def lists(self, include_alt=True):
        """
        Generator enumerates and returns record lists that may be stored
        """
        altparent = self._parentsite if include_alt else None
        for f in self._children(RecordList, altparent=altparent):
            l = self.get_list(f)
            if l and l.get_id() != "_initial_values":
                yield l
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
        l = RecordList.create(self, list_id, list_meta)
        return l

    def get_list(self, list_id):
        """
        Retrieve identified list description

        list_id     local identifier for the list to retrieve.

        returns a RecordList object for the identified list, or None.
        """
        l = RecordList.load(self, list_id, altparent=self._parentsite)
        return l

    def remove_list(self, list_id):
        """
        Remove identified list description

        list_id     local identifier for the list to remove.

        Returns a non-False status code if the list is not removed.
        """
        s = RecordList.remove(self, list_id)
        return s

    def set_default_list(self, list_id):
        """
        Set and save the default list to be displayed for the current collection.
        """
        self["annal:default_list"] = list_id
        self._save()
        return

    def get_default_list(self):
        """
        Return the default list to be displayed for the current collection.
        """
        return self.get("annal:default_list", None)

# End.
