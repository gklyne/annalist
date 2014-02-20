"""
Analist site views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os
# import os.path
# import collections
# import urlparse
# import json
# import traceback

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import resolve, reverse

# from annalist.identifiers       import ANNAL
from annalist.exceptions        import Annalist_Error, EntityNotFound_Error
from annalist                   import message
from annalist                   import util
from annalist.site              import Site

from annalist.views             import AnnalistGenericView
from annalist.views.confirm     import ConfirmView

# @@TODO: align form variable names with stored collection metadata

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
                        action_description=     message.REMOVE_COLLECTIONS%(", ".join(collections)),
                        action_params=          request.POST,
                        complete_action_uri=    reverse('AnnalistSiteActionView'),
                        cancel_action_uri=      reverse('AnnalistSiteView'),
                        title=                  self.site_data()["title"]
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
            self.site().add_collection(new_id, coll_meta)
            return self.redirect_info("AnnalistSiteView", message.CREATED_COLLECTION_ID%(new_id))
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
        log.debug("siteactionview.post: %r"%(request.POST))
        if request.POST.get("remove", None):
            log.debug("Complete remove %r"%(request.POST.getlist("select")))
            auth_required = self.authorize("DELETE")
            if auth_required:
                return auth_required
            coll_ids = request.POST.getlist("select")
            for coll_id in coll_ids:
                err = self.site().remove_collection(coll_id)
                if err:
                    return self.redirect_error("AnnalistSiteView", str(err))
            # @@TODO: change redirect logic to accept URI not view name
            return self.redirect_info(
                "AnnalistSiteView", 
                message.COLLECTIONS_REMOVED%(", ".join(coll_ids))
                )
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(reverse("AnnalistSiteView"))

# End.
