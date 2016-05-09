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
from annalist.views.form_utils.fieldrowvaluemap import FieldRowValueMap
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

    pos_prev    Position following previous field
    offset      Offset of next field
    width       Width of next field 
    display     True if next field is to be displayed, otherwise False.

    Returns a tuple containing::
    [0] True if next field is to be placed on next row
    [1] Amount of padding (0..11) to be added from end of last field or start of row
    [2] Position of next free space after new element
    """
    if not display:
        # Field not to be displayed
        return (False, 0, pos_prev)
    if (offset < pos_prev) or (offset+width > 12):
        # Force to next row
        next_row = True
        padding  = offset
    else:
        # Same row
        next_row = False
        padding  = offset - pos_prev
    pos_next = offset + width
    return (next_row, padding, pos_next)

def get_padding_desc(position, field_desc):
    """
    Calculate padding required to position field where requested, and return:
    [0] next row indicator: True if the field and padding are to be placed 
        on a new row.
    [1] padding field descriptor, or None
    [2] updated position vector

    NOTE: the field is forced onto a new row if it does not fit on the same row 
    for a large display.  For smaller displays, fields that run off the end of 
    a row are positioned by the browser.  Position information is maintained
    separately for all display sizes so that size-dependent padding can be 
    calculated.

    position    is the position immediately following the preceeding field.
    field_desc  is the next field descriptor to be addedc to the display.
    """
    placement = field_desc['field_placement']
    # log.info(
    #     "@@ get_padding_desc: prev %r, next %r, width %r"%
    #     (position, placement.offset, placement.width)
    #     )
    next_rows, pad_s, next_s = next_field(position.s, placement.offset.s, placement.width.s, placement.display.s)
    next_rowm, pad_m, next_m = next_field(position.m, placement.offset.m, placement.width.m, placement.display.m)
    next_rowl, pad_l, next_l = next_field(position.l, placement.offset.l, placement.width.l, placement.display.l)
    pos_next = LayoutOptions(s=next_s, m=next_m, l=next_l)
    pad_desc = get_padding_field_desc(pad_s, pad_m, pad_l)
    # log.info(
    #     "@@ get_padding_desc: next_row %r, pad_desc %r, pos_next %r"%
    #     (next_rowl, LayoutOptions(s=pad_s, m=pad_m, l=pad_l), pos_next)
    #     )
    return (next_rowl, pad_desc, pos_next)

#   ----------------------------------------------------------------------------
#
#   Support class for generating row data
#
#   ----------------------------------------------------------------------------

class RowData(object):

    def __init__(self, coll, view_context):
        self._coll   = coll
        self._view   = view_context
        self._pos    = LayoutOptions(s=0, m=0, l=0)
        self._fields = []
        return

    def next_field(self, field_desc, map_field_row):
        next_row, pad_desc, pos_next = get_padding_desc(self._pos, field_desc)
        if next_row:
            self.flush(map_field_row)
        if pad_desc:
            self._fields.append(pad_desc)
        self._fields.append(field_desc)
        self._pos = pos_next
        return

    def flush(self, map_field_row):
        if self._fields:
            # Context name: cf. FieldListValueMap.map_entity_to_context
            row_values_map  = FieldRowValueMap("_fieldlistvaluemap_", self._coll, self._fields, self._view)
            map_field_row.append(row_values_map)
        self._pos    = LayoutOptions(s=0, m=0, l=0)
        self._fields = []
        return

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
        rowdata     = RowData(coll, view_context)
        for f in fields:
            # Add field descriptor for field presentation
            # log.debug("FieldListValueMap: field %r"%(f,))
            field_desc = field_description_from_view_field(coll, f, view_context)
            properties = field_desc.resolve_duplicates(properties)
            self.fd.append(field_desc)

            # Add field value mapper to field value map list
            if field_desc.is_repeat_group():
                # Repeat group occupies new row
                rowdata.flush(self.fm)
                repeatfieldsmap = FieldListValueMap('_repeatfieldsmap_', 
                    coll, field_desc.group_view_fields(), view_context
                    )
                # Context name: cf. FieldListValueMap.map_entity_to_context
                repeatvaluesmap = RepeatValuesMap(c='_fieldlistvaluemap_',
                    f=field_desc, fieldlist=repeatfieldsmap
                    )
                self.fm.append(repeatvaluesmap)
            else:
                # Single field: try to fit on current row
                rowdata.next_field(field_desc, self.fm)
        # Flush out any remaining fields
        rowdata.flush(self.fm)
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

    def map_form_to_entity_repeated_item(self, formvals, entityvals, prefix):
        """
        Extra helper method used when mapping a repeated list of fields items to 
        repeated entity values.  Returns values corresponding to a single repeated 
        set of fields.  The field names extracted are constructed using the supplied 
        prefix string.

        Returns a dictionary of repeated field values found using the supplied prefix.
        (which evaluates as False if fields using the supplied prefix are not found)
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
