"""
Tests for FieldDescription module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.test                        import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions

from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist.models.site               import Site
from annalist.models.collection         import Collection

from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field

from annalist.views.fields.render_placement     import Placement
from annalist.views.fields.render_repeatgroup   import RenderRepeatGroup

from tests                  import init_annalist_test_site
from tests                  import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from AnnalistTestCase       import AnnalistTestCase

from entity_testentitydata  import entity_url

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

    def test_FieldDescriptionTest(self):
        self.assertEqual(
            FieldDescription.__name__, "FieldDescription", 
            "Check FieldDescription class name"
            )
        return

    def test_Field_InitialValues(self):
        fd = field_description_from_view_field(
            self.testcoll, 
            { ANNAL.CURIE.field_id: "_initial_values" }, 
            {}
            )
        expect_placement = Placement(
            field = 'small-12 columns', 
            label = 'small-12 medium-2 columns', 
            value = 'small-12 medium-10 columns'
            )
        expect_field_desc = (
            { 'field_id':                   '_initial_values'
            , 'field_name':                 '_initial_values'
            , 'field_value_type':           ANNAL.CURIE.Text
            , 'field_label':                ''
            , 'field_help':                 ''
            , 'field_property_uri':         ''
            , 'field_placeholder':          ''
            , 'field_default_value':        None
            , 'field_placement':            expect_placement
            , 'field_options_typeref':      None
            , 'field_choice_links':         None
            , 'field_restrict_values':      'ALL'
            , 'field_group_ref':            None
            , 'field_render_type':          'Text'
            })
        # print repr(fd)
        self.assertDictionaryMatch(fd, expect_field_desc)
        return

    def test_Field_id(self):
        fd = field_description_from_view_field(
            self.testcoll, 
            { ANNAL.CURIE.field_id: "Field_id" }, 
            {}
            )
        expect_placement = Placement(
            field = 'small-6 columns', 
            label = 'small-12 medium-4 columns', 
            value = 'small-12 medium-8 columns'
            )
        expect_field_desc = (
            { 'field_id':                   'Field_id'
            , 'field_name':                 'entity_id'
            , 'field_value_type':           ANNAL.CURIE.Slug
            , 'field_label':                'Id'
            , 'field_property_uri':         ANNAL.CURIE.id
            , 'field_placeholder':          '(field id)'
            , 'field_default_value':        None
            , 'field_placement':            expect_placement
            , 'field_options_typeref':      None
            , 'field_choice_links':         None
            , 'field_restrict_values':      'ALL'
            , 'field_group_ref':            None
            , 'field_render_type':          'EntityId'
            })
        # print repr(fd)
        self.assertDictionaryMatch(fd, expect_field_desc)
        return

    def test_Group_field_sel(self):
        fd = field_description_from_view_field(
            self.testcoll, 
            { ANNAL.CURIE.field_id: "Group_field_sel" }, 
            {}
            )
        expect_placement = Placement(
            field='small-6 columns', 
            label='small-12 medium-4 columns', 
            value='small-12 medium-8 columns'
            )
        expect_choice_ids = (
            [ 'Entity_comment'
            , 'Entity_id'
            , 'Entity_label'
            , 'Entity_type'
            ])
        expect_choice_labels = OrderedDict(
            [ (id, id) for id in expect_choice_ids]
            )
        expect_choice_links = OrderedDict(
            [ (id, entity_url("testcoll", "_field", id)) 
              for id in expect_choice_ids
            ])
        expect_field_desc = (
            { 'field_id':                   'Group_field_sel'
            , 'field_name':                 'Field_id'
            , 'field_value_type':           ANNAL.CURIE.Slug
            , 'field_label':                'Field id'
            , 'field_property_uri':         ANNAL.CURIE.field_id
            , 'field_placeholder':          '(field sel)'
            , 'field_default_value':        ''
            , 'field_placement':            expect_placement
            , 'field_options_typeref':      '_field'
            , 'field_choice_labels':        expect_choice_labels
            , 'field_choice_links':         expect_choice_links
            , 'field_restrict_values':      '[annal:field_entity_type] in entity[annal:record_type]'
            , 'field_group_ref':            None
            , 'field_render_type':          'Field'
            })
        # print repr(fd)
        self.assertDictionaryMatch(fd, expect_field_desc)
        return

    def test_View_fields(self):
        fd = field_description_from_view_field(
            self.testcoll, 
            { ANNAL.CURIE.field_id: "View_fields" }, 
            {}
            )
        expect_placement = Placement(
            field = 'small-12 columns', 
            label = 'small-12 medium-2 columns', 
            value = 'small-12 medium-10 columns'
            )
        expect_field_desc = (
            { 'field_id':                   'View_fields'
            , 'field_name':                 'View_fields'
            , 'field_value_type':           ANNAL.CURIE.Field_group
            , 'field_label':                'Fields'
            , 'field_property_uri':         ANNAL.CURIE.view_fields
            , 'field_placeholder':          '(repeat field description)'
            , 'field_default_value':        None
            , 'field_placement':            expect_placement
            , 'field_options_typeref':      None
            , 'field_choice_labels':        None
            , 'field_choice_links':         None
            , 'field_restrict_values':      'ALL'
            , 'field_group_ref':            'View_field_group'
            })
        self.assertDictionaryMatch(fd, expect_field_desc)
        self.assertEqual(fd['field_render_type'], "RepeatGroupRow")
        self.assertEqual(fd['field_render_colhead'], "field/annalist_head_any.html")
        self.assertEqual(fd['field_render_colview'], "field/annalist_item_none.html")
        self.assertIsInstance(fd['field_render_view'], RenderRepeatGroup)
        self.assertIsInstance(fd['field_render_edit'], RenderRepeatGroup)
        expect_group_details = (
            { 'group_id':           "View_fields"
            , 'group_label':        "Fields"
            , 'group_add_label':    "Add field"
            , 'group_delete_label': "Remove selected field(s)"
            })
        self.assertDictionaryMatch(fd, expect_group_details)
        self.assertEqual(len(fd['group_field_descs']), 3)
        # Field type selector
        expect_field0_placement = Placement(
            field='small-12 medium-4 columns', 
            label='small-12 medium-6 columns', 
            value='small-12 medium-6 columns'
            )
        expect_field0_desc = (
            { 'field_id':                   'Group_field_sel'
            , 'field_name':                 'Field_id'
            , 'field_value_type':           ANNAL.CURIE.Slug
            , 'field_label':                'Field id'
            , 'field_render_type':          'Field'
            , 'field_property_uri':         ANNAL.CURIE.field_id
            , 'field_placement':            expect_field0_placement
            })
        self.assertDictionaryMatch(fd['group_field_descs'][0], expect_field0_desc)
        # Field property URI
        expect_field1_placement = Placement(
            field='small-12 medium-4 columns', 
            label='small-12 medium-6 columns', 
            value='small-12 medium-6 columns'
            )
        expect_field1_desc = (
            { 'field_id':                   'Group_field_property'
            , 'field_name':                 'Field_property'
            , 'field_value_type':           ANNAL.CURIE.Identifier
            , 'field_label':                'Property'
            , 'field_render_type':          'Identifier'
            , 'field_property_uri':         ANNAL.CURIE.property_uri
            , 'field_placement':            expect_field1_placement
            })
        self.assertDictionaryMatch(fd['group_field_descs'][1], expect_field1_desc)
        # Field placement (within group)
        expect_field2_placement = Placement(
            field='small-12 medium-4 columns', 
            label='small-12 medium-6 columns', 
            value='small-12 medium-6 columns'
            )
        expect_field2_desc = (
            { 'field_id':                   'Group_field_placement'
            , 'field_name':                 'Field_placement'
            , 'field_value_type':           ANNAL.CURIE.Placement
            , 'field_label':                'Position/size'
            , 'field_render_type':          'Placement'
            , 'field_property_uri':         ANNAL.CURIE.field_placement
            , 'field_placement':            expect_field2_placement
            })
        self.assertDictionaryMatch(fd['group_field_descs'][2], expect_field2_desc)
        return

# End.

if __name__ == "__main__":
    # Runtests in this module
    # runner = unittest.TextTestRunner(verbosity=2)
    # tests = unittest.TestSuite()
    # tests  = getSuite(select=sel)
    # if tests: runner.run(tests)
    unittest.main()
