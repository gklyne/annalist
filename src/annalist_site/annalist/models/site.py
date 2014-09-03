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

from annalist.identifiers       import ANNAL, RDFS
from annalist.exceptions        import Annalist_Error, EntityNotFound_Error
from annalist                   import layout
from annalist                   import message

from annalist.models.entityroot import EntityRoot
from annalist.models.sitedata   import SiteData
from annalist.models.collection import Collection
from annalist                   import util

class Site(EntityRoot):

    _entitytype     = ANNAL.CURIE.Site
    _entitytypeid   = "_site"
    _entityfile     = layout.SITE_META_FILE
    _entityref      = layout.META_SITE_REF

    def __init__(self, sitebaseuri, sitebasedir, host=""):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base directory for site information
        """
        log.debug("Site init: %s"%(sitebasedir))
        super(Site, self).__init__(host+sitebaseuri, sitebasedir)
        self._sitedata = SiteData(self)
        return

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        Yielded values are collection objects.
        """
        log.debug("site.collections: basedir: %s"%(self._entitydir))
        for f in self._children(Collection):
            c = Collection.load(self, f)
            # log.info("Site.colections: Collection.load %s %r"%(f, c.get_values()))
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
        # @@TODO: consider using generic view logic for this mapping (and elsewhere?)
        #         This is currently a bit of a kludge, designed to match the site
        #         view template.  In due course, it may be reveiwed and implemented
        #         using the generic Annalist form generating framework
        site_data = self._load_values()
        if not site_data:
            return None
        site_data["title"] = site_data.get(RDFS.CURIE.label, message.SITE_NAME_DEFAULT)
        # log.info("site.site_data: site_data %r"%(site_data))
        colls = collections.OrderedDict()
        for k, v in self.collections_dict().items():
            # log.info("site.site_data: colls[%s] %r"%(k, v))
            colls[k] = dict(v.items(), id=k, url=v[ANNAL.CURIE.url], title=v[RDFS.CURIE.label])
        site_data["collections"] = colls
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
