"""
Annalist site root URL definitions
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf                import settings
from django.conf.urls           import include
from django.urls                import re_path

from django.contrib             import admin
admin.autodiscover()

from annalist.views.home_redirects  import AnnalistHomeView
from annalist.views.statichack      import serve_static, serve_favicon

annalist_pattern = "^"+settings.ANNALIST_SITE_SEG+"/"
urlpatterns  = [
    re_path(r'^$',         		AnnalistHomeView.as_view(), name='AnnalistHomeView'),

    re_path(r'^admin/',    		admin.site.urls),

    re_path(annalist_pattern,	include('annalist.urls')),
    ]

static_pattern = "^"+settings.STATIC_SEG+"/"
urlpatterns += [
    re_path(static_pattern+r'(?P<path>.*)$', serve_static),
    ]

urlpatterns += [
    re_path(r'(?P<path>favicon.ico)$', serve_favicon),
    ]

# End.
