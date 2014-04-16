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
    # recordtype_create_values, 
    # collection_create_values,
    # site_dir, 
    collection_dir, 
    # recordtype_dir, recorddata_dir,  entitydata_dir,
    collection_edit_uri,
    # recordtype_edit_uri,
    # entity_uri, entitydata_edit_uri, 
    # entitydata_list_type_uri,
    # recordtype_form_data,
    # entitydata_value_keys, entitydata_create_values, entitydata_values,
    # entitydata_recordtype_view_context_data, 
    # # entitydata_context_data, 
    # entitydata_recordtype_view_form_data,
    # # entitydata_form_data, 
    # entitydata_delete_confirm_form_data,
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

def recordtype_uri(coll_id="testcoll", type_id="testtype"):
    viewname = "AnnalistRecordTypeAccessView"
    kwargs   = {'coll_id': coll_id}
    if valid_id(type_id):
        kwargs.update({'type_id': type_id})
    else:
        kwargs.update({'type_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordtype_view_uri(coll_id="testcoll", type_id="testtype"):
    viewname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': "_type"}
    if valid_id(type_id):
        kwargs.update({'entity_id': type_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordtype_edit_uri(action, coll_id, type_id=None):
    viewname = ( 
        'AnnalistRecordTypeNewView'     if action == "new"    else
        'AnnalistRecordTypeCopyView'    if action == "copy"   else
        'AnnalistRecordTypeEditView'    if action == "edit"   else
        'AnnalistRecordTypeDeleteView'  if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action})
    if type_id:
        if valid_id(type_id):
            kwargs.update({'type_id': type_id})
        else:
            kwargs.update({'type_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordType data
#
#   -----------------------------------------------------------------------------

def recordtype_value_keys():
    return set(
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordtype_load_keys():
    return recordtype_value_keys() | {"@id"}

def recordtype_create_values(coll_id="testcoll", type_id="testtype", update="RecordType"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':     "%s %s/%s"%(update, coll_id, type_id)
        , 'rdfs:comment':   "%s help for %s in collection %s"%(update, type_id, coll_id)
        })

def recordtype_values(
        coll_id="testcoll", type_id="testtype", 
        update="RecordType", hosturi=TestHostUri):
    d = recordtype_create_values(coll_id, type_id, update=update).copy()
    d.update(
        { 'annal:id':       type_id
        , 'annal:type':     "annal:RecordType"
        , 'annal:uri':      hosturi + recordtype_view_uri(coll_id, type_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  recordtype_uri(coll_id, type_id)
        })
    return d

def recordtype_read_values(
        coll_id="testcoll", type_id="testtype", 
        update="RecordType", hosturi=TestHostUri):
    d = recordtype_values(coll_id, type_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        })
    return d

def recordtype_context_data(
        type_id=None, orig_id=None, action=None, 
        update="RecordType", hosturi=TestHostUri):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            "testcoll"
        , 'orig_id':            "orig_type_id"
        , 'type_label':         "%s testcoll/..."%(update)
        , 'type_help':          "%s help for ... in collection testcoll"%(update)
        , 'type_uri':           recordtype_view_uri("testcoll", "___")
        , 'continuation_uri':   collection_edit_uri("testcoll")
        })
    if type_id:
        context_dict['type_id']     = type_id
        context_dict['orig_id']     = type_id
        context_dict['type_label']  = "%s testcoll/%s"%(update, type_id)
        context_dict['type_help']   = "%s help for %s in collection testcoll"%(update,type_id)
        context_dict['type_uri']    = hosturi + recordtype_view_uri("testcoll", type_id)
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordtype_form_data(
        type_id=None, orig_id=None, action=None, cancel=None, 
        update="RecordType", hosturi=TestHostUri):
    form_data_dict = (
        { 'type_label':         "%s testcoll/..."%(update)
        , 'type_help':          "%s help for ... in collection testcoll"%(update)
        , 'type_class':         recordtype_view_uri("testcoll", "___")
        , 'orig_id':            "orig_type_id"
        , 'continuation_uri':   collection_edit_uri("testcoll")
        })
    if type_id:
        form_data_dict['type_id']       = type_id
        form_data_dict['orig_id']       = type_id
        form_data_dict['type_label']    = "%s testcoll/%s"%(update, type_id)
        form_data_dict['type_help']     = "%s help for %s in collection testcoll"%(update,type_id)
        form_data_dict['type_class']    = hosturi + recordtype_view_uri("testcoll", type_id)
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = "Save"
    return form_data_dict

def recordtype_delete_confirm_form_data(type_id=None):
    return (
        { 'typelist':    type_id,
          'type_delete': 'Delete'
        })

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordtype view
#
#   -----------------------------------------------------------------------------

def entitydata_recordtype_view_context_data(
        entity_id=None, orig_id=None, type_id="testtype", type_ids=[],
        action=None, update="Entity"
    ):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            'testcoll'
        , 'type_id':            'testtype'
        , 'orig_id':            'orig_entity_id'
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
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_name':         'Type_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_comment'
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
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
          ]
        , 'continuation_uri':   entitydata_list_type_uri("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][2]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['fields'][3]['field_value'] = TestBaseUri + "/c/%s/d/%s/%s/"%("testcoll", "testtype", entity_id)
        context_dict['orig_id']     = entity_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_recordtype_view_form_data(
        entity_id=None, orig_id=None, 
        type_id="testtype", orig_type=None,
        coll_id="testcoll", 
        action=None, cancel=None, update="Entity"):
    # log.info("entitydata_recordtype_view_form_data: entity_id %s"%(entity_id))
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, orig_type or type_id)
        })
    if entity_id:
        form_data_dict['entity_id']     = entity_id
        form_data_dict['Type_label']    = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Type_comment']  = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Type_uri']      = TestBaseUri + "/c/%s/d/%s/%s/"%(coll_id, type_id, entity_id)
        form_data_dict['orig_id']       = entity_id
        form_data_dict['orig_type']     = type_id
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if orig_type:
        form_data_dict['orig_type']     = orig_type
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

# End.
