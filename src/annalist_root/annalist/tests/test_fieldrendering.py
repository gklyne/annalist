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
from annalist.views.fields                      import render_tokenset
from annalist.views.fields.render_tokenset      import RenderTokenSet
from annalist.views.fields                      import render_repeatgroup
from annalist.views.fields.render_repeatgroup   import RenderRepeatGroup

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
      { 'field_placement':        get_placement_classes("small:0,12")
      , 'field_name':             "test_field"
      , 'field_label':            "test label"
      , 'field_placeholder':      "(test placeholder)"
      , 'field_value_encoded':    "aa bb cc"
      }
    , 'repeat':
      { 'repeat_prefix': "prefix_"
      }
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
                    , "annal:field_placement":  "small:0,12;medium:6,6right"
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
                , 'field_id':                   'View_repeat_fields'
                , 'field_name':                 'View_repeat_fields'
                , 'field_label':                'Fields'
                , 'field_help':                 'This resource descibes the repeated field description used when displaying and/or editing a record view description'
                , 'field_placeholder':          '(repeat field description)'
                , 'field_placement':            get_placement_classes("small:0,12")
                , 'field_property_uri':         'annal:view_fields'
                , 'field_value_type':           'annal:Field_group'
                , 'field_group_ref':            'View_field_view'
                , 'field_render_type':          'RepeatGroup'
                , 'group_id':                   'View_repeat_fields'
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

    def test_RenderTokenSetTest(self):
        self.assertEqual(
            RenderTokenSet.__name__, "RenderTokenSet", 
            "Check RenderTokenSet class name"
            )
        return

    def test_RenderTokenSetEncode(self):
        fieldrender = RenderTokenSet(render_tokenset.edit)
        self.assertEqual(fieldrender.encode(["aa"]), "aa")
        self.assertEqual(fieldrender.encode(["aa", "bb", "cc" ]), "aa bb cc")
        # Rendering non-list generates warning
        with SuppressLogging(logging.WARNING):
            self.assertEqual(fieldrender.encode("aa"), "aa")
        return

    def test_RenderTokenSetDecode(self):
        fieldrender = RenderTokenSet(render_tokenset.edit)
        self.assertEqual(fieldrender.decode("aa"), ["aa"])
        self.assertEqual(fieldrender.decode("aa bb cc"), ["aa", "bb", "cc"])
        return

    def test_RenderTokenSetEdit(self):
        fieldrender = RenderTokenSet(render_tokenset.edit)
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <p>test label</p> </div>'''
            , '''<div class="small-12 medium-10 columns">'''
            , '''<input type="text" size="64" name="prefix_test_field" '''+
              '''placeholder="(test placeholder)" value="aa bb cc"/>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_RenderTokenSetView(self):
        fieldrender = RenderTokenSet(render_tokenset.view)
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="small-12 columns">'''
            , '''<div class="row">'''
            , '''<div class="view-label small-12 medium-2 columns"> <p>test label</p> </div>'''
            , '''<div class="small-12 medium-10 columns"> <p>aa bb cc</p> </div>'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

    def test_RenderTokenSetItem(self):
        fieldrender = RenderTokenSet(render_tokenset.item)
        rendered_text = fieldrender.render(tokenset_context)
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="view-label small-12 columns">'''+
              ''' aa bb cc'''+
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
            [ '''<div class="small-12 columns"> <p class="grouplabel">Fields</p> </div>'''
            , '''<div class="row selectable">'''
            , '''<p>Field id</p>'''
            , '''<p>Property</p>'''
            , '''<p>Size/position</p>'''
            # 1st field
            , '''<input type="checkbox" name="View_repeat_fields__select_fields"'''+
              ''' value="0" class="right" />'''
            , '''<select name="View_repeat_fields__0__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option selected="selected">Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_repeat_fields__0__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            , '''<input type="text" size="64" name="View_repeat_fields__0__Field_placement"'''+
              ''' placeholder="(field display size and placement details)"'''+
              ''' value="small:0,12;medium:0,6"/>'''
            # 2nd field
            , '''<input type="checkbox" name="View_repeat_fields__select_fields"'''+
              ''' value="1" class="right" />'''
            , '''<select name="View_repeat_fields__1__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option selected="selected">Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_repeat_fields__1__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            , '''<input type="text" size="64" name="View_repeat_fields__1__Field_placement"'''+
              ''' placeholder="(field display size and placement details)"'''+
              ''' value="small:0,12;medium:6,6right"/>'''
             # 3rd field
            , '''<input type="checkbox" name="View_repeat_fields__select_fields"'''+
              ''' value="2" class="right" />'''
            , '''<select name="View_repeat_fields__2__Field_id">'''+
              ''' <option>Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option selected="selected">Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_repeat_fields__2__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value="rdfs:label"/>'''
            , '''<input type="text" size="64" name="View_repeat_fields__2__Field_placement"'''+
              ''' placeholder="(field display size and placement details)"'''+
              ''' value="small:0,12"/>'''
            # 4th field
            , '''<input type="checkbox" name="View_repeat_fields__select_fields"'''+
              ''' value="3" class="right" />'''
            , ''' <select name="View_repeat_fields__3__Field_id">'''+
              ''' <option selected="selected">Entity_comment</option>'''+
              ''' <option>Entity_id</option>'''+
              ''' <option>Entity_label</option>'''+
              ''' <option>Entity_type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_repeat_fields__3__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value="rdfs:comment"/>'''
            , '''<input type="text" size="64" name="View_repeat_fields__3__Field_placement"'''+
              ''' placeholder="(field display size and placement details)"'''+
              ''' value="small:0,12"/>'''
            # Buttons
            , '''<input type="submit" name="View_repeat_fields__remove" value="Remove selected field(s)" />'''
            , '''<input type="submit" name="View_repeat_fields__add" value="Add field" />'''
            ])
        for e in expect_elements:
            self.assertIn(e, rendered_text)
        return

# End.

if __name__ == "__main__":
    import django
    django.setup()  # Needed for template loader
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()
