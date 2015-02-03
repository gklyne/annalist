"""
Record field data functions to support entity data testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.http                import QueryDict
from django.utils.http          import urlquote, urlunquote
from django.core.urlresolvers   import resolve, reverse

from annalist.util              import valid_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testentitydata      import entitydata_list_type_url
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils import (
    collection_dir, 
    collection_edit_url,
    collection_entity_view_url,
    site_title
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordtype_dir(coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_TYPE_PATH%{'id': type_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordtype_site_url(site, type_id="testtype"):
    return site._entityurl + layout.SITE_TYPE_PATH%{'id': type_id} + "/"

def recordtype_coll_url(site, coll_id="testcoll", type_id="testtype"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_TYPE_PATH%{'id': type_id} + "/"

def recordtype_url(coll_id="testcoll", type_id="testtype"):
    """
    URL for record type description data; also view using default entity view
    """
    if not valid_id(type_id):
        type_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_type", entity_id=type_id)

def recordtype_edit_url(action=None, coll_id=None, type_id=None):
    """
    URI for record type description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordTypeDeleteView'  if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_type", 'view_id': "Type_view"})
    if type_id:
        if valid_id(type_id):
            kwargs.update({'entity_id': type_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordType data
#
#   -----------------------------------------------------------------------------

def recordtype_value_keys(type_uri=False):
    ks = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type', 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:type_view', 'annal:type_list'
        ])
    if type_uri:
        ks.add('annal:uri')
    return ks

def recordtype_load_keys(type_uri=False):
    return recordtype_value_keys(type_uri=type_uri) | {'@id', '@type'}

def recordtype_create_values(coll_id="testcoll", type_id="testtype", update="RecordType"):
    """
    Entity values used when creating a record type entity
    """
    d = (
        { 'annal:type':         "annal:Type"
        , 'rdfs:label':         "%s %s/%s"%(update, coll_id, type_id)
        , 'rdfs:comment':       "%s help for %s in collection %s"%(update, type_id, coll_id)
        , 'annal:type_view':    "Default_view"
        , 'annal:type_list':    "Default_list"
        })
    return d

def recordtype_values(
        coll_id="testcoll", type_id="testtype", type_uri=None,
        update="RecordType", hosturi=TestHostUri):
    type_url = recordtype_url(coll_id=coll_id, type_id=type_id)
    d = recordtype_create_values(coll_id, type_id, update=update).copy()
    d.update(
        { 'annal:id':       type_id
        , 'annal:type_id':  "_type"
        , 'annal:url':      type_url
        # , 'annal:uri':      type_uri    # @@TODO: isn't this part of create_values?
        })
    if type_uri:
        d['annal:uri'] = type_uri
    return d

def recordtype_read_values(
        coll_id="testcoll", type_id="testtype", 
        update="RecordType", hosturi=TestHostUri):
    d = recordtype_values(coll_id, type_id,
        update=update,
        hosturi=hosturi
        ).copy()
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:Type"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordtype view
#
#   -----------------------------------------------------------------------------

def recordtype_entity_view_context_data(
        coll_id="testcoll", type_id=None, orig_id=None, type_ids=[],
        action=None, update="RecordType"
    ):
    context_dict = (
        { 'title':              "Collection %s"%(coll_id)
        , 'coll_id':            coll_id
        , 'type_id':            '_type'
        , 'orig_id':            'orig_type_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_name':         'entity_id'
            , 'field_render_type':  'EntityId'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Type_id'
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_name':         'Type_label'
            , 'field_render_type':  'Text'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_label'
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_name':         'Type_comment'
            , 'field_render_type':  'Textarea'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_comment'
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_label':        'URI'
            , 'field_name':         'Type_uri'
            , 'field_render_type':  'Identifier'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_uri'
            , 'field_value_type':   'annal:Identifier'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Default view'
            , 'field_name':         'Type_view'
            , 'field_render_type':  'View'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Type_view'
            , 'field_value_type':   'annal:View'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Default list'
            , 'field_name':         'Type_list'
            , 'field_render_type':  'List'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_id':           'Type_list'
            , 'field_value_type':   'annal:List'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_type")
        })
    if type_id:
        type_url = recordtype_url(coll_id=coll_id, type_id=type_id)
        context_dict['fields'][0]['field_value'] = type_id
        context_dict['fields'][1]['field_value'] = '%s %s/%s'%(update, coll_id, type_id)
        context_dict['fields'][2]['field_value'] = '%s help for %s in collection %s'%(update, type_id, coll_id)
        context_dict['fields'][3]['field_value'] = type_url
        context_dict['orig_id']     = type_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordtype_entity_view_form_data(
        coll_id="testcoll", 
        type_id=None, orig_id=None, 
        action=None, cancel=None, close=None, edit=None, copy=None, 
        update="RecordType"
        ):
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_type_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_type")
        })
    if type_id:
        type_url = recordtype_url(coll_id=coll_id, type_id=type_id)
        form_data_dict['entity_id']     = type_id
        form_data_dict['orig_id']       = type_id
        form_data_dict['Type_label']    = '%s %s/%s'%(update, coll_id, type_id)
        form_data_dict['Type_comment']  = '%s help for %s in collection %s'%(update, type_id, coll_id)
        form_data_dict['Type_uri']      = type_url
        form_data_dict['Type_view']     = "Default_view"
        form_data_dict['Type_list']     = "Default_list"
        form_data_dict['orig_type']     = "_type"
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
#   ----- Recordtype delete confirmation form data
#
#   -----------------------------------------------------------------------------

def recordtype_delete_form_data(type_id=None, list_id="Default_list"):
    return (
        { 'list_choice':        list_id
        , 'continuation_url':   ""
        , 'search_for':         ""
        , 'entity_select':      ["_type/%s"%(type_id)]
        , 'delete':             "Delete"
        })

def recordtype_delete_confirm_form_data(type_id=None):
    return (
        { 'typelist':    type_id,
          'type_delete': 'Delete'
        })

# End.
