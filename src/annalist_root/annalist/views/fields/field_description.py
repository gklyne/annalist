"""
Define class to represent a field description when processing an entity view.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import traceback
import collections

import logging
log = logging.getLogger(__name__)

from annalist               import layout
from annalist               import message
from annalist.identifiers   import RDFS, ANNAL
from annalist.exceptions    import Annalist_Error, EntityNotFound_Error, UnexpectedValue_Error
from annalist.util          import extract_entity_id

# from annalist.models.recordfield            import RecordField
from annalist.models.entitytypeinfo         import EntityTypeInfo
from annalist.models.entityfinder           import EntityFinder

from annalist.views.fields.field_renderer   import FieldRenderer
from annalist.views.fields.find_renderers   import (
    is_repeat_field_render_type,
    get_value_mapper
    )
from annalist.views.fields.render_placement import (
    get_placement_classes
    )
from annalist.views.form_utils.fieldchoice  import FieldChoice

class FieldDescription(object):
    """
    Describes an entity view field, and methods to perform 
    manipulations involving the field description.
    """

    __slots__ = ("_collection", "_field_desc", "_field_suffix_index", "_field_suffix")

    def __init__(self, 
            collection, recordfield, view_context=None, 
            field_property=None, field_placement=None, 
            field_list=None, field_ids_seen=[],
            field_placement_classes=None
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
        field_list      if the field itself contains or references a list of fields, this is
                        that list of fields.
        field_ids_seen  field ids expanded so far, to check for recursive reference.
        field_placement_classes
                        if supplied, overrides field placement classes derived from value
                        for `field_placement` string.
        """
        self._collection    = collection
        # log.debug("FieldDescription recordfield: %r"%(recordfield,))
        field_id            = recordfield.get(ANNAL.CURIE.id,         "_missing_id_")
        field_name          = recordfield.get(ANNAL.CURIE.field_name, field_id)  # Field name in form
        field_label         = recordfield.get(RDFS.CURIE.label, "")
        field_help          = recordfield.get(RDFS.CURIE.comment, "")
        field_property      = field_property  or recordfield.get(ANNAL.CURIE.property_uri, "")
        field_placement     = field_placement or recordfield.get(ANNAL.CURIE.field_placement, "")
        field_placement_c   = field_placement_classes or get_placement_classes(field_placement)
        field_placeholder   = recordfield.get(ANNAL.CURIE.placeholder, "")
        field_tooltip       = recordfield.get(ANNAL.CURIE.tooltip, "")
        field_render_type   = extract_entity_id(recordfield.get(ANNAL.CURIE.field_render_type, ""))
        field_value_mode    = extract_entity_id(recordfield.get(ANNAL.CURIE.field_value_mode, "@@FieldDescription:value_mode@@"))
        field_ref_type      = extract_entity_id(recordfield.get(ANNAL.CURIE.field_ref_type, None))
        field_entity_type   = recordfield.get(ANNAL.CURIE.field_entity_type, None)
        field_group_ref     = extract_entity_id(recordfield.get(ANNAL.CURIE.group_ref, None))
        self._field_desc    = (
            { 'field_id':                   field_id
            , 'field_name':                 field_name
            , 'field_instance_name':        field_name
            , 'field_render_type':          field_render_type
            , 'field_value_mode':           field_value_mode
            , 'field_value_type':           recordfield.get(ANNAL.CURIE.field_value_type, "")
            , 'field_label':                field_label
            , 'field_help':                 field_help
            , 'field_property_uri':         field_property
            , 'field_placement':            field_placement_c
            , 'field_placeholder':          field_placeholder
            , 'field_tooltip':              field_tooltip
            , 'field_tooltip_test':         field_tooltip or (field_help) or ""
            , 'field_default_value':        recordfield.get(ANNAL.CURIE.default_value, None)
            , 'field_ref_type':             field_ref_type
            , 'field_ref_field':            recordfield.get(ANNAL.CURIE.field_ref_field, None)
            , 'field_ref_restriction':      recordfield.get(ANNAL.CURIE.field_ref_restriction, "ALL")
            , 'field_entity_type':          field_entity_type
            , 'field_choices':              None
            , 'field_group_ref':            field_group_ref
            , 'group_label':                None
            , 'group_add_label':            None
            , 'group_delete_label':         None
            , 'group_field_list':           None
            , 'group_field_descs':          None
            , 'field_renderer':             FieldRenderer(field_render_type, field_value_mode)
            , 'field_value_mapper':         get_value_mapper(field_render_type) # Used by fieldvaluemap.py
            })
        self._field_suffix_index  = 0    # No dup
        self._field_suffix        = ""
        # If field references type, pull in copy of type id and link values
        type_ref = self._field_desc['field_ref_type']
        if type_ref:
            restrict_values = self._field_desc['field_ref_restriction']
            entity_finder   = EntityFinder(collection, selector=restrict_values)
            entities        = entity_finder.get_entities_sorted(
                type_id=type_ref, context=view_context, altscope="select"
                )
            # Note: the options list may be used more than once, so the id generator
            # returned must be materialized as a list
            # Uses collections.OrderedfDict to preserve entity ordering
            self._field_desc['field_choices'] = collections.OrderedDict()
            if field_render_type in ["Enum_optional", "Enum_choice_opt"]:
                # Add blank choice for optional selections
                self._field_desc['field_choices'][''] = FieldChoice('', label=field_placeholder)
            for e in entities:
                eid = e.get_id()
                val = e.get_type_entity_id()
                if eid != layout.INITIAL_VALUES_ID:
                    self._field_desc['field_choices'][val] = FieldChoice(
                        val, label=e.get_label(), link=e.get_view_url_path()
                        )
        # If field references or contains field list, pull in field details
        if field_list:
            if field_id in field_ids_seen:
                raise Annalist_Error(field_id, "Recursive field reference in field group")
            field_ids_seen = field_ids_seen + [field_id]
            group_label  = field_label
            add_label    = recordfield.get(ANNAL.CURIE.repeat_label_add,    None) or "Add "+field_id
            remove_label = recordfield.get(ANNAL.CURIE.repeat_label_delete, None) or "Remove "+field_id
            group_field_descs = []
            for subfield in field_list:
                f = field_description_from_view_field(collection, subfield, view_context, field_ids_seen)
                group_field_descs.append(f)
            self._field_desc.update(
                { 'group_id':           field_id
                , 'group_label':        group_label
                , 'group_add_label':    add_label
                , 'group_delete_label': remove_label
                , 'group_field_list':   field_list          # Description from field/group
                , 'group_field_descs':  group_field_descs   # Resulting field description list
                })
        # log.debug("FieldDescription: %s"%field_id)
        # log.info("FieldDescription._field_desc %r"%(self._field_desc,))
        # log.info("FieldDescription.field_placement %r"%(self._field_desc['field_placement'],))
        return

    def __copy__(self):
        """
        Shallow copy of self.

        (Tried code from http://stackoverflow.com/a/15774013, but got type error)
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result._collection         = self._collection
        result._field_desc         = self._field_desc
        result._field_suffix_index = self._field_suffix_index
        result._field_suffix       = self._field_suffix
        return result

    def copy(self):
        return self.__copy__()

    def resolve_duplicates(self, properties):
        """
        Resolve duplicate property URIs that appear in a common context corresponding to
        the supplied `properties` diuctionary.  If there is a clash, assign a suffix that
        can be added to the field_id and field_property_uri to make them unique.

        The properties paramneter should be initialized to None by the calling program,
        and updated to the return value of this method each time it is called.
        """
        if properties is None:
            properties = (set(), set())
        i      = 0
        if ( (self._field_desc['field_name']         in properties[0]) or
             (self._field_desc['field_property_uri'] in properties[1]) ):
            i = 1
            suffix = ""
            while ( (self._field_desc['field_name']+suffix         in properties[0]) or
                    (self._field_desc['field_property_uri']+suffix in properties[1]) ):
                i += 1
                suffix = "__%d"%i
            self._field_suffix_index                = i
            self._field_suffix                      = suffix
            # Only use suffix for values that actually clash:
            if self._field_desc['field_name'] in properties[0]:
                self._field_desc['field_name']         += suffix 
            if self._field_desc['field_property_uri'] in properties[1]:
                self._field_desc['field_property_uri'] += suffix 
        properties[0].add(self._field_desc['field_name'])
        properties[1].add(self._field_desc['field_property_uri'])
        return properties

    def get_field_id(self):
        """
        Returns the field identifier
        """
        return self._field_desc['field_id']

    def get_field_name(self):
        """
        Returns form field name to be used for the described field
        """
        return self._field_desc['field_name']

    def set_field_instance_name(self, instance_name):
        """
        Set instance name for field (used when scanning field groups)

        This is the full field instance name including group ids and 
        indexes.
        """
        self._field_desc['field_instance_name'] = instance_name
        return

    def get_field_instance_name(self):
        """
        Get instance name for field (used when scanning field groups)
        """
        return self._field_desc['field_instance_name']

    def get_field_property_uri(self):
        """
        Returns form field property URI to be used for the described field
        """
        return self._field_desc['field_property_uri']

    def get_field_subproperty_uris(self):
        """
        Returns list of possible subproperty URIs for the described field
        """
        subproperty_uris = []
        if self._collection is not None:
            property_uri     = self.get_field_property_uri()
            subproperty_uris = self._collection.cache_get_subproperty_uris(property_uri)
        return subproperty_uris

    def get_field_value_key(self, entityvals):
        """
        Return field value key used in current entity.

        This takes account of possible use of subproperties of the property URI
        specified in the field description.  If the declared property URI is not 
        present in the entity, and a subproperty URI is present, then that 
        subproperty URI is returned.  Otherwise the declared property URI is returned.
        """
        if self.get_field_property_uri() not in entityvals:
            for altkey in self.get_field_subproperty_uris():
                if altkey in entityvals:
                    return altkey
        return self.get_field_property_uri()

    def group_ref(self):
        """
        If the field itself contains or uses a group of fields, returns an
        reference (a group_id) for the field group, or None
        """
        return self._field_desc['field_group_ref']

    def group_view_fields(self):
        """
        If the field itself contains or uses a group of fields, returns a
        list of the field references
        """
        field_list = self._field_desc.get('group_field_list', None)
        if field_list is None:
            msg = "Field %(field_id)s is missing 'group_field_list' value"%(self._field_desc)
            log.error(msg)
            raise ValueError(msg)
            # log.error("".join(traceback.format_stack()))
            # return []
        return field_list

    def group_field_descs(self):
        """
        If the field itself contains or uses a group of fields, returns a
        list of field descriptions as a list of FieldDescriptiopn values.
        """
        return self._field_desc['group_field_descs']

    def is_repeat_group(self):
        """
        Returns true if this is a repeating field, in which case the field
        value is assumed to be a list of values to be rendered, and to
        have buttons for adding and removing values.
        """
        return is_repeat_field_render_type(self._field_desc['field_render_type'])

    def is_enum_field(self):
        """
        Returns true if this is an enumerated-value field, in which case the
        'field_ref_type' field is assumed to the type_id of the value 
        type to be enumerated.
        """
        enum_render_types = (
            [ "EntityTypeId"
            , "Type", "View", "List", "Field"
            , "Enum", "Enum_optional", "Enum_choice"
            ])
        return self._field_desc['field_render_type'] in enum_render_types

    def has_new_button(self):
        """
        Returns true if this field has a control (a 'new' or '+' button)
        that invokes a new form to create a new entity.
        """
        # Strictly, this test includes 'Enum_choice' which does not have a '+' button,
        # but since the absent button cannot be clicked, the infidelity here is benign
        return self._field_desc['field_ref_type'] is not None

    def is_import_field(self):
        """
        Returns 'true' if this field has a control (an 'import' button) that is used 
        to request additional external data is added to an entity
        """
        return self._field_desc['field_value_mode'] == "Value_import"

    def is_upload_field(self):
        """
        Returns 'true' if this field is a file-upload field (selected file contents are 
        returned with the form response.)
        """
        return self._field_desc['field_value_mode'] == "Value_upload"

    def has_field_list(self):
        """
        Returns true if this field contains or references a list of 
        field descriptions

        @@ (Currently, this function duplicates `is_repeat_group`.)

        @@ test for:  group_ref, group_field_descs, and group_id
        """
        return is_repeat_field_render_type(self._field_desc['field_render_type'])

    def __repr1__(self):
        return (
            "FieldDescription(\n"+
            "  { 'field_id': %r\n"%(self._field_desc["field_id"])+
            "  , 'field_name': %r\n"%(self.get_field_name())+
            "  , 'field_render_type': %r\n"%(self._field_desc["field_render_type"])+
            "  , 'field_property_uri': %r\n"%(self.get_field_property_uri())+
            "  , 'field_ref_type': %r\n"%(self._field_desc["field_ref_type"])+
            "  , 'group_field_list': %r\n"%(self._field_desc["group_field_list"])+
            "  , 'group_field_descs': %r\n"%(self._field_desc["group_field_descs"])+
            "  })"
            )

    def __repr2__(self):
        return (
            "FieldDescription("+repr(self._field_desc)+")"
            )

    def __repr3__(self):
        return (
            "FieldDescription("+repr(self._field_desc['field_id'])+")"
            )

    def __repr__(self):
        return self.__repr1__()

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

def field_description_from_view_field(
    collection, field, view_context=None, field_ids_seen=[]
    ):
    """
    Returns a field description value created using information from
    a field reference in a view description record (i.e. a dictionary
    containing a field id value and optional field property URI and
    placement values.  (The optional values, if not provided, are 
    obtained from the referenced field description)

    collection      is a collection from which data is being rendered.
    field           is a dictionary with the field description from a view or list 
                    description, containing a field id and placement values.
    view_context    is a dictionary of additional values that may be used in assembling
                    values to be used when rendering the field.  In particular, a copy 
                    of the view description record provides context for some enumeration 
                    type selections.
    field_ids_seen  field ids expanded so far, to check for recursive reference.
    """
    field_id    = extract_entity_id(field[ANNAL.CURIE.field_id])
    # recordfield = RecordField.load(collection, field_id, altscope="all")
    recordfield = collection.get_field(field_id)
    if recordfield is None:
        log.warning("Can't retrieve definition for field %s"%(field_id))
        # recordfield = RecordField.load(collection, "Field_missing", altscope="all")
        recordfield = collection.get_field("Field_missing")
        recordfield[RDFS.CURIE.label] = message.MISSING_FIELD_LABEL%{ 'id': field_id }

    # If field references group, pull in group details
    field_list = recordfield.get(ANNAL.CURIE.field_fields, None)
    if not field_list:
        group_ref = extract_entity_id(recordfield.get(ANNAL.CURIE.group_ref, None))
        if group_ref:
            raise UnexpectedValue_Error("Group %s used in field %s"%(group_ref, field_id))

    # If present, `field_property` and `field_placement` override values in the field dexcription
    return FieldDescription(
        collection, recordfield, view_context=view_context, 
        field_property=field.get(ANNAL.CURIE.property_uri, None),
        field_placement=field.get(ANNAL.CURIE.field_placement, None), 
        field_list=field_list,
        field_ids_seen=field_ids_seen
        )

# End.
