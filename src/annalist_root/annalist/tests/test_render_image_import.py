"""
Tests for image import field; view as image.
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

class ImageImportRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Rendering test

    def test_RenderImageImportValue(self):

        def import_url_value(url):
            return {'resource_name': "imported.jpg", 'import_url': url}

        def expect_render(value, linktext, alttext):
            render_view = (
                '''<a href="%s" target="_blank">'''%(linktext)+
                  '''<img src="%s" alt="Image at '%s'" />'''%(linktext, linktext)+
                '''</a>'''
                )
            if value:
                labeltext = '''Previously imported: %s '''%alttext
            else:
                labeltext = ""
            render_edit = (
                '''<div class="row"> '''+
                  '''<div class="small-10 columns view-value view-subfield less-import-button"> '''+
                    '''<input type="text" size="64" '''+
                      '''name="repeat_prefix_test_field" '''+
                      '''placeholder="(test placeholder)" value="%s" /> '''%(alttext,)+
                  '''</div> '''+
                  '''<div class="small-2 columns view-value view-subfield import-button left small-text-right"> '''+
                    '''<input type="submit" '''+
                      '''name="repeat_prefix_test_field__import" '''+
                      '''value="Import" /> '''+
                  '''</div> '''+
                '''</div>'''
                )
            return {'view': render_view, 'edit': render_edit}

        no_resource = ""
        test_values = ( # field value, linktext, alttext
            [ ("",                                 "imported.jpg", no_resource)
            , (import_url_value("test-image.jpg"), "imported.jpg", "test-image.jpg")
            , ("test-image.jpg",                   "imported.jpg", "test-image.jpg")
            ])
        test_value_context_renders = (
            [ ( self._make_test_context(value, target_link=linktext),
                expect_render(value, linktext, alttext)
              ) for value, linktext, alttext in test_values
            ])
        renderer = FieldRenderer("RefImage", "Value_import")
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

    def test_DecodeImageImportValue(self):
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
