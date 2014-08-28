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

from annalist.util              import valid_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

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

def site_view_url():
    return reverse("AnnalistSiteView")

def collection_view_url(coll_id="testcoll"):
    return reverse("AnnalistCollectionView", kwargs={'coll_id': coll_id})

def collection_edit_url(coll_id="testcoll"):
    return reverse("AnnalistCollectionEditView", kwargs={'coll_id': coll_id})

def continuation_url_param(uri, prev_cont=None):
    if prev_cont:
        uri += "?" + prev_cont
    return "continuation_url=" + urlquote(uri, safe="/=!")

def confirm_delete_params(
        button_id="entity_delete", coll_id="testcoll", entity_id="entity1", search_for="", list_id=None, type_id="testtype"):
    vals = (
        { 'button_id':  button_id
        , 'entity_id':  entity_id
        , 'coll_id':    coll_id
        , 'list_id_':   "/l/"+list_id+"/" if list_id else "/d/"
        , 'type_id_':   type_id + '/' if type_id else ""
        , 'search_for': search_for
        })
    params = (
        """{"%(button_id)s": ["Delete"],"""+
        """ "entity_id": ["%(entity_id)s"],"""+
        """ "continuation_url": [null],"""+
        """ "completion_url": ["/testsite/c/%(coll_id)s%(list_id_)s%(type_id_)s"],"""+
        """ "search_for": ["%(search_for)s"]}"""
        )%vals
    return params

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
        [ '@type'
        , 'annal:id' # , 'annal:type_id'
        , 'annal:url', 'annal:uri'
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
        , '@type':          ["annal:Collection"]
        , 'annal:id':       coll_id
        # , 'annal:type_id':  "_coll"
        , 'annal:type':     "annal:Collection"
        , 'annal:url':      hosturi + collection_view_url(coll_id=coll_id)
        , 'annal:uri':      hosturi + collection_view_url(coll_id=coll_id)
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
