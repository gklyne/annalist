"""
Utility functions to support entity data testing
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse
import copy
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.conf                import settings
from django.http                import QueryDict
from django.utils.http          import urlquote, urlunquote
from django.core.urlresolvers   import resolve, reverse

from annalist.util              import valid_id
from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from annalist.views.form_utils.fieldchoice  import FieldChoice
from annalist.views.fields.render_placement import (
    get_placement_classes
    )

from entity_testfielddesc       import get_field_description, get_bound_field
from entity_testentitydata      import entitydata_list_type_url
from entity_testutils           import (
    collection_dir, 
    site_title, 
    collection_entity_view_url,
    context_field_row
    )
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

def recordview_coll_url(site, coll_id="testcoll", view_id="testview"):
    return urlparse.urljoin(
        site._entityurl,
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_VIEW_PATH%{'id': view_id} + "/"
        )

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

def recordview_value_keys(view_uri=False, view_entity_type=True):
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
    if view_entity_type or (view_entity_type == ""):
        keys.add('annal:view_entity_type')
    return keys

def recordview_load_keys(view_uri=False, view_entity_type=True):
    return (
        recordview_value_keys(view_uri=view_uri, view_entity_type=view_entity_type) | 
        {"@id", '@type', '@context'}
        )

def recordview_create_values(
        coll_id="testcoll", view_id="testview", update="RecordView", view_uri=None, 
        view_entity_type="annal:Test_default",
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
        , 'annal:view_entity_type':  view_entity_type
        , 'annal:open_view':    True
        , 'annal:view_fields':
          [ { 'annal:field_id':         layout.FIELD_TYPEID+"/Entity_id"
            , 'annal:field_placement':  "small:0,12;medium:0,6"
            }
          , { 'annal:field_id':         layout.FIELD_TYPEID+"/Entity_type"
            , 'annal:field_placement':  "small:0,12;medium:6,6"
            }
          , { 'annal:field_id':         layout.FIELD_TYPEID+"/Entity_label"
            , 'annal:field_placement':  "small:0,12"
            }
          , { 'annal:field_id':         layout.FIELD_TYPEID+"/Entity_comment"
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
        view_entity_type="annal:Test_default",
        num_fields=4, field3_placement="small:0,12",
        extra_field=None, extra_field_uri=None):
    d = recordview_create_values(
        coll_id, view_id, update=update, view_uri=view_uri,
        view_entity_type=view_entity_type,
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
        view_entity_type="annal:Test_default",
        update="RecordView", hosturi=TestHostUri):
    d = recordview_values(
        coll_id, view_id, view_uri=view_uri, 
        view_entity_type=view_entity_type,
        update=update, hosturi=hosturi
        ).copy()
    d.update(
        { '@id':            layout.COLL_BASE_VIEW_REF%{'id': view_id}
        , '@type':          ["annal:View"]
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
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

default_view_fields_list = (
    [ { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/Entity_id"
      # , ANNAL.CURIE.property_uri:       ANNAL.CURIE.id
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:0,6"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/Entity_type"
      # , ANNAL.CURIE.property_uri:       ANNAL.CURIE.type_id
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:6,6"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/Entity_label"
      # , ANNAL.CURIE.property_uri:       RDFS.CURIE.label
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/Entity_comment"
      # , ANNAL.CURIE.property_uri:       RDFS.CURIE.comment
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    ])

view_view_fields_list = (
    [
      { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+'/View_id'
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.id
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:0,6"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/View_label"
      , ANNAL.CURIE.property_uri:       RDFS.CURIE.label
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/View_comment"
      , ANNAL.CURIE.property_uri:       RDFS.CURIE.comment
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/View_entity_type"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.view_entity_type
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/View_edit_view"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.open_view
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:0,6"
      }
    , { ANNAL.CURIE.field_id:           layout.FIELD_TYPEID+"/View_fields"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.view_fields
      , ANNAL.CURIE.field_placement:    "small:0,12"
      }
    ])

# Field list within a view_fields field of a view display
# (this is confusingly, but unavoidably, self-referential)
group_field_list = (
    [ { ANNAL.CURIE.field_id:           "_field/View_field_sel"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.field_id
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:0,4"
      }
    , { ANNAL.CURIE.field_id:           "_field/View_field_property"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.property_uri
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:4,4"
      }
    , { ANNAL.CURIE.field_id:           "_field/View_field_placement"
      , ANNAL.CURIE.property_uri:       ANNAL.CURIE.field_placement
      , ANNAL.CURIE.field_placement:    "small:0,12;medium:8,4"
      }
    ])

def view_view_context_data(
        coll_id="testcoll", view_id="", orig_id=None,
        action=None, 
        view_uri=None,
        view_label=None,
        view_descr=None,
        view_entity_type="annal:Default_type",
        view_edit_view=True,
        view_fields=None, 
        add_field=None, remove_field=None, move_up=None, move_down=None,
        field_choices=None,
        update="RecordView",
        continuation_url=None
    ):
    if view_label is None:
        #@@TODO: use same format for both; change form data too
        if view_id:
            view_label = "%s %s/%s"%(update, coll_id, view_id)
        else:
            view_label = "%s data ... (%s/)"%(update, coll_id)
    # Target record fields listed in the view description
    if view_fields is None:
        view_fields = default_view_fields_list
    if continuation_url is None:
        continuation_url = entitydata_list_type_url(coll_id, layout.VIEW_TYPEID)
    view_heading = "View definition"
    view_title   = (
        "%s - %s - Collection %s"%(view_label, view_heading, coll_id) if view_label
        else
        "%s - Collection %s"%(view_heading, coll_id)
        )
    view_fields = copy.deepcopy(view_fields) # Prevents testing Heisenbugs
    bound_view_fields = get_bound_field("View_fields", view_fields)
    if field_choices is not None:
        # Add field choices to field definitions...
        bound_view_fields['description']['group_field_list'] = group_field_list
        group_field_descs = (
            [ get_field_description(f[ANNAL.CURIE.field_id]) 
              for f in group_field_list 
            ])
        fcs = OrderedDict()
        for fid in field_choices:
            fref      = layout.FIELD_TYPEID + "/" + fid
            fdesc     = get_field_description(fid)
            fc        = FieldChoice(fref, 
                label=fdesc['field_label'],
                link=TestBasePath+"/c/"+coll_id+"/d/"+fref+"/"
                )
            fcs[fref] = fc
        group_field_descs[0]['field_choices'] = fcs
        bound_view_fields['description']['group_field_descs'] = group_field_descs
    context_dict = (
        { 'title':              view_title
        , 'heading':            view_heading
        , 'coll_id':            coll_id
        , 'type_id':            layout.VIEW_TYPEID
        , 'orig_id':            orig_id
        , 'view_id':            'View_view'
        , 'entity_id':          view_id or ""
        , 'orig_id':            orig_id
        , 'orig_type':          layout.VIEW_TYPEID
        , 'record_type':        "annal:View"
        , 'continuation_url':   continuation_url
        , 'fields':
          [ context_field_row(
              get_bound_field("View_id",           view_id),                # 0 (0,0)
              )
          , context_field_row(
              get_bound_field("View_label",        view_label)              # 1 (1,0)
              )
          , context_field_row(
              get_bound_field("View_comment",      view_descr)              # 2 (2,0)
              )
          , context_field_row(
              get_bound_field("View_entity_type",  view_entity_type)        # 3 (3,0)
              )
          , context_field_row(
              get_bound_field("View_edit_view",    view_edit_view)          # 4 (4,0)
              )
          , bound_view_fields  # 5 (5, 0)
          ]
        })
    if view_uri:
        context_dict['entity_uri']  = view_uri
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

def view_view_form_data(
        coll_id="testcoll", orig_coll=None,
        view_id="", orig_id=None, 
        action=None, cancel=None, 
        view_entity_type="annal:View",
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
        , 'View_entity_type':   view_entity_type
        , 'View_edit_view':     "Yes"
        , 'orig_id':            'orig_view_id'
        , 'record_type':        'annal:View'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_view")
        # View fields
        , 'View_fields__0__View_field_sel':          layout.FIELD_TYPEID+"/Entity_id"
        , 'View_fields__0__View_field_placement':    "small:0,12;medium:0,6"
        , 'View_fields__1__View_field_sel':          layout.FIELD_TYPEID+"/Entity_type"
        , 'View_fields__1__View_field_placement':    "small:0,12;medium:6,6"
        , 'View_fields__2__View_field_sel':          layout.FIELD_TYPEID+"/Entity_label"
        , 'View_fields__2__View_field_property':     "rdfs:label"
        , 'View_fields__2__View_field_placement':    "small:0,12"
        , 'View_fields__3__View_field_sel':          layout.FIELD_TYPEID+"/Entity_comment"
        , 'View_fields__3__View_field_property':     "rdfs:comment"
        , 'View_fields__3__View_field_placement':    field3_placement
        })
    if extra_field:
        # Insert extra field with supplied Id
        form_data_dict['View_fields__4__View_field_sel']       = layout.FIELD_TYPEID+"/"+extra_field
        form_data_dict['View_fields__4__View_field_placement'] = "small:0,12"
        if extra_field_uri:
            form_data_dict['View_fields__4__View_field_property'] = extra_field_uri
    if view_id is not None:
        form_data_dict['entity_id']     = view_id
    if view_id:
        form_data_dict['entity_id']     = view_id
        form_data_dict['View_label']    = '%s %s/%s'%(update, coll_id, view_id)
        form_data_dict['View_comment']  = '%s help for %s in collection %s'%(update, view_id, coll_id)
        form_data_dict['View_uri']      = TestBaseUri + "/c/%s/d/_view/%s/"%(coll_id, view_id)
        form_data_dict['orig_id']       = view_id
        form_data_dict['orig_type']     = "_view"
        form_data_dict['orig_coll']     = coll_id
    if orig_id:
        form_data_dict['orig_id']       = orig_id
    if orig_coll:
        form_data_dict['orig_coll']     = orig_coll
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
