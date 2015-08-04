"""
Renderer and value mapper for URI value displayed as an image.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_context_field_value,
    get_field_edit_value,
    get_field_view_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Image reference value mapping
#
#   ----------------------------------------------------------------------------


class RefImageValueMapper(RenderBase):
    """
    Value mapper class for image resource reference
    """

    @classmethod
    def encode(cls, data_value):
        """
        Encodes image reference as a string
        """
        return data_value or ""

    @classmethod
    def decode(cls, field_value):
        """
        Decodes a URI value as an image reference.
        """
        return field_value or ""

#   ----------------------------------------------------------------------------
#
#   Image reference field renderers
#
#   ----------------------------------------------------------------------------

class ref_image_view_renderer(object):

    def render(self, context):
        """
        Render reference in entity view as referenced image.
        """
        linkval = RefImageValueMapper.encode(get_context_field_value(context, "target_value_link", ""))
        return (
            '''<a href="%s" target="_blank">'''+
            '''<img src="%s" alt="Image at '%s'" />'''+
            '''</a>''')%(linkval, linkval, linkval)

class ref_image_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" '''+
                   '''placeholder="{{field.field_placeholder}}" '''+
                   '''value="{{field.field_edit_value}}" />'''
        )
        return

    def render(self, context):
        """
        Render image URI for editing
        """
        return self._template.render(context)

def get_ref_image_renderer():
    """
    Return field renderer object for token list values
    """
    return RenderFieldValue(
        view_renderer=ref_image_view_renderer(), 
        edit_renderer=ref_image_edit_renderer(),
        )

# End.
