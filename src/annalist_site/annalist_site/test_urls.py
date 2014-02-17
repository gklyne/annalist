"""
Annalist site root URL definitions for testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf        import settings
from django.conf.urls   import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'annalist_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^'+settings.TEST_BASE_PATH+"/", include('annalist.urls')),
)
