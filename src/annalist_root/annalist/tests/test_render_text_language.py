"""
Tests for languaged-tagged text value rendering.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2019, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import sys
import os
import unittest
import re

from annalist.resourcetypes import (
    file_extension, file_extension_for_content_type
    )

from annalist.views.fields.render_text_language import (
    get_text_language_renderer, 
    TextLanguageValueMapper
    )

from .field_rendering_support import FieldRendererTestSupport

class TextLanguageRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Rendering test

    def test_RenderTextLanguageValue(self):

        def language_text_value(text, lang):
            return {'@value': text, '@language': lang} if lang else {'@value': text}

        def expect_render(text, lang):
            view_text = "%s (%s)"%(text, lang) if lang else text
            render_view = '''<span>%s</span>'''%(view_text)
            render_edit = (
                '''<input type="text" size="64" name="repeat_prefix_test_field" '''+
                       '''placeholder="(test placeholder)" '''+
                       '''value="%s" />'''
                )%view_text
            return {'view': render_view, 'edit': render_edit}

        test_values = (
            [ ("text-en",      "en",  "text-en (en)")
            , ("text-en",      "en",  "text-en    (en)")
            , ("text-nl",      "",    "text-nl")
            , ("text (en) nl", "",    "text (en) nl")
            ])
        test_value_context_renders = (
            [ (self._make_test_context(render_text), expect_render(text, lang))
              for text, lang, render_text in test_values
            ])
        renderer = get_text_language_renderer()

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

    def test_DecodeTextLanguageValue(self):
        test_decode_values = (
            { None:               { "@value": "" }
            , "text":             { "@value": "text" }
            , "text (en)":        { "@value": "text", "@language": "en" }
            , "text (en) more":   { "@value": "text (en) more" }
            , "":                 { "@value": "" }
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = TextLanguageValueMapper.decode(valtext)
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
