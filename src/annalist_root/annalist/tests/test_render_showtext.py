"""
Tests for boolean value rendering as checkbox
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

from annalist.views.fields.find_renderers   import get_field_base_renderer

from annalist.tests.field_rendering_support import FieldRendererTestSupport

class ShowtextRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_RenderShowtextValue(self):

        def expect_render(valtext, valhtml):
            render_view = """<span>%s</span>"""%valhtml
            return {'view': render_view, 'edit': render_view}

        test_values = (
            [ ( "text", "text")
            , ( "",     "&nbsp;")
            , ( None,   "&nbsp;")
            ])

        test_value_context_renders = (
            [ (self._make_test_context(val), expect_render(val, valtext))
              for val, valtext in test_values
            ])
        renderer = get_field_base_renderer("Showtext")

        for render_context, expect_render in test_value_context_renders:
            # print repr(render_context['field']['field_value'])
            # print expect_render['edit']
            self._check_value_renderer_results(
                renderer,
                context=render_context,
                expect_rendered_view=expect_render['view'],
                expect_rendered_edit=expect_render['edit'],
                collapse_whitespace=False
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
