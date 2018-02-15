"""
Record field data functions to support entity data testing
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
    Placement, LayoutOptions,
    make_field_width, make_field_offset, make_field_display,
    get_placement_classes
    )

from tests import (
    TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
    )
from entity_testutils               import (
    collection_dir, 
    site_title,
    collection_entity_view_url,
    context_field_row
    )
from entity_testentitydata          import (
    entitydata_list_type_url
    )

#   -----------------------------------------------------------------------------
#
#   Directory generating functions
#
#   -----------------------------------------------------------------------------

def recordfield_dir(coll_id="testcoll", field_id="testfield"):
    return collection_dir(coll_id) + layout.COLL_FIELD_PATH%{'id': field_id} + "/"

#   -----------------------------------------------------------------------------
#
#   URI generating functions
#
#   -----------------------------------------------------------------------------

#   These use the Django `reverse` function so they correspond to
#   the declared URI patterns.

def recordfield_coll_url(site, coll_id="testcoll", field_id="testfield"):
    return urlparse.urljoin(
        site._entityurl,
        layout.SITE_COLL_PATH%{'id': coll_id} + "/" + 
        layout.COLL_FIELD_PATH%{'id': field_id} + "/"
        )

def recordfield_url(coll_id, field_id):
    """
    URI for record field description data; also view using default entity view
    """
    if not valid_id(field_id):
        return None
        # field_id = "___"
    return collection_entity_view_url(coll_id=coll_id, type_id="_field", entity_id=field_id)

def recordfield_edit_url(action=None, coll_id=None, field_id=None):
    """
    URI for record field description editing view
    """
    viewname = ( 
        'AnnalistEntityDataView'        if action == "view"   else
        'AnnalistEntityNewView'         if action == "new"    else
        'AnnalistEntityEditView'        if action == "copy"   else
        'AnnalistEntityEditView'        if action == "edit"   else
        'AnnalistRecordFieldDeleteView' if action == "delete" else
        'unknown'
        )
    kwargs = {'coll_id': coll_id, 'type_id': "_field", 'view_id': "Field_view"}
    if action != "delete":
        kwargs.update({'action': action})
    if field_id:
        if valid_id(field_id):
            kwargs.update({'entity_id': field_id})
        else:
            kwargs.update({'entity_id': "___"})
    return reverse(viewname, kwargs=kwargs)

#   -----------------------------------------------------------------------------
#
#   ----- RecordField data
#
#   -----------------------------------------------------------------------------

def recordfield_init_keys(field_uri=False):
    keys = set(
        [ 'annal:id'
        , 'annal:type_id'
        , 'annal:type'
        , 'annal:url'
        , 'rdfs:label'
        , 'rdfs:comment'
        , 'annal:property_uri'
        , 'annal:field_render_type'
        , 'annal:field_value_mode'
        , 'annal:field_value_type'
        , 'annal:tooltip'
        ])
    if field_uri:
        keys.add('annal:uri')
    return keys

def recordfield_value_keys(field_uri=False):
    return (recordfield_init_keys(field_uri=field_uri) |
        { 'annal:field_entity_type'
        , 'annal:field_value_type'
        , 'annal:field_placement'
        , 'annal:placeholder'
        , 'annal:default_value'
        })

def recordfield_load_keys(field_uri=False):
    return recordfield_value_keys(field_uri=field_uri) | {'@id', '@type', '@context'}

def recordfield_create_values(coll_id="testcoll", field_id="testfield", 
        property_uri=None, superproperty_uris=None,
        render_type="_enum_render_type/Text", 
        value_mode="_enum_value_mode/Value_direct",
        value_type="annal:Text",
        entity_type_uri=None,
        update="Field"):
    """
    Entity values used when creating a record field entity
    """
    # print("@@@@ recordfield_create_values property_uri: "+str(property_uri))
    if not property_uri:
      property_uri = "test_property:" + field_id
    d = (
        { 'rdfs:label':                 "%s %s/_field/%s"%(update, coll_id, field_id)
        , 'rdfs:comment':               "%s help for %s in collection %s"%(update, field_id, coll_id)
        , 'annal:field_render_type':    render_type
        , 'annal:field_value_mode':     value_mode
        , 'annal:field_value_type':     value_type
        , 'annal:tooltip':              "%s tooltip for %s in collection %s"%(update, field_id, coll_id)
        })
    if property_uri:
        d.update(
            { 'annal:property_uri':     property_uri
            })
    if superproperty_uris:
        d.update(
            { 'annal:superproperty_uri': [ {"@id": u} for u in superproperty_uris ]
            })
    if entity_type_uri:
        d.update(
            { 'annal:field_entity_type': entity_type_uri
            })
    return d

def recordfield_values(
        coll_id="testcoll", field_id="testfield", field_uri=None,
        property_uri=None, superproperty_uris=None,
        entity_type_uri=None,
        render_type="_enum_render_type/Text", 
        value_mode="_enum_value_mode/Value_direct",
        value_type="annal:Text",
        update="Field", hosturi=TestHostUri):
    # print("@@@@ recordfield_values property_uri: "+str(property_uri))
    d = recordfield_create_values(
        coll_id, field_id, 
        property_uri=property_uri, superproperty_uris=superproperty_uris,
        render_type=render_type, value_mode=value_mode, value_type=value_type,
        entity_type_uri=None,
        update=update
        ).copy()
    d.update(
        { 'annal:id':                   field_id
        , 'annal:type_id':              "_field"
        , 'annal:type':                 "annal:Field"
        , 'annal:url':                  recordfield_url(coll_id, field_id)
        })
    if field_uri:
        d['annal:uri'] = field_uri
    return d

def recordfield_read_values(
        coll_id="testcoll", field_id="testfield",
        property_uri=None, superproperty_uris=None,
        render_type="_enum_render_type/Text", 
        value_mode="_enum_value_mode/Value_direct",
        value_type="annal:Text",
        entity_type_uri=None,
        update="Field", hosturi=TestHostUri):
    d = recordfield_values(
        coll_id, field_id, 
        property_uri=property_uri, superproperty_uris=superproperty_uris,
        entity_type_uri=entity_type_uri,
        render_type=render_type, value_mode=value_mode, value_type=value_type,
        update=update, hosturi=hosturi
        ).copy()
    d.update(
        { '@id':            layout.COLL_BASE_FIELD_REF%{'id': field_id}
        , '@type':          ["annal:Field"]
        , '@context':       [{"@base": "../../"}, "../../coll_context.jsonld"]
        })
    return d

#   -----------------------------------------------------------------------------
#
#   ----- Entity data in recordfield view
#
#   -----------------------------------------------------------------------------

def recordfield_entity_view_context_data(
        coll_id="testcoll", field_id=None, orig_id=None, type_ids=[],
        field_label=None,
        field_value_type="annal:Text",
        field_render_type="Text",
        field_value_mode="Value_direct",
        field_property="",
        field_placement="",
        field_superproperty_uris=[],
        field_placeholder="",
        field_tooltip="",
        field_fields=[],
        field_repeat_label_add="Add",
        field_repeat_label_delete="Remove",
        field_entity_type="",
        action=None, update="Field"
    ):
    if not field_label:
        if field_id:
            field_label = "%s %s/_field/%s"%(update, coll_id, field_id)
        else:
            field_label = "%s data ... (testcoll/_field)"%(update)
    padding_placement = Placement(
        width=make_field_width(sw=0, mw=6, lw=6),
        offset=make_field_offset(so=0, mo=0, lo=0),
        display=make_field_display(sd=False, md=True, ld=True),
        field="hide-for-small-only medium-6 large-6 columns",
        label="small-4 columns",
        value="small-8 columns"
        )
    # @@TODO: re-work context structure used for testing so that field definitions present
    #         as an included dictionary, not as direct dictionary elements of bound_field.
    #         I'm not sure how extensive a re-work this would be, but there's an opportunity
    #         here to rationalize the test framework; e.g. define field desription values once
    #         and re-use, rather than duplicate values here.
    context_dict = (
        { "title":              "%s - Field definition - Collection %s"%(field_label, coll_id)
        , 'heading':            "Field definition"
        , 'coll_id':            coll_id
        , 'type_id':            "_field"
        , 'orig_id':            "orig_field_id"
        , 'fields':
          [ context_field_row(
              { 'field_id':               "Field_id"                    # 0 (0,0)
              , 'field_name':             "entity_id"
              , 'field_label':            "Field Id"
              , 'field_value_type':       "annal:EntityRef"
              , 'field_render_type':      "EntityId"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:..."
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_property_uri':     'annal:id'
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field id)"
              , 'field_default_value':    ""
              # , 'field_value':          (Supplied separately)
              , 'options':                []
              },
              { 'field_id':               "Field_render_type"           # 1 (0,1)
              , 'field_name':             "Field_render_type"
              , 'field_label':            "Render type"
              , 'field_value_type':       "annal:EntityRef"
              , 'field_render_type':      "Enum_choice"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_render_type"
              , 'field_placement':        get_placement_classes('small:0,12;medium:6,6')
              , 'field_ref_type':         "_enum_render_type"
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field render type)"
              , 'field_default_value':    "Text"
              , 'field_value':            field_render_type
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_label"                 # 2 (1,0)
              , 'field_name':             "Field_label"
              , 'field_label':            "Field label"
              , 'field_value_type':       "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "rdfs:label"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field label)"
              , 'field_default_value':    ""
              , 'field_value':            field_label
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_help"                  # 3 (2,0)
              , 'field_name':             "Field_help"
              , 'field_label':            "Help"
              , 'field_value_type':       "annal:Richtext"
              , 'field_render_type':      "Markdown"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "rdfs:comment"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(Field usage commentary or help text)"
              , 'field_default_value':    ""
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_property"              # 4 (3,0)
              , 'field_name':             "Field_property"
              , 'field_label':            "Property URI"
              , 'field_value_type':       "annal:Identifier"
              , 'field_render_type':      "Identifier"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:property_uri"
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field URI or CURIE)"
              , 'field_default_value':    ""
              , 'field_value':            field_property
              , 'options':                []
              },
              { 'field_id':               "Field_placement"             # 5 (3,1)
              , 'field_name':             "Field_placement"
              , 'field_label':            "Position/size"
              , 'field_value_type':       "annal:Placement"
              , 'field_render_type':      "Placement"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_placement"
              , 'field_placement':        get_placement_classes('small:0,12;medium:6,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field position and size)"
              , 'field_default_value':    ""
              , 'field_value':            field_placement
              , 'options':                []
              })
          , { 'field_id':             'Field_superproperty_uris'        # 6 (4,0)
            , 'field_name':           'Field_superproperty_uris'
            , 'field_value_type':     'annal:Field_superproperty_uri'
            , 'field_label':          'Superproperty URIs'
            , 'field_render_type':    'Group_Set_Row'
            , 'field_value_mode':     'Value_direct'
            , 'field_placement':      get_placement_classes('small:0,12')
            # , 'field_value':        (Supplied separately)
            , 'options':              []
            }
          , context_field_row(
              { 'field_id':               "Field_value_type"            # 7 (5,0)
              , 'field_name':             "Field_value_type"
              , 'field_label':            "Value type"
              , 'field_value_type':       "annal:Identifier"
              , 'field_render_type':      "Identifier"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_value_type"
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field value type)"
              , 'field_default_value':    "annal:Text"
              , 'field_value':            field_value_type
              , 'options':                []
              },
              { 'field_id':               "Field_value_mode"            # 8 (5,1)
              , 'field_name':             "Field_value_mode"
              , 'field_label':            "Value mode"
              , 'field_value_type':       "annal:EntityRef"
              , 'field_render_type':      "Enum_choice"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_value_mode"
              , 'field_placement':        get_placement_classes('small:0,12;medium:6,6')
              , 'field_ref_type':         "_enum_value_mode"
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field value mode)"
              , 'field_default_value':    "Value_direct"
              , 'field_value':            field_value_mode
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_entity_type"           # 9 (6,0)
              , 'field_name':             "Field_entity_type" 
              , 'field_label':            "Entity type"
              , 'field_value_type':       "annal:Identifier"
              , 'field_render_type':      "Identifier"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_entity_type"
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              # , 'field_placeholder':      "..."
              , 'field_default_value':    ""
              , 'field_value':            field_entity_type
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_typeref"               # 10 (7,0)
              , 'field_name':             "Field_typeref"
              , 'field_label':            "Refer to type"
              , 'field_value_type':       "annal:EntityRef"
              , 'field_render_type':      "Enum_optional"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_ref_type"
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_ref_type':         "_type"
              , 'field_ref_field':        None
              , 'field_placeholder':      "(no type selected)"
              , 'field_default_value':    ""
              , 'field_value':            ""
              , 'options':                []
              },
              { 'field_id':               "Field_fieldref"              # 11 (7,1)
              , 'field_name':             "Field_fieldref"
              , 'field_label':            "Refer to field"
              , 'field_value_type':       "annal:Identifier"
              , 'field_render_type':      "Identifier"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_ref_field"
              , 'field_placement':        get_placement_classes('small:0,12;medium:6,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field URI or CURIE)"
              , 'field_default_value':    ""
              , 'field_value':            ""
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_default"               # 12 (8,0)
              , 'field_name':             "Field_default"
              , 'field_label':            "Default value"
              , 'field_value_type':       "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:default_value"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(field default value)"
              , 'field_default_value':    ""
              , 'field_value':            ""
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_placeholder"           # 13 (9,0)
              , 'field_name':             "Field_placeholder"
              , 'field_label':            "Placeholder"
              , 'field_value_type':       "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:placeholder"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(placeholder text)"
              , 'field_default_value':    ""
              , 'field_value':            field_placeholder
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_tooltip"               # 14 (10,0)
              , 'field_name':             "Field_tooltip"
              , 'field_label':            "Tooltip"
              , 'field_value_type':       "annal:Longtext"
              , 'field_render_type':      "Textarea"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:tooltip"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              , 'field_placeholder':      "(Field usage popup help text)"
              , 'field_default_value':    ""
              , 'options':                []
              })
          , { 'field_id':               "Field_fields"                  # 15 (11,0)
            , 'field_name':             "Field_fields"
            , 'field_value_type':       "annal:Field_list"
            , 'field_label':            "Subfields"
            , 'field_render_type':      "Group_Seq_Row"
            , 'field_value_mode':       "Value_direct"
            , 'field_property_uri':     "annal:field_fields"
            , 'field_placement':        get_placement_classes('small:0,12')
            , 'field_value':            field_fields
            , 'options':                []
            }
          , context_field_row(
              { 'field_id':               "Field_repeat_label_add"      # 16 (12,0)
              , 'field_name':             "Field_repeat_label_add"
              , 'field_label':            "Add value label"
              , 'field_value_type':       "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:repeat_label_add"
              , 'field_placement':        get_placement_classes('small:0,12;medium:0,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              # , 'field_placeholder':      "..."
              , 'field_default_value':    "Add"
              , 'field_value':            field_repeat_label_add
              , 'options':                []
              },
              { 'field_id':               "Field_repeat_label_delete"   # 17 (12,1)
              , 'field_name':             "Field_repeat_label_delete"
              , 'field_label':            "Remove value label"
              , 'field_value_type':       "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:repeat_label_delete"
              , 'field_placement':        get_placement_classes('small:0,12;medium:6,6')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              # , 'field_placeholder':      "..."
              , 'field_default_value':    "Remove"
              , 'field_value':            field_repeat_label_delete
              , 'options':                []
              })
          , context_field_row(
              { 'field_id':               "Field_restrict"              # 18 (18,0)
              , 'field_name':             "Field_restrict"
              , 'field_label':            "Value restriction"
              , 'field_value_type':      "annal:Text"
              , 'field_render_type':      "Text"
              , 'field_value_mode':       "Value_direct"
              , 'field_property_uri':     "annal:field_ref_restriction"
              , 'field_placement':        get_placement_classes('small:0,12')
              , 'field_ref_type':         None
              , 'field_ref_field':        None
              # , 'field_placeholder':      "..."
              , 'field_default_value':    ""
              , 'field_value':            ""
              , 'options':                []
              })
          ]
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_field")
        })
    if field_id:
        context_dict['fields'][0]['row_field_descs'][0]['field_value'] = field_id
        context_dict['orig_id']     = field_id
    if orig_id:
        context_dict['orig_id']     = orig_id
    if action:  
        context_dict['action']      = action
    return context_dict

def recordfield_entity_view_form_data(
        field_id="", orig_id=None, 
        coll_id="testcoll", 
        field_label=None,
        render_type="Text", value_mode="Value_direct",
        entity_type=None, property_uri=None, value_type="annal:Text",
        field_placement="",
        action=None, cancel=None, task=None,
        update="Field"):
    # log.info("recordfield_entity_view_form_data: field_id %s"%(field_id))
    form_data_dict = (
        { 'Field_label':        '%s data ... (%s/%s)'%(update, coll_id, "_field")
        , 'Field_comment':      '%s description ... (%s/%s)'%(update, coll_id, "_field")
        , 'Field_render_type':  render_type
        , 'Field_value_mode':   value_mode
        , 'orig_id':            'orig_field_id'
        , 'continuation_url':   entitydata_list_type_url(coll_id, "_field")
        })
    if field_id is not None:
        form_data_dict['entity_id']         = field_id
    if field_id:
        field_url = recordfield_url(coll_id=coll_id, field_id=field_id)
        form_data_dict['entity_id']         = field_id
        form_data_dict['Field_label']       = '%s %s/%s/%s'%(update, coll_id, "_field", field_id)
        form_data_dict['Field_help']        = '%s help for %s in collection %s'%(update, field_id, coll_id)
        form_data_dict['Field_tooltip']     = '%s tooltip for %s in collection %s'%(update, field_id, coll_id)
        form_data_dict['Field_uri']         = field_url
        form_data_dict['Field_placement']   = field_placement
        form_data_dict['orig_id']           = field_id
        form_data_dict['orig_type']         = "_field"
    if orig_id:
        form_data_dict['orig_id']           = orig_id
    if field_label:
        form_data_dict['Field_label']       = field_label
        form_data_dict['Field_help']        = "Help for "+field_label
        form_data_dict['Field_tooltip']     = "Tooltip for "+field_label
    if entity_type:
        form_data_dict['Field_entity_type'] = entity_type
    if property_uri:
        form_data_dict['Field_property']    = property_uri
    if value_type:
        form_data_dict['Field_value_type']  = value_type
    if action:
        form_data_dict['action']            = action
    if cancel:
        form_data_dict['cancel']    = "Cancel"
    elif task:
        form_data_dict[task]        = task
    else:
        form_data_dict['save']      = 'Save'
    return form_data_dict

# End.
