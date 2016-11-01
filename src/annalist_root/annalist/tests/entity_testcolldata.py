"""
Support for Annalist collection view testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest
import urlparse

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.db                          import models
from django.http                        import QueryDict
from django.core.urlresolvers           import resolve, reverse

import annalist
from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import layout
from annalist.util                      import valid_id

from tests                              import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir

from entity_testutils                   import (
    site_dir, collection_dir,
    collection_entity_view_url
    )
from entity_testentitydata          import (
    entitydata_list_type_url, entitydata_list_all_url,
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def collectiondata_dir(coll_id="testcoll"):
    # e.g. <base_dir>/c/testcoll
    return collection_dir(coll_id)

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

def collectiondata_url(coll_id="testcoll"):
    """
    URI for collection description data; also view using default entity view

    e.g. 
      http://example.com/site/c/_annalist_site/d/_coll/testcoll/
    """
    if not valid_id(coll_id):
        coll_id = "___"
    return collection_entity_view_url(coll_id=layout.SITEDATA_ID, type_id="_coll", entity_id=coll_id)

def collectiondata_resource_url(coll_id="testcoll", resource_ref=layout.COLL_META_FILE):
    """
    Return URL for collection data resource

    e.g. 
      http://example.com/site/c/_annalist_site/d/_coll/testcoll/
    """
    return urlparse.urljoin(
        collectiondata_url(coll_id=coll_id),
        "%s/%s"%(layout.COLL_BASE_DIR, resource_ref)
        )

def collectiondata_view_url(coll_id="testcoll", action=None):
    """
    Return URL for edit view of collection metadata

    e.g. 
      http://example.com/site/c/_annalist_site/v/Collection_view/_coll/testcoll/!view
      http://example.com/site/c/_annalist_site/v/Collection_view/_coll/testcoll/!edit
    """
    viewname = ( 
        'AnnalistEntityNewView'             if action == "new" else
        'AnnalistEntityEditView'
        )
    args = (
        { 'action':     action
        , 'coll_id':    "_annalist_site"
        , 'view_id':    "Collection_view"
        , 'type_id':    "_coll"
        , 'entity_id':  coll_id
        })
    return reverse(viewname, kwargs=args)

def collectiondata_view_resource_url(coll_id="testcoll", resource_ref=layout.COLL_META_FILE):
    """
    Return URL for collectiondata resource

    e.g. 
      http://example.com/site/c/_annalist_site/v/Collection_view/_coll/testcoll/!view
      http://example.com/site/c/_annalist_site/v/Collection_view/_coll/testcoll/!edit
    """
    return urlparse.urljoin(
        collectiondata_view_url(coll_id=coll_id, action="view"),
        "%s/%s"%(layout.COLL_BASE_DIR,resource_ref)
        )

#   -----------------------------------------------------------------------------
#
#   ----- Collection data
#
#   -----------------------------------------------------------------------------

def collectiondata_value_keys():
    keys = set(
        [ 'annal:id', 'annal:type_id', 'annal:type'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:software_version'
        , 'annal:meta_comment'
        ])    
    return keys

def collectiondata_load_keys():
    return collectiondata_value_keys() | {'@id', '@type', '@context'}

def collectiondata_create_values(
        coll_id="testcoll",
        coll_label=None,
        coll_descr=None,
        ):
    """
    Values used when creating a collection data record
    """
    if coll_label is None:
        coll_label="Collection %s"%coll_id
    if coll_descr is None:
        coll_descr="Collection %s description/help"%coll_id
    d = (
        { 'annal:type':             "annal:Collection"
        , 'rdfs:label':             coll_label
        , 'rdfs:comment':           coll_descr
        , 'annal:software_version': annalist.__version_data__
        , 'annal:meta_comment':     "Created by Annalist test suite"
        })
    return d

def collectiondata_values(coll_id="testcoll", coll_label=None, coll_descr=None):
    """
    Values filled in automatically when a user record is created
    """
    d = collectiondata_create_values(coll_id=coll_id, coll_label=coll_label, coll_descr=coll_descr)
    d.update(
        { 'annal:id':       coll_id
        , 'annal:type_id':  "_coll"
        })
    return d

def collectiondata_read_values(coll_id="testcoll", coll_label=None, coll_descr=None):
    d = collectiondata_values(coll_id=coll_id, coll_label=coll_label, coll_descr=coll_descr)
    d.update(
        { '@id':            layout.META_COLL_REF
        , '@type':          ["annal:Collection"]
        , '@context':       [{"@base": layout.META_COLL_BASE_REF}, layout.COLL_CONTEXT_FILE]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Collection data view form data
#
#   -----------------------------------------------------------------------------

def collectiondata_view_form_data(
        coll_id="testcoll",
        coll_label=None,
        coll_descr=None,
        action=None, cancel=None, close=None, edit=None, copy=None, 
        orig_id=None
        ):
    d = collectiondata_create_values(coll_id=coll_id, coll_label=coll_label, coll_descr=coll_descr)
    form_data_dict = (
        { 'entity_id':              coll_id
        , 'orig_id':                coll_id
        , 'Entity_label':           d['rdfs:label']
        , 'Entity_comment':         d['rdfs:comment']
        , 'Coll_software_version':  annalist.__version_data__
        , 'Coll_comment':           "Created by Annalist test suite"
        , 'orig_type':              "_coll"
        , 'continuation_url':       ""
        })
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    elif close:
        form_data_dict['close']         = "Close"
    elif edit:
        form_data_dict['edit']          = "Edit"
    elif copy:
        form_data_dict['copy']          = "Copy"
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

# End.
