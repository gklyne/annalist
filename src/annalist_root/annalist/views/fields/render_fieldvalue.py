"""
RenderFieldValue class for returning field renderers.  This class works for 
fields that can be rendered using supplied renderer objects (which may be 
compiled templates).

The class provides for wrapping the value rendering templates in various ways 
so that they can be applied in a range of different contexts.

This class is based on RenderFieldValue, but accepts renderers rather than
template file names.  In due course, RenderFieldValue should be renamed and
re-written to be based on the class defined here.
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

import django
django.setup()  # Needed for template loader
from django.template.loaders.app_directories import Loader
 
from annalist.exceptions import Annalist_Error

#   ------------------------------------------------------------
#   Local data values
#   ------------------------------------------------------------

#   These templates all expect the value renderer to be provided in the
#   view context as `value_renderer`

# Render-type-independent templates

label_template = (
    """<span>{{field.field_label|default:"&nbsp;"}}</span>"""
    )

_unused_col_head_template = (
    """<div class="view-label col-head {{field.field_placement.field}}">"""+
    """  <span>{{field.field_label}}</span>"""+
    """</div>"""
    )

no_tooltip   = ""
with_tooltip = "{{field.field_tooltip|safe}}"

# Renderer wrapper templates

# @@TODO: change label rendering to use wrapper via TemplateWrapValueRenderer
#         save renderer for label in class init, based on (reduced) label_template (above)

# Wrap field label
label_wrapper_template = ( 
    # """<!-- label_wrapper_template ({{field.field_render_type}}) -->"""+
    """<div class="view-label {{field.field_placement.field}}">\n"""+
    """  {% include value_renderer %}\n"""+
    "</div>"""
    )

# Wrap bare value (e.g. column value)
def value_wrapper_template(tooltip):
    return ( 
        # """<!-- value_wrapper_template ({{field.field_render_type}}) -->"""+
        """<div class="view-value {{field.field_placement.field}}"%s>\n"""+
        """  {%% include value_renderer %%}\n"""+
        """</div>"""
        )%(tooltip,)

view_value_wrapper_template = value_wrapper_template(no_tooltip)
edit_value_wrapper_template = value_wrapper_template(with_tooltip)

# Wrap value and include label
def label_value_wrapper_template(tooltip):
    return (
        # """<!-- label_value_wrapper_template ({{field.field_render_type}}) -->"""+
        """<div class="{{field.field_placement.field}}"%s>\n"""+
        """  <div class="row view-value-row">\n"""+
        """    <div class="view-label {{field.field_placement.label}}">\n"""+
        """      <span>{{field.field_label}}</span>\n"""+
        """    </div>\n"""+
        """    <div class="view-value {{field.field_placement.value}}">\n"""+
        """      {%% include value_renderer %%}\n"""+
        """    </div>\n"""+
        """  </div>\n"""+
        """</div>"""
        )%(tooltip,)

label_view_value_wrapper_template = label_value_wrapper_template(no_tooltip)
label_edit_value_wrapper_template = label_value_wrapper_template(with_tooltip)

# Wrap field label with column heading styling
col_head_wrapper_template = ( 
    # """<!-- col_head_wrapper_template ({{field.field_render_type}}) -->"""+
    """<div class="view-label col-head {{field.field_placement.field}}">\n"""+
    """  {% include value_renderer %}\n"""+
    """</div>"""
    )

# Wrap value with column value styling; include label on small displays only
def col_label_value_wrapper_template(tooltip):
    return ( 
        # """<!-- col_label_value_wrapper_template ({{field.field_render_type}}) -->"""+
        """<div class="{{field.field_placement.field}}"%s>\n"""+
        """  <div class="row show-for-small-only">\n"""+
        """    <div class="view-label small-12 columns">\n"""+
        """      <span>{{field.field_label}}</span>\n"""+
        """    </div>\n"""+
        """  </div>\n"""+
        """  <div class="row view-value-col">\n"""+
        """    <div class="view-value small-12 columns">\n"""+
        """      {%% include value_renderer %%}\n"""+
        """    </div>\n"""+
        """  </div>\n"""+
        """</div>"""
        )%(tooltip,)

col_label_view_value_wrapper_template = col_label_value_wrapper_template(no_tooltip)
col_label_edit_value_wrapper_template = col_label_value_wrapper_template(with_tooltip)

#   ------------------------------------------------------------
#   Helper classes
#   ------------------------------------------------------------

class TemplateWrapValueRenderer(object):
    """
    Render class combines a value renderer with a wrapper template.

    The wrapper template invokes the value renderer by a reference
    to `{% include value_renderer %}`
    """
    def __init__(self, wrapper_template, value_renderer):
        self.compiled_wrapper = Template(wrapper_template)
        self.value_renderer   = value_renderer
        return
    def render(self, context):
        with context.push(value_renderer=self.value_renderer):
            try:
                return self.compiled_wrapper.render(context)
            except Exception as e:
                log.exception("Exception in TemplateWrapValueRenderer.render")
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                response_parts = (
                    ["Exception in TemplateWrapValueRenderer.render"]+
                    [repr(e)]+
                    traceback.format_exception(ex_type, ex, tb)+
                    ["***TemplateWrapValueRenderer.render***"]
                    )
                del tb
                return "\n".join(response_parts)

class ModeWrapValueRenderer(object):
    """
    Render class invokes a value renderer with a specified render mode.
    """
    def __init__(self, render_mode, value_renderer):
        self.render_mode    = render_mode
        self.value_renderer = value_renderer
        return
    def render(self, context):
        with context.push(render_mode=self.render_mode):
            try:
                return self.value_renderer.render(context)
            except Exception as e:
                log.exception("Exception in ModeWrapValueRenderer.render")
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                response_parts = (
                    ["Exception in ModeWrapValueRenderer.render"]+
                    [repr(e)]+
                    traceback.format_exception(ex_type, ex, tb)+
                    ["***ModeWrapValueRenderer.render***"]
                    )
                del tb
                return "\n".join(response_parts)

#   ------------------------------------------------------------
#   Renderer factory class
#   ------------------------------------------------------------

class RenderFieldValue(object):
    """
    Renderer constructor for an entity value field.
  
    Given simple rendering templates for a display and editing an entity value
    fields, this class will construct new rendferers for using those values in
    different contexts:
  
      * label_view: labeled value display, not editable
      * label_edit: labeled value edit control
      * col_head:   value label or nothing, depending on media context
      * col_view:   labeled or unlabeled value display, depending on media context
      * col_edit:   labeled or unlabeled value edit control, depending on media context
      * label:      value label
      * view:       unlabeled value display control
      * edit:       unlabeled value edit control

    The various renderers returned require `context['field']` to contain a 
    `bound_field` value corresponding to the value and field to be displayed.
    (In the case of the `label` renderer, the field description is enough.)
    """

    def __init__(self, render_type,
        view_renderer=None, edit_renderer=None, 
        col_head_view_renderer=None, col_head_edit_renderer=None, 
        view_template=None, edit_template=None,
        view_file=None, edit_file=None
        ):
        """
        Creates a renderer factory for a value field.

        render_type     render type string (for diagnostics)
        view_renderer   is a render object that formats a field value
        edit_renderer   is a render object that formats a field value in a
                        form control that allows the value to be edited
        col_head_view_renderer
                        if supplied, overrides the renderer normally used for 
                        displaying column headings when viewing an entity.
        col_head_edit_renderer
                        if supplied, overrides the renderer normally used for 
                        displaying column headings when viewing an entity.
        view_template   is a template string that formats a field value
        edit_template   is a template string that formats a field value in a
                        form control that allows the value to be edited
        view_file       is the name of a template file that formats a field value
        edit_file       is the name of a template file that formats a field value
                        in an editable form control


        Methods provided return composed renderers for a variety of contexts.
        """
        # log.info("RenderFieldValue: viewrender %s, editrender %s"%(viewrender, edit_file))
        super(RenderFieldValue, self).__init__()
        self._render_type = render_type
        # Save label renderer
        self._label_renderer = Template(label_template)
        # Save view renderer
        if view_renderer is not None:
            self._view_renderer = view_renderer
        elif view_template is not None:
            self._view_renderer = Template(view_template)
        elif view_file is not None:
            self._view_renderer = Template(get_template(view_file))
        else:
            raise Annalist_Error("RenderFieldValue: no view renderer or template provided")
        # Save edit renderer
        if edit_renderer is not None:
            self._edit_renderer = edit_renderer
        elif edit_template is not None:
            self._edit_renderer = Template(edit_template)
        elif edit_file is not None:
            self._edit_renderer = Template(get_template(edit_file))
        else:
            raise Annalist_Error("RenderFieldValue: no edit renderer or template provided")
        # Initialize various renderer caches
        self._col_head_view_renderer = col_head_view_renderer
        self._col_head_edit_renderer = col_head_edit_renderer
        self._render_label           = None
        self._render_view            = None
        self._render_edit            = None
        self._render_label_view      = None
        self._render_label_edit      = None
        self._render_col_head        = None
        self._render_col_head_view   = None
        self._render_col_head_edit   = None
        self._render_col_view        = None
        self._render_col_edit        = None
        self._renderers              = None
        return
  
    def __str__(self):
        return (
            "RenderFieldValue: view_renderer %s, edit_renderer %s"%
            (self._view_renderer, self._edit_renderer)
            )
  
    def __repr__(self):
        return (
            "RenderFieldValue(render_type=%s, view_renderer=%r, edit_renderer=%r)"%
            (self._render_type, self._view_renderer, self._edit_renderer)
            )

    # Helpers

    def render_mode(self):
        """
        Returns a renderer object that renders whatever is required for the 
        current value of "render_mode" in the view context.
        """
        if self._renderers is None:
            # Create dictionary of renderers for render_mode
            self._renderers = (
                { "view":           self.view
                , "edit":           self.edit
                , "label_view":     self.label_view
                , "label_edit":     self.label_edit
                , "col_head":       self.col_head
                , "col_head_view":  self.col_head_view
                , "col_head_edit":  self.col_head_edit
                , "col_view":       self.col_view
                , "col_edit":       self.col_edit
                })       
        _renderers = self._renderers
        class _renderer(object):
            def __init__(self):
                pass
            def render(self, context):
                try:
                    m = context['render_mode']
                    r = _renderers[m]()
                    return r.render(context)
                except Exception as e:
                    log.exception("Exception in render_fieldvalue.render_mode.render")
                    ex_type, ex, tb = sys.exc_info()
                    traceback.print_tb(tb)
                    response_parts = (
                        ["Exception in render_fieldvalue.render_mode.render"]+
                        [repr(e)]+
                        traceback.format_exception(ex_type, ex, tb)+
                        ["***render_fieldvalue.render_mode.render***"]
                        )
                    del tb
                    return "\n".join(response_parts)
        return _renderer()

    # Template access functions

    def label(self):
        """
        Returns a renderer object to display a field label from the 
        supplied `context['field']` value.
        """
        if not self._render_label:
            self._render_label = ModeWrapValueRenderer(
                "label",
                TemplateWrapValueRenderer(
                    label_template, None
                    )
                )
        # log.info("self._render_label %r"%self._render_label)
        return self._render_label

    def view(self):
        """
        Returns a renderer object to display just a non-editable field value.
        """
        # log.info("self._view_renderer %r"%self._view_renderer)
        if not self._render_view:
            self._render_view = ModeWrapValueRenderer(
                "view",
                TemplateWrapValueRenderer(
                    view_value_wrapper_template, self._view_renderer
                    )
                )
        return self._render_view

    def edit(self):
        """
        Returns a renderer object to display just an editable field value.
        """
        if not self._render_edit:
            self._render_edit = ModeWrapValueRenderer(
                "edit",
                TemplateWrapValueRenderer(
                    edit_value_wrapper_template, self._edit_renderer
                    )
                )
        return self._render_edit

    def label_view(self):
        """
        Returns a renderer object to display a labeled non-editable field value.
        """
        if not self._render_label_view:
            self._render_label_view = ModeWrapValueRenderer(
                "label_view",
                TemplateWrapValueRenderer(
                    label_view_value_wrapper_template, self._view_renderer
                    )
                )
        return self._render_label_view

    def label_edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_label_edit:
            self._render_label_edit = ModeWrapValueRenderer(
                "label_edit",
                TemplateWrapValueRenderer(
                    label_edit_value_wrapper_template, self._edit_renderer
                    )
                )
        return self._render_label_edit

    def col_head(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media.
        """
        if not self._render_col_head:
            self._render_col_head = ModeWrapValueRenderer(
                "col_head",
                TemplateWrapValueRenderer(
                    col_head_wrapper_template, self._label_renderer
                    )
                )
        return self._render_col_head

    def col_head_view(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media when
        viewing an entity.
        """
        if not self._render_col_head_view and self._col_head_view_renderer:
            self._render_col_head_view = ModeWrapValueRenderer(
                "col_head_view",
                TemplateWrapValueRenderer(
                    col_head_wrapper_template, self._col_head_view_renderer
                    )
                )
        return self._render_col_head_view or self.col_head()

    def col_head_edit(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media when
        editing an entity.
        """
        if not self._render_col_head_edit and self._col_head_edit_renderer:
            self._render_col_head_edit = ModeWrapValueRenderer(
                "col_head_edit",
                TemplateWrapValueRenderer(
                    col_head_wrapper_template, self._col_head_edit_renderer
                    )
                )
        return self._render_col_head_edit or self.col_head()

    def col_view(self):
        """
        Returns a renderer object to display a non-editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_view:
            self._render_col_view = ModeWrapValueRenderer(
                "col_view",
                TemplateWrapValueRenderer(
                    col_label_view_value_wrapper_template, self._view_renderer
                    )
                )
        return self._render_col_view

    def col_edit(self):
        """
        Returns a renderer object to display an editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_edit:
            self._render_col_edit = ModeWrapValueRenderer(
                "col_edit",
                TemplateWrapValueRenderer(
                    col_label_edit_value_wrapper_template, self._edit_renderer
                    )
                )
        return self._render_col_edit

# Helper function for caller to get template content.
# This uses the configured Django template loader.

def get_template(templatefile, failmsg="no template filename supplied"):
    """
    Retrieve template source from the supplied filename
    """
    assert templatefile, "get_template: %s"%failmsg
    # Instantiate a template loader
    loader = Loader()
    # Source: actual source code read from template file
    # File path: absolute file path of template file
    source, file_path = loader.load_template_source(templatefile)
    return source

# Helper functions for accessing values from context

def get_context_value(context, key, default):
    if key in context:
        return context[key]
    return default

# def get_context_repeat_value(context, key, default):
#     repeat = get_context_value(context, 'repeat', {})
#     return get_context_value(repeat, key, default)

def get_context_field_value(context, key, default):
    field = get_context_value(context, 'field', {})
    return get_context_value(field, key, default)

def get_field_edit_value(context, default):
    return get_context_field_value(context, 'field_edit_value', default)

def get_field_view_value(context, default):
    return get_context_field_value(context, 'field_view_value', default)

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
