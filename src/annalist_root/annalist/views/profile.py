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

from annalist.views.generic         import AnnalistGenericView

class ProfileView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist user profile URI
    """
    def __init__(self):
        super(ProfileView, self).__init__()
        return

    # GET

    def get(self, request):
        def resultdata():
            username, useruri = self.get_user_identity()
            return (
                { 'title':      self.site_data()["title"]
                , 'user':       request.user 
                , 'username':   username
                , 'useruri':    useruri
                })
        return (
            self.authenticate() or 
            self.render_html(resultdata(), 'annalist_profile.html') or 
            self.error(self.error406values())
            )

# End.
