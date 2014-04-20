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

def continuation_uri_param(uri, prev_cont=None):
    if prev_cont:
        uri += "?" + prev_cont
    return "continuation_uri=" + urlquote(uri, safe="/=!")

#   -----------------------------------------------------------------------------
#
#   ----- Site data
#
#   -----------------------------------------------------------------------------

def site_title(template="%s"):
    return template%("Annalist data notebook test site")

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
        , 'annal:uri'
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

# End.
