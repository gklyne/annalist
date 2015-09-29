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

from annalist.views.fields.render_placement     import get_field_placement_renderer

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class FieldPlacementRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        self.placement_context = self._make_test_context("small:0,12;medium:4,4")
        return

    def tearDown(self):
        return

    def test_RenderFieldPlacementValue(self):
        self._check_value_renderer_results(
            get_field_placement_renderer(),
            context=self.placement_context,
            expect_rendered_view=
                '''<span class="placement-text">'''+
                '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                ''' (4/4)</span>''',
            expect_rendered_edit=
                '''<select class="placement-text" name="repeat_prefix_test_field">\n'''+
                '''  <option value="">(test placeholder)</option>\n'''+
                '''  <option value="small:0,12">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (0/12)</option>\n'''+
                #@@ Label width calculation doesn't work for placements not sub-multiple of 12
                #@@ (but still OK for columns)
                # '''  <option value="small:0,12;medium:0,9">'''+
                #     '''&block;&block;&block;&block;&block;&block;'''+
                #     '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                #     ''' (0/9)</option>\n'''+
                # '''  <option value="small:0,12;medium:3,9">'''+
                #     '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                #     '''&block;&block;&block;&block;&block;&block;'''+
                #     ''' (3/9)</option>\n'''+
                # '''  <option value="small:0,12;medium:0,8">'''+
                #     '''&block;&block;&block;&block;&block;&block;'''+
                #     '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                #     ''' (0/8)</option>\n'''+
                # '''  <option value="small:0,12;medium:4,8">'''+
                #     '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                #     '''&block;&block;&block;&block;&block;&block;'''+
                #     ''' (4/8)</option>\n'''+
                #@@
                '''  <option value="small:0,12;medium:0,6">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/6)</option>\n'''+
                '''  <option value="small:0,12;medium:3,6">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (3/6)</option>\n'''+
                '''  <option value="small:0,12;medium:6,6">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (6/6)</option>\n'''+
                '''  <option value="small:0,12;medium:0,4">'''+
                    '''&block;&block;&block;&block;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/4)</option>\n'''+
                '''  <option value="small:0,12;medium:4,4" selected="selected">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                    '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (4/4)</option>\n'''+
                '''  <option value="small:0,12;medium:8,4">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&block;&block;&block;&block;'''+
                    ''' (8/4)</option>\n'''+
                '''  <option value="small:0,12;medium:0,3">'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/3)</option>\n'''+
                '''  <option value="small:0,12;medium:3,3">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (3/3)</option>\n'''+
                '''  <option value="small:0,12;medium:6,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (6/3)</option>\n'''+
                '''  <option value="small:0,12;medium:9,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    ''' (9/3)</option>\n'''+
                # Old right-aligned placement strings
                '''  <option value="small:0,12;medium:6,6right">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (6/6 right)</option>\n'''+
                '''  <option value="small:0,12;medium:8,4right">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&block;&block;&block;&block;'''+
                    ''' (8/4 right)</option>\n'''+
                '''  <option value="small:0,12;medium:9,3right">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    ''' (9/3 right)</option>\n'''+
                # Column placement strings affecting all display sizes
                '''  <option value="small:0,9">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (0/9 column)</option>\n'''+
                '''  <option value="small:3,9">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (3/9 column)</option>\n'''+
                '''  <option value="small:0,8">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/8 column)</option>\n'''+
                '''  <option value="small:4,8">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (4/8 column)</option>\n'''+
                '''  <option value="small:0,6">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/6 column)</option>\n'''+
                '''  <option value="small:3,6">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (3/6 column)</option>\n'''+
                '''  <option value="small:6,6">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (6/6 column)</option>\n'''+
                '''  <option value="small:0,4">'''+
                    '''&block;&block;&block;&block;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/4 column)</option>\n'''+
                '''  <option value="small:4,4">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                    '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (4/4 column)</option>\n'''+
                '''  <option value="small:8,4">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&block;&block;&block;&block;'''+
                    ''' (8/4 column)</option>\n'''+
                '''  <option value="small:0,3">'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/3 column)</option>\n'''+
                '''  <option value="small:3,3">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (3/3 column)</option>\n'''+
                '''  <option value="small:6,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (6/3 column)</option>\n'''+
                '''  <option value="small:9,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    ''' (9/3 column)</option>\n'''+
                '''</select>'''
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
