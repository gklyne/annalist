"""
Support methods for field value renderer tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import os
import re
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings
from django.template                        import Context, Template, loader

from annalist.views.fields.render_placement import Placement, get_placement_classes

from annalist.tests.tests                   import TestHost, TestHostUri, TestBasePath, TestBaseUri
from annalist.tests.AnnalistTestCase        import AnnalistTestCase


class TestBoundField(object):

    def __init__(self, field_dict,
            target_value=None, 
            field_link=None, 
            target_link=None, 
            field_ref_type=None,
            options=None,
            continuation_url="test_cont"
        ):
        self._field = dict(field_dict)
        if field_ref_type is not None:
            self._field['description']['field_ref_type'] = field_ref_type
        if target_value is not None:
            self._field['target_value'] = target_value
        #@@@@
        if field_link is not None:
            self._field['field_value_link']               = field_link
        #     self._field['field_value_link_continuation']  = field_link+"?continuation_url="+continuation_url
        if target_link is not None:
            self._field['target_value_link']              = target_link
        #     self._field['target_value_link_continuation'] = target_link+"?continuation_url="+continuation_url
        #@@@@
        if options is not None:
            self._field['options'] = options
        return

    def __getattr__(self, name):
        #@@@@
        # if name in ["entity_id", "entity_link", "entity_type_id", "entity_type_link"]:
        #     return self.value.get(name, "")
        # elif name == "entity_value":
        #     return self.value
        # elif name == "field_value_key":
        #     return self._key
        #@@@@
        if name == "_field":
            return self._field
        elif name in ["description"]:
            return self._field["description"]
        elif name == "field_id":
            return self._field["description"].get("field_id", None)
        elif name == "field_name":
            return self._field["description"].get("field_name", None)
        elif name == "field_tooltip_attr":
            return ""
        elif name in ["field_value", "field_edit_value"]:
            return self._field["target_value"]
        #@@@@
        # elif name == "field_value_link":
        #     return self._field["field_value_link"]
        #@@@@
        elif name == "options":
            return self._field["options"]
        #@@@@
        # elif name == "context_extra_values":
        #     return self._extras
        #@@@@
        attr = "@@TestBoundField.%s@@"%(name,)
        return attr

    # Define methods to facilitate access to values using dictionary operations
    # on the FieldDescription object

    def keys(self):
        """
        Return collection metadata value keys
        """
        return self._field.keys()

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._field.items()

    def get(self, k, default):
        """
        Equivalent to dict.get() function
        """
        return self[k] if self._field and k in self._field else default

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._field[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._field[k] = v
        return

    def __iter__(self):
        """
        Iterator over dictionary keys
        """
        for k in self._field:
            yield k
        return


#   -----------------------------------------------------------------------------
#
#   Field renderer tests support
#
#   -----------------------------------------------------------------------------

class FieldRendererTestSupport(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        return

    def tearDown(self):
        return

    def assertRenderMatch(self, rendered, expected, collapse_whitespace=False):
        rendered = re.sub(r'<!--.*-->\n', "", rendered)
        if collapse_whitespace:
            rendered = re.sub(r'\s+', " ", rendered).strip()
            expected = re.sub(r'\s+', " ", expected).strip()
        if rendered != expected:
            log.info("rendered "+rendered)
            log.info("expected "+expected)
        self.assertEqual(rendered, expected)
        return

    def _make_test_context(self, val, 
            repeat_prefix="repeat_prefix_", 
            target_value=None, 
            field_link=None, 
            target_link=None, 
            field_ref_type=None,
            options=None,
            coll_id="testcoll", coll=None
        ):
        fd = (
            { 'field_placement':      get_placement_classes("small:0,12")
            , 'field_name':           "test_field"
            , 'field_label':          "test label"
            , 'field_value':          val
            , 'field_edit_value':     val
            , 'target_value':         val     # Mimics bound_field default behaviour
            , 'field_view_value':     val
            , 'continuation_param':   "?continuation_url=test_cont"
            , 'description':
                { 'field_id':             "test_field"
                , 'field_name':           "test_field"
                , 'field_label':          "test label"
                , 'field_placement':      get_placement_classes("small:0,12")
                , 'field_placeholder':    "(test placeholder)"
                }
            })
        cd = (
            { 'field': TestBoundField(fd,
                            target_value=target_value, 
                            field_link=field_link, 
                            target_link=target_link, 
                            field_ref_type=field_ref_type,
                            options=options,
                            continuation_url="test_cont"
                            )
            , 'collection':           coll
            , 'repeat_prefix':        repeat_prefix
            , 'HOST':                 TestHostUri
            , 'SITE':                 TestBaseUri
            , 'COLL':                 TestBaseUri+"/c/"+coll_id+"/"
            , 'BASE':                 TestBasePath+"/c/"+coll_id+"/d/"
            })
        #@@@@
        # if target_value is not None:
        #     cd['field']['target_value'] = target_value
        # if field_link is not None:
        #     cd['field']['field_value_link']              = field_link
        #     cd['field']['field_value_link_continuation'] = field_link+"?continuation_url=test_cont"
        # if target_link is not None:
        #     cd['field']['target_value_link']              = target_link
        #     cd['field']['target_value_link_continuation'] = target_link+"?continuation_url=test_cont"
        # if field_ref_type is not None:
        #     cd['field']['field_ref_type'] = field_ref_type
        # if options is not None:
        #     cd['field']['options'] = options
        #@@@@
        return Context(cd)

    def _check_value_renderer_results(self,
        fieldrender, context=None,
        expect_rendered_view="...", 
        expect_rendered_edit="...",
        collapse_whitespace=False
        ):
        #@@@@
        #@@ - method unused, deprecated.  When stabilized, remove this code.
        # rendered_label = fieldrender.label().render(context)
        # self.assertRenderMatch(
        #     rendered_label, 
        #     '''<div class="view-label small-12 columns">  <span>test label</span></div>''',
        #     collapse_whitespace
        #     )
        #@@
        #@@@@
        rendered_view = fieldrender.view().render(context)
        self.assertRenderMatch(
            rendered_view, 
            '''<div class="view-value small-12 columns">\n  %s\n</div>'''%expect_rendered_view,
            collapse_whitespace
            )
        rendered_edit = fieldrender.edit().render(context)
        self.assertRenderMatch(
            rendered_edit, 
            '''<div class="view-value small-12 columns">\n  %s\n</div>'''%expect_rendered_edit,
            collapse_whitespace
            )
        rendered_label_view = fieldrender.label_view().render(context)
        self.assertRenderMatch(
            rendered_label_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row view-value-row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''    <div class="view-value small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_label_edit = fieldrender.label_edit().render(context)
        self.assertRenderMatch(
            rendered_label_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row view-value-row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''    <div class="view-value small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_head = fieldrender.col_head().render(context)
        self.assertRenderMatch(
            rendered_col_head, 
            '''<div class="view-label col-head small-12 columns">\n'''+
            '''  <span>test label</span>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_view = fieldrender.col_view().render(context)
        self.assertRenderMatch(
            rendered_col_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row view-value-col">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        rendered_col_edit = fieldrender.col_edit().render(context)
        self.assertRenderMatch(
            rendered_col_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <span>test label</span>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row view-value-col">\n'''+
            '''    <div class="view-value small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>''',
            collapse_whitespace
            )
        return

# End.
