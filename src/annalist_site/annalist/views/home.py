"""
Annalist home page view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os
# import os.path
# import json
# import random
# import uuid
# import copy

import logging
log = logging.getLogger(__name__)

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
# from django.template                import RequestContext, loader
# from django.views                   import generic
# from django.views.decorators.csrf   import csrf_exempt
from django.core.urlresolvers       import resolve, reverse

from django.conf import settings

# import oauth2.views

# from utils.ContentNegotiationView   import ContentNegotiationView

# from annalist                       import message
# from annalist                       import layout
from annalist.views.generic           import AnnalistGenericView
# from annalist.site                  import Site
# from annalist.collection            import Collection
# from annalist.recordtype            import RecordType

LOGIN_URIS = None

# Create your views here.

class AnnalistHomeView(AnnalistGenericView):
    """
    View class for home view
    """
    def __init__(self):
        super(AnnalistHomeView, self).__init__()
        return

    def get(self, request):
        return HttpResponseRedirect(reverse("AnnalistSiteView"))

# End.
