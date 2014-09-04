"""
Annalist home page view definition
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

# End.
