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

import json

from annalist.identifiers               import RDFS, ANNAL

from annalist.views.fields.bound_field  import bound_field

class RepeatValuesMap(object):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple values in an entity.  

    c       request context field name for the field value mapping entry
    repeat  is a `FieldDescription` value describing the repeated data.
    fields  a `FieldListValueMap` object describing a set of fields to be 
            displayed for each repeated value.
    """

    def __init__(self, c=None, repeat=None, fields=None):
        self.c = c
        self.r = repeat
        self.f = fields
        self.e = repeat["field_property_uri"]
        return

    def __repr__(self):
        return (
            "RepeatValuesMap.r: %r\n"%(self.r)+
            "RepeatValuesMap.f: %r\n"%(self.f)
            )

    def map_entity_to_context(self, entityvals, extras=None):
        """
        Returns a bound_field, which is a dictionary-like of values to be added 
        to the display context under construction
        """
        # @@TODO: repeats FieldValueMap - make subclass?
        # log.info("*** map entity %s to context %s, vals %r"%(self.e, self.f, entityvals))
        # log.info("map_entity_to_context: bound_field: extras %r"%(extras,))
        boundfield = bound_field(
            field_description=self.r, 
            entityvals=entityvals,
            extras=extras
            )
        return { self.c: boundfield }

    def map_form_to_entity(self, formvals):
        # log.info(repr(formvals))
        prefix_template = self.r['group_id']+"__%d__"
        prefix_n        = 0
        repeatvals      = []
        while True:
            prefix = prefix_template%prefix_n
            rvals = self.f.map_form_to_entity_repeated_items(formvals, prefix)
            if rvals:
                repeatvals.append(rvals)
            else:
                break
            prefix_n += 1
        return {self.e: repeatvals}

    def get_structure_description(self):
        """
        Helper function returns structure description information
        """
        return (
            { 'field_type':    "RepeatValuesMap"
            , 'field_descr':   self.r
            })

    def get_field_description(self):
        return self.r

# End.
