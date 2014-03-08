"""
Utility functions to support entity data testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import QueryDict
from django.core.urlresolvers       import resolve, reverse

from annalist.identifiers           import RDF, RDFS, ANNAL
# from annalist                       import layout
# from annalist.models.site           import Site
# from annalist.models.collection     import Collection
# from annalist.models.recordtype     import RecordType
# from annalist.models.recordtypedata import RecordTypeData
# from annalist.models.entitydata     import EntityData

from tests      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def site_view_uri():
    return reverse("AnnalistSiteView")

def collection_edit_uri(coll_id="testcoll"):
    return reverse("AnnalistCollectionEditView", kwargs={'coll_id': coll_id})

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
        kwargs.update({'type_id': type_id})
    return reverse(viewname, kwargs=kwargs)

def entity_uri(coll_id, type_id, entity_id):
    viewname = "AnnalistEntityDataAccessView"
    kwargs   = {'coll_id': coll_id, 'type_id': type_id, 'entity_id': entity_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_uri(coll_id, type_id):
    viewname = "AnnalistEntityDefaultListType"
    kwargs   = {'coll_id': coll_id, 'type_id': type_id}
    return reverse(viewname, kwargs=kwargs)

def entitydata_edit_uri(action, coll_id, type_id, entity_id=None):
    viewname = ( 
        'AnnalistEntityDefaultNewView'      if action == "new" else
        'AnnalistEntityDefaultEditView'
        )
    if action != "new": action = "edit"
    kwargs = {'action': action, 'coll_id': coll_id, 'type_id': type_id}
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def entitydata_delete_confirm_uri(coll_id, type_id):
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

def entitydata_value_keys():
    """
    Keys in default view entity data
    """
    return (
        [ 'annal:id', 'annal:type', 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        ])

def entitydata_create_values(entity_id, update="Entity"):
    """
    Data used when creating entity test data
    """
    return (
        { 'rdfs:label': '%s testcoll/testtype/%s'%(update, entity_id)
        , 'rdfs:comment': '%s coll testcoll, type testtype, entity %s'%(update, entity_id)
        , 'annal:uri': entity_uri("testcoll", "testtype", entity_id)
        })

def entitydata_values(entity_id, update="Entity"):
    d = entitydata_create_values(entity_id, update=update).copy()
    d.update(
        { '@id':            './'
        , 'annal:id':       entity_id
        , 'annal:type':     'annal:EntityData'
        })
    return d

def entitydata_context_data(entity_id=None, orig_entity_id=None, action=None, update="Entity"):
    context_dict = (
        { 'title':              'Annalist data journal test site'
        , 'coll_id':            'testcoll'
        , 'type_id':            'testtype'
        , 'orig_entity_id':     'orig_entity_id'
        , 'fields':
          [ { 'field_label':      'Id'
            , 'field_render':     'field/annalist_field_text.html'
            , 'field_name':       'Entity_id'
            , 'field_placement':  'small-12 medium-4 columns'
            , 'field_id':         'Entity_id'
            , 'field_value_type': 'annal:Slug'
            # , 'field_value':      ''
            }
          , { 'field_label':      'Label'
            , 'field_render':     'field/annalist_field_text.html'
            , 'field_name':       'Entity_label'
            , 'field_placement':  'small-12 columns'
            , 'field_id':         'Entity_label'
            , 'field_value_type': 'annal:Text'
            , 'field_value':      '%s data ... (testcoll/testtype)'%(update)
            }
          , { 'field_label':      'Comment'
            , 'field_render':     'field/annalist_field_textarea.html'
            , 'field_name':       'Entity_comment'
            , 'field_placement':  'small-12 columns'
            , 'field_id':         'Entity_comment'
            , 'field_value_type': 'annal:Longtext'
            , 'field_value':      '%s description ... (testcoll/testtype)'%(update)
            }
          ]
        , 'continuation_uri':   entitydata_list_uri("testcoll", "testtype")
        })
    if entity_id:
        context_dict['fields'][0]['field_value'] = entity_id
        context_dict['fields'][1]['field_value'] = '%s testcoll/testtype/%s'%(update,entity_id)
        context_dict['fields'][2]['field_value'] = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        context_dict['orig_entity_id']  = entity_id
    if orig_entity_id:
        context_dict['orig_entity_id']  = orig_entity_id
    if action:  
        context_dict['action']  = action
    return context_dict

def entitydata_form_data(entity_id=None, orig_entity_id=None, action=None, cancel=None, update="Entity"):
    form_data_dict = (
        { 'Entity_label':       '%s data ... (testcoll/testtype)'%(update)
        , 'Entity_comment':     '%s description ... (testcoll/testtype)'%(update)
        , 'orig_entity_id':     'orig_entity_id'
        , 'continuation_uri':   entitydata_list_uri("testcoll", "testtype")
        })
    if entity_id:
        form_data_dict['Entity_id']         = entity_id
        form_data_dict['Entity_label']      = '%s testcoll/testtype/%s'%(update,entity_id)
        form_data_dict['Entity_comment']    = '%s coll testcoll, type testtype, entity %s'%(update,entity_id)
        form_data_dict['orig_entity_id']    = entity_id
    if orig_entity_id:
        form_data_dict['orig_entity_id']    = orig_entity_id
    if action:
        form_data_dict['action']            = action
    if cancel:
        form_data_dict['cancel']            = "Cancel"
    else:
        form_data_dict['save']              = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Miscellaneous data
#
#   -----------------------------------------------------------------------------

def entitydata_delete_confirm_form_data(entity_id=None):
    """
    Form data from entity deletion confirmation
    """
    return (
        { 'entity_id':     entity_id,
          'entity_delete': 'Delete'
        })

def collection_create_values(coll_id="testcoll"):
    """
    Entity values used when creating a collection entity
    """
    return (
        { 'rdfs:label':     'Collection %s'%coll_id
        , 'rdfs:comment':   'Description of Collection %s'%coll_id
        })

def recordtype_value_keys():
    return (
        [ 'annal:id', 'annal:type', 'annal:uri'
        , 'rdfs:label', 'rdfs:comment'
        ])

def recordtype_create_values(type_id="testtype"):
    """
    Entity values used when creating a record type entity
    """
    return (
        { 'rdfs:label':     'recordType %s'%type_id
        , 'rdfs:comment':   'Description of RecordType %s'%type_id
        })

# End.
