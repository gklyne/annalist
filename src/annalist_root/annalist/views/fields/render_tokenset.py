"""
Renderer and value mapper for field consisting of a list of simple token values.

Simple tokens may not contain whitespace.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_context_value, get_context_field_value, get_field_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Token set render support functions
#
#   ----------------------------------------------------------------------------


class TokenSetValueMapper(object):
    """
    Value mapper class for token list
    """

    @staticmethod
    def encode(field_value):
        """
        Encodes a token list as a string of space-separated values
        """
        if isinstance(field_value, (list,tuple)):
            return " ".join(field_value)
        log.warning("TokenSetValueMapper.encode tokenset: supplied value is not a list or tuple")
        return str(field_value)

    @staticmethod
    def decode(field_value):
        """
        Decodes a string of space-separated tokens as a list of tokens
        """
        return field_value.split()

#   ----------------------------------------------------------------------------
#
#   Token set field renderers
#
#   ----------------------------------------------------------------------------

class tokenset_view_renderer(object):
    def render(self, context):
        """
        Render token list for viewing.
        """
        tokenset = get_field_value(context, None)
        return TokenSetValueMapper.encode(tokenset) if tokenset else "&nbsp;"

class tokenset_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" '''+
                '''placeholder="{{field.field_placeholder}}" '''+
                '''value="{{encoded_field_value}}"/>'''
            )

    def render(self, context):
        """
        Render token list for editing
        """
        tokenset = get_field_value(context, None)
        with context.push(encoded_field_value=TokenSetValueMapper.encode(tokenset)):
            return self._template.render(context)

def get_field_tokenset_renderer():
    """
    Return field renderer object for token list values
    """
    return RenderFieldValue(
        view_renderer=tokenset_view_renderer(), 
        edit_renderer=tokenset_edit_renderer(),
        )

# End.
