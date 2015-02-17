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

# from django.conf                import settings
# from django.http                import QueryDict
# from django.utils.http          import urlquote, urlunquote
# from django.core.urlresolvers   import resolve, reverse

# from annalist.util              import valid_id
# from annalist.identifiers       import RDF, RDFS, ANNAL
# from annalist                   import layout
# from annalist                   import message

# from tests import (
#     TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
#     )

# from entity_testsitedata            import (
#     get_site_types, get_site_types_sorted,
#     get_site_lists, get_site_lists_sorted,
#     get_site_list_types, get_site_list_types_sorted,
#     get_site_views, get_site_views_sorted,
#     get_site_field_groups, get_site_field_groups_sorted, 
#     get_site_fields, get_site_fields_sorted, 
#     get_site_field_types, get_site_field_types_sorted, 
#     )


#   -----------------------------------------------------------------------------
#
#   ----- Site-wide entities defined
#
#   -----------------------------------------------------------------------------

#   ----- Types -----

site_types = (
    [ "_initial_values"
    , "_field"
    , "_group"
    , "_list"
    , "_type"
    , "_user"
    , "_view"
    , "BibEntry_type"
    , "Default_type"
    , "Enum_bib_type"
    , "Enum_list_type"
    , "Enum_render_type"
    ])

def get_site_types_sorted():
    return site_types[1:]

def get_site_types():
    return set(site_types[1:])

#   ----- Lists -----

site_lists = (
    [ "_initial_values"
    , "BibEntry_list"
    , "Default_list"
    , "Default_list_all"
    , "Field_group_list"
    , "Field_list"
    , "List_list"
    , "Type_list"
    , "User_list"
    , "View_list"
    ])

def get_site_lists_sorted():
    return site_lists[1:]

def get_site_lists():
    return set(site_lists[1:])

#   ----- List types -----

site_list_types = (
    [ "Grid"
    , "List"
    ])

def get_site_list_types_sorted():
    return site_list_types

def get_site_list_types():
    return set(site_list_types)

#   ----- Views -----

site_views = (
    [ "_initial_values"
    , "BibEntry_view"
    , "Default_view"
    , "Field_group_view"
    , "Field_view"
    , "List_view"
    , "Type_view"
    , "User_view"
    , "View_view"
    ])

def get_site_views_sorted():
    return site_views[1:]

def get_site_views():
    return set(site_views[1:])

#   ----- Field groups -----

site_field_groups = (
    [ "_initial_values"
    , "Bib_book_group"
    , "Bib_identifier_group"
    , "Bib_journal_group"
    , "Bib_license_group"
    , "Bib_person_group"
    , "Bib_publication_group"
    , "Group_field_group"
    , "List_field_group"
    , "Type_alias_group"
    , "View_field_group"
    ])

def get_site_field_groups_sorted():
    return site_field_groups[1:]

def get_site_field_groups():
    return set(site_field_groups[1:])

#   ----- Fields -----

site_default_entity_fields = (
    [ "_initial_values"
    , "Entity_comment"
    , "Entity_id"
    , "Entity_label"
    , "Entity_type"
    ])

site_bibentry_fields = (
    [ "_initial_values"
    , "Bib_address"
    , "Bib_alternate"
    , "Bib_authors"
    , "Bib_bookentry"
    , "Bib_booktitle"
    , "Bib_chapter"
    , "Bib_description"
    , "Bib_edition"
    , "Bib_editors"
    , "Bib_eprint"
    , "Bib_firstname"
    , "Bib_howpublished"
    , "Bib_id"
    , "Bib_idanchor"
    , "Bib_identifiers"
    , "Bib_idtype"
    , "Bib_institution"
    , "Bib_journal"
    , "Bib_jurisdiction"
    , "Bib_lastname"
    , "Bib_license"
    , "Bib_month"
    , "Bib_name"
    , "Bib_note"
    , "Bib_number"
    , "Bib_organization"
    , "Bib_pages"
    , "Bib_publication_details"
    , "Bib_publisher"
    , "Bib_school"
    , "Bib_shortcode"
    , "Bib_title"
    , "Bib_type"
    , "Bib_url"
    , "Bib_volume"
    , "Bib_year"
    ])

site_field_fields = (
    [ "_initial_values"
    , "Field_comment"
    , "Field_default"
    , "Field_entity_type"
    , "Field_groupref"
    , "Field_id"
    , "Field_label"
    , "Field_missing"
    , "Field_placeholder"
    , "Field_placement"
    , "Field_property"
    , "Field_render"
    , "Field_repeat_label_add"
    , "Field_repeat_label_delete"
    , "Field_restrict"
    , "Field_type"
    , "Field_typeref"
    ])

site_group_fields = (
    [ "_initial_values"
    , "Group_comment"
    , "Group_field_sel"
    , "Group_field_placement"
    , "Group_field_property"
    , "Group_id"
    , "Group_label"
    , "Group_repeat_fields"
    ])

site_list_fields = (
    [ "_initial_values"
    , "List_choice"
    , "List_comment"
    , "List_default_type"
    , "List_default_view"
    , "List_entity_selector"
    , "List_id"
    , "List_label"
    , "List_repeat_fields"
    , "List_target_type"
    , "List_type"
    ])

site_type_fields = (
    [ "_initial_values"
    , "Type_comment"
    , "Type_id"
    , "Type_label"
    , "Type_list"
    , "Type_uri"
    , "Type_view"
    ])

site_user_fields = (
    [ "_initial_values"
    , "User_description"
    , "User_id"
    , "User_name"
    , "User_permissions"
    , "User_uri"
    ])

site_view_fields = (
    [ "_initial_values"
    # , "View_choice"
    , "View_comment"
    , "View_edit_view"
    , "View_fields"
    , "View_id"
    , "View_label"
    , "View_target_type"
    ])

site_fields = (
    [ "_initial_values" ] +
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
    return set(site_fields[1:])

def get_site_default_entity_fields_sorted():
    return site_default_entity_fields[1:]

def get_site_default_entity_fields():
    return set(site_default_entity_fields[1:])

def get_site_view_fields_sorted():
    return site_default_entity_fields[1:] + site_view_fields[1:]

def get_site_view_fields():
    return set(get_site_view_fields_sorted())

def get_site_bibentry_fields_sorted():
    return site_bibentry_fields[1:] + site_default_entity_fields[1:]

def get_site_bibentry_fields():
    return set(get_site_bibentry_fields_sorted())

#   ----- Field render types -----

site_field_types = (
    [ "_initial_values"
    , "CheckBox"
    , "EntityId"
    , "EntityTypeId"
    , "Enum"
    , "Enum_choice"
    , "Enum_optional"
    , "Field"
    , "Identifier"
    , "List"
    , "Markdown"
    , "Placement"
    , "RepeatGroup"
    , "RepeatGroupRow"
    , "Slug"
    , "Text"
    , "Textarea"
    , "TokenSet"
    , "Type"
    , "URIImage"
    , "URILink"
    , "View"
    ])

def get_site_field_types_sorted():
    return site_field_types[1:]

def get_site_field_types():
    return set(site_field_types[1:])

# End.
