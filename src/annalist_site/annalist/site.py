"""
Analist site-related facilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import collections
import urlparse
import json
import traceback

import logging
log = logging.getLogger(__name__)

from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.conf                import settings
from django.core.urlresolvers   import resolve, reverse

from annalist.identifiers       import ANNAL
from annalist.exceptions        import Annalist_Error, EntityNotFound_Error
from annalist                   import layout
from annalist                   import message
from annalist.entity            import EntityRoot
from annalist.collection        import Collection
from annalist                   import util

class Site(EntityRoot):

    _entitytype = ANNAL.CURIE.Site
    _entityfile = layout.SITE_META_FILE
    _entityref  = layout.META_SITE_REF

    def __init__(self, sitebaseuri, sitebasedir):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base directory for site information
        """
        log.debug("Site init: %s"%(sitebasedir))
        super(Site, self).__init__(sitebaseuri, sitebasedir)
        return

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        Yielded values are collection objects.
        """
        log.debug("site.collections: basedir: %s"%(self._entitydir))
        for f in self._children(Collection):
            c = Collection.load(self, f)
            if c:
                yield c
        return

    def collections_dict(self):
        """
        Return an ordered dictionary of collection URIs indexed by collection id
        """
        coll = [ (c.get_id(), c) for c in self.collections() ]
        return collections.OrderedDict(sorted(coll))

    def site_data(self):
        """
        Return dictionary of site data
        """
        site_data = self._load_values()
        # @@TODO rationalize this ad-hoc value creation.
        #        cf. Entity.set_values()
        site_data["title"]       = site_data.get("rdfs:label", message.SITE_NAME_DEFAULT)
        site_data["collections"] = self.collections_dict()
        return site_data

    def add_collection(self, coll_id, coll_meta):
        """
        Add a new collection to the current site

        coll_id     identifier for the new collection, as a string
                    with a form that is valid as URI path segment.
        coll_meta   a dictionary providing additional information about
                    the collection to be created.

        returns a Collection object for the newly created collection.
        """
        c = Collection.create(self, coll_id, coll_meta)
        return c

    def remove_collection(self, coll_id):
        """
        Remove a collection from the site data.

        coll_id     identifier for the collection to remove.

        Returns a non-False status code if the collection is not removed.
        """
        log.debug("remove_collection: %s"%(coll_id))
        return Collection.remove(self, coll_id)

# End.
