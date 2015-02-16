"""
Tests for rendering value as selection from list of options
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

from annalist.views.fields.render_select        import (
    get_select_renderer, get_choice_renderer, 
    SelectValueMapper
    )

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

#   ---- support methods ----

def expect_render_option(choice_val, select_val, placeholder):
    selected    = ''' selected="selected"''' if choice_val == select_val else ''''''
    if choice_val == "":
        choice_text = placeholder
        value_text  = ''' value=""'''
    else:
        choice_text = choice_val
        value_text  = ''''''
    return '''<option%s%s>%s</option>'''%(value_text, selected, choice_text)

def expect_render_select(select_name, choice_list, select_val, placeholder):
    if select_val not in choice_list:
        choice_list = list(choice_list)     # Clone
        choice_list.insert(0, select_val)
    sel  = """<select name="%s">"""%select_name
    opts = [ expect_render_option(choice_val, select_val, placeholder) for choice_val in choice_list ]
    end  = "</select>\n"
    return "\n".join([sel]+opts+[end])

#   ---- test class ----

class SelectRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def _make_select_test_context(self, valtext, vallink, valchoices):
        if valtext not in valchoices:
            vallink = None
        # print "_make_select_test_context: valtext %r, valchoices %r, vallink %s"%(valtext, valchoices, vallink)
        return self._make_test_context(valtext, options=valchoices, link=vallink)

    def test_RenderChoiceValue(self):
        def expect_render(valtext, vallink, valchoices):
            if vallink and valtext in valchoices:
                render_view = """<a href="%s">%s</a> """%(vallink+"?continuation_url=test_cont", valtext)
            else:
                render_view = """<span>%s</span> """%(valtext)
            render_edit = expect_render_select(
                "repeat_prefix_test_field",
                valchoices, 
                valtext, 
                "(test placeholder)"
                )
            return {'view': render_view, 'edit': render_edit}
        test_values = (
            [ ( u"aa", "http://example.org/aa", ["aa", "bb", "cc"])
            , ( u"",   None,                    ["", "aa", "bb", "cc"])
            , ( u"dd", "http://example.org/dd", ["aa", "bb", "cc"])
            , ( u"",   None,                    ["aa", "bb", "cc"])
            ])
        test_value_context_renders = (
            [ ( self._make_select_test_context(valtext, vallink, valchoices), 
                expect_render(valtext, vallink, valchoices)
              ) for valtext, vallink, valchoices in test_values
            ])
        renderer = get_choice_renderer()
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


    def test_RenderSelectValue(self):
        def expect_render(valtext, vallink, valchoices):
            if vallink and valtext in valchoices:
                render_view = """<a href="%s">%s</a> """%(vallink+"?continuation_url=test_cont", valtext)
            else:
                render_view = """<span>%s</span> """%(valtext)
            select = expect_render_select(
                "repeat_prefix_test_field",
                valchoices, 
                valtext, 
                "(test placeholder)"
                )
            render_edit = (
                '''<div class="row">\n'''+
                '''  <div class="small-10 columns view-value less-new-button">\n'''+
                '''    %s\n'''+
                '''  </div>\n'''+
                '''  <div class="small-2 columns view-value new-button left small-text-right">\n'''+
                '''    <button type="submit" \n'''+
                '''            name="%s__new" \n'''+
                '''            value="New"\n'''+
                '''            title="Define new %s"\n'''+
                '''    >\n'''+
                '''      +\n'''+
                '''    </button>\n'''+
                '''  </div>\n'''+
                '''</div>\n'''
                )%(select, "repeat_prefix_test_field", "test label")
            return {'view': render_view, 'edit': render_edit}
        test_values = (
            [ ( u"aa", "http://example.org/aa", ["aa", "bb", "cc"])
            , ( u"",   "http://example.org/aa", ["", "aa", "bb", "cc"])
            , ( u"dd", "http://example.org/aa", ["aa", "bb", "cc"])
            , ( u"",   "http://example.org/aa", ["aa", "bb", "cc"])
            ])
        test_value_context_renders = (
            [ ( self._make_select_test_context(valtext, vallink, valchoices), 
                expect_render(valtext, vallink, valchoices)
              ) for valtext, vallink, valchoices in test_values
            ])
        renderer = get_select_renderer()
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

    def test_DecodeSelectValue(self):
        test_decode_values = (
            { None:         None
            , "":           ""
            , "text":       "text"
            })
        for valtext, expect_valdata in test_decode_values.items():
            valdata = SelectValueMapper.decode(valtext)
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
