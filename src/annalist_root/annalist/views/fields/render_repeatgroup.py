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
    <!-- views.fields.render_repeatgroup.edit_template -->
    <div class="small-12 columns">
      <p class="caption">{{field.group_label}}</p>
    </div>

    {% for f in field.group_fields %}
      <div class="small-12 columns">
        <div class="row selectable">
          <div class="small-2 columns">
            {% if auth_config %}
            <input type="checkbox" name="{{field.group_id}}__select_fields"
                   value="{{f.repeat_index}}" class="right" />
            {% endif %}
          </div>
          <div class="small-10 columns">
            {% for field in f.fields %}
            {% include field.field_render_edit %}
            {% endfor %}
          </div>
        </div>
      </div>
    {% endfor %}

    <div class="small-12 columns">
      <div class="row">
        <div class="small-2 columns">
          &nbsp;
        </div>
        <div class="small-10 columns">
          <input type="submit" name="{{field.group_id}}__remove" 
                 value="{{field.repeat_label_delete}}" />
          <input type="submit" name="{{field.group_id}}__add"    
                 value="{{field.repeat_label_add}}" />
        </div>
      </div>
    </div>
    """)

view = ("""
    <!-- views.fields.render_repeatgroup.view_template -->
    <div class="{{field.field_placement.field}}">
        <div class="row">
            <div class="view_label {{field.field_placement.label}}">
                <p>{{field.field_label}}</p>
            </div>
            <div class="{{field.field_placement.value}}">
                <p>{{field.field_value_encoded}}</p>
            </div>
        </div>
    </div>
    """)

item = ("""
    <!-- views.fields.render_repeatgroup.view_template -->
    <td class="{{field.field_placement.field}}">
    {{ field.field_value_encoded|default:"&nbsp;" }}
    </td>
    """)

class RenderRepeatGroup(object):
  """
  Render class for repeated field group
  """

  def __init__(self, template=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object for a simple text field
    """
    super(RenderRepeatGroup, self).__init__()
    assert template is not None, "RenderRepeatGroup template must be supplied (.edit, .view or .item)"
    self._template = Template(template)
    return

  def __str__(self):
    return "RenderRepeatGroup" # %self.render(Context({}))

  def render(self, context):
    """
    Renders a repeating field group.

    `context`   is a dictionary-like object that provises information for the
                rendering operation.

    returns a string that is incorporated into the resulting web page.

    `context['field']` is a `bound_field` value that combines the field 
    definition, entity values and additional context information.  
    The entity values are either the entire entity that is currently 
    being rendered, or one of a set of repeated field groups, augmented
    with indexing information that can be used to generate unique 
    field names in the generated form.
    """

    # @@ 
    # Need to clarify what the incoming context looks like.
    # If the repeated entity structures have not been unrolled, then we need some 
    # distinguished value in the context to guide the process.  For normal fields, the
    # value '.field' is a bound_field value combining an entity values record with the 
    # field description.  For top level repeat structures, this can still work.  If 
    # there are nested structures then recursive calls must provide scoped/component
    # context values

    # 1. Group caption

    # 2. Iterate over groups from entity body
    #
    #    For each group, generate unique field names using group id and repeat index,
    #    and render fields:
    #    (a) render Group select checkbox (and up/down buttons in due course?)
    #    (b) for each field, render that field

    # 3. Create affordances for adding and removing groups using labels provided

    return responsebody

  # def encode(self, field_value):
  #   """
  #   Encodes a token list as a simple string of space-separated values
  #   """
  #   if isinstance(field_value, (list,tuple)):
  #     return " ".join(field_value)
  #   log.warning("encode tokenlist: supplied value is not a list or tuple")
  #   return str(field_value)

  # def decode(self, field_value):
  #   """
  #   Decodes a string of space-separated tokens as a list of tokens
  #   """
  #   return field_value.split()


# End.
