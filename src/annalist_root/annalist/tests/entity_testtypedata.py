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
        return None
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

def recordtype_value_keys(type_uri=False, supertype_uris=False):
    ks = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:type_view', 'annal:type_list'
        ])
    if type_uri:
        ks.add('annal:uri')
    if supertype_uris:
        ks.add('annal:supertype_uris')
    return ks

def recordtype_load_keys(type_uri=False, supertype_uris=False):
    return recordtype_value_keys(type_uri=type_uri, supertype_uris=supertype_uris) | {'@id', '@type'}

def recordtype_create_values(
        coll_id="testcoll", type_id="testtype", update="RecordType",
        type_uri=None, supertype_uris=None
        ):
    """
    Entity values used when creating a record type entity
    """
    d = (
        { 'annal:type':         "annal:Type"
        , 'rdfs:label':         "%s %s/%s"%(update, coll_id, type_id)
        , 'rdfs:comment':       "%s help for %s in collection %s"%(update, type_id, coll_id)
        , 'annal:type_view':    "_view/Default_view"
        , 'annal:type_list':    "_list/Default_list"
        })
    if type_uri:
        d['annal:uri'] = type_uri
        if supertype_uris is not None:
            d['annal:supertype_uris'] = (
                [ { 'annal:supertype_uri': st } for st in supertype_uris ]
                )
        else:
            d['annal:supertype_uris'] = (
                [ { 'annal:supertype_uri': type_uri+"/super1" }
                , { 'annal:supertype_uri': type_uri+"/super2" }
                ])
    return d

def recordtype_values(
        coll_id="testcoll", type_id="testtype", type_uri=None,
        update="RecordType", hosturi=TestHostUri):
    type_url = recordtype_url(coll_id=coll_id, type_id=type_id)
    d = recordtype_create_values(
        coll_id, type_id, update=update, type_uri=type_uri
        ).copy()
    d.update(
        { 'annal:id':       type_id
        , 'annal:type_id':  "_type"
        , 'annal:url':      type_url
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
        action=None, update="RecordType",
        type_uri=None, supertype_uris=None #@@ need to deal with these.
    ):
    context_dict = (
        { 'title':              "Collection %s"%(coll_id)
        , 'coll_id':            coll_id
        , 'type_id':            '_type'
        , 'orig_id':            'orig_type_id'
        , 'fields':
          [ { 'field_id':           'Type_id'
            , 'field_name':         'entity_id'
            , 'field_target_type':  'annal:Slug'
            , 'field_label':        'Id'
            , 'field_render_type':  'EntityId'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_id':           'Type_label'
            , 'field_name':         'Type_label'
            , 'field_target_type':  'annal:Text'
            , 'field_label':        'Label'
            , 'field_render_type':  'Text'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        '%s data ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_id':           'Type_comment'
            , 'field_name':         'Type_comment'
            , 'field_label':        'Comment'
            , 'field_target_type':  'annal:Richtext'
            , 'field_render_type':  'Markdown'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        '%s description ... (%s/%s)'%(update, coll_id, type_id)
            , 'options':            []
            }
          , { 'field_id':           'Type_uri'
            , 'field_name':         'Type_uri'
            , 'field_target_type':  'annal:Identifier'
            , 'field_label':        'URI'
            , 'field_render_type':  'Identifier'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_id':           'Type_supertype_uris'
            , 'field_name':         'Type_supertype_uris'
            , 'field_target_type':  'annal:Type_supertype_uri'
            , 'field_label':        'Supertype URIs'
            , 'field_render_type':  'RepeatGroupRow'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_id':           'Type_view'
            , 'field_name':         'Type_view'
            , 'field_target_type':  'annal:View'
            , 'field_label':        'Default view'
            , 'field_render_type':  'Enum_optional'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_id':           'Type_list'
            , 'field_name':         'Type_list'
            , 'field_target_type':  'annal:List'
            , 'field_label':        'Default list'
            , 'field_render_type':  'Enum_optional'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
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
        context_dict['fields'][3]['field_value'] = type_url or ""
        context_dict['orig_id']     = type_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordtype_entity_view_form_data(
        coll_id="testcoll", 
        type_id=None, orig_id=None, 
        action=None, cancel=None, close=None, edit=None, copy=None, task=None,
        update="RecordType",
        type_uri=None
        ):
    """
    Returns a request dictionary that can be used with the Django test client.
    Per Django documentation, multiple values for a key are provided as a list.
    See: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#making-requests
    """
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_type_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_type")
        })
    if type_id:
        type_url  = recordtype_url(coll_id=coll_id, type_id=type_id)
        type_help = '%s help for %s in collection %s'%(update, type_id, coll_id)
        form_data_dict['entity_id']           = type_id
        form_data_dict['orig_id']             = type_id
        form_data_dict['Type_label']          = '%s %s/%s'%(update, coll_id, type_id)
        form_data_dict['Type_comment']        = type_help
        form_data_dict['Type_uri']            = type_url or ""
        form_data_dict['Type_view']           = "_view/Default_view"
        form_data_dict['Type_list']           = "_list/Default_list"
        form_data_dict['orig_type']           = "_type"
    if orig_id:
        form_data_dict['orig_id']   = orig_id
    if action:
        form_data_dict['action']    = action
    if cancel:
        form_data_dict['cancel']    = "Cancel"
    elif close:
        form_data_dict['close']     = "Close"
    elif edit:
        form_data_dict['edit']      = "Edit"
    elif copy:
        form_data_dict['copy']      = "Copy"
    elif task:
        form_data_dict[task]        = task
    else:
        form_data_dict['save']      = "Save"
    if type_uri:
        form_data_dict['Type_uri']                                   = type_uri
        form_data_dict['Type_supertype_uris__0__Type_supertype_uri'] = type_uri+"/super1"
        form_data_dict['Type_supertype_uris__1__Type_supertype_uri'] = type_uri+"/super2"
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Recordtype delete confirmation form data
#
#   -----------------------------------------------------------------------------

def recordtype_delete_form_data(type_id=None, list_id="Default_list"):
    return (
        { 'list_choice':        "_list/"+list_id
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
