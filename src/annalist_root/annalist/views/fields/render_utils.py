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
import render_tokenset

def get_edit_renderer(renderid):
    """
    Returns an field edit renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    if renderid == "Text":
        return "field/annalist_edit_text.html"
        # return RenderText()
    if renderid == "Slug":
        return "field/annalist_edit_slug.html"
    if renderid == "Placement":
        return "field/annalist_edit_text.html"
    if renderid == "EntityId":
        return "field/annalist_edit_entityid.html"    
    if renderid == "EntityTypeId":
        return "field/annalist_edit_entitytypeid.html"    
    if renderid == "Identifier":
        return "field/annalist_edit_identifier.html"    
    if renderid == "Textarea":
        return "field/annalist_edit_textarea.html"
    if renderid in ["Type", "View", "List", "Field", "Enum", "Enum_optional"]:
        return "field/annalist_edit_select.html"
    if renderid == "View_sel":
        return "field/annalist_edit_view_sel.html"
    if renderid == "TokenSet":
        # return "field/annalist_edit_tokenlist.html"
        return RenderTokenSet(render_tokenset.edit)
    log.warning("get_edit_renderer: %s not found"%renderid)
    # raise ValueError("get_edit_renderer: %s not found"%renderid)
    # Default to simple text for unknown renderer type
    return "field/annalist_edit_text.html"

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
    if renderid == "Text":
        return "field/annalist_view_text.html"
        # return RenderText()
    if renderid == "Textarea":
        return "field/annalist_view_textarea.html"
    if renderid == "Slug":
        return "field/annalist_view_slug.html"
    if renderid == "Placement":
        return "field/annalist_view_text.html"
    if renderid == "EntityId":
        return "field/annalist_view_entityid.html"    
    if renderid == "EntityTypeId":
        return "field/annalist_view_entitytypeid.html"    
    if renderid == "Identifier":
        return "field/annalist_view_identifier.html"    
    if renderid in ["Type", "View", "List", "Field", "Enum", "Enum_optional"]:
        return "field/annalist_view_select.html"
    if renderid == "View_sel":
        return "field/annalist_view_view_sel.html"
    if renderid == "TokenSet":
        # return "field/annalist_view_tokenlist.html"
        return RenderTokenSet(render_tokenset.view)
    log.warning("get_view_renderer: %s not found"%renderid)
    # raise ValueError("get_view_renderer: %s not found"%renderid)
    # Default to simple text for unknown renderer type
    return "field/annalist_view_text.html"

def get_head_renderer(renderid):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    return "field/annalist_head_any.html"

def get_item_renderer(renderid):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "Text":
        return "field/annalist_item_text.html"
    if renderid == "Slug":
        return "field/annalist_item_text.html"
    if renderid == "EntityId":
        return "field/annalist_item_entityid.html"    
    if renderid == "EntityTypeId":
        return "field/annalist_item_entitytypeid.html"
    if renderid == "Identifier":
        return "field/annalist_item_identifier.html"
    if renderid in ["Type", "View", "List", "Field", "Enum", "Enum_optional"]:
        return "field/annalist_item_select.html"
    if renderid == "TokenSet":
        return RenderTokenSet(render_tokenset.item)
    log.debug("get_item_renderer: %s not found"%renderid)
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
