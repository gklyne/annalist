"""
Renderer for simple text field
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.http        import HttpResponse
from django.template    import Template

from annalist.views.fields.render_base  import RenderBase

#   ----------------------------------------------------------------------------
#
#   Text value mapping
#
#   ----------------------------------------------------------------------------

class TextValueMapper(RenderBase):
    """
    Value mapper for simple text entry field.
    """

    def __init__(self):
        """
        Creates a renderer object for a simple text field
        """
        super(TextValueMapper, self).__init__()
        return

    # encode, decode methods default to RenderBase; i.e. identity mappings


#   ----------------------------------------------------------------------------
#
#   Text field renderers
#
#   ----------------------------------------------------------------------------

class text_view_renderer(object):

    def render(self, context):
        """
        Renders a simple text field for viewing
        """
        responsetemplate = Template("""
            <!-- views/fields/render_text.py:text_view_renderer -->
            <span>{{ field.field_value|default:"&nbsp;" }}</span>
            """)
        responsebody = responsetemplate.render(context)
        return responsebody

class text_edit_renderer(object):

    def render(self, context):
        """
        Renders a simple text field.

        See also:
            http://stackoverflow.com/questions/1480588/input-size-vs-width
        """
        responsetemplate = Template("""
            <!-- views/fields/render_text.py:text_edit_renderer -->
            <input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" 
                   placeholder="{{field.field_placeholder}}"
                   value="{{field.field_value}}" />
            """)
        responsebody = responsetemplate.render(context)
        return responsebody

def get_text_renderer():
    """
    Return field renderer object for text values
    """
    return RenderFieldValue("text",
        view_renderer=text_view_renderer(), 
        edit_renderer=text_edit_renderer(),
        )

# End.
