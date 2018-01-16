"""
Namespace vocabulary functions to support testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse

import logging
log = logging.getLogger(__name__)

# from django.conf                import settings
# from django.utils.http          import urlquote, urlunquote
from django.core.urlresolvers   import resolve, reverse

from annalist.util              import valid_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

from entity_testentitydata      import entitydata_list_type_url
from entity_testutils           import (
    collection_dir, 
    collection_entity_view_url
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordvocab_dir(coll_id="testcoll", vocab_id="testvocab"):
    return collection_dir(coll_id) + layout.COLL_VOCAB_PATH%{'id': vocab_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

def recordvocab_coll_url(site, coll_id="testcoll", vocab_id="testvocab"):
    return (
        site._entityurl + 
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_VOCAB_PATH%{'id': vocab_id} + "/"
        )

def recordvocab_url(coll_id, vocab_id):
    """
    URI for namespace vocabulary description data; also view using default entity view
    """
    if not valid_id(vocab_id):
        return None
        # vocab_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_vocab", entity_id=vocab_id)

def recordvocab_edit_url(action=None, coll_id=None, vocab_id=None):
    """
    URI for vocabulary description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordVocabDeleteView' if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id, 'type_id': "_vocab", 'view_id': "Vocab_view"}
    if action != "delete":
        kwargs.update({'action': action})
    if vocab_id:
        if valid_id(vocab_id):
            kwargs.update({'entity_id': vocab_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordVocab data
#
#   -----------------------------------------------------------------------------

def recordvocab_init_keys():
    keys = set(
        [ 'annal:id'
        , 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label'
        , 'rdfs:comment'
        , 'annal:uri'
        , 'rdfs:seeAlso'
        ])
    return keys

def recordvocab_value_keys():
    return (recordvocab_init_keys())

def recordvocab_load_keys():
    return recordvocab_value_keys() | {'@id', '@type', '@context'}

def recordvocab_create_values(
        coll_id="testcoll", vocab_id="testvocab", 
        vocab_uri="test:testvocab",
        update="RecordVocab"):
    """
    Entity values used when creating a namespace vocabulary entity
    """
    d = (
        { 'rdfs:label':                 "%s %s/_vocab/%s"%(update, coll_id, vocab_id)
        , 'rdfs:comment':               "%s help for %s in collection %s"%(update, vocab_id, coll_id)
        , 'rdfs:seeAlso':               []
        })
    if vocab_uri:
        d['annal:uri'] = vocab_uri
    return d

def recordvocab_values(
        coll_id="testcoll", vocab_id="testvocab", 
        vocab_uri="test:testvocab",
        update="RecordVocab"):
    d = recordvocab_create_values(
        coll_id, vocab_id, 
        vocab_uri=vocab_uri,
        update=update
        ).copy()
    d.update(
        { 'annal:id':                   vocab_id
        , 'annal:type_id':              "_vocab"
        , 'annal:type':                 "annal:Vocabulary"
        , 'annal:url':                  recordvocab_url(coll_id, vocab_id)
        })
    return d

def recordvocab_read_values(
        coll_id="testcoll", vocab_id="testvocab",
        vocab_uri="test:testvocab",
        update="RecordVocab"):
    d = recordvocab_values(coll_id, vocab_id, vocab_uri=vocab_uri, update=update)
    d.update(
        { '@id':            "_vocab/%s"%(vocab_id)
        , '@type':          ["annal:Vocabulary"]
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
        })
    return d


#   -----------------------------------------------------------------------------
#
#   ----- Entity data in vocabulary namespace view
#
#   -----------------------------------------------------------------------------

def recordvocab_entity_view_context_data(
        coll_id="testcoll", vocab_id="", orig_id=None, action=None, 
        vocab_uri=None,
        update="RecordVocab"
    ):
    if vocab_id:
        vocab_label = "%s %s/%s"%(update, coll_id, vocab_id)
        vocab_descr = "%s help for %s in collection %s"%(update, vocab_id, coll_id)
    else:
        vocab_label = "%s data ... (%s/%s)"%(update, coll_id, vocab_id)
        vocab_descr = "%s description ... (%s/%s)"%(update, coll_id, vocab_id)
    context_dict = (
        { 'title':              "%s - Vocabulary definition - Collection %s"%(vocab_label, coll_id)
        , 'heading':            "Vocabulary definition"
        , 'coll_id':            coll_id
        , 'type_id':            '_vocab'
        , 'orig_id':            'orig_vocab_id'
        , 'fields':
          [ context_field_row(
              { 'field_id':           'Vocab_id'
              , 'field_name':         'entity_id'
              , 'field_value_type':   'annal:EntityRef'
              , 'field_label':        'Prefix'
              , 'field_render_type':  'EntityId'
              , 'field_value_mode':   'Value_direct'
              , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
              # , 'field_value':      (Supplied separately)
              , 'options':            []
              })
          , context_field_row(
              { 'field_id':           'Entity_label'
              , 'field_name':         'Entity_label'
              , 'field_value_type':   'annal:Text'
              , 'field_label':        'Label'
              , 'field_render_type':  'Text'
              , 'field_value_mode':   'Value_direct'
              , 'field_placement':    get_placement_classes('small:0,12')
              , 'field_value':        vocab_label
              , 'options':            []
              })
          , context_field_row(
              { 'field_id':           'Entity_comment'
              , 'field_name':         'Entity_comment'
              , 'field_label':        'Comment'
              , 'field_value_type':   'annal:Richtext'
              , 'field_render_type':  'Markdown'
              , 'field_value_mode':   'Value_direct'
              , 'field_placement':    get_placement_classes('small:0,12')
              , 'field_value':        vocab_descr
              , 'options':            []
              })
          , context_field_row(
              { 'field_id':           'Entity_uri'
              , 'field_name':         'Entity_uri'
              , 'field_value_type':   'annal:Identifier'
              , 'field_label':        'URI'
              , 'field_render_type':  'Identifier'
              , 'field_value_mode':   'Value_direct'
              , 'field_placement':    get_placement_classes('small:0,12')
              # , 'field_value':      (Supplied separately)
              , 'options':            []
              })
          , { 'field_id':             'See_also'
            , 'field_name':           'See_also'
            , 'field_value_type':     'annal:seealso'
            , 'field_label':          'See also'
            , 'field_render_type':    'RepeatGroupRow'
            , 'field_value_mode':     'Value_direct'
            , 'field_placement':      get_placement_classes('small:0,12')
            , 'field_value':          []
            , 'options':              []
            }
          ]
        , 'continuation_url':   entitydata_list_vocab_url(coll_id, "_vocab")
        })
    if vocab_id:
        vocab_url = recordvocab_url(coll_id=coll_id, vocab_id=vocab_id)
        context_dict['fields'][0]['row_field_descs'][0]['field_value'] = vocab_id
        context_dict['fields'][3]['row_field_descs'][0]['field_value'] = vocab_url or ""
        context_dict['orig_id']     = vocab_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordvocab_entity_view_form_data(
        coll_id="testcoll", orig_coll=None,
        vocab_id="", orig_id=None, 
        action=None, cancel=None, close=None, edit=None, copy=None, task=None,
        update="RecordVocab",
        vocab_uri=None
        ):
    """
    Returns a request dictionary that can be used with the Django test client.
    Per Django documentation, multiple values for a key are provided as a list.
    See: https://docs.djangoproject.com/en/1.8/topics/testing/tools/#making-requests
    """
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/_vocab/%s)'%(update, coll_id, vocab_id)
        , 'Entity_comment':     '%s description ... (%s/_vocab/%s)'%(update, coll_id, vocab_id)
        , 'orig_id':            'orig_vocab_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_vocab")
        })
    if vocab_id is not None:
        form_data_dict['entity_id']           = vocab_id
    if vocab_id:
        vocab_url  = recordvocab_url(coll_id=coll_id, vocab_id=vocab_id)
        vocab_help = '%s help for %s in collection %s'%(update, vocab_id, coll_id)
        form_data_dict['entity_id']           = vocab_id
        form_data_dict['Entity_label']        = '%s %s/_vocab/%s'%(update, coll_id, vocab_id)
        form_data_dict['Entity_comment']      = vocab_help
        form_data_dict['Vocab_uri']           = vocab_url or ""
        form_data_dict['orig_id']             = vocab_id
        form_data_dict['orig_type']           = "_vocab"
        form_data_dict['orig_coll']           = coll_id
    if vocab_uri:
        form_data_dict['Vocab_uri']  = vocab_uri
    if orig_id:
        form_data_dict['orig_id']    = orig_id
    if orig_coll:
        form_data_dict['orig_coll']  = orig_coll
    if action:
        form_data_dict['action']     = action
    if cancel:
        form_data_dict['cancel']     = "Cancel"
    elif close:
        form_data_dict['close']      = "Close"
    elif edit:
        form_data_dict['edit']       = "Edit"
    elif copy:
        form_data_dict['copy']       = "Copy"
    elif task:
        form_data_dict[task]         = task
    else:
        form_data_dict['save']       = "Save"
    return form_data_dict

# End.
