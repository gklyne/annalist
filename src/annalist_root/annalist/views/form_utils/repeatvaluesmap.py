"""
Annalist class for processing a RepeatValuesMap in an annalist view value mapping table.

A RepeatValuesMap is used to render repeated groups of fields for each of 
a list of values.

When the mapping function `map_entity_to_context` is called, the supplied `entityvals` 
is expected to be an iterator (list, tuple, etc.) of entities or dictionary values 
to be processed for display.

When decoding values from a form, different logic is required to extract a
repeating structure from the flat namespace used for form data.  See method 
`map_form_to_entity`, along with `FieldListValueMap.map_form_to_entity_repeated_items` 
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
        # @@TODO: use field_name (self.i) for prefix?
        prefix_template = self.f['group_id']+"__%d__"
        prefix_n        = 0
        repeatvals      = []
        prefix_found    = True
        while prefix_found:
            vals          = {}
            prefix        = prefix_template%prefix_n
            prefix_found  = self.fieldlist.map_form_to_entity_repeated_items(formvals, vals, prefix)
            if prefix_found:
                repeatvals.append(vals)
            prefix_n += 1
        entityvals[self.e] = repeatvals
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
