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

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def site_dir():
    return TestBaseDir + "/"

def collection_dir(coll_id="testcoll"):
    return site_dir() + layout.SITE_COLL_PATH%{'id': coll_id} + "/"

def recordtype_dir(coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_TYPE_PATH%{'id': type_id} + "/"

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

def site_view_uri():
    return reverse("AnnalistSiteView")

def collection_view_uri(coll_id="testcoll"):
    return reverse("AnnalistCollectionView", kwargs={'coll_id': coll_id})

def collection_edit_uri(coll_id="testcoll"):
    return reverse("AnnalistCollectionEditView", kwargs={'coll_id': coll_id})

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

def recordview_uri(coll_id, view_id):
    viewname = "AnnalistRecordViewAccessView"
    kwargs   = {'coll_id': coll_id}
    if valid_id(view_id):
        kwargs.update({'view_id': view_id})
    else:
        kwargs.update({'view_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordview_view_uri(coll_id, view_id):
    viewname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': "_view"}
    if valid_id(view_id):
        kwargs.update({'entity_id': view_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordlist_uri(coll_id, list_id):
    viewname = "AnnalistRecordListAccessView"
    kwargs   = {'coll_id': coll_id}
    if valid_id(list_id):
        kwargs.update({'list_id': list_id})
    else:
        kwargs.update({'list_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def recordlist_view_uri(coll_id, list_id):
    viewname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': "_list"}
    if valid_id(list_id):
        kwargs.update({'entity_id': list_id})
    else:
        kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_all_uri(coll_id="testcoll", list_id=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id}
    else:
        viewname = "AnnalistEntityDefaultListAll"
        kwargs   = {'coll_id': coll_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_type_uri(coll_id="testcoll", type_id="testtype", list_id=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id, 'type_id': type_id}
    else:
        viewname = "AnnalistEntityDefaultListType"
        kwargs   = {'coll_id': coll_id, 'type_id': type_id}
    return reverse(viewname, kwargs=kwargs)

# def entitydata_list_id_uri(coll_id="testcoll", type_id="testtype", list_id="Default_list"):
#     viewname = "AnnalistEntityDefaultListType"
#     kwargs   = {'coll_id': coll_id, 'type_id': type_id, 'list_id': list_id}
#     return reverse(viewname, kwargs=kwargs)

def entity_uri(coll_id="testcoll", type_id="testtype", entity_id="entity_id"):
    viewname = "AnnalistEntityDefaultDataView"
    kwargs   = {'coll_id': coll_id, 'type_id': type_id, 'entity_id': entity_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_edit_uri(action, coll_id, type_id=None, entity_id=None, view_id=None):
    if view_id:
        viewname = ( 
            'AnnalistEntityNewView'             if action == "new" else
            'AnnalistEntityEditView'
            )
        kwargs = {'action': action, 'coll_id': coll_id, 'view_id': view_id}
    else:
        viewname = ( 
            'AnnalistEntityDefaultNewView'      if action == "new" else
            'AnnalistEntityDefaultEditView'
            )
        kwargs = {'action': action, 'coll_id': coll_id}
    if type_id:
        kwargs.update({'type_id': type_id})
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def entitydata_delete_confirm_uri(coll_id, type_id):
    kwargs = {'coll_id': coll_id, 'type_id': type_id}
    return reverse("AnnalistEntityDataDeleteView", kwargs=kwargs)

def continuation_uri_param(uri, prev_cont=None):
    if prev_cont:
        uri += "?" + prev_cont
    return "continuation_uri=" + urlquote(uri, safe="/=!")

#   -----------------------------------------------------------------------------
#
#   ----- Entity data
#
#   -----------------------------------------------------------------------------

#   The following all return some arbitrary entity data, but corresponding to 
#   the same entity at different stages of the processing (initial values, 
#   stored values, Django view context data and Django form data).

def entitydata_value_keys():
    """
    Keys in default view entity data
    """
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def entitydata_create_values(entity_id, type_id="testtype", update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s testcoll/%s/%s'%(update, type_id, entity_id)
        , 'rdfs:comment': '%s coll testcoll, type %s, entity %s'%(update, type_id, entity_id)
        })

def entitydata_values(entity_id, update="Entity", coll_id="testcoll", type_id="testtype", hosturi=TestHostUri):
    d = entitydata_create_values(entity_id, type_id=type_id, update=update).copy()
    d.update(
        { '@id':            './'
        , 'annal:id':       entity_id
        , 'annal:type':     'annal:EntityData'
        , 'annal:uri':      hosturi + entity_uri(coll_id, type_id, entity_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  entity_uri(coll_id, type_id, entity_id)
        })
    return d

def entitydata_context_data(
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
            , 'field_name':         'Entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Entity_id'
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Type'
            , 'field_render_view':  'field/annalist_view_select.html'
            , 'field_render_edit':  'field/annalist_edit_select.html'
            , 'field_name':         'Entity_type'
            , 'field_placement':    get_placement_classes('small:0,12;medium:6,6right')
            , 'field_id':           'Entity_type'
            , 'field_value_type':   'annal:Slug'
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_label':        'Label'
            , 'field_render_view':  'field/annalist_view_text.html'
            , 'field_render_edit':  'field/annalist_edit_text.html'
            , 'field_name':         'Entity_label'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Entity_label'
            , 'field_value_type':   'annal:Text'
            , 'field_value':        '%s data ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          , { 'field_label':        'Comment'
            , 'field_render_view':  'field/annalist_view_textarea.html'
            , 'field_render_edit':  'field/annalist_edit_textarea.html'
            , 'field_name':         'Entity_comment'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_id':           'Entity_comment'
            , 'field_value_type':   'annal:Longtext'
            , 'field_value':        '%s description ... (testcoll/testtype)'%(update)
            , 'options':            []
            }
          ]
        , 'continuation_uri':   entitydata_list_type_uri("testcoll", type_id)
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = type_id if valid_id(type_id) else None
        context_dict['fields'][2]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][3]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_id']     = entity_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_form_data(
        entity_id=None, orig_id=None, 
        type_id="testtype", orig_type=None,
        coll_id="testcoll", 
        action=None, cancel=None, update="Entity"):
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Entity_comment':     '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_uri':   entitydata_list_type_uri(coll_id, orig_type or type_id)
        })
    if entity_id:
        form_data_dict['Entity_id']         = entity_id
        form_data_dict['Entity_type']       = type_id
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
    else:
        form_data_dict['save']              = 'Save'
    return form_data_dict

def entitydata_delete_confirm_form_data(entity_id=None):
    """
    Form data from entity deletion confirmation
    """
    return (
        { 'entity_id':     entity_id,
          'entity_delete': 'Delete'
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
            , 'field_name':         'Entity_id'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_id':           'Entity_id'
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
        form_data_dict['Entity_id']     = entity_id
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

#   -----------------------------------------------------------------------------
#
#   ----- Entity list
#
#   -----------------------------------------------------------------------------

def entitylist_form_data(action, search="", list_id="Default_list", entities=None):
    """
    Form data from entity list form submission

    list_form_data = (
        { 'search_for':         ""
        , 'search':             "Find"
        , 'list_id':            "Default_list"
        , 'list_view':          "View"
        , 'entity_select':      ["{{entity.entity_id}}"]
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        , 'continuation_uri':   "{{continuation_uri}}"
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
    form_data = (
        { 'search_for':         search
        , 'list_id':            list_id
        , 'continuation_uri':   collection_edit_uri("testcoll")
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
#   ----- Collection data
#
#   -----------------------------------------------------------------------------

def collection_value_keys():
    """
    Keys in collection data
    """
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def collection_create_values(coll_id="testcoll", update="Collection"):
    """
    Entity values used when creating a collection entity
    """
    return (
        { 'rdfs:label':     "%s %s"%(update, coll_id)
        , 'rdfs:comment':   'Description of %s %s'%(update, coll_id)
        })

def collection_values(coll_id, update="Collection", hosturi=TestHostUri):
    d = collection_create_values(coll_id, update=update).copy()
    d.update(
        { '@id':            "../"
        , 'annal:id':       coll_id
        , 'annal:type':     "annal:Collection"
        , 'annal:uri':      hosturi + collection_view_uri(coll_id=coll_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  collection_view_uri(coll_id=coll_id)
        })
    return d

def collection_new_form_data(coll_id, update="Collection"):
        return (
            { "new":        "New collection"
            , "new_id":     coll_id
            , "new_label":  "%s %s"%(update, coll_id)
            })

def collection_remove_form_data(coll_id_list):
        return (
            { "remove":     "Remove selected"
            , "new_id":     ""
            , "new_label":  ""
            , "select":     coll_id_list
            })


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
#   ----- RecordView data
#
#   -----------------------------------------------------------------------------

def recordview_value_keys():
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordview_create_values(coll_id="testcoll", view_id="testview", update="RecordView"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':     "%s %s/%s"%(update, coll_id, view_id)
        , 'rdfs:comment':   "%s help for %s in collection %s"%(update, view_id, coll_id)
        })

def recordview_values(
        coll_id="testcoll", view_id="testtype", 
        update="RecordView", hosturi=TestHostUri):
    d = recordview_create_values(coll_id, view_id, update=update).copy()
    d.update(
        { '@id':            "./"
        , 'annal:id':       view_id
        , 'annal:type':     "annal:RecordView"
        , 'annal:uri':      hosturi + recordview_view_uri(coll_id, view_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  recordview_uri(coll_id, view_id)
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- RecordList data
#
#   -----------------------------------------------------------------------------

def recordlist_value_keys():
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri', 'annal:urihost', 'annal:uripath'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordlist_create_values(coll_id="testcoll", list_id="testlist", update="RecordList"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':     "%s %s/%s"%(update, coll_id, list_id)
        , 'rdfs:comment':   "%s help for %s in collection %s"%(update, list_id, coll_id)
        })

def recordlist_values(
        coll_id="testcoll", list_id="testlist", 
        update="RecordList", hosturi=TestHostUri):
    d = recordlist_create_values(coll_id, list_id, update=update).copy()
    d.update(
        { '@id':            "./"
        , 'annal:id':       list_id
        , 'annal:type':     "annal:RecordList"
        , 'annal:uri':      hosturi + recordlist_view_uri(coll_id, list_id)
        , 'annal:urihost':  urlparse.urlparse(hosturi).netloc
        , 'annal:uripath':  recordlist_uri(coll_id, list_id)
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Miscellaneous data
#
#   -----------------------------------------------------------------------------

def site_title(template="%s"):
    return template%("Annalist data notebook test site")

# End.
