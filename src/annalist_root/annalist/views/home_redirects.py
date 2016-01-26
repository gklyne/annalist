"""
Annalist home page and other view redirects
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect

from annalist.views.generic         import AnnalistGenericView

class AnnalistHomeView(AnnalistGenericView):
    """
    View class for home view
    """
    def __init__(self):
        super(AnnalistHomeView, self).__init__()
        return

    def get(self, request):
        return HttpResponseRedirect(self.view_uri("AnnalistSiteView"))

class AnnalistTypeRedirect(AnnalistGenericView):
    """
    View class for type URL without railing '/'
    """
    def __init__(self):
        super(AnnalistTypeRedirect, self).__init__()
        return

    def get(self, request, coll_id=None, type_id=None, list_id=None):
        return HttpResponseRedirect(request.get_full_path()+"/")

class AnnalistEntityRedirect(AnnalistGenericView):
    """
    View class for entity URL without railing '/'
    """
    def __init__(self):
        super(AnnalistEntityRedirect, self).__init__()
        return

    def get(self, request, coll_id=None, type_id=None, entity_id=None, view_id=None):
        return HttpResponseRedirect(request.get_full_path()+"/")

# End.
