"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.fields.render_text    import RenderText

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
    log.info("get_renderer %s"%(renderid))
    if renderid == "annal:field_render/Text":
        return "annalist_field_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Textarea":
        return "annalist_field_text.html"
    if renderid == "annal:field_render/Slug":
        return "annalist_field_text.html"
        # return RenderText()
    log.info("*** not found ***")
    return None

# End.
