"""

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
    """<div class="{{field.field_placement.field}}">"""+
    """{{field.field_label}}"""+
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
    """    <div class="view_label {{field.field_placement.label}}">\n"""+
    """      <p>{{field.field_label}}</p>\n"""+
    """    </div>\n"""+
    """    <div class="{{field.field_placement.value}}">\n"""+
    """      %s\n"""+
    """    </div>\n"""+
    """  </div>\n"""+
    """</div>"""
    )

itemlabel_template = (
    """<div class="{{field.field_placement.field}} hide-for-small-only">"""+
    """{{field.field_label}}"""+
    """</div>"""
    )

itemlabel_wrapper_template = (
    """<div class="{{field.field_placement.field}}">\n"""+
    """  <div class="row show-for-small-only">\n"""+
    """    <div class="view_label small-12 columns">\n"""+
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
  
      * labelview:  labeled value display, not editable
      * labeledit:  labeled value edit control
      * itemhead:   value label or nothing, depending on media context
      * itemview:   labeled or unlabeled value display, depending on media context
      * itemedit:   labeled or unlabeled value edit control, depending on media context
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
        self._viewtemplate      = None
        self._edittemplate      = None
        self._render_labelview  = None
        self._render_labeledit  = None
        self._render_itemhead   = None
        self._render_itemview   = None
        self._render_itemedit   = None
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

    def _get_viewtemplate(self):
        if not self._viewtemplate:
            self._viewtemplate = self._get_template(
                self._viewfile, 
                "Can't get view template"
                )
        return self._viewtemplate

    def _get_edittemplate(self):
        if not self._edittemplate:
            self._edittemplate = self._get_template(
                self._editfile, 
                "Can't get edit template"
                )
        return self._edittemplate

    def _get_renderer(self, fieldtemplate, wrappertemplate):
        pass

    # Template access functions

    def label(self):
        """
        Returns a renderer object to display a field label from the 
        supplied `context['field']` value.
        """
        if not self._render_labelview:
            self._render_labelview = Template(label_template)
        return self._render_labelview

    def view(self):
        """
        Returns a renderer object to display a non-editable field value.
        """
        if not self._render_view:
            t = value_wrapper_template%(self._get_viewtemplate())
            self._render_view = Template(t)
        return self._render_view

    def edit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_edit:
            t = value_wrapper_template%(self._get_edittemplate())
            self._render_edit = Template(t)
        return self._render_edit

    def labelview(self):
        """
        Returns a renderer object to display a labeled non-editable field value.
        """
        if not self._render_labelview:
            t = label_wrapper_template%(self._get_viewtemplate())
            self._render_labelview = Template(t)
        return self._render_labelview

    def labeledit(self):
        """
        Returns a renderer object to display an editable field value.
        """
        if not self._render_labeledit:
            t = label_wrapper_template%(self._get_edittemplate())
            self._render_labeledit = Template(t)
        return self._render_labeledit

    def itemhead(self):
        """
        Returns a renderer object to display nothing on small media, or
        a field label used as a column header on larger media.
        """
        if not self._render_itemhead:
            self._render_itemhead = Template(itemlabel_template)
        return self._render_itemhead

    def itemview(self):
        if not self._render_itemview:
            t = itemlabel_wrapper_template%(self._get_viewtemplate())
            self._render_itemview = Template(t)
        return self._render_itemview

    def itemedit(self):
        if not self._render_itemedit:
            t = itemlabel_wrapper_template%(self._get_edittemplate())
            self._render_itemedit = Template(t)
        return self._render_itemedit

# End.
#........1.........2.........3.........4.........5.........6.........7.........8
