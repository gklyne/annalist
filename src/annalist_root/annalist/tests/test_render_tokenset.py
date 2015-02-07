"""
Tests for token set rendering functions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import unittest
import re

import logging
log = logging.getLogger(__name__)

# from django.conf                        import settings
# from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
# from django.template                    import Context, Template, loader

from utils.SuppressLoggingContext           import SuppressLogging

from annalist.views.fields.render_tokenset  import get_field_tokenset_renderer, TokenSetValueMapper

from field_rendering_support                import FieldRendererTestSupport

class TokenSetRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        # init_annalist_test_site()
        # self.testsite = Site(TestBaseUri, TestBaseDir)
        # self.testcoll = Collection(self.testsite, "testcoll")
        self.tokenset_context  = self._make_test_context(
            ["aa", "bb", "cc"], repeat_prefix="tokprefix_"
            )
        # self.intvalue_context  = self._make_test_context(42, repeat_prefix="intprefix_")
        return

    def tearDown(self):
        return

    # Tests

    def test_TokenSetValueMapperTest(self):
        self.assertEqual(
            TokenSetValueMapper.__name__, "TokenSetValueMapper", 
            "Check TokenSetValueMapper class name"
            )
        return

    def test_TokenSetValueMapperEncode(self):
        fieldrender = TokenSetValueMapper()
        self.assertEqual(fieldrender.encode(["aa"]), "aa")
        self.assertEqual(fieldrender.encode(["aa", "bb", "cc" ]), "aa bb cc")
        # Rendering non-list generates warning
        with SuppressLogging(logging.WARNING):
            self.assertEqual(fieldrender.encode("aa"), "aa")
        return

    def test_TokenSetValueMapperDecode(self):
        fieldrender = TokenSetValueMapper()
        self.assertEqual(fieldrender.decode("aa"), ["aa"])
        self.assertEqual(fieldrender.decode("aa bb cc"), ["aa", "bb", "cc"])
        return

    def test_TokenSetRender_Edit(self):
        fieldrender   = get_field_tokenset_renderer().label_edit()
        rendered_text = fieldrender.render(self.tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row view-value-row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <span>test label</span> </div>'''
            , '''<div class="view-value small-12 medium-10 columns">'''
            , '''<input type="text" size="64" name="tokprefix_test_field" '''+
              '''placeholder="(test placeholder)" value="aa bb cc"/>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_TokenSetRender_View(self):
        fieldrender   = get_field_tokenset_renderer().label_view()
        rendered_text = fieldrender.render(self.tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row view-value-row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <span>test label</span> </div>'''
            , '''<div class="view-value small-12 medium-10 columns"> aa bb cc </div>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_TokenSetRender_Item(self):
        fieldrender   = get_field_tokenset_renderer().col_view()
        rendered_text = fieldrender.render(self.tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="view-label small-12 columns">'''+
              ''' <span>test label</span> '''+
              '''</div>'''
            , '''<div class="view-value small-12 columns">'''+
              ''' aa bb cc '''+
              '''</div>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
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
