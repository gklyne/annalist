"""
Annalist application URL definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf.urls           import patterns, url

from annalist.views             import AnnalistHomeView
from annalist.views.profile     import ProfileView
from annalist.views.confirm     import ConfirmView
from annalist.views.site        import SiteView, SiteActionView
from annalist.views.collection  import CollectionEditView
from oauth2.views               import LoginUserView, LoginPostView, LoginDoneView, LogoutUserView

urlpatterns = patterns('',
    url(r'^$',              AnnalistHomeView.as_view(), name='AnnalistHomeView'),
    url(r'^site/$',         SiteView.as_view(),         name='AnnalistSiteView'),
    url(r'^site_action/$',  SiteActionView.as_view(),   name='AnnalistSiteActionView'),
    url(r'^profile/$',      ProfileView.as_view(),      name='AnnalistProfileView'),
    url(r'^confirm/$',      ConfirmView.as_view(),      name='AnnalistConfirmView'),
    url(r'^collections/(?P<coll_id>\w{0,32})/$',
                            CollectionEditView.as_view(),
                            name='AnnalistCollectionEditView'),
    )

urlpatterns += patterns('',
    url(r'^login/$',      LoginUserView.as_view(),      name='LoginUserView'),
    url(r'^login_post/$', LoginPostView.as_view(),      name='LoginPostView'),
    url(r'^login_done/',  LoginDoneView.as_view(),      name='LoginDoneView'),
    url(r'^logout/$',     LogoutUserView.as_view(),     name='LogoutUserView'),
    )

# End.
