"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections                    import OrderedDict, namedtuple

from django.conf                    import settings

from render_text                    import RenderText
from render_tokenset                import RenderTokenSet
from render_fieldvalue              import RenderFieldValue
from render_tokenset                import RenderTokenSet
import render_tokenset
from render_repeatgroup             import RenderRepeatGroup
import render_repeatgroup

_field_renderers = {}

_field_view_files = (
    { "Text":           "field/annalist_view_text.html"
    , "Textarea":       "field/annalist_view_textarea.html"
    , "Slug":           "field/annalist_view_slug.html"
    , "Placement":      "field/annalist_view_text.html"
    , "EntityId":       "field/annalist_view_entityid.html"    
    , "EntityTypeId":   "field/annalist_view_entitytypeid.html"    
    , "Identifier":     "field/annalist_view_identifier.html"    
    , "Type":           "field/annalist_view_select.html"
    , "View":           "field/annalist_view_select.html"
    , "List":           "field/annalist_view_select.html"
    , "Field":          "field/annalist_view_select.html"
    , "Enum":           "field/annalist_view_select.html"
    , "Enum_optional":  "field/annalist_view_select.html"
    , "View_sel":       "field/annalist_view_view_sel.html"
    })

_field_edit_files = (
    { "Text":           "field/annalist_edit_text.html"
    , "Textarea":       "field/annalist_edit_textarea.html"
    , "Slug":           "field/annalist_edit_slug.html"
    , "Placement":      "field/annalist_edit_text.html"
    , "EntityId":       "field/annalist_edit_entityid.html"    
    , "EntityTypeId":   "field/annalist_edit_entitytypeid.html"    
    , "Identifier":     "field/annalist_edit_identifier.html"    
    , "Type":           "field/annalist_edit_select.html"
    , "View":           "field/annalist_edit_select.html"
    , "List":           "field/annalist_edit_select.html"
    , "Field":          "field/annalist_edit_select.html"
    , "Enum":           "field/annalist_edit_select.html"
    , "Enum_optional":  "field/annalist_edit_select.html"
    , "View_sel":       "field/annalist_edit_view_sel.html"
    })

def get_field_renderer(renderid):
    if renderid not in _field_renderers:
        if ( (renderid in _field_view_files) or
             (renderid in _field_edit_files) ):
            viewfile = _field_view_files.get(renderid, None)
            editfile = _field_edit_files.get(renderid, None)
            _field_renderers[renderid] = RenderFieldValue(
                viewfile=viewfile, editfile=editfile
                )
    return _field_renderers.get(renderid, None)

def get_edit_renderer(renderid):
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
    if renderid == "TokenSet":
        # return "field/annalist_edit_tokenlist.html"
        return RenderTokenSet(render_tokenset.edit)
    if renderid == "RepeatGroup":
        return RenderRepeatGroup(render_repeatgroup.edit_group)
    # @@TODO: not currently used
    # if renderid == "RepeatListRow":
    #     return RenderRepeatGroup(render_repeatgroup.edit_listrow)
    if renderid == "RepeatGroupRow":
        return RenderRepeatGroup(render_repeatgroup.edit_grouprow)
    renderer = get_field_renderer(renderid)
    if renderer:
        return renderer.label_edit()
    log.debug("get_edit_renderer: %s not found"%renderid)
    # raise ValueError("get_edit_renderer: %s not found"%renderid)
    # Default to simple text for unknown renderer type
    renderer = get_field_renderer("Text")
    return renderer.label_edit()

def get_view_renderer(renderid):
    """
    Returns a field view renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    if renderid == "TokenSet":
        # return "field/annalist_view_tokenlist.html"
        return RenderTokenSet(render_tokenset.view)
    if renderid == "RepeatGroup":
        return RenderRepeatGroup(render_repeatgroup.view_group)
    if renderid == "RepeatListRow":
        return RenderRepeatGroup(render_repeatgroup.view_listrow)
    if renderid == "RepeatGroupRow":
        return RenderRepeatGroup(render_repeatgroup.view_grouprow)
    renderer = get_field_renderer(renderid)
    if renderer:
        return renderer.label_view()
    # Default to simple text for unknown renderer type
    log.warning("get_view_renderer: %s not found"%renderid)
    renderer = get_field_renderer("Text")
    return renderer.label_view()

def get_colhead_renderer(renderid):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    renderer = get_field_renderer(renderid)
    if renderer:
        return renderer.col_head()
    log.debug("get_colhead_renderer: %s not found"%renderid)
    return "field/annalist_head_any.html"

def get_coledit_renderer(renderid):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "TokenSet":
        return RenderTokenSet(render_tokenset.item)
    # if renderid == "RepeatGroup":
    #     return RenderRepeatGroup(render_repeatgroup.view_row)
    renderer = get_field_renderer(renderid)
    if renderer:
        return renderer.col_edit()
    log.debug("get_coledit_renderer: %s not found"%renderid)
    return "field/annalist_item_none.html"

def get_colview_renderer(renderid):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "TokenSet":
        return RenderTokenSet(render_tokenset.item)
    # if renderid == "RepeatGroup":
    #     return RenderRepeatGroup(render_repeatgroup.view_row)
    renderer = get_field_renderer(renderid)
    if renderer:
        return renderer.view()
    log.debug("get_colview_renderer: %s not found"%renderid)
    return "field/annalist_item_none.html"

def get_value_mapper(renderid):
    """
    Returns a value mapper class (with encode and decode methods) which is used to map
    values between entity fields and textual form fields.

    The default 'RenderText' object returned contains identity mappings.
    """
    if renderid == "TokenSet":
        return RenderTokenSet("no template")
    else:
        return RenderText()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
