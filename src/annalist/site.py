"""
Analist site-related facilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf import settings

import annalist.util

from utils.ContentNegotiationView import ContentNegotiationView
from annalist.views               import AnnalistGenericView

class Site(object):

    def __init__(self, sitebaseuri, sitebasedir):
        self._baseuri = sitebaseuri if sitebaseuri.endswith("/") else sitebaseuri+"/"
        self._basedir = sitebasedir if sitebasedir.endswith("/") else sitebasedir+"/"
        return

    def collections(self):
        """
        Generator enumerates and returns collections that are part of a site.
        """
        # @@TODO: more serious enumeration
        for c in ["foo", "bar"]:
            yield c
        return

    def collections_dict(self):
        """
        Return a dictionary of collection URIs indexed by collledtion id
        """
        coll = {}
        for c in self.collections():
            coll[c] = self._baseuri+c+"/"
        return coll

    def addCollection(self, coll_id, coll_meta):
        """
        Add a new collection to the current site

        coll_id     identifier for the new collection, as a string
                    with a form that is valid as URI path segment.
        coll_meta   a dictionary providing additional information about
                    the collection to be created.

        returns a Collection object for the newly created collection.
        """
        if not annalist.util.valid_id(coll_id):
            raise ValueError("Invalid colllection identifier: %s"%(coll_id))
        c = Collection.create(coll_id, coll_meta, self._baseuri, self._basedir)
        # @@TODO save copy for local cache?
        return c


class SiteView(AnnalistGenericView):
    """
    View class to handle requests to the annalist site home URI
    """
    def __init__(self):
        super(SiteView, self).__init__()
        return

    # GET

    def get(self, request):
        """
        Create a rendering of the current site home page, containing (among other things)
        a list of defined collections.
        """
        def resultdata():
            site = Site(self.get_request_uri(), settings.SITE_BASE)
            return { "collections":  site.collections_dict() }
        return (
            self.render_html(resultdata(), 'annalist_site.html') or 
            self.error(self.error406values())
            )

# End.
