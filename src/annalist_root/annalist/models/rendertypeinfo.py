"""
Annalist renderer type information, used for generating JSON-LD context data.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import os
# import os.path
# import urlparse
# import shutil

import logging
log = logging.getLogger(__name__)

# from annalist                   import layout
# from annalist.exceptions        import Annalist_Error
# from annalist.identifiers       import ANNAL
# from annalist                   import util

# Render type classification, used for generating appropriate JSON-LD context values
# Separated from annalist.views.fields.find_renderers to avoid model dependency on views

_render_type_literal = set(
    [ "Text", "Textarea", "Codearea", "Showtext"
    , "Placement", "CheckBox", "Markdown", "ShowMarkdown"
    , "EntityId", "EntityTypeId"
    , "TokenSet"
    # , "RefMultifield"
    ])

_render_type_id = set(
    [ "Identifier"
    , "EntityRef"
    , "RefAudio", "RefImage", "URILink", "URIImage"
    , "RefMultifield"
    , "Group_Set", "Group_Set_Row"
    , "Enum", "Enum_optional", "Enum_choice", "Enum_choice_opt"
    , "View_choice"
    , "Type", "View", "List", "Field"
    ])

_render_type_object = set(
    [ "URIImport", "FileUpload"
    , "RepeatGroup", "RepeatGroupRow", "Group_Seq", "Group_Seq_Row"
    ])

_render_type_set = set(
    [ "TokenSet", "Group_Set", "Group_Set_Row"
    ])

_render_type_list = set(
    [ "RepeatGroup", "RepeatGroupRow", "Group_Seq", "Group_Seq_Row"
    ])

def is_render_type_literal(field_render_type):
    """
    Returns True if the supplied render type expects a literral (string) 
    value to be stored in a corresponding entity field.
    """
    return field_render_type in _render_type_literal

def is_render_type_id(field_render_type):
    """
    Returns True if the supplied render type expects a id (URI reference) 
    value to be stored in a corresponding entity field.
    """
    return field_render_type in _render_type_id

def is_render_type_set(field_render_type):
    """
    Returns True if the supplied render type expects a list value,
    which is interpreted as a set, to be stored in a corresponding 
    entity field.
    """
    return field_render_type in _render_type_set

def is_render_type_list(field_render_type):
    """
    Returns True if the supplied render type expects a list value,
    which is interpreted as an ordered list, to be stored in a 
    corresponding entity field.
    """
    return field_render_type in _render_type_list

def is_render_type_object(field_render_type):
    """
    Returns True if the supplied render type expects a complex (object) 
    value to be stored in a corresponding entity field.
    """
    return field_render_type in _render_type_object

# End.
