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
from annalist               import layout
from annalist.exceptions    import Annalist_Error, EntityNotFound_Error
from annalist.views         import AnnalistGenericView
from annalist.confirmview   import ConfirmView
from annalist               import util
from annalist.entity        import EntityRoot, Entity
from annalist.collection    import Collection

# @@TODO: align form variable names with stored collection metadata

class Site(EntityRoot):

    def __init__(self, sitebaseuri, sitebasedir):
        """
        Initialize a Site object

        sitebaseuri     the base URI of the site
        sitebasedir     the base dictionary for site information
        """
        log.debug("Site init: %s"%(sitebasedir))
        super(Site, self).__init__(sitebaseuri, sitebasedir)
        return

    def collections(self):
        """
        Generator enumerates and returns collection descriptions that are part of a site.

        Yielded values are collection objects.
        """
        log.debug("site.collections: basedir: %s"%(self._basedir))
        site_files = os.listdir(self._basedir)
        for f in site_files:
            c = Collection.load(f, self._baseuri, self._basedir)
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
        p = util.entity_path(self._basedir, [], layout.SITE_META_FILE)
        if not (p and os.path.exists(p)):
            raise EntityNotFound_Error(p)
        site_data = util.read_entity(p)
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

    def remove_collection(self, coll_id):
        """
        Remove a collection from the site data.

        coll_id     identifier for the collection to remove.

        Returns a non-False status code if the collection is not removed.
        """
        log.debug("remove_collection: %s"%(coll_id))
        return Collection.remove(coll_id, self._basedir)

class SiteView(AnnalistGenericView):
    """
    View class to handle requests to the annalist site home URI
    """
    def __init__(self):
        super(SiteView, self).__init__()
        self._site      = Site(self._sitebaseuri, self._sitebasedir)
        self._site_data = None
        return

    def site_data(self):
        if not self._site_data:
            self._site_data = self._site.site_data()
        return self._site_data

    # GET

    def get(self, request):
        """
        Create a rendering of the current site home page, containing (among other things)
        a list of defined collections.
        """
        return (
            # self.authenticate() or 
            self.authorize("VIEW") or 
            self.render_html(self.site_data(), 'annalist_site.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request):
        """
        Process options to add or remove a collection in an Annalist site
        """
        log.debug("site.post: %r"%(request.POST.lists()))
        if request.POST.get("remove", None):
            collections = request.POST.getlist("select", [])
            if collections:
                # Get user to confirm action before actually doing it
                return (
                    self.authorize("DELETE") or
                    ConfirmView.render_form(request,
                        action_description= message.REMOVE_COLLECTIONS%(", ".join(collections)),
                        action_params=      request.POST,
                        complete_action=    'AnnalistSiteActionView',
                        cancel_action=      'AnnalistSiteView',
                        title=              self.site_data()["title"]
                        )
                    )
            else:
                return self.redirect_info(
                    "AnnalistSiteView", message.NO_COLLECTIONS_SELECTED,
                    info_head=message.NO_ACTION_PERFORMED
                    )
        if request.POST.get("new", None):
            # Create new collection with name and label supplied
            new_id    = request.POST["new_id"]
            new_label = request.POST["new_label"]
            log.debug("New collection %s: %s"%(new_id, new_label))
            if not new_id:
                return self.redirect_error("AnnalistSiteView", message.MISSING_COLLECTION_ID)
            if not util.valid_id(new_id):
                return self.redirect_error("AnnalistSiteView", message.INVALID_COLLECTION_ID%(new_id))
            # Create new collection with name and label supplied
            auth_required = self.authorize("CREATE")
            if auth_required:
                return auth_required
            coll_meta = (
                { 'rdfs:label':    new_label
                , 'rdfs:comment':  ""
                })
            self._site.add_collection(new_id, coll_meta)
            return self.redirect_info("AnnalistSiteView", message.CREATED_COLLECTION_ID%(new_id))
        return self.error(self.error400values())

class SiteActionView(AnnalistGenericView):
    """
    View class to perform completion of confirmed action requested from site view
    """
    def __init__(self):
        super(SiteActionView, self).__init__()
        self._site = Site(self._sitebaseuri, self._sitebasedir)
        return

    # POST
    # @@TODO: Delete collection: POST <site-action-uri> should be DELETE <collection-uri>
    #         use secondary request here when DELETE <collection-uri>?

    def post(self, request):
        """
        Process options to complete action to add or remove a collection
        """
        log.debug("siteactionview.post: %r"%(request.POST))
        if request.POST.get("remove", None):
            log.debug("Complete remove %r"%(request.POST.getlist("select")))
            auth_required = self.authorize("DELETE")
            if auth_required:
                return auth_required
            coll_ids = request.POST.getlist("select")
            for coll_id in coll_ids:
                err = self._site.remove_collection(coll_id)
                if err:
                    return self.redirect_error("AnnalistSiteView", str(err))
            return self.redirect_info(
                "AnnalistSiteView", 
                message.COLLECTIONS_REMOVED%(", ".join(coll_ids))
                )
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(reverse("AnnalistSiteView"))

# End.
