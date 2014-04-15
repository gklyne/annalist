"""
Tests for EntityData metadata editing view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import unittest

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.db                      import models
from django.http                    import QueryDict
from django.contrib.auth.models     import User
from django.test                    import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions
from django.test.client             import Client

from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist                       import layout
from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

from annalist.views.entityedit      import GenericEntityEditView

from tests                          import TestHost, TestHostUri, TestBasePath, TestBaseUri, TestBaseDir
from tests                          import init_annalist_test_site
from AnnalistTestCase               import AnnalistTestCase
from entity_testutils               import (
    recordtype_create_values, collection_create_values,
    site_dir, collection_dir, recordtype_dir, recorddata_dir,  entitydata_dir,
    collection_edit_uri,
    recordtype_edit_uri,
    entity_uri, entitydata_edit_uri, 
    entitydata_list_type_uri,
    recordtype_form_data,
    entitydata_value_keys, entitydata_create_values, entitydata_values,
    entitydata_recordtype_view_context_data, 
    # entitydata_context_data, 
    entitydata_recordtype_view_form_data,
    # entitydata_form_data, 
    entitydata_delete_confirm_form_data,
    site_title
    )

#   -----------------------------------------------------------------------------
#
#   GenericEntityEditView tests
#
#   -----------------------------------------------------------------------------

class FieldEditViewTest(AnnalistTestCase):
    """
    Tests for record type edit views
    """

    def setUp(self):
        init_annalist_test_site()
        self.testsite = Site(TestBaseUri, TestBaseDir)
        self.testcoll = Collection.create(self.testsite, "testcoll", collection_create_values("testcoll"))
        # self.viewtype = RecordType.load(self.testcoll, "_view", altparent=self.testsite)
        self.user     = User.objects.create_user('testuser', 'user@test.example.com', 'testpassword')
        self.user.save()
        self.client   = Client(HTTP_HOST=TestHost)
        loggedin      = self.client.login(username="testuser", password="testpassword")
        self.assertTrue(loggedin)
        # self.type_ids   = ['testtype', 'Default_type']
        self.no_options = ['(no options)']
        return

    def tearDown(self):
        return

    #   -----------------------------------------------------------------------------
    #   Helpers
    #   -----------------------------------------------------------------------------

    def _create_view_data(self, view_id, update="RecordView"):
        "Helper function creates view data with supplied view_id"
        e = RecordView.create(self.collection, view_id, 
            recordview_create_values(view_id=view_id, update=update)
            )
        return e    

    def _check_view_data_values(self, view_id, update="RecordView", parent=None):
        "Helper function checks content of form-updated record type entry with supplied view_id"
        self.assertTrue(RecordView.exists(self.testcoll, view_id, altparent=self.testsite))
        e = RecordView.load(self.testcoll, view_id, altparent=self.testsite)
        self.assertEqual(e.get_id(), view_id)
        self.assertEqual(e.get_uri(), TestHostUri + recordview_uri("testcoll", view_id))
        v = recordview_values(view_id, update=update)
        self.assertDictionaryMatch(e.get_values(), v)
        return e

    def _check_context_fields(self, response, 
            field_id="(?field_id)", 
            field_type="(?field_type)",
            field_label="(?field_label)",
            field_comment="(?field_comment)",
            field_placeholder="(?field_placeholder)",
            field_property="(?field_property)",
            field_placement="(?field_placement)"
            ):
        r = response
        self.assertEqual(len(r.context['fields']), 7)        
        # 1st field - Id
        field_id_help = (
            "A short identifier that distinguishes this field from all other fields in the same collection.  "+
            "A given field may occur in a number of different record types and/or views, "+
            "so is scoped to the containing collection."
            )
        self.assertEqual(r.context['fields'][0]['field_id'], 'Field_id')
        self.assertEqual(r.context['fields'][0]['field_name'], 'Field_id')
        self.assertEqual(r.context['fields'][0]['field_label'], 'Id')
        self.assertEqual(r.context['fields'][0]['field_help'], field_id_help)
        self.assertEqual(r.context['fields'][0]['field_placeholder'], "(field id)")
        self.assertEqual(r.context['fields'][0]['field_property_uri'], "annal:id")
        self.assertEqual(r.context['fields'][0]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][0]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][0]['field_placement'].field, "small-12 medium-6 columns")
        self.assertEqual(r.context['fields'][0]['field_value_type'], "annal:Slug")
        self.assertEqual(r.context['fields'][0]['field_value'], field_id)
        self.assertEqual(r.context['fields'][0]['options'], self.no_options)
        # 2nd field - Label
        field_type_help = (
            "Type of display field.  "+
            "This encompasses the actual form of the rendered value and "+
            "the type of underlying record data that is formatted, and "+
            "any defaults of other values that may be applied to the field."
            )
        self.assertEqual(r.context['fields'][1]['field_id'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_name'], 'Field_type')
        self.assertEqual(r.context['fields'][1]['field_label'], 'Field value type')
        self.assertEqual(r.context['fields'][1]['field_help'], field_type_help)
        self.assertEqual(r.context['fields'][1]['field_placeholder'], "(field value type)")
        self.assertEqual(r.context['fields'][1]['field_property_uri'], "annal:field_render")
        self.assertEqual(r.context['fields'][1]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][1]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][1]['field_placement'].field, "small-12 medium-6 right columns")
        self.assertEqual(r.context['fields'][1]['field_value_type'], "annal:RenderType")
        self.assertEqual(r.context['fields'][1]['field_value'], field_type)
        self.assertEqual(r.context['fields'][1]['options'], self.no_options)
        # 3rd field - Label
        field_label_help = (
            "Short string used to label value in form display, or as heading of list column"
            )
        self.assertEqual(r.context['fields'][2]['field_id'], 'Field_label')
        self.assertEqual(r.context['fields'][2]['field_name'], 'Field_label')
        self.assertEqual(r.context['fields'][2]['field_label'], 'Label')
        self.assertEqual(r.context['fields'][2]['field_help'], field_label_help)
        self.assertEqual(r.context['fields'][2]['field_placeholder'], "(field label)")
        self.assertEqual(r.context['fields'][2]['field_property_uri'], "rdfs:label")
        self.assertEqual(r.context['fields'][2]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][2]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][2]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][2]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][2]['field_value'], field_label)
        self.assertEqual(r.context['fields'][2]['options'], self.no_options)
        # 4th field - comment
        field_comment_help = (
            "Descriptive text explaining how field is intended to be used.  "+
            "This text may be used to provide content for a tooltip "+
            "associated with the field display in a form."
            )
        field_comment_placeholder = (
            "(field usage commentary or help text)"
            )
        self.assertEqual(r.context['fields'][3]['field_id'], 'Field_comment')
        self.assertEqual(r.context['fields'][3]['field_name'], 'Field_comment')
        self.assertEqual(r.context['fields'][3]['field_label'], 'Help')
        self.assertEqual(r.context['fields'][3]['field_help'], field_comment_help)
        self.assertEqual(r.context['fields'][3]['field_placeholder'], field_comment_placeholder)
        self.assertEqual(r.context['fields'][3]['field_property_uri'], "rdfs:comment")
        self.assertEqual(r.context['fields'][3]['field_render_view'],   "field/annalist_view_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_render_edit'],   "field/annalist_edit_textarea.html")
        self.assertEqual(r.context['fields'][3]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][3]['field_value_type'], "annal:Longtext")
        self.assertEqual(r.context['fields'][3]['field_value'], field_comment)
        self.assertEqual(r.context['fields'][3]['options'], self.no_options)
        # 5th field - URI
        field_placeholder_help = (
            "Placeholder string displayed in field until actual value is selected"
            )
        self.assertEqual(r.context['fields'][4]['field_id'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][4]['field_name'], 'Field_placeholder')
        self.assertEqual(r.context['fields'][4]['field_label'], 'Placeholder')
        self.assertEqual(r.context['fields'][4]['field_help'], field_placeholder_help)
        self.assertEqual(r.context['fields'][4]['field_placeholder'], "(placeholder text)")
        self.assertEqual(r.context['fields'][4]['field_property_uri'], "annal:placeholder")
        self.assertEqual(r.context['fields'][4]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][4]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][4]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][4]['field_value_type'], "annal:Text")
        self.assertEqual(r.context['fields'][4]['field_value'], field_placeholder)
        self.assertEqual(r.context['fields'][4]['options'], self.no_options)
        # 6th field - Field_property
        field_property_help = (
            "Property URI (or CURIE) used to represent this field data in a record"
            )
        self.assertEqual(r.context['fields'][5]['field_id'], 'Field_property')
        self.assertEqual(r.context['fields'][5]['field_name'], 'Field_property')
        self.assertEqual(r.context['fields'][5]['field_label'], 'Property')
        self.assertEqual(r.context['fields'][5]['field_help'], field_property_help)
        self.assertEqual(r.context['fields'][5]['field_placeholder'], "(property URI or CURIE)")
        self.assertEqual(r.context['fields'][5]['field_property_uri'], "annal:property_uri")
        self.assertEqual(r.context['fields'][5]['field_render_view'], "field/annalist_view_entityref.html")
        self.assertEqual(r.context['fields'][5]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][5]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][5]['field_value_type'], "annal:Identifier")
        self.assertEqual(r.context['fields'][5]['field_value'], field_property)
        self.assertEqual(r.context['fields'][5]['options'], self.no_options)
        # 7th field - ??
        field_placement_help = (
            "Size of displayed field, and hints for its position in a record display"
            )
        field_placement_placeholder = (
            "(field display size and placement details)"
            )
        self.assertEqual(r.context['fields'][6]['field_id'], 'Field_placement')
        self.assertEqual(r.context['fields'][6]['field_name'], 'Field_placement')
        self.assertEqual(r.context['fields'][6]['field_label'], 'Size and position')
        self.assertEqual(r.context['fields'][6]['field_help'], field_placement_help)
        self.assertEqual(r.context['fields'][6]['field_placeholder'], field_placement_placeholder)
        self.assertEqual(r.context['fields'][6]['field_property_uri'], "annal:field_placement")
        self.assertEqual(r.context['fields'][6]['field_render_view'], "field/annalist_view_text.html")
        self.assertEqual(r.context['fields'][6]['field_render_edit'], "field/annalist_edit_text.html")
        self.assertEqual(r.context['fields'][6]['field_placement'].field, "small-12 columns")
        self.assertEqual(r.context['fields'][6]['field_value_type'], "annal:Placement")
        self.assertEqual(r.context['fields'][6]['field_value'], field_placement)
        self.assertEqual(r.context['fields'][6]['options'], self.no_options)

    #   -----------------------------------------------------------------------------
    #   Form rendering tests
    #   -----------------------------------------------------------------------------

    def test_GenericEntityEditView(self):
        self.assertEqual(GenericEntityEditView.__name__, "GenericEntityEditView", "Check GenericEntityEditView class name")
        return

    def test_get_form_rendering(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # log.info(r.content)
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        formrow1col1 = """
            <div class="small-12 medium-6 columns">
                <div class="row">
                    <div class="view_label small-12 medium-4 columns">
                        <p>Id</p>
                    </div>
                    <div class="small-12 medium-8 columns">
                        <input type="text" size="64" name="Field_id" value="00000001"/>
                    </div>
                </div>
            </div>
            """
        formrow1col2 = """
            <div class="small-12 medium-6 right columns">
                <div class="row">
                    <div class="view_label small-12 medium-4 columns">
                        <p>Field value type</p>
                    </div>
                    <div class="small-12 medium-8 columns">
                        <input type="text" size="64" name="Field_type" value="(field value type)"/>
                    </div>
                </div>
            </div>
            """
        formrow2 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Label</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_label" value="Entity &#39;00000001&#39; of type &#39;_field&#39; in collection &#39;testcoll&#39;"/>
                    </div>
                </div>
            </div>
            """
        formrow3 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Help</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                                <textarea cols="64" rows="6" name="Field_comment" class="small-rows-4 medium-rows-8"></textarea>
                    </div>
                </div>
            </div>
            """
        formrow4 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Placeholder</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_placeholder" value="(placeholder text)"/>
                    </div>
                </div>
            </div>
            """
        formrow5 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Property</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_property" value="(property URI or CURIE)"/>
                    </div>
                </div>
            </div>
            """
        formrow6 = """
            <div class="small-12 columns">
                <div class="row">
                    <div class="view_label small-12 medium-2 columns">
                        <p>Size and position</p>
                    </div>
                    <div class="small-12 medium-10 columns">
                        <input type="text" size="64" name="Field_placement" 
                               value="(field display size and placement details)"/>
                    </div>
                </div>
            </div>
            """
        self.assertContains(r, formrow1col1, html=True)
        self.assertContains(r, formrow1col2, html=True)
        self.assertContains(r, formrow2, html=True)
        self.assertContains(r, formrow3, html=True)
        self.assertContains(r, formrow4, html=True)
        self.assertContains(r, formrow5, html=True)
        self.assertContains(r, formrow6, html=True)
        return

    def test_get_new(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_uri = entity_uri(type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + field_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="00000001",
            field_type="(field value type)",
            field_label="Entity '00000001' of type '_field' in collection 'testcoll'",
            field_comment="",
            field_placeholder="(placeholder text)",
            field_property="(property URI or CURIE)",
            field_placement="(field display size and placement details)"
            )
        return

    def test_get_new_no_continuation(self):
        u = entitydata_edit_uri("new", "testcoll", "_field", view_id="Field_view")
        r = self.client.get(u)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        # Test context
        field_uri = entity_uri(type_id="_field", entity_id="00000001")
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "00000001")
        self.assertEqual(r.context['orig_id'],          "00000001")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + field_uri)
        self.assertEqual(r.context['action'],           "new")
        self.assertEqual(r.context['continuation_uri'], "")
        return

    def test_get_edit(self):
        u = entitydata_edit_uri("edit", "testcoll", "_field", entity_id="Type_label", view_id="Field_view")
        # log.info("test_get_edit uri %s"%u)
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        # log.info("test_get_edit resp %s"%r.content)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>'_field' data in collection 'testcoll'</h3>")
        # Test context
        self.assertEqual(r.context['title'],            site_title())
        self.assertEqual(r.context['coll_id'],          "testcoll")
        self.assertEqual(r.context['type_id'],          "_field")
        self.assertEqual(r.context['entity_id'],        "Type_label")
        self.assertEqual(r.context['orig_id'],          "Type_label")
        self.assertEqual(r.context['entity_uri'],       TestHostUri + entity_uri("testcoll", "_field", "Type_label"))
        self.assertEqual(r.context['action'],           "edit")
        self.assertEqual(r.context['continuation_uri'], "/xyzzy/")
        # Fields
        self._check_context_fields(r, 
            field_id="Type_label",
            field_type="annal:field_render/Text",    # @@TODO review usage here
            field_label="Label",
            field_comment="Short string used to describe record type when displayed",
            field_placeholder="(label)",
            field_property="rdfs:label",
            field_placement="(field display size and placement details)"
            )
        return

    def test_get_edit_not_exists(self):
        u = entitydata_edit_uri("edit", "testcoll", "_field", entity_id="typenone", view_id="Field_view")
        r = self.client.get(u+"?continuation_uri=/xyzzy/")
        self.assertEqual(r.status_code,   404)
        self.assertEqual(r.reason_phrase, "Not found")
        self.assertContains(r, "<title>Annalist error</title>", status_code=404)
        self.assertContains(r, "<h3>404: Not found</h3>", status_code=404)
        # log.info(r.content)
        self.assertContains(r, 
            "<p>Entity &#39;typenone&#39; of type &#39;_field&#39; "+
            "in collection &#39;testcoll&#39; does not exist</p>", 
            status_code=404
            )
        return

    #   -----------------------------------------------------------------------------
    #   Form response tests
    #   -----------------------------------------------------------------------------

    #   -------- new entity --------

    @unittest.skip("@@TODO")
    def test_post_new_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check new entity data created
        self._check_view_data_values("newentity")
        return

    @unittest.skip("@@TODO")
    def test_post_new_entity_no_continuation(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new")
        f['continuation_uri'] = ""
        u = entitydata_edit_uri("new", "testcoll", "testtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        # print r.content
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check new entity data created
        self._check_view_data_values("newentity")
        return

    @unittest.skip("@@TODO")
    def test_post_new_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", action="new", cancel="Cancel")
        u = entitydata_edit_uri("new", "testcoll", "testtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        return

    @unittest.skip("@@TODO")
    def test_post_new_entity_missing_id(self):
        f = entitydata_recordtype_view_form_data(action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordtype_view_context_data(action="new")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    @unittest.skip("@@TODO")
    def test_post_new_entity_invalid_id(self):
        f = entitydata_recordtype_view_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="new")
        u = entitydata_edit_uri("new", "testcoll", "testtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="new"
            )
        # log.info(repr(r.context['fields'][1]))
        self.assertDictionaryMatch(r.context, expect_context)
        return

    @unittest.skip("@@TODO")
    def test_new_entity_default_type(self):
        # Checks logic related to creating a new recorddata entity in collection 
        # for type defined in site data
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", type_id="Default_type", action="new")
        u = entitydata_edit_uri("new", "testcoll", "Default_type", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "Default_type"))
        # Check new entity data created
        self._check_view_data_values("newentity", type_id="Default_type")
        return

    @unittest.skip("@@TODO")
    def test_new_entity_new_type(self):
        # Checks logic for creating an entity which may require creation of new recorddata
        # Create new type
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        f = recordtype_form_data(type_id="newtype", action="new")
        u = recordtype_edit_uri("new", "testcoll")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + collection_edit_uri())
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        # Create new entity
        self.assertFalse(EntityData.exists(self.testdata, "newentity"))
        f = entitydata_recordtype_view_form_data(entity_id="newentity", type_id="newtype", action="new")
        u = entitydata_edit_uri("new", "testcoll", "newtype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "newtype"))
        # Check new entity data created
        self._check_view_data_values("newentity", type_id="newtype")
        return

    #   -------- copy type --------

    @unittest.skip("@@TODO")
    def test_post_copy_entity(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_recordtype_view_form_data(entity_id="copytype", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type exists
        self._check_view_data_values("copytype")
        return

    @unittest.skip("@@TODO")
    def test_post_copy_entity_cancel(self):
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        f = entitydata_recordtype_view_form_data(entity_id="copytype", action="copy", cancel="Cancel")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that target record type still does not exist
        self.assertFalse(EntityData.exists(self.testdata, "copytype"))
        return

    @unittest.skip("@@TODO")
    def test_post_copy_entity_missing_id(self):
        f = entitydata_recordtype_view_form_data(action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordtype_view_context_data(action="copy")
        self.assertDictionaryMatch(r.context, expect_context)
        return

    @unittest.skip("@@TODO")
    def test_post_copy_entity_invalid_id(self):
        f = entitydata_recordtype_view_form_data(entity_id="!badentity", orig_id="orig_entity_id", action="copy")
        u = entitydata_edit_uri("copy", "testcoll", "testtype", entity_id="entity1", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="copy"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        return

    @unittest.skip("@@TODO")
    #   -------- edit type --------

    def test_post_edit_entity(self):
        self._create_view_data("entityedit")
        self._check_view_data_values("entityedit")
        f = entitydata_recordtype_view_form_data(entity_id="entityedit", action="edit", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityedit", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        self._check_view_data_values("entityedit", update="Updated entity")
        return

    @unittest.skip("@@TODO")
    def test_post_edit_entity_new_id(self):
        self._create_view_data("entityeditid1")
        self._check_view_data_values("entityeditid1")
        # Now post edit form submission with different values and new id
        f = entitydata_recordtype_view_form_data(
            entity_id="entityeditid2", orig_id="entityeditid1", action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityeditid1", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that new record type exists and old does not
        self.assertFalse(EntityData.exists(self.testdata, "entityeditid1"))
        self._check_view_data_values("entityeditid2")
        return

    @unittest.skip("@@TODO")
    def test_post_edit_entity_new_type(self):
        # NOTE that the RecordType_viewform does not include a type field, but the new-type
        # logic is checked by the test_entitydefaultedit suite
        self._create_view_data("entityedittype")
        self._check_view_data_values("entityedittype")
        self.assertFalse(RecordType.exists(self.testcoll, "newtype"))
        newtype = RecordType.create(self.testcoll, "newtype", recordtype_create_values("newtype"))
        newtypedata = RecordTypeData(self.testcoll, "newtype")
        self.assertTrue(RecordType.exists(self.testcoll, "newtype"))
        self.assertFalse(RecordTypeData.exists(self.testcoll, "newtype"))
        # Now post edit form submission with new type id
        f = entitydata_recordtype_view_form_data(
            entity_id="entityedittype", orig_id="entityedittype", 
            type_id="newtype", orig_type="testtype",
            action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="entityedittype", view_id="RecordType_view")
        r = self.client.post(u, f)
        # log.info("***********\n"+r.content)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        return

    @unittest.skip("@@TODO")
    def test_post_edit_entity_cancel(self):
        self._create_view_data("edittype")
        self._check_view_data_values("edittype")
        # Post from cancelled edit form
        f = entitydata_recordtype_view_form_data(entity_id="edittype", action="edit", cancel="Cancel", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   302)
        self.assertEqual(r.reason_phrase, "FOUND")
        self.assertEqual(r.content,       "")
        self.assertEqual(r['location'], TestHostUri + entitydata_list_type_uri("testcoll", "testtype"))
        # Check that target record type still does not exist and unchanged
        self._check_view_data_values("edittype")
        return

    @unittest.skip("@@TODO")
    def test_post_edit_entity_missing_id(self):
        self._create_view_data("edittype")
        self._check_view_data_values("edittype")
        # Form post with ID missing
        f = entitydata_recordtype_view_form_data(action="edit", update="Updated entity")
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordtype_view_context_data(action="edit", update="Updated entity")
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("edittype")
        return

    @unittest.skip("@@TODO")
    def test_post_edit_entity_invalid_id(self):
        self._create_view_data("edittype")
        self._check_view_data_values("edittype")
        # Form post with ID malformed
        f = entitydata_recordtype_view_form_data(

            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        u = entitydata_edit_uri("edit", "testcoll", "testtype", entity_id="edittype", view_id="RecordType_view")
        r = self.client.post(u, f)
        self.assertEqual(r.status_code,   200)
        self.assertEqual(r.reason_phrase, "OK")
        self.assertContains(r, site_title("<title>%s</title>"))
        self.assertContains(r, "<h3>Problem with entity identifier</h3>")
        self.assertContains(r, "<h3>'testtype' data in collection 'testcoll'</h3>")
        # Test context for re-rendered form
        expect_context = entitydata_recordtype_view_context_data(
            entity_id="!badentity", orig_id="orig_entity_id", action="edit"
            )
        self.assertDictionaryMatch(r.context, expect_context)
        # Check stored entity is unchanged
        self._check_view_data_values("edittype")
        return

# End.
