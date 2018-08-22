from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
This module implements a class that is used for rendering a bound field, given
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import traceback

from annalist.views.fields.find_renderers   import (
    get_label_renderer,
    get_view_renderer,
    get_edit_renderer, 
    get_label_view_renderer,
    get_label_edit_renderer, 
    get_col_head_renderer, 
    get_col_head_view_renderer, 
    get_col_head_edit_renderer, 
    get_col_view_renderer,
    get_col_edit_renderer,
    get_value_mapper
    )

class FieldRenderer(object):
    """
    This class represents a value renderer that is bound to a specific field value.

    Methods are referenced from Django templates by a {% include ... %} directive.
    """

    def __init__(self, field_render_type, field_value_mode):
        """
        Initialize a bound field renderer object.
        """
        self._field_render_type = field_render_type
        self._field_value_mode  = field_value_mode
        self._value_mapper      = get_value_mapper(field_render_type)
        self._value_renderer    = (
            { 'label':         get_label_renderer(        field_render_type, field_value_mode)
            , 'view':          get_view_renderer(         field_render_type, field_value_mode)
            , 'edit':          get_edit_renderer(         field_render_type, field_value_mode)
            , 'label_view':    get_label_view_renderer(   field_render_type, field_value_mode)
            , 'label_edit':    get_label_edit_renderer(   field_render_type, field_value_mode)
            , 'col_head':      get_col_head_renderer(     field_render_type, field_value_mode)
            , 'col_head_view': get_col_head_view_renderer(field_render_type, field_value_mode)
            , 'col_head_edit': get_col_head_edit_renderer(field_render_type, field_value_mode)
            , 'col_view':      get_col_view_renderer(     field_render_type, field_value_mode)
            , 'col_edit':      get_col_edit_renderer(     field_render_type, field_value_mode)
            })
        return

    def __str__(self):
        return (
            "FieldRenderer(render_type=%s, value_mode=%s)"%
            (self._field_render_type, self._field_value_mode)
            )

    def value_mapper(self):
        return self._value_mapper

    def renderer(self, mode):
        """
        Return a renderer for a specified mode.

        The renderer returned is accessed from a template using a {% include %} directive,
        which can accept an object with a render method.  A context value is supplied by 
        the Django template processor at the point of invocation.  This mechanism is used
        in the "render_fieldvalue" module, and when composing value renderers.

        See: https://docs.djangoproject.com/en/2.0/ref/templates/builtins/#std:templatetag-include
        """
        return self._value_renderer[mode]
        # return self.diagnostic_renderer(mode)

    def diagnostic_renderer(self, mode):
        """
        Return a diagnostic renderer for a specified mode.

        This is similar to the standard renderer, except that it allows for additional
        diagnostic information to be included to assist in debugging renderer call flows.
        """
        class _renderer(object):
            def __init__(self, field_renderer, mode):
                self._render_type = field_renderer._field_render_type
                self._value_mode  = field_renderer._field_value_mode
                self._mode        = mode
                self._renderer    = field_renderer._value_renderer[mode]
                return
            def render(self, context):
                try:
                    msg = (
                        "@@render(render_type=%s, value_mode=%s, mode=%s)"%
                        (self._render_type, self._value_mode, self._mode)
                        )
                    log.info(msg)
                    return "<!-- %s -->\n"%msg + self._renderer.render(context)
                except Exception as e:
                    log.error("Error in FieldRenderer.renderer: "+str(e))
                    log.info("\n".join(traceback.format_stack()))
                    return str(e)

        class _error_renderer(object):
            def __init__(self, field_renderer, mode, exc):
                self._render_type = field_renderer._field_render_type
                self._value_mode  = field_renderer._field_value_mode
                self._mode        = mode
                self._error       = str(exc)
                return
            def render(self, context):
                return (
                    "@@_error_renderer(render_type=%s, value_mode=%s, mode=%s, error=%s)"%
                    (self._render_type, self._value_mode, self._mode, self._error)
                    )

        try:
            r = _renderer(self, mode)
        except Exception as e:
            log.error("Error in FieldRenderer.renderer._renderer(): "+str(e))
            log.info("\n".join(traceback.format_stack()))
            r = _error_renderer(self, mode, e)
        return r

    def label(self):
        return self.renderer("label")

    def view(self):
        return self.renderer("view")

    def edit(self):
        return self.renderer("edit")

    def label_view(self):
        return self.renderer("label_view")

    def label_edit(self):
        return self.renderer("label_edit")

    def col_head(self):
        return self.renderer("col_head")

    def col_head_view(self):
        return self.renderer("col_head_view")

    def col_head_edit(self):
        return self.renderer("col_head_edit")

    def col_view(self):
        return self.renderer("col_view")

    def col_edit(self):
        return self.renderer("col_edit")

    def mode(self):
        class _renderer(object):
            def __init__(modeself):
                pass
            def render(modeself, context):
                try:
                    r = self._value_renderer[context['render_mode']].render(context)
                except Exception as e:
                    log.error("Exception in FieldRenderer.mode, _renderer.render: %s"%(str(e),))
                    formatted_traceback = traceback.format_stack()
                    log.info("".join(formatted_traceback))
                    response_parts = (
                        ["Exception in FieldRenderer.mode, _renderer.render"]+
                        [repr(e)]+
                        formatted_traceback
                        )
                    return "\n".join(response_parts)
                return r
        return _renderer()

# End.
