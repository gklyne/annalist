"""
Analist site views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist.identifiers           import ANNAL, RDFS
from annalist.exceptions            import Annalist_Error, EntityNotFound_Error
from annalist                       import message
from annalist                       import util
from annalist                       import layout


import annalist.models.entitytypeinfo as entitytypeinfo
from annalist.models.entitytypeinfo import CONFIG_PERMISSIONS, SITE_PERMISSIONS
from annalist.models.site           import Site
from annalist.models.collection     import Collection


from annalist.views.displayinfo     import DisplayInfo
from annalist.views.generic         import AnnalistGenericView
from annalist.views.confirm         import ConfirmView
from annalist.views.uri_builder     import uri_with_params

class SiteView(AnnalistGenericView):
    """
    View class to handle requests to the annalist site home URI
    """
    def __init__(self):
        super(SiteView, self).__init__()
        self.help_markdown = None
        return

    # GET

    def get(self, request):
        """
        Create a rendering of the current site home page, containing (among other things)
        a list of defined collections.
        """
        viewinfo = DisplayInfo(self, "view", {}, None)    # No continuation
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(layout.SITEDATA_ID)
        viewinfo.get_type_info(entitytypeinfo.COLL_ID)
        viewinfo.check_authorization("view")
        if viewinfo.http_response:
            return viewinfo.http_response
        self.help_markdown = viewinfo.collection.get(RDFS.CURIE.comment, None)
        resultdata = viewinfo.sitedata
        resultdata.update(viewinfo.context_data())
        # log.info("SiteView.get: site_data %r"%(self.site_data()))
        return (
            self.check_site_data() or
            self.render_html(resultdata, 'annalist_site.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request):
        """
        Process options to add or remove a collection in an Annalist site
        """
        log.debug("site.post: %r"%(request.POST.lists()))

        collections   = request.POST.getlist("select", [])
        coll_id       = collections[0] if collections else "_"
        coll_ids      = {'ids': ", ".join(collections)}
        perm_req      = None
        perm_scope    = None
        none_msg      = None
        many_msg      = None
        redirect_uri  = None
        http_response = None
        # Process POST option
        if   "view" in request.POST:
            # Collection data is considered part of configuration, hence CONFIG_PERMISSIONS:
            perm_req     = CONFIG_PERMISSIONS["view"]
            # Use Collection or Site permissions:
            perm_scope   = "all"
            none_msg     = message.NO_COLLECTION_VIEW
            many_msg     = message.MANY_COLLECTIONS_VIEW
            target_uri   = self.view_uri("AnnalistEntityEditView",
                coll_id=layout.SITEDATA_ID,
                view_id="Collection_view",
                type_id="_coll",
                entity_id=coll_id,
                action="view"
                )
            redirect_uri = uri_with_params(
                    target_uri, 
                    {'continuation_url': self.continuation_here()}
                    )
        elif "edit" in  request.POST:
            perm_req    = CONFIG_PERMISSIONS["edit"]
            perm_scope  = "all"
            none_msg    = message.NO_COLLECTION_EDIT
            many_msg    = message.MANY_COLLECTIONS_EDIT
            target_uri  = self.view_uri("AnnalistEntityEditView",
                coll_id=layout.SITEDATA_ID,
                view_id="Collection_view",
                type_id="_coll",
                entity_id=coll_id,
                action="edit"
                )
            redirect_uri = uri_with_params(
                    target_uri, 
                    {'continuation_url': self.continuation_here()}
                    )
        elif "remove" in request.POST:
            perm_req    = "DELETE_COLLECTION"
            perm_scope  = "all"    # Collection or site permissions
            none_msg    = message.NO_COLLECTIONS_REMOVE
        elif "new" in request.POST:
            perm_req    = "CREATE_COLLECTION"
            perm_scope  = "site"    # Site permission required
            new_id      = request.POST["new_id"]
            new_label   = request.POST["new_label"]
        # Common checks
        if none_msg and not collections:
            http_response = self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=none_msg, info_head=message.NO_ACTION_PERFORMED
                )
        elif many_msg and len(collections) > 1:
            http_response = self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=many_msg%coll_ids, 
                info_head=message.NO_ACTION_PERFORMED
                )
        elif perm_req:
            if perm_scope == "all":
                # Check collections for permissions
                for cid in collections:
                    if http_response is None:
                        site     = self.site(host=self.get_request_host())
                        sitedata = self.site_data()
                        coll     = Collection.load(site, cid, altscope="site")
                        http_response = (
                            self.authorize("ADMIN", coll) and   # Either of these...
                            self.authorize(perm_req, coll)
                            )
                        coll = None
            else:
                # Check site only for permissions
                http_response = (
                    self.authorize("ADMIN", None) and 
                    self.authorize(perm_req, None)
                    )
        if http_response is not None:
            return http_response            
        # Perform selected option
        if redirect_uri:
            log.info("Redirect to %s"%redirect_uri)
            return HttpResponseRedirect(redirect_uri)
        if "remove" in request.POST:
            if layout.SITEDATA_ID in collections:
                log.warning("Attempt to delete site data collection %(ids)s"%(coll_ids))
                http_response = self.error(self.error403values(scope="DELETE_SITE"))
            else:
                http_response = ConfirmView.render_form(request,
                    action_description=     message.REMOVE_COLLECTIONS%coll_ids,
                    action_params=          request.POST,
                    confirmed_action_uri=   self.view_uri('AnnalistSiteActionView'),
                    cancel_action_uri=      self.view_uri('AnnalistSiteView'),
                    title=                  self.site_data()["title"]
                    )
            return http_response
        if "new" in request.POST:
            log.info("New collection %s: %s"%(new_id, new_label))
            error_message = None
            if not new_id:
                error_message = message.MISSING_COLLECTION_ID
            elif not util.valid_id(new_id):
                error_message = message.INVALID_COLLECTION_ID%{'coll_id': new_id}
            if error_message:
                return self.redirect_error(
                    self.view_uri("AnnalistSiteView"), 
                    error_message=error_message
                    )
            coll_meta = (
                { RDFS.CURIE.label:    new_label
                , RDFS.CURIE.comment:  ""
                })
            # Add collection
            coll = self.site().add_collection(new_id, coll_meta)
            coll.generate_coll_jsonld_context()
            user             = self.request.user
            user_id          = user.username
            user_uri         = "mailto:"+user.email
            user_name        = "%s %s"%(user.first_name, user.last_name)
            user_description = "User %s: permissions for %s in collection %s"%(user_id, user_name, new_id)
            coll.create_user_permissions(
                user_id, user_uri, 
                user_name, user_description,
                user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
                )
            return self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=message.CREATED_COLLECTION_ID%{'coll_id': new_id}
                )

        # elif "remove" in request.POST:
        #     collections = request.POST.getlist("select", [])
        #     if collections:
        #         # Check authorization
        #         if layout.SITEDATA_ID in collections:
        #             log.warning("Attempt to delete site data collection %r"%(collections))
        #             auth_required = self.error(self.error403values(scope="DELETE_SITE"))
        #         else:
        #             auth_required = (
        #                 self.authorize("ADMIN", None) and           # either of these..
        #                 self.authorize("DELETE_COLLECTION", None)
        #                 )
        #         return (
        #             # Get user to confirm action before actually doing it
        #             auth_required or
        #             ConfirmView.render_form(request,
        #                 action_description=     message.REMOVE_COLLECTIONS%{'ids': ", ".join(collections)},
        #                 action_params=          request.POST,
        #                 confirmed_action_uri=   self.view_uri('AnnalistSiteActionView'),
        #                 cancel_action_uri=      self.view_uri('AnnalistSiteView'),
        #                 title=                  self.site_data()["title"]
        #                 )
        #             )
        #     else:
        #         return self.redirect_info(
        #             self.view_uri("AnnalistSiteView"), 
        #             info_message=message.NO_COLLECTIONS_REMOVE, info_head=message.NO_ACTION_PERFORMED
        #             )
        # if "new" in request.POST:
        #     # Create new collection with name and label supplied
        #     new_id    = request.POST["new_id"]
        #     new_label = request.POST["new_label"]
        #     log.debug("New collection %s: %s"%(new_id, new_label))
        #     if not new_id:
        #         return self.redirect_error(
        #             self.view_uri("AnnalistSiteView"), 
        #             error_message=message.MISSING_COLLECTION_ID
        #             )
        #     if not util.valid_id(new_id):
        #         return self.redirect_error(
        #             self.view_uri("AnnalistSiteView"), 
        #             error_message=message.INVALID_COLLECTION_ID%{'coll_id': new_id}
        #             )
        #     # Create new collection with name and label supplied
        #     auth_required = (
        #         self.authorize("ADMIN", None) and           # either of these..
        #         self.authorize("CREATE_COLLECTION", None)
        #         )
        #     if auth_required:
        #         return auth_required
        #     coll_meta = (
        #         { RDFS.CURIE.label:    new_label
        #         , RDFS.CURIE.comment:  ""
        #         })
        #     coll = self.site().add_collection(new_id, coll_meta)
        #     # Generate initial context
        #     coll.generate_coll_jsonld_context()
        #     # Create full permissions in new collection for creating user
        #     user = self.request.user
        #     user_id = user.username
        #     user_uri = "mailto:"+user.email
        #     user_name = "%s %s"%(user.first_name, user.last_name)
        #     user_description = "User %s: permissions for %s in collection %s"%(user_id, user_name, new_id)
        #     coll.create_user_permissions(
        #         user_id, user_uri, 
        #         user_name, user_description,
        #         user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        #         )
        #     return self.redirect_info(
        #         self.view_uri("AnnalistSiteView"), 
        #         info_message=message.CREATED_COLLECTION_ID%{'coll_id': new_id}
        #         )
        log.warning("Invalid POST request: %r"%(request.POST.lists()))
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
            auth_required = (
                self.authorize("ADMIN", None) and           # either of these..
                self.authorize("DELETE_COLLECTION", None)
                )
            if auth_required:
                return auth_required
            coll_ids = request.POST.getlist("select")
            for coll_id in coll_ids:
                if coll_id == layout.SITEDATA_ID:
                    err = Annalist_Error("Attempt to delete site data collection (%s)"%coll_id)
                    log.warning(str(err))
                else:
                    err = self.site().remove_collection(coll_id)
                if err:
                    return self.redirect_error(
                        self.view_uri("AnnalistSiteView"), 
                        error_message=str(err))
            return self.redirect_info(
                self.view_uri("AnnalistSiteView"), 
                info_message=message.COLLECTION_REMOVED%{'ids': ", ".join(coll_ids)}
                )
        else:
            return self.error(self.error400values())
        return HttpResponseRedirect(self.view_uri("AnnalistSiteView"))

# End.
