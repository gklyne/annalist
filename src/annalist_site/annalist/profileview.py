"""
Annalist action confirmation view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path
import json
import random
import logging
import uuid
import copy

# import rdflib
# import httplib2

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import RequestContext, loader

from django.conf                    import settings

from utils.ContentNegotiationView   import ContentNegotiationView

from annalist.views                 import AnnalistGenericView

class ProfileView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist user profile URI
    """
    def __init__(self):
        super(ProfileView, self).__init__()
        return

    # GET

    @ContentNegotiationView.accept_types(["text/html", "application/html", "*/*"])
    def render_html(self, resultdata):
        resultdata["user"] = self.request.user
        template = loader.get_template('annalist_profile.html')
        context  = RequestContext(self.request, resultdata)
        return HttpResponse(template.render(context))

    def get(self, request):
        def resultdata():
            return { 'user': request.user }
        return (
            self.authenticate() or 
            self.render_html(resultdata()) or 
            self.error(self.error406values())
            )

# End.
