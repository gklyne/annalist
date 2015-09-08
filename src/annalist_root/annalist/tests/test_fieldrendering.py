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
from django.template                    import Context, Template, loader

from utils.SuppressLoggingContext       import SuppressLogging

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist.models.site               import Site
from annalist.models.collection         import Collection

from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field

from annalist.views.fields.render_placement     import get_placement_classes
from annalist.views.fields                      import render_repeatgroup
from annalist.views.fields.render_repeatgroup   import RenderRepeatGroup
from annalist.views.fields.render_text          import RenderText
from annalist.views.fields.render_fieldvalue    import RenderFieldValue, get_template

from tests                      import init_annalist_test_site, resetSitedata
from tests                      import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from field_rendering_support    import FieldRendererTestSupport

#   -----------------------------------------------------------------------------
#
#   FieldRendering tests
#
#   -----------------------------------------------------------------------------

class FieldRenderingTest(FieldRendererTestSupport):
    """
    Tests for Site object interface
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection(self.testsite, "testcoll")
        # self.tokenset_context  = self._make_test_context(
        #     ["aa", "bb", "cc"], repeat_prefix="tokprefix_"
        #     )
        self.intvalue_context  = self._make_test_context(42, repeat_prefix="intprefix_")
        return

    def tearDown(self):
        # resetSitedata(scope="collections")
        return

    @classmethod
    def tearDownClass(cls):
        resetSitedata()
        return

    def _get_repeatgroup_context(self):
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
                , 'field_target_type':          'annal:Field_group'
                , 'field_label':                'Fields'
                , 'field_help':                 'This resource descibes the repeated field description used when displaying and/or editing a record view description'
                , 'field_render_type':          'RepeatGroup'
                , 'field_value_mode':           'Value_direct'
                , 'field_property_uri':         'annal:view_fields'
                , 'field_placement':            get_placement_classes("small:0,12")
                , 'field_placeholder':          '(repeat field description)'
                , 'field_group_ref':            'View_field_view'
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
        rendered_text = fieldrender.render(self._get_repeatgroup_context())
        # print "\n**************\n"
        # print rendered_text
        # print "\n**************\n"
        # replace runs of whitespace/newlines with single space:
        rendered_text = re.sub(r'\s+', " ", rendered_text)
        expect_elements = (
            [ '''<div class="group-label small-2 columns"> <span>Fields</span> </div>'''
            , '''<div class="row selectable">'''
            , '''<div class="view-label small-12 medium-4 columns"> <span>Field id</span> </div>'''
            , '''<div class="view-label small-12 medium-4 columns"> <span>Property</span> </div>'''
            , '''<div class="view-label small-12 medium-4 columns"> <span>Position/size</span> </div>'''
            # 1st field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="0" class="right" />'''
            , '''<select name="View_fields__0__Field_id">'''+
              ''' <option value="">(field sel)</option>'''+
              ''' <option value="_field/Entity_comment">Comment</option>'''+
              ''' <option value="_field/Entity_id" selected="selected">Id</option>'''+
              ''' <option value="_field/Entity_label">Label</option>'''+
              ''' <option value="_field/Entity_type">Type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__0__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            # 2nd field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="1" class="right" />'''
            , '''<select name="View_fields__1__Field_id">'''+
              ''' <option value="">(field sel)</option>'''+
              ''' <option value="_field/Entity_comment">Comment</option>'''+
              ''' <option value="_field/Entity_id">Id</option>'''+
              ''' <option value="_field/Entity_label">Label</option>'''+
              ''' <option value="_field/Entity_type" selected="selected">Type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__1__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value=""/>'''
            # 3rd field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="2" class="right" />'''
            , '''<select name="View_fields__2__Field_id">'''+
              ''' <option value="">(field sel)</option>'''+
              ''' <option value="_field/Entity_comment">Comment</option>'''+
              ''' <option value="_field/Entity_id">Id</option>'''+
              ''' <option value="_field/Entity_label" selected="selected">Label</option>'''+
              ''' <option value="_field/Entity_type">Type</option>'''+
              ''' </select>'''
            , '''<input type="text" size="64" name="View_fields__2__Field_property"'''+
              ''' placeholder="(field URI or CURIE)"'''+
              ''' value="rdfs:label"/>'''
            # 4th field
            , '''<input type="checkbox" name="View_fields__select_fields"'''+
              ''' value="3" class="right" />'''
            , ''' <select name="View_fields__3__Field_id">'''+
              ''' <option value="">(field sel)</option>'''+
              ''' <option value="_field/Entity_comment" selected="selected">Comment</option>'''+
              ''' <option value="_field/Entity_id">Id</option>'''+
              ''' <option value="_field/Entity_label">Label</option>'''+
              ''' <option value="_field/Entity_type">Type</option>'''+
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
            context=self.intvalue_context,
            expect_rendered_view="42",
            expect_rendered_edit=
                '''<input type="text" size="64" name="intprefix_test_field" '''+
                '''placeholder="(test placeholder)" value="42"/>'''           
            )
        return

    # Rendering using compiled template supplied
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
            context=self.intvalue_context,
            expect_rendered_view=
                '''<span>42</span>''',
            expect_rendered_edit=
                '''<input type="text" size="64" name="intprefix_test_field" \n'''+
                '''       placeholder="(test placeholder)"\n'''+
                '''       value="42" />'''
            )
        return

    # Rendering using template file name supplied
    def test_RenderFieldValue_files(self):
        fieldrender = RenderFieldValue(
            view_file="field/annalist_view_text.html", 
            edit_file="field/annalist_edit_text.html"
            )
        self._check_value_renderer_results(
            fieldrender,
            context=self.intvalue_context,
            expect_rendered_view=
                '''<span>42</span>''',
            expect_rendered_edit=
                '''<input type="text" size="64" name="intprefix_test_field" \n'''+
                '''       placeholder="(test placeholder)"\n'''+
                '''       value="42" />'''
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
