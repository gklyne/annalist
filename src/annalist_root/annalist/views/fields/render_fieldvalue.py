"""
RenderFieldValue class for returning field renderers.  This class works for fields that can be 
rendered using simple templates that are provided as files in the project templkates directory.

The class provides for wrapping the value rendering templates in various ways so that they can
be appliued in a range of different contexts.
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

label_template = (
    """<div class="view-label {{field.field_placement.field}}">"""+
    """  <p>{{field.field_label|default:"&nbsp;"}}</p>"""+
    """</div>"""
    )

value_wrapper_template = (
    """<div class="{{field.field_placement.field}}">"""+
    """%s"""+
    """</div>"""
    )

label_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row">\n"""+
    """    <div class="view-label {{field.field_placement.label}}">\n"""+
    """      <p>{{field.field_label}}</p>\n"""+
    """    </div>\n"""+
    """    <div class="{{field.field_placement.value}}">\n"""+
    """      %s\n"""+
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
    """      %s\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
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

    def __init__(self, viewfile=None, editfile=None):
        """
        Creates a renderer factory for a value field.
        """
        # log.info("RenderFieldValue: viewfile %s, editfile %s"%(viewfile, editfile))
        super(RenderFieldValue, self).__init__()
        self._viewfile          = viewfile
        self._editfile          = editfile
        self._view_template     = None
        self._edit_template     = None
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
            "RenderFieldValue: viewfile %s, editfile %s"%
            (self._viewfile, self._editfile)
            )
  
    def __repr__(self):
        return (
            "RenderFieldValue(viewfile=%r, editfile=%r)"%
            (self._viewfile, self._editfile)
            )

    # Helpers

    def _get_template(self, templatefile, failmsg):
        assert templatefile, "%s: no template filename"
        # Instantiate a template loader
        loader = Loader()
        # Source: actual source code read from template file
        # File path: absolute file path of template file
        source, file_path = loader.load_template_source(
            templatefile
            )
        return source

    def _get_view_template(self):
        if not self._view_template:
            self._view_template = self._get_template(
                self._viewfile, 
                "Can't get view template"
                )
        return self._view_template

    def _get_edit_template(self):
        if not self._edit_template:
            self._edit_template = self._get_template(
                self._editfile, 
                "Can't get edit template"
                )
        return self._edit_template

    def _get_renderer(self, fieldtemplate, wrappertemplate):
        pass

    # Template access functions

    def label(self):
        """
        Returns a renderer object to display a field label from the 
        supplied `context['field']` value.
        """
        if not self._render_label_view:
            self._render_label_view = Template(label_template)
        return self._render_label_view

    def view(self):
        """
        Returns a renderer object to display a non-editable field value.
        """
        if not self._render_view:
            t = value_wrapper_template%(self._get_view_template())
            self._render_view = Template(t)
        return self._render_view

    def edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_edit:
            t = value_wrapper_template%(self._get_edit_template())
            self._render_edit = Template(t)
        return self._render_edit

    def label_view(self):
        """
        Returns a renderer object to display a labeled non-editable field value.
        """
        if not self._render_label_view:
            t = label_wrapper_template%(self._get_view_template())
            self._render_label_view = Template(t)
        return self._render_label_view

    def label_edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_label_edit:
            t = label_wrapper_template%(self._get_edit_template())
            self._render_label_edit = Template(t)
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
            t = col_label_wrapper_template%(self._get_view_template())
            self._render_col_view = Template(t)
        return self._render_col_view

    def col_edit(self):
        """
        Returns a renderer object to display an editable field,
        labeled on a small display, and unlabelled for a larger display
        """
        if not self._render_col_edit:
            t = col_label_wrapper_template%(self._get_edit_template())
            self._render_col_edit = Template(t)
        return self._render_col_edit

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
