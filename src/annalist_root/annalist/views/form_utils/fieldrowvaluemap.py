"""
Annalist class for processing a row of field mappings for conversion between
entity values context values and form data.

A FieldRowValueMap is an object that can be inserted into an entity view value
mapping table to process the corresponding list of fields.  It functions like a 
simplified form of FieldListValueMap, except that each row is wrapped in a 
"<div class='row'>...</div>", etc., to force a new row of displayed output.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import collections

from django.conf                        import settings

from annalist.identifiers               import RDFS, ANNAL

from annalist.views.form_utils.fielddescription import FieldDescription, field_description_from_view_field
from annalist.views.form_utils.fieldvaluemap    import FieldValueMap
from annalist.views.fields.bound_field          import bound_field

# from annalist.views.form_utils.repeatvaluesmap  import RepeatValuesMap
# from annalist.views.fields.render_placement     import (
#     Placement, LayoutOptions,
#     make_field_width, make_field_offset, make_field_display,
#     )

#@@
# #   ----------------------------------------------------------------------------
# #
# #   FieldRowValueMap field description data
# #
# #   ----------------------------------------------------------------------------

# row_field_data = (
#     { "annal:id":                   "Field_row"
#     , "rdfs:label":                 ""
#     , "annal:field_render_type":    "FieldRow"
#     , "annal:field_value_mode":     "Value_direct"
#     })

# row_placement = Placement(
#         width=make_field_width(sw=12, mw=12, lw=12),
#         offset=make_field_offset(so=0, mo=0, lo=0),
#         display=make_field_display(sd=True, md=True, ld=True),
#         field="small-12 columns",
#         label="small-4 columns",
#         value="small-8 columns"
#         )
#@@

#   ----------------------------------------------------------------------------
#
#   FieldRowValueMap class
#
#   ----------------------------------------------------------------------------

class FieldRowValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.
    """

    def __init__(self, c, coll, field_descs, view_context):
        """
        Define an entry to be added to an entity view value mapping table,
        corresponding to a list of field descriptions.

        c               name of field used for this value in display context
        coll            is a collection from which data is being rendered.
        field_descs     list of field descriptions from a view definition, each
                        of which is a dictionary with the field description from 
                        a view or list description.
        view_context    is a dictionary of additional values that may be used in
                        assembling values to be used when rendering the fields.

        The form rendering template iterates over the field descriptions to be
        added to the form display.  The constructor for this object appends the 
        current field to a list of field value mappings, with a `map_entity_to_context`
        method that assigns a list of values from the supplied entity to a context 
        field named by parameter `c`.
        """
        self.c     = c              # Context field name for row values
        self.fd    = field_descs    # Field descriptors for fields in row
        self.fm    = []             # Field maps for fields in row
        for field_desc in field_descs:
            # Add field value mapper to field value map list
            self.fm.append(FieldValueMap(c='_fieldrowvaluemap_', f=field_desc))
        fieldrow_data = (
            { ANNAL.CURIE.id:                   "Row_fields"
            , RDFS.CURIE.label:                 "Fields in row"
            , RDFS.CURIE.comment:               "@@@ Field description for row of fields @@@"
            , ANNAL.CURIE.field_name:           "Row_fields"
            , ANNAL.CURIE.field_render_type:    "FieldRow"
            , ANNAL.CURIE.field_value_mode:     "Value_direct"
            })
        self.rd = FieldDescription(
            coll, fieldrow_data,
            view_context=view_context
            )
        # @@TODO: Review this: consider passing in bare field descriptions from view, and
        #         adapting or using a variant of field_description_from_view_field to populate 
        #         'row_field_descs' in field cescription.  This would be more in line with
        #         treatment of ref_multifield fields.
        self.rd['row_field_descs'] = self.fd
        return

    def __repr__(self):
        return (
            "FieldRowValueMap.fd: %r\n"%(self.fd)
            )

    def map_entity_to_context(self, entityvals, context_extra_values=None):
        """
        Add row of fields to display context.

        The context returned uses a single field with a special renderer that 
        handles expansion of contained fields, wrapped ibn markup that presents 
        the data as a new row.
        """
        rowcontext = bound_field(
            self.rd, entityvals, 
            context_extra_values=context_extra_values
            )
        return { self.c: rowcontext }

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

        Returns a dictionary of repeated field values found using the supplied prefix
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
            { 'field_type':     'FieldRowValueMap'
            , 'field_list':     self.fd 
            })

    def get_field_description(self):
        return None

# End.
