"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re

# from annalist.fields.render_text    import RenderText
from render_text    import RenderText

def get_renderer(renderid):
    """
    Returns a field renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    # @@TODO: currently just a minimal placeholder
    if renderid == "annal:field_render/Text":
        return "annalist_field_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "annalist_field_text.html"
    if renderid == "annal:field_render/Textarea":
        return "annalist_field_textarea.html"
    log.warning("get_renderer: %s not found"%renderid)
    return None

def get_placement_class(placement):
    """
    Returns placement classes corresponding to placement string provided.

    >>> get_placement_class("small:0,12")
    'small-12 columns'
    >>> get_placement_class("medium:0,12")
    'medium-12 columns'
    >>> get_placement_class("large:0,12")
    'large-12 columns'
    >>> get_placement_class("small:0,12;medium:0,4")
    'small-12 medium-4 columns'
    >>> get_placement_class("small:0,12;medium:0,6;large:0,4")
    'small-12 medium-6 large-4 columns'
    """
    ppr = re.compile(r"^(small|medium|large):(\d+),(\d+)$")
    ps = placement.split(';')
    c = ""
    for p in ps:
        pm = ppr.match(p)
        if not pm:
            break
        c += pm.group(1)+"-"+pm.group(3)+" "
    c += "columns"
    return c

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
