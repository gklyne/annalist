"""
Renderer and value mapper for text value rendered as Markdown.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import markdown

from annalist.views.displayinfo                 import apply_substitutions

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value,
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Markdown text value mapping
#
#   ----------------------------------------------------------------------------


class TextMarkdownValueMapper(RenderBase):
    """
    Value mapper class for Markdown text
    """

    @classmethod
    def encode(cls, data_value):
        """
        Encodes supplied data value as string to appear in <textarea> form input.
        """
        return data_value or ""

#   ----------------------------------------------------------------------------
#
#   Markdown text field renderers
#
#   ----------------------------------------------------------------------------

class text_markdown_view_renderer(object):
    def render(self, context):
        """
        Render Markdown text for viewing.
        """
        textval = TextMarkdownValueMapper.encode(get_field_view_value(context, None))
        textval = apply_substitutions(context, textval)
        htmlval = markdown.markdown(textval)
        return """<span class="markdown">%s</span>"""%htmlval

class text_markdown_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<textarea cols="64" rows="6" name="{{repeat_prefix}}{{field.field_name}}" '''+
                      '''class="small-rows-4 medium-rows-8" '''+
                      '''placeholder="{{field.field_placeholder}}" '''+
                      '''>{{encoded_field_value}}</textarea>'''
            )
        return

    def render(self, context):
        """
        Render Markdown text for editing
        """
        val     = get_field_edit_value(context, None)
        textval = TextMarkdownValueMapper.encode(val)
        with context.push(encoded_field_value=textval):
            result = self._template.render(context)
        return result

def get_text_markdown_renderer():
    """
    Return field renderer object for Markdown text
    """
    return RenderFieldValue("markdown",
        view_renderer=text_markdown_view_renderer(), 
        edit_renderer=text_markdown_edit_renderer(),
        )

def get_show_markdown_renderer():
    """
    Return field renderer object for display-only (no input) of Markdown text
    """
    return RenderFieldValue("show_markdown",
        view_renderer=text_markdown_view_renderer(), 
        edit_renderer=text_markdown_view_renderer(),
        )

# End.
