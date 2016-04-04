"""
Renderer and value mapper for a group of fields repeated over a list of values.
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

from annalist.exceptions                import Annalist_Error

from annalist.views.fields.bound_field  import bound_field

from render_fieldvalue  import (
    RenderFieldValue,
    TemplateWrapValueRenderer, 
    ModeWrapValueRenderer
    )

#   ------------------------------------------------------------
#   Local data values
#   ------------------------------------------------------------

view_group = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.view_group -->
        <div class="small-12 columns">
          <div class="row">
            <div class="group-label small-2 columns">
              <span>{{field.field_label}}</span>
            </div>
            <div class="group-placeholder small-10 columns">
              {{field.field_placeholder}}
            </div>
          </div>
        </div>"""
    , 'body':
        """
        <div class="group-row small-12 columns">
          <div class="row">
            <div class="small-2 columns">
              &nbsp;
            </div>
            <div class="small-10 columns">
              {% for f in repeat_bound_fields %}
                <div class="view-group row">
                  {% include f.field_render_label_view with field=f %}
                </div>
              {% endfor %}
            </div>
          </div>
        </div>"""
    # , 'tail':
    #     """
    #     """
    })

edit_group = (
    { 'head':
        """<!-- views.fields.render_repeatgroup.edit_group -->
        <div class="small-12 columns"{{field.field_tooltip|safe}}>
          <div class="row">
            <div class="group-label small-2 columns">
              <span>{{field.field_label}}</span>
            </div>
            <div class="group-placeholder small-10 columns">
              {{field.field_placeholder}}
            </div>
          </div>
        </div>"""
    , 'body':
        """
        <div class="group-row small-12 columns"{{field.field_tooltip|safe}}>
          <div class="row selectable">
            <div class="small-2 columns checkbox-in-edit-padding">
              {% if auth_config %}
              <input type="checkbox" name="{{field.group_id}}__select_fields"
                     value="{{repeat_index}}" class="right" />
              {% endif %}
            </div>
            <div class="small-10 columns">
              {% for f in repeat_bound_fields %}
                <div class="edit-group row">
                  {% include f.field_render_label_edit with field=f %}
                </div>
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
              <input type="submit" name="{{field.group_id}}__up"
                     value="Move &#x2b06;" />
              <input type="submit" name="{{field.group_id}}__down"
                     value="Move &#x2b07;" />
            </div>
          </div>
        </div>"""
    })

view_grouprow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.view_grouprow -->
        <div class="small-12 columns">
          <div class="row">
            <div class="group-label small-12 medium-2 columns">
              <span>{{field.field_label}}</span>
            </div>
            <div class="small-12 medium-10 columns hide-for-small-only">
              <div class="row">
                <div class="small-12 columns">
                  <div class="view-grouprow col-head row">
                    {% for f in field.group_field_descs %}
                    {% include f.field_render_colhead_view with field=f %}
                    {% endfor %}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    , 'head_empty':
        """
        <!-- views.fields.render_repeatgroup.view_grouprow (empty list) -->
        <div class="small-12 columns">
          <div class="row">
            <div class="group-label small-12 medium-2 columns">
              <span>{{field.field_label}}</span>
            </div>
            <div class="group-placeholder small-12 medium-10 columns">
              <span>(None)</span>
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="small-12 columns">
          <div class="row">
            <div class="small-12 medium-2 columns">
              &nbsp;
            </div>
            <div class="small-12 medium-10 columns">
              <div class="row select-row">
                <div class="small-12 columns">
                  <div class="view-grouprow row">
                    {% for f in repeat_bound_fields %}
                    {% include f.field_render_colview with field=f %}
                    {% endfor %}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        """
    # , 'tail':
    #     """
    #     """
    })

edit_grouprow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.edit_grouprow -->
        <div class="small-12 columns"{{field.field_tooltip|safe}}>
          <div class="row">
            <div class="group-label small-12 medium-2 columns">
              <span>{{field.field_label}}</span>
            </div>
            <div class="small-12 medium-10 columns hide-for-small-only">
              <div class="row">
                <div class="small-1 columns">
                  &nbsp;
                </div>
                <div class="small-11 columns">
                  <div class="edit-grouprow col-head row">
                    {% for f in field.group_field_descs %}
                    {% include f.field_render_colhead_edit with field=f %}
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
              <div class="tbody row select-row">
                <div class="small-1 columns checkbox-in-edit-padding">
                  <input type="checkbox" class="select-box right"
                         name="{{field.group_id}}__select_fields"
                         value="{{repeat_index}}" />
                </div>
                <div class="small-11 columns">
                  <div class="edit-grouprow row">
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
            <div class="group-buttons small-12 medium-10 columns">
              <div class="row">
                <div class="small-1 columns">
                  &nbsp;
                </div>
                <div class="small-11 columns">
                  <input type="submit" name="{{field.group_id}}__remove" 
                         value="{{field.group_delete_label}}" />
                  <input type="submit" name="{{field.group_id}}__add"    
                         value="{{field.group_add_label}}" />
                  <input type="submit" name="{{field.group_id}}__up"
                         value="Move &#x2b06;" />
                  <input type="submit" name="{{field.group_id}}__down"
                         value="Move &#x2b07;" />
                </div>
              </div>
            </div>
          </div>
        </div>"""
    })

# Used for rendering lists of entities via the EntityList view class
view_listrow = (
    { 'head':
        """
        <!-- views.fields.render_repeatgroup.view_listrow -->
        <div class="thead row">
          <div class="small-1 columns">
            &nbsp;
          </div>
          <div class="small-11 columns">
            <div class="view-listrow col-head row">
              {% for f in field.group_field_descs %}
              {% include f.field_render_colhead with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>
        """
    , 'body':
        """
        <div class="tbody row select-row">
          <div class="small-1 columns">
            <input type="checkbox" class="select-box right" name="entity_select" 
                   value="{{repeat_entity.entity_type_id}}/{{repeat_entity.entity_id}}" />
          </div>
          <div class="small-11 columns">
            <div class="view-listrow row">
              {% for f in repeat_bound_fields %}
              {% include f.field_render_view with field=f %}
              {% endfor %}
            </div>
          </div>
        </div>
        """
    })

view_group_col = (
    { 'head':
        """
        {% for f in field.group_field_descs %}
        {% include f.field_render_label with field=f %}
        {% endfor %}
        """
    , 'body':
        """
        {% for f in repeat_bound_fields %}
        {% include f.field_render_view with field=f %}
        {% endfor %}
        """
    # , 'tail':
    #     """
    #     """
    })

#   ------------------------------------------------------------
#   Repeat group render class
#   ------------------------------------------------------------

class RenderRepeatGroup(object):
    """
    Render class for repeated field group
    """

    def __init__(self, templates=None):
        """
        Creates a renderer object for a repeating group field
        """
        # Later, may introduce a template_file= option to read from templates directory
        # log.info("RenderRepeatGroup: __init__ %r"%(templates))
        super(RenderRepeatGroup, self).__init__()
        assert templates is not None, "RenderRepeatGroup template must be supplied (.edit, .view or .item)"
        self._template_head  = Template(templates.get('head', ""))
        self._template_body  = Template(templates.get('body', "@@missing body@@"))
        self._template_tail  = Template(templates.get('tail', ""))
        self._template_empty = self._template_head
        if 'head_empty' in templates:
            self._template_empty = Template(templates['head_empty'])
        return

    def __str__(self):
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
        being rendered, or sub-element containing a list of repeated values that 
        are each formatted using the supplied body template.
        """
        # log.info("RenderRepeatGroup.render")
        try:
            # log.info("RenderRepeatGroup.render field: %r"%(context['field'],))
            # log.info("RenderRepeatGroup.render descs: %r"%(context['field']['group_field_descs'],))
            value_list     = context['field']['field_value']
            if len(value_list) > 0:
                response_parts = [self._template_head.render(context)]
                repeat_index = 0
                extras       = context['field']['context_extra_values']
                for g in value_list:
                    # log.debug("RenderRepeatGroup.render field_val: %r"%(g))
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
            else:
                # Empty list
                response_parts = [self._template_empty.render(context)]
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

    def render_mode(self):
        """
        Returns a renderer object that renders whatever is required for the 
        current value of "render_mode" in the view context.
        """
        return self
        # return RenderRepeatGroup(view_group_col)

    #@@
    # class RenderModeRepeatGroup(object):
    #     """
    #     Render class for a repeated field group that renders according to the "render_mode"
    #     value inthe supplied context.
    #     """
    #     def __init__(self, baserenderer):
    #         self._baserenderer = baserenderer
    #         return
    #     def render(self, context):
    #         """
    #         Renders a repeat group according to render_mode.
    #         """
    #         value_list = context['field']['field_value']
    #         mode       = context['render_mode']
    #         if mode in ["col_head", "col_head_view", "col_head_edit"]:
    #             # Render row headings
    #         elif mode in ["col_view", "col_edit"]:
    #             # render row value
    #         else
    #             response = self._baserenderer.render(context)
    #         return response
    #@@


#   ------------------------------------------------------------
#   Repeat group renderer factory class and functions
#   ------------------------------------------------------------

class RenderGroupFieldValue(RenderFieldValue):
    """
    Return field render factory for a repeated group based on 
    the supplied render value objects.
    """
    def __init__(self, render_type, view_renderer=None, edit_renderer=None):
        """
        Creates a renderer factory for a repeating value field.

        view_renderer   is a render object that formats values for viewing
        edit_renderer   is a render object that formats value editing widgets

        Methods provided return composed renderers for a variety of contexts.
        """
        super(RenderGroupFieldValue, self).__init__(render_type,
            view_renderer=view_renderer, 
            edit_renderer=edit_renderer
            )
        # Override view/edit renderers to not use wrapper.
        self._render_view       = ModeWrapValueRenderer("view", self._view_renderer)
        self._render_edit       = ModeWrapValueRenderer("edit", self._edit_renderer)
        #@@TODO: remove labelling from templates instead?
        self._render_label_view = ModeWrapValueRenderer("view", self._view_renderer)
        self._render_label_edit = ModeWrapValueRenderer("edit", self._edit_renderer)
        self._render_col_view   = ModeWrapValueRenderer("view", self._view_renderer)
        self._render_col_edit   = ModeWrapValueRenderer("edit", self._edit_renderer)
        return

    # def label_view(self):
    #     log.warning("RepeatGroup renderer has no label_view method")
    #     raise Annalist_Error("RepeatGroup renderer has no label_view method")

    # def label_edit(self):
    #     log.warning("RepeatGroup renderer has no label_edit method")
    #     raise Annalist_Error("RepeatGroup renderer has no label_edit method")

    # def col_head(self):
    #     log.warning("RepeatGroup renderer has no col_head method")
    #     raise Annalist_Error("RepeatGroup renderer has no col_head method")

    # def col_head_view(self):
    #     log.warning("RepeatGroup renderer has no col_head_view method")
    #     raise Annalist_Error("RepeatGroup renderer has no col_head_view method")

    # def col_head_edit(self):
    #     log.warning("RepeatGroup renderer has no col_head_edit method")
    #     raise Annalist_Error("RepeatGroup renderer has no col_head_edit method")

    # def col_view(self):
    #     log.warning("RepeatGroup renderer has no col_view method")
    #     raise Annalist_Error("RepeatGroup renderer has no col_view method")

    # def col_edit(self):
    #     log.warning("RepeatGroup renderer has no col_edit method")
    #     raise Annalist_Error("RepeatGroup renderer has no col_edit method")


def get_repeatgroup_renderer():
    """
    Return field renderer object for RepeatGroup (labeled fields)
    """
    return RenderGroupFieldValue("repeatgroup",
        view_renderer=RenderRepeatGroup(view_group),
        edit_renderer=RenderRepeatGroup(edit_group)
        )

def get_repeatgrouprow_renderer():
    """
    Return field renderer object for RepeatGroup as row (col headier labels)
    """
    return RenderGroupFieldValue("repeatgrouprow",
        view_renderer=RenderRepeatGroup(view_grouprow),
        edit_renderer=RenderRepeatGroup(edit_grouprow)
        )

def get_repeatlistrow_renderer():
    """
    Return field renderer object for RepeatGroup as list (col header labels)
    """
    return RenderGroupFieldValue("repeatlistrow",
        view_renderer=RenderRepeatGroup(view_listrow),
        edit_renderer=Template("@@repeatlistrow_renderer cannot be used for editing@@")
        )

# End.
