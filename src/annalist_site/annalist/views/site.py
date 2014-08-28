"""
Analist site views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.http                import HttpResponse
from django.http                import HttpResponseRedirect
from django.core.urlresolvers   import resolve, reverse

from annalist.identifiers       import ANNAL, RDFS
from annalist.exceptions        import Annalist_Error, EntityNotFound_Error
from annalist                   import message
from annalist                   import util

from annalist.models.site       import Site

from annalist.views.generic     import AnnalistGenericView
from annalist.views.confirm     import ConfirmView

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
        # log.info("SiteView.get: site_data %r"%(self.site_data()))
        return (
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
        if "remove" in request.POST:
            collections = request.POST.getlist("select", [])
            if collections:
                # Get user to confirm action before actually doing it
                return (
                    self.authorize("DELETE") or
                    ConfirmView.render_form(request,
                        action_description=     message.REMOVE_COLLECTIONS%{'ids': ", ".join(collections)},
                        action_params=          request.POST,
                        confirmed_action_uri=   self.view_uri('AnnalistSiteActionView'),
                        cancel_action_uri=      self.view_uri('AnnalistSiteView'),
                        title=                  self.site_data()["title"]
                        )
                    )
            else:
                return self.redirect_info(
                    self.view_uri("AnnalistSiteView"), 
                    info_message=message.NO_COLLECTIONS_SELECTED, info_head=message.NO_ACTION_PERFORMED
                    )
        if "new" in request.POST:
            # Create new collection with name and label supplied
            new_id    = request.POST["new_id"]
            new_label = request.POST["new_label"]
            log.debug("New collection %s: %s"%(new_id, new_label))
            if not new_id:
                return self.redirect_error(
                    self.view_uri("AnnalistSiteView"), 
                    error_message=message.MISSING_COLLECTION_ID)
            if not util.valid_id(new_id):
                return self.redirect_error(
                    self.view_uri("AnnalistSiteView"), 
                    error_message=message.INVALID_COLLECTION_ID%(new_id))
            # Create new collection with name and label supplied
            auth_required = self.authorize("CREATE")
            if auth_required:
                return auth_required
            coll_meta = (
                { RDFS.CURIE.label:    new_label
                , RDFS.CURIE.comment:  ""
                })
            self.site().add_collection(new_id, coll_meta)
            return self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=message.CREATED_COLLECTION_ID%{'coll_id': new_id}
                )
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
        if "remove" in request.POST:
            log.debug("Complete remove %r"%(request.POST.getlist("select")))
            auth_required = self.authorize("DELETE")
            if auth_required:
                return auth_required
            coll_ids = request.POST.getlist("select")
            for coll_id in coll_ids:
                err = self.site().remove_collection(coll_id)
                if err:
                    return self.redirect_error(
                        self.view_uri("AnnalistSiteView"), 
                        error_message=str(err))
            return self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=message.COLLECTIONS_REMOVED%{'ids': ", ".join(coll_ids)}
                )
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(self.view_uri("AnnalistSiteView"))

# End.
