"""
Utility functions to support entity data testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse
import copy

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import QueryDict
from django.utils.http              import urlquote, urlunquote
from django.utils.html              import escape
from django.core.urlresolvers       import resolve, reverse
from django.template                import Context
from django.contrib.auth.models     import User

import annalist
from annalist.util                  import valid_id, extract_entity_id
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout

from annalist.models.annalistuser   import AnnalistUser

from annalist.views.uri_builder                 import uri_params, uri_with_params
from annalist.views.fields.bound_field          import bound_field, get_entity_values
from annalist.views.fields.render_placement     import get_placement_classes
from annalist.views.form_utils.fieldchoice      import FieldChoice, update_choice_labels
from annalist.views.form_utils.fielddescription import FieldDescription

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
    return (
        os.path.normpath(site_dir() + layout.SITE_COLL_PATH%{'id': coll_id})
        + "/"
        )

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def entitydata_list_url_query(viewname, kwargs, query_params, more_params):
    """
    Helper function for generatinglist URLs
    """
    list_url=reverse(viewname, kwargs=kwargs)
    return uri_with_params(list_url, query_params, more_params)

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
    return entitydata_list_url_query(view, args, None,
        { 'scope': scope
        })

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
          <option value="aa">aa</option>
          <option value="bb" selected="selected">bb</option>
          <option value="cc">cc</option>
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
    <BLANKLINE>
    >>> print render_select_options("foo", "foo_label", ["", "aa", "bb", "cc"], "", placeholder="(select)")
    <div class="row">
      <div class="small-10 columns view-value less-new-button">
        <select name="foo">
          <option value="" selected="selected">(select)</option>
          <option value="aa">aa</option>
          <option value="bb">bb</option>
          <option value="cc">cc</option>
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
    <BLANKLINE>
    """
    # Local helper to cleanup options and acount for duplicate labels
    def update_options(opts):
        return update_choice_labels(
            [ FieldChoice(o) if isinstance(o, (str, unicode)) else o 
              for o in opts
            ])

    # Local helper to render single option
    def select_option(opt):
        # if isinstance(opt, (str, unicode)):
        #     opt = FieldChoice(opt)
        # selected = ('' if opt.value != sel else ' selected="selected"')
        # label    = (placeholder or "") if opt.value == "" else opt.label
        # label    = opt.label or opt.value or placeholder or ""
        # return '<option value="%s"%s>%s</option>'%(opt.value, selected, label)
        selected = ('' if opt.value != sel else ' selected="selected"')
        label    = (placeholder or "") if opt.value == "" else opt.choice_html()
        # label    = opt.label or opt.value or placeholder or ""
        return '<option value="%s"%s>%s</option>'%(opt.value, selected, label)
    #
    select_template = (
        """<div class="row">\n"""+
        """  <div class="small-10 columns view-value less-new-button">\n"""+
        """    <select name="%(name)s">\n"""+
        """      %(options)s\n"""+
        """    </select>\n"""+
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
        , 'options':    "\n      ".join(
            [ select_option(o) for o in update_options(opts) ])
        })

def render_choice_options(
        name, opts, sel, placeholder=None, select_class=None, escape_label=False):
    """
    Cf. `templates.field.annalist_edit_choice.html`.
    Like select, but without the "New" button.

    >>> print render_choice_options("foo", ["aa", "bb", "cc"], "bb")
    <select name="foo">
      <option value="aa">aa</option>
      <option value="bb" selected="selected">bb</option>
      <option value="cc">cc</option>
    </select>
    >>> print render_choice_options("foo", ["", "aa", "bb", "cc"], "", placeholder="(select)")
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
        label    = (placeholder or "") if opt.value == "" else opt.choice()
        if escape_label:
            label = escape(label)
        # label    = opt.label or opt.value or placeholder or ""
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
        """<select name="%(name)s"%(select_class)s>\n"""+
        """  %(options)s\n"""+
        """</select>"""+
        "")
    return select_template%(
        { 'name':           name
        , 'options':        "\n  ".join([ select_option(o) for o in opts ])
        , 'select_class':   ''' class="%s"'''%select_class if select_class is not None else ""
        })

#   -----------------------------------------------------------------------------
#
#   ----- Authorization support
#
#   -----------------------------------------------------------------------------

def create_user_permissions(parent, 
        user_id,
        user_permissions=["VIEW", "CREATE", "UPDATE", "DELETE", "CONFIG"]
        ):
    user_values = (
        { 'annal:type':             "annal:User"
        , 'rdfs:label':             "Test User"
        , 'rdfs:comment':           "User %s: permissions for %s in collection %s"%(user_id, "Test User", parent.get_id())
        , 'annal:user_uri':         "mailto:%s@%s"%(user_id, TestHost)
        , 'annal:user_permission':  user_permissions
        })
    user = AnnalistUser.create(parent, user_id, user_values)
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
            user_id, "mailto:%s@%s"%(user_id, TestHost),
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

def context_field_row(*fields):
    row = (
        { 'field_id':           "Row_fields"
        , 'field_name':         "Row_fields"
        , 'field_label':        "Fields in row"
        , 'field_value_mode':   "Value_direct"
        , 'field_render_type':  "FieldRow"
        , 'field_placement':    get_placement_classes('small:0,12')
        , 'row_field_descs':    list(fields)
        })
    return row

def context_field_map(context):
    fields = context['fields']
    response = ["context_field_map: %d rows"%(len(fields))]
    for rn in range(len(fields)):
        row = fields[rn]
        if 'row_field_descs' in row:
            # Pick column from row
            cols = row['row_field_descs']
        else:
            # Field is not row-wrapped
            cols = [row]
        response.append("  row %d: %d cols"%(rn, len(cols)))
        for cn in range(len(cols)):
            field = cols[cn]
            response.append("    col %d, id %s, pos %s"%(cn, field['field_id'], field['field_placement']))
    return "\n".join(response)

def context_view_field(context, rownum, colnum):
    row = context['fields'][rownum]
    if 'row_field_descs' in row:
        # Pick column from row
        field = row['row_field_descs'][colnum]
    else:
        # Field is not row-wrapped
        field = row
    if isinstance(field, FieldDescription):
        # fields in row are late-bound, so create a binding now
        entity_vals = context['fields'][rownum]['entity_value']
        extras      = context['fields'][rownum]['context_extra_values']
        field       = bound_field(field, entity_vals, context_extra_values=extras) 
    return field

def context_bind_fields(context):
    """
    Fields in field rows are late bound so entity values do not appear in
    the actual context used.  This method binds entity values to fields
    so that all field values can be tested.
    """
    # bound_context = Context(context.flatten()) # Doesn't work for ContextList used for tests
    context_vals  = {}
    for k in context.keys():
        context_vals[k] = context[k]
    bound_context = Context(context_vals)
    bound_rows    = []
    for row in context['fields']:
        if 'row_field_descs' in row:
            entity_vals = row['entity_value']
            extras      = row['context_extra_values']
            bound_cols  = []
            for field in row['row_field_descs']:
                if isinstance(field, FieldDescription):
                    # fields in row are late-bound, so create a binding now
                    field       = bound_field(field, entity_vals, context_extra_values=extras) 
                bound_cols.append(field)
            bound_row = row.copy()
            bound_row._field_description['row_field_descs'] = bound_cols
        else:
            bound_row = row
        bound_rows.append(bound_row)
    bound_context['fields'] = bound_rows
    return bound_context

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

def check_context_field_value(test, context_field,
        field_value_type=None,
        field_value=None
        ):
    """
    Check field value in context field against supplied parameters.

    This function allows certain variations for robustness of tests.
    """
    context_field_value = context_field['field_value']
    if field_value is None:
        context_field_value = None
    elif field_value_type in ["annal:EntityRef", "annal:Type", "annal:View", "annal:List"]:
        context_field_value = extract_entity_id(context_field_value)
    if isinstance(field_value, (list, tuple)):
        for i in range(len(field_value)):
            log.debug("check_context_field_value (list): [%d] %r"%(i, field_value[i]))
            test.assertDictionaryMatch(context_field_value[i], field_value[i], prefix="[%d]"%i)
    elif isinstance(field_value, dict):
        test.assertDictionaryMatch(context_field_value, field_value[i], prefix="")
    else:
        test.assertEqual(context_field_value, field_value)
    return

def check_context_field(test, context_field,
        field_id=None,
        field_name=None,
        field_label=None,
        field_placeholder=None,
        field_property_uri=None,
        field_render_type=None,
        field_value_mode=None,
        field_value_type=None,
        field_placement=None,
        field_value=None,
        options=None,
        ):
    """
    Check values in context field against supplied parameters.

    This function allows certain variations for robustness of tests.
    """
    test.assertEqual(context_field['field_id'],   field_id)
    test.assertEqual(context_field['field_name'], field_name)
    if field_label:
        test.assertEqual(context_field['field_label'], field_label)
    if field_placeholder:
        test.assertEqual(context_field['field_placeholder'], field_placeholder)
    if field_property_uri:
        test.assertEqual(context_field['field_property_uri'], field_property_uri)
    test.assertEqual(extract_entity_id(context_field['field_render_type']), field_render_type)
    test.assertEqual(extract_entity_id(context_field['field_value_mode']),  field_value_mode)
    test.assertEqual(context_field['field_value_type'],                     field_value_type)
    if options:
        test.assertEqual(set(context_field['options']), set(options))
    if field_placement:
        test.assertEqual(context_field['field_placement'].field, field_placement)
    check_context_field_value(test, context_field, 
        field_value_type=field_value_type, 
        field_value=field_value
        )
    return

def check_context_list_field_value(test, context_field,
        field_value=None
        ):
    """
    Check field value according to type in context
    """
    check_context_field_value(test, context_field,
        field_value_type=context_field['field_value_type'],
        field_value=field_value
        )
    return

def check_field_list_context_fields(test, response, field_entities):
    """
    Check field list values in supplied context
    """
    head_fields = context_list_head_fields(response.context)
    test.assertEqual(len(head_fields), 1)       # One row of 4 cols..
    test.assertEqual(len(head_fields[0]['row_field_descs']), 4)
    f0 = context_view_field(response.context, 0, 0)
    f1 = context_view_field(response.context, 0, 1)
    f2 = context_view_field(response.context, 0, 2)
    f3 = context_view_field(response.context, 0, 3)
    # 1st field
    check_context_field(test, f0,
        field_id=           "Entity_id",
        field_name=         "entity_id",
        field_label=        "Id",
        field_placeholder=  "(entity id)",
        field_property_uri= "annal:id",
        field_render_type=  "EntityId",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:EntityRef",
        field_placement=    "small-4 medium-3 columns"
        )
    # 2nd field
    check_context_field(test, f1,
        field_id=           "Field_render_type",
        field_name=         "Field_render_type",
        field_label=        "Render type",
        field_placeholder=  "(field render type)",
        field_property_uri= "annal:field_render_type",
        field_render_type=  "Enum_choice",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:EntityRef",
        field_placement=    "small-4 medium-3 columns"
        )
    # 3rd field
    check_context_field(test, f2,
        field_id=           "Field_value_type",
        field_name=         "Field_value_type",
        field_label=        "Value type",
        field_placeholder=  "(field value type)",
        field_property_uri= "annal:field_value_type",
        field_render_type=  "Identifier",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Identifier",
        field_placement=    "small-12 medium-3 columns show-for-medium-up"
        )
    # 4th field
    check_context_field(test, f3,
        field_id=           "Entity_label",
        field_name=         "Entity_label",
        field_label=        "Label",
        field_placeholder=  "(label)",
        field_property_uri= "rdfs:label",
        field_render_type=  "Text",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Text",
        field_placement=    "small-4 medium-3 columns"
        )
    # Selection of field entities from list
    entities = context_list_entities(response.context)
    entity_ids = [ context_list_item_field_value(response.context, e, 0) for e in entities ]
    for f in field_entities:
        for eid in range(len(entities)):
            item_fields = context_list_item_fields(response.context, entities[eid])
            if item_fields[0]['field_value'] == f[0]:
                # Expected field entity found in context data, check details...
                for fid in range(4):
                    item_field = item_fields[fid]
                    head_field = head_fields[0]['row_field_descs'][fid]
                    for fkey in (
                            'field_id', 'field_name', 'field_label', 
                            'field_property_uri', 'field_render_type',
                            'field_placement', 'field_value_type'):
                        test.assertEqual(item_field[fkey], head_field[fkey])
                    # Check listed field values
                    check_context_list_field_value(test, item_field, f[fid])
                break
        else:
            test.fail("Field %s not found in context"%f[0])
    return

type_no_options   = [ FieldChoice('', label="(no options)") ]
def check_type_view_context_fields(test, response, 
        action="",
        entity_id="", orig_entity_id=None,
        type_id="_type",
        type_label="(?type_label)",
        type_comment="(?type_comment)",
        type_uri="(?type_uri)",
        type_supertype_uris="",
        type_view="Default_view", type_view_options=None,
        type_list="Default_list", type_list_options=None,
        type_aliases=[]
        ):
    # Common entity attributes
    test.assertEqual(response.context['entity_id'],        entity_id)
    test.assertEqual(response.context['orig_id'],          orig_entity_id or entity_id)
    test.assertEqual(response.context['type_id'],          type_id)
    test.assertEqual(response.context['orig_type'],        type_id)
    test.assertEqual(response.context['coll_id'],          'testcoll')
    test.assertEqual(response.context['action'],           action)
    test.assertEqual(response.context['view_id'],          'Type_view')
    # View fields
    test.assertEqual(len(response.context['fields']), 7)
    f0 = context_view_field(response.context, 0, 0)
    f1 = context_view_field(response.context, 1, 0)
    f2 = context_view_field(response.context, 2, 0)
    f3 = context_view_field(response.context, 3, 0)
    f4 = context_view_field(response.context, 4, 0)
    f5 = context_view_field(response.context, 5, 0)
    f6 = context_view_field(response.context, 5, 1)
    f7 = context_view_field(response.context, 6, 0)
    # 1st field - Id
    check_context_field(test, f0,
        field_id=           "Type_id",
        field_name=         "entity_id",
        field_label=        "Type Id",
        field_placeholder=  "(type id)",
        field_property_uri= "annal:id",
        field_render_type=  "EntityId",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:EntityRef",
        field_placement=    "small-12 medium-6 columns",
        field_value=        entity_id,
        options=            type_no_options
        )
    # 2nd field - Label
    check_context_field(test, f1,
        field_id=           "Type_label",
        field_name=         "Type_label",
        field_label=        "Label",
        field_placeholder=  "(label)",
        field_property_uri= "rdfs:label",
        field_render_type=  "Text",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Text",
        field_placement=    "small-12 columns",
        field_value=        type_label,
        options=            type_no_options
        )
    # 3rd field - comment
    type_comment_placeholder = (
        "(type description)"
        )
    check_context_field(test, f2,
        field_id=           "Type_comment",
        field_name=         "Type_comment",
        field_label=        "Comment",
        field_placeholder=  type_comment_placeholder,
        field_property_uri= "rdfs:comment",
        field_render_type=  "Markdown",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Richtext",
        field_placement=    "small-12 columns",
        field_value=        type_comment,
        options=            type_no_options
        )
    # 4th field - URI
    type_uri_placeholder = (
        "(Type URI)"
        )
    check_context_field(test, f3,
        field_id=           "Type_uri",
        field_name=         "Type_uri",
        field_label=        "Type URI",
        field_placeholder=  type_uri_placeholder,
        field_property_uri= "annal:uri",
        field_render_type=  "Identifier",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Identifier",
        field_value=        type_uri,
        options=            type_no_options
        )
    # 5th field - Supertype URIs
    type_supertype_uris_placeholder = (
        "(Supertype URIs or CURIEs)"
        )
    check_context_field(test, f4,
        field_id=           "Type_supertype_uris",
        field_name=         "Type_supertype_uris",
        field_label=        "Supertype URIs",
        field_placeholder=  type_supertype_uris_placeholder,
        field_property_uri= "annal:supertype_uri",
        field_render_type=  "Group_Seq_Row",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Type_supertype_uri",
        field_value=        type_supertype_uris,
        options=            type_no_options
        )
    # 6th field - view id
    type_view_id_placeholder = (
        "(view id)"
        )
    check_context_field(test, f5,
        field_id=           "Type_view",
        field_name=         "Type_view",
        field_label=        "Default view",
        field_placeholder=  type_view_id_placeholder,
        field_property_uri= "annal:type_view",
        field_render_type=  "Enum_optional",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:View",
        field_placement=    "small-12 medium-6 columns",
        field_value=        type_view,
        options=            type_view_options
        )
    # 7th field - list id
    type_list_id_placeholder = (
        "(list id)"
        )
    check_context_field(test, f6,
        field_id=           "Type_list",
        field_name=         "Type_list",
        field_label=        "Default list",
        field_placeholder=  type_list_id_placeholder,
        field_property_uri= "annal:type_list",
        field_render_type=  "Enum_optional",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:List",
        field_placement=    "small-12 medium-6 columns",
        field_value=        type_list,
        options=            type_list_options
        )
    # 8th field - field aliases
    type_aliases_placeholder = (
        "(field aliases)"
        )
    check_context_field(test, f7,
        field_id=           "Type_aliases",
        field_name=         "Type_aliases",
        field_label=        "Field aliases",
        field_placeholder=  type_aliases_placeholder,
        field_property_uri= "annal:field_aliases",
        field_render_type=  "Group_Seq_Row",
        field_value_mode=   "Value_direct",
        field_value_type=   "annal:Type_alias",
        field_placement=    "small-12 columns",
        field_value=        type_aliases,
        options=            type_no_options
        )
    return

def check_field_record(test, field_record,
        field_id=None,
        field_ref=None,
        field_types=None,
        field_name=None,
        field_type_id=None,
        field_type=None,
        field_uri=None,
        field_url=None,
        field_label=None,
        field_comment=None,
        field_render_type=None,
        field_value_mode=None,
        field_property_uri=None,
        field_placement=None,
        field_entity_type=None,
        field_value_type=None,
        field_placeholder=None,
        field_default=None,
        ):
        if field_id:
            test.assertEqual(field_id,           field_record['annal:id'])
        if field_ref:
            test.assertEqual(field_ref,          field_record['@id'])
        if field_types:
            test.assertEqual(field_types,        field_record['@type'])
        if field_type_id:
            test.assertEqual(field_type_id,      field_record['annal:type_id'])
        if field_type:
            test.assertEqual(field_type,         field_record['annal:type'])
        if field_uri:
            test.assertEqual(field_uri,          field_record['annal:uri'])
        if field_url:
            test.assertEqual(field_url,          field_record['annal:url'])
        if field_label:
            test.assertEqual(field_label,        field_record['rdfs:label'])
        if field_comment:
            test.assertEqual(field_comment,      field_record['rdfs:comment'])

        if field_name:
            test.assertEqual(field_name,         field_record['annal:field_name'])
        if field_render_type:
            test.assertEqual(
                field_render_type,  
                extract_entity_id(field_record['annal:field_render_type'])
                )
        if field_value_mode:
            test.assertEqual(
                field_value_mode,   
                extract_entity_id(field_record['annal:field_value_mode'])
                )
        if field_property_uri:
            test.assertEqual(field_property_uri, field_record['annal:property_uri'])
        if field_placement:
            test.assertEqual(field_placement,    field_record['annal:field_placement'])
        if field_entity_type:
            test.assertEqual(field_entity_type,  field_record['annal:field_entity_type'])
        if field_value_type:
            test.assertEqual(field_value_type,   field_record['annal:field_value_type'])
        if field_placeholder:
            test.assertEqual(field_placeholder,  field_record['annal:placeholder'])
        if field_default:
            test.assertEqual(field_default,      field_record['annal:default_value'])
        return

#   -----------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
