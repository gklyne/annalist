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

# from annalist.util              import valid_id
# from annalist.identifiers       import RDF, RDFS, ANNAL
# from annalist                   import layout
# from annalist                   import message

from annalist.views.form_utils.fieldchoice  import FieldChoice

# from tests import (
#     TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
#     )

from entity_testentitydata      import entity_url

#   -----------------------------------------------------------------------------
#
#   ----- Site-wide entities defined
#
#   -----------------------------------------------------------------------------

#   ----- Types -----

site_types = (
    [ FieldChoice("_initial_values")
    , FieldChoice("_field",                     label="View field"                  )
    , FieldChoice("_group",                     label="Field group"                 )
    , FieldChoice("_list",                      label="List"                        )
    , FieldChoice("_type",                      label="Type"                        )
    , FieldChoice("_user",                      label="User"                        )
    , FieldChoice("_view",                      label="View"                        )
    , FieldChoice("BibEntry_type",              label="Bibliographic record"        )
    , FieldChoice("Default_type",               label="Default record"              )
    , FieldChoice("Enum_bib_type",              label="Bibliographic entry type"    )
    , FieldChoice("Enum_list_type",             label="List display type"           )
    , FieldChoice("Enum_render_type",           label="Field render type"           )
    , FieldChoice("Enum_value_mode",            label="Field value mode"            )
    ])

def get_site_types_sorted():
    return site_types[1:]

def get_site_types_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "_type", fc.id)) 
          for fc in get_site_types_sorted() 
        ])

def get_site_types():
    return set( ( fc.id for fc in get_site_types_sorted() )  )

#   ----- Lists -----

site_lists = (
    [ FieldChoice("_initial_values")
    , FieldChoice("BibEntry_list",              label="List bibliographic entries")
    , FieldChoice("Default_list",               label="List entities")
    , FieldChoice("Default_list_all",           label="List entities with type information")
    , FieldChoice("Field_group_list",           label="List field groups")
    , FieldChoice("Field_list",                 label="List fields")
    , FieldChoice("List_list",                  label="List lists")
    , FieldChoice("Type_list",                  label="List types")
    , FieldChoice("User_list",                  label="List users")
    , FieldChoice("View_list",                  label="List views")
    ])

def get_site_lists_sorted():
    return site_lists[1:]

def get_site_lists_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "_list", fc.id)) 
          for fc in get_site_lists_sorted() 
        ])

def get_site_lists():
    return set( ( fc.id for fc in get_site_lists_sorted() )  )

#   ----- List types -----

site_list_types = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Grid",                       label="Grid display")
    , FieldChoice("List",                       label="List display")
    ])

def get_site_list_types_sorted():
    return site_list_types[1:]

def get_site_list_types():
    return set( ( fc.id for fc in get_site_list_types_sorted() )  )

#   ----- Views -----

site_views = (
    [ FieldChoice("_initial_values")
    , FieldChoice("BibEntry_view",              label="Bibliographic metadata"  )
    , FieldChoice("Default_view",               label="Default record view"     )
    , FieldChoice("Field_group_view",           label="Field group view"        )
    , FieldChoice("Field_view",                 label="Field description view"  )
    , FieldChoice("List_view",                  label="List description view"   )
    , FieldChoice("Type_view",                  label="Type description view"   )
    , FieldChoice("User_view",                  label="User permissions view"   )
    , FieldChoice("View_view",                  label="View description view"   )
    ])

def get_site_views_sorted():
    return site_views[1:]

def get_site_views_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "_view", fc.id)) 
          for fc in get_site_views_sorted() 
        ])

def get_site_views():
    return set( ( fc.id for fc in get_site_views_sorted() )  )

#   ----- Field groups -----

site_field_groups = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Bib_book_group",             label="BibEntry book fields"       )
    , FieldChoice("Bib_identifier_group",       label="BibEntry identifier fields" )
    , FieldChoice("Bib_journal_group",          label="BibEntry journal fields"    )
    , FieldChoice("Bib_license_group",          label="BibEntry license fields"    )
    , FieldChoice("Bib_person_group",           label="BibEntry person fields"     )
    , FieldChoice("Bib_publication_group",      label="BibEntry publication fields")
    , FieldChoice("Group_field_group",          label="Group field fields"         )
    , FieldChoice("List_field_group",           label="List field fields"          )
    , FieldChoice("Type_alias_group",           label="Field alias fields"         )
    , FieldChoice("View_field_group",           label="View field fields"          )
    ]) 

def get_site_field_groups_sorted():
    return site_field_groups[1:]

def get_site_field_groups_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "_group", fc.id)) 
          for fc in get_site_field_groups_sorted()
        ])

def get_site_field_groups():
    return set( ( fc.id for fc in get_site_field_groups_sorted() )  )

#   ----- Fields -----

site_default_entity_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Entity_comment",             label="Comment"          )
    , FieldChoice("Entity_id",                  label="Id"               )
    , FieldChoice("Entity_label",               label="Label"            )
    , FieldChoice("Entity_type",                label="Type"             )
    ])

site_bibentry_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Bib_address",                label="Address"             )
    , FieldChoice("Bib_alternate",              label="Alternate name"      )
    , FieldChoice("Bib_authors",                label="Author(s)"           )
    , FieldChoice("Bib_bookentry",              label="Book content"        )
    , FieldChoice("Bib_booktitle",              label="Book title"          )
    , FieldChoice("Bib_chapter",                label="Chapter"             )
    , FieldChoice("Bib_description",            label="Description"         )
    , FieldChoice("Bib_edition",                label="Edition"             )
    , FieldChoice("Bib_editors",                label="Editor(s)"           )
    , FieldChoice("Bib_eprint",                 label="ePrint"              )
    , FieldChoice("Bib_firstname",              label="First name"          )
    , FieldChoice("Bib_howpublished",           label="How published"       )
    , FieldChoice("Bib_id",                     label="Id"                  )
    , FieldChoice("Bib_idanchor",               label="Anchor"              )
    , FieldChoice("Bib_identifiers",            label="Identifiers"         )
    , FieldChoice("Bib_idtype",                 label="Identifier type"     )
    , FieldChoice("Bib_institution",            label="Institution"         )
    , FieldChoice("Bib_journal",                label="Journal"             )
    , FieldChoice("Bib_jurisdiction",           label="Jurisdiction"        )
    , FieldChoice("Bib_lastname",               label="Last name"           )
    , FieldChoice("Bib_license",                label="License"             )
    , FieldChoice("Bib_month",                  label="Month"               )
    , FieldChoice("Bib_name",                   label="Name"                )
    , FieldChoice("Bib_note",                   label="Note"                )
    , FieldChoice("Bib_number",                 label="Issue number"        )
    , FieldChoice("Bib_organization",           label="Organization"        )
    , FieldChoice("Bib_pages",                  label="Pages"               )
    , FieldChoice("Bib_publication_details",    label="Publication details" )
    , FieldChoice("Bib_publisher",              label="Publisher"           )
    , FieldChoice("Bib_school",                 label="School"              )
    , FieldChoice("Bib_shortcode",              label="Short code"          )
    , FieldChoice("Bib_title",                  label="Title"               )
    , FieldChoice("Bib_type",                   label="Publication type"    )
    , FieldChoice("Bib_url",                    label="URL"                 )
    , FieldChoice("Bib_volume",                 label="Volume"              )
    , FieldChoice("Bib_year",                   label="Year"                )
    ])

site_field_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Field_comment",              label="Help"                )
    , FieldChoice("Field_default",              label="Default"             )
    , FieldChoice("Field_entity_type",          label="Entity type"         )
    , FieldChoice("Field_fieldref",             label="Refer to field"      )
    , FieldChoice("Field_groupref",             label="Field group"         )
    , FieldChoice("Field_id",                   label="Id"                  )
    , FieldChoice("Field_label",                label="Label"               )
    , FieldChoice("Field_missing",              label="Missing"             )
    , FieldChoice("Field_placeholder",          label="Placeholder"         )
    , FieldChoice("Field_placement",            label="Position/size"       )
    , FieldChoice("Field_property",             label="Property"            )
    , FieldChoice("Field_render",               label="Field render type"   )
    , FieldChoice("Field_repeat_label_add",     label="Add fields label"    )
    , FieldChoice("Field_repeat_label_delete",  label="Delete fields label" )
    , FieldChoice("Field_restrict",             label="Value restriction"   )
    , FieldChoice("Field_type",                 label="Field value type"    )
    , FieldChoice("Field_typeref",              label="Refer to type"       )
    , FieldChoice("Field_value_mode",           label="Value mode"          )
    ])  

site_group_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Group_comment",              label="Help"                )
    , FieldChoice("Group_field_placement",      label="Position/size"       )
    , FieldChoice("Group_field_property",       label="Property"            )
    , FieldChoice("Group_field_sel",            label="Field id"            )
    , FieldChoice("Group_fields",               label="Fields"              )
    , FieldChoice("Group_id",                   label="Id"                  )
    , FieldChoice("Group_label",                label="Label"               )
    , FieldChoice("Group_target_type",          label="Record type"         )
    ])

site_list_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("List_comment",               label="Help"                )
    , FieldChoice("List_default_type",          label="Record type"         )
    , FieldChoice("List_default_view",          label="View"                )   
    , FieldChoice("List_entity_selector",       label="Selector"            )
    , FieldChoice("List_field_placement",       label="Position/size"       )
    , FieldChoice("List_field_property",        label="Property"            )
    , FieldChoice("List_field_sel",             label="Field id"            )
    , FieldChoice("List_fields",                label="Fields"              )
    , FieldChoice("List_id",                    label="Id"                  )
    , FieldChoice("List_label",                 label="Label"               )
    , FieldChoice("List_target_type",           label="Record type URI"     )
    , FieldChoice("List_type",                  label="List display type"   )
    ])
    # , FieldChoice("List_choice",                label="List view"           )

site_type_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Type_alias_source",          label="Type alias source"   )
    , FieldChoice("Type_alias_target",          label="Type alias target"   )
    , FieldChoice("Type_aliases",               label="Field aliases"       )
    , FieldChoice("Type_comment",               label="Comment"             )
    , FieldChoice("Type_id",                    label="Id"                  )
    , FieldChoice("Type_label",                 label="Label"               )
    , FieldChoice("Type_list",                  label="Default list"        )
    , FieldChoice("Type_uri",                   label="URI"                 )
    , FieldChoice("Type_view",                  label="Default view"        )
    ])

site_user_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("User_description",           label="Description"         )
    , FieldChoice("User_id",                    label="User Id"             )
    , FieldChoice("User_name",                  label="User name"           )
    , FieldChoice("User_permissions",           label="Permissions"         )
    , FieldChoice("User_uri",                   label="URI"                 )
    ])

site_view_fields = (
    [ FieldChoice("_initial_values")
    , FieldChoice("View_comment",               label="Help"                )
    , FieldChoice("View_edit_view",             label="Editable view?"      )
    , FieldChoice("View_field_placement",       label="Position/size"       )
    , FieldChoice("View_field_property",        label="Property"            )
    , FieldChoice("View_field_sel",             label="Field id"            )
    , FieldChoice("View_fields",                label="Fields"              )
    , FieldChoice("View_id",                    label="Id"                  )
    , FieldChoice("View_label",                 label="Label"               )
    , FieldChoice("View_target_type",           label="Record type"         )
    ])
    # , FieldChoice("View_choice",          "Choose view")

site_fields = (
    [ FieldChoice("_initial_values")] +
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
    return set( ( fc.id for fc in get_site_fields_sorted() )  )

def get_site_default_entity_fields_sorted():
    return site_default_entity_fields[1:]

def get_site_default_entity_fields_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "_field", fc.id)) 
          for fc in get_site_default_entity_fields_sorted() 
        ])

def get_site_default_entity_fields():
    return set( ( fc.id for fc in get_site_default_entity_fields_sorted() )  )

def get_site_default_entity_fields():
    return set( ( fc.id for fc in  get_site_default_entity_fields_sorted() )  )

def get_site_view_fields_sorted():
    return site_default_entity_fields[1:] + site_view_fields[1:]

def get_site_view_fields():
    return set( ( fc.id for fc in get_site_view_fields_sorted() )  )

def get_site_field_fields_sorted():
    return site_default_entity_fields[1:] + site_field_fields[1:]

def get_site_field_fields():
    return set( ( fc.id for fc in get_site_field_fields_sorted() )  )

def get_site_group_fields_sorted():
    return site_default_entity_fields[1:] + site_group_fields[1:]

def get_site_group_fields():
    return set( ( fc.id for fc in get_site_group_fields_sorted() )  )

def get_site_list_fields_sorted():
    return site_default_entity_fields[1:] + site_list_fields[1:]

def get_site_list_fields():
    return set( ( fc.id for fc in get_site_list_fields_sorted() )  )

def get_site_type_fields_sorted():
    return site_default_entity_fields[1:] + site_type_fields[1:]

def get_site_type_fields():
    return set( ( fc.id for fc in get_site_type_fields_sorted() )  )

def get_site_user_fields_sorted():
    return site_default_entity_fields[1:] + site_user_fields[1:]

def get_site_user_fields():
    return set( ( fc.id for fc in get_site_user_fields_sorted() )  )

def get_site_bibentry_fields_sorted():
    return site_bibentry_fields[1:] + site_default_entity_fields[1:]

def get_site_bibentry_fields():
    return set( ( fc.id for fc in get_site_bibentry_fields_sorted() )  )

#   ----- Field render types -----

site_field_types = (
    [ FieldChoice("_initial_values")
    , FieldChoice("CheckBox",                   label="CheckBox"                     )
    , FieldChoice("EntityId",                   label="Entity Id"                    )
    , FieldChoice("EntityTypeId",               label="Entity type Id"               )
    , FieldChoice("Enum",                       label="Required entity ref"          )
    , FieldChoice("Enum_choice",                label="Entity choice"                )
    , FieldChoice("Enum_optional",              label="Optional entity ref"          )
    , FieldChoice("Field",                      label="Field Id"             ) #@@deprecated
    , FieldChoice("FileUpload",                 label="File upload"                  )
    , FieldChoice("Identifier",                 label="Identifier"                   )
    , FieldChoice("List",                       label="List Id"              ) #@@deprecated
    , FieldChoice("Markdown",                   label="Markdown rich text"           )
    , FieldChoice("Placement",                  label="Position/size"                )
    , FieldChoice("RefAudio",                   label="Ref audio file"               )
    , FieldChoice("RefImage",                   label="Ref image file"               )
    , FieldChoice("RefMultifield",              label="Fields of referenced entity"  )
    , FieldChoice("RepeatGroup",                label="Repeating field group"        )
    , FieldChoice("RepeatGroupRow",             label="Repeating fields as row"      )
    , FieldChoice("Slug",                       label="Short name"                   )
    , FieldChoice("Text",                       label="Short text"                   )
    , FieldChoice("Textarea",                   label="Multiline text"               )
    , FieldChoice("TokenSet",                   label="Space-separated tokens"       )
    , FieldChoice("Type",                       label="Type Id"              ) #@@deprecated
    , FieldChoice("URIImport",                  label="Web import"                   )
    , FieldChoice("URILink",                    label="Web link"                     )
    , FieldChoice("View",                       label="View Id"              ) #@@deprecated
    ])

def get_site_field_types_sorted():
    return site_field_types[1:]

def get_site_field_types_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "Enum_render_type", fc.id)) 
          for fc in get_site_field_types_sorted()
        ])

def get_site_field_types():
    return set( ( fc.id for fc in get_site_field_types_sorted() )  )

#   ----- Field value mode types -----

site_value_modes = (
    [ FieldChoice("_initial_values")
    , FieldChoice("Value_direct",               label="Direct value"      )
    , FieldChoice("Value_entity",               label="Entity reference"  )
    , FieldChoice("Value_field",                label="Field reference"   )
    , FieldChoice("Value_import",               label="Import from web"   )
    , FieldChoice("Value_upload",               label="File upload"       )
    ])

def get_site_value_modes_sorted():
    return site_value_modes[1:]

def get_site_value_modes_linked(coll_id):
    return (
        [ fc.add_link(entity_url(coll_id, "Enum_value_mode", fc.id)) 
          for fc in get_site_value_modes_sorted()
        ])

def get_site_value_modes():
    return set( ( fc.id for fc in get_site_value_modes_sorted() )  )

# End.
