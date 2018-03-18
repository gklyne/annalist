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

from annalist.util              import valid_id, extract_entity_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout
from annalist                   import message

from annalist.views.uri_builder import uri_base, uri_params, uri_with_params

from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testfielddesc       import get_field_description, get_bound_field
from entity_testutils import (
    collection_dir, 
    entitydata_list_url_query,
    site_view_url,
    collection_view_url,
    collection_edit_url,
    collection_entity_view_url,
    site_title,
    context_field_row
    )
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

#   -----------------------------------------------------------------------------
#
#   Helper functions
#
#   -----------------------------------------------------------------------------

def value_or_default(value, default):
    """
    Returns the supplied value of it is non None, otherwise the supplied default.
    """
    return value if value is not None else default

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

# Each entity type has its own data directory within a collection:

def recorddata_dir(coll_id="testcoll", type_id="testtype"):
    return collection_dir(coll_id) + layout.COLL_TYPEDATA_PATH%{'id': type_id} + "/"

def entitydata_dir(coll_id="testcoll", type_id="testtype", entity_id="testentity"):
    return recorddata_dir(coll_id, type_id) + layout.TYPEDATA_ENTITY_PATH%{'id': entity_id} + "/"


#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These all use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def entity_url(coll_id="testcoll", type_id="testtype", entity_id="entity_id"):
    """
    URI for entity data; also view using default entity view
    """
    if not valid_id(entity_id):
        entity_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def entity_resource_url(
    coll_id="testcoll", type_id="testtype", entity_id="entity_id", 
    resource_ref=layout.ENTITY_DATA_FILE
    ):
    """
    URI for entity resource data
    """
    base = entity_url(coll_id, type_id, entity_id)
    return urlparse.urljoin(base, resource_ref)

def entitydata_edit_url(action=None, coll_id="testcoll", type_id=None, entity_id=None, view_id="Default_view"):
    viewname = ( 
        'AnnalistEntityNewView'             if action == "new" else
        'AnnalistEntityEditView'            if action is not None else
        'AnnalistEntityDataView'
        )
    kwargs = {'coll_id': coll_id, 'view_id': view_id}
    if action:
        kwargs.update({'action': action})
    if type_id:
        kwargs.update({'type_id': type_id})
    if entity_id:
        kwargs.update({'entity_id': entity_id})
    return reverse(viewname, kwargs=kwargs)

def entitydata_list_all_url(
        coll_id="testcoll", list_id=None, 
        scope=None, continuation_url=None, query_params=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id}
    else:
        viewname = "AnnalistEntityDefaultListAll"
        kwargs   = {'coll_id': coll_id}
    return entitydata_list_url_query(viewname, kwargs, 
        query_params,
        { 'scope': scope
        , 'continuation_url': continuation_url
        })
    # if scope is not None:
    #     kwargs['scope'] = scope
    # return reverse(viewname, kwargs=kwargs)

def entitydata_list_type_url(
        coll_id="testcoll", type_id="testtype", list_id=None, 
        scope=None, continuation_url=None, query_params=None):
    if list_id:
        viewname = "AnnalistEntityGenericList"
        kwargs   = {'list_id': list_id, 'coll_id': coll_id, 'type_id': type_id}
    else:
        viewname = "AnnalistEntityDefaultListType"
        kwargs   = {'coll_id': coll_id, 'type_id': type_id}
    return entitydata_list_url_query(viewname, kwargs, 
        query_params,
        { 'scope': scope
        , 'continuation_url': continuation_url
        })
    # if scope is not None:
    #     kwargs['scope'] = scope
    # return reverse(viewname, kwargs=kwargs)

def entitydata_delete_confirm_url(coll_id="testcoll", type_id="testtype"):
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

def entitydata_type(type_id):
    """
    Returns type URI/CURIE/ref for indicated type id.
    """
    if type_id == "_type":
        return "annal:Type"
    elif type_id == "_list":
        return "annal:List"
    elif type_id == "_view":
        return "annal:View"
    elif type_id == "_field":
        return "annal:Field"
    else:
        return "annal:EntityData"

def entitydata_value_keys(entity_uri=False):
    """
    Keys in default view entity data
    """
    keys = (
        [ '@type'
        , 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        ])
    if entity_uri:
        keys.add('annal:uri')
    return keys

def entitydata_load_keys(entity_uri=False):
    return (
        recordview_value_keys(entity_uri=entity_uri) | 
        {"@id", '@type', '@context'}
        )

def entitydata_create_values(
        entity_id, update="Entity", coll_id="testcoll", type_id="testtype", 
        entity_uri=None, type_uri=None, supertype_uris=None,
        hosturi=TestHostUri,
        extra_fields=None):
    """
    Data used when creating entity test data
    """
    if type_uri is not None:
        types = [type_uri, entitydata_type(type_id)]
        if supertype_uris is not None:
            types = types + supertype_uris
    else:
        types = [entity_url(coll_id, "_type", type_id), entitydata_type(type_id)]
    # log.info('entitydata_create_values: types %r'%(types,)) 
    d = (
        { '@type':          types
        , 'annal:type':     types[0]
        , 'rdfs:label':     '%s testcoll/%s/%s'%(update, type_id, entity_id)
        , 'rdfs:comment':   '%s coll testcoll, type %s, entity %s'%(update, type_id, entity_id)
        })
    if entity_uri:
        d['annal:uri'] = entity_uri
    if extra_fields:
        d.update(extra_fields)
    return d

def entitydata_values_add_field(data, property_uri, dup_index, value):
    """
    Add field to data; if duplicate then reformat appropriately.

    Updates and returns supplied entity value dictionary.
    """
    if property_uri in data:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    data[property_uri+suffix] = value
    return data

def entitydata_values(
        entity_id, update="Entity", 
        coll_id="testcoll", type_id="testtype", 
        entity_uri=None,
        type_uri=None, supertype_uris=None, 
        hosturi=TestHostUri
        ):
    # type_uri = entity_url(coll_id, "_type", type_id)
    dataurl = entity_url(coll_id, type_id, entity_id)
    d = entitydata_create_values(
        entity_id, update=update, coll_id=coll_id, type_id=type_id, 
        entity_uri=entity_uri, type_uri=type_uri, supertype_uris=supertype_uris,
        hosturi=hosturi
        ).copy() #@@ copy needed here?
    d.update(
        { '@id':            "%s/%s"%(type_id, entity_id)
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
        , 'annal:id':       entity_id
        , 'annal:type_id':  type_id
        , 'annal:url':      dataurl
        })
    # log.info("entitydata_values %r"%(d,))
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity in specified view context data
#
#   -----------------------------------------------------------------------------

def specified_view_context_data(
        coll_id="testcoll", type_id="testtype", 
        view_id="Default_view", view_heading="Default record view",
        entity_id=None, orig_id=None,
        type_ref=None, type_choices=None, type_ids=[],
        entity_label=None, entity_descr=None, 
        record_type="annal:EntityData",
        view_fields=None,
        update="Entity",
        action=None, 
        continuation_url=None
    ):
    """
    Returns view context test data for entity presented using specified view
    """
    if entity_id:
        entity_label = value_or_default(entity_label,
            '%s (%s/%s/%s)'%(update, coll_id, type_id, entity_id)
            )
        entity_descr = value_or_default(entity_descr,
            '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
            )
    else:
        entity_label = value_or_default(entity_label,
            '%s (%s/%s/)'%(update, coll_id, type_id)
            )
        entity_descr = value_or_default(entity_descr,
            '%s coll %s, type %s, no entity id'%(update, coll_id, type_id)
            )
    continuation_url = value_or_default(continuation_url, 
        entitydata_list_type_url(coll_id, type_id)
        )
    view_title = (
        "%s - %s - Collection %s"%(entity_label, view_heading, coll_id) if entity_label
        else
        "%s - Collection %s"%(view_heading, coll_id)
        )
    if view_fields is None:
        view_fields = (
            [ context_field_row(
                get_bound_field("Entity_id", entity_id),                          # 0 (0,0)
                get_bound_field("Entity_type", type_ref, options=type_choices)    # 1 (0,1)
                )
            , context_field_row(
                get_bound_field("Entity_label", entity_label)                     # 2 (1,0)
                )
            , context_field_row(
                get_bound_field("Entity_comment", entity_descr)                   # 3 (2,0)
                )
            ])
    context_dict = (
        { 'title':              view_title
        , 'heading':            view_heading
        , 'coll_id':            coll_id
        , 'type_id':            type_id
        , 'view_id':            view_id
        , 'entity_id':          entity_id
        , 'orig_type':          type_id
        , 'record_type':        record_type
        , 'fields':             view_fields
        , 'continuation_url':   continuation_url
        })
    if orig_id is not None:
        context_dict['orig_id']     = orig_id
    elif entity_id and action != "new":
        context_dict['orig_id']     = entity_id
    if action:  
        context_dict['action']      = action
    return context_dict

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in Default_view
#
#   -----------------------------------------------------------------------------

def default_view_context_data(
        entity_id=None, orig_id=None, 
        coll_id="testcoll", type_id="testtype", 
        type_ref=None, type_choices=None, type_ids=[],
        entity_label=None, entity_descr=None,
        view_label="Default record view",
        record_type="annal:EntityData",
        update="Entity",
        action=None, 
        continuation_url=None
    ):
    """
    Returns view context test data for entity presented using default view
    """
    if entity_id:
        type_ref = value_or_default(type_ref,
            "_type/"+type_id if valid_id(type_id) else None
            )
        entity_label = value_or_default(entity_label,
            '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
            )
        entity_descr = value_or_default(entity_descr,
            '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
            )
    else:
        type_ref     = type_ref or ""
        entity_label = value_or_default(entity_label,
            '%s data ... (%s/%s)'%(update, coll_id, type_id)
            )
        entity_descr = value_or_default(entity_descr,
            '%s description ... (%s/%s)'%(update, coll_id, type_id)
            )
    continuation_url = value_or_default(continuation_url, 
        entitydata_list_type_url("testcoll", type_id)
        )
    view_title = (
        "%s - %s - Collection %s"%(entity_label, view_label, coll_id) if entity_label
        else
        "%s - Collection %s"%(view_label, coll_id)
        )
    view_fields = (
        [ context_field_row(
            get_bound_field("Entity_id", entity_id),                          # 0 (0,0)
            get_bound_field("Entity_type", type_ref, options=type_choices)    # 1 (0,1)
            )
        , context_field_row(
            get_bound_field("Entity_label", entity_label)                     # 2 (1,0)
            )
        , context_field_row(
            get_bound_field("Entity_comment", entity_descr)                   # 3 (2,0)
            )
        ])
    context_dict = (
        { 'title':              view_title
        , 'heading':            view_label
        , 'coll_id':            coll_id
        , 'type_id':            type_id
        , 'orig_id':            orig_id
        , 'record_type':        record_type
        , 'fields':             view_fields
        , 'continuation_url':   continuation_url
        })
    if orig_id:
        context_dict['orig_id']     = orig_id
    elif entity_id and action != "new":
        context_dict['orig_id']     = entity_id
    if action:  
        context_dict['action']      = action
    return context_dict

def entitydata_context_add_field(
    context_dict, field_id, dup_index, field_value,
        field_name='Entity_comment',
        field_label='Comment',
        field_render_type='Markdown',
        field_value_mode='Value_direct',
        field_value_type='annal:Richtext',
        field_placement='small:0,12',
        field_options=[]
        ):
    """
    Add field value to context; if duplicate then reformat appropriately.

    Field details default to Entity_comment

    Updates and returns supplied context dictionary.
    """
    #@@TODO: use field context from  entity_testfielddesc
    field_ids = [ f['field_id'] for f in context_dict['fields'] ]
    if field_id in field_ids:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    context_dict['fields'].append(
        { 'field_id':           field_id
        , 'field_value':        field_value
        , 'field_name':         field_name+suffix
        , 'field_label':        field_label
        , 'field_render_type':  field_render_type
        , 'field_value_mode':   field_value_mode
        , 'field_value_type':   field_value_type
        , 'field_placement':    get_placement_classes(field_placement)
        , 'options':            field_options
        })
    return context_dict

def default_view_form_data(
        coll_id="testcoll", orig_coll=None,
        type_id="testtype", orig_type=None,
        entity_id=None, orig_id=None, 
        action=None, cancel=None, close=None, view=None, edit=None, copy=None, 
        update="Entity",
        add_view_field=None, use_view=None, default_view=None,
        new_view=None, new_field=None, new_type=None, 
        new_enum=None, do_import=None
        ):
    # log.info("default_view_form_data: entity_id %s"%(entity_id))
    form_data_dict = (
        { 'Entity_label':       '%s data ... (%s/%s)'%(update, coll_id, type_id)
        , 'Entity_comment':     '%s description ... (%s/%s)'%(update, coll_id, type_id)
        , 'orig_id':            'orig_entity_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, orig_type or type_id)
        })
    if entity_id is not None:
        # Allow setting to blank string...
        form_data_dict['entity_id']       = entity_id
    if entity_id:
        form_data_dict['entity_type']     = "_type/"+type_id
        form_data_dict['Entity_label']    = '%s %s/%s/%s'%(update, coll_id, type_id, entity_id)
        form_data_dict['Entity_comment']  = '%s coll %s, type %s, entity %s'%(update, coll_id, type_id, entity_id)
        form_data_dict['orig_id']         = entity_id
        form_data_dict['orig_type']       = type_id
        form_data_dict['orig_coll']       = coll_id
    if orig_id:
        form_data_dict['orig_id']         = orig_id
    if orig_type:
        form_data_dict['orig_type']       = orig_type
    if orig_coll:
        form_data_dict['orig_coll']       = orig_coll
    if action:
        form_data_dict['action']          = action
    if cancel:
        form_data_dict['cancel']          = "Cancel"
    elif close:
        form_data_dict['close']           = "Close"
    elif view:
        form_data_dict['view']            = "View"
    elif edit:
        form_data_dict['edit']            = "Edit"
    elif copy:
        form_data_dict['copy']            = "Copy"
    elif add_view_field:
        form_data_dict['add_view_field']  = add_view_field
    elif use_view:
        form_data_dict['use_view']        = "Show view"
        form_data_dict['view_choice']     = use_view
    elif default_view:
        form_data_dict['default_view']    = "default_view"
    elif new_view:
        form_data_dict['new_view']        = new_view
    elif new_field:
        form_data_dict['new_field']       = new_field
    elif new_type:
        form_data_dict['new_type']        = new_type
    elif new_enum:
        form_data_dict[new_enum]          = new_enum
    elif do_import:
        form_data_dict[do_import]         = do_import
    else:
        form_data_dict['save']            = 'Save'
    return form_data_dict

def entitydata_form_add_field(form_data_dict, field_name, dup_index, value):
    """
    Add field value to form data; if duplicate then reformat appropriately.

    Updates and returns supplied form data dictionary.
    """
    if field_name in form_data_dict:
        suffix = "__%d"%dup_index
    else:
        suffix = ""
    form_data_dict[field_name+suffix] = value
    return form_data_dict

def entitydata_delete_form_data(entity_id=None, type_id="Default_type", list_id="Default_list"):
    return (
        { 'list_choice':        "_list/"+list_id
        , 'continuation_url':   ""
        , 'search_for':         ""
        , 'entity_select':      ["%s/%s"%(type_id, entity_id)]
        , 'delete':             "Delete"
        })

def entitydata_delete_confirm_form_data(entity_id=None, search=None):
    """
    Form data from entity deletion confirmation
    """
    form_data = (
        { 'entity_id':     entity_id,
          'entity_delete': 'Delete'
        })
    if search:
        form_data['search'] = search
    return form_data

#   -----------------------------------------------------------------------------
#
#   ----- Entity list
#
#   -----------------------------------------------------------------------------

def entitylist_form_data(
        action, list_scope_all=None, search="", 
        list_id="Default_list", entities=None, 
        continuation_url=None):
    """
    Form data from entity list form submission
    """
    form_actions = (
        { 'search':             "Find"
        , 'list_view':          "View"
        , 'new':                "New"
        , 'copy':               "Copy"
        , 'edit':               "Edit"
        , 'delete':             "Delete"
        , 'close':              "Close"
        , 'default_view':       "Set default"
        , 'customize':          "Customize"
        })
    if continuation_url is None:
        continuation_url = "" # collection_edit_url("testcoll")
    form_data = (
        { 'search_for':         search
        , 'list_choice':        "_list/"+list_id
        , 'continuation_url':   continuation_url
        })
    if list_scope_all is not None:
        form_data['list_scope_all'] = list_scope_all
    if entities is not None:
        form_data['entity_select'] = entities
    if action in form_actions:
        form_data[action] = form_actions[action]
    else:
        form_data[action] = action
    return form_data

#   -----------------------------------------------------------------------------
#
#   ----- Default field values
#
#   -----------------------------------------------------------------------------

def default_fields(
    coll_id=None, type_id=None, entity_id=None, 
    width=12, **kwargs):
    """
    Returns a function that accepts a field width and returns a dictionary of entity values
    for testing.  The goal is to isolate default entity value settings from the test cases.
    """
    def_label       = kwargs.get("default_label",
        default_label(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
        )
    def_comment     = kwargs.get("default_comment",
        default_comment(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
        )
    def_label_esc   = def_label.replace("'", "&#39;")
    def_comment_esc = def_comment.replace("'", "&#39;")
    def_entity_url  = collection_entity_view_url(coll_id=coll_id, type_id=type_id, entity_id=entity_id)
    collection_url  = collection_view_url(coll_id).rstrip("/")
    def def_fields(width=12):
        fields = layout_classes(width=width)
        fields.update(
            { 'coll_id':             coll_id
            , 'type_id':             type_id
            , 'entity_id':           entity_id
            , 'default_label':       def_label
            , 'default_comment':     def_comment
            , 'default_label_esc':   def_label_esc
            , 'default_comment_esc': def_comment_esc
            , 'default_entity_url':  def_entity_url
            , 'collection_url':      collection_url
            })
        if kwargs:
            fields.update(kwargs)
        return fields
    return def_fields


def default_label(coll_id=None, type_id=None, entity_id=None):
    # Note: for built-in types, default values matches corresponding sitedata _initial_values
    if type_id in ["_type", "_view", "_list", "_field"]:
        return ""
    return message.ENTITY_DEFAULT_LABEL%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def default_comment(coll_id=None, type_id=None, entity_id=None):
    # Note: for built-in types, default values matches corresponding sitedata _initial_values
    if type_id in ["_type", "_view", "_list", "_field"]:
        return ""
    #@@
    # if type_id == "_field":
    #     return "(tooltip text here)"
    #@@
    return message.ENTITY_DEFAULT_COMMENT%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

def error_label(coll_id=None, type_id=None, entity_id=None):
    return message.ENTITY_MESSAGE_LABEL%dict(coll_id=coll_id, type_id=type_id, entity_id=entity_id)

#   -----------------------------------------------------------------------------
#
#   ----- Field layout classes
#
#   -----------------------------------------------------------------------------

def layout_classes(width=12):
    if width == 2:
        class_dict = (
            { 'space_classes':          "medium-2 columns show-for-medium-up"
            })
    elif width == 4:
        class_dict = (
            { 'label_classes':          "view-label small-12 medium-6 columns"
            , 'input_classes':          "view-value small-12 medium-6 columns"
            , 'col_head_classes':       "view-label col-head small-12 medium-4 columns"
            , 'col_item_classes':       "view-value col-???? small-12 medium-4 columns"
            , 'button_wide_classes':    "small-12 medium-4 columns"
            })
    elif width == 6:
        class_dict = (
            { 'label_classes':          "view-label small-12 medium-4 columns"
            , 'input_classes':          "view-value small-12 medium-8 columns"
            , 'col_head_classes':       "view-label col-head small-12 medium-6 columns"
            , 'col_item_classes':       "small-12 medium-6 columns"
            , 'button_wide_classes':    "small-12 medium-6 columns"
            })
    elif width == 10:
        class_dict = (
            { 'button_wide_classes':    "small-10 columns"
            })
    elif width == 12:
        class_dict = (
            { 'group_label_classes':    "group-label small-12 medium-2 columns"
            , 'group_placeholder_classes':  "group-placeholder small-12 medium-10 columns"
            , 'group_space_classes':    "small-12 medium-2 columns hide-for-small-only"
            , 'group_row_head_classes': "small-12 medium-10 columns hide-for-small-only"
            , 'group_row_body_classes': "small-12 medium-10 columns"
            , 'group_buttons_classes':  "group-buttons small-12 medium-10 columns"
            , 'label_classes':          "view-label small-12 medium-2 columns"
            , 'input_classes':          "view-value small-12 medium-10 columns"
            , 'col_head_classes':       "view-label col-head small-12 columns"
            , 'col_item_classes':       "view-value col-???? small-12 columns"
            , 'space_classes':          "medium-2 columns show-for-medium-up"
            , 'button_wide_classes':    "small-12 medium-10 columns"
            , 'button_half_classes':    "form-buttons small-12 medium-5 columns"
            })
    else:
        assert False, "Unexpected width %r"%width
    class_dict.update(
        { 'button_left_classes':        "form-buttons small-12 columns"
        , 'button_right_classes':       "form-buttons small-12 columns text-right"
        , 'button_r_med_up_classes':    "form-buttons small-12 columns medium-up-text-right"        
        })
    return class_dict

# End.
