"""
Tests for URI reference displayed as an audio playback widget.

@@TODO: later developments should also support CURIES (cf. issue #19,
https://github.com/gklyne/annalist/issues/19).
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
import re
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_ref_audio import (
    get_ref_audio_renderer, 
    RefAudioValueMapper
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class RefAudioRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_RenderRefAudioValue(self):

        def expect_render(linktext, alttext):
            render_view = (
                """<div>Audio at '<a href="%s" target="_blank">%s</a>'</div>"""%(linktext, alttext)+
                """<audio controls="controls" src="%s" ></audio>"""%(linktext)+
                "")
            render_edit = (
                """<input type="text" size="64" name="repeat_prefix_test_field" """+
                       """placeholder="(test placeholder)" """+
                       """value="%s" />"""
                )%linktext
            return {'view': render_view, 'edit': render_edit}

        test_values = (
            [ ("http://example.com/path",         "http://example.com/path")
            , ("https://example.com/path",        "https://example.com/path")
            , ("file:///example/path",            "file:///example/path")
            , ("file://example.com/path",         "file://example.com/path")
            ])
        test_value_context_renders = (
            [ (self._make_test_context(linktext, target_link=linktext),  expect_render(linktext, alttext))
                for linktext, alttext in test_values
            ])
        renderer = get_ref_audio_renderer()

        for render_context, expect_render in test_value_context_renders:
            # print repr(render_context['field']['field_value'])
            self._check_value_renderer_results(
                renderer,
                context=render_context,
                expect_rendered_view=expect_render['view'],
                expect_rendered_edit=expect_render['edit']
                )
        return

    def test_DecodeRefAudioValue(self):
        test_decode_values = (
            { None:                         ""
            , "http://example.com/path":    "http://example.com/path"
            , "https://example.com/path":   "https://example.com/path"
            , "file:///example/path":       "file:///example/path"
            , "file://example.com/path":    "file://example.com/path"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = RefAudioValueMapper.decode(valtext)
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
