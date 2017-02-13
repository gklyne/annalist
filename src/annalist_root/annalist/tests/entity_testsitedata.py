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

from annalist                               import layout
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
    , FieldChoice("_type/_coll",                      label="Collection"            )
    , FieldChoice("_type/_enum_list_type",            label="List display type"     )
    , FieldChoice("_type/_enum_render_type",          label="Field render type"     )
    , FieldChoice("_type/_enum_value_mode",           label="Field value mode"      )
    , FieldChoice("_type/_enum_value_type",           label="Field value type"      )
    , FieldChoice("_type/_field",                     label="Field"                 )
    , FieldChoice("_type/_group",                     label="Field group"           )
    , FieldChoice("_type/_list",                      label="List"                  )
    , FieldChoice("_type/_type",                      label="Type"                  )
    , FieldChoice("_type/_user",                      label="User permissions"      )
    , FieldChoice("_type/_view",                      label="View"                  )
    , FieldChoice("_type/_vocab",                     label="Vocabulary namespace"  )
    , FieldChoice("_type/Default_type",               label="Default record"        )
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

site_bib_types = (
    site_types[0:1]+
    sorted(site_types[1:] +
        [ FieldChoice("_type/BibEntry_type",              label="Bibliographic record"        )
        , FieldChoice("_type/Enum_bib_type",              label="Bibliographic entry type"    )
        ])
    )

def get_site_bib_types_sorted():
    return site_bib_types[1:]

def get_site_bib_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_type") 
          for fc in get_site_bib_types_sorted() 
        ])

def get_site_bib_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_bib_types_sorted() )  )

site_schema_types = (
    site_types[0:1]+
    sorted(site_types[1:] +
        [ FieldChoice("_type/Class",    label="Class"    )
        , FieldChoice("_type/Datatype", label="Datatype" )
        , FieldChoice("_type/Property", label="Property" )
        ])
    )

def get_site_schema_types_sorted():
    return site_schema_types[1:]

def get_site_schema_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_type") 
          for fc in get_site_schema_types_sorted() 
        ])

def get_site_schema_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_schema_types_sorted() )  )

#   ----- Lists -----

site_lists = (
    [ FieldChoice("_list/_initial_values")
    , FieldChoice("_list/Default_list",               label="List entities")
    , FieldChoice("_list/Default_list_all",           label="List entities with type information")
    , FieldChoice("_list/Enum_list_all",              label="List enumeration values and types")
    , FieldChoice("_list/Field_group_list",           label="Field groups")
    , FieldChoice("_list/Field_list",                 label="Field definitions")
    , FieldChoice("_list/List_list",                  label="List definitions")
    , FieldChoice("_list/Type_list",                  label="Entity types")
    , FieldChoice("_list/User_list",                  label="User permissions")
    , FieldChoice("_list/View_list",                  label="View definitions")
    , FieldChoice("_list/Vocab_list",                 label="Vocabulary namespaces")
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

site_bib_lists = (
    site_lists[0:1] +
    sorted(site_lists[1:] +
        [ FieldChoice("_list/BibEntry_list",              label="List bibliographic entries")
        ])
    )

def get_site_bib_lists_sorted():
    return site_bib_lists[1:]

def get_site_bib_lists_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_list") 
          for fc in get_site_bib_lists_sorted() 
        ])

def get_site_bib_lists():
    return set( ( id_from_field_choice(fc) for fc in get_site_bib_lists_sorted() )  )

site_schema_lists = (
    site_lists[0:1] +
    sorted(site_lists[1:] +
        [ FieldChoice("_list/Classes",    label="Classes")
        , FieldChoice("_list/Properties", label="Properties")
        ])
    )

def get_site_schema_lists_sorted():
    return site_schema_lists[1:]

def get_site_schema_lists_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_list") 
          for fc in get_site_schema_lists_sorted() 
        ])

def get_site_schema_lists():
    return set( ( id_from_field_choice(fc) for fc in get_site_schema_lists_sorted() )  )

#   ----- List types -----

site_list_types = (
    [ FieldChoice("_enum_list_type/_initial_values")
    , FieldChoice("_enum_list_type/Grid",   label="Grid display")
    , FieldChoice("_enum_list_type/List",   label="List display")
    ])

def get_site_list_types_sorted():
    return site_list_types[1:]

def get_site_list_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, layout.ENUM_LIST_TYPE_ID) 
          for fc in get_site_list_types_sorted() 
        ])

def get_site_list_types():
    return set( ( fc.id for fc in get_site_list_types_sorted() )  )

#   ----- Views -----

site_views = (
    [ FieldChoice("_view/_initial_values")
    , FieldChoice("_view/Collection_view",  label="Collection metadata"    )
    , FieldChoice("_view/Default_view",     label="Default record view"    )
    , FieldChoice("_view/Enum_view",        label="Enumerated value view"  )
    , FieldChoice("_view/Field_group_view", label="Field group definition" )
    , FieldChoice("_view/Field_view",       label="Field definition"       )
    , FieldChoice("_view/List_view",        label="List definition"        )
    , FieldChoice("_view/Type_view",        label="Type definition"        )
    , FieldChoice("_view/User_view",        label="User permissions"       )
    , FieldChoice("_view/View_view",        label="View definition"        )
    , FieldChoice("_view/Vocab_view",       label="Vocabulary namespace"   )
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

site_bib_views = (
    site_views[0:1] +
    sorted(site_views[1:] +
        [ FieldChoice("_view/BibEntry_view",    label="Bibliographic metadata"  )
        ])
    )

def get_site_bib_views_sorted():
    return site_bib_views[1:]

def get_site_bib_views_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_view") 
          for fc in get_site_bib_views_sorted() 
        ])

def get_site_bib_views():
    return set( ( id_from_field_choice(fc) for fc in get_site_bib_views_sorted() )  )



#   ----- Field groups -----

site_field_groups = (
    [ FieldChoice("_group/_initial_values")
    , FieldChoice("_group/Entity_see_also_r",       label="Links to further information" )
    , FieldChoice("_group/Group_field_group",       label="Group field fields"           )
    , FieldChoice("_group/List_field_group",        label="List field fields"            )
    , FieldChoice("_group/Type_alias_group",        label="Field alias fields"           )
    , FieldChoice("_group/Type_supertype_uri_r",    label="Supertype URIs"               )
    , FieldChoice("_group/View_field_group",        label="View field fields"            )
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

site_defined_entity_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Entity_comment",             label="Comment"          )
    , FieldChoice("_field/Entity_id",                  label="Id"               )
    , FieldChoice("_field/Entity_label",               label="Label"            )
    , FieldChoice("_field/Entity_see_also",            label="See also"         )
    , FieldChoice("_field/Entity_see_also_r",          label="See also"         )
    , FieldChoice("_field/Entity_type",                label="Type"             )
    ])

site_default_entity_fields = (
    [ fc 
      for fc in site_defined_entity_fields 
      if fc.id != "_field/Entity_see_also" 
    ])

site_enum_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Enum_uri",                   label="Value URI"           )
    ])

site_coll_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Coll_comment",               label="Collection metadata" )
    , FieldChoice("_field/Coll_default_list_id",       label="Default list"        )
    , FieldChoice("_field/Coll_default_view_entity",   label="Default view entity" )
    , FieldChoice("_field/Coll_default_view_id",       label="Default view"        )
    , FieldChoice("_field/Coll_default_view_type",     label="Default view type"   )
    , FieldChoice("_field/Coll_parent",                label="Parent"              )
    , FieldChoice("_field/Coll_software_version",      label="S/W version"         )
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
    , FieldChoice("_field/Field_id",                   label="Field Id"            )
    , FieldChoice("_field/Field_label",                label="Label"               )
    , FieldChoice("_field/Field_missing",              label="Missing"             )
    , FieldChoice("_field/Field_placeholder",          label="Placeholder"         )
    , FieldChoice("_field/Field_placement",            label="Position/size"       )
    , FieldChoice("_field/Field_property",             label="Property URI"        )
    , FieldChoice("_field/Field_render_type",          label="Render type"   )
    , FieldChoice("_field/Field_repeat_label_add",     label="Add value label"     )
    , FieldChoice("_field/Field_repeat_label_delete",  label="Delete value label"  )
    , FieldChoice("_field/Field_restrict",             label="Value restriction"   )
    , FieldChoice("_field/Field_typeref",              label="Refer to type"       )
    , FieldChoice("_field/Field_value_mode",           label="Value mode"          )
    , FieldChoice("_field/Field_value_type",           label="Value type"          )
    ])  

site_defined_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Group_comment",              label="Help"                )
    , FieldChoice("_field/Group_field_placement",      label="Position/size"       )
    , FieldChoice("_field/Group_field_property",       label="Property URI"        )
    , FieldChoice("_field/Group_field_sel",            label="Field id"            )
    , FieldChoice("_field/Group_fields",               label="Fields"              )
    , FieldChoice("_field/Group_id",                   label="Group Id"            )
    , FieldChoice("_field/Group_label",                label="Label"               )
    , FieldChoice("_field/Group_target_type",          label="Group entity type"   )
    ])

site_group_fields = (
    [ fc 
      for fc in site_defined_group_fields 
      if fc.id not in
        [ "_field/Group_field_placement"
        , "_field/Group_field_property"
        , "_field/Group_field_sel"
        ]
    ])

site_group_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Group_field_placement",      label="Position/size"       )
    , FieldChoice("_field/Group_field_property",       label="Property URI"        )
    , FieldChoice("_field/Group_field_sel",            label="Field id"            )
    ])

site_defined_list_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/List_choice",                label="List view"           )
    , FieldChoice("_field/List_comment",               label="Help"                )
    , FieldChoice("_field/List_default_type",          label="Default type"        )
    , FieldChoice("_field/List_default_view",          label="Default view"        )   
    , FieldChoice("_field/List_entity_selector",       label="Selector"            )
    , FieldChoice("_field/List_field_placement",       label="Position/size"       )
    , FieldChoice("_field/List_field_property",        label="Property URI"        )
    , FieldChoice("_field/List_field_sel",             label="Field id"            )
    , FieldChoice("_field/List_fields",                label="Fields"              )
    , FieldChoice("_field/List_id",                    label="List Id"             )
    , FieldChoice("_field/List_label",                 label="Label"               )
    , FieldChoice("_field/List_target_type",           label="List entity type"    )
    , FieldChoice("_field/List_type",                  label="List display type"   )
    ])

site_list_fields = (
    [ fc 
      for fc in site_defined_list_fields 
      if fc.id not in
        [ "_field/List_choice" 
        , "_field/List_field_placement"
        , "_field/List_field_property"
        , "_field/List_field_sel"
        ]
    ])

site_list_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/List_field_placement",       label="Position/size"       )
    , FieldChoice("_field/List_field_property",        label="Property URI"        )
    , FieldChoice("_field/List_field_sel",             label="Field id"            )
    ])

site_defined_type_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Type_alias_source",          label="Field alias value"   )
    , FieldChoice("_field/Type_alias_target",          label="Field alias name"    )
    , FieldChoice("_field/Type_aliases",               label="Field aliases"       )
    , FieldChoice("_field/Type_comment",               label="Comment"             )
    , FieldChoice("_field/Type_id",                    label="Type Id"             )
    , FieldChoice("_field/Type_label",                 label="Label"               )
    , FieldChoice("_field/Type_list",                  label="Default list"        )
    , FieldChoice("_field/Type_supertype_uri",         label="Supertype URI"       )
    , FieldChoice("_field/Type_supertype_uris",        label="Supertype URIs"      )
    , FieldChoice("_field/Type_uri",                   label="Type URI"            )
    , FieldChoice("_field/Type_view",                  label="Default view"        )
    ])

site_type_fields = (
    [ fc for fc in site_defined_type_fields if 
      fc.id not in {"_field/Type_alias_source", "_field/Type_alias_target", "_field/Type_supertype_uri"} ]
    )

# site_type_supertype_uris_fields = (
#     [ FieldChoice("_field/_initial_values")
#     , FieldChoice("_field/Type_supertype_uri",         label="Supertype URI"       )
#     , FieldChoice("_field/Type_supertype_uris",        label="Supertype URIs"      )
#     ])

# site_type_aliases_fields = (
#     [ FieldChoice("_field/_initial_values")
#     , FieldChoice("_field/Type_alias_source",          label="Type alias source"   )
#     , FieldChoice("_field/Type_alias_target",          label="Type alias target"   )
#     ])

site_user_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/User_description",           label="Description"         )
    , FieldChoice("_field/User_id",                    label="User Id"             )
    , FieldChoice("_field/User_name",                  label="User name"           )
    , FieldChoice("_field/User_permissions",           label="Permissions"         )
    , FieldChoice("_field/User_uri",                   label="User URI"            )
    ])

site_defined_view_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/View_choice",                label="Choose view"         )
    , FieldChoice("_field/View_comment",               label="Help"                )
    , FieldChoice("_field/View_edit_view",             label="Editable view?"      )
    , FieldChoice("_field/View_field_placement",       label="Position/size"       )
    , FieldChoice("_field/View_field_property",        label="Property URI"        )
    , FieldChoice("_field/View_field_sel",             label="Field id"            )
    , FieldChoice("_field/View_fields",                label="Fields"              )
    , FieldChoice("_field/View_id",                    label="View Id"             )
    , FieldChoice("_field/View_label",                 label="Label"               )
    , FieldChoice("_field/View_target_type",           label="View entity type"    )
    ])

site_view_fields = (
    [ fc 
      for fc in site_defined_view_fields 
      if fc.id not in
        [ "_field/View_choice" 
        , "_field/View_field_placement"
        , "_field/View_field_property"
        , "_field/View_field_sel"
        ]
    ])

site_view_field_group_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/View_field_placement",       label="Position/size"       )
    , FieldChoice("_field/View_field_property",        label="Property URI"        )
    , FieldChoice("_field/View_field_sel",             label="Field id"            )
    ])

site_vocab_fields = (
    [ FieldChoice("_field/_initial_values")
    , FieldChoice("_field/Vocab_id",                   label="Prefix"              )
    , FieldChoice("_field/Vocab_uri",                  label="Vocabulary URI"      )
    ])

site_fields = (
    [ FieldChoice("_field/_initial_values")] +
    # site_bibentry_fields[1:] +
    site_coll_fields[1:] +
    site_defined_entity_fields[1:] +
    site_enum_fields[1:] +
    site_field_fields[1:] +
    site_defined_group_fields[1:] +
    site_defined_list_fields[1:] +
    site_defined_type_fields[1:] +
    site_user_fields[1:] +
    site_defined_view_fields[1:] +
    site_vocab_fields[1:] +
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

def get_site_vocab_fields_sorted():
    return ( 
        site_default_entity_fields[1:] + 
        site_vocab_fields[1:]
        )

def get_site_vocab_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_vocab_fields_sorted() ) )

def get_site_bibentry_fields_sorted():
    return site_bibentry_fields[1:] + site_default_entity_fields[1:]

def get_site_bibentry_fields():
    return set( ( id_from_field_choice(fc) for fc in get_site_bibentry_fields_sorted() ) )

#   ----- Field render types -----

site_field_types = (
    [ FieldChoice("_enum_render_type/_initial_values")
    , FieldChoice("_enum_render_type/CheckBox",         label="CheckBox"                     )
    , FieldChoice("_enum_render_type/Codearea",         label="Monospace text"               )
    , FieldChoice("_enum_render_type/EntityId",         label="Entity Id"                    )
    , FieldChoice("_enum_render_type/EntityRef",        label="Local entity ref"             )
    , FieldChoice("_enum_render_type/EntityTypeId",     label="Entity type Id"               )
    , FieldChoice("_enum_render_type/Enum",             label="Required entity ref"          )
    , FieldChoice("_enum_render_type/Enum_choice",      label="Entity choice"                )
    , FieldChoice("_enum_render_type/Enum_choice_opt",  label="Optional entity choice"       )
    , FieldChoice("_enum_render_type/Enum_optional",    label="Optional entity ref"          )
    , FieldChoice("_enum_render_type/FileUpload",       label="File upload"                  )
    , FieldChoice("_enum_render_type/Group_Seq",        label="Field group sequence"         )
    , FieldChoice("_enum_render_type/Group_Seq_Row",    label="Field group sequence as table")
    , FieldChoice("_enum_render_type/Group_Set",        label="Field group set"              )
    , FieldChoice("_enum_render_type/Group_Set_Row",    label="Field group set as table"     )
    , FieldChoice("_enum_render_type/Identifier",       label="Identifier"                   )
    , FieldChoice("_enum_render_type/Markdown",         label="Markdown rich text"           )
    , FieldChoice("_enum_render_type/Placement",        label="Position/size"                )
    , FieldChoice("_enum_render_type/RefAudio",         label="Audio clip reference"         )
    , FieldChoice("_enum_render_type/RefImage",         label="Image reference"              )
    , FieldChoice("_enum_render_type/RefMultifield",    label="Fields of referenced entity"  )
    , FieldChoice("_enum_render_type/RepeatGroup",      label="Repeating field group "+
                                                              "(@@use Group_Seq 'Field group sequence')")
    , FieldChoice("_enum_render_type/RepeatGroupRow",   label="Repeating fields as table "+
                                                              "(@@use Group_Seq_Row 'Field group sequence as table')")
    , FieldChoice("_enum_render_type/ShowMarkdown",     label="Display Markdown rich text"   )
    , FieldChoice("_enum_render_type/Showtext",         label="Display text"                 )
    , FieldChoice("_enum_render_type/Text",             label="Short text"                   )
    , FieldChoice("_enum_render_type/Textarea",         label="Multiline text"               )
    , FieldChoice("_enum_render_type/TokenSet",         label="Space-separated tokens"       )
    , FieldChoice("_enum_render_type/URIImport",        label="Web import"                   )
    , FieldChoice("_enum_render_type/URILink",          label="Web link"                     )
    , FieldChoice("_enum_render_type/View_choice",      label="Choose view"                  )
    ])

def get_site_field_types_sorted():
    return site_field_types[1:]

def get_site_field_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_enum_render_type") 
          for fc in get_site_field_types_sorted()
        ])

def get_site_field_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_field_types_sorted() ) )

#   ----- Users -----

site_users = (
    [ FieldChoice("_user/_default_user_perms", label="Default permissions")
    , FieldChoice("_user/_unknown_user_perms", label="Unknown user")
    ])

def get_site_users_sorted():
    return site_users

def get_site_users_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_vocab") 
          for fc in get_site_users_sorted()
        ])

def get_site_users():
    return set( ( id_from_field_choice(fc) for fc in get_site_users_sorted() )  )

#   ----- Vocabulary namespaces -----

site_vocabs = (
    [ FieldChoice("_vocab/_initial_values")
    , FieldChoice("_vocab/annal",      label="Vocabulary namespace for Annalist-defined terms")
    , FieldChoice("_vocab/owl",        label="OWL ontology namespace")
    , FieldChoice("_vocab/rdf",        label="RDF core namespace")
    , FieldChoice("_vocab/rdfs",       label="RDF schema namespace")
    , FieldChoice("_vocab/xsd",        label="XML Schema datatypes namespace")
    ])

def get_site_vocabs_sorted():
    return site_vocabs[1:]

def get_site_vocabs_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_vocab") 
          for fc in get_site_vocabs_sorted()
        ])

def get_site_vocabs():
    return set( ( id_from_field_choice(fc) for fc in get_site_vocabs_sorted() )  )

#   ----- Field value mode types -----

site_value_modes = (
    [ FieldChoice("_enum_value_mode/_initial_values")
    , FieldChoice("_enum_value_mode/Value_direct",      label="Direct value"      )
    , FieldChoice("_enum_value_mode/Value_entity",      label="Entity reference"  )
    , FieldChoice("_enum_value_mode/Value_field",       label="Field reference"   )
    , FieldChoice("_enum_value_mode/Value_import",      label="Import from web"   )
    , FieldChoice("_enum_value_mode/Value_upload",      label="File upload"       )
    ])

def get_site_value_modes_sorted():
    return site_value_modes[1:]

def get_site_value_modes_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_enum_value_mode") 
          for fc in get_site_value_modes_sorted()
        ])

def get_site_value_modes():
    return set( ( id_from_field_choice(fc) for fc in get_site_value_modes_sorted() )  )

#   ----- Field value types -----

site_value_types = (
    [ FieldChoice("_enum_value_type/_initial_values")
    , FieldChoice("_enum_value_type/Longtext",                  label="annal:Longtext"  )
    , FieldChoice("_enum_value_type/Text",                      label="annal:Text"      )
    ])

def get_site_value_types_sorted():
    return site_value_types[1:]

def get_site_value_types_linked(coll_id):
    return (
        [ add_link_to_field_choice(fc, coll_id, "_enum_value_type") 
          for fc in get_site_value_types_sorted()
        ])

def get_site_value_types():
    return set( ( id_from_field_choice(fc) for fc in get_site_value_types_sorted() )  )

#   ----- All site entities (including test collection data) -----

test_types = (
    [ FieldChoice("_type/testtype",     label="RecordType testcoll/testtype")
    , FieldChoice("_type/testtype2",    label="RecordType testcoll/testtype2")
    ])

def get_test_types_sorted():
    return test_types

test_users = (
    [ FieldChoice("_user/testuser",     label="Test User")
    ])

def get_test_users_sorted():
    return test_users

test_entities = (
    [ FieldChoice("testtype/entity1",   label="Entity testcoll/testtype/entity1")
    , FieldChoice("testtype/entity2",   label="Entity testcoll/testtype/entity2")
    , FieldChoice("testtype/entity3",   label="Entity testcoll/testtype/entity3")
    , FieldChoice("testtype2/entity4",  label="Entity testcoll/testtype2/entity4")
    ])

def get_test_entities_sorted():
    return test_entities

site_entities = (
    get_site_list_types_sorted() +
    get_site_field_types_sorted() +     # @@TODO: change to render_types
    get_site_value_modes_sorted() +
    get_site_value_types_sorted() +
    get_site_fields_sorted() +
    get_site_field_groups_sorted() +
    get_site_lists_sorted() +
    get_site_types_sorted() +
    get_test_types_sorted() +
    get_site_users_sorted() +
    get_test_users_sorted() +
    get_site_views_sorted() +
    get_site_vocabs_sorted() +
    get_test_entities_sorted()
    )

def get_site_entities_sorted():
    return site_entities

def get_site_entities():
    return set( ( id_from_field_choice(fc) for fc in get_site_entities_sorted() )  )

# End.
