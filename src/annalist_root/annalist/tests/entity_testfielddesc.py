"""
Record field definitions for testing.

This module contains record field definitioons that can be used in 
test context values.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os
# import urlparse

from collections                import OrderedDict

import logging
log = logging.getLogger(__name__)

from annalist.identifiers       import RDF, RDFS, ANNAL
from annalist                   import layout

from annalist.views.fields.render_placement import get_placement_classes
from annalist.views.form_utils.fieldchoice  import FieldChoice

#   -----------------------------------------------------------------------------
#
#   ----- Field definition data
#
#   -----------------------------------------------------------------------------

no_options = [ FieldChoice('', label="(no options)") ]

f_Field_id = (
    { 'field_id':               "Field_id"
    , 'field_name':             "entity_id"
    , 'field_label':            "Field Id"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_render_type':      "EntityId"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:..."
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_property_uri':     'annal:id'
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field id)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_render_type = (
    { 'field_id':               "Field_render_type"
    , 'field_name':             "Field_render_type"
    , 'field_label':            "Render type"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_render_type':      "Enum_choice"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_render_type"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         "_enum_render_type"
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field render type)"
    , 'field_default_value':    "Text"
    , 'field_choices':          []
    })

f_Field_label = (
    { 'field_id':               "Field_label"
    , 'field_name':             "Field_label"
    , 'field_label':            "Field label"
    , 'field_value_type':       "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "rdfs:label"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field label)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_help = (
    { 'field_id':               "Field_help"
    , 'field_name':             "Field_help"
    , 'field_label':            "Help"
    , 'field_value_type':       "annal:Richtext"
    , 'field_render_type':      "Markdown"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "rdfs:comment"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Field usage commentary or help text)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_property = (
    { 'field_id':               "Field_property"
    , 'field_name':             "Field_property"
    , 'field_label':            "Property URI"
    , 'field_value_type':       "annal:Identifier"
    , 'field_render_type':      "Identifier"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:property_uri"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field URI or CURIE)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_placement = (
    { 'field_id':               "Field_placement"
    , 'field_name':             "Field_placement"
    , 'field_label':            "Position/size"
    , 'field_value_type':       "annal:Placement"
    , 'field_render_type':      "Placement"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_placement"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field position and size)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_superproperty_uris = (
    { 'field_id':               'Field_superproperty_uris'
    , 'field_name':             'Field_superproperty_uris'
    , 'field_value_type':       'annal:Field_superproperty_uri'
    , 'field_label':            'Superproperty URIs'
    , 'field_render_type':      'Group_Set_Row'
    , 'field_value_mode':       'Value_direct'
    , 'field_placement':        "small:0,12"
    , 'field_choices':          no_options
    })

f_Field_value_type = (
    { 'field_id':               "Field_value_type"
    , 'field_name':             "Field_value_type"
    , 'field_label':            "Value type"
    , 'field_value_type':       "annal:Identifier"
    , 'field_render_type':      "Identifier"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_value_type"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field value type)"
    , 'field_default_value':    "annal:Text"
    , 'field_choices':          no_options
    })

f_Field_value_mode = (
    { 'field_id':               "Field_value_mode"
    , 'field_name':             "Field_value_mode"
    , 'field_label':            "Value mode"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_render_type':      "Enum_choice"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_value_mode"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         "_enum_value_mode"
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field value mode)"
    , 'field_default_value':    "Value_direct"
    , 'field_choices':          []
    })

f_Field_entity_type = (
    { 'field_id':               "Field_entity_type"
    , 'field_name':             "Field_entity_type" 
    , 'field_label':            "Entity type"
    , 'field_value_type':       "annal:Identifier"
    , 'field_render_type':      "Identifier"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_entity_type"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    # , 'field_placeholder':      "..."
    , 'field_default_value':    ""
    , 'field_choices':          []
    })

f_Field_typeref = (
    { 'field_id':               "Field_typeref"
    , 'field_name':             "Field_typeref"
    , 'field_label':            "Refer to type"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_render_type':      "Enum_optional"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_ref_type"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         "_type"
    , 'field_ref_field':        None
    , 'field_placeholder':      "(no type selected)"
    , 'field_default_value':    ""
    , 'field_choices':          []
    })

f_Field_fieldref = (
    { 'field_id':               "Field_fieldref"
    , 'field_name':             "Field_fieldref"
    , 'field_label':            "Refer to field"
    , 'field_value_type':       "annal:Identifier"
    , 'field_render_type':      "Identifier"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_ref_field"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field URI or CURIE)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_default = (
    { 'field_id':               "Field_default"
    , 'field_name':             "Field_default"
    , 'field_label':            "Default value"
    , 'field_value_type':       "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:default_value"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(field default value)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_placeholder = (
    { 'field_id':               "Field_placeholder"
    , 'field_name':             "Field_placeholder"
    , 'field_label':            "Placeholder"
    , 'field_value_type':       "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:placeholder"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(placeholder text)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_tooltip = (
    { 'field_id':               "Field_tooltip"
    , 'field_name':             "Field_tooltip"
    , 'field_label':            "Tooltip"
    , 'field_value_type':       "annal:Longtext"
    , 'field_render_type':      "Textarea"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:tooltip"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Field usage popup help text)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_fields = (
    { 'field_id':               "Field_fields"
    , 'field_name':             "Field_fields"
    , 'field_value_type':       "annal:Field_list"
    , 'field_label':            "Subfields"
    , 'field_render_type':      "Group_Seq_Row"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_fields"
    , 'field_placement':        "small:0,12"
    , 'field_choices':          no_options
    })

f_Field_repeat_label_add = (
    { 'field_id':               "Field_repeat_label_add"
    , 'field_name':             "Field_repeat_label_add"
    , 'field_label':            "Add value label"
    , 'field_value_type':       "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:repeat_label_add"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    # , 'field_placeholder':      "..."
    , 'field_default_value':    "Add"
    , 'field_choices':          no_options
    })

f_Field_repeat_label_delete = (
    { 'field_id':               "Field_repeat_label_delete"
    , 'field_name':             "Field_repeat_label_delete"
    , 'field_label':            "Remove value label"
    , 'field_value_type':       "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:repeat_label_delete"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    # , 'field_placeholder':      "..."
    , 'field_default_value':    "Remove"
    , 'field_choices':          no_options
    })

f_Field_restrict = (
    { 'field_id':               "Field_restrict"
    , 'field_name':             "Field_restrict"
    , 'field_label':            "Value restriction"
    , 'field_value_type':      "annal:Text"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_property_uri':     "annal:field_ref_restriction"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    # , 'field_placeholder':      "..."
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Field_undefined = (
    { 'field_id':               "Field_undefined"
    , 'field_name':             "Field_undefined"
    , 'field_label':            "@@undefined@@"
    , 'field_value_type':       "@@undefined@@"
    , 'field_render_type':      "@@undefined@@"
    , 'field_value_mode':       "@@undefined@@"
    , 'field_property_uri':     "@@undefined@@"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    # , 'field_placeholder':      "..."
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

fields_by_id = (
    { "Field_id":                   f_Field_id
    , "Field_render_type":          f_Field_render_type
    , "Field_label":                f_Field_label
    , "Field_help":                 f_Field_help
    , "Field_property":             f_Field_property
    , "Field_placement":            f_Field_placement
    , 'Field_superproperty_uris':   f_Field_superproperty_uris
    , "Field_value_type":           f_Field_value_type
    , "Field_value_mode":           f_Field_value_mode
    , "Field_entity_type":          f_Field_entity_type
    , "Field_typeref":              f_Field_typeref
    , "Field_fieldref":             f_Field_fieldref
    , "Field_default":              f_Field_default
    , "Field_placeholder":          f_Field_placeholder
    , "Field_tooltip":              f_Field_tooltip
    , "Field_fields":               f_Field_fields
    , "Field_repeat_label_add":     f_Field_repeat_label_add
    , "Field_repeat_label_delete":  f_Field_repeat_label_delete
    , "Field_restrict":             f_Field_restrict
    })

#   -----------------------------------------------------------------------------
#
#   Assemble and return a field definition value
#
#   -----------------------------------------------------------------------------

def zzz_get_field_description(field_id, field_val=None):
    if field_id in fields_by_id:
        field_desc = fields_by_id[field_id].copy()
    else:
        field_desc = f_Field_undefined.copy()
        field_desc["field_id"]    = "Undefined_"+field_id
        field_desc["field_name"]  = "Undefined_"+field_id
    if field_val is not None:
        field_desc["field_value"] = field_val
    field_pos  = field_desc["field_placement"]
    field_desc["field_placement"] = get_placement_classes(field_pos)
    return field_desc

def get_field_description(field_id):
    if field_id in fields_by_id:
        field_desc = fields_by_id[field_id].copy()
    else:
        field_desc = f_Field_undefined.copy()
        field_desc["field_id"]    = "Undefined_"+field_id
        field_desc["field_name"]  = "Undefined_"+field_id
    field_pos  = field_desc["field_placement"]
    field_desc["field_placement"] = get_placement_classes(field_pos)
    return field_desc

def get_bound_field(field_id, field_val=None):
    field_desc = get_field_description(field_id)
    options    = field_desc.pop('field_choices', None)  # OrderedDict
    bound_field = (
        { "field_description": field_desc
        })
    if field_val is not None:
        bound_field["field_value"] = field_val
    # if options == []:
    #     options = [ FieldChoice('', label="(no options)") ]
    #     # options = []
    if isinstance(options, OrderedDict):
        options = options.values()
    if options is not None:
        bound_field["options"] = options
    return bound_field

# End.
