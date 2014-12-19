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

edit = ("""
    <!-- views.fields.render_tokenset.edit -->
    <div class="{{field.field_placement.field}}">
      <div class="row">
        <div class="view-label {{field.field_placement.label}}">
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

view = ("""
    <!-- views.fields.render_tokenset.view -->
    <div class="{{field.field_placement.field}}">
        <div class="row">
            <div class="view-label {{field.field_placement.label}}">
                <p>{{field.field_label}}</p>
            </div>
            <div class="{{field.field_placement.value}}">
                <p>{{field.field_value_encoded}}</p>
            </div>
        </div>
    </div>
    """)

item = (
    """<div class="view-label {{field.field_placement.field}}">"""+
    """  {{ field.field_value_encoded|default:"&nbsp;" }}"""+
    """</div>"""
    )

class RenderTokenSet(object):
  """
  Render class for token list field
  """

  def __init__(self, template=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object for a string of space-separated values
    """
    super(RenderTokenSet, self).__init__()
    assert template is not None, "RenderTokenSet template must be supplied (.edit, .view or .item)"
    self._template = Template(template)
    return

  def __str__(self):
    return "RenderTokenSet" # %self.render(Context({}))

  def render(self, context):
    """
    Renders a token list field
    """
    responsebody = self._template.render(context)
    # log.info("RenderTokenSet.render: %s"%responsebody)
    return responsebody

  def encode(self, field_value):
    """
    Encodes a token list as a string of space-separated values
    """
    if isinstance(field_value, (list,tuple)):
      return " ".join(field_value)
    log.warning("encode tokenlist: supplied value is not a list or tuple")
    return str(field_value)

  def decode(self, field_value):
    """
    Decodes a string of space-separated tokens as a list of tokens
    """
    return field_value.split()


# End.
