"""
Annalist class for processing a RepeatValuesMap in an annalist view value mapping table.

A RepeatValuesMap is used to render repeated groups of fields for each one of a list of 
sets of values.

When the mapping function `map_entity_to_context` is called, the supplied `entityvals` 
is expected to be an iterator (list, tuple, etc.) of entities or dictionry values to be 
processed for display.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import json

class RepeatValuesMap(object):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple values in an entity.  

    repeat  is a `RepeatDescription` value describing the repeated data.
    fields  a `FieldListValueMap` object describing a set of fields to be 
            displayed for each repeated value.
    """

    def __init__(self, c=None, repeat=None, fields=None):
        self.r = repeat
        self.f = fields
        self.e = repeat["repeat_entity_values"]
        return

    def __repr__(self):
        return (
            "RepeatValuesMap.e: %r\n"%(self.e)+
            "RepeatValuesMap.r: %r\n"%(self.r)+
            "RepeatValuesMap.f: %r\n"%(self.f)
            )

    def map_entity_to_context(self, entityval, extras=None):
        """
        Return a context dictionary for mapping entity list values to repeated
        field descriptions in a displayed form.
        """
        repeatextras = extras.copy().update(self.r)
        # log.info("RepeatValuesMap.map_entity_to_context, self.e: %s, entityval %r, entityval[self.e]: %r"%(self.e, entityval, entityval.get(self.e, None)))
        rcv = []
        if self.e in entityval:
            # Iterate over repeated values in entity data:
            #
            # There is a special case for `RecordView_view` data, where the data is both
            # view description and data to be displayed.  The field list iterator 
            # (`FieldListValueMap`) iterates over the value as view description, and
            # needs information about the repeated field structure, distinguished by 
            # an `annal:repeat_id` value, but the data value iterator here generates a
            # list of fields to be actually displayed as a repeated value, and simply
            # preserves the repeated field data so that it can be included in an updated
            # entity record.
            #
            # E.g. repeated field data for the entity edit view looks like this:
            #
            # , { "annal:repeat_id":              "View_fields"
            #   , "annal:repeat_label_add":       "Add field"
            #   , "annal:repeat_label_delete":    "Remove selected field(s)"
            #   , "annal:repeat_entity_values":   "annal:view_fields"
            #   , "annal:repeat_context_values":  "repeat"
            #   , "annal:repeat":
            #     [ { "annal:field_id":               "Field_sel"
            #       , "annal:field_placement":        "small:0,12; medium:0,6"
            #       }
            #     , { "annal:field_id":               "Field_placement"
            #       , "annal:field_placement":        "small:0,12; medium:6,6"
            #       }
            #     ]
            #   }
            repeat_index  = 0
            for repeatedval in entityval[self.e]:
                if "annal:repeat_id" not in repeatedval:    # special case test
                    # log.info("RepeatValuesMap.map_entity_to_context: repeatedval %r"%repeatedval)
                    fieldscontext = self.f.map_entity_to_context(repeatedval, extras=repeatextras)
                    # log.info("RepeatValuesMap.map_entity_to_context: fieldscontext %r"%fieldscontext)
                else:
                    fieldscontext = self.map_repeat_field_data_to_context(repeatedval)
                fieldscontext['repeat_id']     = self.r['repeat_id']
                fieldscontext['repeat_index']  = repeat_index
                fieldscontext['repeat_prefix'] = self.r['repeat_id']+("__%d__"%repeat_index)
                rcv.append(fieldscontext)
                repeat_index += 1
        repeatcontext    = self.get_structure_description()
        repeatcontextkey = repeatcontext['repeat_context_values']
        repeatcontext[repeatcontextkey] = rcv
        return repeatcontext

    def map_form_to_entity(self, formvals):
        # log.info(repr(formvals))
        prefix_template = self.r['repeat_id']+"__%d__"
        prefix_n        = 0
        repeatvals      = []
        while True:
            prefix = prefix_template%prefix_n
            vals = (
                self.map_form_to_repeat_field_data(formvals, prefix)
                or
                self.f.map_form_to_entity_repeated_items(formvals, prefix)
                )
            if vals is None:
                break
            repeatvals.append(vals)
            prefix_n += 1
        return {self.e: repeatvals}

    def map_repeat_field_data_to_context(self, repeatedval):
        return (
            { 'repeat_fields_data': json.dumps(repeatedval)
            })

    def map_form_to_repeat_field_data(self, formvals, prefix):
        # Generate repeated field description as above, per map_repeat_data_to_context
        v = formvals.get(prefix+"repeat_fields_data", None)
        if v:
            v = json.loads(v)
        return v

    def get_structure_description(self):
        """
        Helper function returns structure description information
        """
        rd = self.r.get_structure_description()
        rd['field_type']                = "RepeatValuesMap"
        rd['repeat_fields_description'] = self.f.get_structure_description()
        return rd

# End.
