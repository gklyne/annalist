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

def recordview_site_uri(site, view_id="testview"):
    return site._entityuri + layout.SITE_FIELD_PATH%{'id': view_id} + "/"

def recordview_coll_uri(site, coll_id="testcoll", view_id="testview"):
    return site._entityuri + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_FIELD_PATH%{'id': view_id} + "/"

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
        'AnnalistRecordFieldDeleteView' if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id, 'type_id': "_view", 'view_id': "RecordView_view"}
    if action != "delete":
        kwargs.update({'action': action})
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

def recordview_value_keys():
    return (
        [ 'annal:id', 'annal:type'
        , 'annal:uri'
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
        , 'annal:uri':      hosturi + recordview_uri(coll_id, view_id)
        })
    return d

# End.
