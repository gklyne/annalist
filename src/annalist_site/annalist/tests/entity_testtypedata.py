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

from django.conf                    import settings
from django.http                    import QueryDict
from django.utils.http              import urlquote, urlunquote
from django.core.urlresolvers       import resolve, reverse

from annalist.util                  import valid_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.fields.render_utils   import get_placement_classes

from tests                          import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils               import (
    collection_dir, 
    collection_edit_uri,
    site_title
    )
from entity_testentitydata          import (
    entitydata_list_type_uri
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

def recordtype_site_uri(site, type_id="testtype"):
    return site._entityuri + layout.SITE_TYPE_PATH%{'id': type_id} + "/"

def recordtype_coll_uri(site, coll_id="testcoll", type_id="testtype"):
    return site._entityuri + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_TYPE_PATH%{'id': type_id} + "/"

def recordtype_uri(coll_id="testcoll", type_id="testtype"):
    """
    URI for record type description data; also view using default entity view
    """
    viewname = "AnnalistEntityAccessView"
    kwargs   = {'coll_id': coll_id, "type_id": "_type"}
    if valid_id(type_id):
        kwargs.update({'entity_id': type_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordtype_edit_uri(action=None, coll_id=None, type_id=None):
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

def recordtype_value_keys():
    ks = set(
        [ 'annal:id', 'annal:type'
        , 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:type_view', 'annal:type_list'
        ])
    return ks

def recordtype_load_keys():
    return recordtype_value_keys() | {"@id"}

def recordtype_create_values(coll_id="testcoll", type_id="testtype", update="RecordType"):
    """
    Entity values used when creating a record type entity
    """
    d = (
        { 'rdfs:label':         "%s %s/%s"%(update, coll_id, type_id)
        , 'rdfs:comment':       "%s help for %s in collection %s"%(update, type_id, coll_id)
        , 'annal:type_view':    "Default_view"
        , 'annal:type_list':    "Default_list"
        })
    return d

def recordtype_values(
        coll_id="testcoll", type_id="testtype", 
        update="RecordType", hosturi=TestHostUri):
    d = recordtype_create_values(coll_id, type_id, update=update).copy()
    d.update(
        { 'annal:id':       type_id
        , 'annal:type':     "annal:Type"
        , 'annal:uri':      hosturi + recordtype_uri(coll_id, type_id)
        })
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
        { 'title':              site_title()
        , 'coll_id':            coll_id
        , 'type_id':            '_type'
        , 'orig_id':            'orig_type_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Type_id'
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'Type_label'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_label'
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_name':         'Type_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_comment'
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_label':        'URI'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'Type_uri'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_uri'
            , 'field_value_type':   'annal:Text'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Default view'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'Type_view'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_view'
            , 'field_value_type':   'annal:Text'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Default list'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'Type_list'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_list'
            , 'field_value_type':   'annal:Text'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          ]
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, "_type")
        })
    if type_id:
        context_dict['fields'][0]['field_value'] = type_id
        context_dict['fields'][1]['field_value'] = '%s %s/%s'%(update, coll_id, type_id)
        context_dict['fields'][2]['field_value'] = '%s help for %s in collection %s'%(update, type_id, coll_id)
        context_dict['fields'][3]['field_value'] = TestBaseUri + "/c/%s/d/_type/%s/"%(coll_id, type_id)
        context_dict['orig_id']     = type_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordtype_entity_view_form_data(
        coll_id="testcoll", 
        type_id=None, orig_id=None, 
        action=None, cancel=None, update="RecordType"):
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_type_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, "_type")
        })
    if type_id:
        form_data_dict['entity_id']     = type_id
        form_data_dict['orig_id']       = type_id
        form_data_dict['Type_label']    = '%s %s/%s'%(update, coll_id, type_id)
        form_data_dict['Type_comment']  = '%s help for %s in collection %s'%(update, type_id, coll_id)
        form_data_dict['Type_uri']      = TestBaseUri + "/c/%s/d/_type/%s/"%(coll_id, type_id)
        form_data_dict['Type_view']     = "Default_view"
        form_data_dict['Type_list']     = "Default_list"
        form_data_dict['orig_type']     = "_type"
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Recordtype delete confirmation form data
#
#   -----------------------------------------------------------------------------

def recordtype_delete_confirm_form_data(type_id=None):
    return (
        { 'typelist':    type_id,
          'type_delete': 'Delete'
        })

# End.
