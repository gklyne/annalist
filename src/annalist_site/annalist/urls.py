"""
Annalist application URL definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf.urls import patterns, url

import annalist.views
import annalist.profileview
import annalist.confirmview
import annalist.site
import oauth2.views

urlpatterns = patterns('',
    url(r'^$',              annalist.views.AnnalistHomeView.as_view(),    name='AnnalistHomeView'),
    url(r'^site/$',         annalist.site.SiteView.as_view(),             name='AnnalistSiteView'),
    url(r'^site_action/$',  annalist.site.SiteActionView.as_view(),       name='AnnalistSiteActionView'),
    url(r'^profile/$',      annalist.profileview.ProfileView.as_view(),   name='AnnalistProfileView'),
    url(r'^confirm/$',      annalist.confirmview.ConfirmView.as_view(),   name='AnnalistConfirmView'),
    url(r'^collections/(?P<coll_id>\w{0,32})/$',
                            annalist.collection.CollectionEditView.as_view(),
                            name='AnnalistCollectionEditView'),
    )

urlpatterns += patterns('',
    url(r'^login/$',      oauth2.views.LoginUserView.as_view(),  name='LoginUserView'),
    url(r'^login_post/$', oauth2.views.LoginPostView.as_view(),  name='LoginPostView'),
    url(r'^login_done/',  oauth2.views.LoginDoneView.as_view(),  name='LoginDoneView'),
    url(r'^logout/$',     oauth2.views.LogoutUserView.as_view(), name='LogoutUserView'),
    )

# End.
