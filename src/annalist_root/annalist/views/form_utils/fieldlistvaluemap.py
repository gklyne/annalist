"""
Annalist class for processing a list of field mappings for conversion between
entity values context values and form data.

A FieldListValueMap is an object that can be inserted into an entity view value
mapping table to process the corresponding list of fields.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import collections

from django.conf                        import settings

from annalist.identifiers               import RDFS, ANNAL

from annalist.views.form_utils.fielddescription import FieldDescription, field_description_from_view_field
from annalist.views.form_utils.fieldvaluemap    import FieldValueMap
from annalist.views.form_utils.repeatvaluesmap  import RepeatValuesMap
from annalist.views.fields.render_placement     import (
    Placement, LayoutOptions,
    make_field_width, make_field_offset, make_field_display,
    )

#   ----------------------------------------------------------------------------
#
#   Support functions for generating padding fields
#
#   ----------------------------------------------------------------------------

padding_field_data = (
    { "annal:id":                   "Field_padding"
    , "rdfs:label":                 ""
    , "annal:field_render_type":    "Padding"
    , "annal:field_value_mode":     "Value_direct"
    })

def get_padding_field_desc(pad_s, pad_m, pad_l):
    if pad_s == 0:
        if pad_m == 0:
            if pad_l == 0:
                # No padding
                return None
            else:
                # Pad for large only
                disp = "show-for-large-up large-%d columns"%(pad_l,)
        else:
            if pad_l == 0:
                # Pad for medium only
                disp = "show-for-medium-only medium-%d columns"%(pad_m,)
            else:
                disp = "hide-for-small-only medium-%d large-%d columns"%(pad_m, pad_l)
    else:
        if pad_m == 0:
            if pad_l == 0:
                # Pad for small only
                disp = "show-for-small-only small-%d"%(pad_s,)
            else:
                # Pad for small and large
                disp = "hide-for-medium-only small-%d large-%d"%(pad_s, pad_l)
        else:
            if pad_l == 0:
                # Pad for small and medium
                disp = "hide-for-large-up small-%d medium-%d"%(pad_s, pad_m)
            else:
                # Pad all sizes
                disp = "small-%d medium-%d large-%d"%(pad_s, pad_m, pad_l)
    placement = Placement(
            width=make_field_width(sw=pad_s, mw=pad_m, lw=pad_l),
            offset=make_field_offset(so=0, mo=0, lo=0),
            display=make_field_display(sd=bool(pad_s), md=bool(pad_m), ld=bool(pad_l)),
            field=disp,
            label="small-4 columns",
            value="small-8 columns"
            )
    pad_desc = FieldDescription(
        None, padding_field_data, field_placement_classes=placement
        )
    return pad_desc

def next_field(pos_prev, offset, width, display):
    """
    Local helper calculates padding required for a given previous position,
    field offset and field width.
    """
    if not display:
        return (0, 0, pos_prev)
    if offset < pos_prev:
        # Force to next row
        pad1     = 12 - pos_prev
        pad2     = offset
        if offset == 0 and width > pad1:
            pad1 = 0
    else:
        # Same row
        pad1 = offset - pos_prev
        pad2 = 0
    pos_next = offset + width
    if pos_next == 12:
        pos_next = 0
    elif pos_next > 12:     # Overlength field is forced to next row
        pad2     = 0
        pos_next = width
    return (pad1, pad2, pos_next)

def get_padding_desc(position, field_desc):
    """
    Calculate padding required to position field where requested, and return:
    [0] updated position vector
    [1] 1st padding field descriptor, or None
    [2] 2nd padding field descriptor, or None

    Note: 2 padding fields may be required in some circumstances:
    (a) to force a field to start on the next row, and 
    (b) to offset the field from the start of next row.

    position    is the position immediately following the preceeding field.
    field_desc  is the next field descriptor.
    """
    placement = field_desc['field_placement']
    pad1_s, pad2_s, next_s  = next_field(position.s, placement.offset.s, placement.width.s, placement.display.s)
    pad1_m, pad2_m, next_m  = next_field(position.m, placement.offset.m, placement.width.m, placement.display.m)
    pad1_l, pad2_l, next_l  = next_field(position.l, placement.offset.l, placement.width.l, placement.display.l)
    pos_next  = LayoutOptions(s=next_s, m=next_m, l=next_l)
    pad1_desc = get_padding_field_desc(pad1_s, pad1_m, pad1_l)
    pad2_desc = get_padding_field_desc(pad2_s, pad2_m, pad2_l)
    return (pos_next, pad1_desc, pad2_desc)

#   ----------------------------------------------------------------------------
#
#   FieldListValueMap class
#
#   ----------------------------------------------------------------------------

class FieldListValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.
    """

    def __init__(self, c, coll, fields, view_context):
        """
        Define an entry to be added to an entity view value mapping table,
        corresponding to a list of field descriptions.

        c               name of field used for this value in display context
        coll            is a collection from which data is being rendered.
        fields          list of field descriptions from a view definition, each
                        of which is a dictionary with the field description from 
                        a view or list description.
        view_context    is a dictionary of additional values that may be used in
                        assembling values to be used when rendering the fields.
                        Specifically, this are currently used in calls of
                        `EntityFinder` for building filtered lists of entities
                        used to populate enumerated field values.  Fields in
                        the supplied context currently used are `entity` for the
                        entity value being rendered, and `view` for the view record
                        used to render that value
                        (cf. GenericEntityEditView.get_view_entityvaluemap)

        The form rendering template iterates over the field descriptions to be
        added to the form display.  The constructor for this object appends the 
        current field to a list of field value mappings, with a `map_entity_to_context`
        method that assigns a list of values from the supplied entity to a context 
        field named by parameter `c`.
        """
        self.c      = c         # Context field name for values mapped from entity
        self.fd     = []        # List of field descriptions
        self.fm     = []        # List of field value maps
        properties  = None      # Used to detect and disambiguate duplicate properties
        position    = LayoutOptions(s=0, m=0, l=0)
        for f in fields:
            # Add field descriptor for field presentation
            log.debug("FieldListValueMap: field %r"%(f,))
            field_desc = field_description_from_view_field(coll, f, view_context)
            properties = field_desc.resolve_duplicates(properties)
            self.fd.append(field_desc)
            # Add padding to field value map list
            position, pad1_desc, pad2_desc = get_padding_desc(position, field_desc)
            if pad1_desc:
                self.fm.append(FieldValueMap(c='_fieldlistvaluemap_', f=pad1_desc))
            if pad2_desc:
                self.fm.append(FieldValueMap(c='_fieldlistvaluemap_', f=pad2_desc))
            # Add field value mapper to field value map list
            if field_desc.is_repeat_group():
                repeatfieldsmap = FieldListValueMap('_unused_fieldlistvaluemap_', 
                    coll, field_desc.group_view_fields(), view_context
                    )
                repeatvaluesmap = RepeatValuesMap(c='_fieldlistvaluemap_',
                    f=field_desc, fieldlist=repeatfieldsmap
                    )
                self.fm.append(repeatvaluesmap)
            else:
                self.fm.append(FieldValueMap(c='_fieldlistvaluemap_', f=field_desc))
        return

    def __repr__(self):
        return (
            "FieldListValueMap.fm: %r\n"%(self.fm)
            )

    def map_entity_to_context(self, entityvals, context_extra_values=None):
        listcontext = []
        for f in self.fm:
            fv = f.map_entity_to_context(entityvals, context_extra_values=context_extra_values)
            listcontext.append(fv['_fieldlistvaluemap_'])
        return { self.c: listcontext }

    def map_form_to_entity(self, formvals, entityvals):
        """
        Use form data to update supplied entity values
        """
        for f in self.fm:
            f.map_form_to_entity(formvals, entityvals)
        return entityvals

    def map_form_to_entity_repeated_items(self, formvals, entityvals, prefix):
        """
        Extra helper method used when mapping a repeated list of fields items to 
        repeated entity values.  Returns values corresponding to a single repeated 
        set of fields.  The field names extracted are constructed using the supplied 
        prefix string.

        Returns a dictionary of repeated field values found using the supplied prefix.
        """
        for f in self.fm:
            f.map_form_to_entity_repeated_item(formvals, entityvals, prefix)
        return entityvals

    def get_structure_description(self):
        """
        Helper function returns list of field description information
        """
        return (
            { 'field_type':     'FieldListValueMap'
            , 'field_list':     self.fd 
            })

    def get_field_description(self):
        return None

# End.
