"""
Annalist class for processing a RepeatValuesMap in an annalist view value mapping table.

A RepeatValuesMap is used to render repeated groups of fields for each of 
a list of values.

When the mapping function `map_entity_to_context` is called, the supplied `entityvals` 
is expected to be an iterator (list, tuple, etc.) of entities or dictionary values 
to be processed for display.

When decoding values from a form, different logic is required to extract a
repeating structure from the flat namespace used for form data.  See method 
`map_form_to_entity`, along with `FieldListValueMap.map_form_to_entity_repeated_item` 
for more details. 
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import json

from annalist.identifiers               import RDFS, ANNAL

from annalist.views.form_utils.fieldvaluemap    import FieldValueMap
from annalist.views.fields.bound_field          import bound_field

class RepeatValuesMap(FieldValueMap):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple values in an entity.  

    c           request context field name for the field value mapping entry
    f           is a `FieldDescription` value describing the repeated data.
    fieldlist   a `FieldListValueMap` object describing a set of fields to be 
                displayed for each repeated value.
    """

    def __init__(self, c=None, f=None, fieldlist=None):
        super(RepeatValuesMap, self).__init__(c=c, f=f)
        self.fieldlist = fieldlist
        return

    def __repr__(self):
        return (
            super(RepeatValuesMap, self).__repr__()+
            "RepeatValuesMap.fieldlist: %r\n"%(self.fieldlist)
            )

    def map_form_to_entity(self, formvals, entityvals):
        # log.info(repr(formvals))
        prefix_template  = self.i+"__%d__"
        prefix_n         = 0
        repeat_vals      = []
        field_key        = self.f.get_field_value_key(entityvals)
        previous_vals    = entityvals.get(field_key,[])
        while True:
            #@@ 
            #   The following logic works, but sometimes yields unexpected results:
            #   Specifically, when the original data has more fields than the form,
            #   the additional old fields were copied over into the result.
            #
            #   For now, we live with the restriction that fields within repeated 
            #   fields cannot propagate subproperty values used; i.e. when editing, 
            #   subproperties used in the data are replaced by the superproeprty from
            #   the repeated field definition.  In practice, this may not be a problem,
            #   as the cases of repeated fields with subproperties are generally associated
            #   with special JSON-LD keys like '@id' or '@value'
            #
            # Extract previous values in same position to be updated
            # This ad-hocery is used to try and preserve property URIs used 
            # within the list, so that subproperties (where used) are preserved.
            # if len(previous_vals) > prefix_n:
            #     vals     = previous_vals[prefix_n]
            # else:
            #     vals     = {}
            #@@
            vals         = {}
            prefix       = prefix_template%prefix_n
            updated_vals = self.fieldlist.map_form_to_entity_repeated_item(formvals, vals, prefix)
            if not updated_vals:
                break
            repeat_vals.append(updated_vals)
            prefix_n += 1
        entityvals[field_key] = repeat_vals
        return entityvals

    def get_structure_description(self):
        """
        Helper function returns structure description information
        """
        return (
            { 'field_type':     "RepeatValuesMap"
            , 'field_descr':    self.f
            , 'entity_field':   self.e
            , 'form_field':     self.i
            })

# End.
