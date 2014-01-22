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

from annalist               import message
from annalist               import layout as site_layout
from annalist.collection    import Collection
from annalist.views         import AnnalistGenericView
from annalist.confirmview   import ConfirmView
from annalist.util          import valid_id, read_data


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
        c = Collection.create(coll_id, coll_meta, self._baseuri, self._basedir)
        return c

class SiteView(AnnalistGenericView):
    """
    View class to handle requests to the annalist site home URI
    """
    def __init__(self):
        super(SiteView, self).__init__()
        return

    def site_data(self):
        site = Site(self.get_request_uri(), os.path.join(settings.BASE_DATA_DIR, site_layout.SITE_DIR))
        return site.site_data()

    # GET

    def get(self, request):
        """
        Create a rendering of the current site home page, containing (among other things)
        a list of defined collections.
        """
        return (
            # self.authenticate() or 
            self.authorize("GET") or 
            self.render_html(self.site_data(), 'annalist_site.html') or 
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
                    action_description= message.REMOVE_COLLECTIONS%(", ".join(collections)),
                    action_params=      request.POST,
                    complete_action=    'AnnalistSiteActionView',
                    cancel_action=      'AnnalistSiteView',
                    title=              self.site_data()["title"]
                    )
            else:
                return HttpResponseRedirect(request.get_request_uri())
        if request.POST.get("new", None):
            # Create new collection with name and label supplied
            new_id    = request.POST["new_id"]
            new_label = request.POST["new_label"]
            log.info("New collection %s: %s"%(new_id, new_label))
            if not new_id:
                return self.redirect_error("AnnalistSiteView", message.MISSING_COLLECTION_ID)
            if not valid_id(new_id):
                return self.redirect_error("AnnalistSiteView", message.INVALID_COLLECTION_ID%(new_id))
            # Create new collection with name and label supplied
            # @@TODO
            return HttpResponseRedirect(reverse("AnnalistSiteView"))
        return self.error(self.error400values())

class SiteActionView(AnnalistGenericView):
    """
    View class to perform completion of confirmed action requested from site view
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
            log.info("Complete remove %r"%(request.POST.getlist("select")))
            # @@TODO
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(reverse("AnnalistSiteView"))

# End.
