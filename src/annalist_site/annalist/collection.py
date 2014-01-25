"""
Annalist collection
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
    def collections(site):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        site            Site object containing collections to enumerate.
        """
        site_files   = os.listdir(site._basedir)
        for f in site_files:
            p = util.entity_path(site._basedir, [f, layout.COLL_META_DIR], layout.COLL_META_FILE)
            d = util.read_entity(p)
            if d:
                d["id"]    = f
                d["uri"]   = urlparse.urljoin(site._baseuri, f)
                d["title"] = d.get("rdfs:label", "Collection "+f)
                yield d
        return

    @staticmethod
    def exists(coll_id, site):
        """
        Method tests for existence of identified collection in site.

        site            Site object containing collections to test.

        Returns True if the collection exists, as determined by existence of the 
        collection description metadata file.
        """
        log.info("Colllection.exists: id %s"%(coll_id))
        p = util.entity_path(site._basedir, [coll_id, layout.COLL_META_DIR], layout.COLL_META_FILE)
        return (p != None) and os.path.isfile(p)

    @staticmethod
    def create(coll_id, coll_meta, site):
        """
        Method creates a new collection in a site, saving its details to disk

        coll_id         identifier for new collection
        coll_meta       description metadata about the new collection
        site            Site object that will hold the created collection.
        """
        log.info("Colllection.create: id %s, meta %r"%(coll_id, coll_meta))
        c = Collection(coll_id, site)
        c.set_values(coll_meta)
        c.save()
        return c

    @staticmethod
    def remove(coll_id, site):
        """
        Method removes a collection, deleting its details and data from disk

        coll_id     the collection identifier of the collection
        site        Site object for site where collection currently resides

        Returns None on sucess, of a status value indicating a reason for value.
        """
        log.info("Colllection.remove: id %s"%(coll_id))
        if Collection.exists(coll_id, site):
            c = Collection(coll_id, site)
            d = c._basedir
            if d.startswith(site._basedir):
                shutil.rmtree(d)
            else:
                raise Annalist_Error("Collection %s unexpected base dir %s"%(coll_id, d))
        else:
            return Annalist_Error("Collection %s not found"%(coll_id))
        return None

    def __init__(self, coll_id, site):
        """
        Initialize a new Collection object.  A collectiion Id and values must be 
        set before the collection can be used.

        coll_id     the collection identifier for the collection
        site        Site object in which holds the collection
        """
        if not util.valid_id(coll_id):
            raise ValueError("Invalid colllection identifier: %s"%(coll_id))
        baseuri = site._baseuri+coll_id
        basedir = site._basedir+coll_id
        self._baseuri = baseuri if baseuri.endswith("/") else baseuri+"/"
        self._basedir = basedir if basedir.endswith("/") else basedir+"/"
        self._id      = coll_id
        self._values  = None
        log.info("Colllection.__init__: base URI %s, base dir %s"%(self._baseuri, self._basedir))
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
