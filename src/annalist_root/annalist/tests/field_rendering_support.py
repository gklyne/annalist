"""
Support methods for field value renderer tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import re
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

    def assertRenderMatch(self, rendered, expected, collapse_whitespace=False):
        rendered = re.sub(r'<!--.*-->\n', "", rendered)
        if collapse_whitespace:
            rendered = re.sub(r'\s+', " ", rendered).strip()
            expected = re.sub(r'\s+', " ", expected).strip()
        if rendered != expected:
            print "rendered "+rendered
            print "expected "+expected
        self.assertEqual(rendered, expected)
        return

    def _make_test_context(self, val, 
            repeat_prefix="repeat_prefix_", 
            target_value= None, 
            field_link=None, 
            target_link=None, 
            field_ref_type=None,
            options=None
        ):
        cd = (
            { 'field':
              { 'field_placement':      get_placement_classes("small:0,12")
              , 'field_name':           "test_field"
              , 'field_label':          "test label"
              , 'field_placeholder':    "(test placeholder)"
              , 'field_value':          val
              , 'field_edit_value':     val
              , 'target_value':         val     # Mimics bound_field default behaviour
              , 'field_view_value':     val
              , 'continuation_param':   "?continuation_url=test_cont"
              }
            , 'repeat_prefix':        repeat_prefix
            })
        if target_value is not None:
            cd['field']['target_value'] = target_value
        if field_link is not None:
            cd['field']['field_value_link']              = field_link
            cd['field']['field_value_link_continuation'] = field_link+"?continuation_url=test_cont"
        if target_link is not None:
            cd['field']['target_value_link']              = target_link
            cd['field']['target_value_link_continuation'] = target_link+"?continuation_url=test_cont"
        if field_ref_type is not None:
            cd['field']['field_ref_type'] = field_ref_type
        if options is not None:
            cd['field']['options'] = options
        return Context(cd)

    def _check_value_renderer_results(self,
        fieldrender, context=None,
        expect_rendered_view="...", 
        expect_rendered_edit="...",
        collapse_whitespace=False
        ):
        #@@ - method unused, deprecated.  When stabilized, remove this code.
        # rendered_label = fieldrender.label().render(context)
        # self.assertRenderMatch(
        #     rendered_label, 
        #     '''<div class="view-label small-12 columns">  <span>test label</span></div>''',
        #     collapse_whitespace
        #     )
        #@@
        rendered_view = fieldrender.view().render(context)
        self.assertRenderMatch(
            rendered_view, 
            '''<div class="view-value small-12 columns">\n  %s\n</div>'''%expect_rendered_view,
            collapse_whitespace
            )
        rendered_edit = fieldrender.edit().render(context)
        self.assertRenderMatch(
            rendered_edit, 
            '''<div class="view-value small-12 columns">\n  %s\n</div>'''%expect_rendered_edit,
            collapse_whitespace
            )
        rendered_label_view = fieldrender.label_view().render(context)
        self.assertRenderMatch(
            rendered_label_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row view-value-row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''    <div class="view-value small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_label_edit = fieldrender.label_edit().render(context)
        self.assertRenderMatch(
            rendered_label_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row view-value-row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''    <div class="view-value small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_head = fieldrender.col_head().render(context)
        self.assertRenderMatch(
            rendered_col_head, 
            '''<div class="view-label col-head small-12 columns">\n'''+
            '''  <span>test label</span>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_view = fieldrender.col_view().render(context)
        self.assertRenderMatch(
            rendered_col_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row view-value-col">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_edit = fieldrender.col_edit().render(context)
        self.assertRenderMatch(
            rendered_col_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row view-value-col">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        return


# End.
