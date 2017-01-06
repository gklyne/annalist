"""
Annalist action confirmation view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os.path
# import json
# import random
import logging
# import uuid
# import copy

import logging
log = logging.getLogger(__name__)

# import rdflib
# import httplib2

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import RequestContext, loader

from django.conf                    import settings

from utils.ContentNegotiationView   import ContentNegotiationView

from annalist.models.annalistuser   import AnnalistUser

from annalist.views.generic         import AnnalistGenericView

class ServerLogView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist user profile URI
    """
    def __init__(self):
        super(ServerLogView, self).__init__()
        return

    # GET

    def get(self, request):
        def resultdata():
            serverlogname = settings.LOGGING_FILE
            serverlogfile = open(serverlogname, "r")
            serverlog     = list(serverlogfile)
            return (
                { 'title':              self.site_data()["title"]
                , 'serverlogname':      serverlogname
                , 'serverlog':          "".join(serverlog)
                , 'continuation_url':   continuation_url
                })
        continuation_url  = self.continuation_next(
            request.GET, self.view_uri("AnnalistHomeView")
            )
            # viewinfo = DisplayInfo(self, "delete", request_params, continuation_url)
            # viewinfo.check_authorization("delete")
            # if viewinfo.http_response:
            #     return viewinfo.http_response
        return (
            self.authenticate(continuation_url) or 
            self.authorize("ADMIN", None) or
            self.render_html(resultdata(), 'annalist_serverlog.html') or 
            self.error(self.error406values())
            )

    def post(self, request):
        continuation_url  = request.POST.get("continuation_url", "../")
        return HttpResponseRedirect(continuation_url)

# End.
