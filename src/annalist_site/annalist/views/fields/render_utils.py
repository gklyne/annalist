"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections    import OrderedDict, namedtuple

from django.conf                    import settings

# from annalist.models.entity         import EntityRoot, Entity #@@
from annalist.models.entitytypeinfo import EntityTypeInfo

from render_text                    import RenderText

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
    if renderid == "annal:field_render/Text":
        return "field/annalist_edit_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "field/annalist_edit_slug.html"
    if renderid == "annal:field_render/Placement":
        return "field/annalist_edit_text.html"
    if renderid == "annal:field_render/EntityId":
        return "field/annalist_edit_entityid.html"    
    if renderid == "annal:field_render/EntityTypeRef":
        return "field/annalist_edit_entitytyperef.html"    
    if renderid == "annal:field_render/Identifier":
        return "field/annalist_edit_identifier.html"    
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_edit_textarea.html"
    if renderid in ["annal:field_render/Type",
                    "annal:field_render/View", 
                    "annal:field_render/List", 
                    "annal:field_render/Field", 
                    "annal:field_render/Enum"]:
        return "field/annalist_edit_select.html"
    if renderid == "annal:field_render/View_sel":
        return "field/annalist_edit_view_sel.html"
    if renderid == "annal:field_render/View_fields":
        return "field/annalist_todo.html"
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
    if renderid == "annal:field_render/Text":
        return "field/annalist_view_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_view_textarea.html"
    if renderid == "annal:field_render/Slug":
        return "field/annalist_view_slug.html"
    if renderid == "annal:field_render/Placement":
        return "field/annalist_view_text.html"
    if renderid == "annal:field_render/EntityId":
        return "field/annalist_view_entityid.html"    
    if renderid == "annal:field_render/EntityTypeRef":
        return "field/annalist_view_entitytyperef.html"    
    if renderid == "annal:field_render/Identifier":
        return "field/annalist_view_identifier.html"    
    if renderid in ["annal:field_render/Type",
                    "annal:field_render/View", 
                    "annal:field_render/List", 
                    "annal:field_render/Field", 
                    "annal:field_render/Enum"]:
        return "field/annalist_view_select.html"
    if renderid == "annal:field_render/View_sel":
        return "field/annalist_view_view_sel.html"
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
    if renderid == "annal:field_render/Text":
        return "field/annalist_item_text.html"
    if renderid == "annal:field_render/Slug":
        return "field/annalist_item_text.html"
    if renderid == "annal:field_render/EntityId":
        return "field/annalist_item_entityid.html"    
    if renderid == "annal:field_render/EntityTypeRef":
        return "field/annalist_item_entitytyperef.html"
    if renderid == "annal:field_render/Identifier":
        return "field/annalist_item_identifier.html"
    if renderid in ["annal:field_render/Type",
                    "annal:field_render/View", 
                    "annal:field_render/List", 
                    "annal:field_render/Field", 
                    "annal:field_render/Enum"]:
        return "field/annalist_item_entityref.html"
    # if renderid == "annal:field_render/View_sel":
    #     return "field/annalist_item_entityref.html"
    log.debug("get_item_renderer: %s not found"%renderid)
    return "field/annalist_item_none.html"

def get_entity_values(displayinfo, entity, entity_id=None):
    """
    Returns an entity values dictionary for a supplied entity, suitable for
    use with a bound_field object (see above).
    """
    if not entity_id:
        entity_id = entity.get_id()
    type_id    = entity.get_type_id()
    typeinfo   = EntityTypeInfo(displayinfo.site, displayinfo.collection, type_id)
    entityvals = entity.get_values().copy()
    entityvals['entity_id']        = entity_id
    entityvals['entity_link']      = entity.get_view_url_path()
    # log.info("type_id %s"%(type_id))
    entityvals['entity_type_id']   = type_id
    entityvals['entity_type_link'] = typeinfo.recordtype.get_view_url_path()
    return entityvals

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
