"""
Annalist application URL definitions
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.urls                        import re_path

from annalist.views.home_redirects      import (
    AnnalistHomeView, AnnalistTypeRedirect, AnnalistEntityRedirect
    )
from annalist.views.profile             import ProfileView
from annalist.views.confirm             import ConfirmView
from annalist.views.serverlog           import ServerLogView
from annalist.views.site                import SiteView, SiteActionView
from annalist.views.collection          import CollectionView, CollectionEditView
from annalist.views.recordtypedelete    import RecordTypeDeleteConfirmedView
from annalist.views.recordviewdelete    import RecordViewDeleteConfirmedView
from annalist.views.recordlistdelete    import RecordListDeleteConfirmedView

from annalist.views.entityedit          import GenericEntityEditView
from annalist.views.entitylist          import EntityGenericListView
from annalist.views.entitylistdata      import EntityListDataView
from annalist.views.entitydelete        import EntityDataDeleteConfirmedView

from annalist.views.siteresource        import SiteResourceAccess
from annalist.views.collectionresource  import CollectionResourceAccess
from annalist.views.entityresource      import EntityResourceAccess
from annalist.views.statichack          import serve_pages, serve_static

from login.login_views                  import LoginUserView, LoginPostView, LogoutUserView
from login.auth_oidc_client             import OIDC_AuthDoneView
from login.auth_django_client           import LocalUserPasswordView

# c - collections
# v - view
# l - list
# d - data/default view
#
# Metadata (using built-in type identifiers, otherwise same pattern as data):
#
# /c/<coll-id>/d/_type/                           list of record types
# /c/<coll-id>/d/_type/<type-id>                  view of type description
# /c/<coll-id>/d/_view/                           list of record views
# /c/<coll-id>/d/_view/<view-id>                  view of view description
# /c/<coll-id>/d/_list/                           list of record lists
# /c/<coll-id>/d/_list/<list-id>                  view of list description
# /c/<coll-id>/d/_field/                          list of field descriptions
# /c/<coll-id>/d/_field/<field-id>                view of field description
#
# Data:
#
# /c/<coll-id>/d/                                 default list of records
# /c/<coll-id>/d/<type-id>/                       default list of records of specified type
# /c/<coll-id>/d/<type-id>/<entity-id>            default view of identified entity
#
# /c/<coll-id>/l/<list-id>/                       specified list of records
# /c/<coll-id>/l/<list-id>/<type-id>              specified list of records of specified type
# /c/<coll-id>/v/<view-id>/<type-id>/<entity-id>  specified view of record
#
# Suffixes /!new, /!copy, /!edit, /!delete, etc. are used for forms that are part of the
# user interface for editing collections and resources, and do not of themselves identify
# persistent resources.

urlpatterns = [

    # Site pages
    re_path(r'^$',              AnnalistHomeView.as_view(),     name='AnnalistHomeView'),
    re_path(r'^site/$',         SiteView.as_view(),             name='AnnalistSiteView'),
    re_path(r'^site/!action$',  SiteActionView.as_view(),       name='AnnalistSiteActionView'),
    re_path(r'^confirm/$',      ConfirmView.as_view(),          name='AnnalistConfirmView'),
    re_path(r'^serverlog/$',    ServerLogView.as_view(),        name='AnnalistServerLogView'),

    #@@ site/site.json
    #@@ site/site.ttl

    # Special forms for collection view, customize and type/view/list deletion
    re_path(r'^c/(?P<coll_id>\w{1,128})/$',
                            CollectionView.as_view(),
                            name='AnnalistCollectionView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/!edit$',
                            CollectionEditView.as_view(),
                            name='AnnalistCollectionEditView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/types/!delete_confirmed$',
                            RecordTypeDeleteConfirmedView.as_view(),
                            name='AnnalistRecordTypeDeleteView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/views/!delete_confirmed$',
                            RecordViewDeleteConfirmedView.as_view(),
                            name='AnnalistRecordViewDeleteView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/lists/!delete_confirmed$',
                            RecordListDeleteConfirmedView.as_view(),
                            name='AnnalistRecordListDeleteView'),

    # Default/API access lists and data
    # (these may content negotiate for various formats)
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultListAll'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultListType'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/!delete_confirmed$',
                            EntityDataDeleteConfirmedView.as_view(),
                            name='AnnalistEntityDataDeleteView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityAccessView'),

    # Default edit views
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>copy)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDefaultDataView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>edit)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDefaultDataView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>view)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDefaultDataView'),

    # JSON list views without list_id specified
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<list_ref>entity_list.[\w]{1,32})$',
                            EntityListDataView.as_view(),
                            name='AnnalistEntityListDataAll'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<list_ref>entity_list.[\w]{1,32})$',
                            EntityListDataView.as_view(),
                            name='AnnalistEntityListDataType'),

    # Redirect type/entity URIs without trailing '/'
    # (Note these cannot match JSON resource names as '.' is not matched here)
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})$',
                            AnnalistTypeRedirect.as_view(),
                            name='AnnalistTypeRedirect'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})$',
                            AnnalistEntityRedirect.as_view(),
                            name='AnnalistEntityRedirect'),

    # Specified list views
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultList'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/(?P<type_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),

    # JSON specified list views
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_ref>entity_list.[\w]{1,32})$',
                            EntityListDataView.as_view(),
                            name='AnnalistEntityListDataAll'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/(?P<list_ref>entity_list.[\w]{1,32})$',
                            EntityListDataView.as_view(),
                            name='AnnalistEntityListDataAll'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<list_ref>entity_list.[\w]{1,32})$',
                            EntityListDataView.as_view(),
                            name='AnnalistEntityListDataType'),

    # Specified entity edit/view forms
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDataView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/!(?P<action>new)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityNewView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>copy)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>edit)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>view)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),

    # Named resource access (metadata, context, attachments, etc.)
    re_path(r'^site/(?P<resource_ref>[\w.-]{1,250})$',
                            SiteResourceAccess.as_view(),
                            name='AnnalistSiteResourceAccess'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<resource_ref>[\w.-]{1,250})$',
                            CollectionResourceAccess.as_view(),
                            name='AnnalistCollectionResourceAccess'),
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistEntityResourceAccess'),

    # Entity resource data access with specified view
    re_path(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistEntityViewAccess'),

    # Access supporting application pages in same collection
    re_path(r'^c/(?P<coll_id>\w{1,128})/p/(?P<page_ref>[\w/.-]{1,250})$',
                            serve_pages),

    # Access "favicon.ico"
    re_path(r'^(?P<path>favicon.ico)$',
                            serve_static),

    ] # End of urlpatterns

# Login-related view URLs

urlpatterns += [
    re_path(r'^login/$',        LoginUserView.as_view(),            name='LoginUserView'),
    re_path(r'^login_post/$',   LoginPostView.as_view(),            name='LoginPostView'),
    re_path(r'^login_local/$',  LocalUserPasswordView.as_view(),    name='LocalUserPasswordView'),
    re_path(r'^login_done/',    OIDC_AuthDoneView.as_view(),        name='OIDC_AuthDoneView'),
    re_path(r'^profile/$',      ProfileView.as_view(),              name='AnnalistProfileView'),
    re_path(r'^logout/$',       LogoutUserView.as_view(),           name='LogoutUserView'),
    # Info view...
    # re_path(r'^c/(?P<coll_id>_annalist_site)/d/(?P<type_id>_info)/(?P<entity_id>about)/$',
    re_path(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/$',
                            GenericEntityEditView.as_view(),    name='AnnalistInfoView'),
    ]

# End.
