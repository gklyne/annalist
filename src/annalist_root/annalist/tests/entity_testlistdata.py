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

from annalist.views.form_utils.fieldchoice  import FieldChoice
from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testentitydata      import entitydata_list_type_url
from entity_testfielddesc       import get_field_description, get_bound_field
from entity_testtypedata        import recordtype_url
from entity_testsitedata        import (
    make_field_choices, no_selection,
    get_site_types, get_site_types_sorted, get_site_types_linked,
    get_site_lists, get_site_lists_sorted, get_site_lists_linked,
    get_site_views, get_site_views_sorted, get_site_views_linked,
    get_site_list_types, get_site_list_types_sorted, get_site_list_types_linked,
    get_site_field_groups, get_site_field_groups_sorted, 
    get_site_fields, get_site_fields_sorted, 
    get_site_field_types, get_site_field_types_sorted, 
    )
from entity_testutils           import (
    collection_dir, 
    site_title, 
    collection_entity_view_url,
    context_field_row
    )
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
        # , "annal:list_entity_type":     None
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

def list_view_context_data(
        coll_id="testcoll", list_id=None, orig_id=None,
        action=None,
        list_uri=None,
        list_type="List",
        list_label=None,
        list_descr=None,
        list_default_type="_type/Default_type", type_choices=None,
        list_default_view="_type/Default_view", view_choices=None,
        list_entity_selector="ALL",
        list_entity_type="",
        list_fields=None,
        num_fields=0,
        update="RecordList",
        continuation_url=None
    ):
    if list_label is None:
        if list_id:
            #@@TODO: use same format as no list_id; change form data too
            list_label = "%s %s/%s"%(update, coll_id, list_id)
        else:
            list_label = "%s list (%s/)"%(update, coll_id)
    if list_fields is None:
        if num_fields == 2:
            list_fields = (
                [ { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_id"
                  , "annal:field_placement":  "small:0,3"
                  }
                , { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_label"
                  , "annal:field_placement":  "small:3,9"
                  }
                ])
        if num_fields == 3:
            list_fields = (
                [ { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_id"
                  , "annal:field_placement":  "small:0,3"
                  }
                , { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_type" 
                  , "annal:field_placement":  "small:3,3"
                  }
                , { "annal:field_id":         layout.FIELD_TYPEID+"/Entity_label"
                  , "annal:field_placement":  "small:6,6"
                  }
                ])
    list_type_choices = get_site_list_types_linked("testcoll")
    if type_choices is None:
        type_choices = (
            [ FieldChoice("", label="(default entity type)")] +
            get_site_types_linked("testcoll") +
            [ FieldChoice("_type/testtype", 
                label="RecordType testcoll/_type/testtype",
                link=recordtype_url("testcoll", "testtype")
                )]
            )
    if view_choices is None:
        view_choices = (
            [ FieldChoice("", label="(view id)") ] +
            get_site_views_linked("testcoll")
            )
    if continuation_url is None:
        continuation_url = entitydata_list_type_url(coll_id, layout.LIST_TYPEID)
    view_label = "List definition"
    view_title = (
        "%s - %s - Collection %s"%(list_label, view_label, coll_id) if list_label
        else
        "%s - Collection %s"%(view_label, coll_id)
        )
    # Target record fields listed in the view description
    context_dict = (
        { 'title':              view_title
        , 'heading':            view_label
        , 'coll_id':            coll_id
        , 'type_id':            layout.LIST_TYPEID
        , 'view_id':            'List_view'
        , 'entity_id':          list_id or ""
        , 'orig_id':            orig_id
        , 'orig_type':          layout.LIST_TYPEID
        , 'record_type':        "annal:List"
        , 'continuation_url':   continuation_url
        , 'fields':
          [ context_field_row(
              get_bound_field("List_id",              list_id),             # 0 (0,0)
              get_bound_field("List_type",            list_type,            # 1 (0,1)
                              options=list_type_choices),
              )
          , context_field_row(
              get_bound_field("List_label",           list_label)           # 2 (1,0)
              )
          , context_field_row(
              get_bound_field("List_comment",         list_descr)           # 3 (2,0)
              )
          , context_field_row(
              get_bound_field("List_default_type",    list_default_type,    # 4 (3,0)
                              options=type_choices),
              get_bound_field("List_default_view",    list_default_view,    # 5 (3,1)
                              options=view_choices),
              )
          , context_field_row(
              get_bound_field("List_entity_selector", list_entity_selector) # 6 (4,0)
              )
          , context_field_row(
              get_bound_field("List_entity_type",     list_entity_type)     # 7 (5,0)
              )
          , get_bound_field("List_fields",            list_fields)          # 8 (6, 0)
          ]
        })
    if action:  
        context_dict['action']      = action
    if list_uri:
        context_dict['entity_uri']  = list_uri
    return context_dict

def list_view_form_data(
        coll_id="testcoll", orig_coll=None,
        list_id="", orig_id=None, 
        action=None, cancel=None, task=None,
        update="RecordView"):
    form_data_dict = (
        { "List_type":              "_enum_list_type/List"
        , "List_label":             "%s list (%s/%s)"%(update, coll_id, list_id)
        , "List_comment":           "%s help (%s/%s)"%(update, coll_id, list_id)
        , "List_default_type":      "_type/Default_type"
        , "List_default_view":      "_view/Default_view"
        , "List_entity_selector":   "ALL"
        # List repeating fields
        , "List_fields__0__Field_id":           layout.FIELD_TYPEID+"/Entity_id"
        , "List_fields__0__Field_placement":    "small:0,3"
        , "List_fields__1__Field_id":           layout.FIELD_TYPEID+"/Entity_label"
        , "List_fields__1__Field_placement":    "small:3,9"
        # Hidden fields
        , "action":                 action
        , "view_id":                "List_view"
        , "orig_id":                "orig_list_id"
        , "orig_type":              "_list"
        , "orig_coll":              coll_id
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
    if orig_coll:
        form_data_dict['orig_coll']     = orig_coll
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
