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

from annalist.models.recordgroup        import RecordGroup
from annalist.models.recordfield        import RecordField
from annalist.models.entitytypeinfo     import EntityTypeInfo
from annalist.models.entityfinder       import EntityFinder

from annalist.views.fields.render_utils import (
    get_view_renderer,
    get_edit_renderer, 
    get_colhead_renderer, 
    get_colview_renderer,
    get_coledit_renderer,
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
    def __init__(self, 
            collection, recordfield, view_context=None, 
            field_property=None, field_placement=None, 
            group_view=None
            ):
        """
        Creates a field description value to use in a context value when
        rendering a form.  Values defined here are mentioned in field
        rendering templates.

        The FieldDescription object behaves as a dictionary containing the 
        various field attributes.

        collection      is a collection from which data is being rendered.
        recordfield     is a RecordField value or dictionary containing details of
                        the field for which a descriptor is constructed.
        view_context    is a dictionary of additional values that may be used in assembling
                        values to be used when rendering the field.  In particular, a copy 
                        of the view description record provides context for some enumeration 
                        type selections.
        field_property  if supplied, overrides the field property URI from `recordfield`
        field_placement if supplied, overrides field placement from `recordfield`
        group_view      if the field itself references a list of fields, this is a
                        RecordGroup value or dictionary containing the referenced list 
                        of fields.
        """
        # log.debug("FieldDescription recordfield: %r"%(recordfield,))
        field_id            = recordfield.get(ANNAL.CURIE.id,         "_missing_id_")
        field_name          = recordfield.get(ANNAL.CURIE.field_name, field_id)  # Field name in form
        field_label         = recordfield.get(RDFS.CURIE.label, "")
        field_property      = field_property or recordfield.get(ANNAL.CURIE.property_uri, "")
        field_placement     = field_placement or recordfield.get(ANNAL.CURIE.field_placement, "")
        field_render_type   = recordfield.get(ANNAL.CURIE.field_render_type, "")
        self._field_desc    = (
            { 'field_id':                   field_id
            , 'field_name':                 field_name
            , 'field_label':                field_label
            , 'field_help':                 recordfield.get(RDFS.CURIE.comment, "")
            , 'field_property_uri':         field_property
            , 'field_placement':            get_placement_classes(field_placement)
            , 'field_render_type':          field_render_type
            , 'field_render_view':          get_view_renderer(field_render_type)
            , 'field_render_edit':          get_edit_renderer(field_render_type)
            , 'field_render_colhead':       get_colhead_renderer(field_render_type)
            , 'field_render_colview':       get_colview_renderer(field_render_type)
            , 'field_render_coledit':       get_coledit_renderer(field_render_type)
            , 'field_value_mapper':         get_value_mapper(field_render_type)
            , 'field_value_type':           recordfield.get(ANNAL.CURIE.field_value_type, "")
            , 'field_placeholder':          recordfield.get(ANNAL.CURIE.placeholder, "")
            , 'field_default_value':        recordfield.get(ANNAL.CURIE.default_value, None)
            , 'field_options_typeref':      recordfield.get(ANNAL.CURIE.options_typeref, None)
            , 'field_restrict_values':      recordfield.get(ANNAL.CURIE.restrict_values, "ALL")
            , 'field_choice_labels':        None
            , 'field_choice_links':         None
            , 'field_group_ref':            recordfield.get(ANNAL.CURIE.group_ref, None)
            , 'group_label':                None
            , 'group_add_label':            None
            , 'group_delete_label':         None
            , 'group_view':                 None
            , 'group_field_descs':          None
            })
        # If field references type, pull in copy of type id and link values
        type_ref = self._field_desc['field_options_typeref']
        if type_ref:
            restrict_values = self._field_desc['field_restrict_values']
            entity_finder   = EntityFinder(collection, selector=restrict_values)
            entities        = entity_finder.get_entities_sorted(
                type_id=type_ref, context=view_context
                )
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
        # If field references group, pull in field details
        if group_view:
            group_label = (field_label or 
                group_view.get(RDFS.CURIE.label, self._field_desc['field_group_ref'])
                )
            group_field_descs = []
            for subfield in group_view[ANNAL.CURIE.group_fields]:
                f = field_description_from_view_field(collection, subfield, view_context)
                group_field_descs.append(f)
            self._field_desc.update(
                { 'group_id':           field_id
                , 'group_label':        group_label
                , 'group_add_label':    recordfield.get(ANNAL.CURIE.repeat_label_add, "Add "+group_label)
                , 'group_delete_label': recordfield.get(ANNAL.CURIE.repeat_label_delete, "Remove "+group_label)
                , 'group_view':         group_view
                , 'group_field_descs':  group_field_descs
                })
        # log.debug("FieldDescription: %s"%field_id)
        # log.info("FieldDescription._field_desc %r"%(self._field_desc,))
        # log.info("FieldDescription.field_placement %r"%(self._field_desc['field_placement'],))
        return

    def group_ref(self):
        """
        If the field itself contains or uses a group of fields, returns an
        reference (a group_id) for the field group, or None
        """
        return self._field_desc['field_group_ref']

    def group_view_fields(self):
        """
        If the field itself contains or uses a group of fields, returns a
        RecoirdGroupvalue or dictionary describiung the fields field.
        """
        return self._field_desc['group_view'][ANNAL.CURIE.group_fields]

    def group_field_descs(self):
        """
        If the field itself contains or uses a group of fields, returns a
        list of field descriptions as a list of FieldDescriptiopn values.
        """
        return self._field_desc['group_field_descs']

    def is_repeat_group(self):
        """
        Returns true if this is a repeating field, in which case the field value
        is assumed to be a list of values to be rendered.
        """
        repeat_render_types = ["RepeatGroup", "RepeatGroupRow", "RepeatListRow"]
        return self._field_desc['field_render_type'] in repeat_render_types

    def __repr__(self):
        return (
            "FieldDescription("+
            "  { 'field_id': %r\n"%(self._field_desc["field_id"])+
            "  , 'field_name': %r\n"%(self._field_desc["field_name"])+
            "  , 'field_property_uri': %r\n"%(self._field_desc["field_property_uri"])+
            "  , 'group_ref': %r"%(self._field_desc["field_group_ref"])+
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

def field_description_from_view_field(collection, field, view_context=None):
    """
    Returns a field description value created using information from
    a field reference in a view description record (i.e. a dictionary
    containing a field id value and optional field property URI and
    placement values.  (The optional values, if not provided, are 
    obtained from the referenced field descriptionb)

    collection      is a collection from which data is being rendered.
    field           is a dictionary with the field description from a view or list 
                    description, containing a field id and placement values.
    view_context    is a dictionary of additional values that may be used in assembling
                    values to be used when rendering the field.  In particular, a copy 
                    of the view description record provides context for some enumeration 
                    type selections.
    """
    #@@TODO: for resilience, revert this when all tests pass?
    # field_id    = field.get(ANNAL.CURIE.field_id, "Field_id_missing")  # Field ID slug in URI
    #@@
    field_id    = field[ANNAL.CURIE.field_id]
    recordfield = RecordField.load(collection, field_id, collection._parentsite)
    if recordfield is None:
        log.warning("Can't retrieve definition for field %s"%(field_id))
        recordfield = RecordField.load(collection, "Field_missing", collection._parentsite)
    field_property  = (
        field.get(ANNAL.CURIE.property_uri, None) or 
        recordfield.get(ANNAL.CURIE.property_uri, "")
        )
    field_placement = get_placement_classes(
        field.get(ANNAL.CURIE.field_placement, None) or 
        recordfield.get(ANNAL.CURIE.field_placement, "")
        )
    # If field references group, pull in field details
    group_ref = recordfield.get(ANNAL.CURIE.group_ref, None)
    if group_ref:
        group_view = RecordGroup.load(collection, group_ref, collection._parentsite)
        if not group_view:
            raise EntityNotFound_Error("Group %s used in field %s"%(group_ref, field_id))
    else:
        group_view = None
    return FieldDescription(
        collection, recordfield, view_context=view_context, 
        field_property=field.get(ANNAL.CURIE.property_uri, None),
        field_placement=field.get(ANNAL.CURIE.field_placement, None), 
        group_view=group_view
        )

# End.
