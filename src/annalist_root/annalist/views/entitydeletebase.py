"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist.views.uri_builder         import continuation_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.generic             import AnnalistGenericView

#   -------------------------------------------------------------------------------------------
#
#   Generic delete entity confirmation response handling class
#
#   -------------------------------------------------------------------------------------------

class EntityDeleteConfirmedBaseView(AnnalistGenericView):
    """
    View class to perform completion of confirmed entity deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(EntityDeleteConfirmedBaseView, self).__init__()
        return

    def complete_remove_entity(self, 
            coll_id, type_id, entity_id, 
            default_continuation_url, request_params):
        """
        Complete action to remove an entity.
        """
        continuation_url = (
            request_params.get('completion_url', None) or
            default_continuation_url
            )
        continuation_url_params = continuation_params(request_params)
        viewinfo = DisplayInfo(self, "delete", request_params, continuation_url)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.check_authorization("delete")
        if viewinfo.http_response:
            return viewinfo.http_response
        typeinfo     = viewinfo.entitytypeinfo
        message_vals = {'id': entity_id, 'type_id': type_id, 'coll_id': coll_id}
        messages     = (
            { 'entity_removed': typeinfo.entitymessages['entity_removed']%message_vals
            })
        err = typeinfo.entityclass.remove(typeinfo.entityparent, entity_id)
        if err:
            return self.redirect_error(continuation_url, continuation_url_params, error_message=str(err))
        return self.redirect_info(
            continuation_url, continuation_url_params, 
            info_message=messages['entity_removed']
            )

# End.
