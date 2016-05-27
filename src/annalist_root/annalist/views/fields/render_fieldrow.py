"""
Renderer and value mapper for multiple fields displayed from a referenced entity.

The renderer displays a number of fields from the referenced entity as a single 
row, wrapped in a row <div> to force the fields to a new row.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import traceback
import logging
log = logging.getLogger(__name__)

from django.http            import HttpResponse
from django.template        import Template, Context

# from annalist.exceptions    import TargetIdNotFound_Error, TargetEntityNotFound_Error

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.bound_field          import bound_field
from annalist.views.fields.render_fieldvalue    import (
    ModeWrapValueRenderer,
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value
    )

#   ------------------------------------------------------------
#   Local data values
#   ------------------------------------------------------------

view_fieldrow = (
    { 'head':
        """\n"""+
        """<!-- views.fields.render_fieldrow.view_fieldrow head (mode:{{render_mode}}) -->\n"""
    , 'body':
        """<!-- views.fields.render_fieldrow.view_fieldrow body (mode:{{render_mode}}) -->\n"""+
        """<div class="small-12 columns">\n"""+
        """  <div class="view-fieldrow row">\n"""+
        # """@@  field: {{field}}\n"""+
        # """@@  row_bound_fields: {{row_bound_fields}}\n"""+
        """    {% for f in row_bound_fields %}"""+
        """      {% include f.field_render_mode with field=f %}"""+
        """    {% endfor %}"""+
        """  </div>\n"""+
        """</div>\n"""
    , 'tail':
        """<!-- views.fields.render_fieldrow.view_fieldrow tail (mode:{{render_mode}})-->
        """
    })

# edit_fieldrow = (
#     { 'head':
#         """\n"""+
#         """<!-- views.fields.render_fieldrow.edit_fieldrow head (mode:{{render_mode}}) -->\n"""
#     , 'body':
#         """<!-- views.fields.render_fieldrow.edit_fieldrow body (mode:{{render_mode}}) -->\n"""+
#         """<div class="small-12 columns">\n"""+
#         """  <div class="view-fieldrow row">\n"""+
#         """    {% for f in row_bound_fields %}"""+
#         """      {% include f.field_render_mode with field=f %}"""+
#         """    {% endfor %}"""+
#         """  </div>\n"""+
#         """</div>\n"""
#     , 'tail':
#         """<!-- views.fields.render_fieldrow.edit_fieldrow tail (mode:{{render_mode}})-->
#         """
#     })

target_blank = """<span class="value-blank">%s</span>"""

target_missing = """<span class="value-missing">%s</span>"""

#   ----------------------------------------------------------------------------
#   Multi-field reference field: value renderer for viewing or editing
#   ----------------------------------------------------------------------------

class RenderFieldRow(object):
  """
  Render class for field values in a referenced entity.
  """

  def __init__(self, templates=None):
    """
    Creates a renderer object
    """
    # log.info("RenderFieldRow: __init__ %r"%(templates))
    super(RenderFieldRow, self).__init__()
    assert templates is not None, "RenderFieldRow template must be supplied"
    self._template_head  = Template(templates.get('head', ""))
    self._template_body  = Template(templates.get('body', "@@missing body@@"))
    self._template_tail  = Template(templates.get('tail', ""))
    return

  def __str__(self):
    return "RenderFieldRow %r"%(self._template_head)
    # return "RenderFieldRow %r, %s"%(self._template_head,self.render(context))

  def render(self, context):
    """
    Renders multiple fields in a row

    `context`   is a dictionary-like object that provides information for the
                rendering operation.  `context['row_bound_fields']` provides a
                list of bound fields to be rendered.

    returns a string that is incorporated into the resulting web page.
    """
    # log.info("RenderFieldRow.render (mode: %s)"%context['render_mode'])
    # row_bound_fields = context['field']['row_bound_fields']
    # log.info("RenderFieldRow.render field: %r"%(context['field'],))
    # log.info("RenderFieldRow.render descs: %r"%(context['field']['row_bound_fields'],))
    try:
        row_field_descs = context['field']['row_field_descs']
        entity_vals     = context['field']['entity_value']
        extras          = context['field']['context_extra_values']
        row_bound_fields = [
            bound_field(f, entity_vals, context_extra_values=extras) 
            for f in  row_field_descs
            ]
        with context.push({'row_bound_fields': row_bound_fields}):
            response_parts  = [self._template_head.render(context)]
            response_parts.append(self._template_body.render(context))
            response_parts.append(self._template_tail.render(context))
    except Exception as e:
        log.exception("Exception in RenderFieldRow.render")
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
        response_parts = (
            ["Exception in RenderFieldRow.render"]+
            [repr(e)]+
            traceback.format_exception(ex_type, ex, tb)+
            ["***RenderFieldRow.render***"]
            )
        del tb
    return "".join(response_parts)

#   ----------------------------------------------------------------------------
#   Field row reference value mapping
#   ----------------------------------------------------------------------------

class FieldRowValueMapper(RenderBase):
    """
    Value mapper for simple text entry field.
    """

    def __init__(self):
        """
        Creates a renderer object for a simple text field
        """
        super(FieldRowValueMapper, self).__init__()
        return

    # encode, decode methods default to RenderBase; i.e. identity mappings

def get_fieldrow_renderer():
    """
    Return field row renderer object.

    This renders multiple fields froma supplied entity as a single row, wrapping
    the entire set of fields in a row <div>.
    """
    r = RenderFieldValue("fieldrow",
        view_renderer=RenderFieldRow(view_fieldrow),
        edit_renderer=RenderFieldRow(view_fieldrow) # @@@@ change back to edit
        )
    # Suppress all modal rendering: just render field content
    # @@TODO: this is a hack - need to re-think how render modes are hamndled.
    r._render_label           = None
    r._render_view            = ModeWrapValueRenderer("view", r._view_renderer)
    r._render_edit            = ModeWrapValueRenderer("edit", r._edit_renderer)
    r._render_label_view      = ModeWrapValueRenderer("label_view", r._view_renderer)
    r._render_label_edit      = ModeWrapValueRenderer("label_edit", r._edit_renderer)
    r._render_col_head        = None
    r._render_col_head_view   = ModeWrapValueRenderer("col_head_view", r._view_renderer)
    r._render_col_head_edit   = ModeWrapValueRenderer("col_head_edit", r._edit_renderer)
    r._render_col_view        = ModeWrapValueRenderer("col_view", r._view_renderer)
    r._render_col_edit        = ModeWrapValueRenderer("col_edit", r._edit_renderer)
    r._render_label           = None

    # r._render_label           = None
    # r._render_view            = ModeWrapValueRenderer("view", r.view().value_renderer)
    # r._render_edit            = ModeWrapValueRenderer("edit", r.edit().value_renderer)
    # r._render_label_view      = ModeWrapValueRenderer("label_view", r.view().value_renderer)
    # r._render_label_edit      = ModeWrapValueRenderer("label_edit", r.edit().value_renderer)
    # r._render_col_head        = None
    # r._render_col_head_view   = ModeWrapValueRenderer("col_head_view", r.view().value_renderer)
    # r._render_col_head_edit   = ModeWrapValueRenderer("col_head_edit", r.edit().value_renderer)
    # r._render_col_view        = ModeWrapValueRenderer("col_view", r.view().value_renderer)
    # r._render_col_edit        = ModeWrapValueRenderer("col_edit", r.edit().value_renderer)
    # r._render_label           = None



    return r

# End.
