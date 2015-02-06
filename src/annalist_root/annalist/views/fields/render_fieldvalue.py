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
from django.template.loaders.app_directories    import Loader
 
#   ------------------------------------------------------------
#   Local data values
#   ------------------------------------------------------------

#   These templatres all expect the value renderer to be provided in the
#   view context as `value_renderer`

label_template = (
    """<div class="view-label {{field.field_placement.field}}">"""+
    """  <span>{{field.field_label|default:"&nbsp;"}}</span>"""+
    """</div>"""
    )

value_wrapper_template = (
    """<div class="view-value {{field.field_placement.field}}">"""+
    """  {% include value_renderer %}"""+
    """</div>"""
    )

label_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row view-value-row">\n"""+
    """    <div class="view-label {{field.field_placement.label}}">\n"""+
    """      <span>{{field.field_label}}</span>\n"""+
    """    </div>\n"""+
    """    <div class="view-value {{field.field_placement.value}}">\n"""+
    """      {% include value_renderer %}\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """</div>"""
    )

col_head_template = (
    """<div class="view-label col-head {{field.field_placement.field}}">"""+
    """  <span>{{field.field_label}}</span>"""+
    """</div>"""
    )

col_label_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row show-for-small-only">\n"""+
    """    <div class="view-label small-12 columns">\n"""+
    """      <span>{{field.field_label}}</span>\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """  <div class="row view-value-col">\n"""+
    """    <div class="view-value small-12 columns">\n"""+
    """      {% include value_renderer %}\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """</div>"""
    )

col_value_wrapper_template = (
    """<div class="view-value {{field.field_placement.field}}">"""+
    """  {% include value_renderer %}"""+
    """</div>"""
    )

#   ------------------------------------------------------------
#   Renderer factory class
#   ------------------------------------------------------------

class RenderFieldValue(object):
    """
    Renderer constructor for an entity value field.
  
    Given simple rendering templates for a display and editing an entity value
    fields, this class will construct new rendferers for usingthose values in
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

    def __init__(self, 
        view_renderer=None, edit_renderer=None, 
        view_template=None, edit_template=None,
        view_file=None, edit_file=None
        ):
        """
        Creates a renderer factory for a value field.

        view_renderer   is a render object that formats a field value
        edit_renderer   is a render object that formats a field value in a
                        form control that allows the value to be edited
        view_template   is a template string that formats a field value
        edit_template   is a template string that formats a field value in a
                        form control that allows the value to be edited
        view_file       is the name of a template file that formats a field value
        edit_file       is the name of a template file that formats a field value
                        in an editable form control


        Methods provided return composed renderers for a varietom of contexts.
        """
        # log.info("RenderFieldValue: viewrender %s, editrender %s"%(viewrender, edit_file))
        super(RenderFieldValue, self).__init__()
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
            raise Annalist_Error("RenderFieldValue: no view renderer or template provided")
        # Initialize various renderer caches
        self._render_view       = None
        self._render_edit       = None
        self._render_label_view = None
        self._render_label_edit = None
        self._render_col_head   = None
        self._render_col_view   = None
        self._render_col_edit   = None
        self._render_label      = None
        self._render_view       = None
        self._render_edit       = None
        return
  
    def __str__(self):
        return (
            "RenderFieldValue: view_renderer %s, edit_renderer %s"%
            (self._view_renderer, self._edit_renderer)
            )
  
    def __repr__(self):
        return (
            "RenderFieldValue(view_renderer=%r, edit_renderer=%r)"%
            (self._view_renderer, self._edit_renderer)
            )

    # Helpers

    def _get_renderer(self, wrapper_template, value_renderer):
        """
        Returns a renderer that combines a specified wrapper template with a 
        supplied value renderer
        """
        class _renderer(object):
            def __init__(self): # , wrapper, value_renderer):
                pass
            def render(self, context):
                with context.push(value_renderer=value_renderer):
                    return compiled_wrapper.render(context)
        # Compile wrapper template and return inner renderer class
        compiled_wrapper = Template(wrapper_template)
        return _renderer()

    # Template access functions

    def label(self):
        """
        Returns a renderer object to display a field label from the 
        supplied `context['field']` value.
        """
        if not self._render_label_view:
            self._render_label_view = self._get_renderer(label_template, None)
        # log.info("self._render_label_view %r"%self._render_label_view)
        return self._render_label_view

    def view(self):
        """
        Returns a renderer object to display just a non-editable field value.
        """
        # log.info("self._view_renderer %r"%self._view_renderer)
        if not self._render_view:
            self._render_view = self._get_renderer(
                value_wrapper_template, self._view_renderer
                )
        return self._render_view

    def edit(self):
        """
        Returns a renderer object to display just an editable field value.
        """
        if not self._render_edit:
            self._render_edit = self._get_renderer(
                value_wrapper_template, self._edit_renderer
                )
        return self._render_edit

    def label_view(self):
        """
        Returns a renderer object to display a labeled non-editable field value.
        """
        if not self._render_label_view:
            self._render_label_view = self._get_renderer(
                label_wrapper_template, self._view_renderer
                )
        return self._render_label_view

    def label_edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_label_edit:
            self._render_label_edit = self._get_renderer(
                label_wrapper_template, self._edit_renderer
                )
        return self._render_label_edit

    def col_head(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media.
        """
        if not self._render_col_head:
            self._render_col_head = Template(col_head_template)
        return self._render_col_head

    def col_view(self):
        """
        Returns a renderer object to display a non-editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_view:
            self._render_col_view = self._get_renderer(
                col_label_wrapper_template, self._view_renderer
                )
        return self._render_col_view

    def col_edit(self):
        """
        Returns a renderer object to display an editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_edit:
            self._render_col_edit = self._get_renderer(
                col_label_wrapper_template, self._edit_renderer
                )
        return self._render_col_edit


# Helper function for caller to get template content.
# This uses the configured Django templatre loader.

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

def get_field_value(context, default):
    return get_context_field_value(context, 'field_value', default)

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
