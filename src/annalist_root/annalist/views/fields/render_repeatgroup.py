"""
Renderer and value mapper for field consisting of a list of simple token values.

Simple tokens may not contain whitespace.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import traceback
import logging
log = logging.getLogger(__name__)

from django.http        import HttpResponse
from django.template    import Template, Context

from annalist.views.fields.bound_field  import bound_field

view_group = (      # @@TODO rationalize (see above; not currently used)
    { 'head':
        """
        @@TODO: FIXME render_repeatgroup.view_group.head@@
        <!-- views.fields.render_repeatgroup.view_group -->
        <div class="small-12 columns">
          <p class="grouplabel">{{field.field_label}}</p>
        </div>"""
    , 'body':
        """
        @@TODO: FIXME render_repeatgroup.view_group.body@@
        <div class="small-12 columns">
          <div class="row selectable">
            <div class="small-12 columns">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_view with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>"""
    # , 'tail':
    #     """
    #     @@TODO: FIXME render_repeatgroup.view_group.tail@@
    #     """
    })

edit_group = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.edit_group -->
        <div class="small-12 columns">
          <p class="grouplabel">{{field.field_label}}</p>
        </div>"""
    , 'body':
        """
        <div class="small-12 columns">
          <div class="row selectable">
            <div class="small-2 columns checkbox-in-edit-padding">
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
    , 'tail':
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

view_listrow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.view_listrow -->
        <div class="thead row">
          <div class="small-1 columns">
            <th>&nbsp;</th>
          </div>
          <div class="small-11 columns">
            <div class="row">
              {% for f in field.group_field_descs %}
              {% include f.field_render_colhead with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="trow row select-row">
          <div class="small-1 columns">
            <input type="checkbox" class="select-box right" name="entity_select" 
                   value="{{repeat_entity.entity_type_id}}/{{repeat_entity.entity_id}}" />
          </div>
          <div class="small-11 columns">
            <div class="row">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_colview with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>
        """
    })

edit_listrow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.edit_listrow -->
        <div class="thead row">
          <div class="small-12 columns">
            <div class="row">
              <div class="small-12 columns">
                <p class="grouplabel">{{field.field_label}}</p>
              </div>
            </div>
            <div class="row">
              <div class="small-1 columns">
                <th>&nbsp;</th>
              </div>
              <div class="small-11 columns">
                <div class="row">
                  {% for f in field.group_field_descs %}
                  {% include f.field_render_colhead with field=f %}
                  {% endfor %}
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="trow row select-row">
          <div class="small-1 columns checkbox-in-edit-padding">
            <input type="checkbox" class="select-box right" name="entity_select" 
                   value="{{repeat_entity.entity_type_id}}/{{repeat_entity.entity_id}}" />
          </div>
          <div class="small-11 columns">
            <div class="row">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_coledit with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>"""
    , 'tail':
        """
        <div class="row">
          <div class="small-12 columns">
            <input type="submit" name="{{field.group_id}}__remove" 
                   value="{{field.group_delete_label}}" />
            <input type="submit" name="{{field.group_id}}__add"    
                   value="{{field.group_add_label}}" />
          </div>
        </div>"""
    })

view_grouprow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.view_grouprow -->
        <div class="row">
          <div class="small-12 medium-2 columns">
            <p class="grouplabel">{{field.field_label}}</p>
          </div>
          <div class="small-12 medium-10 columns hide-for-small-only">
            <div class="row">
              <div class="small-1 columns">
                <th>&nbsp;</th>
              </div>
              <div class="small-11 columns">
                <div class="row">
                  {% for f in field.group_field_descs %}
                  {% include f.field_render_colhead with field=f %}
                  {% endfor %}
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="row">
          <div class="small-12 medium-2 columns">
            &nbsp;
          </div>
          <div class="small-12 medium-10 columns">
            <div class="row select-row">
              <div class="small-1 columns">
                <input type="checkbox" class="select-box right"
                       name="{{field.group_id}}__select_fields"
                       value="{{repeat_index}}" />
              </div>
              <div class="small-11 columns">
                <div class="row">
                  {% for f in repeat_bound_fields %}
                  {% include f.field_render_colview with field=f %}
                  {% endfor %}
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    })

edit_grouprow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.edit_grouprow -->
        <div class="small-12 columns">
          <div class="row">
            <div class="small-12 medium-2 columns">
              <p class="grouplabel">{{field.field_label}}</p>
            </div>
            <div class="small-12 medium-10 columns hide-for-small-only">
              <div class="row">
                <div class="small-1 columns">
                  <th>&nbsp;</th>
                </div>
                <div class="small-11 columns">
                  <div class="row">
                    {% for f in field.group_field_descs %}
                    {% include f.field_render_colhead with field=f %}
                    {% endfor %}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="small-12 columns">
          <div class="row">
            <div class="small-12 medium-2 columns hide-for-small-only">
              &nbsp;
            </div>
            <div class="small-12 medium-10 columns">
              <div class="trow row select-row">
                <div class="small-1 columns checkbox-in-edit-padding">
                  <input type="checkbox" class="select-box right"
                         name="{{field.group_id}}__select_fields"
                         value="{{repeat_index}}" />
                </div>
                <div class="small-11 columns">
                  <div class="row">
                    {% for f in repeat_bound_fields %}
                    {% include f.field_render_coledit with field=f %}
                    {% endfor %}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    , 'tail':
        """
        <div class="small-12 columns">
          <div class="row">
            <div class="small-12 medium-2 columns">
              &nbsp;
            </div>
            <div class="small-12 medium-10 columns">
              <input type="submit" name="{{field.group_id}}__remove" 
                     value="{{field.group_delete_label}}" />
              <input type="submit" name="{{field.group_id}}__add"    
                     value="{{field.group_add_label}}" />
            </div>
          </div>
        </div>"""
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
    # log.info("RenderRepeatGroup: __init__ %r"%(templates))
    super(RenderRepeatGroup, self).__init__()
    assert templates is not None, "RenderRepeatGroup template must be supplied (.edit, .view or .item)"
    self._template_head = Template(templates.get('head', ""))
    self._template_body = Template(templates.get('body', "@@missing body@@"))
    self._template_tail = Template(templates.get('tail', ""))
    return

  def __str__(self):
    # Minimal context for rendering repeat group...
    # context = Context(
    #   { 'field':
    #     { 'context_extra_values': {}
    #     , 'field_value':
    #       [ { 'entity_id': "test_id"
    #         , 'test_uri':  "test value 1"
    #         }
    #       , { 'entity_id': "test_id"
    #         , 'test_uri':  "test value 2"
    #         }
    #       ]
    #     , 'group_field_descs':
    #       [ { 'field_property_uri': "test_uri"
    #         , 'field_id':           "test_field_id"
    #         }
    #       ]
    #     , 'group_id': "test_group_id"
    #     }
    #   })
    return "RenderRepeatGroup %r"%(self._template_head)
    # return "RenderRepeatGroup %r, %s"%(self._template_head,self.render(context))

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
    log.info("RenderRepeatGroup.render")
    try:
        # log.info("RenderRepeatGroup.render field: %r"%(context['field'],))
        # log.info("RenderRepeatGroup.render descs: %r"%(context['field']['group_field_descs'],))
        response_parts = [self._template_head.render(context)]
        repeat_index = 0
        extras       = context['field']['context_extra_values']
        for g in context['field']['field_value']:
            log.debug("RenderRepeatGroup.render field_val: %r"%(g))
            r = [ bound_field(f, g, context_extra_values=extras) 
                  for f in context['field']['group_field_descs'] ]
            repeat_id = context.get('repeat_prefix', "") + context['field']['group_id']
            repeat_dict = (
                { 'repeat_id':            repeat_id
                , 'repeat_index':         str(repeat_index)
                , 'repeat_prefix':        repeat_id+("__%d__"%repeat_index)
                , 'repeat_bound_fields':  r
                , 'repeat_entity':        g
                })
            # log.info("RenderRepeatGroup.render repeat_dict: %r"%(repeat_dict))
            with context.push(repeat_dict):
                response_parts.append(self._template_body.render(context))
            repeat_index += 1
        response_parts.append(self._template_tail.render(context))
    except Exception as e:
        log.exception("Exception in RenderRepeatGroup.render")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        response_parts = (
            ["Exception in RenderRepeatGroup.render"]+
            [repr(e)]+
            traceback.format_exception(ex_type, ex, tb)+
            ["***RenderRepeatGroup.render***"]
            )
        del tb
    return "".join(response_parts)

# End.
