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

from django.conf                    import settings
from django.http                    import QueryDict
from django.utils.http              import urlquote, urlunquote
from django.core.urlresolvers       import resolve, reverse

from annalist.util                  import valid_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.fields.render_utils   import get_placement_classes

from tests  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from entity_testutils               import (
    collection_dir, 
    # collection_edit_uri,
    site_title
    )
from entity_testentitydata          import (
    # entity_uri, entitydata_edit_uri, 
    entitydata_list_type_uri
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordview_dir(coll_id="testcoll", view_id="testview"):
    return collection_dir(coll_id) + layout.COLL_VIEW_PATH%{'id': view_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordview_site_uri(site, view_id="testview"):
    return site._entityuri + layout.SITE_VIEW_PATH%{'id': view_id} + "/"

def recordview_coll_uri(site, coll_id="testcoll", view_id="testview"):
    return site._entityuri + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_VIEW_PATH%{'id': view_id} + "/"

def recordview_uri(coll_id, view_id):
    """
    URI for record view description data; also view using default entity view
    """
    viewname = "AnnalistEntityAccessView"
    kwargs   = {'coll_id': coll_id, "type_id": "_view"}
    if valid_id(view_id):
        kwargs.update({'entity_id': view_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordview_edit_uri(action=None, coll_id=None, view_id=None):
    """
    URI for record view description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordViewDeleteView'  if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_view", 'view_id': "RecordView_view"})
    if view_id:
        if valid_id(view_id):
            kwargs.update({'entity_id': view_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordView data
#
#   -----------------------------------------------------------------------------


# { "@id":                "annal:views/Default_view"
# , "annal:id":           "default_view"
# , "annal:type":         "annal:display/RecordView"
# , "annal:record_type":  "annal:DefaultType"
# , "rdfs:label":         "View description for default record view"
# , "rdfs:comment":       "This resource describes the default form used for viewing and editing records."
# , "annal:view_fields":
#   [ { "annal:field_id":         "Entity_id"
#     , "annal:field_placement":  "small:0,12;medium:0,6"
#     }
#   , { "annal:field_id":         "Entity_type"
#     , "annal:field_placement":  "small:0,12;medium:6,6right"
#     }
#   , { "annal:field_id":         "Entity_label"
#     , "annal:field_placement":  "small:0,12"
#     }
#   , { "annal:field_id":         "Entity_comment"
#     , "annal:field_placement":  "small:0,12"
#     }
#   ]
# }

def recordview_value_keys():
    return set(
        [ 'annal:id', 'annal:type', 'annal:uri'
        , 'annal:record_type'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:view_fields'
        ])

def recordview_load_keys():
    return recordview_value_keys() | {"@id"}

def recordview_create_values(coll_id="testcoll", view_id="testview", update="RecordView"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':         "%s %s/%s"%(update, coll_id, view_id)
        , 'rdfs:comment':       "%s help for %s in collection %s"%(update, view_id, coll_id)
        , 'annal:record_type':  "annal:DefaultType"
        , 'annal:view_fields':
          [ { 'annal:field_id':         "Entity_id"
            , 'annal:field_placement':  "small:0,12;medium:0,6"
            }
          , { 'annal:field_id':         "Entity_type"
            , 'annal:field_placement':  "small:0,12;medium:6,6right"
            }
          , { 'annal:field_id':         "Entity_label"
            , 'annal:field_placement':  "small:0,12"
            }
          , { 'annal:field_id':         "Entity_comment"
            , 'annal:field_placement':  "small:0,12"
            }
          ]
        })

def recordview_values(
        coll_id="testcoll", view_id="testtype", 
        update="RecordView", hosturi=TestHostUri):
    d = recordview_create_values(coll_id, view_id, update=update).copy()
    d.update(
        { 'annal:id':       view_id
        , 'annal:type':     "annal:RecordView"
        , 'annal:uri':      hosturi + recordview_uri(coll_id, view_id)
        })
    return d

def recordview_read_values(
        coll_id="testcoll", view_id="testview", 
        update="RecordView", hosturi=TestHostUri):
    d = recordview_values(coll_id, view_id, update=update, hosturi=hosturi).copy()
    d.update(
        { '@id':            "./"
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordtype view
#
#   -----------------------------------------------------------------------------

def recordview_entity_view_context_data(
        coll_id="testcoll", view_id=None, orig_id=None, view_ids=[],
        action=None, update="RecordView"
    ):
    context_dict = (
        { 'title':              site_title()
        , 'coll_id':            coll_id
        , 'type_id':            '_view'
        , 'orig_id':            'orig_view_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_render_view':  'field/annalist_view_entityref.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'View_id'
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'View_label'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'View_label'
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (%s/%s)'%(update, coll_id, view_id)
            , 'options':            []
            }
          , { 'field_label':        'Help'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_name':         'View_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'View_comment'
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (%s/%s)'%(update, coll_id, view_id)
            , 'options':            []
            }
          # More...
          ]
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, "_view")
        })
    if view_id:
        context_dict['fields'][0]['field_value'] = view_id
        context_dict['fields'][1]['field_value'] = '%s %s/%s'%(update, coll_id, view_id)
        context_dict['fields'][2]['field_value'] = '%s help for %s in collection %s'%(update, view_id, coll_id)
        context_dict['orig_id']     = view_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordview_entity_view_form_data(
        coll_id="testcoll", 
        view_id=None, orig_id=None, 
        action=None, cancel=None, update="RecordView"):
    form_data_dict = (
        { 'View_label':         '%s data ... (%s/%s)'%(update, coll_id, view_id)
        , 'View_comment':       '%s description ... (%s/%s)'%(update, coll_id, view_id)
        , 'orig_id':            'orig_view_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, "_view")
        })
    if view_id:
        form_data_dict['entity_id']     = view_id
        form_data_dict['orig_id']       = view_id
        form_data_dict['View_label']    = '%s %s/%s'%(update, coll_id, view_id)
        form_data_dict['View_comment']  = '%s help for %s in collection %s'%(update, view_id, coll_id)
        form_data_dict['View_uri']      = TestBaseUri + "/c/%s/d/_view/%s/"%(coll_id, view_id)
        form_data_dict['orig_type']     = "_view"
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

def recordview_delete_confirm_form_data(view_id=None):
    return (
        { 'viewlist':    view_id,
          'view_delete': 'Delete'
        })

# End.
