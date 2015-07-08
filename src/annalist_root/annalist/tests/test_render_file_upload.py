"""
Tests for file upload field; view as hyperlink.
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

from annalist.views.fields.render_file_upload import (
    get_file_upload_renderer, 
    FileUploadValueMapper
    )

from annalist.tests.field_rendering_support import FieldRendererTestSupport

class FileUploadRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    # Rendering test

    def test_RenderFileUploadValue(self):

        def expect_render(filename, labeltext):
            # render_view = '''<a href="%s" target="_blank">%s</a>'''%(filename, labeltext)
            # render_edit = (
            #     '''<input type="file" name="repeat_prefix_test_field" '''+
            #            '''placeholder="(test placeholder)" '''+
            #            '''value="%s" /> '''
            #     )%filename
            render_view = (
                '''Uploaded file <a href="%s" target="_blank">%s</a>'''
                )%(filename, labeltext)
            render_edit = (
                '''<input type="file" name="repeat_prefix_test_field" '''+
                       '''placeholder="(test placeholder)" '''+
                       '''value="%s" /> '''+
                '''Previously uploaded: %s '''
                )%(filename, labeltext)
            return {'view': render_view, 'edit': render_edit}

        def upload_file_value(file):
            return {'resource_name': file, 'uploaded_file': "uploaded.ext"}

        test_values = (
            [ (upload_file_value("testfile.ext"),   "uploaded.ext")
            ])
        test_value_context_renders = (
            [ (self._make_test_context(filename),  expect_render(filename['resource_name'], labeltext))
                for filename, labeltext in test_values
            ])
        renderer = get_file_upload_renderer()

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

    def test_DecodeFileUploadValue(self):
        test_decode_values = (
            { None:                 ""
            , "testfile.ext":       "testfile.ext"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = FileUploadValueMapper.decode(valtext)
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
