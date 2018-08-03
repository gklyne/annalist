from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Annalist site root URL definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf                import settings
from django.conf.urls           import include, url

from django.contrib             import admin
admin.autodiscover()

from annalist.views.home_redirects  import AnnalistHomeView
from annalist.views.statichack      import serve_static

urlpatterns = [
    url(r'^$',         AnnalistHomeView.as_view(), name='AnnalistHomeView'),

    url(r'^admin/',    include(admin.site.urls)),

    url(r'^annalist/', include('annalist.urls')),
    ]

if not settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve_static),
        ]

# End.
