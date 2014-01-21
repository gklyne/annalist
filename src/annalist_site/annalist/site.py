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

from django.conf              import settings
from django.core.urlresolvers import resolve, reverse

from annalist               import layout as site_layout
from annalist.collection    import Collection
from annalist.views         import AnnalistGenericView
from annalist.confirmview   import ConfirmView
from annalist.util          import read_data

class Site(object):

    def __init__(self, sitebaseuri, sitebasedir):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base dictionary for site information
        """
        log.info("Site init: %s"%(sitebasedir))
        self._baseuri = sitebaseuri if sitebaseuri.endswith("/") else sitebaseuri+"/"
        self._basedir = sitebasedir if sitebasedir.endswith("/") else sitebasedir+"/"
        return

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.
        """
        site_files   = os.listdir(self._basedir)
        for f in site_files:
            d = read_data(self._basedir, f, site_layout.COLL_META_DIR, site_layout.COLL_META_FILE)
            if d:
                d["id"]    = f
                d["uri"]   = urlparse.urljoin(self._baseuri, f)
                d["title"] = d.get("rdfs:label", "Collection "+f)
                yield d
        return

    def collections_dict(self):
        """
        Return a dictionary of collection URIs indexed by collection id
        """
        coll = collections.OrderedDict()
        for c in self.collections():
            coll[c["id"]] = c
        return coll

    def site_data(self):
        """
        Return dictionary of site data
        """
        site_data = read_data(self._basedir, [], site_layout.SITE_META_DIR, site_layout.SITE_META_FILE)
        site_data["title"]       = site_data.get("rdfs:label", "Annalist linked data journal")
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
        c = Collection.create(coll_id, coll_meta, self._baseuri, self._basedir)
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
            site = Site(self.get_request_uri(), os.path.join(settings.BASE_DATA_DIR, site_layout.SITE_DIR))
            return site.site_data()
        return (
            # self.authenticate() or 
            self.authorize("GET") or 
            self.render_html(resultdata(), 'annalist_site.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request):
        """
        Process options to add or remove a collection in an Annalist site
        """
        log.info("site.post: %r"%(request.POST))
        if request.POST.get("remove", None):
            collections = request.POST.getlist("select", [])
            log.info("collections: "+repr(collections))
            if collections:
                # Get user to confirm action before actually doing it
                return ConfirmView.render_form(request,
                    action_description= "Remove collections %s"%(", ".join(collections)),
                    action_params=      request.POST,
                    complete_action=    'AnnalistSiteActionView',
                    cancel_action=      'AnnalistSiteView'
                    )
            else:
                return HttpResponseRedirect(request.get_request_uri())
        if request.POST.get("new", None):
            # Create new collection with name and label supplied
            # @@TODO
            pass
        return self.error(self.error400values())

class SiteActionView(AnnalistGenericView):
    """
    View class to completion of confirmed action from site view
    """
    def __init__(self):
        super(SiteActionView, self).__init__()
        return

    # POST

    def post(self, request):
        """
        Process options to complete action to add or remove a collection
        """
        log.info("site.post: %r"%(request.POST))
        if request.POST.get("remove", None):
            log.info("Complete remove....")
            # @@TODO
        elif request.POST.get("new", None):
            log.info("Complete new....")
            # Create new collection with name and label supplied
            # @@TODO
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(reverse("AnnalistSiteView"))

# End.
