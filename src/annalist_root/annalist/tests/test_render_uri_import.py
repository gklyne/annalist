"""
Tests for text value used as URI for import object; view as hyperlink.

The text value is taken to be a URI or URI reference.

@@TODO: later developments should also support CURIES (cf. issue #19,
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

from annalist.resourcetypes                 import file_extension, file_extension_for_content_type

from annalist.views.fields.render_uri_import import (
    get_uri_import_renderer, 
    URIImportValueMapper
    )

from annalist.tests.field_rendering_support import FieldRendererTestSupport

class UriImportRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Supporting tests

    def test_resourcetypes(self):
        self.assertEqual(file_extension("annal:Text"),     "txt")
        self.assertEqual(file_extension("annal:Richtext"), "md")
        self.assertEqual(file_extension("annal:Image"),    "png")
        self.assertEqual(file_extension("ex:foo"),         "dat")
        self.assertEqual(file_extension_for_content_type("annal:Text",     "text/plain"),       "txt")
        self.assertEqual(file_extension_for_content_type("annal:Richtext", "text/markdown"),    "md")
        self.assertEqual(file_extension_for_content_type("annal:Richtext", "text/plain"),       "txt")
        self.assertEqual(file_extension_for_content_type("annal:Image",    "image/jpeg"),       "jpg")
        self.assertEqual(file_extension_for_content_type("ex:foo", "application/octet-stream"), "dat")
        self.assertEqual(file_extension_for_content_type("ex:foo", "image/jpeg"),               None)
        return

    # Rendering test

    def test_RenderUriImportValue(self):

        def expect_render(linktext, labeltext):
            render_view = '''<a href="%s" target="_blank">%s</a>'''%(linktext, labeltext)
            render_edit = (
                '''<div class="row"> '''+
                  '''<div class="small-10 columns view-value view-subfield less-import-button"> '''+
                    '''<input type="text" size="64" name="repeat_prefix_test_field" '''+
                           '''placeholder="(test placeholder)" '''+
                           '''value="%s" /> '''+
                  '''</div> '''+
                  '''<div class="small-2 columns view-value view-subfield import-button left small-text-right"> '''+
                    '''<input type="submit" name="repeat_prefix_test_field__import" value="Import" /> '''+
                  '''</div> '''+
                '''</div> '''
                # '''<input type="text" size="64" name="repeat_prefix_test_field" '''+
                #        '''placeholder="(test placeholder)" '''+
                #        '''value="%s" />'''+
                # '''&nbsp;'''+
                # '''<input type="submit" name="repeat_prefix_test_field__import" value="Import" />'''
                )%linktext
            return {'view': render_view, 'edit': render_edit}

        def import_uri_value(uri):
            return {'import_url': uri}

        test_values = (
            [ (import_uri_value("http://example.com/path"),   "example.com/path")
            , (import_uri_value("https://example.com/path"),  "example.com/path")
            , (import_uri_value("file:///example/path"),      "example/path")
            , (import_uri_value("file://example.com/path"),   "example.com/path")
            , (import_uri_value("mailto:user@example.com"),   "user@example.com")
            , (import_uri_value("foo://example.com/more"),    "foo://example.com/more")
            ])
        test_value_context_renders = (
            [ (self._make_test_context(linktext),  expect_render(linktext['import_url'], labeltext))
                for linktext, labeltext in test_values
            ])
        renderer = get_uri_import_renderer()

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

    def test_DecodeUriImportValue(self):
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
            valdata = URIImportValueMapper.decode(valtext)
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
