"""
RenderFieldValue2 class for returning field renderers.  This class works for 
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

from django.template.loaders.app_directories    import Loader
 
#   ------------------------------------------------------------
#   Local data values
#   ------------------------------------------------------------

#   These templatres all expect the value renderer to be provided in the
#   view context as `value_renderer`

label_template = (
    """<div class="view-label {{field.field_placement.field}}">"""+
    """  <p>{{field.field_label|default:"&nbsp;"}}</p>"""+
    """</div>"""
    )

value_wrapper_template = (
    """<div class="{{field.field_placement.field}}">"""+
    """  {% include value_renderer %}"""+
    """</div>"""
    )

label_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row">\n"""+
    """    <div class="view-label {{field.field_placement.label}}">\n"""+
    """      <p>{{field.field_label}}</p>\n"""+
    """    </div>\n"""+
    """    <div class="{{field.field_placement.value}}">\n"""+
    """      {% include value_renderer %}\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """</div>"""
    )

col_label_template = (
    """<div class="view-label {{field.field_placement.field}}">"""+
    """  <p>{{field.field_label}}</p>"""+
    """</div>"""
    )

col_label_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row show-for-small-only">\n"""+
    """    <div class="view-label small-12 columns">\n"""+
    """      <p>{{field.field_label}}</p>\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """  <div class="row">\n"""+
    """    <div class="small-12 columns">\n"""+
    """      {% include value_renderer %}\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """</div>"""
    )

#   ------------------------------------------------------------
#   Renderer factory class
#   ------------------------------------------------------------

class RenderFieldValue2(object):
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

    def __init__(self, viewrenderer=None, editrenderer=None):
        """
        Creates a renderer factory for a value field.

        viewrenderer    is a render object that displays a field value,
                        or a string containing a value display template file name
        editrenderer    is a render object that displays a field value in a
                        form control that allows the value to be edited,
                        or a string containing a value editing template file name
        """
        # log.info("RenderFieldValue2: viewrender %s, editrender %s"%(viewrender, editfile))
        super(RenderFieldValue2, self).__init__()
        # Save value renderers
        if isinstance(viewrenderer, (str, unicode)):
            self._viewrenderer  = Template(viewrenderer)
        else:
            self._viewrenderer  = viewrenderer
        if isinstance(editrenderer, (str, unicode)):
            self._editrenderer  = Template(editrenderer)
        else:
            self._editrenderer  = editrenderer
        # Initialize various renderer caches
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
            "RenderFieldValue2: viewrenderer %s, editrenderer %s"%
            (self._viewrenderer, self._editrenderer)
            )
  
    def __repr__(self):
        return (
            "RenderFieldValue2(viewrenderer=%r, editrenderer=%r)"%
            (self._viewrenderer, self._editrenderer)
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
        log.info("self._render_label_view %r"%self._render_label_view)
        return self._render_label_view

    def view(self):
        """
        Returns a renderer object to display just a non-editable field value.
        """
        log.info("self._viewrenderer %r"%self._viewrenderer)
        return self._viewrenderer

    def edit(self):
        """
        Returns a renderer object to display just an editable field value.
        """
        return self._editrenderer

    def label_view(self):
        """
        Returns a renderer object to display a labeled non-editable field value.
        """
        if not self._render_label_view:
            self._render_label_view = self._get_renderer(
                label_wrapper_template, self._viewrenderer
                )
        return self._render_label_view

    def label_edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_label_edit:
            self._render_label_edit = self._get_renderer(
                label_wrapper_template, self._editrenderer
                )
        return self._render_label_edit

    def col_head(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media.
        """
        if not self._render_col_head:
            self._render_col_head = Template(col_label_template)
        return self._render_col_head

    def col_view(self):
        """
        Returns a renderer object to display a non-editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_view:
            self._render_col_view = self._get_renderer(
                col_label_wrapper_template, self._viewrenderer
                )
        return self._render_col_view

    def col_edit(self):
        """
        Returns a renderer object to display an editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_edit:
            self._render_col_edit = self._get_renderer(
                col_label_wrapper_template, self._editrenderer
                )
        return self._render_col_edit


# Helper function for caller to get template content.
# This uses the configured Django templatre loader.

def get_template(templatefile, failmsg):
    """
    Retrieve template source from the supplied filename
    """
    assert templatefile, "%s: no template filename"%failmsg
    # Instantiate a template loader
    loader = Loader()
    # Source: actual source code read from template file
    # File path: absolute file path of template file
    source, file_path = loader.load_template_source(templatefile)
    return source


# End.
#........1.........2.........3.........4.........5.........6.........7.........8
