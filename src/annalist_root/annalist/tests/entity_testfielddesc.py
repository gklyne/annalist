"""
Record field definitions for testing.

This module contains record field definitioons that can be used in 
test context values.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

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

# ===== Generic/default entity data =====

f_Entity_id = (
    { 'field_id':               "Entity_id"
    , 'field_name':             "entity_id"
    , 'field_label':            "Id"
    , 'field_render_type':      "EntityId"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_property_uri':     "annal:id"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(entity id)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Entity_type = (
    { 'field_id':               "Entity_type"
    , 'field_name':             "entity_type"
    , 'field_label':            "Type"
    , 'field_render_type':      "EntityTypeId"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:EntityRef"
    , 'field_property_uri':     "annal:type_id"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         "_type"
    , 'field_ref_field':        None
    , 'field_placeholder':      "(type id)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Entity_label = (
    { 'field_id':               "Entity_label"
    , 'field_name':             "Entity_label"
    , 'field_label':            "Label"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "rdfs:label"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(label)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Entity_comment = (
    { 'field_id':               "Entity_comment"
    , 'field_name':             "Entity_comment"
    , 'field_label':            "Comment"
    , 'field_render_type':      "Markdown"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:Richtext"
    , 'field_property_uri':     "rdfs:comment"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(description)"
    , 'field_default_value':    ""
    , 'field_choices':          None # no_options
    })

f_Entity_uri = (
    { 'field_id':               "Entity_uri"
    , 'field_name':             "Entity_uri"
    , 'field_label':            "Entity URI"
    , 'field_render_type':      "Identifer"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:Identifer"
    , 'field_property_uri':     "annal:uri"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(URI)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Entity_see_also_r = (
    { 'field_id':               "Entity_see_also_r"
    , 'field_name':             "Entity_see_also_r"
    , 'field_label':            "See also"
    , 'field_render_type':      "Group_Set_Row"
    , 'field_value_mode':       "Value_direct"
    , 'field_value_type':       "annal:Entity_see_also_list"
    , 'field_property_uri':     "rdfs:seeAlso"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Links to further information)"
    , 'field_default_value':    None
    , 'field_choices':          no_options
    })

f_Entity_see_also = (
    { 'field_id':               "Entity_see_also"
    , 'field_name':             "Entity_see_also"
    , 'field_label':            "Link to further information"
    , 'field_render_type':      "URILink"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Entity_see_also_list"
    , 'field_value_type':       "rdfs:Resource"
    , 'field_property_uri':     "rdfs:seeAlso"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(URL for further information)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

# ===== BibEntry data (used only for testing) =====

f_Bib_type = (
    { 'field_id':               "Bib_type"
    , 'field_name':             "Bib_type"
    , 'field_label':            "Bib_type"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:type"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_type)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_title = (
    { 'field_id':               "Bib_title"
    , 'field_name':             "Bib_title"
    , 'field_label':            "Bib_title"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:title"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_title)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_month = (
    { 'field_id':               "Bib_month"
    , 'field_name':             "Bib_month"
    , 'field_label':            "Bib_month"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:month"
    , 'field_placement':        "small:0,12;medium:0,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_month)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_year = (
    { 'field_id':               "Bib_year"
    , 'field_name':             "Bib_year"
    , 'field_label':            "Bib_year"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:year"
    , 'field_placement':        "small:0,12;medium:6,6"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_year)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_authors = (
    { 'field_id':               "Bib_authors"
    , 'field_name':             "Bib_authors"
    , 'field_label':            "Bib_authors"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:authors"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_authors)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_editors = (
    { 'field_id':               "Bib_editors"
    , 'field_name':             "Bib_editors"
    , 'field_label':            "Bib_editors"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:editors"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_editors)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_journal = (
    { 'field_id':               "Bib_journal"
    , 'field_name':             "Bib_journal"
    , 'field_label':            "Bib_journal"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:journal"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_journal)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_bookentry = (
    { 'field_id':               "Bib_bookentry"
    , 'field_name':             "Bib_bookentry"
    , 'field_label':            "Bib_bookentry"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:bookentry"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_bookentry)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_publication_details = (
    { 'field_id':               "Bib_publication_details"
    , 'field_name':             "Bib_publication_details"
    , 'field_label':            "Bib_publication_details"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:publication_details"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_publication_details)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_identifiers = (
    { 'field_id':               "Bib_identifiers"
    , 'field_name':             "Bib_identifiers"
    , 'field_label':            "Bib_identifiers"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:identifiers"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_identifiers)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_license = (
    { 'field_id':               "Bib_license"
    , 'field_name':             "Bib_license"
    , 'field_label':            "Bib_license"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:license"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_license)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

f_Bib_note = (
    { 'field_id':               "Bib_note"
    , 'field_name':             "Bib_note"
    , 'field_label':            "Bib_note"
    , 'field_render_type':      "Text"
    , 'field_value_mode':       "Value_direct"
    , 'field_entity_type':      "annal:Type"
    , 'field_value_type':       "annal:Text"
    , 'field_property_uri':     "Bib:note"
    , 'field_placement':        "small:0,12"
    , 'field_ref_type':         None
    , 'field_ref_field':        None
    , 'field_placeholder':      "(Bib_note)"
    , 'field_default_value':    ""
    , 'field_choices':          no_options
    })

# ===== Field data =====

f_Field_id = (
    { "field_id":               "Field_id"
    , "field_name":             "entity_id"
    , "field_label":            "Field Id"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_render_type = (
    { "field_id":               "Field_render_type"
    , "field_name":             "Field_render_type"
    , "field_label":            "Render type"
    , "field_render_type":      "Enum_choice"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:field_render_type"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         "_enum_render_type"
    , "field_ref_field":        None
    , "field_placeholder":      "(field render type)"
    , "field_default_value":    "Text"
    , "field_choices":          []
    })

f_Field_label = (
    { "field_id":               "Field_label"
    , "field_name":             "Field_label"
    , "field_label":            "Field label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "rdfs:label"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field label)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_help = (
    { "field_id":               "Field_help"
    , "field_name":             "Field_help"
    , "field_label":            "Help"
    , "field_render_type":      "Markdown"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Richtext"
    , "field_property_uri":     "rdfs:comment"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Field usage commentary or help text)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_property = (
    { "field_id":               "Field_property"
    , "field_name":             "Field_property"
    , "field_label":            "Property URI"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:property_uri"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field URI or CURIE)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_placement = (
    { "field_id":               "Field_placement"
    , "field_name":             "Field_placement"
    , "field_label":            "Position/size"
    , "field_render_type":      "Placement"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Placement"
    , "field_property_uri":     "annal:field_placement"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field position and size)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_sel = (
    { "field_id":               "Field_sel"
    , "field_name":             "entity_id"
    , "field_label":            "Field sel"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_superproperty_uris = (
    { "field_id":               "Field_superproperty_uris"
    , "field_name":             "Field_superproperty_uris"
    , "field_label":            "Superproperty URIs"
    , "field_render_type":      "Group_Set_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Field_superproperty_uri"
    , "field_property_uri":     "annal:superproperty_uri"
    , "field_placement":        "small:0,12"
    , "field_choices":          no_options
    })

f_Field_value_type = (
    { "field_id":               "Field_value_type"
    , "field_name":             "Field_value_type"
    , "field_label":            "Value type"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:field_value_type"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field value type)"
    , "field_default_value":    "annal:Text"
    , "field_choices":          no_options
    })

f_Field_value_mode = (
    { "field_id":               "Field_value_mode"
    , "field_name":             "Field_value_mode"
    , "field_label":            "Value mode"
    , "field_render_type":      "Enum_choice"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:field_value_mode"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         "_enum_value_mode"
    , "field_ref_field":        None
    , "field_placeholder":      "(field value mode)"
    , "field_default_value":    "Value_direct"
    , "field_choices":          []
    })

f_Field_entity_type = (
    { "field_id":               "Field_entity_type"
    , "field_name":             "Field_entity_type" 
    , "field_label":            "Entity type"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:field_entity_type"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_default_value":    ""
    , "field_choices":          []
    })

f_Field_typeref = (
    { "field_id":               "Field_typeref"
    , "field_name":             "Field_typeref"
    , "field_label":            "Refer to type"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:field_ref_type"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         "_type"
    , "field_ref_field":        None
    , "field_placeholder":      "(no type selected)"
    , "field_default_value":    ""
    , "field_choices":          []
    })

f_Field_fieldref = (
    { "field_id":               "Field_fieldref"
    , "field_name":             "Field_fieldref"
    , "field_label":            "Refer to field"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:field_ref_field"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field URI or CURIE)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_default = (
    { "field_id":               "Field_default"
    , "field_name":             "Field_default"
    , "field_label":            "Default value"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "annal:default_value"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field default value)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_placeholder = (
    { "field_id":               "Field_placeholder"
    , "field_name":             "Field_placeholder"
    , "field_label":            "Placeholder"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "annal:placeholder"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(placeholder text)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_tooltip = (
    { "field_id":               "Field_tooltip"
    , "field_name":             "Field_tooltip"
    , "field_label":            "Tooltip"
    , "field_render_type":      "Textarea"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Longtext"
    , "field_property_uri":     "annal:tooltip"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Field usage popup help text)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_fields = (
    { "field_id":               "Field_fields"
    , "field_name":             "Field_fields"
    , "field_label":            "Subfields"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Field_list"
    , "field_property_uri":     "annal:field_fields"
    , "field_placement":        "small:0,12"
    , "field_choices":          no_options
    })

f_Field_repeat_label_add = (
    { "field_id":               "Field_repeat_label_add"
    , "field_name":             "Field_repeat_label_add"
    , "field_label":            "Add value label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "annal:repeat_label_add"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_default_value":    "Add"
    , "field_choices":          no_options
    })

f_Field_repeat_label_delete = (
    { "field_id":               "Field_repeat_label_delete"
    , "field_name":             "Field_repeat_label_delete"
    , "field_label":            "Remove value label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "annal:repeat_label_delete"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_default_value":    "Remove"
    , "field_choices":          no_options
    })

f_Field_restrict = (
    { "field_id":               "Field_restrict"
    , "field_name":             "Field_restrict"
    , "field_label":            "Value restriction"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":      "annal:Text"
    , "field_property_uri":     "annal:field_ref_restriction"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Field_undefined = (
    { "field_id":               "Field_undefined"
    , "field_name":             "Field_undefined"
    , "field_label":            "@@undefined@@"
    , "field_render_type":      "@@undefined@@"
    , "field_value_mode":       "@@undefined@@"
    , "field_entity_type":      "annal:Field"
    , "field_value_type":       "@@undefined@@"
    , "field_property_uri":     "@@undefined@@"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

# ===== List data =====

f_List_id = (
    { "field_id":               "List_id"
    , "field_name":             "entity_id"
    , "field_label":            "List Id"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(list id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_List_type = (
    { "field_id":               "List_type"
    , "field_name":             "List_type"
    , "field_label":            "List display type"
    , "field_render_type":      "Enum_choice"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:List_type"
    , "field_property_uri":     "annal:display_type"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         "_enum_list_type"
    , "field_ref_field":        None
    , "field_placeholder":      "(list type)"
    , "field_default_value":    "List"
    , "field_choices":          no_options
    })

f_List_label = (
    { "field_id":               "List_label"
    , "field_name":             "List_label"
    , "field_label":            "Label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "rdfs:label"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(list label)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_List_comment = (
    { "field_id":               "List_comment"
    , "field_name":             "List_comment"
    , "field_value_type":       "annal:Richtext"
    , "field_render_type":      "Markdown"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:Richtext"
    , "field_label":            "Help"
    , "field_property_uri":     "rdfs:comment"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(description of list view)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_List_default_type = (
    { "field_id":               "List_default_type"
    , "field_name":             "List_default_type"
    , "field_label":            "Default type"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:Type"
    , "field_property_uri":     "annal:default_type"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         "_type"
    , "field_ref_field":        None
    , "field_placeholder":      "(default entity type)"
    , "field_default_value":    "Default_type"
    , "field_choices":          no_options
    })

f_List_default_view = (
    { "field_id":               "List_default_view"
    , "field_name":             "List_default_view"
    , "field_label":            "Default view"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:View"
    , "field_property_uri":     "annal:default_view"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         "_view"
    , "field_ref_field":        None
    , "field_placeholder":      "(view id)"
    , "field_default_value":    "Default_view"
    , "field_choices":          no_options
    })

f_List_entity_selector = (
    { "field_id":               "List_entity_selector"
    , "field_name":             "List_entity_selector"
    , "field_label":            "Selector"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "annal:list_entity_selector"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(entity selector; e.g. 'ALL', '<type> in [@type]', '[<field>]==<value>', etc.)"
    , "field_default_value":    "ALL"
    , "field_choices":          no_options
    })

f_List_entity_type = (
    { "field_id":               "List_entity_type"
    , "field_name":             "List_entity_type"
    , "field_label":            "List entity type"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:list_entity_type"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(entity type URI/CURIE displayed by list)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_List_fields = (
    { "field_id":               "List_fields"
    , "field_name":             "List_fields"
    , "field_label":            "Fields"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:List"
    , "field_value_type":       "annal:List_field"
    , "field_property_uri":     "annal:list_fields"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(list field description)"
    , "field_default_value":    None
    , "field_choices":          no_options
    })

# ===== Type data =====

f_Type_id = (
    { "field_id":               "Type_id"
    , "field_name":             "entity_id"
    , "field_label":            "Type Id"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(type id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Type_label = (
    { "field_id":               "Type_label"
    , "field_name":             "Type_label"
    , "field_label":            "Label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "rdfs:label"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(label)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Type_comment = (
    { "field_id":               "Type_comment"
    , "field_name":             "Type_comment"
    , "field_label":            "Comment"
    , "field_render_type":      "Markdown"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:Richtext"
    , "field_property_uri":     "rdfs:comment"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(type description)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Type_uri = (
    { "field_id":               "Type_uri"
    , "field_name":             "Type_uri"
    , "field_label":            "Type URI"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:uri"
    , "field_placement":        "small:0,12" #@@@ "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Type URI or CURIE)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Type_supertype_uris = (
    { "field_id":               "Type_supertype_uris"
    , "field_name":             "Type_supertype_uris"
    , "field_label":            "Supertype URIs"
    , "field_render_type":      "Group_Set_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:Type_supertype_uri"
    , "field_property_uri":     "annal:supertype_uri"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Supertype URIs or CURIEs)"
    , "field_default_value":    None
    , "field_choices":          no_options
    })

f_Type_view = (
    { "field_id":               "Type_view"
    , "field_name":             "Type_view"
    , "field_label":            "Default view"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:View"
    , "field_property_uri":     "annal:type_view"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         "_view"
    , "field_ref_field":        None
    , "field_placeholder":      "(view id)"
    , "field_default_value":    "_view/Default_view"
    , "field_choices":          []
    })

f_Type_list = (
    { "field_id":               "Type_list"
    , "field_name":             "Type_list"
    , "field_label":            "Default list"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:List"
    , "field_property_uri":     "annal:type_list"
    , "field_placement":        "small:0,12;medium:6,6"
    , "field_ref_type":         "_list"
    , "field_ref_field":        None
    , "field_placeholder":      "(list id)"
    , "field_default_value":    "_list/Default_list"
    , "field_choices":          []
    })

f_Type_aliases = (
    { "field_id":               "Type_aliases"
    , "field_name":             "Type_aliases"
    , "field_label":            "Field aliases"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Type"
    , "field_value_type":       "annal:Type_alias"
    , "field_property_uri":     "annal:field_aliases"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field aliases)"
    , "field_default_value":    None
    , "field_choices":          no_options
    })

# ===== View data =====

f_View_id = (
    { "field_id":               "View_id"
    , "field_name":             "entity_id"
    , "field_label":            "View Id"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(view id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_View_label = (
    { "field_id":               "View_label"
    , "field_name":             "View_label"
    , "field_label":            "Label"
    , "field_render_type":      "Text"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:Text"
    , "field_property_uri":     "rdfs:label"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(view label)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_View_comment = (
    { "field_id":               "View_comment"
    , "field_name":             "View_comment"
    , "field_label":            "Help"
    , "field_render_type":      "Markdown"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:Richtext"
    , "field_property_uri":     "rdfs:comment"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(description of record view)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_View_entity_type = (
    { "field_id":               "View_entity_type"
    , "field_name":             "View_entity_type"
    , "field_label":            "View entity type"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:view_entity_type"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Entity type URI/CURIE displayed by view)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_View_edit_view = (
    { "field_id":               "View_edit_view"
    , "field_name":             "View_edit_view"
    , "field_label":            "Editable view?"
    , "field_render_type":      "CheckBox"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:Boolean"
    , "field_property_uri":     "annal:open_view"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(edit view from edit entity form)"
    , "field_default_value":    True
    , "field_choices":          no_options
    })

f_View_fields = (
    { "field_id":               "View_fields"
    , "field_name":             "View_fields"
    , "field_label":            "Fields"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View"
    , "field_value_type":       "annal:View_field"
    , "field_property_uri":     "annal:view_fields"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(repeat field description)"
    , "field_default_value":    None
    , "field_choices":          no_options
    })

f_View_field_sel = (
    { "field_id":               "View_field_sel"
    , "field_name":             "View_field_sel"
    , "field_label":            "Field ref"
    , "field_render_type":      "Enum_optional"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View_field"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:field_id"
    , "field_placement":        "small:0,12;medium:0,4"
    , "field_ref_type":         "_field"
    , "field_ref_field":        None
    , "field_placeholder":      "(field reference)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_View_field_property = (
    { "field_id":               "View_field_property"
    , "field_name":             "View_field_property"
    , "field_label":            "Property URI"
    , "field_render_type":      "Identifier"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View_field"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:property_uri"
    , "field_placement":        "small:0,12;medium:4,4"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field URI or CURIE)"
    , "field_default_value":    ""
    , "field_choices":          None
    })

f_View_field_placement = (
    { "field_id":               "View_field_placement"
    , "field_name":             "View_field_placement"
    , "field_label":            "Position/size"
    , "field_render_type":      "Placement"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:View_field"
    , "field_value_type":       "annal:Placement"
    , "field_property_uri":     "annal:field_placement"
    , "field_placement":        "small:0,12;medium:8,4"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(field position and size)"
    , "field_default_value":    ""
    , "field_choices":          None
    })

# ===== Namespace vocabulary data =====

f_Vocab_id = (
    { "field_id":               "Vocab_id"
    , "field_name":             "entity_id"
    , "field_label":            "Prefix"
    , "field_render_type":      "EntityId"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Vocabulary"
    , "field_value_type":       "annal:EntityRef"
    , "field_property_uri":     "annal:id"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(vocabulary id)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

f_Vocab_uri = (
    { "field_id":               "Vocab_uri"
    , "field_name":             "Vocab_uri"
    , "field_label":            "Vocabulary URI"
    , "field_render_type":      "URILink"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "annal:Vocabulary"
    , "field_value_type":       "annal:Identifier"
    , "field_property_uri":     "annal:uri"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(Vocabulary namespace URI)"
    , "field_default_value":    ""
    , "field_choices":          no_options
    })

# ===== Test case fields =====

f_Test_repeat_field = (
    { "field_id":               "Test_repeat_field"
    , "field_name":             "Test_repeat_field"
    , "field_label":            "Test repeat field label"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    # , "field_entity_type":      "test:img_type"
    , "field_value_type":       "annal:Field_group"
    , "field_property_uri":     "test:repeat_fields"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(test repeat field)"
    , "group_id":               "Test_repeat_field"
    , "group_label":            "Test repeat field label"
    , "group_add_label":        "Add Test_repeat_field"
    , "group_delete_label":     "Remove Test_repeat_field"
    , "group_field_list":       [ { "annal:field_id":   "Entity_comment" } ]
    })

f_Test_refimg_field = (
    { "field_id":               "Test_refimg_field"
    , "field_name":             "Test_refimg_field"
    , "field_label":            "Image reference"
    , "field_render_type":      "RefMultifield"
    , "field_value_mode":       "Value_entity"
    , "field_entity_type":      "test:img_type"
    , "field_value_type":       "annal:Field_group"
    , "field_property_uri":     "test:ref_image"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         "img_type"
    , "field_ref_field":        None
    , "field_placeholder":      "(ref image field)"
    , "group_id":               "Test_refimg_field"
    , "group_label":            "Image reference"
    , "group_add_label":        "Add Test_refimg_field"
    , "group_delete_label":     "Remove Test_refimg_field"
    , "group_field_list":       [ { "annal:field_id":   "Test_comment" }
                                , { "annal:field_id":   "Test_image" }
                                ]
    })

f_Test_rptref_field = (
    { "field_id":               "Test_rptref_field"
    , "field_name":             "Test_rptref_field"
    , "field_label":            "Repeat image reference"
    , "field_render_type":      "Group_Seq_Row"
    , "field_value_mode":       "Value_direct"
    # , "field_entity_type":      "test:img_type"
    , "field_value_type":       "annal:Field_group"
    , "field_property_uri":     "test:rpt_image"
    , "field_placement":        "small:0,12"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(repeat image field)"
    , "group_id":               "Test_rptref_field"
    , "group_label":            "Repeat image reference"
    , "group_add_label":        "Add Test_rptref_field"
    , "group_delete_label":     "Remove Test_rptref_field"
    , "group_field_list":       [ { "annal:field_id":   "Test_refimg_field" } ]
    })

f_Test_comment = (
    { "field_id":               "Test_comment"
    , "field_name":             "Test_comment"
    , "field_label":            "View comment field"
    , "field_render_type":      "Markdown"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "test:img_type"
    , "field_value_type":       "annal:Richtext"
    , "field_property_uri":     "rdfs:comment"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(view comment field)"
    , "field_default_value":    None
    , "field_choices":          None
    })

f_Test_image = (
    { "field_id":               "Test_image"
    , "field_name":             "Test_image"
    , "field_label":            "View image field"
    , "field_render_type":      "RefImage"
    , "field_value_mode":       "Value_direct"
    , "field_entity_type":      "test:img_type"
    , "field_value_type":       "annal:Image"
    , "field_property_uri":     "test:image"
    , "field_placement":        "small:0,12;medium:0,6"
    , "field_ref_type":         None
    , "field_ref_field":        None
    , "field_placeholder":      "(view image field)"
    , "field_default_value":    None
    , "field_choices":          None
    })

# ===== Lookup table =====

fields_by_id = (
    { '_sentinel_not_used':         None
    , "Entity_id":                  f_Entity_id
    , "Entity_type":                f_Entity_type
    , "Entity_label":               f_Entity_label
    , "Entity_comment":             f_Entity_comment
    , "Entity_uri":                 f_Entity_uri
    , "Entity_see_also_r":          f_Entity_see_also_r
    , "Entity_see_also":            f_Entity_see_also
    , "Bib_type":                   f_Bib_type
    , "Bib_title":                  f_Bib_title
    , "Bib_month":                  f_Bib_month
    , "Bib_year":                   f_Bib_year
    , "Bib_authors":                f_Bib_authors
    , "Bib_editors":                f_Bib_editors
    , "Bib_journal":                f_Bib_journal
    , "Bib_bookentry":              f_Bib_bookentry
    , "Bib_publication_details":    f_Bib_publication_details
    , "Bib_identifiers":            f_Bib_identifiers
    , "Bib_license":                f_Bib_license
    , "Bib_note":                   f_Bib_note
    , "Field_id":                   f_Field_id
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
    , "List_id":                    f_List_id
    , "List_type":                  f_List_type
    , "List_label":                 f_List_label
    , "List_comment":               f_List_comment
    , "List_default_type":          f_List_default_type
    , "List_default_view":          f_List_default_view
    , "List_entity_selector":       f_List_entity_selector
    , "List_entity_type":           f_List_entity_type
    , "List_fields":                f_List_fields
    , "Type_id":                    f_Type_id
    , "Type_label":                 f_Type_label
    , "Type_comment":               f_Type_comment
    , "Type_uri":                   f_Type_uri
    , "Type_supertype_uris":        f_Type_supertype_uris
    , "Type_view":                  f_Type_view
    , "Type_list":                  f_Type_list
    , "Type_aliases":               f_Type_aliases
    , "View_id":                    f_View_id
    , "View_label":                 f_View_label
    , "View_comment":               f_View_comment
    , "View_entity_type":           f_View_entity_type
    , "View_edit_view":             f_View_edit_view
    , "View_fields":                f_View_fields
    , "View_field_sel":             f_View_field_sel
    , "View_field_property":        f_View_field_property
    , "View_field_placement":       f_View_field_placement
    , "Vocab_id":                   f_Vocab_id
    , "Vocab_uri":                  f_Vocab_uri
    , "Test_repeat_field":          f_Test_repeat_field
    , "Test_refimg_field":          f_Test_refimg_field
    , "Test_rptref_field":          f_Test_rptref_field
    , "Test_comment":               f_Test_comment
    , "Test_image":                 f_Test_image
    })

#   -----------------------------------------------------------------------------
#
#   Assemble and return a field definition value
#
#   -----------------------------------------------------------------------------

def get_field_description(field_id, placement=None, name=None, prop_uri=None):
    """
    Returns a `FieldDescription` equivalent dictionary for a supplied field id.
    """
    field_id = field_id.split("/")[-1]
    if field_id in fields_by_id:
        field_desc = fields_by_id[field_id].copy()
    else:
        field_desc = f_Field_undefined.copy()
        field_desc["field_id"]   = "Undefined:"+field_id
        field_desc["field_name"] = "Undefined:"+field_id
    field_pos  = placement or field_desc["field_placement"]
    field_desc["field_placement"]    = get_placement_classes(field_pos)
    field_desc["field_name"]         = name or field_desc["field_name"]
    field_desc["field_property_uri"] = prop_uri or field_desc["field_property_uri"]
    if "group_field_list" in field_desc:
        # Generate "group_field_descs" entry
        group_field_descs = []
        for f in field_desc["group_field_list"]:
            fd = get_field_description(f[ANNAL.CURIE.field_id])
            group_field_descs.append(fd)
        field_desc["group_field_descs"] = group_field_descs
    return field_desc

def get_bound_field(field_id, 
    field_val=None, options=None, placement=None, name=None, prop_uri=None,
    group_add_label=None, group_delete_label=None,
    ):
    """
    Returns a `bound_field` equivalent for a supplied field id and value.
    """
    field_desc  = get_field_description(field_id, 
        placement=placement, name=name, prop_uri=prop_uri
        )
    if group_add_label is not None:
        field_desc["group_add_label"] = group_add_label
    if group_delete_label is not None:
        field_desc["group_delete_label"] = group_delete_label
    f_options   = field_desc.pop('field_choices', None)  # OrderedDict
    options     = options if options is not None else f_options
    bound_field = (
        { "description": field_desc
        })
    if field_val is not None:
        bound_field["field_value"] = field_val
    if isinstance(options, OrderedDict):
        options = list(options.values())
    if options is not None:
        bound_field["options"] = options
    return bound_field

# End.
