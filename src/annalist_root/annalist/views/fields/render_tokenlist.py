"""
Renderer and value mapper for field consisting of a list of simple token values.

Simple tokens may not contain whitespace.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.http        import HttpResponse
from django.template    import Template, Context

class RenderTokenList(object):
    """
    Render class for token list field
    """

    def __init__(self):
        """
        Creates a renderer object for a simple text field
        """
        super(RenderTokenList, self).__init__()
        self.responsetemplate = Template("""
            <!-- views/fields/render_tokenlist.py -->
            <div class="{{field.field_placement.field}}">
                <div class="row">
                    <div class="view_label {{field.field_placement.label}}">
                        <p>{{field.field_label}}</p>
                    </div>
                    <div class="{{field.field_placement.value}}">
                        <!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->
                        <input type="text" size="64" name="{{repeat.repeat_prefix}}{{field.field_name}}" 
                               placeholder="{{field.field_placeholder}}"
                               value="{{field.field_value_encoded}}"/>
                    </div>
                </div>
            </div>
            """)
        return

    def __str__(self):
        return "RenderTokenList" # %self.render(Context({}))

    def render(self, context):
        """
        Renders a token list field
        """
        responsebody = self.responsetemplate.render(context)
        # log.info("RenderTokenList.render: %s"%responsebody)
        return responsebody

    def encode(self, field_value):
        """
        Encodes a token list as a simple string of space-separated values
        """
        return " ".join(field_value)

    def decode(self, field_value):
        """
        Decodes a string of space-separated tokens as a list of tokens
        """
        return field_value.split()


# End.
