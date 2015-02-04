"""
Renderer and value mapper for Boolean value rendered as a checkbox.
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
#   Boolean checkbox value mapping
#
#   ----------------------------------------------------------------------------


class BoolCheckboxValueMapper(object):
    """
    Value mapper class for token list
    """

    @staticmethod
    def encode(data_value):
        """
        Encodes supplied data value as string
        """
        # print "data_value "+repr(data_value)
        if data_value is None:
            textval = "No"
        elif isinstance(data_value, str):
            textval = data_value
        elif isinstance(data_value, bool):
            textval = "Yes" if data_value else "No"
        else:
            textval = "Unknown Boolean "+repr(data_value)
        # print "text_value "+repr(textval)
        return textval

    @staticmethod
    def decode(field_value):
        """
        Decodes a checkbox value attribute string as a Boolean value
        """
        # print "field_value "+repr(field_value)
        return BoolCheckboxValueMapper.encode(field_value).lower() in ["yes", "true"]

#   ----------------------------------------------------------------------------
#
#   Boolean checkbox field renderers
#
#   ----------------------------------------------------------------------------

class bool_checkbox_view_renderer(object):
    def render(self, context):
        """
        Render token list for viewing.
        """
        return BoolCheckboxValueMapper.encode(get_field_value(context, None))

class bool_checkbox_edit_renderer(object):
    def __init__(self):
        self._template = Template(
            '''<input type="checkbox" '''+
                   '''name="{{repeat_prefix}}{{field.field_name}}" '''+
                   '''value="{{encoded_field_value}}"{{checked|safe}}>'''+
              '''{{field.field_label}}'''+
            '''</input>'''
            )
        return
    def render(self, context):
        """
        Render token list for editing
        """
        val     = get_field_value(context, None)
        boolval = BoolCheckboxValueMapper.decode(val)
        textval = BoolCheckboxValueMapper.encode(val)
        checked = ''' checked="checked"''' if boolval else ''''''
        with context.push(encoded_field_value=textval, checked=checked):
            result = self._template.render(context)
        return result

def get_bool_checkbox_renderer():
    """
    Return field renderer object for token list values
    """
    return RenderFieldValue(
        view_renderer=bool_checkbox_view_renderer(), 
        edit_renderer=bool_checkbox_edit_renderer(),
        )

# End.
