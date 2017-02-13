"""
Annalist application URL definitions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf.urls                   import patterns, url

from annalist.views.home_redirects      import (
    AnnalistHomeView, AnnalistTypeRedirect, AnnalistEntityRedirect
    )
from annalist.views.profile             import ProfileView
from annalist.views.confirm             import ConfirmView
from annalist.views.serverlog           import ServerLogView
from annalist.views.site                import SiteView, SiteActionView
from annalist.views.collection          import CollectionView, CollectionEditView
from annalist.views.annalistuserdelete  import AnnalistUserDeleteConfirmedView
from annalist.views.recordtypedelete    import RecordTypeDeleteConfirmedView
from annalist.views.recordviewdelete    import RecordViewDeleteConfirmedView
from annalist.views.recordlistdelete    import RecordListDeleteConfirmedView
from login.login_views                  import LoginUserView, LoginPostView, LogoutUserView
from login.auth_oidc_client             import OIDC_AuthDoneView
from login.auth_django_client           import LocalUserPasswordView

from annalist.views.entityedit          import GenericEntityEditView
from annalist.views.entitylist          import EntityGenericListView
from annalist.views.entitylistjson      import EntityGenericListJsonView
from annalist.views.entitydelete        import EntityDataDeleteConfirmedView

from annalist.views.siteresource        import SiteResourceAccess
from annalist.views.collectionresource  import CollectionResourceAccess
from annalist.views.entityresource      import EntityResourceAccess


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
# /c/<coll-id>/l/<list-id>/                       specified list of records
# /c/<coll-id>/l/<list-id>/<type-id>              specified list of records of specified type
# /c/<coll-id>/v/<view-id>/<type-id>/<entity-id>  specified view of record
#
# Suffixes /!new, /!copy, /!edit, /!delete, etc. are used for forms that are opart of the
# user interface for editing collections and resources, and do not of themselves identify
# persistent resources.

urlpatterns = patterns('',

    # Site pages
    url(r'^$',              AnnalistHomeView.as_view(),     name='AnnalistHomeView'),
    url(r'^site/$',         SiteView.as_view(),             name='AnnalistSiteView'),
    url(r'^site/!action$',  SiteActionView.as_view(),       name='AnnalistSiteActionView'),
    url(r'^confirm/$',      ConfirmView.as_view(),          name='AnnalistConfirmView'),
    url(r'^serverlog/$',    ServerLogView.as_view(),        name='AnnalistServerLogView'),

    # Special forms
    url(r'^c/(?P<coll_id>\w{1,128})/$',
                            CollectionView.as_view(),
                            name='AnnalistCollectionView'),
    url(r'^c/(?P<coll_id>\w{1,128})/!edit$',
                            CollectionEditView.as_view(),
                            name='AnnalistCollectionEditView'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/users/!delete_confirmed$',
                            AnnalistUserDeleteConfirmedView.as_view(),
                            name='AnnalistUserDeleteView'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/types/!delete_confirmed$',
                            RecordTypeDeleteConfirmedView.as_view(),
                            name='AnnalistRecordTypeDeleteView'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/views/!delete_confirmed$',
                            RecordViewDeleteConfirmedView.as_view(),
                            name='AnnalistRecordViewDeleteView'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/lists/!delete_confirmed$',
                            RecordListDeleteConfirmedView.as_view(),
                            name='AnnalistRecordListDeleteView'),

    # Default/API access lists and data
    # (these may content negotiate for various formats)
    url(r'^c/(?P<coll_id>\w{1,128})/d/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultListAll'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultListType'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/!delete_confirmed$',
                            EntityDataDeleteConfirmedView.as_view(),
                            name='AnnalistEntityDataDeleteView'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityAccessView'),

    # JSON list views without list_id specified
    url(r'^c/(?P<coll_id>\w{1,128})/d/entity_list\.jsonld$',
                            EntityGenericListJsonView.as_view(),
                            name='AnnalistEntityJsonListAll'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/entity_list\.jsonld$',
                            EntityGenericListJsonView.as_view(),
                            name='AnnalistEntityJsonListType'),

    # Redirect type/entity URIs without trailing '/'
    # (Note these cannot match JSON resource names as '.' is not matched here)
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})$',
                            AnnalistTypeRedirect.as_view(),
                            name='AnnalistTypeRedirect'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})$',
                            AnnalistEntityRedirect.as_view(),
                            name='AnnalistEntityRedirect'),

    # Specified list views
    url(r'^c/(?P<coll_id>\w{1,128})/l/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityDefaultList'),
    url(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),
    url(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/(?P<type_id>\w{1,128})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),

    # JSON list views
    url(r'^c/(?P<coll_id>\w{1,128})/l/entity_list\.jsonld$',
                            EntityGenericListJsonView.as_view(),
                            name='AnnalistEntityJsonListAll'),
    url(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/entity_list\.jsonld$',
                            EntityGenericListJsonView.as_view(),
                            name='AnnalistEntityJsonListAll'),
    url(r'^c/(?P<coll_id>\w{1,128})/l/(?P<list_id>\w{1,128})/(?P<type_id>\w{1,128})/entity_list\.jsonld$',
                            EntityGenericListJsonView.as_view(),
                            name='AnnalistEntityJsonListType'),

    # Specified entity edit/view forms
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityDataView'),
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/!(?P<action>new)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityNewView'),
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>copy)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>edit)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/!(?P<action>view)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),

    # Additional resource access (context, attachments, etc.)
    url(r'^site/(?P<resource_ref>[\w.-]{1,250})$',
                            SiteResourceAccess.as_view(),
                            name='AnnalistSiteResourceAccess'),

    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<resource_ref>[\w.-]{1,250})$',
                            CollectionResourceAccess.as_view(),
                            name='AnnalistCollectionResourceAccess'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistEntityResourceAccess'),
    url(r'^c/(?P<coll_id>\w{1,128})/d/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/d/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistCollectionResourceAccess'),

    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistEntityResourceAccess'),
    url(r'^c/(?P<coll_id>\w{1,128})/v/(?P<view_id>\w{1,128})/(?P<type_id>\w{1,128})/(?P<entity_id>\w{1,128})/d/(?P<resource_ref>[\w.-]{1,250})$',
                            EntityResourceAccess.as_view(),
                            name='AnnalistCollectionResourceAccess'),

    ) # End of urlpatterns

urlpatterns += patterns('',
    url(r'^login/$',        LoginUserView.as_view(),            name='LoginUserView'),
    url(r'^login_post/$',   LoginPostView.as_view(),            name='LoginPostView'),
    url(r'^login_local/$',  LocalUserPasswordView.as_view(),    name='LocalUserPasswordView'),
    url(r'^login_done/',    OIDC_AuthDoneView.as_view(),        name='OIDC_AuthDoneView'),
    url(r'^profile/$',      ProfileView.as_view(),              name='AnnalistProfileView'),
    url(r'^logout/$',       LogoutUserView.as_view(),           name='LogoutUserView'),
    )

# End.
