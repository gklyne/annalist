"""
Define class to represent a field description when processing an entity view.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import collections

import logging
log = logging.getLogger(__name__)

from annalist.identifiers               import RDFS, ANNAL
from annalist.exceptions                import EntityNotFound_Error

from annalist.models.recordfield        import RecordField
from annalist.models.recordview         import RecordView
from annalist.models.entitytypeinfo     import EntityTypeInfo
from annalist.models.entityfinder       import EntityFinder

from annalist.views.fields.render_utils import (
    get_edit_renderer, 
    get_view_renderer,
    get_head_renderer, 
    get_item_renderer,
    get_value_mapper
    )
from annalist.views.fields.render_placement import (
    get_placement_classes
    )

class FieldDescription(object):
    """
    Describes an entity view field, and methods to perform 
    manipulations involving the field description.
    """

    def __init__(self, collection, field, view_context):
        """
        Creates a field description value to use in a context value when
        rendering a form.  Values defined here are mentioned in field
        rendering templates.

        The FieldDescription object behaves as a dictionary containing the 
        various field attributes.

        collection      is a collection from which data is being rendered.
        field           is a dictionary with the field description from a view or list 
                        description, containing a field id and placement values.
        view_context    is a dictionary of additional values that may be used in assembling
                        values to be used when rendering the field.  In particular, a copy 
                        of the view description record provides context for some enumeration 
                        type selections.
        """
        field_id    = field[ANNAL.CURIE.field_id]       # Field ID slug in URI
        recordfield = RecordField.load(collection, field_id, collection._parentsite)
        if recordfield is None:
            log.warning("Can't retrieve definition for field %s"%(field_id))
            recordfield = RecordField.load(collection, "Field_missing", collection._parentsite)
        field_name      = recordfield.get(ANNAL.CURIE.field_name, field_id)   # Field name in form
        field_label     = recordfield.get(RDFS.CURIE.label, "")
        field_property  = (
            field.get(ANNAL.CURIE.property_uri, None) or 
            recordfield.get(ANNAL.CURIE.property_uri, "")
            )
        field_placement = get_placement_classes(
            field.get(ANNAL.CURIE.field_placement, None) or 
            recordfield.get(ANNAL.CURIE.field_placement, "")
            )
        log.debug("recordfield   %r"%(recordfield and recordfield.get_values()))
        # log.info("FieldDescription: field['annal:field_placement'] %s"%(field['annal:field_placement']))
        # log.info("FieldDescription: field_placement %r"%(get_placement_classes(field['annal:field_placement']),))
        field_render_type = recordfield.get(ANNAL.CURIE.field_render_type, "")
        self._field_desc = (
            { 'field_id':                   field_id
            , 'field_name':                 field_name
            , 'field_label':                field_label
            , 'field_help':                 recordfield.get(RDFS.CURIE.comment, "")
            , 'field_property_uri':         field_property
            , 'field_placement':            field_placement
            , 'field_render_head':          get_head_renderer(field_render_type)
            , 'field_render_item':          get_item_renderer(field_render_type)
            , 'field_render_view':          get_view_renderer(field_render_type)
            , 'field_render_edit':          get_edit_renderer(field_render_type)
            , 'field_value_mapper':         get_value_mapper(field_render_type)
            , 'field_value_type':           recordfield.get(ANNAL.CURIE.field_value_type, "")
            , 'field_placeholder':          recordfield.get(ANNAL.CURIE.placeholder, "")
            , 'field_default_value':        recordfield.get(ANNAL.CURIE.default_value, None)
            , 'field_options_typeref':      recordfield.get(ANNAL.CURIE.options_typeref, None)
            , 'field_restrict_values':      recordfield.get(ANNAL.CURIE.restrict_values, "ALL")
            , 'field_choice_labels':        None
            , 'field_choice_links':         None
            , 'field_group_viewref':        recordfield.get(ANNAL.CURIE.group_viewref, None)
            , 'group_label':                None
            , 'group_add_label':            None
            , 'group_delete_label':         None
            , 'group_fields':               None
            })
        # If field references type, pull in copy of type id and link values
        type_ref = self._field_desc['field_options_typeref']
        if type_ref:
            restrict_values = self._field_desc['field_restrict_values']
            entity_finder   = EntityFinder(collection, selector=restrict_values)
            entities        = entity_finder.get_entities_sorted(type_id=type_ref, context=view_context)
            # Note: the options list may be used more than once, so the id generator
            # returned must be materialized as a list
            # Uses collections.OrderedfDict to preserve entity ordering
            # 'Enum_optional' adds a blank entry at the start of the list
            self._field_desc['field_choice_labels'] = collections.OrderedDict()
            self._field_desc['field_choice_links']  = collections.OrderedDict()
            if field_render_type == "Enum_optional":
                self._field_desc['field_choice_labels'][''] = ""
                self._field_desc['field_choice_links']['']  = None
            for e in entities:
                eid = e.get_id()
                if eid != "_initial_values":
                    self._field_desc['field_choice_labels'][eid] = eid   # @@TODO: be smarter about label?
                    self._field_desc['field_choice_links'][eid]  = e.get_view_url_path()
            # log.info("typeref %s: %r"%
            #     (self._field_desc['field_options_typeref'], list(self._field_desc['field_choices']))
            #     )
        # If field references view, pull in details from view, including field details
        group_ref = self._field_desc['field_group_viewref']
        if group_ref:
            group_view = RecordView.load(collection, group_ref, collection._parentsite)
            if not group_view:
                raise EntityNotFound_Error("View %s used in field %s"%(group_ref, field_id))
            group_label = field_label or group_view.get(RDFS.CURIE.label, group_ref)
            group_fields = []
            repeat_index = 0
            for subfield in group_view[ANNAL.CURIE.view_fields]:
                f = FieldDescription(collection, subfield, view_context)
                group_fields.append(f)
            self._field_desc.update(
                { 'group_id':           field_id
                , 'group_label':        group_label
                , 'group_add_label':    recordfield.get(ANNAL.CURIE.repeat_label_add, "Add "+group_label)
                , 'group_delete_label': recordfield.get(ANNAL.CURIE.repeat_label_delete, "Remove "+group_label)
                , 'group_fields':       group_fields
                })
        # log.info("FieldDescription: %s"%field_id)
        # log.info("FieldDescription.field %r"%field)
        # log.info("FieldDescription.field_context %r"%(self._field_desc,))
        # log.info("FieldDescription.field_placement %r"%(self._field_desc['field_placement'],))
        return

    def get_structure_description(self):
        """
        Helper function returns field description information
        (field selector and placement).

        @@TODO: redundant?
        """
        return (
            { 'field_id':           self._field_desc['field_id']
            , 'field_placement':    self._field_desc['field_placement']
            , 'field_property_uri': self._field_desc['field_property_uri']
            })

    def __repr__(self):
        return (
            "FieldDescription("+
            "  { 'field_id': %r\n"%(self._field_desc["field_id"])+
            "  , 'field_name': %r\n"%(self._field_desc["field_name"])+
            "  , 'field_property_uri': %r\n"%(self._field_desc["field_property_uri"])+
            "  })"
            )

    # Define methods to facilitate access to values using dictionary operations
    # on the FieldDescription object

    def keys(self):
        """
        Return collection metadata value keys
        """
        return self._field_desc.keys()

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._field_desc.items()

    def get(self, key, default):
        """
        Equivalent to dict.get() function
        """
        return self[key] if self._field_desc and key in self._field_desc else default

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._field_desc[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._field_desc[k] = v
        return

    def __iter__(self):
        """
        Iterator over dictionary keys
        """
        for k in self._field_desc:
            yield k
        return

# End.
