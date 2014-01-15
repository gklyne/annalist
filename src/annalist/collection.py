"""
Annalist collection
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist               import util

# from annalist.recordtype    import RecordType
from annalist.views         import AnnalistGenericView

class Collection(object):

    @static
    def create(cls, coll_id, coll_meta, sitebaseuri, sitebasedir):
        """
        Class method creates a new collection, saving its details to disk
        """
        baseuri = sitebaseuri+coll_id
        basedir = sitebasedir+coll_id
        c = Collection(baseuri, basedir)
        c.set_id(coll_id)
        c.set_values(coll_meta)
        c.save()
        return c

    def __init__(self, baseuri, basedir):
        """
        Initialize a Collection object

        baseuri     the base URI of the site
        basedir     the base dictionary for site information
        coll_meta   a dictionary providing additional metadata about the collection
        """
        self._baseuri = baseuri if baseuri.endswith("/") else baseuri+"/"
        self._basedir = basedir if basedir.endswith("/") else basedir+"/"
        self._id      = util.slug_from_uri(self._baseuri[:-1])
        self._values  = {}
        return

    def set_id(self, coll_id):
        """
        Set or update identifier (slug) for a collection
        """
        if not util.valid_id(coll_id):
            raise ValueError("Invalid colllection identifier: %s"%(coll_id))
        self._id = coll_id
        return

    def get_id(self):
        return self._id

    def set_values(self, values):
        """
        Set or update values for a collection
        """
        self._values = values
        return

    def get_values(self):
        return self._values.copy().update({ '_id': self._id })

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

class CollectionView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection URI
    """
    def __init__(self):
        super(CollectionView, self).__init__()
        return

    # GET

    def get(self, request):
        """
        Create a rendering of the current collection.
        """
        def resultdata():
            coll = Collection(self.get_request_uri(), self.get_base_dir())
            return coll.get_values()
        return (
            self.render_html(resultdata(), 'annalist_collection.html') or 
            self.error(self.error406values())
            )

# End.
