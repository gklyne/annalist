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

from annalist.views.fields.bound_field  import bound_field

edit = (
    { 'repeatgroup_head':
        """
        <!-- views.fields.render_repeatgroup.edit_template -->
        <div class="small-12 columns">
          <p class="caption">{{field.field_label}}</p>
        </div>"""
    , 'repeatgroup_body':
        # Context values:
        #   repeat_index - index of value presented
        #   repeat_bound_fields is list of bound fields to process for this value
        """
        <div class="small-12 columns">
          <div class="row selectable">
            <div class="small-2 columns">
              {% if auth_config %}
              <input type="checkbox" name="{{field.group_id}}__select_fields"
                     value="{{repeat_index}}" class="right" />
              {% endif %}
            </div>
            <div class="small-10 columns">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_edit with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>"""
    , 'repeatgroup_tail':
        """
        <div class="small-12 columns">
          <div class="row">
            <div class="small-2 columns">
              &nbsp;
            </div>
            <div class="small-10 columns">
              <input type="submit" name="{{field.group_id}}__remove" 
                     value="{{field.group_delete_label}}" />
              <input type="submit" name="{{field.group_id}}__add"    
                     value="{{field.group_add_label}}" />
            </div>
          </div>
        </div> """
    })

view = (
    { 'repeatgroup_head':
        """
        <!-- views.fields.render_repeatgroup.view_template -->
        <div class="small-12 columns">
          <p class="caption">{{field.field_label}}</p>
        </div>"""
    , 'repeatgroup_body':
        # Context values:
        #   repeat_id - id of repeated group
        #   repeat_index - index of value presented
        #   repeat_prefix - index of value presented
        #   repeat_bound_fields is list of bound fields to process for this value
        """
        <div class="small-12 columns">
          <div class="row selectable">
            <div class="small-12 columns">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_view with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>"""
    , 'repeatgroup_tail':
        """"""
    })

item = (
    { 'repeatgroup_head':
        """"""
    , 'repeatgroup_body':
        # Context values:
        #   repeat_id - id of repeated group
        #   repeat_index - index of value presented
        #   repeat_prefix - index of value presented
        #   repeat_bound_fields is list of bound fields to process for this value
        """
        <tr class="select_row">
          {% for f in repeat_bound_fields %}
          <!-- f.entity_link {{f.entity_link}} -->
          <!-- f.entity_type_link {{f.entity_type_link}} -->
          <!-- f.entity_link_continuation {{f.entity_link_continuation}} -->
          <!-- f.entity_type_link_continuation {{f.entity_type_link_continuation}} -->
          {% include f.field_render_item with field=f %}
          {% endfor %}
          <td class="select_row">
            <input type="checkbox" name="entity_select" 
                   value="{{repeat_entity.entity_type_id}}/{{repeat_entity.entity_id}}" />
          </td>
        </tr>
        """
    , 'repeatgroup_tail':
        """"""
    })

class RenderRepeatGroup(object):
  """
  Render class for repeated field group
  """

  def __init__(self, templates=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object for a simple text field
    """
    super(RenderRepeatGroup, self).__init__()
    assert templates is not None, "RenderRepeatGroup template must be supplied (.edit, .view or .item)"
    self._template_head = Template(templates['repeatgroup_head'])
    self._template_body = Template(templates['repeatgroup_body'])
    self._template_tail = Template(templates['repeatgroup_tail'])
    return

  def __str__(self):
    return "RenderRepeatGroup" # %self.render(Context({}))

  def render(self, context):
    """
    Renders a repeating field group.

    `context`   is a dictionary-like object that provides information for the
                rendering operation.

    returns a string that is incorporated into the resulting web page.

    `context['field']` is a `bound_field` value that combines the field 
    definition, entity values and additional context information.  
    The entity value is either the entire entity that is currently 
    being rendered, or a list of repeated values that are each formatted
    using the supplied body template.
    """
    response_parts  = [self._template_head.render(context)]
    repeat_index = 0
    # @@TODO: devise cleaner mechanism
    x = context['field']['_extras']
    for g in context['field']['field_value']:
        r = [ bound_field(f, g, extras=x) for f in context['field']['group_field_descs'] ]
        repeat_id = context.get('repeat_prefix', "") + context['field']['group_id']
        repeat_dict = (
            { 'repeat_id':            repeat_id
            , 'repeat_index':         str(repeat_index)
            , 'repeat_prefix':        repeat_id+("__%d__"%repeat_index)
            , 'repeat_bound_fields':  r
            , 'repeat_entity':        g
            })
        # @@TODO: rationalize this to eliminate 'repeat' item
        #         (currently included for compatibility with old field renderers)
        with context.push(repeat_dict, repeat=repeat_dict):
            response_parts.append(self._template_body.render(context))
        repeat_index += 1
    response_parts.append(self._template_tail.render(context))
    return "".join(response_parts)

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
