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

from annalist.util              import valid_id, extract_entity_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testentitydata      import entitydata_list_type_url
from entity_testfielddesc       import get_field_description, get_bound_field
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils import (
    collection_dir, 
    collection_edit_url,
    collection_entity_view_url,
    site_title,
    context_field_row
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

def recordtype_coll_url(site, coll_id="testcoll", type_id="testtype"):
    return urlparse.urljoin(
        site._entityurl,
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_TYPE_PATH%{'id': type_id} + "/"
        )

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
        ks.add('annal:supertype_uri')
    return ks

def recordtype_load_keys(type_uri=False, supertype_uris=False):
    return (
        recordtype_value_keys(type_uri=type_uri, supertype_uris=supertype_uris) | 
        {'@id', '@type', '@context'}
        )

def recordtype_create_values(
        coll_id="testcoll", type_id="testtype", update="RecordType",
        type_uri=None, supertype_uris=None
        ):
    """
    Entity values used when creating a record type entity
    """
    d = (
        { 'annal:type':         "annal:Type"
        , 'rdfs:label':         "%s %s/%s/%s"%(update, coll_id, "_type", type_id)
        , 'rdfs:comment':       '%s coll %s, type %s, entity %s'%(update, coll_id, "_type", type_id)
        , 'annal:type_view':    "_view/Default_view"
        , 'annal:type_list':    "_list/Default_list"
        })
    if type_uri:
        d['annal:uri'] = type_uri
        if supertype_uris is not None:
            d['annal:supertype_uri'] = (
                [ { '@id': st } for st in supertype_uris ]
                )
        else:
            d['annal:supertype_uri'] = (
                [ { '@id': type_uri+"/super1" }
                , { '@id': type_uri+"/super2" }
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
        { '@id':            layout.COLL_BASE_TYPE_REF%{'id': type_id}
        , '@type':          ["annal:Type"]
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordtype view
#
#   -----------------------------------------------------------------------------

def type_view_context_data(action=None,
        coll_id="testcoll",
        type_type_id=layout.TYPE_TYPEID, orig_type=None,
        type_entity_id="", orig_id=None, type_ids=[],
        type_label=None,
        type_descr=None,
        type_uri=None,
        type_supertype_uris=[],
        type_view="_view/Default_view",
        type_list="_list/Default_list",
        type_aliases=[],
        record_type="annal:Type",
        update="RecordType",
        continuation_url=None
    ):
    if type_uri is None:
        type_uri = ""
        if type_entity_id:
            type_uri = recordtype_url(coll_id=coll_id, type_id=type_entity_id)
    if type_label is None:
        if type_entity_id:
            type_label = "%s %s/%s/%s"%(update, coll_id, type_type_id, type_entity_id)
        elif orig_id:
            type_label = "%s %s/%s/%s"%(update, coll_id, type_type_id, orig_id)
        else:
            type_label = "%s data ... (%s/%s)"%(update, coll_id, type_entity_id)
    if type_uri is None:
       type_uri = recordtype_url(coll_id=coll_id, type_id=type_entity_id)
    if continuation_url is None:
        continuation_url = entitydata_list_type_url(coll_id, type_type_id)
    view_heading = "Type definition"
    view_title   = (
        "%s - %s - Collection %s"%(type_label, view_heading, coll_id) if type_label
        else
        "%s - Collection %s"%(view_heading, coll_id)
        )
    context_dict = (
        { 'title':              view_title
        , 'heading':            view_heading
        , 'coll_id':            coll_id
        , 'type_id':            type_type_id
        , 'view_id':            "Type_view"
        , 'entity_id':          type_entity_id or ""
        , 'orig_type':          orig_type or type_type_id
        , 'record_type':        record_type
        , 'continuation_url':   continuation_url
        , 'fields':
          [ context_field_row(
              get_bound_field("Type_id",           type_entity_id),         # 0 (0,0)
              )
          , context_field_row(
              get_bound_field("Type_label",        type_label)              # 1 (1,0)
              )
          , context_field_row(
              get_bound_field("Type_comment",      type_descr)              # 2 (2,0)
              )
          , context_field_row(
              get_bound_field("Type_uri",          type_uri),               # 3 (3,0)
              )
          , get_bound_field("Type_supertype_uris", type_supertype_uris)     # 4 (4)  
          , context_field_row(
              get_bound_field("Type_view",         type_view),              # 5 (5,0)
              get_bound_field("Type_list",         type_list)               # 6 (5,1)
              )
          , get_bound_field("Type_aliases",        type_aliases)            # 7 (6)
          ]
        })
    if orig_id is not None:
        context_dict['orig_id']     = orig_id
    elif action != "new":
        context_dict['orig_id']     = type_entity_id
    if action:  
        context_dict['action']      = action
    return context_dict

def type_view_form_data(action=None, 
        coll_id="testcoll", orig_coll=None,
        type_type_id="_type", orig_type=None,
        type_entity_id="", orig_id=None, type_entity_uri=None,
        cancel=None, close=None, edit=None, copy=None, task=None,
        add_view_field=None, open_view=None, customize=None,
        update="RecordType",
        ):
    """
    Returns a request dictionary that can be used with the Django test client.
    Per Django documentation, multiple values for a key are provided as a list.
    See: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#making-requests

    Note: historically, some tests use Type_view to display non-type data, 
    hence explicit type_type_id and type_entity_id parameters.
    """
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_entity_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_entity_id)
        , 'continuation_url':   entitydata_list_type_url(coll_id, type_type_id)
        })
    if action:
        form_data_dict['action']        = action
    if type_type_id:
        form_data_dict['entity_type']   = "_type/"+type_type_id
        form_data_dict['orig_type']     = extract_entity_id(type_type_id)
    if type_entity_id is not None:
        form_data_dict['entity_id']     = type_entity_id
        form_data_dict['orig_id']       = type_entity_id
    if type_entity_id and type_type_id:
        entity_url  = recordtype_url(coll_id=coll_id, type_id=type_entity_id)
        form_data_dict['entity_id']     = type_entity_id
        form_data_dict['Type_uri']      = entity_url or ""
        form_data_dict['Type_view']     = "_view/Default_view"
        form_data_dict['Type_list']     = "_list/Default_list"
        form_data_dict['orig_coll']     = coll_id
    if orig_coll:
        form_data_dict['orig_coll']     = orig_coll
    if orig_type:
        form_data_dict['orig_type']     = orig_type
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    label_id = type_entity_id or orig_id
    if label_id and type_type_id:
        form_data_dict['Type_label']    = (
            '%s %s/%s/%s'%(update, coll_id, type_type_id, label_id)
            )
        form_data_dict['Type_comment']  = (
            '%s coll %s, type %s, entity %s'%(update, coll_id, type_type_id, label_id)
            )
    if type_entity_uri:
        form_data_dict['Type_uri']                                   = type_entity_uri
        type_uri_rstrip = type_entity_uri.rstrip()
        form_data_dict['Type_supertype_uris__0__Type_supertype_uri'] = type_uri_rstrip+"/super1"
        form_data_dict['Type_supertype_uris__1__Type_supertype_uri'] = type_uri_rstrip+"/super2"
    if cancel:
        form_data_dict['cancel']            = "Cancel"
    elif close:
        form_data_dict['close']             = "Close"
    elif edit:
        form_data_dict['edit']              = "Edit"
    elif copy:
        form_data_dict['copy']              = "Copy"
    elif add_view_field:
        form_data_dict['add_view_field']    = add_view_field
    elif open_view:
        form_data_dict['open_view']         = open_view
    elif customize:
        form_data_dict['customize']         = customize
    elif task:
        form_data_dict[task]                = task
    else:
        form_data_dict['save']      = "Save"
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
