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
    # site_dir, collection_dir, recordtype_dir, recorddata_dir,  entitydata_dir,
    # collection_edit_uri,
    # recordtype_edit_uri,
    # entity_uri, entitydata_edit_uri, 
    entitydata_list_type_uri,
    # recordtype_form_data,
    # entitydata_value_keys, entitydata_create_values, entitydata_values,
    # entitydata_recordtype_view_context_data, 
    # # entitydata_context_data, 
    # entitydata_recordtype_view_form_data,
    # # entitydata_form_data, 
    # entitydata_delete_confirm_form_data,
    site_title
    )

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordfield_uri(coll_id, field_id):
    fieldname = "AnnalistRecordFieldAccessView"
    kwargs   = {'coll_id': coll_id}
    if valid_id(field_id):
        kwargs.update({'field_id': field_id})
    else:
        kwargs.update({'field_id': "___"})
    return reverse(fieldname, kwargs=kwargs)

def recordfield_view_uri(coll_id, field_id):
    fieldname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': "_field"}
    if valid_id(field_id):
        kwargs.update({'entity_id': field_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(fieldname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordField data
#
#   -----------------------------------------------------------------------------

def recordfield_value_keys():
    return set(
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordfield_load_keys():
    return recordfield_value_keys() | {"@id"}

def recordfield_create_values(coll_id="testcoll", field_id="testfield", update="RecordField"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':     "%s %s/_field/%s"%(update, coll_id, field_id)
        , 'rdfs:comment':   "%s help for %s in collection %s"%(update, field_id, coll_id)
        })

def recordfield_values(
        coll_id="testcoll", field_id="testfield",
        update="Field", hosturi=TestHostUri):
    d = recordfield_create_values(coll_id, field_id, update=update).copy()
    d.update(
        { 'annal:id':       field_id
        , 'annal:type':     "annal:RecordField"
        , 'annal:uri':      hosturi + recordfield_view_uri(coll_id, field_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  recordfield_uri(coll_id, field_id)
        })
    return d

def recordfield_read_values(
        coll_id="testcoll", type_id="testtype", 
        update="RecordField", hosturi=TestHostUri):
    d = recordfield_values(coll_id, type_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        })
    return d

def recordfield_context_data(
        type_id=None, orig_id=None, action=None, 
        update="RecordField", hosturi=TestHostUri):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            "testcoll"
        , 'orig_id':            "orig_type_id"
        , 'type_label':         "%s testcoll/..."%(update)
        , 'type_help':          "%s help for ... in collection testcoll"%(update)
        , 'type_uri':           recordfield_view_uri("testcoll", "___")
        , 'continuation_uri':   collection_edit_uri("testcoll")
        })
    if type_id:
        context_dict['type_id']     = type_id
        context_dict['orig_id']     = type_id
        context_dict['type_label']  = "%s testcoll/%s"%(update, type_id)
        context_dict['type_help']   = "%s help for %s in collection testcoll"%(update,type_id)
        context_dict['type_uri']    = hosturi + recordfield_view_uri("testcoll", type_id)
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordfield_form_data(
        type_id=None, orig_id=None, action=None, cancel=None, 
        update="RecordField", hosturi=TestHostUri):
    form_data_dict = (
        { 'type_label':         "%s testcoll/..."%(update)
        , 'type_help':          "%s help for ... in collection testcoll"%(update)
        , 'type_class':         recordfield_view_uri("testcoll", "___")
        , 'orig_id':            "orig_type_id"
        , 'continuation_uri':   collection_edit_uri("testcoll")
        })
    if type_id:
        form_data_dict['type_id']       = type_id
        form_data_dict['orig_id']       = type_id
        form_data_dict['type_label']    = "%s testcoll/%s"%(update, type_id)
        form_data_dict['type_help']     = "%s help for %s in collection testcoll"%(update,type_id)
        form_data_dict['type_class']    = hosturi + recordfield_view_uri("testcoll", type_id)
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = "Save"
    return form_data_dict

def recordfield_delete_confirm_form_data(type_id=None):
    return (
        { 'typelist':    type_id,
          'type_delete': 'Delete'
        })

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordfield view
#
#   -----------------------------------------------------------------------------

def entitydata_recordfield_view_context_data(
        field_id=None, orig_id=None, type_ids=[],
        action=None, update="Field"
    ):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            'testcoll'
        , 'type_id':            '_field'
        , 'orig_id':            'orig_field_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_id':           'Field_id'
            , 'field_name':         'entity_id'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Field value type'
            , 'field_id':           'Field_type'
            , 'field_name':         'Field_type'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6right')
            , 'field_value_type':   'annal:RenderType'
            , 'field_value':        '(field value type)'
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_id':           'Field_label'
            , 'field_name':         'Field_label'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (testcoll/_field)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Help'
            , 'field_id':           'Field_comment'
            , 'field_name':         'Field_comment'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (testcoll/_field)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Placeholder'
            , 'field_id':           'Field_placeholder'
            , 'field_name':         'Field_placeholder'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '(placeholder text)'
            , 'options':            []
            }
          , { 'field_label':        'Property'
            , 'field_id':           'Field_property'
            , 'field_name':         'Field_property'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Identifier'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Size and position'
            , 'field_id':           'Field_placement'
            , 'field_name':         'Field_placement'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Placement'
            , 'field_value':        '(field display size and placement details)'
            , 'options':            []
            }
          ]
        , 'continuation_uri':   entitydata_list_type_uri("testcoll", "_field")
        })
    if field_id:
        context_dict['fields'][0]['field_value'] = field_id
        context_dict['fields'][2]['field_value'] = '%s testcoll/_field/%s'%(update,field_id)
        context_dict['fields'][3]['field_value'] = '%s coll testcoll, type _field, entity %s'%(update,field_id)
        context_dict['fields'][5]['field_value'] = TestBaseUri + "/c/%s/d/%s/%s/"%("testcoll", "_field", field_id)
        context_dict['orig_id']     = field_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_recordfield_view_form_data(
        field_id=None, orig_id=None, 
        coll_id="testcoll", 
        action=None, cancel=None, update="Field"):
    # log.info("entitydata_recordfield_view_form_data: field_id %s"%(field_id))
    form_data_dict = (
        { 'Field_label':        '%s data ... (%s/%s)'%(update, coll_id, "_field")
        , 'Field_comment':      '%s description ... (%s/%s)'%(update, coll_id, "_field")
        , 'orig_id':            'orig_field_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, "_field")
        })
    if field_id:
        form_data_dict['entity_id']     = field_id
        form_data_dict['Field_label']   = '%s %s/%s/%s'%(update, coll_id, "_field", field_id)
        form_data_dict['Field_comment'] = '%s help for %s in collection %s'%(update, field_id, coll_id)
        form_data_dict['Field_uri']     = TestBaseUri + "/c/%s/d/%s/%s/"%(coll_id, "_field", field_id)
        form_data_dict['orig_id']       = field_id
        form_data_dict['orig_type']     = "_field"
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

# End.
