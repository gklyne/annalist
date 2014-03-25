__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf.urls import patterns, url

from rovserver import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='index')
    url(r'^$', views.RovServerHomeView.as_view(), name='RovServerHomeView'),
    url(r'^login/$', views.RovServerLoginUserView.as_view(), name='RovServerLoginUserView'),
    url(r'^login/auth/$', views.RovServerLoginAuthView.as_view(), name='RovServerLoginAuthView'),
    url(r'^login/complete/', views.RovServerLoginCompleteView.as_view(), name='RovServerLoginCompleteView'),
    url(r'^logout/$', views.RovServerLogoutUserView.as_view(), name='RovServerLogoutUserView'),
    url(r'^ROs/([0-9a-f]{8})/$', views.ResearchObjectView.as_view(), name='ResearchObjectView')
    )
