"""
Tests for field rendering functions
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

from django.conf                        import settings
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.template                    import Context, Template, loader

# from bs4                                import BeautifulSoup

from utils.SuppressLoggingContext       import SuppressLogging

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist.models.site               import Site
from annalist.models.collection         import Collection

from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field

from annalist.views.fields.render_text          import RenderText
from annalist.views.fields.render_placement     import Placement, get_placement_classes
from annalist.views.fields.render_tokenset      import get_field_tokenset_renderer, TokenSetValueMapper
from annalist.views.fields.render_placement     import get_field_placement_renderer
from annalist.views.fields                      import render_repeatgroup
from annalist.views.fields.render_repeatgroup   import RenderRepeatGroup
from annalist.views.fields.render_fieldvalue    import RenderFieldValue, get_template

from tests                  import init_annalist_test_site
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from AnnalistTestCase       import AnnalistTestCase

from entity_testentitydata  import entity_url

#   -----------------------------------------------------------------------------
#
#   Test data
#
#   -----------------------------------------------------------------------------

tokenset_context = Context(
    { 'field':
      { 'field_placement':      get_placement_classes("small:0,12")
      , 'field_name':           "test_field"
      , 'field_label':          "test label"
      , 'field_placeholder':    "(test placeholder)"
      , 'field_value':          ["aa", "bb", "cc"]
      }
    # , 'repeat':
    #   { 'repeat_prefix':        "prefix_"
    #   }
    , 'repeat_prefix':        "tokprefix_"
    })

intvalue_context = Context(
    { 'field':
      { 'field_placement':      get_placement_classes("small:0,12")
      , 'field_name':           "test_field"
      , 'field_label':          "test label"
      , 'field_placeholder':    "(test placeholder)"
      , 'field_value':          42
      }
    # , 'repeat':
    #   { 'repeat_prefix': "prefix_"
    #   }
    , 'repeat_prefix':        "intprefix_"
    })

placement_context = Context(
    { 'field':
      { 'field_placement':      get_placement_classes("small:0,12")
      , 'field_name':           "test_field"
      , 'field_label':          "test label"
      , 'field_placeholder':    "(test placeholder)"
      , 'field_value':          "small:0,12;medium:4,4"
      }
    # , 'repeat':
    #   { 'repeat_prefix': "prefix_"
    #   }
    , 'repeat_prefix': "repeat_prefix_"
    })

#   -----------------------------------------------------------------------------
#
#   FieldDescription tests
#
#   -----------------------------------------------------------------------------

class FieldDescriptionTest(AnnalistTestCase):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        return

    def tearDown(self):
        return

    def get_repeatgroup_context(self):
        # context['field'] is essentially a bound_field value, combining the repeat group
        # description with a list of entity values to be formatted.
        repeatgroup_context = Context(
            { 'field':
                # ----- Repeated field values, as presented by bound_field
                { 'field_value':
                  [ { "annal:field_id":         "Entity_id"
                    , "annal:field_placement":  "small:0,12;medium:0,6"
                    }
                  , { "annal:field_id":         "Entity_type"
                    , "annal:field_placement":  "small:0,12;medium:6,6"
                    }
                  , { "annal:field_id":         "Entity_label"
                    , "annal:field_placement":  "small:0,12"
                    , "annal:property_uri":     "rdfs:label"
                    }
                  , { "annal:field_id":         "Entity_comment"
                    , "annal:field_placement":  "small:0,12"
                    , "annal:property_uri":     "rdfs:comment"
                    }
                  ]
                # ----- Field description -----
                , 'field_id':                   'View_fields'
                , 'field_name':                 'View_fields'
                , 'field_label':                'Fields'
                , 'field_help':                 'This resource descibes the repeated field description used when displaying and/or editing a record view description'
                , 'field_placeholder':          '(repeat field description)'
                , 'field_placement':            get_placement_classes("small:0,12")
                , 'field_property_uri':         'annal:view_fields'
                , 'field_value_type':           'annal:Field_group'
                , 'field_group_ref':            'View_field_view'
                , 'field_render_type':          'RepeatGroup'
                , 'group_id':                   'View_fields'
                , 'group_label':                'Fields'
                , 'group_add_label':            'Add field'
                , 'group_delete_label':         'Remove selected field(s)'
                , 'group_field_descs':
                    [ field_description_from_view_field(
                        self.testcoll, { ANNAL.CURIE.field_id: "Group_field_sel" },        {}
                        )
                    , field_description_from_view_field(
                        self.testcoll, { ANNAL.CURIE.field_id: "Group_field_property" },   {}
                        )
                    , field_description_from_view_field(
                        self.testcoll, { ANNAL.CURIE.field_id: "Group_field_placement" },  {}
                        )
                    ]
                , 'context_extra_values':       {}
                }
            # ----- other values -----
            , 'auth_config':                  True
            })
        return repeatgroup_context

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
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <p>test label</p> </div>'''
            , '''<div class="small-12 medium-10 columns">'''
            , '''<input type="text" size="64" name="tokprefix_test_field" '''+
              '''placeholder="(test placeholder)" value="aa bb cc"/>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_TokenSetRender_View(self):
        fieldrender   = get_field_tokenset_renderer().label_view()
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <p>test label</p> </div>'''
            , '''<div class="small-12 medium-10 columns"> aa bb cc </div>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_TokenSetRender_Item(self):
        fieldrender   = get_field_tokenset_renderer().col_view()
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="view-label small-12 columns">'''+
              ''' <p>test label</p> '''+
              '''</div>'''
            , '''<div class="small-12 columns">'''+
              ''' aa bb cc '''+
              '''</div>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_RenderRepeatGroupTest(self):
        # print "\n".join(sys.path)
        # template = loader.get_template('field/annalist_edit_select.html')
        self.assertEqual(
            RenderRepeatGroup.__name__, "RenderRepeatGroup", 
            "Check RenderRepeatGroup class name"
            )
        return

    def test_RenderRepeatGroupEdit(self):
        fieldrender   = RenderRepeatGroup(render_repeatgroup.edit_group)
        rendered_text = fieldrender.render(self.get_repeatgroup_context())
        # print "\n**************\n"
        # print rendered_text
        # print "\n**************\n"
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-2 columns"> <p class="group-label">Fields</p> </div>'''
            , '''<div class="row selectable">'''
            , '''<p>Field id</p>'''
            , '''<p>Property</p>'''
            , '''<p>Position/size</p>'''
            # 1st field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="0" class="right" />'''
            , '''<select name="View_fields__0__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option selected="selected">Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__0__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            # 2nd field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="1" class="right" />'''
            , '''<select name="View_fields__1__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option selected="selected">Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__1__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            # 3rd field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="2" class="right" />'''
            , '''<select name="View_fields__2__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option selected="selected">Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__2__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value="rdfs:label"/>'''
            # 4th field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="3" class="right" />'''
            , ''' <select name="View_fields__3__Field_id">'''+
              ''' <option selected="selected">Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__3__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value="rdfs:comment"/>'''
            # Buttons
            , '''<input type="submit" name="View_fields__remove" value="Remove selected field(s)" />'''
            , '''<input type="submit" name="View_fields__add" value="Add field" />'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def _check_value_renderer_results(self,
        fieldrender, context=None,
        expect_rendered_view="...", 
        expect_rendered_edit="..."
        ):
        rendered_label      = fieldrender.label().render(context)
        self.assertEqual(
            rendered_label, 
            '''<div class="view-label small-12 columns">  <p>test label</p></div>'''
            )
        rendered_view       = fieldrender.view().render(context)
        self.assertEqual(
            rendered_view, 
            '''<div class="small-12 columns">  %s</div>'''%expect_rendered_view
            )
        rendered_edit       = fieldrender.edit().render(context)
        self.assertEqual(
            rendered_edit, 
            '''<div class="small-12 columns">  %s</div>'''%expect_rendered_edit
            )
        rendered_label_view = fieldrender.label_view().render(context)
        self.assertEqual(
            rendered_label_view, 
            '''<div class="view-label small-12 columns">  '''+
            '''<p>test label</p>'''+
            '''</div>'''
            )
        rendered_label_edit = fieldrender.label_edit().render(context)
        self.assertEqual(
            rendered_label_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="view-label small-12 medium-2 columns">\n'''+
            '''      <p>test label</p>\n'''+
            '''    </div>\n'''+
            '''    <div class="small-12 medium-10 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        rendered_col_head   = fieldrender.col_head().render(context)
        self.assertEqual(
            rendered_col_head, 
            '''<div class="view-label small-12 columns">  '''+
            '''<p>test label</p></div>'''
            )
        rendered_col_view   = fieldrender.col_view().render(context)
        self.assertEqual(
            rendered_col_view, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <p>test label</p>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_view+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        rendered_col_edit   = fieldrender.col_edit().render(context)
        self.assertEqual(
            rendered_col_edit, 
            '''<div class="small-12 columns">\n'''+
            '''  <div class="row show-for-small-only">\n'''+
            '''    <div class="view-label small-12 columns">\n'''+
            '''      <p>test label</p>\n'''+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''  <div class="row">\n'''+
            '''    <div class="small-12 columns">\n'''+
            '''      %s\n'''%expect_rendered_edit+
            '''    </div>\n'''+
            '''  </div>\n'''+
            '''</div>'''
            )
        return

    def test_RenderFieldValue_renderers(self):

        class render_int_view(object):
            def render(self, context):
                return str(context['field']['field_value'])

        class render_int_edit(object):
            def render(self, context):
                return (
                    ('''<input type="text" size="64" '''+
                        '''name="%(repeat_prefix)s%(field_name)s" '''+
                        '''placeholder="%(field_placeholder)s" '''+
                        '''value="%(field_value)d"/>''')%
                    { 'field_value':        context['field']['field_value']
                    , 'field_name':         context['field']['field_name']
                    , 'field_placeholder':  context['field']['field_placeholder']
                    , 'repeat_prefix':      context['repeat_prefix']
                    })

        fieldrender = RenderFieldValue(
            view_renderer=render_int_view(), 
            edit_renderer=render_int_edit()
            )
        self._check_value_renderer_results(
            fieldrender,
            context=intvalue_context,
            expect_rendered_view="42",
            expect_rendered_edit=
                '''<input type="text" size="64" name="intprefix_test_field" '''+
                '''placeholder="(test placeholder)" value="42"/>'''           
            )
        return

    def test_RenderFieldValue_templates(self):
        view_template = get_template(
            "field/annalist_view_text.html",  
            "Can't load view template"
            )
        edit_template = get_template(
            "field/annalist_edit_text.html",
            "Can't load edit template"
            )
        fieldrender = RenderFieldValue(
            view_template=view_template, 
            edit_template=edit_template
            )
        self._check_value_renderer_results(
            fieldrender,
            context=intvalue_context,
            expect_rendered_view=
                '''<!-- field/annalist_view_text.html -->\n42''',
            expect_rendered_edit=
                '''<!-- field/annalist_edit_text.html -->\n'''+
                '''<!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->\n'''+
                '''<input type="text" size="64" name="intprefix_test_field" \n'''+
                '''       placeholder="(test placeholder)"\n'''+
                '''       value="42"/>'''
            )
        return

    def test_RenderFieldValue_files(self):
        fieldrender = RenderFieldValue(
            view_file="field/annalist_view_text.html", 
            edit_file="field/annalist_edit_text.html"
            )
        self._check_value_renderer_results(
            fieldrender,
            context=intvalue_context,
            expect_rendered_view=
                '''<!-- field/annalist_view_text.html -->\n42''',
            expect_rendered_edit=
                '''<!-- field/annalist_edit_text.html -->\n'''+
                '''<!-- cf http://stackoverflow.com/questions/1480588/input-size-vs-width -->\n'''+
                '''<input type="text" size="64" name="intprefix_test_field" \n'''+
                '''       placeholder="(test placeholder)"\n'''+
                '''       value="42"/>'''
            )
        return

    def test_RenderFieldPlacementValue(self):
        self._check_value_renderer_results(
            get_field_placement_renderer(),
            context=placement_context,
            expect_rendered_view=
                '''<span class="placement-text">'''+
                '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                ''' (4/4)</span>''',
            expect_rendered_edit=
                '''<select class="placement-text" name="repeat_prefix_test_field">\n'''+
                '''  <option value="">(test placeholder)</option>\n'''+
                '''  <option value="small:0,12">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (0/12)</option>\n'''+
                '''  <option value="small:0,12;medium:0,6">'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/6)</option>\n'''+
                '''  <option value="small:0,12;medium:6,6">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&block;&block;&block;'''+
                    ''' (6/6)</option>\n'''+
                '''  <option value="small:0,12;medium:0,4">'''+
                    '''&block;&block;&block;&block;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/4)</option>\n'''+
                '''  <option value="small:0,12;medium:4,4" selected="selected">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&block;&block;'''+
                    '''&block;&block;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (4/4)</option>\n'''+
                '''  <option value="small:0,12;medium:8,4">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&block;&block;&block;&block;'''+
                    ''' (8/4)</option>\n'''+
                '''  <option value="small:0,12;medium:0,3">'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (0/3)</option>\n'''+
                '''  <option value="small:0,12;medium:3,3">'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    ''' (3/3)</option>\n'''+
                '''  <option value="small:0,12;medium:6,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&block;&block;&block;&blk14;&blk14;&blk14;'''+
                    ''' (6/3)</option>\n'''+
                '''  <option value="small:0,12;medium:9,3">'''+
                    '''&blk14;&blk14;&blk14;&blk14;&blk14;&blk14;'''+
                    '''&blk14;&blk14;&blk14;&block;&block;&block;'''+
                    ''' (9/3)</option>\n'''+
                '''</select>'''
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
