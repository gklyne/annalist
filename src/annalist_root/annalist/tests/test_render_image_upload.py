"""
Tests for image upload field; view as image.
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

from annalist.views.fields.field_renderer import FieldRenderer
from annalist.views.fields.render_ref_image import RefImageValueMapper
from .field_rendering_support import FieldRendererTestSupport

class ImageUploadRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Rendering test

    def test_RenderImageUploadValue(self):

        def upload_file_value(file):
            return {'resource_name': "uploaded.jpg", 'uploaded_file': file}

        def expect_render(value, linktext, alttext):
            render_view = (
                '''<a href="%s" target="_blank">'''%(linktext)+
                  '''<img src="%s" alt="Image at '%s'" />'''%(linktext, linktext)+
                '''</a>'''
                )
            if value:
                labeltext = '''Previously uploaded: %s '''%alttext
            else:
                labeltext = ""
            render_edit = (
                ('''<input type="file" name="repeat_prefix_test_field" '''+
                       '''placeholder="(test placeholder)" '''+
                       '''value="%s" /> '''
                )%(linktext,) + labeltext
                )
            return {'view': render_view, 'edit': render_edit}

        no_resource = "(@@resource_name not present)"
        test_values = ( # field value, linktext, alttext
            [ ("",                                  "uploaded.data", no_resource)
            , (upload_file_value("test-image.jpg"), "uploaded.jpg",  "test-image.jpg")
            , ("test-image.jpg",                    "uploaded.data", "test-image.jpg")
            ])
        test_value_context_renders = (
            [ ( self._make_test_context(value, target_link=linktext),
                expect_render(value, linktext, alttext)
              ) for value, linktext, alttext in test_values
            ])
        renderer = FieldRenderer("RefImage", "Value_upload")
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

    def test_DecodeImageUploadValue(self):
        test_decode_values = (
            { None:                 ""
            , "test-image.jpg":     "test-image.jpg"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = RefImageValueMapper.decode(valtext)
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
