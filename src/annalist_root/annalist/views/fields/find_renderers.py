"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections                import OrderedDict, namedtuple

from django.conf                import settings

from render_fieldvalue          import RenderFieldValue
from render_text                import TextValueMapper
from render_entityid            import EntityIdValueMapper
from render_placement           import get_field_placement_renderer
from render_tokenset            import get_field_tokenset_renderer, TokenSetValueMapper
from render_bool_checkbox       import get_bool_checkbox_renderer, BoolCheckboxValueMapper
from render_ref_audio           import get_ref_audio_renderer, RefAudioValueMapper
from render_ref_image           import get_ref_image_renderer, RefImageValueMapper
from render_text_markdown       import (
    get_text_markdown_renderer, get_show_markdown_renderer, TextMarkdownValueMapper
    )
from render_select              import (
    get_select_renderer, get_choice_renderer,
    get_entitytype_renderer, get_view_choice_renderer,
    SelectValueMapper
    )
from render_uri_link            import get_uri_link_renderer, URILinkValueMapper
from render_uri_import          import get_uri_import_renderer, URIImportValueMapper
from render_file_upload         import get_file_upload_renderer, FileUploadValueMapper
from render_repeatgroup         import (
    get_repeatgroup_renderer,
    get_repeatgrouprow_renderer,
    get_repeatlistrow_renderer,
    )
from render_fieldrow            import get_fieldrow_renderer, FieldRowValueMapper
from render_ref_multifields     import get_ref_multifield_renderer, RefMultifieldValueMapper

# Render type mappings to templates and/or renderer access functions

_field_renderers = {}   # renderer cache

_field_view_files = (
    { "Text":           "field/annalist_view_text.html"
    , "Showtext":       "field/annalist_view_text.html"
    , "Textarea":       "field/annalist_view_textarea.html"
    , "Codearea":       "field/annalist_view_codearea.html"
    , "EntityRef":      "field/annalist_view_entityref.html"
    , "EntityId":       "field/annalist_view_entityid.html"
    , "Identifier":     "field/annalist_view_identifier.html"
    , "Padding":        "field/annalist_view_padding.html"
    })

_field_edit_files = (
    { "Text":           "field/annalist_edit_text.html"
    , "Showtext":       "field/annalist_view_text.html"
    , "Textarea":       "field/annalist_edit_textarea.html"
    , "Codearea":       "field/annalist_edit_codearea.html"
    , "EntityRef":      "field/annalist_edit_entityref.html"
    , "EntityId":       "field/annalist_edit_entityid.html"
    , "Identifier":     "field/annalist_edit_identifier.html"
    , "Padding":        "field/annalist_edit_padding.html"
    })

_field_get_renderer_functions = (
    { "Placement":          get_field_placement_renderer
    , "TokenSet":           get_field_tokenset_renderer
    , "CheckBox":           get_bool_checkbox_renderer
    , "Markdown":           get_text_markdown_renderer
    , "ShowMarkdown":       get_show_markdown_renderer
    , "RefAudio":           get_ref_audio_renderer
    , "RefImage":           get_ref_image_renderer
    , "URILink":            get_uri_link_renderer
    , "URIImport":          get_uri_import_renderer
    , "FileUpload":         get_file_upload_renderer
    , "EntityTypeId":       get_entitytype_renderer
    , "Enum":               get_select_renderer
    , "Enum_optional":      get_select_renderer
    , "Enum_choice":        get_choice_renderer
    , "Enum_choice_opt":    get_choice_renderer
    , "View_choice":        get_view_choice_renderer
    , "RefMultifield":      get_ref_multifield_renderer
    , "RepeatGroup":        get_repeatgroup_renderer
    , "Group_Seq":          get_repeatgroup_renderer
    , "Group_Set":          get_repeatgroup_renderer
    , "RepeatGroupRow":     get_repeatgrouprow_renderer
    , "Group_Seq_Row":      get_repeatgrouprow_renderer
    , "Group_Set_Row":      get_repeatgrouprow_renderer
    , "RepeatListRow":      get_repeatlistrow_renderer
    , "FieldRow":           get_fieldrow_renderer
    # Render types recognized for backward compatibility
    , "URIImage":           get_ref_image_renderer
    , "Type":               get_select_renderer
    , "View":               get_select_renderer
    , "List":               get_select_renderer
    , "Field":              get_select_renderer
    , "List_sel":           get_choice_renderer
    })

_field_value_mappers = (
    { "TokenSet":           TokenSetValueMapper
    , "CheckBox":           BoolCheckboxValueMapper
    , "Markdown":           TextMarkdownValueMapper
    , "ShowMarkdown":       TextMarkdownValueMapper
    , "RefAudio":           RefAudioValueMapper
    , "RefImage":           RefImageValueMapper
    , "URILink":            URILinkValueMapper
    , "URIImport":          URIImportValueMapper
    , "FileUpload":         FileUploadValueMapper
    , "EntityId":           EntityIdValueMapper
    , "EntityTypeId":       SelectValueMapper
    , "Enum":               SelectValueMapper
    , "Enum_optional":      SelectValueMapper
    , "Enum_choice":        SelectValueMapper
    , "Enum_choice_opt":    SelectValueMapper
    , "View_choice":        SelectValueMapper
    , "RefMultifield":      RefMultifieldValueMapper
    , "FieldRow":           FieldRowValueMapper
    # Render types recognized for backward compatibility
    , "URIImage":           RefImageValueMapper
    , "Type":               SelectValueMapper
    , "View":               SelectValueMapper
    , "List":               SelectValueMapper
    , "Field":              SelectValueMapper
    , "List_sel":           SelectValueMapper
    })

def is_repeat_field_render_type(render_type):
    repeat_field_render_types = (
        [ "RepeatGroup", "RepeatGroupRow"
        , "Group_Seq", "Group_Seq_Row"
        , "Group_Set", "Group_Set_Row"
        ])
    return render_type in repeat_field_render_types

def get_field_base_renderer(field_render_type):
    """
    Lookup and return base renderer for given field type.
    """
    if field_render_type not in _field_renderers:
        # Create and cache renderer
        if ( (field_render_type in _field_view_files) or
             (field_render_type in _field_edit_files) ):
            viewfile = _field_view_files.get(field_render_type, None)
            editfile = _field_edit_files.get(field_render_type, None)
            _field_renderers[field_render_type] = RenderFieldValue(
                field_render_type,
                view_file=viewfile, edit_file=editfile
                )
        elif field_render_type in _field_get_renderer_functions:
            _field_renderers[field_render_type] = _field_get_renderer_functions[field_render_type]()
    return _field_renderers.get(field_render_type, None)

def get_entityref_edit_renderer(renderer, field_render_type):
    """
    Returns an updated edit renderer, called for fields with an entity type reference:
    used to force a selection renderer for fields with other view render types.
    """
    if field_render_type not in ["Enum", "Enum_optional", "Enum_choice", "Enum_choice_opt", "View_choice", "List_sel"]:
        renderer = get_field_base_renderer("Enum")
    return renderer

def get_uriimport_edit_renderer(renderer, field_render_type):
    """
    Returns an updated edit renderer for fields with a URI import value type
    """
    if field_render_type not in ["URIImport"]:
        renderer = get_field_base_renderer("URIImport")
    return renderer

def get_fileupload_edit_renderer(renderer, field_render_type):
    """
    Returns an updated edit renderer for fields with a file upload value type
    """
    if field_render_type not in ["FileUpload"]:
        renderer = get_field_base_renderer("FileUpload")
    return renderer

def get_field_edit_renderer(field_render_type, field_value_mode):
    """
    Get edit renderer for supplied field details, taking account of variations 
    on the base renderer due to field reference and field value type.
    """
    # log.debug("Render field_render_type %s, field_value_mode %s"%(field_render_type, field_value_mode))
    renderer = get_field_base_renderer(field_render_type)
    if field_value_mode in ["Value_entity", "Value_field"]:
        renderer = get_entityref_edit_renderer(renderer, field_render_type)
    elif field_value_mode == "Value_import":
        renderer = get_uriimport_edit_renderer(renderer, field_render_type)
    elif field_value_mode == "Value_upload":
        renderer = get_fileupload_edit_renderer(renderer, field_render_type)
    return renderer

def get_label_renderer(field_render_type, field_value_mode):
    """
    Returns a field label renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    class _renderer(object):
        def __init__(self):
            pass
        def render(self, context):
            return context.get('field_label', "@@no 'field_label'@@")
    return _renderer()

def get_edit_renderer(field_render_type, field_value_mode):
    """
    Returns an field edit renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    The original version returns the name of a template to render the form.
    With versions of Django >=1.7, an alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    renderer = get_field_edit_renderer(field_render_type, field_value_mode)
    if not renderer:
        # Default to simple text for unknown renderer type
        log.warning("get_edit_renderer: %s not found"%field_render_type)
        renderer = get_field_base_renderer("Text")
    return renderer.edit()

def get_view_renderer(field_render_type, field_value_mode):
    """
    Returns a field view renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    The original version returns the name of a template to render the form.
    With versions of Django >=1.7, an alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    renderer = get_field_base_renderer(field_render_type)
    if not renderer:
        # Default to simple text for unknown renderer type
        log.warning("get_view_renderer: %s not found"%field_render_type)
        renderer = get_field_base_renderer("Text")
    return renderer.view()

def get_label_edit_renderer(field_render_type, field_value_mode):
    """
    Returns an field edit renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_base_renderer(field_render_type)
    if not renderer:
        # Default to simple text for unknown renderer type
        log.warning("get_label_edit_renderer: %s not found"%field_render_type)
        renderer = get_field_base_renderer("Text")
    return renderer.label_edit()

def get_label_view_renderer(field_render_type, field_value_mode):
    """
    Returns a field view renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_base_renderer(field_render_type)
    if not renderer:
        # Default to simple text for unknown renderer type
        log.warning("get_label_view_renderer: %s not found"%field_render_type)
        renderer = get_field_base_renderer("Text")
    return renderer.label_view()

def get_col_head_renderer(field_render_type, field_value_mode):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_base_renderer(field_render_type)
    if renderer:
        return renderer.col_head()
    log.debug("get_col_head_renderer: %s not found"%field_render_type)
    return "field/annalist_head_any.html"

def get_col_head_view_renderer(field_render_type, field_value_mode):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element when viewing an entity.
    """
    renderer = get_field_base_renderer(field_render_type)
    if renderer:
        return renderer.col_head_view()
    log.debug("get_col_head_view_renderer: %s not found"%field_render_type)
    return "field/annalist_head_any.html"

def get_col_head_edit_renderer(field_render_type, field_value_mode):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element when editing an entity.
    """
    renderer = get_field_base_renderer(field_render_type)
    if renderer:
        return renderer.col_head_edit()
    log.debug("get_col_head_edit_renderer: %s not found"%field_render_type)
    return "field/annalist_head_any.html"

def get_col_edit_renderer(field_render_type, field_value_mode):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_edit_renderer(field_render_type, field_value_mode)
    if renderer:
        return renderer.col_edit()
    log.debug("get_col_edit_renderer: %s not found"%field_render_type)
    return "field/annalist_item_none.html"

def get_col_view_renderer(field_render_type, field_value_mode):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_base_renderer(field_render_type)
    if renderer:
        return renderer.col_view()
    log.debug("get_col_view_renderer: %s not found"%field_render_type)
    return "field/annalist_item_none.html"

def get_mode_renderer(field_render_type, field_value_mode):
    """
    Returns a renderer for the indicated render type that renders a field using the
    current render_mode (used for nested renderers which can be invoked in different 
    view contexts).
    """
    renderer = get_field_base_renderer(field_render_type)
    if not renderer:
        # Default to simple text for unknown renderer type
        log.debug("get_mode_renderer: %s not found"%field_render_type)
        renderer = get_field_base_renderer("Text")
    return renderer.render_mode()

def get_value_mapper(field_render_type):
    """
    Returns a value mapper class instance (with encode and decode methods) 
    which is used to map values between entity fields and textual form fields.

    The default 'RenderText' object returned contains identity mappings.
    """
    mapper_class = TextValueMapper
    if field_render_type in _field_value_mappers:
        mapper_class = _field_value_mappers[field_render_type]
    return mapper_class()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
