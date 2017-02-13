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
    collection_entity_view_url,
    context_field_row
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

def recordlist_coll_url(site, coll_id="testcoll", list_id="testlist"):
    return urlparse.urljoin(
        site._entityurl,
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_LIST_PATH%{'id': list_id} + "/"
        )

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
    return recordlist_value_keys(list_uri=list_uri) | {'@id', '@type', '@context'}

def recordlist_create_values(
        coll_id="testcoll", list_id="testlist", list_uri=None, update="RecordList"):
    """
    Entity values used when creating a record list entity
    """
    d = (
        { 'annal:type':                 "annal:List"
        , 'rdfs:label':                 "%s %s/%s"%(update, coll_id, list_id)
        , 'rdfs:comment':               "%s help for %s/%s"%(update, coll_id, list_id)
        , "annal:display_type":         "_enum_list_type/List"
        , "annal:default_view":         "_view/Default_view"
        , "annal:default_type":         "_type/Default_type"
        , "annal:list_entity_selector": "ALL"
        , "annal:list_fields":
          [ { "annal:field_id":             layout.FIELD_TYPEID+"/Entity_id"
            , "annal:field_placement":      "small:0,3"
            }
          , { "annal:field_id":             layout.FIELD_TYPEID+"/Entity_label"
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
        { '@id':            layout.COLL_BASE_LIST_REF%{'id': list_id}
        , '@type':          ["annal:List"]
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
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
    if list_id:
        list_label = "%s %s/%s"%(update, coll_id, list_id)
        list_descr = "%s help for %s/%s"%(update, coll_id, list_id)
    else:
        list_label = "%s list (%s/@@list_id@@)"%(update, coll_id)
        list_descr = "%s description ... (%s/%s)"%(update, coll_id, list_id)
    list_fields = (
        [ { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_id"
          , "annal:field_placement":  "small:0,3"
          }
        , { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_label"
          , "annal:field_placement":  "small:3,9"
          }
        ])
    context_dict = (
        { "title":              "%s - List definition - Collection %s"%(list_label, coll_id)
        , 'heading':            "List definition"
        , "coll_id":            coll_id
        , "type_id":            "_list"
        , "orig_id":            "orig_list_id"
        , "continuation_url":   entitydata_list_type_url(coll_id, "_list")
        , "fields":
          [ context_field_row(
              { "field_id":           "List_id"                   # fields[0]
              , "field_name":         "entity_id"
              , "field_value_type":   "annal:EntityRef"
              , "field_label":        "List Id"
              , "field_render_type":  "EntityRef"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12;medium:0,6")
              # , "field_value":      (Supplied separately, below)
              , "options":            []
              },
              { "field_id":           "List_type"                 # fields[1]
              , "field_name":         "List_type"
              , "field_value_type":  "annal:List_type"
              , "field_label":        "List display type"
              , "field_render_type":  "Enum_choice"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12;medium:6,6")
              , "field_value":        "_enum_list_type/List"
              , "options":            [] # ["list", "grid"]
              })
          , context_field_row(
              { "field_id":           "List_label"                # fields[2]
              , "field_name":         "List_label"
              , "field_value_type":   "annal:Text"
              , "field_label":        "Label"
              , "field_render_type":  "Text"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12")
              # , "field_value":      (Supplied separately, below)
              , "options":            []
              })
          , context_field_row(
              { "field_id":           "List_comment"              # fields[3]
              , "field_name":         "List_comment"
              , "field_label":        "Help"
              , "field_value_type":   "annal:Richtext"
              , "field_render_type":  "Markdown"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12")
              # , "field_value":      (Supplied separately, below)
              , "options":            []
              })
          , context_field_row(
              { "field_id":           "List_default_type"         # fields[4]
              , "field_name":         "List_default_type"
              , "field_value_type":   "annal:Type"
              , "field_label":        "Default type"
              , "field_render_type":  "Enum_optional"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12;medium:0,6")
              , "field_value":        "_type/Default_type"
              , "options":            []
              },
              { "field_id":           "List_default_view"         # fields[5]
              , "field_name":         "List_default_view"
              , "field_value_type":   "annal:View"
              , "field_label":        "Default view"
              , "field_render_type":  "Enum_optional"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12;medium:6,6")
              , "field_value":        "_view/Default_view"
              , "options":            []
              })
          , context_field_row(
              { "field_id":           "List_entity_selector"      # fields[6]
              , "field_name":         "List_entity_selector"
              , "field_value_type":   "annal:Text"
              , "field_label":        "Selector"
              , "field_render_type":  "Text"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12")
              , "field_value":        "ALL"
              , "options":            []
              })
          , context_field_row(
              { "field_id":           "List_target_type"          # fields[7]
              , "field_name":         "List_target_type"
              , "field_value_type":   "annal:Identifier"
              , "field_label":        "List entity type"
              , "field_render_type":  "Identifier"
              , "field_value_mode":   "Value_direct"
              , "field_placement":    get_placement_classes("small:0,12")
              , "field_value":        ""
              , "options":            []
              })
          , { "field_id":           "List_fields"           # fields[8]
            , "field_name":         "List_fields"
            , "field_value_type":   "annal:Field_group"
            , "field_label":        "Fields"
            , "field_render_type":  "RepeatGroupRow"
            , "field_value_mode":   "Value_direct"
            , "field_placement":    get_placement_classes("small:0,12")
            , "field_value":        list_fields
            , "options":            []
            }
          ]
        })
    if list_id:
        context_dict['fields'][0]['row_field_descs'][0]['field_value'] = list_id
        context_dict['fields'][1]['row_field_descs'][0]['field_value'] = list_label
        context_dict['fields'][2]['row_field_descs'][0]['field_value'] = list_descr
        context_dict['orig_id']     = list_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordlist_view_form_data(
        coll_id="testcoll", 
        list_id="", orig_id=None, 
        action=None, cancel=None, task=None,
        update="RecordView"):
    form_data_dict = (
        { "List_type":              "_enum_list_type/List"
        , "List_label":             "%s list (%s/@@list_id@@)"%(update, coll_id)
        , "List_comment":           "%s help (%s/@@list_id@@)"%(update, coll_id)
        , "List_default_type":      "_type/Default_type"
        , "List_default_view":      "_view/Default_view"
        , "List_entity_selector":   "ALL"
        # List repeating fields
        , "List_fields__0__Field_id":           layout.FIELD_TYPEID+"/Entity_id"
        , "List_fields__0__Field_placement":    "small:0,3"
        , "List_fields__1__Field_id":           layout.FIELD_TYPEID+"/Entity_label"
        , "List_fields__1__Field_placement":    "small:3,9"
        # Hidden fields
        , "action":                 "@@TBD@@"
        , "view_id":                "List_view"
        , "orig_id":                "orig_list_id"
        , "orig_type":              "_list"
        , "continuation_url":       entitydata_list_type_url(coll_id, "_list")        
        })
    if list_id is not None:
        form_data_dict['entity_id']     = list_id
    if list_id:
        form_data_dict['entity_id']     = list_id
        form_data_dict['orig_id']       = list_id
        form_data_dict['List_label']    = "%s %s/%s"%(update, coll_id, list_id)
        form_data_dict['List_comment']  = "%s help for %s/%s"%(update, coll_id, list_id)
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    elif task:
        form_data_dict[task]            = task        
    else:
        form_data_dict['save']          = "Save"
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
