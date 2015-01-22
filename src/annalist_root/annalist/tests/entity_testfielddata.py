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

from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils               import (
    collection_dir, 
    site_title,
    collection_entity_view_url
    )
from entity_testentitydata          import (
    entitydata_list_type_url
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordfield_dir(coll_id="testcoll", field_id="testfield"):
    return collection_dir(coll_id) + layout.COLL_FIELD_PATH%{'id': field_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordfield_site_url(site, field_id="testfield"):
    return site._entityurl + layout.SITE_FIELD_PATH%{'id': field_id} + "/"

def recordfield_coll_url(site, coll_id="testcoll", field_id="testfield"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_FIELD_PATH%{'id': field_id} + "/"

def recordfield_url(coll_id, field_id):
    """
    URI for record field description data; also view using default entity view
    """
    if not valid_id(field_id):
        field_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_field", entity_id=field_id)

def recordfield_edit_url(action=None, coll_id=None, field_id=None):
    """
    URI for record field description editing view
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
    if field_id:
        if valid_id(field_id):
            kwargs.update({'entity_id': field_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordField data
#
#   -----------------------------------------------------------------------------

def recordfield_init_keys(field_uri=False):
    keys = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type', 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        ])
    if field_uri:
        keys.add('annal:uri')
    return keys

def recordfield_value_keys(field_uri=False):
    return (recordfield_init_keys(field_uri=field_uri) |
        { 'annal:property_uri'
        , 'annal:field_entity_type'
        , 'annal:field_value_type'
        , 'annal:field_placement'
        , 'annal:field_render_type'
        , 'annal:placeholder'
        , 'annal:default_value'
        })

def recordfield_load_keys(field_uri=False):
    return recordfield_value_keys(field_uri=field_uri) | {'@id', '@type'}

def recordfield_create_values(coll_id="testcoll", field_id="testfield", update="Field"):
    """
    Entity values used when creating a record field entity
    """
    return (
        { 'rdfs:label':     "%s %s/_field/%s"%(update, coll_id, field_id)
        , 'rdfs:comment':   "%s help for %s in collection %s"%(update, field_id, coll_id)
        })

def recordfield_values(
        coll_id="testcoll", field_id="testfield", field_uri=None,
        update="Field", hosturi=TestHostUri):
    d = recordfield_create_values(coll_id, field_id, update=update).copy()
    d.update(
        { 'annal:id':       field_id
        , 'annal:type_id':  "_field"
        , 'annal:type':     "annal:Field"
        , 'annal:url':      recordfield_url(coll_id, field_id)
        })
    if field_uri:
        d['annal:uri'] = field_uri
    return d

def recordfield_read_values(
        coll_id="testcoll", field_id="testfield",
        update="Field", hosturi=TestHostUri):
    d = recordfield_values(coll_id, field_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:Field"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordfield view
#
#   -----------------------------------------------------------------------------

def recordfield_entity_view_context_data(
        field_id=None, orig_id=None, type_ids=[],
        action=None, update="Field"
    ):
    context_dict = (
        { 'title':              "Collection testcoll"
        , 'coll_id':            'testcoll'
        , 'type_id':            '_field'
        , 'orig_id':            'orig_field_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_id':           'Field_id'
            , 'field_name':         'entity_id'
            , 'field_render_type':  'EntityId'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value_type':   'annal:Slug'
            , 'field_placeholder':  '(field id)'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Field value type'
            , 'field_id':           'Field_type'
            , 'field_name':         'Field_type'
            , 'field_render_type':  'Identifier'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_value_type':   'annal:Identifier'
            , 'field_placeholder':  '(field value type)'
            , 'field_value':        'annal:Text'
            , 'options':            []
            }
          , { 'field_label':        'Field render type'
            , 'field_id':           'Field_render'
            , 'field_name':         'Field_render'
            , 'field_render_type':  'Enum_choice'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value_type':   'annal:Slug'
            , 'field_placeholder':  '(field render type)'
            , 'field_value':        'Text'
            , 'options':            []
            }
          , { 'field_label':        'Position/size'
            , 'field_id':           'Field_placement'
            , 'field_name':         'Field_placement'
            , 'field_render_type':  'Placement'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_value_type':   'annal:Placement'
            , 'field_placeholder':  '(field position and size)'
            , 'field_value':        ''
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_id':           'Field_label'
            , 'field_name':         'Field_label'
            , 'field_render_type':  'Text'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Text'
            , 'field_placeholder':  '(field label)'
            , 'field_value':        '%s data ... (testcoll/_field)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Help'
            , 'field_id':           'Field_comment'
            , 'field_name':         'Field_comment'
            , 'field_render_type':  'Textarea'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Longtext'
            , 'field_placeholder':  '(field usage commentary or help text)'
            , 'field_value':        '%s description ... (testcoll/_field)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Placeholder'
            , 'field_id':           'Field_placeholder'
            , 'field_name':         'Field_placeholder'
            , 'field_render_type':  'Text'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Text'
            , 'field_placeholder':  '(placeholder text)'
            , 'field_value':        ''
            , 'options':            []
            }
          , { 'field_label':        'Property'
            , 'field_id':           'Field_property'
            , 'field_name':         'Field_property'
            , 'field_render_type':  'Identifier'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_type':   'annal:Identifier'
            , 'field_placeholder':  "(field URI or CURIE)"
            , 'field_value':        ''
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url("testcoll", "_field")
        })
    if field_id:
        context_dict['fields'][0]['field_value'] = field_id
        context_dict['fields'][4]['field_value'] = '%s testcoll/_field/%s'%(update,field_id)
        context_dict['fields'][5]['field_value'] = '%s help for %s in collection testcoll'%(update,field_id)
        context_dict['orig_id']     = field_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordfield_entity_view_form_data(
        field_id=None, orig_id=None, 
        coll_id="testcoll", 
        action=None, cancel=None, update="Field"):
    # log.info("recordfield_entity_view_form_data: field_id %s"%(field_id))
    form_data_dict = (
        { 'Field_label':        '%s data ... (%s/%s)'%(update, coll_id, "_field")
        , 'Field_comment':      '%s description ... (%s/%s)'%(update, coll_id, "_field")
        , 'orig_id':            'orig_field_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_field")
        })
    if field_id:
        field_url = recordfield_url(coll_id=coll_id, field_id=field_id)
        form_data_dict['entity_id']     = field_id
        form_data_dict['Field_label']   = '%s %s/%s/%s'%(update, coll_id, "_field", field_id)
        form_data_dict['Field_comment'] = '%s help for %s in collection %s'%(update, field_id, coll_id)
        form_data_dict['Field_uri']     = field_url
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
