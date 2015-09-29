"""
This module contains definitions intended to reflect the site-wide data
used by all Annalist installations.

Test cases should use values returned by this module so that additions to 
the site data can be updated here, in just one place.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import urlparse

import logging
log = logging.getLogger(__name__)

from annalist.util                          import valid_id, split_type_entity_id

from annalist.views.form_utils.fieldchoice  import FieldChoice

from entity_testentitydata                  import entity_url

#   -----------------------------------------------------------------------------
#
#   ----- Field choice generation support functions
#
#   -----------------------------------------------------------------------------

# Convert list of ids and labvels into list of field choices
def make_field_choices(options):
    return [ FieldChoice(v, v, l) for v,l in options ]

def no_selection(label):
    return [ FieldChoice("", "", label) ]

def id_from_field_choice(fc):
    type_id, entity_id = split_type_entity_id(fc.id)
    return entity_id

def add_link_to_field_choice(fc, coll_id, default_type_id=None):
    type_id, entity_id = split_type_entity_id(fc.id, default_type_id=default_type_id)
    return fc.add_link(entity_url(coll_id, type_id, entity_id))

#   -----------------------------------------------------------------------------
#
#   ----- Site-wide entities defined
#
#   -----------------------------------------------------------------------------

#   ----- Types -----

site_types = (
    [ FieldChoice("_type/_initial_values")
    , FieldChoice("_type/_field",                     label="View field"                  )
    , FieldChoice("_type/_group",                     label="Field group"                 )
    , FieldChoice("_type/_list",                      label="List"                        )
    , FieldChoice("_type/_type",                      label="Type"                        )
    , FieldChoice("_type/_user",                      label="User permissions"                        )
    , FieldChoice("_type/_view",                      label="View"                        )
    , FieldChoice("_type/BibEntry_type",              label="Bibliographic record"        )
    , FieldChoice("_type/Default_type",               label="Default record"              )
    , FieldChoice("_type/Enum_bib_type",              label="Bibliographic entry type"    )
    , FieldChoice("_type/Enum_list_type",             label="List display type"           )
    , FieldChoice("_type/Enum_render_type",           label="Field render type"           )
    , FieldChoice("_type/Enum_value_mode",            label="Field value mode"            )
    ])

def get_site_types_sorted():
    return site_types[1:]

def get_site_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_type") 
          for fc in get_site_types_sorted() 
        ])

def get_site_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_types_sorted() )  )

#   ----- Lists -----

site_lists = (
    [ FieldChoice("_list/_initial_values")
    , FieldChoice("_list/BibEntry_list",              label="List bibliographic entries")
    , FieldChoice("_list/Default_list",               label="List entities")
    , FieldChoice("_list/Default_list_all",           label="List entities with type information")
    , FieldChoice("_list/Field_group_list",           label="List field groups")
    , FieldChoice("_list/Field_list",                 label="List fields")
    , FieldChoice("_list/List_list",                  label="List lists")
    , FieldChoice("_list/Type_list",                  label="List types")
    , FieldChoice("_list/User_list",                  label="User permissions")
    , FieldChoice("_list/View_list",                  label="List views")
    ])

def get_site_lists_sorted():
    return site_lists[1:]

def get_site_lists_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_list")
          for fc in get_site_lists_sorted() 
        ])

def get_site_lists():
    return set( ( id_from_field_choice(fc) for fc in get_site_lists_sorted() )  )

#   ----- List types -----

site_list_types = (
    [ FieldChoice("Enum_list_type/_initial_values")
    , FieldChoice("Enum_list_type/Grid",                       label="Grid display")
    , FieldChoice("Enum_list_type/List",                       label="List display")
    ])

def get_site_list_types_sorted():
    return site_list_types[1:]

def get_site_list_types():
    return set( ( fc.id for fc in get_site_list_types_sorted() )  )

#   ----- Views -----

site_views = (
    [ FieldChoice("_view/_initial_values")
    , FieldChoice("_view/BibEntry_view",              label="Bibliographic metadata"  )
    , FieldChoice("_view/Default_view",               label="Default record view"     )
    , FieldChoice("_view/Field_group_view",           label="Field group view"        )
    , FieldChoice("_view/Field_view",                 label="Field description view"  )
    , FieldChoice("_view/List_view",                  label="List description view"   )
    , FieldChoice("_view/Type_view",                  label="Type description view"   )
    , FieldChoice("_view/User_view",                  label="User permissions view"   )
    , FieldChoice("_view/View_view",                  label="View description view"   )
    ])

def get_site_views_sorted():
    return site_views[1:]

def get_site_views_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_view") 
          for fc in get_site_views_sorted() 
        ])

def get_site_views():
    return set( ( id_from_field_choice(fc) for fc in get_site_views_sorted() )  )

#   ----- Field groups -----

site_field_groups = (
    [ FieldChoice("_group/_initial_values")
    , FieldChoice("_group/Bib_book_group",             label="BibEntry book fields"       )
    , FieldChoice("_group/Bib_identifier_group",       label="BibEntry identifier fields" )
    , FieldChoice("_group/Bib_journal_group",          label="BibEntry journal fields"    )
    , FieldChoice("_group/Bib_license_group",          label="BibEntry license fields"    )
    , FieldChoice("_group/Bib_person_group",           label="BibEntry person fields"     )
    , FieldChoice("_group/Bib_publication_group",      label="BibEntry publication fields")
    , FieldChoice("_group/Group_field_group",          label="Group field fields"         )
    , FieldChoice("_group/List_field_group",           label="List field fields"          )
    , FieldChoice("_group/Type_alias_group",           label="Field alias fields"         )
    , FieldChoice("_group/Type_supertype_uri_group",   label="Supertype URIs"             )
    , FieldChoice("_group/View_field_group",           label="View field fields"          )
    ]) 

def get_site_field_groups_sorted():
    return site_field_groups[1:]

def get_site_field_groups_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_group") 
          for fc in get_site_field_groups_sorted()
        ])

def get_site_field_groups():
    return set( ( id_from_field_choice(fc) for fc in get_site_field_groups_sorted() ) )

#   ----- Fields -----

site_default_entity_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Entity_comment",             label="Comment"          )
    , FieldChoice("_field/Entity_id",                  label="Id"               )
    , FieldChoice("_field/Entity_label",               label="Label"            )
    , FieldChoice("_field/Entity_type",                label="Type"             )
    ])

site_bibentry_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Bib_address",                label="Address"             )
    , FieldChoice("_field/Bib_alternate",              label="Alternate name"      )
    , FieldChoice("_field/Bib_authors",                label="Author(s)"           )
    , FieldChoice("_field/Bib_bookentry",              label="Book content"        )
    , FieldChoice("_field/Bib_booktitle",              label="Book title"          )
    , FieldChoice("_field/Bib_chapter",                label="Chapter"             )
    , FieldChoice("_field/Bib_description",            label="Description"         )
    , FieldChoice("_field/Bib_edition",                label="Edition"             )
    , FieldChoice("_field/Bib_editors",                label="Editor(s)"           )
    , FieldChoice("_field/Bib_eprint",                 label="ePrint"              )
    , FieldChoice("_field/Bib_firstname",              label="First name"          )
    , FieldChoice("_field/Bib_howpublished",           label="How published"       )
    , FieldChoice("_field/Bib_id",                     label="Id"                  )
    , FieldChoice("_field/Bib_idanchor",               label="Anchor"              )
    , FieldChoice("_field/Bib_identifiers",            label="Identifiers"         )
    , FieldChoice("_field/Bib_idtype",                 label="Identifier type"     )
    , FieldChoice("_field/Bib_institution",            label="Institution"         )
    , FieldChoice("_field/Bib_journal",                label="Journal"             )
    , FieldChoice("_field/Bib_jurisdiction",           label="Jurisdiction"        )
    , FieldChoice("_field/Bib_lastname",               label="Last name"           )
    , FieldChoice("_field/Bib_license",                label="License"             )
    , FieldChoice("_field/Bib_month",                  label="Month"               )
    , FieldChoice("_field/Bib_name",                   label="Name"                )
    , FieldChoice("_field/Bib_note",                   label="Note"                )
    , FieldChoice("_field/Bib_number",                 label="Issue number"        )
    , FieldChoice("_field/Bib_organization",           label="Organization"        )
    , FieldChoice("_field/Bib_pages",                  label="Pages"               )
    , FieldChoice("_field/Bib_publication_details",    label="Publication details" )
    , FieldChoice("_field/Bib_publisher",              label="Publisher"           )
    , FieldChoice("_field/Bib_school",                 label="School"              )
    , FieldChoice("_field/Bib_shortcode",              label="Short code"          )
    , FieldChoice("_field/Bib_title",                  label="Title"               )
    , FieldChoice("_field/Bib_type",                   label="Publication type"    )
    , FieldChoice("_field/Bib_url",                    label="URL"                 )
    , FieldChoice("_field/Bib_volume",                 label="Volume"              )
    , FieldChoice("_field/Bib_year",                   label="Year"                )
    ])

site_field_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Field_comment",              label="Help"                )
    , FieldChoice("_field/Field_default",              label="Default"             )
    , FieldChoice("_field/Field_entity_type",          label="Entity type"         )
    , FieldChoice("_field/Field_fieldref",             label="Refer to field"      )
    , FieldChoice("_field/Field_groupref",             label="Field group"         )
    , FieldChoice("_field/Field_id",                   label="Id"                  )
    , FieldChoice("_field/Field_label",                label="Label"               )
    , FieldChoice("_field/Field_missing",              label="Missing"             )
    , FieldChoice("_field/Field_placeholder",          label="Placeholder"         )
    , FieldChoice("_field/Field_placement",            label="Position/size"       )
    , FieldChoice("_field/Field_property",             label="Property"            )
    , FieldChoice("_field/Field_render",               label="Field render type"   )
    , FieldChoice("_field/Field_repeat_label_add",     label="Add fields label"    )
    , FieldChoice("_field/Field_repeat_label_delete",  label="Delete fields label" )
    , FieldChoice("_field/Field_restrict",             label="Value restriction"   )
    , FieldChoice("_field/Field_type",                 label="Field value type"    )
    , FieldChoice("_field/Field_typeref",              label="Refer to type"       )
    , FieldChoice("_field/Field_value_mode",           label="Value mode"          )
    ])  

site_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Group_comment",              label="Help"                )
    , FieldChoice("_field/Group_fields",               label="Fields"              )
    , FieldChoice("_field/Group_id",                   label="Id"                  )
    , FieldChoice("_field/Group_label",                label="Label"               )
    , FieldChoice("_field/Group_target_type",          label="Record type"         )
    ])

site_group_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Group_field_placement",      label="Position/size"       )
    , FieldChoice("_field/Group_field_property",       label="Property"            )
    , FieldChoice("_field/Group_field_sel",            label="Field id"            )
    ])

site_list_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/List_comment",               label="Help"                )
    , FieldChoice("_field/List_default_type",          label="Record type"         )
    , FieldChoice("_field/List_default_view",          label="View"                )   
    , FieldChoice("_field/List_entity_selector",       label="Selector"            )
    , FieldChoice("_field/List_fields",                label="Fields"              )
    , FieldChoice("_field/List_id",                    label="Id"                  )
    , FieldChoice("_field/List_label",                 label="Label"               )
    , FieldChoice("_field/List_target_type",           label="Record type URI"     )
    , FieldChoice("_field/List_type",                  label="List display type"   )
    ])
    # , FieldChoice("List_choice",                label="List view"           )

site_list_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/List_field_placement",       label="Position/size"       )
    , FieldChoice("_field/List_field_property",        label="Property"            )
    , FieldChoice("_field/List_field_sel",             label="Field id"            )
    ])

site_type_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Type_aliases",               label="Field aliases"       )
    , FieldChoice("_field/Type_comment",               label="Comment"             )
    , FieldChoice("_field/Type_id",                    label="Id"                  )
    , FieldChoice("_field/Type_label",                 label="Label"               )
    , FieldChoice("_field/Type_list",                  label="Default list"        )
    , FieldChoice("_field/Type_supertype_uris",        label="Supertype URIs"      )
    , FieldChoice("_field/Type_uri",                   label="URI"                 )
    , FieldChoice("_field/Type_view",                  label="Default view"        )
    ])

site_type_supertype_uris_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Type_supertype_uri",         label="Supertype URI"       )
    ])

site_type_aliases_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Type_alias_source",          label="Type alias source"   )
    , FieldChoice("_field/Type_alias_target",          label="Type alias target"   )
    ])

site_user_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/User_description",           label="Description"         )
    , FieldChoice("_field/User_id",                    label="User Id"             )
    , FieldChoice("_field/User_name",                  label="User name"           )
    , FieldChoice("_field/User_permissions",           label="Permissions"         )
    , FieldChoice("_field/User_uri",                   label="URI"                 )
    ])

site_view_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/View_comment",               label="Help"                )
    , FieldChoice("_field/View_edit_view",             label="Editable view?"      )
    , FieldChoice("_field/View_fields",                label="Fields"              )
    , FieldChoice("_field/View_id",                    label="Id"                  )
    , FieldChoice("_field/View_label",                 label="Label"               )
    , FieldChoice("_field/View_target_type",           label="Record type"         )
    ])
    # , FieldChoice("View_choice",          "Choose view")

site_view_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/View_field_placement",       label="Position/size"       )
    , FieldChoice("_field/View_field_property",        label="Property"            )
    , FieldChoice("_field/View_field_sel",             label="Field id"            )
    ])

site_fields = (
    [ FieldChoice("_field/_initial_values")] +
    site_bibentry_fields[1:] +
    site_default_entity_fields[1:] +
    site_field_fields[1:] +
    site_group_fields[1:] +
    site_list_fields[1:] +
    site_type_fields[1:] +
    site_user_fields[1:] +
    site_view_fields[1:] +
    [])

def get_site_fields_sorted():
    return site_fields[1:]

def get_site_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_fields_sorted() ) )

def get_site_default_entity_fields_sorted():
    return site_default_entity_fields[1:]

def get_site_default_entity_fields_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_field") 
          for fc in get_site_default_entity_fields_sorted() 
        ])

def get_site_default_entity_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_default_entity_fields_sorted() ) )

def get_site_default_entity_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_default_entity_fields_sorted() ) )

def get_site_view_fields_sorted():
    return site_default_entity_fields[1:] + site_view_fields[1:]

def get_site_view_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_view_fields_sorted() ) )

def get_site_field_fields_sorted():
    return site_default_entity_fields[1:] + site_field_fields[1:]

def get_site_field_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_field_fields_sorted() ) )

def get_site_group_fields_sorted():
    return site_default_entity_fields[1:] + site_group_fields[1:]

def get_site_group_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_group_fields_sorted() ) )

def get_site_list_fields_sorted():
    return site_default_entity_fields[1:] + site_list_fields[1:]

def get_site_list_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_list_fields_sorted() ) )

def get_site_type_fields_sorted():
    return site_default_entity_fields[1:] + site_type_fields[1:]

def get_site_type_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_type_fields_sorted() ) )

def get_site_user_fields_sorted():
    return site_default_entity_fields[1:] + site_user_fields[1:]

def get_site_user_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_user_fields_sorted() ) )

def get_site_bibentry_fields_sorted():
    return site_bibentry_fields[1:] + site_default_entity_fields[1:]

def get_site_bibentry_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_bibentry_fields_sorted() ) )

#   ----- Field render types -----

site_field_types = (
    [ FieldChoice("Enum_render_type/_initial_values")
    , FieldChoice("Enum_render_type/CheckBox",          label="CheckBox"                     )
    , FieldChoice("Enum_render_type/EntityId",          label="Entity Id"                    )
    , FieldChoice("Enum_render_type/EntityTypeId",      label="Entity type Id"               )
    , FieldChoice("Enum_render_type/Enum",              label="Required entity ref"          )
    , FieldChoice("Enum_render_type/Enum_choice",       label="Entity choice"                )
    , FieldChoice("Enum_render_type/Enum_optional",     label="Optional entity ref"          )
    , FieldChoice("Enum_render_type/FileUpload",        label="File upload"                  )
    , FieldChoice("Enum_render_type/Identifier",        label="Identifier"                   )
    , FieldChoice("Enum_render_type/Markdown",          label="Markdown rich text"           )
    , FieldChoice("Enum_render_type/Placement",         label="Position/size"                )
    , FieldChoice("Enum_render_type/RefAudio",          label="Ref audio file"               )
    , FieldChoice("Enum_render_type/RefImage",          label="Ref image file"               )
    , FieldChoice("Enum_render_type/RefMultifield",     label="Fields of referenced entity"  )
    , FieldChoice("Enum_render_type/RepeatGroup",       label="Repeating field group"        )
    , FieldChoice("Enum_render_type/RepeatGroupRow",    label="Repeating fields as row"      )
    , FieldChoice("Enum_render_type/Slug",              label="Short name"                   )
    , FieldChoice("Enum_render_type/Text",              label="Short text"                   )
    , FieldChoice("Enum_render_type/Textarea",          label="Multiline text"               )
    , FieldChoice("Enum_render_type/TokenSet",          label="Space-separated tokens"       )
    , FieldChoice("Enum_render_type/URIImport",         label="Web import"                   )
    , FieldChoice("Enum_render_type/URILink",           label="Web link"                     )
    ])
    # , FieldChoice("Enum_render_type/Field",             label="Field Id"             ) #@@deprecated
    # , FieldChoice("Enum_render_type/List",              label="List Id"              ) #@@deprecated
    # , FieldChoice("Enum_render_type/Type",              label="Type Id"              ) #@@deprecated
    # , FieldChoice("Enum_render_type/View",              label="View Id"              ) #@@deprecated

def get_site_field_types_sorted():
    return site_field_types[1:]

def get_site_field_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "Enum_render_type") 
          for fc in get_site_field_types_sorted()
        ])

def get_site_field_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_field_types_sorted() ) )

#   ----- Field value mode types -----

site_value_modes = (
    [ FieldChoice("Enum_value_mode/_initial_values")
    , FieldChoice("Enum_value_mode/Value_direct",               label="Direct value"      )
    , FieldChoice("Enum_value_mode/Value_entity",               label="Entity reference"  )
    , FieldChoice("Enum_value_mode/Value_field",                label="Field reference"   )
    , FieldChoice("Enum_value_mode/Value_import",               label="Import from web"   )
    , FieldChoice("Enum_value_mode/Value_upload",               label="File upload"       )
    ])

def get_site_value_modes_sorted():
    return site_value_modes[1:]

def get_site_value_modes_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "Enum_value_mode") 
          for fc in get_site_value_modes_sorted()
        ])

def get_site_value_modes():
    return set( ( id_from_field_choice(fc) for fc in get_site_value_modes_sorted() )  )

# End.
