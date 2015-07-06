"""
Renderer and value mapper for URI value displayed as a link.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value, get_field_view_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Link URI value mapping
#
#   ----------------------------------------------------------------------------


class URILinkValueMapper(RenderBase):
    """
    Value mapper class for token list
    """

    @classmethod
    def encode(cls, data_value):
        """
        Encodes link value as string
        """
        return data_value or ""

    @classmethod
    def decode(cls, field_value):
        """
        Decodes a URI string value as a link
        """
        return field_value or ""


#   ----------------------------------------------------------------------------
#
#   Link URI field renderers
#
#   ----------------------------------------------------------------------------

class uri_link_view_renderer(object):

    def render(self, context):
        """
        Render link for viewing.
        """
        linkval = URILinkValueMapper.encode(get_field_view_value(context, ""))
        common_prefixes = (
            [ "http://", "https://"
            , "file:///", "file://localhost/", "file://"
            , "mailto:"]
            )
        textval = linkval
        for p in common_prefixes:
            if linkval.startswith(p):
                textval = linkval[len(p):]
                break
        return '''<a href="%s" target="_blank">%s</a>'''%(linkval, textval)

class uri_link_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" '''+
                   '''placeholder="{{field.field_placeholder}}" '''+
                   '''value="{{field.field_edit_value}}" />'''
        )
        return

    def render(self, context):
        """
        Render link for editing
        """
        return self._template.render(context)

def get_uri_link_renderer():
    """
    Return field renderer object for token list values
    """
    return RenderFieldValue(
        view_renderer=uri_link_view_renderer(), 
        edit_renderer=uri_link_edit_renderer(),
        )

# End.
