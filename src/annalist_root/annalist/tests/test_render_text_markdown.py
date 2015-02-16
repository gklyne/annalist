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

# from django.conf                                import settings
# from django.test                                import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
# from django.template                            import Context, Template, loader

from annalist.views.fields.render_text_markdown import (
    get_text_markdown_renderer, 
    TextMarkdownValueMapper
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class TextMarkdownRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_RenderTextMarkdownValue(self):

        def expect_render(valtext, valhtml):
            render_view = """<span class="markdown">%s</span>"""%valhtml
            render_edit = (
                '''<textarea cols="64" rows="6" name="repeat_prefix_test_field" '''+
                          '''class="small-rows-4 medium-rows-8" '''+
                          '''placeholder="(test placeholder)" '''+
                          '''>%s</textarea>'''
                )%valtext
            return {'view': render_view, 'edit': render_edit}

        nl  = "\n"
        nl2 = "\n\n"
        test_values = (
            [ ( u"markdown", "<p>markdown</p>")
            , ( u"# heading"+nl2+
                u"text paragraph"+nl+
                "", 
                "<h1>heading</h1>\n<p>text paragraph</p>"
              )
            ])

        test_value_context_renders = (
            [ (self._make_test_context(val), expect_render(val, valtext))
              for val, valtext in test_values
            ])
        renderer = get_text_markdown_renderer()

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

    def test_DecodeTextMarkdownValue(self):
        test_decode_values = (
            { None:         None
            , "":           ""
            , "text":       "text"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = TextMarkdownValueMapper.decode(valtext)
            self.assertEqual(
                valdata, expect_valdata, 
                "Value decode(%s) = %r, expect %r"%(valtext, valdata, expect_valdata)
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
