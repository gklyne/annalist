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
from django.contrib.auth.models     import User

from annalist.util                  import valid_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout

from annalist.models.annalistuser   import AnnalistUser

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

def collection_entity_view_url(coll_id="testcoll", type_id=None, entity_id=None):
    """
    Return URL for entity belonging to some collection.

    This matches the 'annal:url' value that is stored in saved entity data.

    @TODO: update this testing function when final form of entity URIs is
           determined, per https://github.com/gklyne/annalist/issues/32 
    """
    return reverse(
        "AnnalistEntityAccessView", 
        kwargs={'coll_id': coll_id, 'type_id': type_id, 'entity_id': entity_id}
        )

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
        , 'annal:type':     "annal:Collection"
        , 'annal:url':      collection_view_url(coll_id=coll_id)
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
#   ----- Rendering support
#
#   -----------------------------------------------------------------------------

def render_select_options(name, opts, sel, placeholder=None):
    """
    >>> print render_select_options("foo", ["aa", "bb", "cc"], "bb")
    <select name="foo">
      <option>aa</option>
      <option selected="selected">bb</option>
      <option>cc</option>
    </select>
    >>> print render_select_options("foo", ["", aa", "bb", "cc"], "", placeholder=("select)")
      <select name="foo">
        <option value="" selected="selected">(select)</option>
        <option>aa</option>
        <option>bb</option>
        <option>cc</option>
      </select>
    """
    def select_option(o):
        selected = ('' if o != sel else ' selected="selected"')
        if (placeholder is not None) and (o == ""):
            return '<option value=""%s>%s</option>'%(selected,placeholder)
        return '<option%s>%s</option>'%(selected,o)
    #
    select_template = (
        """<select name="%s">\n"""+
        """  %s\n"""+
        """</select>"""
        )
    return select_template%(name, "\n  ".join([ select_option(o) for o in opts ]))

#   -----------------------------------------------------------------------------
#
#   ----- Authorization support
#
#   -----------------------------------------------------------------------------

def create_user_permissions(parent, 
        user_id,
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"],
        use_altpath=False
        ):
    user_values = (
        { 'annal:type':             "annal:User"
        , 'rdfs:label':             "Test User"
        , 'rdfs:comment':           "User %s: permissions for %s in collection %s"%(user_id, "Test User", parent.get_id())
        , 'annal:user_uri':         "mailto:%s@%s"%(user_id, TestHost)
        , 'annal:user_permissions': user_permissions
        })
    user = AnnalistUser.create(parent, user_id, user_values, use_altpath=use_altpath)
    return user

def create_test_user(
        coll, user_id, user_pass="testpassword", 
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
        ):
    django_user = User.objects.create_user(user_id, "%s@%s"%(user_id, TestHost), user_pass)
    django_user.first_name = "Test"
    django_user.last_name  = "User"
    django_user.save()
    if coll:
        user_perms = coll.create_user_permissions(
            "testuser", "mailto:%s@%s"%(user_id, TestHost),
            "Test User",
            "User %s: permissions for %s in collection %s"%(user_id, "Test User", coll.get_id()),
            user_permissions)
    else:
        user_perms = None
    return (django_user, user_perms)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
