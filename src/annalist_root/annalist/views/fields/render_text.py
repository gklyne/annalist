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

class RenderText(RenderBase):
    """
    Render class for simple text entry field.
    """

    def __init__(self):
        """
        Creates a renderer object for a simple text field
        """
        super(RenderText, self).__init__()
        return

    def render(self, context):
        """
        Renders a simple text field.

        See also:
            http://stackoverflow.com/questions/1480588/input-size-vs-width
        """
        responsetemplate = Template("""
            <!-- views/fields/render_text.py -->
            <div class="{{field.field_placement.field}}">
                <div class="row">
                    <div class="view_label {{field.field_placement.label}}">
                        <p>{{field.field_label}}</p>
                    </div>
                    <div class="{{field.field_placement.value}}">
                        <input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" 
                               placeholder="{{field.field_placeholder}}"
                               value="{{field.field_value}}"/>
                    </div>
                </div>
            </div>
            """)
        responsebody = responsetemplate.render(context)
        return responsebody

# End.
