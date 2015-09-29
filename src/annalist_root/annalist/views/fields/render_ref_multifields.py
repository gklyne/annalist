"""
Renderer and value mapper for multiple fields displayed from a referenced entity.

The edit renderer provides for selection of the referenced entity, and stores its
id as the field value.

The view renderer displays a number of fields from the referenced entity corresponding
to a field group specified in the field definition.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import traceback
import logging
log = logging.getLogger(__name__)

from django.http            import HttpResponse
from django.template        import Template, Context

from annalist.exceptions    import TargetIdNotFound_Error, TargetEntityNotFound_Error

from annalist.views.fields.render_select    import edit_select, Select_edit_renderer, SelectValueMapper
from annalist.views.fields.bound_field      import bound_field
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value
    )

col_head_view = (
    { 'head':
        """\n"""+
        """<!-- views.fields.render_ref_multifield.col_head_view head (mode:{{render_mode}}) -->\n"""
    , 'body':
        """<!-- views.fields.render_ref_multifield.col_head_view body (mode:{{render_mode}}) -->\n"""+
        """<div class="view-grouprow col-head row">\n"""+
        """  {% for f in group_bound_fields %}"""+
        """    {% include f.field_render_mode with field=f %}"""+
        """  {% endfor %}"""+
        """</div>\n"""
    , 'tail':
        """<!-- views.fields.render_ref_multifield.col_head_view tail (mode:{{render_mode}}) -->\n"""
    })

view_multifield = (
    { 'head':
        """\n"""+
        """<!-- views.fields.render_ref_multifield.view_multifield head (mode:{{render_mode}}) -->\n"""
    , 'body':
        """<!-- views.fields.render_ref_multifield.view_multifield body (mode:{{render_mode}}) -->\n"""+
        """<div class="view-grouprow row">\n"""+
        """  {% for f in group_bound_fields %}"""+
        """    {% include f.field_render_mode with field=f %}"""+
        """  {% endfor %}"""+
        """</div>\n"""
    , 'tail':
        """<!-- views.fields.render_ref_multifield.view_multifield tail (mode:{{render_mode}})-->
        """
    })

_alt_view_multifield = (
    { 'head':
        """\n"""+
        """<!-- views.fields.render_ref_multifield.view_multifield head (mode:{{render_mode}}) -->\n"""
    , 'body':
        """<!-- views.fields.render_ref_multifield.view_multifield body (mode:{{render_mode}}) -->\n"""+
        """<div class="view-grouprow row">\n"""+
        """  {% for f in group_bound_fields %}"""+
        """    {% include f.field_render_colview with field=f %}"""+
        """  {% endfor %}"""+
        """</div>\n"""
    , 'tail':
        """<!-- views.fields.render_ref_multifield.view_multifield tail (mode:{{render_mode}})-->
        """
    })

target_blank = """<span class="value-blank">%s</span>"""

target_missing = """<span class="value-missing">%s</span>"""

#   ----------------------------------------------------------------------------
#
#   Multi-field reference field label renderer for viewing
#
#   ----------------------------------------------------------------------------

class RenderMultiFields_label(object):
  """
  Render class for a field group labels in a referenced entity.
  """

  def __init__(self, templates=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object
    """
    # log.info("RenderMultiFields_label: __init__ %r"%(templates))
    super(RenderMultiFields_label, self).__init__()
    assert templates is not None, "RenderMultiFields_label template must be supplied"
    self._template_head  = Template(templates.get('head', ""))
    self._template_body  = Template(templates.get('body', "@@missing body@@"))
    self._template_tail  = Template(templates.get('tail', ""))
    return

  def __str__(self):
    return "RenderMultiFields_label %r"%(self._template_head)
    # return "RenderMultiFields_label %r, %s"%(self._template_head,self.render(context))

  def render(self, context):
    """
    Renders column labels for multiple fields in a group

    `context`   is a dictionary-like object that provides information for the
                rendering operation.  `context['field']` contains the group 
                field descriptions.

    returns a string that is incorporated into the resulting web page.
    """
    # log.info("RenderMultiFields_label.render (mode: %s)"%context['render_mode'])
    try:
        # log.info("RenderMultiFields_label.render field: %r"%(context['field'],))
        # log.info("RenderMultiFields_label.render descs: %r"%(context['field']['group_field_descs'],))
        group_fields = [ f for f in context['field']['group_field_descs'] ]
        group_dict = (
            { 'group_bound_fields':  group_fields
            })
        # log.info("RenderMultiFields_label.render group_dict: %r"%(group_dict))
        with context.push(group_dict):
            response_parts = [self._template_head.render(context)]
            response_parts.append(self._template_body.render(context))
            response_parts.append(self._template_tail.render(context))
    except TargetIdNotFound_Error as e:
        response_parts = [ target_blank%str(e) ]
    except TargetEntityNotFound_Error as e:        
        response_parts = [ target_missing%str(e) ]
    except Exception as e:
        log.exception("Exception in RenderMultiFields_label.render")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        response_parts = (
            ["Exception in RenderMultiFields_label.render"]+
            [repr(e)]+
            traceback.format_exception(ex_type, ex, tb)+
            ["***RenderMultiFields_label.render***"]
            )
        del tb
    return "".join(response_parts)

#   ----------------------------------------------------------------------------
#
#   Multi-field reference field value renderer for viewing
#
#   ----------------------------------------------------------------------------

class RenderMultiFields_value(object):
  """
  Render class for field values in a referenced entity.
  """

  def __init__(self, templates=None):
    # Later, may introduce a template_file= option to read from templates directory
    """
    Creates a renderer object
    """
    # log.info("RenderMultiFields_value: __init__ %r"%(templates))
    super(RenderMultiFields_value, self).__init__()
    assert templates is not None, "RenderMultiFields_value template must be supplied (.edit or .view)"
    self._template_head  = Template(templates.get('head', ""))
    self._template_body  = Template(templates.get('body', "@@missing body@@"))
    self._template_tail  = Template(templates.get('tail', ""))
    return

  def __str__(self):
    return "RenderMultiFields_value %r"%(self._template_head)
    # return "RenderMultiFields_value %r, %s"%(self._template_head,self.render(context))

  def render(self, context):
    """
    Renders column values for multiple fields in a group

    `context`   is a dictionary-like object that provides information for the
                rendering operation.  `context['field']` contains the group 
                field descriptions.

    returns a string that is incorporated into the resulting web page.
    """
    # log.info("RenderMultiFields_value.render (mode: %s)"%context['render_mode'])
    try:
        # log.info("RenderMultiFields_value.render field: %r"%(context['field'],))
        # log.info("RenderMultiFields_value.render descs: %r"%(context['field']['group_field_descs'],))
        target_vals = context['field']['target_value']
        extras      = context['field']['context_extra_values']
        log.debug("RenderMultiFields_value.render target_vals: %r"%(target_vals))
        group_fields = [ 
            bound_field(f, target_vals, context_extra_values=extras) 
            for f in context['field']['group_field_descs'] 
            ]
        group_dict = (
            { 'group_bound_fields':  group_fields
            , 'group_entity':        target_vals
            })
        # log.info("RenderMultiFields_value.render group_dict: %r"%(group_dict))
        response_parts = [self._template_head.render(context)]
        with context.push(group_dict):
            response_parts.append(self._template_body.render(context))
        response_parts.append(self._template_tail.render(context))
    except TargetIdNotFound_Error as e:
        response_parts = [ target_blank%str(e) ]
    except TargetEntityNotFound_Error as e:        
        response_parts = [ target_missing%str(e) ]
    except Exception as e:
        log.exception("Exception in RenderMultiFields_value.render")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        response_parts = (
            ["Exception in RenderMultiFields_value.render"]+
            [repr(e)]+
            traceback.format_exception(ex_type, ex, tb)+
            ["***RenderMultiFields_value.render***"]
            )
        del tb
    return "".join(response_parts)

#   ----------------------------------------------------------------------------
#
#   Multi-field reference value mapping
#
#   ----------------------------------------------------------------------------

class RefMultifieldValueMapper(SelectValueMapper):
    """
    Value mapper class for multifield reference

    Inherits all logic from SelectvalueMapper.
    """
    pass

#   ----------------------------------------------------------------------------
#
#   Return render objects for multiple field reference fields
#
#   ----------------------------------------------------------------------------

def get_ref_multifield_renderer():
    """
    Return field renderer object for value selector (with '+' button)
    """
    r = RenderFieldValue(
        col_head_view_renderer=RenderMultiFields_label(col_head_view),
        view_renderer=RenderMultiFields_value(view_multifield),
        edit_renderer=Select_edit_renderer(edit_select)
        )
    return r

# End.
