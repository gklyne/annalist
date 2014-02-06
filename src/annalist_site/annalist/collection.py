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

from annalist               import util
from annalist               import layout
from annalist.exceptions    import Annalist_Error
from annalist.identifiers   import ANNAL

# from annalist.recordtype    import RecordType
# from annalist.views         import AnnalistGenericView

class Collection(object):

    # @@TODO: currently association of a collection with a site is by physical location
    #         which means a collection cannot exist in more than one site.  Later developments
    #         may want to review this.

    @staticmethod
    def create(coll_id, coll_meta, baseuri, basedir):
        """
        Method creates a new collection in a site, saving its details to disk

        coll_id     identifier for new collection
        coll_meta   description metadata about the new collection
        baseuri     is the base URI from which the collection is accessed
        basedir     is the base directory containing the subdirectory containing
                    the collection data
        """
        log.debug("Colllection.create: id %s, meta %r"%(coll_id, coll_meta))
        c = Collection(coll_id, baseuri, basedir)
        c.set_values(coll_meta)
        c.save()
        return c

    @staticmethod
    def load(colldir, baseuri, basedir):
        """
        Return a collection at a location specified by a base directory and subdirectory,
        or None if there is not collection there.

        colldir     is the name of the subdirectory containing the collection data
        baseuri     is the base URI from which the collection is accessed
        basedir     is the base directory containing the subdirectory containing
                    the collection data
        """
        p = util.entity_path(basedir, [colldir, layout.COLL_META_DIR], layout.COLL_META_FILE)
        d = util.read_entity(p)
        if d:
            # @@TODO do we really want this ad hoc stuff in addition to the saved metadata?
            d["id"]    = colldir
            d["uri"]   = urlparse.urljoin(baseuri, colldir)
            d["title"] = d.get("rdfs:label", "Collection "+colldir)
            c = Collection(colldir, baseuri, basedir)
            c.set_values(d)
            return c
        return None

    @staticmethod
    def exists(coll_id, basedir):
        """
        Method tests for existence of identified collection in a given base directory.

        coll_id     is the collection identifier whose exostence is tested
        basedir     is the base directory containing the subdirectory containing
                    the collection data

        Returns True if the collection exists, as determined by existence of the 
        collection description metadata file.
        """
        log.debug("Collection.exists: id %s"%(coll_id))
        p = util.entity_path(basedir, [coll_id, layout.COLL_META_DIR], layout.COLL_META_FILE)
        return (p != None) and os.path.isfile(p)

    @staticmethod
    def remove(coll_id, basedir):
        """
        Method removes a collection, deleting its details and data from disk

        coll_id     the collection identifier of the collection
        basedir     is the base directory containing the subdirectory containing
                    the collection data

        Returns None on sucess, of a status value indicating a reason for value.
        """
        log.debug("Colllection.remove: id %s"%(coll_id))
        if Collection.exists(coll_id, basedir):
            d = os.path.join(basedir, coll_id)
            if d.startswith(basedir):   # Double check...
                shutil.rmtree(d)
            else:
                raise Annalist_Error("Collection %s unexpected base dir %s"%(coll_id, d))
        else:
            return Annalist_Error("Collection %s not found"%(coll_id))
        return None

    def __init__(self, coll_id, baseuri, basedir):
        """
        Initialize a new Collection object.  A collectiion Id and values must be 
        set before the collection can be used.

        coll_id     the collection identifier for the collection
        baseuri     is the base URI from which the collection is accessed
        basedir     is the base directory containing the subdirectory containing
                    the collection data
        """
        if not util.valid_id(coll_id):
            raise ValueError("Invalid colllection identifier: %s"%(coll_id))
        self._id      = coll_id
        self._baseuri = baseuri + coll_id + "/"
        self._basedir = basedir + coll_id + "/"
        self._values  = None
        log.debug("Collection.__init__: base URI %s, base dir %s"%(self._baseuri, self._basedir))
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
        """
        Return collection metadata values
        """
        return self._values

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._values.items()

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._values[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._values[k] = v

    def save(self):
        if not self._id:
            raise ValueError("Collection.save without defined collection id")
        if not self._values:
            raise ValueError("Collection.save without defined collection metadata")
        (coll_meta_dir,coll_meta_file) = util.entity_dir_path(
            self._basedir, layout.COLL_META_DIR, layout.COLL_META_FILE)
        util.ensure_dir(coll_meta_dir)
        util.write_entity(coll_meta_file, "../", self._values, 
            entityid=self._id, entitytype=ANNAL.CURIE.Collection)
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
