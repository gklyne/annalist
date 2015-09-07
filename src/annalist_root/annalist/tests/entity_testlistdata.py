"""
Utility functions to support entity data testing
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

from entity_testutils           import (
    collection_dir, 
    site_title, 
    collection_entity_view_url
    )
from entity_testentitydata      import entitydata_list_type_url
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordlist_dir(coll_id="testcoll", list_id="testlist"):
    return collection_dir(coll_id) + layout.COLL_LIST_PATH%{'id': list_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordlist_site_url(site, list_id="testlist"):
    return site._entityurl + layout.SITE_LIST_PATH%{'id': list_id} + "/"

def recordlist_coll_url(site, coll_id="testcoll", list_id="testlist"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_LIST_PATH%{'id': list_id} + "/"

def recordlist_url(coll_id, list_id):
    """
    URI for record list description data; also view using default entity view
    """
    if not valid_id(list_id):
        list_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_list", entity_id=list_id)

def recordlist_edit_url(action=None, coll_id=None, list_id=None):
    """
    URI for record list description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordListDeleteView'  if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_list", 'view_id': "List_view"})
    if list_id:
        if valid_id(list_id):
            kwargs.update({'entity_id': list_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordList data
#
#   -----------------------------------------------------------------------------

def recordlist_value_keys(list_uri=False):
    keys = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:display_type'
        , 'annal:list_entity_selector'
        , 'annal:default_view'
        , 'annal:default_type'
        , 'annal:list_fields'
        ])
    if list_uri:
        keys.add('annal:uri')
    return keys

def recordlist_load_keys(list_uri=False):
    return recordlist_value_keys(list_uri=list_uri) | {'@id', '@type'}

def recordlist_create_values(
        coll_id="testcoll", list_id="testlist", list_uri=None, update="RecordList"):
    """
    Entity values used when creating a record list entity
    """
    d = (
        { 'annal:type':                 "annal:List"
        , 'rdfs:label':                 "%s %s/%s"%(update, coll_id, list_id)
        , 'rdfs:comment':               "%s help for %s/%s"%(update, coll_id, list_id)
        , "annal:display_type":         "List"
        , "annal:default_view":         "_view/Default_view"
        , "annal:default_type":         "_type/Default_type"
        , "annal:list_entity_selector": "ALL"
        , "annal:list_fields":
          [ { "annal:field_id":             "_field/Entity_id"
            , "annal:field_placement":      "small:0,3"
            }
          , { "annal:field_id":             "_field/Entity_label"
            , "annal:field_placement":      "small:3,9"
            }
          ]
        })
    if list_uri:
        d['annal:uri'] = list_uri
    return d

def recordlist_values(
        coll_id="testcoll", list_id="testlist", list_uri=None,
        update="RecordList", hosturi=TestHostUri):
    list_url = recordlist_url(coll_id, list_id)
    d = recordlist_create_values(coll_id, list_id, list_uri=list_uri, update=update).copy()
    d.update(
        { 'annal:id':       list_id
        , 'annal:type_id':  "_list"
        , 'annal:url':      list_url
        })
    return d

def recordlist_read_values(
        coll_id="testcoll", list_id="testlist", 
        update="RecordList", hosturi=TestHostUri):
    d = recordlist_values(coll_id, list_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:List"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Data in recordlist view for list description data
#
#   -----------------------------------------------------------------------------

def recordlist_view_context_data(
        coll_id="testcoll", list_id=None, orig_id=None, view_ids=[],
        action=None, update="RecordList"
    ):
    list_fields = (
        [ { "annal:field_id":         "_field/Entity_id"
          , "annal:field_placement":  "small:0,3"
          }
        , { "annal:field_id":         "_field/Entity_label"
          , "annal:field_placement":  "small:3,9"
          }
        ])
    context_dict = (
        { 'title':              "Collection %s"%(coll_id)
        , 'coll_id':            coll_id
        , 'type_id':            '_list'
        , 'orig_id':            'orig_list_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_list")
        , 'fields':
          [ { 'field_id':           'List_id'                   # fields[0]
            , 'field_name':         'entity_id'
            , 'field_target_type':  'annal:Slug'
            , 'field_label':        'Id'
            , 'field_render_type':  'Slug'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            # , 'field_value':      (Supplied separately, below)
            , 'options':            []
            }
          , { 'field_id':           'List_type'                 # fields[1]
            , 'field_name':         'List_type'
            , 'field_target_type':  'annal:List_type'
            , 'field_label':        'List display type'
            , 'field_render_type':  'Enum_choice'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value':        'List'
            , 'options':            [] # ['list', 'grid']
            }
          , { 'field_id':           'List_label'                # fields[2]
            , 'field_name':         'List_label'
            , 'field_target_type':  'annal:Text'
            , 'field_label':        'Label'
            , 'field_render_type':  'Text'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            # , 'field_value':      (Supplied separately, below)
            , 'options':            []
            }
          , { 'field_id':           'List_comment'              # fields[3]
            , 'field_name':         'List_comment'
            , 'field_label':        'Help'
            , 'field_target_type':  'annal:Richtext'
            , 'field_render_type':  'Markdown'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            # , 'field_value':      (Supplied separately, below)
            , 'options':            []
            }
          , { 'field_id':           'List_default_type'         # fields[4]
            , 'field_name':         'List_default_type'
            , 'field_target_type':  'annal:Type'
            , 'field_label':        'Record type'
            , 'field_render_type':  'Enum_optional'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value':        '_type/Default_type'
            , 'options':            []
            }
          , { 'field_id':           'List_default_view'         # fields[5]
            , 'field_name':         'List_default_view'
            , 'field_target_type':  'annal:View'
            , 'field_label':        'View'
            , 'field_render_type':  'Enum_optional'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_value':        '_view/Default_view'
            , 'options':            []
            }
          , { 'field_id':           'List_entity_selector'      # fields[6]
            , 'field_name':         'List_entity_selector'
            , 'field_target_type':  'annal:Text'
            , 'field_label':        'Selector'
            , 'field_render_type':  'Text'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        'ALL'
            , 'options':            []
            }
          , { 'field_id':           'List_target_type'          # fields[7]
            , 'field_name':         'List_target_type'
            , 'field_target_type':  'annal:Identifier'
            , 'field_label':        'Record type URI'
            , 'field_render_type':  'Identifier'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        ''
            , 'options':            []
            }
          , { "field_id":           "List_fields"           # fields[8]
            , 'field_name':         'List_fields'
            , 'field_target_type':  'annal:Field_group'
            , 'field_label':        'Fields'
            , 'field_render_type':  'RepeatGroupRow'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        list_fields
            , 'options':            []
            }
          ]
        })
    if list_id:
        context_dict['fields'][0]['field_value'] = list_id
        context_dict['fields'][2]['field_value'] = '%s %s/%s'%(update, coll_id, list_id)
        context_dict['fields'][3]['field_value'] = '%s help for %s/%s'%(update, coll_id, list_id)
        context_dict['orig_id']     = list_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordlist_view_form_data(
        coll_id="testcoll", 
        list_id=None, orig_id=None, 
        action=None, cancel=None,
        update="RecordView"):
    form_data_dict = (
        { 'List_type':              'List'
        , 'List_label':             '%s list (%s/@@list_id@@)'%(update, coll_id)
        , 'List_comment':           '%s help (%s/@@list_id@@)'%(update, coll_id)
        # , 'List_type':      'List'
        , 'List_default_type':      '_type/Default_type'
        , 'List_default_view':      '_view/Default_view'
        , 'List_entity_selector':   'ALL'
        # List repeating fields
        , 'List_fields__0__Field_id':           "_field/Entity_id"
        , 'List_fields__0__Field_placement':    "small:0,3"
        , 'List_fields__1__Field_id':           "_field/Entity_label"
        , 'List_fields__1__Field_placement':    "small:3,9"
        # Hidden fields
        , 'action':                 '@@TBD@@'
        , 'view_id':                'List_view'
        , 'orig_id':                'orig_list_id'
        , 'orig_type':              '_list'
        , 'continuation_url':       entitydata_list_type_url(coll_id, "_list")        
        })
    if list_id:
        form_data_dict['entity_id']     = list_id
        form_data_dict['orig_id']       = list_id
        form_data_dict['List_label']    = '%s %s/%s'%(update, coll_id, list_id)
        form_data_dict['List_comment']  = '%s help for %s/%s'%(update, coll_id, list_id)
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
#   ----- Recordview delete confirmation form data
#
#   -----------------------------------------------------------------------------

def recordlist_delete_confirm_form_data(list_id=None):
    return (
        { 'listlist':    list_id,
          'list_delete': 'Delete'
        })

# End.
