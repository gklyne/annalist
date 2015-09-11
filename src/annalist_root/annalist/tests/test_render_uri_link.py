"""
Tests for text value displayed as a hyperlink.

The text value is taken to be a URI or URI reference.

@@TODO: later developments shoukld also support CURIES (cf. issue #19,
https://github.com/gklyne/annalist/issues/19).
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

from annalist.views.fields.render_uri_link import (
    get_uri_link_renderer, 
    URILinkValueMapper
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class UriLinkRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_RenderUriLinkValue(self):

        def expect_render(linktext, labeltext):
            render_view = '''<a href="%s" target="_blank">%s</a>'''%(linktext, labeltext)
            render_edit = (
                '''<input type="text" size="64" name="repeat_prefix_test_field" '''+
                       '''placeholder="(test placeholder)" '''+
                       '''value="%s" />'''
                )%linktext
            return {'view': render_view, 'edit': render_edit}

        test_values = (
            [ ("http://example.com/path",         "example.com/path")
            , ("https://example.com/path",        "example.com/path")
            , ("file:///example/path",            "example/path")
            , ("file://example.com/path",         "example.com/path")
            , ("mailto:user@example.com",         "user@example.com")
            , ("foo://example.com/more",          "foo://example.com/more")
            ])
        test_value_context_renders = (
            [ (self._make_test_context(linktext),  expect_render(linktext, labeltext))
                for linktext, labeltext in test_values
            ])
        renderer = get_uri_link_renderer()

        for render_context, expect_render in test_value_context_renders:
            # print repr(render_context['field']['field_value'])
            self._check_value_renderer_results(
                renderer,
                context=render_context,
                expect_rendered_view=expect_render['view'],
                expect_rendered_edit=expect_render['edit'],
                collapse_whitespace=True
                )
        return

    def test_DecodeUriLinkValue(self):
        test_decode_values = (
            { None:                         ""
            , "http://example.com/path":    "http://example.com/path"
            , "https://example.com/path":   "https://example.com/path"
            , "example.com/path":           "example.com/path"
            , "file:///example/path/":      "file:///example/path/"
            , "file://example.com/path":    "file://example.com/path"
            , "mailto:user@example.com":    "mailto:user@example.com"
            , "foo://example.com/more":     "foo://example.com/more"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = URILinkValueMapper.decode(valtext)
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
