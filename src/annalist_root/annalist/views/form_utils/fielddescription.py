"""
Define class to represent a field description when processing an entity view.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import collections

import logging
log = logging.getLogger(__name__)

from annalist.identifiers   import RDFS, ANNAL
from annalist.exceptions    import Annalist_Error, EntityNotFound_Error
from annalist.util          import extract_entity_id

from annalist.models.recordgroup            import RecordGroup
from annalist.models.recordfield            import RecordField
from annalist.models.entitytypeinfo         import EntityTypeInfo
from annalist.models.entityfinder           import EntityFinder

from annalist.views.fields.render_utils     import (
    get_view_renderer,
    get_edit_renderer, 
    get_label_view_renderer,
    get_label_edit_renderer, 
    get_col_head_renderer, 
    get_col_head_view_renderer, 
    get_col_head_edit_renderer, 
    get_col_view_renderer,
    get_col_edit_renderer,
    get_mode_renderer,
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
    def __init__(self, 
            collection, recordfield, view_context=None, 
            field_property=None, field_placement=None, 
            group_view=None, group_ids_seen=[]
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
        group_ids_seen  group ids expanded so far, to check for recursive reference.
        """
        self._collection = collection
        # log.debug("FieldDescription recordfield: %r"%(recordfield,))
        field_id            = recordfield.get(ANNAL.CURIE.id,         "_missing_id_")
        field_name          = recordfield.get(ANNAL.CURIE.field_name, field_id)  # Field name in form
        field_label         = recordfield.get(RDFS.CURIE.label, "")
        field_property      = field_property or recordfield.get(ANNAL.CURIE.property_uri, "")
        field_placement     = field_placement or recordfield.get(ANNAL.CURIE.field_placement, "")
        field_placeholder   = recordfield.get(ANNAL.CURIE.placeholder, "")
        field_render_type   = extract_entity_id(recordfield.get(ANNAL.CURIE.field_render_type, ""))
        field_value_mode    = extract_entity_id(recordfield.get(ANNAL.CURIE.field_value_mode, "@@FieldDescription:value_mode@@"))
        field_ref_type      = extract_entity_id(recordfield.get(ANNAL.CURIE.field_ref_type, None))
        field_val_type      = recordfield.get(ANNAL.CURIE.field_value_type, "")
        field_entity_type   = recordfield.get(ANNAL.CURIE.field_entity_type, None)
        field_group_ref     = extract_entity_id(recordfield.get(ANNAL.CURIE.group_ref, None))
        self._field_desc    = (
            { 'field_id':                   field_id
            , 'field_name':                 field_name
            , 'field_instance_name':        field_name
            , 'field_render_type':          field_render_type
            , 'field_value_mode':           field_value_mode
            , 'field_label':                field_label
            , 'field_help':                 recordfield.get(RDFS.CURIE.comment, "")
            , 'field_property_uri':         field_property
            , 'field_placement':            get_placement_classes(field_placement)
            #@@ , 'field_value_type':           field_val_type
            #@@TODO: LATER: rename 'field_target_type' to 'field_value_type' when old references are flushed out
            #@@      See also references to 'field_target_type' in entityedit.py
            , 'field_target_type':          recordfield.get(ANNAL.CURIE.field_target_type, field_val_type)
            , 'field_placeholder':          field_placeholder
            , 'field_default_value':        recordfield.get(ANNAL.CURIE.default_value, None)
            , 'field_ref_type':             field_ref_type
            , 'field_ref_field':            recordfield.get(ANNAL.CURIE.field_ref_field, None)
            , 'field_ref_restriction':      recordfield.get(ANNAL.CURIE.field_ref_restriction, "ALL")
            , 'field_entity_type':          field_entity_type
            , 'field_choices':              None
            # , 'field_choice_labels':        None
            # , 'field_choice_links':         None
            , 'field_group_ref':            field_group_ref
            , 'group_label':                None
            , 'group_add_label':            None
            , 'group_delete_label':         None
            , 'group_view':                 None
            , 'group_field_descs':          None
            , 'field_render_view':          get_view_renderer(         field_render_type, field_value_mode)
            , 'field_render_edit':          get_edit_renderer(         field_render_type, field_value_mode)
            , 'field_render_label_view':    get_label_view_renderer(   field_render_type, field_value_mode)
            , 'field_render_label_edit':    get_label_edit_renderer(   field_render_type, field_value_mode)
            , 'field_render_colhead':       get_col_head_renderer(     field_render_type, field_value_mode)
            , 'field_render_colhead_view':  get_col_head_view_renderer(field_render_type, field_value_mode)
            , 'field_render_colhead_edit':  get_col_head_edit_renderer(field_render_type, field_value_mode)
            , 'field_render_colview':       get_col_view_renderer(     field_render_type, field_value_mode)
            , 'field_render_coledit':       get_col_edit_renderer(     field_render_type, field_value_mode)
            , 'field_render_mode':          get_mode_renderer(         field_render_type, field_value_mode)
            , 'field_value_mapper':         get_value_mapper(field_render_type)
            })
        self._field_suffix_index  = 0    # No dup
        self._field_suffix        = ""
        # If field references type, pull in copy of type id and link values
        type_ref = self._field_desc['field_ref_type']
        if type_ref:
            restrict_values = self._field_desc['field_ref_restriction']
            entity_finder   = EntityFinder(collection, selector=restrict_values)
            # Determine subtypes of field entity type, if specified
            # @@TODO: subtype logic here is just wrong...
            #         need context to conver info that can be used to calculate supertypes
            #         on-the-fly as needed by the field restriction expression.  E.g. include
            #         collection object in context.
            if field_entity_type and restrict_values:
                field_entity_subtypes = (
                    [ t.get_type_uri()
                      for t in entity_finder.get_collection_uri_subtypes(field_entity_type)
                    ])
                self._field_desc['field_entity_subtypes'] = field_entity_subtypes
                field_view_context = dict(view_context or {}, field={'subtypes': field_entity_subtypes})
            else:
                field_view_context = view_context
            entities        = entity_finder.get_entities_sorted(
                type_id=type_ref, context=field_view_context, scope="all"
                )
            # Note: the options list may be used more than once, so the id generator
            # returned must be materialized as a list
            # Uses collections.OrderedfDict to preserve entity ordering
            # 'Enum_optional' adds a blank entry at the start of the list
            self._field_desc['field_choices'] = collections.OrderedDict()
            if field_render_type == "Enum_optional":
                self._field_desc['field_choices'][''] = FieldChoice('', label=field_placeholder)
            for e in entities:
                eid = e.get_id()
                val = e.get_type_entity_id()
                if eid != "_initial_values":
                    self._field_desc['field_choices'][val] = FieldChoice(
                        val, label=e.get_label(), link=e.get_view_url_path()
                        )
            log.debug("FieldDescription: typeref %s: %r"%
                (self._field_desc['field_ref_type'], list(self._field_desc['field_choices'].items()))
                )
        # If field references group, pull in field details
        if group_view:
            if field_id in group_ids_seen:
                raise Annalist_Error(field_id, "Recursive field reference in field group")
            group_ids_seen = group_ids_seen + [field_id]
            group_label = (field_label or 
                group_view.get(RDFS.CURIE.label, self._field_desc['field_group_ref'])
                )
            add_label    = recordfield.get(ANNAL.CURIE.repeat_label_add, None) or "Add "+field_id
            remove_label = recordfield.get(ANNAL.CURIE.repeat_label_delete, None) or "Remove "+field_id
            group_field_descs = []
            for subfield in group_view[ANNAL.CURIE.group_fields]:
                f = field_description_from_view_field(collection, subfield, view_context, group_ids_seen)
                group_field_descs.append(f)
            self._field_desc.update(
                { 'group_id':           field_id
                , 'group_label':        group_label
                , 'group_add_label':    add_label
                , 'group_delete_label': remove_label
                , 'group_view':         group_view
                , 'group_field_descs':  group_field_descs
                })
        # log.debug("FieldDescription: %s"%field_id)
        # log.info("FieldDescription._field_desc %r"%(self._field_desc,))
        # log.info("FieldDescription.field_placement %r"%(self._field_desc['field_placement'],))
        return

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

    def group_ref(self):
        """
        If the field itself contains or uses a group of fields, returns an
        reference (a group_id) for the field group, or None
        """
        return self._field_desc['field_group_ref']

    def group_view_fields(self):
        """
        If the field itself contains or uses a group of fields, returns a
        RecordGroupValue or dictionary describing the fields.
        """
        group_view = self._field_desc['group_view']
        if group_view is None:
            log.error("Field %(field_id)s is missing `group_view` value"%(self._field_desc))
            return []
        return self._field_desc['group_view'][ANNAL.CURIE.group_fields]

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
        repeat_render_types = ["RepeatGroup", "RepeatGroupRow", "RepeatListRow"]
        return self._field_desc['field_render_type'] in repeat_render_types

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

    def has_field_group_ref(self):
        """
        Returns true if this field contains a reference to a field group,
        which in turn references further field descriptions.

        @@@ (Currently, this function duplicates `is_repeat_group`.)

        @@@ test for:  group_ref, group_field_descs, and group_id
        """
        field_group_types = ["RepeatGroup", "RepeatGroupRow", "RepeatListRow"]
        return self._field_desc['field_render_type'] in field_group_types

    def __repr__(self):
        return (
            "FieldDescription("+
            "  { 'field_id': %r\n"%(self._field_desc["field_id"])+
            "  , 'field_name': %r\n"%(self.get_field_name())+
            "  , 'field_render_type': %r\n"%(self._field_desc["field_render_type"])+
            "  , 'field_property_uri': %r\n"%(self.get_field_property_uri())+
            "  , 'type_ref': %r"%(self._field_desc["field_ref_type"])+
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

def field_description_from_view_field(collection, field, view_context=None, group_ids_seen=[]):
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
    group_ids_seen  group ids expanded so far, to check for recursive reference.
    """
    #@@TODO: for resilience, revert this when all tests pass?
    # field_id    = field.get(ANNAL.CURIE.field_id, "Field_id_missing")  # Field ID slug in URI
    #@@
    field_id    = extract_entity_id(field[ANNAL.CURIE.field_id])
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
    group_ref = extract_entity_id(recordfield.get(ANNAL.CURIE.group_ref, None))
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
        group_view=group_view,
        group_ids_seen=group_ids_seen
        )

# End.
