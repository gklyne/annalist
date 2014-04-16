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

def recordview_dir(coll_id="testcoll", view_id="testview"):
    return collection_dir(coll_id) + layout.COLL_VIEW_PATH%{'id': view_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

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

# End.
