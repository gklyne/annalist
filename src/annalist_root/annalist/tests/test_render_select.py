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

from annalist.views.fields.render_select        import (
    get_select_renderer, get_choice_renderer, 
    SelectValueMapper
    )
from annalist.views.form_utils.fieldchoice      import FieldChoice

from annalist.tests.field_rendering_support     import FieldRendererTestSupport

#   ---- support methods ----

def expect_render_option(choice_val, select_val, placeholder):
    selected    = ''' selected="selected"''' if choice_val == select_val else ''''''
    if choice_val == "":
        choice_text = placeholder
        value_text  = ''' value=""'''
    else:
        choice_text = "label "+choice_val
        value_text  = ''' value="opt_type/%s"'''%choice_val
    return '''<option%s%s>%s</option>'''%(value_text, selected, choice_text)

def expect_render_select(select_name, choice_list, select_val, placeholder):
    sel  = """<select name="%s">"""%select_name
    if select_val not in choice_list:
        val = "opt_type/"+select_val if select_val else ""
        lab = "opt_type/"+select_val if select_val else placeholder
        nopt = ['''<option value="%s" selected="selected">%s</option>'''%(val, lab)]
    else:
        nopt = []
    opts = [ expect_render_option(choice_val, select_val, placeholder) for choice_val in choice_list ]
    end  = "</select>\n"
    return "\n".join([sel]+nopt+opts+[end])

#   ---- test class ----

class SelectRenderingTest(FieldRendererTestSupport):

    def setUp(self):
        return

    def tearDown(self):
        return

    def _make_select_test_context(self, valkey, vallink, valchoices, valplaceholder):
        valtext = "opt_type/"+valkey if valkey else ""
        if valkey not in valchoices:
            vallink = None
        # log.info(
        #     "_make_select_test_context: valtext %r, vallink %r, valchoices %r"%
        #     (valtext, vallink, valchoices)
        #     )
        valoptions = []
        for c in valchoices:
            if c != "":
                val = "opt_type/"+c
                lab = "label "+c
            else:
                val = ""
                lab = valplaceholder
            lnk = vallink if val == valtext else "@@no_link@@"
            valoptions.append(FieldChoice(val, label=lab, link=lnk))
        # log.info(
        #     "_make_select_test_context: valoptions %r"%
        #     (valoptions,)
        #     )
        return self._make_test_context(valtext, field_ref_type="ref_type", options=valoptions, field_link=vallink)

    def test_RenderChoiceValue(self):
        def expect_render(valkey, vallabel, vallink, valchoices):
            valcont = "?continuation_url=test_cont"
            valcont = ""
            if vallink and valkey in valchoices:
                render_view = """<a href="%s">%s</a> """%(vallink+valcont, vallabel)
            elif valkey == "":
                render_view = """<span class="value-blank">%s</span> """%(vallabel)
            else:
                render_view = """<span class="value-missing">%s</span> """%(vallabel)
            render_edit = expect_render_select(
                "repeat_prefix_test_field",
                valchoices, 
                valkey, 
                "(test placeholder)"
                )
            return {'view': render_view, 'edit': render_edit}
        noval = "(No 'test label' selected)"
        test_values = (
            [ ( "aa", "label aa",    "http://example.org/aa", ["aa", "bb", "cc"])
            , ( "",   noval,         None,                    ["", "aa", "bb", "cc"])
            , ( "dd", "opt_type/dd", "http://example.org/dd", ["aa", "bb", "cc"])
            , ( "",   noval,         None,                    ["aa", "bb", "cc"])
            ])
        test_value_context_renders = (
            [ ( self._make_select_test_context(valkey, vallink, valchoices, noval), 
                expect_render(valkey, vallabel, vallink, valchoices)
              ) for valkey, vallabel, vallink, valchoices in test_values
            ])
        renderer = get_choice_renderer()
        for render_context, expect_render in test_value_context_renders:
            # log.info("test_RenderChoiceValue: value  %(field_value)r"%render_context['field'])
            # log.info("test_RenderChoiceValue: expect %s"%(expect_render,))
            self._check_value_renderer_results(
                renderer,
                context=render_context,
                expect_rendered_view=expect_render['view'],
                expect_rendered_edit=expect_render['edit'],
                collapse_whitespace=True
                )
        return

    def test_RenderSelectValue(self):
        def expect_render(valkey, vallabel, vallink, valchoices):
            valcont = "?continuation_url=test_cont"
            valcont = ""
            if vallink and valkey in valchoices:
                render_view = (
                    """<a href="%s">%s</a> """%
                    (vallink+valcont, vallabel)
                    )
            elif valkey == "":
                render_view = """<span class="value-blank">%s</span> """%(vallabel)
            else:
                render_view = """<span class="value-missing">%s</span> """%(vallabel)
            select = expect_render_select(
                "repeat_prefix_test_field",
                valchoices, 
                valkey, 
                "(test placeholder)"
                )
            render_edit = (
                '''<div class="row">\n'''+
                '''  <div class="small-10 columns view-value less-new-button">\n'''+
                '''    %s\n'''+
                '''  </div>\n'''+
                '''  <div class="small-2 columns view-value new-button left small-text-right">\n'''+
                '''    <button type="submit" \n'''+
                '''            name="%s__new_edit" \n'''+
                '''            value="New"\n'''+
                '''            title="Define new %s"\n'''+
                '''    >\n'''+
                '''      <span class="select-edit-button-text">+&#x270D;</span>\n'''+
                '''    </button>\n'''+
                '''  </div>\n'''+
                '''</div>\n'''
                )%(select, "repeat_prefix_test_field", "test label")
            return {'view': render_view, 'edit': render_edit}
        noval = "(No 'test label' selected)"
        test_values = (
            [ ( "aa", "label aa",    "http://example.org/aa", ["aa", "bb", "cc"])
            , ( "",   noval,         None,                    ["", "aa", "bb", "cc"])
            , ( "dd", "opt_type/dd", "http://example.org/dd", ["aa", "bb", "cc"])
            , ( "",   noval,         None,                    ["aa", "bb", "cc"])
            ])
        test_value_context_renders = (
            [ ( self._make_select_test_context(valtext, vallink, valchoices, noval), 
                expect_render(valtext, vallabel, vallink, valchoices)
              ) for valtext, vallabel, vallink, valchoices in test_values
            ])
        renderer = get_select_renderer()
        for render_context, expect_render in test_value_context_renders:
            # log.info(repr(render_context['field']['field_value']))
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
