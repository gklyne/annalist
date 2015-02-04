"""
Support methods for field value renderer tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings
from django.template                        import Context, Template, loader

from annalist.views.fields.render_placement import Placement, get_placement_classes

from annalist.tests.AnnalistTestCase        import AnnalistTestCase

#   -----------------------------------------------------------------------------
#
#   Field renderer tests support
#
#   -----------------------------------------------------------------------------

class FieldRendererTestSupport(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        return

    def tearDown(self):
        return

    def _make_test_context(self, val, repeat_prefix="repeat_prefix_"):
        return Context(
            { 'field':
              { 'field_placement':      get_placement_classes("small:0,12")
              , 'field_name':           "test_field"
              , 'field_label':          "test label"
              , 'field_placeholder':    "(test placeholder)"
              , 'field_value':          val
              }
            , 'repeat_prefix':        repeat_prefix
            })

    def _check_value_renderer_results(self,
        fieldrender, context=None,
        expect_rendered_view="...", 
        expect_rendered_edit="..."
        ):
        rendered_label      = fieldrender.label().render(context)
        self.assertEqual(
            rendered_label, 
            '''<div class="view-label small-12 columns">  test label</div>'''
            )
        rendered_view       = fieldrender.view().render(context)
        self.assertEqual(
            rendered_view, 
            '''<div class="view-value small-12 columns">  %s</div>'''%expect_rendered_view
            )
        rendered_edit       = fieldrender.edit().render(context)
        self.assertEqual(
            rendered_edit, 
            '''<div class="view-value small-12 columns">  %s</div>'''%expect_rendered_edit
            )
        rendered_label_view = fieldrender.label_view().render(context)
        self.assertEqual(
            rendered_label_view, 
            '''<div class="view-label small-12 columns">  '''+
            '''test label'''+
            '''</div>'''
            )
        rendered_label_edit = fieldrender.label_edit().render(context)
        self.assertEqual(
            rendered_label_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      test label\n'''+
            '''    </div>\n'''+
            '''    <div class="view-value small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        rendered_col_head   = fieldrender.col_head().render(context)
        self.assertEqual(
            rendered_col_head, 
            '''<div class="view-label col-head small-12 columns">  '''+
            '''test label</div>'''
            )
        rendered_col_view   = fieldrender.col_view().render(context)
        self.assertEqual(
            rendered_col_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      test label\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        rendered_col_edit   = fieldrender.col_edit().render(context)
        self.assertEqual(
            rendered_col_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      test label\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        return

# End.
