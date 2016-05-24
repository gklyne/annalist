"""
Annalist collection views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import message
from annalist                       import layout
from annalist.identifiers           import ANNAL, RDFS
from annalist.exceptions            import Annalist_Error

from annalist.models                import entitytypeinfo
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.collectiondata import migrate_coll_data, migrate_coll_config_dirs

from annalist.views.uri_builder     import uri_with_params
from annalist.views.displayinfo     import DisplayInfo
from annalist.views.generic         import AnnalistGenericView
from annalist.views.confirm         import ConfirmView


class CollectionView(AnnalistGenericView):
    """
    View class to handle requests to display an Annalist collection.

    Redirects to a default view or list view.
    """
    def __init__(self):
        super(CollectionView, self).__init__()
        self.default_continuation = self.view_uri("AnnalistSiteView")
        return

    def collection_view_setup(self, coll_id, action, request_dict):
        """
        Assemble display information for collection view request handler
        """
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.check_authorization(action)
        self.default_continuation = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        if not viewinfo.http_response:
            errs = migrate_coll_config_dirs(viewinfo.collection)
            if errs:
                viewinfo.report_error("\n".join(errs))
        return viewinfo

    def get(self, request, coll_id):
        """
        Display the specified collection 
        """
        viewinfo = self.collection_view_setup(coll_id, "view", request.GET.dict())
        if viewinfo.http_response:
            log.debug(
                "CollectionView.get: response %d: %s"%
                (viewinfo.http_response.status_code, viewinfo.http_response.reason_phrase)
                )
            return viewinfo.http_response
        default_view, default_type, default_entity = viewinfo.get_default_view()
        if default_view and default_type and default_entity:
            redirect_uri = self.view_uri(
                "AnnalistEntityDataView",
                coll_id=coll_id, 
                view_id=default_view, type_id=default_type, entity_id=default_entity
                )
        else:
            redirect_uri = self.view_uri(
                "AnnalistEntityDefaultListAll", 
                coll_id=coll_id
                )
        return HttpResponseRedirect(redirect_uri)

class CollectionEditView(AnnalistGenericView):
    """
    View class to handle requests to an Annalist collection edit URI
    """
    def __init__(self):
        super(CollectionEditView, self).__init__()
        self.default_continuation = self.view_uri("AnnalistSiteView")
        return

    def collection_edit_setup(self, coll_id, action, request_dict):
        """
        Assemble display information for collection view request handler
        """
        viewinfo = DisplayInfo(self, action, request_dict, self.default_continuation)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(entitytypeinfo.COLL_ID)
        viewinfo.check_authorization(action)
        self.default_continuation = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        return viewinfo

    # GET

    def get(self, request, coll_id):
        """
        Form for editing (customizing) the current collection 
        """
        def resultdata(viewinfo):
            def get_id(e):
                return e.get_id()
            coll = viewinfo.collection
            context = (
                { 'continuation_url':   viewinfo.get_continuation_url() or ""
                , 'continuation_param': viewinfo.get_continuation_param()
                , 'types':              sorted(coll.types(altscope=None), key=get_id)
                , 'lists':              sorted(coll.lists(altscope=None), key=get_id)
                , 'views':              sorted(coll.views(altscope=None), key=get_id)
                , 'select_rows':        "6"
                })
            context.update(viewinfo.context_data())
            context['heading'] = "Customize collection: %(coll_label)s"%context
            return context
        continuation_url = None
        # View permission only to display form, 
        # as it presents useful information even when not editing.
        viewinfo = self.collection_edit_setup(coll_id, "view", request.GET.dict())
        if viewinfo.http_response:
            return viewinfo.http_response
        self.help_markdown = viewinfo.collection.get(RDFS.CURIE.comment, None)
        return (
            self.render_html(resultdata(viewinfo), 'annalist_collection_edit.html') or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id):
        """
        Update some aspect of the current collection
        """
        # Note: in many cases, this function redirects to a URI that displays a form
        #       to gather further details of values to update.  Values returned by
        #       POST to this view are then passed as URI segments in the GET request
        #       that renders the form.  Maybe there's an easier way than all this 
        #       URI-wrangling?
        redirect_uri  = None
        http_response = None
        viewinfo = self.collection_edit_setup(coll_id, "config", request.POST.dict())
        if viewinfo.http_response:
            return viewinfo.http_response
        if "close" in request.POST:
            redirect_uri = viewinfo.get_continuation_next()
        if "migrate" in request.POST:
            msgs = migrate_coll_data(viewinfo.collection)
            msg_vals = {'id': coll_id}
            if msgs:
                for msg in msgs:
                    log.warning(msg)
                err = message.MIGRATE_COLLECTION_ERROR%msg_vals
                msg = "\n".join([err]+msgs)
                log.error(msg)
                http_response = self.error(dict(self.error500values(),message=msg))
            else:
                http_response = self.redirect_info(
                    self.get_request_path(), 
                    info_message=message.MIGRATED_COLLECTION_DATA%msg_vals
                    )
            return http_response
        # Edit collection metadata
        if "metadata" in request.POST:
            redirect_uri = self.item_edit_uri(
                layout.SITEDATA_ID, "_coll", "Collection_view", coll_id, 
                message.NO_COLLECTION_METADATA, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        # Record types
        type_id = request.POST.get('typelist', None)
        if "type_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_type", "Type_view", 
                viewinfo.get_continuation_here()
                )
        if "type_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_type", "Type_view", type_id, 
                message.NO_TYPE_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "type_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_type", "Type_view", type_id, 
                message.NO_TYPE_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "type_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, type_id, 
                message.NO_TYPE_FOR_DELETE, 
                message.REMOVE_RECORD_TYPE, 
                "AnnalistRecordTypeDeleteView",
                viewinfo.get_continuation_url()
                )
        # List views
        list_id = request.POST.get('listlist', None)
        if "list_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_list", "List_view", 
                viewinfo.get_continuation_here()
                )
        if "list_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_list", "List_view", list_id, 
                message.NO_LIST_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "list_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_list", "List_view", list_id, 
                message.NO_LIST_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "list_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, list_id, 
                message.NO_LIST_FOR_DELETE, 
                message.REMOVE_RECORD_LIST, 
                "AnnalistRecordListDeleteView",
                viewinfo.get_continuation_url()
                )
        # Record views
        view_id = request.POST.get('viewlist', None)
        if "view_new" in request.POST:
            redirect_uri = self.item_new_uri(
                coll_id, "_view", "View_view", 
                viewinfo.get_continuation_here()
                )
        if "view_copy" in request.POST:
            redirect_uri = self.item_copy_uri(
                coll_id, "_view", "View_view", view_id, 
                message.NO_VIEW_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "view_edit" in request.POST:
            redirect_uri = self.item_edit_uri(
                coll_id, "_view", "View_view", view_id, 
                message.NO_VIEW_FOR_COPY, 
                viewinfo.get_continuation_here(),
                viewinfo.get_continuation_url()
                )
        if "view_delete" in request.POST:
            redirect_uri, http_response = self.item_delete_response(
                coll_id, view_id, 
                message.NO_VIEW_FOR_DELETE, 
                message.REMOVE_RECORD_VIEW, 
                "AnnalistRecordViewDeleteView",
                viewinfo.get_continuation_url()
                )
        # Invoke selected view and/or render status response
        if redirect_uri:
            http_response = http_response or HttpResponseRedirect(redirect_uri)
        if http_response:
            return http_response
        e = Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())
        log.exception(str(e))
        return self.error(
            dict(self.error500values(),
                message=str(e)+" - see server log for details"
                )
            )
        # raise Annalist_Error(request.POST, "Unexpected values in POST to "+self.get_request_path())

    # POST helper methods

    def item_new_uri(self, coll_id, type_id, view_id, continuation_here):
        # @@TODO:  pass in viewinfo rather than continuation URL
        redirect_uri = uri_with_params(
            self.view_uri("AnnalistEntityNewView", 
                coll_id=coll_id, view_id=view_id, type_id=type_id, action="new"
                ),
            {'continuation_url': continuation_here}
            )
        return redirect_uri

    def item_edit_copy_uri(self,
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_url, action):
        # NOTE: continuation_url is the continuation URL from the current page,
        #       and is used as part of the URL used to redisplay the current 
        #       page with an error message.
        # @@TODO:  pass in viewinfo rather than continuation URLs
        redirect_uri = (
            self.check_value_supplied(
                entity_id, no_entity_msg, 
                continuation_url
                )
            or
            uri_with_params(
                self.view_uri("AnnalistEntityEditView", action=action, 
                    coll_id=coll_id, view_id=view_id, type_id=type_id, entity_id=entity_id
                    ),
                {'continuation_url': continuation_here}
                )
            )
        return redirect_uri

    def item_copy_uri(self, 
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_url):
        # NOTE: continuation_url is the continuation URL from the current page,
        #       and is used as part of the URL used to redisplay the current 
        #       page with an error message.
        # @@TODO:  pass in viewinfo rather than continuation URLs
        redirect_uri = self.item_edit_copy_uri(
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_url,
            "copy")
        return redirect_uri

    def item_edit_uri(self,
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_url):
        # NOTE: continuation_url is the continuation URL from the current page,
        #       and is used as part of the URL used to redisplay the current 
        #       page with an error message.
        # @@TODO:  pass in viewinfo rather than continuation URLs
        redirect_uri = self.item_edit_copy_uri(
            coll_id, type_id, view_id, entity_id, no_entity_msg, 
            continuation_here, continuation_url,
            "edit")
        return redirect_uri

    def item_delete_response(self, 
            coll_id, entity_id, 
            no_entity_msg, 
            confirm_msg, 
            complete_action_view,
            continuation_url):
        redirect_uri  = None
        http_response = None
        if entity_id:
            # Get user to confirm action before actually doing it
            confirmed_action_uri = self.view_uri(
                complete_action_view, coll_id=coll_id
                )
            message_vals = {'id': entity_id, 'coll_id': coll_id}
            http_response = (
                ConfirmView.render_form(self.request,
                    action_description=     confirm_msg%message_vals,
                    confirmed_action_uri=   confirmed_action_uri,
                    action_params=          self.request.POST,
                    cancel_action_uri=      self.get_request_path(),
                    title=                  self.site_data()["title"]
                    )
                )
        else:
            redirect_uri = (
                self.check_value_supplied(
                    entity_id, no_entity_msg,
                    continuation_url
                    )
                )
        return redirect_uri, http_response

# End.
