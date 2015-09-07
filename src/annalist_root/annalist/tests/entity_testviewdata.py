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

from entity_testutils           import (
    collection_dir, 
    site_title, 
    collection_entity_view_url
    )
from entity_testentitydata      import entitydata_list_type_url
from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )

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

def recordview_site_url(site, view_id="testview"):
    return site._entityurl + layout.SITE_VIEW_PATH%{'id': view_id} + "/"

def recordview_coll_url(site, coll_id="testcoll", view_id="testview"):
    return site._entityurl + layout.SITE_COLL_PATH%{'id': coll_id} + "/" + layout.COLL_VIEW_PATH%{'id': view_id} + "/"

def recordview_url(coll_id, view_id):
    """
    URI for record view description data; also view using default entity view
    """
    if not valid_id(view_id):
        view_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_view", entity_id=view_id)

def recordview_edit_url(action=None, coll_id=None, view_id=None):
    """
    URI for record view description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordViewDeleteView'  if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id}
    if action != "delete":
        kwargs.update({'action': action, 'type_id': "_view", 'view_id': "View_view"})
    if view_id:
        if valid_id(view_id):
            kwargs.update({'entity_id': view_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordView data for default view
#
#   -----------------------------------------------------------------------------

def recordview_value_keys(view_uri=False, target_record_type=True):
    keys = set(
        [ 'annal:id', 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label', 'rdfs:comment'
        , 'annal:open_view'
        , 'annal:view_fields'
        ])
    if view_uri:
        keys.add('annal:uri')
    if target_record_type:
        keys.add('annal:record_type')
    return keys

def recordview_load_keys(view_uri=False, target_record_type=True):
    return (
        recordview_value_keys(view_uri=view_uri, target_record_type=target_record_type) | 
        {"@id", '@type'}
        )

def recordview_create_values(
        coll_id="testcoll", view_id="testview", update="RecordView", view_uri=None, 
        target_record_type="annal:Test_default",
        num_fields=4, field3_placement="small:0,12",
        extra_field=None, extra_field_uri=None
        ):
    """
    Entity values used when creating a record view entity
    """
    view_values = (
        { 'annal:type':         "annal:View"
        , 'rdfs:label':         "%s %s/%s"%(update, coll_id, view_id)
        , 'rdfs:comment':       "%s help for %s in collection %s"%(update, view_id, coll_id)
        , 'annal:record_type':  target_record_type
        , 'annal:open_view':    True
        , 'annal:view_fields':
          [ { 'annal:field_id':         "_field/Entity_id"
            , 'annal:field_placement':  "small:0,12;medium:0,6"
            }
          , { 'annal:field_id':         "_field/Entity_type"
            , 'annal:field_placement':  "small:0,12;medium:6,6"
            }
          , { 'annal:field_id':         "_field/Entity_label"
            , 'annal:field_placement':  "small:0,12"
            }
          , { 'annal:field_id':         "_field/Entity_comment"
            # , 'annal:field_placement':  field3_placement
            }
          ]
        })
    if view_uri:
        view_values['annal:uri'] = view_uri
    if field3_placement:
        view_values['annal:view_fields'][3]['annal:field_placement'] = field3_placement
    if extra_field:
        efd = (
            { 'annal:field_id':         extra_field
            , 'annal:field_placement':  "small:0,12"
            })
        if extra_field_uri:
            efd['annal:property_uri'] = extra_field_uri
        view_values['annal:view_fields'].append(efd)
    if num_fields == 0:
        view_values['annal:view_fields'] = []
    return view_values

def recordview_values(
        coll_id="testcoll", view_id="testtype", view_uri=None, 
        update="RecordView", hosturi=TestHostUri, 
        target_record_type="annal:Test_default",
        num_fields=4, field3_placement="small:0,12",
        extra_field=None, extra_field_uri=None):
    d = recordview_create_values(
        coll_id, view_id, update=update, view_uri=view_uri,
        target_record_type=target_record_type,
        num_fields=num_fields, field3_placement=field3_placement,
        extra_field=extra_field, extra_field_uri=extra_field_uri
        ).copy()
    view_url = recordview_url(coll_id, view_id)
    d.update(
        { 'annal:id':       view_id
        , 'annal:type_id':  "_view"
        , 'annal:url':      view_url
        })
    return d

def recordview_read_values(
        coll_id="testcoll", view_id="testview", view_uri=None, 
        target_record_type="annal:Test_default",
        update="RecordView", hosturi=TestHostUri):
    d = recordview_values(
        coll_id, view_id, view_uri=view_uri, 
        target_record_type=target_record_type,
        update=update, hosturi=hosturi
        ).copy()
    d.update(
        { '@id':            "./"
        , '@type':          ["annal:View"]
        })
    return d

def recordview_values_add_field(view_data, 
    field_id="Entity_comment", 
    field_property_uri="rdfs:comment",
    field_placement="small:0,12"
    ):
    view_data['annal:view_fields'].append(
        { 'annal:field_id':         field_id
        , 'annal:property_uri':     field_property_uri
        , 'annal:field_placement':  field_placement
        })
    return view_data

#   -----------------------------------------------------------------------------
#
#   ----- Data in recordview view for default entity data
#
#   -----------------------------------------------------------------------------

def recordview_entity_view_context_data(
        coll_id="testcoll", view_id=None, orig_id=None, view_ids=[],
        action=None, 
        target_record_type="annal:View",
        add_field=None, remove_field=None, move_up=None, move_down=None,
        update="RecordView"
    ):
    # Target record fields listed in the view description
    view_fields = (
          [ { 'annal:field_id':         "_field/Entity_id"
            , 'annal:field_placement':  "small:0,12;medium:0,6"
            }
          , { 'annal:field_id':         "_field/Entity_type"
            , 'annal:field_placement':  "small:0,12;medium:6,6"
            }
          , { 'annal:field_id':         "_field/Entity_label"
            , 'annal:property_uri':     "rdfs:label"
            , 'annal:field_placement':  "small:0,12"
            }
          , { 'annal:field_id':         "_field/Entity_comment"
            , 'annal:property_uri':     "rdfs:comment"
            # , 'annal:field_placement':  field3_placement
            }
          ])
    # NOTE: context['fields'][i]['field_id'] comes from FieldDescription instance via
    #       bound_field, so type prefix is stripped.  This does not apply to the field
    #       ids actually coming from the view form.
    context_dict = (
        { 'title':              "Collection %s"%(coll_id)
        , 'coll_id':            coll_id
        , 'type_id':            '_view'
        , 'orig_id':            'orig_view_id'
        , 'record_type':        'annal:View'
        , 'fields':
          [ { 'field_id':           'View_id'               # fields[0]
            , 'field_name':         'entity_id'
            , 'field_target_type':  'annal:Slug'
            , 'field_label':        'Id'
            , 'field_render_type':  'EntityId'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            # , 'field_value':      (Supplied separately)
            , 'options':            []
            }
          , { 'field_id':           'View_label'            # fields[1]
            , 'field_name':         'View_label'
            , 'field_target_type':  'annal:Text'
            , 'field_label':        'Label'
            , 'field_render_type':  'Text'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        '%s data ... (%s/%s)'%(update, coll_id, view_id)
            , 'options':            []
            }
          , { 'field_id':           'View_comment'          # fields[2]
            , 'field_name':         'View_comment'
            , 'field_label':        'Help'
            , 'field_target_type':  'annal:Richtext'
            , 'field_render_type':  'Markdown'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        '%s description ... (%s/%s)'%(update, coll_id, view_id)
            , 'options':            []
            }
          , { 'field_id':           'View_target_type'      # fields[3]
            , 'field_name':         'View_target_type'
            , 'field_target_type':  'annal:Identifier'
            , 'field_label':        'Record type'
            , 'field_render_type':  'Identifier'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        target_record_type
            , 'options':            []
            }
          , { 'field_id':           'View_edit_view'        # fields[4]
            , 'field_name':         'View_edit_view'
            , 'field_target_type':  'annal:Boolean'
            , 'field_label':        'Editable view?'
            , 'field_render_type':  'CheckBox'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12;medium:0,6')
            , 'field_value':        True
            , 'options':            []
            }
          , { "field_id":           'View_fields'           # fields[5]
            , 'field_render_type':  'RepeatGroupRow'
            , 'field_name':         'View_fields'
            , 'field_target_type':  'annal:Field_group'
            , 'field_label':        'Fields'
            , 'field_render_type':  'RepeatGroupRow'
            , 'field_value_mode':   'Value_direct'
            , 'field_placement':    get_placement_classes('small:0,12')
            , 'field_value':        view_fields
            , 'options':            []
            }
          ]
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_view")
        })
    if view_id:
        context_dict['fields'][0]['field_value'] = view_id
        context_dict['fields'][1]['field_value'] = '%s %s/%s'%(update, coll_id, view_id)
        context_dict['fields'][2]['field_value'] = '%s help for %s in collection %s'%(update, view_id, coll_id)
        context_dict['orig_id']     = view_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    if add_field:
        context_dict['fields'][5]['field_value'].append(
            { 'annal:field_id':         None
            , 'annal:property_uri':     None
            , 'annal:field_placement':  None
            })
    if remove_field:
        context_dict['fields'][5]['field_value'][3:4] = []
    if move_up:
        assert move_up == [2,3]
        fields = context_dict['fields'][5]['field_value']
        context_dict['fields'][5]['field_value'] = [ fields[i]  for i in [0,2,3,1] ]
    if move_down:
        assert move_down == [1]
        fields = context_dict['fields'][5]['field_value']
        context_dict['fields'][5]['field_value'] = [ fields[i]  for i in [0,2,1,3] ]
    return context_dict

def recordview_entity_view_form_data(
        coll_id="testcoll", 
        view_id=None, orig_id=None, 
        action=None, cancel=None, 
        target_record_type="annal:View",
        field3_placement="small:0,12",
        extra_field=None,       # Extra field id for some tests (e.g. dup property uri)
        extra_field_uri=None,   # Extra field property URI to add in
        add_field=None,         # True for add field option
        remove_fields=None,     # List of field numbers to remove (as strings)
        move_up_fields=None,    # List of field numbers to move up
        move_down_fields=None,  # List of field numbers to move down
        new_enum=None,          # Id of new-value button enumerated value field
        update="RecordView"
        ):
    form_data_dict = (
        { 'View_label':         '%s data ... (%s/%s)'%(update, coll_id, view_id)
        , 'View_comment':       '%s description ... (%s/%s)'%(update, coll_id, view_id)
        , 'View_target_type':   target_record_type
        , 'View_edit_view':     "Yes"
        , 'orig_id':            'orig_view_id'
        , 'record_type':        'annal:View'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_view")
        # View fields
        , 'View_fields__0__Field_id':           "_field/Entity_id"
        , 'View_fields__0__Field_placement':    "small:0,12;medium:0,6"
        , 'View_fields__1__Field_id':           "_field/Entity_type"
        , 'View_fields__1__Field_placement':    "small:0,12;medium:6,6"
        , 'View_fields__2__Field_id':           "_field/Entity_label"
        , 'View_fields__2__Field_property':     "rdfs:label"
        , 'View_fields__2__Field_placement':    "small:0,12"
        , 'View_fields__3__Field_id':           "_field/Entity_comment"
        , 'View_fields__3__Field_property':     "rdfs:comment"
        , 'View_fields__3__Field_placement':    field3_placement
        })
    if extra_field:
        # Insert extra field with supplied Id
        form_data_dict['View_fields__4__Field_id']        = "_field/"+extra_field
        form_data_dict['View_fields__4__Field_placement'] = "small:0,12"
        if extra_field_uri:
            form_data_dict['View_fields__4__Field_property'] = extra_field_uri
    if view_id:
        form_data_dict['entity_id']     = view_id
        form_data_dict['orig_id']       = view_id
        form_data_dict['View_label']    = '%s %s/%s'%(update, coll_id, view_id)
        form_data_dict['View_comment']  = '%s help for %s in collection %s'%(update, view_id, coll_id)
        form_data_dict['View_uri']      = TestBaseUri + "/c/%s/d/_view/%s/"%(coll_id, view_id)
        form_data_dict['orig_type']     = "_view"
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if action:
        form_data_dict['action']        = action
    if cancel:
        form_data_dict['cancel']        = "Cancel"
    elif add_field:
        form_data_dict['View_fields__add'] = "Add field"
    elif remove_fields:
        form_data_dict['View_fields__remove'] = "Remove field"
        if remove_fields != "no-selection":
            form_data_dict['View_fields__select_fields'] = remove_fields
    elif move_up_fields:
        form_data_dict['View_fields__up'] = "Move up"
        if move_up_fields != "no-selection":
            form_data_dict['View_fields__select_fields'] = move_up_fields
    elif move_down_fields:
        form_data_dict['View_fields__down'] = "Move down"
        if move_down_fields != "no-selection":
            form_data_dict['View_fields__select_fields'] = move_down_fields
    elif new_enum:
        form_data_dict[new_enum]        = new_enum
    else:
        form_data_dict['save']          = 'Save'
    return form_data_dict

#   -----------------------------------------------------------------------------
#
#   ----- Recordview delete confirmation form data
#
#   -----------------------------------------------------------------------------

def recordview_delete_confirm_form_data(view_id=None):
    return (
        { 'viewlist':    view_id,
          'view_delete': 'Delete'
        })

# End.
