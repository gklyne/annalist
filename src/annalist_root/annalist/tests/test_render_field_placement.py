"""
Tests for field placement (size/position) rendering
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
import re
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_placement     import (
    get_field_placement_renderer, option_body, view_body
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class FieldPlacementRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        self.placement_context = self._make_test_context("small:0,12;medium:4,4")
        return

    def tearDown(self):
        return

    def test_RenderFieldPlacementValue(self):
        expect_rendered_view=view_body(
            '''<span class="placement-text">'''+
                '''....####.... (4/4)'''+
                '''</span>'''
                )
        expect_rendered_edit=option_body(
            '''<select class="placement-text" name="repeat_prefix_test_field">\n'''+
            '''  <option value="">(test placeholder)</option>\n'''+
            '''  <option value="small:0,12">'''+
                '''############ (0/12)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:0,6">'''+
                '''######...... (0/6)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:3,6">'''+
                '''...######... (3/6)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:6,6">'''+
                '''......###### (6/6)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:0,4">'''+
                '''####........ (0/4)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:4,4" selected="selected">'''+
                '''....####.... (4/4)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:8,4">'''+
                '''........#### (8/4)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:0,3">'''+
                '''###......... (0/3)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:3,3">'''+
                '''...###...... (3/3)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:6,3">'''+
                '''......###... (6/3)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:9,3">'''+
                '''.........### (9/3)'''+
                '''</option>\n'''+
            # Old right-aligned placement strings
            '''  <option value="small:0,12;medium:6,6right">'''+
                '''......###### (6/6R)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:8,4right">'''+
                '''........#### (8/4R)'''+
                '''</option>\n'''+
            '''  <option value="small:0,12;medium:9,3right">'''+
                '''.........### (9/3R)'''+
                '''</option>\n'''+
            # Column placement strings affecting all display sizes
            '''  <option value="small:0,9">'''+
                '''#########... (0/9col)'''+
                '''</option>\n'''+
            '''  <option value="small:3,9">'''+
                '''...######### (3/9col)'''+
                '''</option>\n'''+
            '''  <option value="small:0,8">'''+
                '''########.... (0/8col)'''+
                '''</option>\n'''+
            '''  <option value="small:4,8">'''+
                '''....######## (4/8col)'''+
                '''</option>\n'''+
            '''  <option value="small:0,6">'''+
                '''######...... (0/6col)'''+
                '''</option>\n'''+
            '''  <option value="small:3,6">'''+
                '''...######... (3/6col)'''+
                '''</option>\n'''+
            '''  <option value="small:6,6">'''+
                '''......###### (6/6col)'''+
                '''</option>\n'''+
            '''  <option value="small:0,4">'''+
                '''####........ (0/4col)'''+
                '''</option>\n'''+
            '''  <option value="small:4,4">'''+
                '''....####.... (4/4col)'''+
                '''</option>\n'''+
            '''  <option value="small:8,4">'''+
                '''........#### (8/4col)'''+
                '''</option>\n'''+
            '''  <option value="small:0,3">'''+
                '''###......... (0/3col)'''+
                '''</option>\n'''+
            '''  <option value="small:3,3">'''+
                '''...###...... (3/3col)'''+
                '''</option>\n'''+
            '''  <option value="small:6,3">'''+
                '''......###... (6/3col)'''+
                '''</option>\n'''+
            '''  <option value="small:9,3">'''+
                '''.........### (9/3col)'''+
                '''</option>\n'''+
            '''</select>'''
            )
        self._check_value_renderer_results(
            get_field_placement_renderer(),
            context=self.placement_context,
            expect_rendered_view=expect_rendered_view,
            expect_rendered_edit=expect_rendered_edit
            )
        return

# End.

if __name__ == "__main__":
    # import django
    # django.setup()  # Needed for template loader
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()
