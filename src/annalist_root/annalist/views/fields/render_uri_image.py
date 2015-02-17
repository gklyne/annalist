"""
Renderer and value mapper for URI value displayed as an image.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Image URI value mapping
#
#   ----------------------------------------------------------------------------


class URIImageValueMapper(object):
    """
    Value mapper class for token list
    """

    @staticmethod
    def encode(data_value):
        """
        Encodes image reference as a string
        """
        return data_value or ""

    @staticmethod
    def decode(field_value):
        """
        Decodes a URI value as an image reference.
        """
        return field_value or ""

#   ----------------------------------------------------------------------------
#
#   Image URI field renderers
#
#   ----------------------------------------------------------------------------

class uri_image_view_renderer(object):

    def render(self, context):
        """
        Render URI in view as referenced image.
        """
        linkval = URIImageValueMapper.encode(get_field_value(context, ""))
        return (
            '''<a href="%s" target="_blank">'''+
            '''<img src="%s" alt="Image at %s" />'''+
            '''</a>''')%(linkval, linkval, linkval)

class uri_image_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" '''+
                   '''placeholder="{{field.field_placeholder}}" '''+
                   '''value="{{field.field_value}}" />'''
        )
        return

    def render(self, context):
        """
        Render image URI for editing
        """
        return self._template.render(context)

def get_uri_image_renderer():
    """
    Return field renderer object for token list values
    """
    return RenderFieldValue(
        view_renderer=uri_image_view_renderer(), 
        edit_renderer=uri_image_edit_renderer(),
        )

# End.
