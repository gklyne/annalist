"""
Field group functions to support testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse

import logging
log = logging.getLogger(__name__)

# from django.conf                import settings
# from django.utils.http          import urlquote, urlunquote
from django.core.urlresolvers   import resolve, reverse

from annalist.util              import valid_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

from entity_testutils           import (
    collection_dir, 
    collection_entity_view_url
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordgroup_dir(coll_id="testcoll", group_id="testgroup"):
    return collection_dir(coll_id) + layout.COLL_GROUP_PATH%{'id': group_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordgroup_site_url(site, group_id="testgroup"):
    return site._entityurl + layout.SITE_GROUP_PATH%{'id': group_id} + "/"

def recordgroup_coll_url(site, coll_id="testcoll", group_id="testgroup"):
    return (
        site._entityurl + 
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_GROUP_PATH%{'id': group_id} + "/"
        )

def recordgroup_url(coll_id, group_id):
    """
    URI for group description data; also view using default entity view
    """
    if not valid_id(group_id):
        return None
        # group_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_group", entity_id=group_id)

def recordgroup_edit_url(action=None, coll_id=None, group_id=None):
    """
    URI for group description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordFieldDeleteView' if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id, 'type_id': "_field", 'view_id': "Field_view"}
    if action != "delete":
        kwargs.update({'action': action})
    if group_id:
        if valid_id(group_id):
            kwargs.update({'entity_id': group_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordGroup data
#
#   -----------------------------------------------------------------------------

def _todo_recordgroup_init_keys(field_uri=False):
    keys = set(
        [ 'annal:id'
        , 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label'
        , 'rdfs:comment'
        , 'annal:field_render_type'
        , 'annal:field_value_mode'
        ])
    if field_uri:
        keys.add('annal:uri')
    return keys

def _todo_recordgroup_value_keys(field_uri=False):
    return (recordgroup_init_keys(field_uri=field_uri) |
        { 'annal:property_uri'
        , 'annal:field_entity_type'
        , 'annal:field_value_type'
        , 'annal:field_placement'
        , 'annal:placeholder'
        , 'annal:default_value'
        })

def _todo_recordgroup_load_keys(field_uri=False):
    return recordgroup_value_keys(field_uri=field_uri) | {'@id', '@type'}

def _todo_recordgroup_create_values(coll_id="testcoll", group_id="testgroup", 
        render_type="Text", value_mode="Value_direct",
        update="Field"):
    """
    Entity values used when creating a group entity
    """
    return (
        { 'rdfs:label':                 "%s %s/_field/%s"%(update, coll_id, group_id)
        , 'rdfs:comment':               "%s help for %s in collection %s"%(update, group_id, coll_id)
        , 'annal:field_render_type':    render_type
        , 'annal:field_value_mode':     value_mode
        })

def _todo_recordgroup_values(
        coll_id="testcoll", group_id="testgroup", field_uri=None,
        render_type="Text", value_mode="Value_direct",
        update="Field", hosturi=TestHostUri):
    d = recordgroup_create_values(
        coll_id, group_id, 
        render_type=render_type, value_mode=value_mode, 
        update=update
        ).copy()
    d.update(
        { 'annal:id':                   group_id
        , 'annal:type_id':              "_field"
        , 'annal:type':                 "annal:Field"
        , 'annal:url':                  recordgroup_url(coll_id, group_id)
        })
    if field_uri:
        d['annal:uri'] = field_uri
    return d

def _todo_recordgroup_read_values(
        coll_id="testcoll", group_id="testgroup",
        update="Field", hosturi=TestHostUri):
    d = recordgroup_values(coll_id, group_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:Field"]
        })
    return d

# End.
