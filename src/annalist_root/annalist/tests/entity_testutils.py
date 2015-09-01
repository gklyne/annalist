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

import annalist
from annalist.util                  import valid_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout

from annalist.models.annalistuser   import AnnalistUser

from annalist.views.fields.bound_field      import bound_field, get_entity_values
from annalist.views.fields.render_placement import get_placement_classes
from annalist.views.form_utils.fieldchoice  import FieldChoice

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
    """
    return reverse(
        "AnnalistEntityAccessView", 
        kwargs={'coll_id': coll_id, 'type_id': type_id, 'entity_id': entity_id}
        )

def collection_entity_edit_url(
        coll_id="testcoll", type_id=None, entity_id=None, 
        view_id=None, action=None
        ):
    """
    Return URL for edit view of entity

    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/!(?P<action>new)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityNewView'),
    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>copy)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    url(r'^c/(?P<coll_id>\w{0,32})/v/(?P<view_id>\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/!(?P<action>edit)$',
                            GenericEntityEditView.as_view(),
                            name='AnnalistEntityEditView'),
    """
    viewname = ( 
        'AnnalistEntityNewView'             if action == "new" else
        'AnnalistEntityEditView'
        )
    args = {'action': action, 'coll_id': coll_id, 'view_id': view_id}
    if type_id:
        args.update({'type_id': type_id})
    if entity_id:
        args.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=args)

def collection_entity_list_url(coll_id="testcoll", list_id=None, type_id=None, scope=None):
    """
    Return URL for entity list in collection some collection.

    url(r'^c/(?P<coll_id>\w{0,32})/l/$',
                            EntityDefaultListView.as_view(),
                            name='AnnalistEntityDefaultList'),
    url(r'^c/(?P<coll_id>\w{0,32})/l/(?P<list_id>\w{0,32})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),
    url(r'^c/(?P<coll_id>\w{0,32})/l/(?P<list_id>\w{0,32})/(?P<type_id>\w{0,32})/$',
                            EntityGenericListView.as_view(),
                            name='AnnalistEntityGenericList'),

    """
    view = "AnnalistEntityDefaultList"
    args = {'coll_id': coll_id}
    if list_id is not None:
        view = "AnnalistEntityGenericList"
        args['list_id'] = list_id
    if type_id is not None:
        args['type_id'] = type_id
    if scope is not None:
        args['scope'] = scope
    return reverse(view, kwargs=args)

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
        , 'annal:id' 
        # , 'annal:type_id'
        , 'annal:url'
        , 'annal:uri'
        , 'rdfs:label'
        , 'rdfs:comment'
        ])

def collection_create_values(coll_id="testcoll", update="Collection"):
    """
    Entity values used when creating a collection entity
    """
    return (
        { 'rdfs:label':             "%s %s"%(update, coll_id)
        , 'rdfs:comment':           "Description of %s %s"%(update, coll_id)
        , 'annal:software_version': annalist.__version_data__
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

def render_select_options(name, label, opts, sel, placeholder=None):
    """
    Cf. `templates.field.annalist_edit_select.html`

    >>> print render_select_options("foo", "foo_label", ["aa", "bb", "cc"], "bb")
    <div class="row">
      <div class="small-10 columns view-value less-new-button">
        <select name="foo">
          <option>aa</option>
          <option selected="selected">bb</option>
          <option>cc</option>
        </select>
      </div>
      <div class="small-2 columns view-value new-button left small-text-right">
        <button type="submit" 
                name="foo__new_edit" 
                value="New"
                title="Define new foo_label">
          <span class="select-edit-button-text">+&#x270D;</span>
        </button>
      </div>
    </div>
    >>> print render_select_options("foo", "foo_label", ["", aa", "bb", "cc"], "", placeholder=("select)")
    <div class="row">
      <div class="small-10 columns view-value less-new-button">
          <select name="foo">
            <option value="" selected="selected">(select)</option>
            <option>aa</option>
            <option>bb</option>
            <option>cc</option>
          </select>
      </div>
      <div class="small-2 columns view-value new-button left small-text-right">
        <button type="submit" 
                name="foo__new_edit" 
                value="New"
                title="Define new foo_label">
          <span class="select-edit-button-text">+&#x270D;</span>
        </button>
      </div>
    </div>
    """
    # Local helper to render single option
    def select_option(opt):
        if isinstance(opt, (str, unicode)):
            opt = FieldChoice(opt)
        selected = ('' if opt.value != sel else ' selected="selected"')
        label    = (placeholder or "") if opt.value == "" else opt.label
        label    = opt.label or opt.value or placeholder or ""
        return '<option value="%s"%s>%s</option>'%(opt.value, selected, label)
    #
    select_template = (
        """<div class="row">\n"""+
        """  <div class="small-10 columns view-value less-new-button">\n"""+
        """    <select name="%(name)s">\n"""+
        """      %(options)s\n"""+
        """    </select>"""+
        """  </div>\n"""+
        """  <div class="small-2 columns view-value new-button left small-text-right">\n"""+
        """    <button type="submit" \n"""+
        """            name="%(name)s__new_edit" \n"""+
        """            value="New"\n"""+
        """            title="Define new %(label)s">\n"""+
        """      <span class="select-edit-button-text">+&#x270D;</span>\n"""+
        """    </button>\n"""+
        """  </div>\n"""+
        """</div>\n"""+
        "")
    return select_template%(
        { 'name':       name
        , 'label':      label
        , 'options':    "\n  ".join([ select_option(o) for o in opts ])
        })

def render_choice_options(name, opts, sel, placeholder=None, select_class=None, _unused_value_dict={}):
    """
    Cf. `templates.field.annalist_edit_choice.html`.
    Like select, but without the "New" button.

    >>> print render_choice_options("foo", "foo_label", ["aa", "bb", "cc"], "bb")
    <select name="foo">
      <option value="aa">aa</option>
      <option value="bb" selected="selected">bb</option>
      <option value="cc">cc</option>
    </select>
    >>> print render_choice_options("foo", "foo_label", ["", aa", "bb", "cc"], "", placeholder=("select)")
    <select name="foo">
      <option value="" selected="selected">(select)</option>
      <option value="aa">aa</option>
      <option value="bb">bb</option>
      <option value="cc">cc</option>
    </select>
    """
    # Local helper to render single option
    def select_option(opt):
        if isinstance(opt, (str, unicode)):
            opt = FieldChoice(opt)
        selected = ('' if opt.value != sel else ' selected="selected"')
        label    = (placeholder or "") if opt.value == "" else opt.label
        label    = opt.label or opt.value or placeholder or ""
        return '<option value="%s"%s>%s</option>'%(opt.value, selected, label)
    def _unused_select_option(o):
        selected = ('' if o != sel else ' selected="selected"')
        if (placeholder is not None) and (o == ""):
            return '<option value=""%s>%s</option>'%(selected,placeholder)
        v = value_dict.get(o, None)
        # value = ('' if v is None else ' value="%s"'%v)
        value = ' value="%s"'%(v or o)
        return '<option%s%s>%s</option>'%(selected,value,o)
    #
    select_template = (
        """<select %(select_class)s name="%(name)s">\n"""+
        """  %(options)s\n"""+
        """</select>"""+
        "")
    return select_template%(
        { 'name':           name
        , 'options':        "\n  ".join([ select_option(o) for o in opts ])
        , 'select_class':   '''class="%s"'''%select_class if select_class is not None else ""
        })

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

#   -----------------------------------------------------------------------------
#
#   ----- Context access utilities
#
#   -----------------------------------------------------------------------------

def context_list_entities(context):
    """
    Returns list of entities to be displayed in list view
    """
    # log.info(context['List_rows'])
    if 'List_rows' in context:
        return context['List_rows']['field_value']
    elif 'entities' in context:
        return context['entities']
    log.warning("No entity list found in context %r"%(context.keys()))
    return None

def context_list_head_fields(context):
    """
    Returns unbound field description used for accessing header information.
    """
    return context['fields']

def context_list_item_fields(context, entity):
    """
    Returns indicated field to be displayed as a bound_field value
    """
    # log.info(context['List_rows'])
    if 'List_rows' in context:
        fds = context['List_rows']['group_field_descs']
        return [ bound_field(fd, entity) for fd in fds ]
    elif 'fields' in entity:
        return entity['fields']
    log.warning("No field value found: context %r, entity %r"%(context.keys(), entity.keys()))
    return None

def context_list_item_field(context, entity, fid):
    """
    Returns indicated field to be displayed as a bound_field value
    """
    # log.info(context['List_rows'])
    if 'List_rows' in context:
        fd = context['List_rows']['group_field_descs'][fid]
        return bound_field(fd, entity)
    elif 'fields' in entity:
        return entity['fields'][fid]
    log.warning("No field value found: context %r, entity %r"%(context.keys(), entity.keys()))
    return None

def context_list_item_field_value(context, entity, fid):
    """
    Returns value of indicated field
    """
    return context_list_item_field(context, entity, fid)['field_value']

#   -----------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
