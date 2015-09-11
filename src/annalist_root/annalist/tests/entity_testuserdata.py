"""
Tests for AnnalistUser module and view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.core.urlresolvers           import resolve, reverse

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.util                      import valid_id

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir

from entity_testutils                   import (
    site_dir, collection_dir,
    collection_entity_view_url
    )
from entity_testentitydata          import (
    entitydata_list_type_url, entitydata_list_all_url,
    )


#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def annalistuser_dir(coll_id="testcoll", user_id="testuser"):
    return collection_dir(coll_id) + layout.COLL_USER_PATH%{'id': user_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def annalistuser_site_url(site, user_id="testuser"):
    return site._entityurl + layout.SITE_USER_PATH%{'id': user_id} + "/"

def annalistuser_coll_url(site, coll_id="testcoll", user_id="testuser"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_USER_PATH%{'id': user_id} + "/"

def annalistuser_url(coll_id="testcoll", user_id="testuser"):
    """
    URI for record type description data; also view using default entity view
    """
    if not valid_id(user_id):
        user_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_user", entity_id=user_id)

def annalistuser_edit_url(action=None, coll_id=None, user_id=None):
    """
    URI for record type description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistUserDeleteView'        if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_type", 'view_id': "User_view"})
    if user_id:
        if valid_id(user_id):
            kwargs.update({'entity_id': user_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- AnnalistUser data
#
#   -----------------------------------------------------------------------------

def annalistuser_value_keys():
    keys = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:user_uri'
        , 'annal:user_permissions'
        ])
    return keys

def annalistuser_load_keys():
    return annalistuser_value_keys() | {'@id', '@type'}

def annalistuser_create_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"]
        ):
    """
    Values used when creating a user record
    """
    d = (
        { 'annal:type':             "annal:User"
        , 'rdfs:label':             user_name
        , 'rdfs:comment':           "User %s: permissions for %s in collection %s"%(user_id, user_name, coll_id)
        , 'annal:user_uri':         user_uri
        , 'annal:user_permissions': user_permissions
        })
    return d

def annalistuser_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
        hosturi=TestHostUri):
    """
    Values filled in automatically when a user record is created
    """
    user_url = annalistuser_url(coll_id, user_id)
    d = annalistuser_create_values(coll_id, user_id, user_name, user_uri, user_permissions)
    d.update(
        { 'annal:id':       user_id
        , 'annal:type_id':  "_user"
        , 'annal:url':      user_url
        })
    return d

def annalistuser_read_values(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG", "ADMIN"],
        hosturi=TestHostUri):
    d = annalistuser_values(
            coll_id, user_id, user_name, user_uri, user_permissions,
            hosturi=hosturi
            )
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:User"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- User edit form data
#
#   -----------------------------------------------------------------------------

def annalistuser_view_form_data(
        coll_id="testcoll", user_id="testuser",
        user_name="Test User",
        user_uri="mailto:testuser@example.org", 
        user_permissions="VIEW CREATE UPDATE DELETE CONFIG ADMIN",
        action=None, cancel=None, close=None, edit=None, copy=None, 
        orig_id=None
        ):
    form_data_dict = (
        { 'entity_id':          user_id
        , 'orig_id':            user_id
        , 'User_name':          user_name
        , 'User_description':   'User %s: permissions for %s in collection %s'%(user_id, user_name, coll_id)
        , 'User_uri':           user_uri
        , 'User_permissions':   user_permissions
        , 'orig_type':          "_user"
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_user")
        })
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    elif close:
        form_data_dict['close']         = "Close"
    elif edit:
        form_data_dict['edit']          = "Edit"
    elif copy:
        form_data_dict['copy']          = "Copy"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- User delete & confirmation form data
#
#   -----------------------------------------------------------------------------

def annalistuser_delete_form_data(user_id=None, list_id="Default_list"):
    return (
        { 'list_choice':        "_list/"+list_id
        , 'continuation_url':   ""
        , 'search_for':         ""
        , 'entity_select':      ["_user/%s"%(user_id)]
        , 'delete':             "Delete"
        })

def annalistuser_delete_confirm_form_data(user_id=None):
    return (
        { 'entity_id':     user_id,
          'entity_delete': 'Delete'
        })

# End.
