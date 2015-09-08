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

from annalist.util              import valid_id, extract_entity_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout
from annalist                   import message

from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testutils import (
    collection_dir, 
    site_view_url,
    collection_edit_url,
    collection_entity_view_url,
    site_title
    )
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

# Each entity type has its own data directory within a collection:

def recorddata_dir(coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_TYPEDATA_PATH%{'id': type_id} + "/"

def entitydata_dir(coll_id="testcoll", type_id="testtype", entity_id="testentity"):
    return recorddata_dir(coll_id, type_id) + layout.TYPEDATA_ENTITY_PATH%{'id': entity_id} + "/"


#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity_id"):
    """
    URI for entity data; also view using default entity view
    """
    if not valid_id(entity_id):
        entity_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def entitydata_edit_url(action=None, coll_id="testcoll", type_id=None, entity_id=None, view_id="Default_view"):
    viewname = ( 
        'AnnalistEntityNewView'             if action == "new" else
        'AnnalistEntityEditView'
        )
    kwargs = {'action': action, 'coll_id': coll_id, 'view_id': view_id}
    if type_id:
        kwargs.update({'type_id': type_id})
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_all_url(coll_id="testcoll", list_id=None, scope=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id}
    else:
        viewname = "AnnalistEntityDefaultListAll"
        kwargs   = {'coll_id': coll_id}
    if scope is not None:
        kwargs['scope'] = scope
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_type_url(coll_id="testcoll", type_id="testtype", list_id=None, scope=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id, 'type_id': type_id}
    else:
        viewname = "AnnalistEntityDefaultListType"
        kwargs   = {'coll_id': coll_id, 'type_id': type_id}
    if scope is not None:
        kwargs['scope'] = scope
    return reverse(viewname, kwargs=kwargs)

def entitydata_delete_confirm_url(coll_id="testcoll", type_id="testtype"):
    kwargs = {'coll_id': coll_id, 'type_id': type_id}
    return reverse("AnnalistEntityDataDeleteView", kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- Entity data
#
#   -----------------------------------------------------------------------------

#   The following all return some arbitrary entity data, but corresponding to 
#   the same entity at different stages of the processing (initial values, 
#   stored values, Django view context data and Django form data).

def entitydata_type(type_id):
    """
    Returns type URI/CURIE/ref for indicated type id.
    """
    if type_id == "_type":
        return "annal:Type"
    elif type_id == "_list":
        return "annal:List"
    elif type_id == "_view":
        return "annal:View"
    elif type_id == "_field":
        return "annal:Field"
    else:
        return "annal:EntityData"

def entitydata_value_keys(entity_uri=False):
    """
    Keys in default view entity data
    """
    keys = (
        [ '@type'
        , 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        ])
    if entity_uri:
        keys.add('annal:uri')
    return keys

def entitydata_create_values(
        entity_id, update="Entity", coll_id="testcoll", type_id="testtype", 
        entity_uri=None, type_uri=None, hosturi=TestHostUri,
        extra_fields=None):
    """
    Data used when creating entity test data
    """
    if type_uri is not None:
        types = [entitydata_type(type_id), type_uri, type_uri+"/super1", type_uri+"/super2"]
    else:
        types = [entitydata_type(type_id), entity_url(coll_id, "_type", type_id)]
    # log.info('entitydata_create_values: types %r'%(types,)) 
    d = (
        { '@type':          types
        , 'annal:type':     types[0]
        , 'rdfs:label':     '%s testcoll/%s/%s'%(update, type_id, entity_id)
        , 'rdfs:comment':   '%s coll testcoll, type %s, entity %s'%(update, type_id, entity_id)
        })
    if entity_uri:
        d['annal:uri'] = entity_uri
    if extra_fields:
        d.update(extra_fields)
    return d

def entitydata_values_add_field(data, property_uri, dup_index, value):
    """
    Add field to data; if duplicate then reformat appropriately.

    Updates and returns supplied entity value dictionary.
    """
    if property_uri in data:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    data[property_uri+suffix] = value
    return data

def entitydata_values(
        entity_id, update="Entity", 
        coll_id="testcoll", type_id="testtype", 
        entity_uri=None,
        type_uri=None, hosturi=TestHostUri
        ):
    # type_uri = entity_url(coll_id, "_type", type_id)
    dataurl = entity_url(coll_id, type_id, entity_id)
    d = entitydata_create_values(
        entity_id, update=update, coll_id=coll_id, type_id=type_id, 
        entity_uri=entity_uri, type_uri=type_uri, hosturi=hosturi
        ).copy() #@@ copy needed here?
    d.update(
        { '@id':            './'
        , 'annal:id':       entity_id
        , 'annal:type_id':  type_id
        , 'annal:url':      dataurl
        })
    # log.info("entitydata_values %r"%(d,))
    return d

def entitydata_context_data(
        entity_id=None, orig_id=None, type_id="testtype", type_ids=[],
        action=None, update="Entity"
    ):
    context_dict = (
        { 'title':              "Collection testcoll"
        , 'coll_id':            'testcoll'
        , 'type_id':            'testtype'
        , 'orig_id':            'orig_entity_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_id':           'Entity_id'
            , 'field_name':         'entity_id'
            , 'field_render_type':  'EntityId'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  "annal:Slug"
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Type'
            , 'field_id':           'Entity_type'
            , 'field_name':         'entity_type'
            , 'field_render_type':  'EntityTypeId'
            , 'field_target_type':  "annal:Slug"
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_value_mode':   'Value_direct'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_id':           'Entity_label'
            , 'field_name':         'Entity_label'
            , 'field_render_type':  'Text'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  "annal:Text"
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_id':           'Entity_comment'
            , 'field_name':         'Entity_comment'
            , 'field_render_type':  'Markdown'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  "annal:Richtext"
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = "_type/"+type_id if valid_id(type_id) else None
        context_dict['fields'][2]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][3]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_id']     = entity_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_context_add_field(
    context_dict, field_id, dup_index, field_value,
        field_name='Entity_comment',
        field_label='Comment',
        field_render_type='Markdown',
        field_value_mode='Value_direct',
        field_value_type='annal:Richtext',
        field_placement='small:0,12',
        field_options=[]
        ):
    """
    Add field value to context; if duplicate then reformat appropriately.

    Field details default to Entity_comment

    Updates and returns supplied context dictionary.
    """
    field_ids = [ f['field_id'] for f in context_dict['fields'] ]
    if field_id in field_ids:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    context_dict['fields'].append(
        { 'field_id':           field_id
        , 'field_value':        field_value
        , 'field_name':         field_name+suffix
        , 'field_label':        field_label
        , 'field_render_type':  field_render_type
        , 'field_value_mode':   field_value_mode
        , 'field_target_type':  field_value_type
        , 'field_placement':    get_placement_classes(field_placement)
        , 'options':            field_options
        })
    return context_dict

def entitydata_form_data(
        entity_id=None, orig_id=None, 
        type_id="testtype", orig_type=None,
        coll_id="testcoll", 
        action=None, cancel=None, close=None, edit=None, copy=None, 
        update="Entity"
        ):
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Entity_comment':     '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, orig_type or type_id)
        })
    if entity_id:
        form_data_dict['entity_id']         = entity_id
        form_data_dict['entity_type']       = "_type/"+type_id
        form_data_dict['Entity_label']      = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Entity_comment']    = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['orig_id']           = entity_id
        form_data_dict['orig_type']         = type_id
    if orig_id:
        form_data_dict['orig_id']           = orig_id
    if orig_type:
        form_data_dict['orig_type']         = orig_type
    if action:
        form_data_dict['action']            = action
    if cancel:
        form_data_dict['cancel']            = "Cancel"
    elif close:
        form_data_dict['close']             = "Close"
    elif edit:
        form_data_dict['edit']              = "Edit"
    elif copy:
        form_data_dict['copy']              = "Copy"
    else:
        form_data_dict['save']              = 'Save'
    return form_data_dict

def entitydata_form_add_field(form_data_dict, field_name, dup_index, value):
    """
    Add field value to form data; if duplicate then reformat appropriately.

    Updates and returns supplied form data dictionary.
    """
    if field_name in form_data_dict:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    form_data_dict[field_name+suffix] = value
    return form_data_dict

def entitydata_delete_form_data(entity_id=None, type_id="Default_type", list_id="Default_list"):
    return (
        { 'list_choice':        "_list/"+list_id
        , 'continuation_url':   ""
        , 'search_for':         ""
        , 'entity_select':      ["%s/%s"%(type_id, entity_id)]
        , 'delete':             "Delete"
        })

def entitydata_delete_confirm_form_data(entity_id=None, search=None):
    """
    Form data from entity deletion confirmation
    """
    form_data = (
        { 'entity_id':     entity_id,
          'entity_delete': 'Delete'
        })
    if search:
        form_data['search'] = search
    return form_data


#   -----------------------------------------------------------------------------
#
#   ----- Entity data in Default_view
#
#   -----------------------------------------------------------------------------

def entitydata_default_view_context_data(
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
            , 'field_name':         'entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Entity_id'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Type'
            , 'field_name':         'entity_type'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6')
            , 'field_id':           'Entity_type'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Text'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_name':         'Entity_label'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Entity_label'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Text'
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_name':         'Entity_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Entity_comment'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Richtext'
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][2]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][3]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_id']     = entity_id
    if type_id:
        context_dict['fields'][1]['field_value'] = type_id       
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_default_view_form_data(
        coll_id="testcoll", 
        type_id="testtype", orig_type=None,
        entity_id=None, orig_id=None, 
        action=None, cancel=None, close=None, view=None, edit=None, copy=None, 
        update="Entity",
        add_view_field=None, use_view=None,
        new_view=None, new_field=None, new_type=None, 
        new_enum=None, do_import=None
        ):
    # log.info("entitydata_default_view_form_data: entity_id %s"%(entity_id))
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Entity_comment':     '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, orig_type or type_id)
        })
    if entity_id:
        form_data_dict['entity_id']       = entity_id
        form_data_dict['entity_type']     = "_type/"+type_id
        form_data_dict['Entity_label']    = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Entity_comment']  = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['orig_id']         = entity_id
        form_data_dict['orig_type']       = type_id
    if orig_id:
        form_data_dict['orig_id']         = orig_id
    if orig_type:
        form_data_dict['orig_type']       = orig_type
    if action:
        form_data_dict['action']          = action
    if cancel:
        form_data_dict['cancel']          = "Cancel"
    elif close:
        form_data_dict['close']           = "Close"
    elif view:
        form_data_dict['view']            = "View"
    elif edit:
        form_data_dict['edit']            = "Edit"
    elif copy:
        form_data_dict['copy']            = "Copy"
    elif add_view_field:
        form_data_dict['add_view_field']  = add_view_field
    elif use_view:
        form_data_dict['use_view']        = "Show view"
        form_data_dict['view_choice']     = use_view
    elif new_view:
        form_data_dict['new_view']        = new_view
    elif new_field:
        form_data_dict['new_field']       = new_field
    elif new_type:
        form_data_dict['new_type']        = new_type
    elif new_enum:
        form_data_dict[new_enum]          = new_enum
    elif do_import:
        form_data_dict[do_import]         = do_import
    else:
        form_data_dict['save']            = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in Type_view
#
#   -----------------------------------------------------------------------------

# Used in test_entitygenericedit - move?

def entitydata_recordtype_view_context_data(
        entity_id=None, orig_id=None, type_id="testtype", type_uri=None, type_ids=[],
        action=None, update="Entity"
    ):
    context_dict = (
        { 'title':              "Collection testcoll"
        , 'coll_id':            'testcoll'
        , 'type_id':            type_id
        , 'orig_id':            'orig_entity_id'
        , 'fields':
          [ { 'field_label':        'Id'
            , 'field_name':         'entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Type_id'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_name':         'Type_label'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_label'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Text'
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_name':         'Type_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_comment'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Richtext'
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'URI'
            , 'field_name':         'Type_uri'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Type_uri'
            , 'field_value_mode':   'Value_direct'
            , 'field_target_type':  'annal:Identifier'
            , 'field_value':        ""
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][2]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_id']                  = entity_id
    if type_uri:
        context_dict['fields'][3]['field_value'] = type_uri # TestBasePath + "/c/%s/d/%s/%s/"%("testcoll", "testtype", entity_id)
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_recordtype_view_form_data(
        coll_id="testcoll", 
        type_id="testtype", orig_type=None, type_uri=None,
        entity_id=None, orig_id=None, 
        action=None, cancel=None, update="Entity",
        add_view_field=None, open_view=None):
    # log.info("entitydata_recordtype_view_form_data: entity_id %s"%(entity_id))
    form_data_dict = (
        { 'Type_label':         '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Type_comment':       '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, orig_type or type_id)
        })
    if entity_id and type_id:
        type_url = entity_url(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
        type_url = type_url.replace("___", entity_id)  # Preserve bad type in form data
        form_data_dict['entity_id']       = entity_id
        form_data_dict['Type_label']      = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Type_comment']    = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Type_uri']        = "" # type_url
        form_data_dict['orig_id']         = entity_id
    if type_id:
        form_data_dict['entity_type']     = "_type/"+type_id
        form_data_dict['orig_type']       = extract_entity_id(type_id)
    if type_uri:
        form_data_dict['Type_uri']        = type_uri
    if orig_id:
        form_data_dict['orig_id']         = orig_id
    if orig_type:
        form_data_dict['orig_type']       = orig_type
    if action:
        form_data_dict['action']          = action
    if cancel:
        form_data_dict['cancel']          = "Cancel"
    elif add_view_field:
        form_data_dict['add_view_field']  = add_view_field
    elif open_view:
        form_data_dict['open_view']       = open_view
    else:
        form_data_dict['save']            = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Entity list
#
#   -----------------------------------------------------------------------------

def entitylist_form_data(action, search="", list_id="Default_list", entities=None, continuation_url=None):
    """
    Form data from entity list form submission

    list_form_data = (
        { 'search_for':         ""
        , 'search':             "Find"
        , 'list_choice':        "_list/Default_list"
        , 'list_view':          "View"
        , 'entity_select':      ["{{entity.entity_id}}"]
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        , 'continuation_url':   "{{continuation_url}}"
        })
    """
    form_actions = (
        { 'search':             "Find"
        , 'list_view':          "View"
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'close':              "Close"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        })
    if continuation_url is None:
        continuation_url = "" # collection_edit_url("testcoll")
    form_data = (
        { 'search_for':         search
        , 'list_choice':        "_list/"+list_id
        , 'continuation_url':   continuation_url
        })
    if entities is not None:
        form_data['entity_select'] = entities
    if action in form_actions:
        form_data[action] = form_actions[action]
    else:
        form_data[action] = action
    return form_data

#   -----------------------------------------------------------------------------
#
#   ----- Default field values
#
#   -----------------------------------------------------------------------------

def default_fields(coll_id=None, type_id=None, entity_id=None, width=12, **kwargs):
    """
    Returns a function that accepts a field width and returns a dictionary of entity values
    for testing.  The goal is to isolate default entity value settings from the test cases.
    """
    def_label       = default_label(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
    def_comment     = default_comment(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
    def_label_esc   = def_label.replace("'", "&#39;")
    def_comment_esc = def_comment.replace("'", "&#39;")
    def_entity_url  = collection_entity_view_url(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
    def def_fields(width=12):
        fields = layout_classes(width=width)
        fields.update(
            { 'coll_id':             coll_id
            , 'type_id':             type_id
            , 'entity_id':           entity_id
            , 'default_label':       def_label
            , 'default_comment':     def_comment
            , 'default_label_esc':   def_label_esc
            , 'default_comment_esc': def_comment_esc
            , 'default_entity_url':  def_entity_url
            })
        if kwargs:
            fields.update(kwargs)
        return fields
    return def_fields


def default_label(coll_id=None, type_id=None, entity_id=None):
    # Note: for built-in types, default values matches corresponding sitedata _initial_values
    if type_id in ["_type", "_view", "_list", "_field"]:
        return ""
    return message.ENTITY_DEFAULT_LABEL%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def default_comment(coll_id=None, type_id=None, entity_id=None):
    # Note: for built-in types, default values matches corresponding sitedata _initial_values
    if type_id in ["_type", "_view", "_list", "_field"]:
        return ""
    return message.ENTITY_DEFAULT_COMMENT%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def error_label(coll_id=None, type_id=None, entity_id=None):
    return message.ENTITY_MESSAGE_LABEL%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

#   -----------------------------------------------------------------------------
#
#   ----- Field layout classes
#
#   -----------------------------------------------------------------------------

def layout_classes(width=12):
    if width == 2:
        class_dict = (
            { 'space_classes':          "medium-2 columns show-for-medium-up"
            })
    elif width == 4:
        class_dict = (
            { 'label_classes':          "view-label small-12 medium-6 columns"
            , 'input_classes':          "view-value small-12 medium-6 columns"
            , 'col_head_classes':       "view-label col-head small-12 medium-4 columns"
            , 'col_item_classes':       "view-value col-???? small-12 medium-4 columns"
            , 'button_wide_classes':    "small-4 columns"
            , 'button_left_classes':    "form-buttons small-12 columns"
            , 'button_right_classes':   "form-buttons small-12 columns text-right"
            })
    elif width == 6:
        class_dict = (
            { 'label_classes':          "view-label small-12 medium-4 columns"
            , 'input_classes':          "view-value small-12 medium-8 columns"
            , 'col_head_classes':       "view-label col-head small-12 medium-6 columns"
            , 'col_item_classes':       "small-12 medium-6 columns"
            , 'button_wide_classes':    "small-6 columns"
            , 'button_left_classes':    "form-buttons small-12 columns"
            , 'button_right_classes':   "form-buttons small-12 columns text-right"
            })
    elif width == 10:
        class_dict = (
            { 'button_wide_classes':    "small-10 columns"
            })
    elif width == 12:
        class_dict = (
            { 'group_label_classes':    "group-label small-12 medium-2 columns"
            , 'group_space_classes':    "small-12 medium-2 columns hide-for-small-only"
            , 'group_row_head_classes': "small-12 medium-10 columns hide-for-small-only"
            , 'group_row_body_classes': "small-12 medium-10 columns"
            , 'group_buttons_classes':  "group-buttons small-12 medium-10 columns"
            , 'label_classes':          "view-label small-12 medium-2 columns"
            , 'input_classes':          "view-value small-12 medium-10 columns"
            , 'col_head_classes':       "view-label col-head small-12 columns"
            , 'col_item_classes':       "view-value col-???? small-12 columns"
            , 'space_classes':          "medium-2 columns show-for-medium-up"
            , 'button_wide_classes':    "small-12 medium-10 columns"
            , 'button_half_classes':    "form-buttons small-12 medium-5 columns"
            , 'button_left_classes':    "form-buttons small-12 columns"
            , 'button_right_classes':   "form-buttons small-12 columns text-right"
            })
    else:
        assert False, "Unexpected width %r"%width
    return class_dict

# End.
