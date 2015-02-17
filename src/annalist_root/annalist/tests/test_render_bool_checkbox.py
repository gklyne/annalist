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

from annalist.views.fields.render_bool_checkbox import (
    get_bool_checkbox_renderer, 
    BoolCheckboxValueMapper
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

class BooleanCheckboxRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_RenderBoolCheckboxValue(self):

        def expect_render(val):
            if isinstance(val, str):
                valtext = val
                valbool = val.lower() in ["true", "yes"]
            else:
                valtext = "Yes" if val else "No"
                valbool = val
            checked     = ''' checked="checked"''' if valbool else ''''''
            render_view = '''<span>%s</span>'''%valtext
            render_edit = (
                '''<input type="checkbox" '''+
                       '''name="repeat_prefix_test_field" '''+
                       ('''value="%s"%s'''%(valtext,checked)) +
                       ''' />'''+
                  ''' <span class="value-placeholder">(test placeholder)</span>'''
                )
            return {'view': render_view, 'edit': render_edit}

        test_value_context_renders = (
            [ (self._make_test_context(None),    expect_render(False))
            , (self._make_test_context(False),   expect_render(False))
            , (self._make_test_context(True),    expect_render(True))
            , (self._make_test_context("False"), expect_render("False"))
            , (self._make_test_context("True"),  expect_render("True"))
            , (self._make_test_context("Yes"),   expect_render("Yes"))
            , (self._make_test_context("No"),    expect_render("No"))
            , (self._make_test_context(u"yes"),  expect_render("yes"))
            , (self._make_test_context(u"no"),   expect_render("no"))
            ])
        renderer = get_bool_checkbox_renderer()

        for render_context, expect_render in test_value_context_renders:
            # print repr(render_context['field']['field_value'])
            self._check_value_renderer_results(
                renderer,
                context=render_context,
                expect_rendered_view=expect_render['view'],
                expect_rendered_edit=expect_render['edit']
                )
        return

    def test_DecodeBoolCheckboxValue(self):
        # Any text other than None or empty string indicates the box is checked, returns True
        test_decode_values = (
            { None:         False
            , "":           False
            , "checked":    True
            , "No":         True
            , "Yes":        True
            , "False":      True
            , "True":       True
            , "false":      True
            , "true":       True
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = BoolCheckboxValueMapper.decode(valtext)
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
