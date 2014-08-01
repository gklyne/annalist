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

class RenderText(object):
    """
    Render class for simple text entry field
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
        """
        responsetemplate = Template("""
            <div class="row">
                <div class="small-12 medium-3 columns">
                    <p>{{field_label}}</p>
                </div>
                <div class="small-12 medium-9 columns">
                    <input type="text" size="64" name="{{field_name}}" value="{{field_value}}"/>
                </div>
            </div>
            """)
        responsebody = responsetemplate.render(context)
        return responsebody

# End.
