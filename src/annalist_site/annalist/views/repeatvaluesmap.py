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

# from annalist.fields.render_utils   import bound_field

class RepeatValuesMap(object):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple values in an entity.  

    repeat  is a `RepeatDescription` value describing the repeated data.
    fields  a `FieldListValueMap` object describing a set of fields to be 
            displayed for each repeated value.
    """

    def __init__(self, c=None, repeat=None, fields=None):
        self.e = repeat["repeat_entity_values"]
        self.c = c
        self.r = repeat
        self.f = fields
        return

    def __repr__(self):
        return (
            "RepeatValuesMap.c: %s\n"%(self.c)+
            "RepeatValuesMap.e: %r\n"%(self.e)+
            "RepeatValuesMap.r: %r\n"%(self.r)+
            "RepeatValuesMap.f: %r\n"%(self.f)
            )

    def map_entity_to_context(self, entityval, extras=None):
        """
        Return a context dictionary for mapping entity list values to repeated
        field descriptions in a displayed form.
        """
        subcontext = {}
        repeatextras = extras.copy().update(self.r)
        # log.info("RepeatValuesMap.map_entity_to_context, self.e: %s, entityval %r, entityval[self.e]: %r"%(self.e, entityval, entityval.get(self.e, None)))
        repeatcontext = []
        if self.e in entityval:
            for repeatedval in entityval[self.e]:
                # log.info("RepeatValuesMap.map_entity_to_context: repeatedval %r"%repeatedval)
                fieldscontext = self.f.map_entity_to_context(repeatedval, extras=repeatextras)
                # log.info("RepeatValuesMap.map_entity_to_context: fieldscontext %r"%fieldscontext)
                repeatcontext.append(fieldscontext)
        repeatcontextkey = self.r['repeat_context_values']
        subcontext[self.c] = (
            { 'repeat_id':              self.r['repeat_id']
            , 'repeat_label':           self.r['repeat_label']
            , 'repeat_btn_label':       self.r['repeat_btn_label']
            , 'repeat_context_values':  repeatcontextkey
            , repeatcontextkey:         repeatcontext
            })
        # log.info("subcontext: %r"%(subcontext))
        return subcontext

    def map_form_to_entity(self, formvals):
        # log.info(repr(formvals))
        prefix_template = self.r['repeat_id']+"__%d__"
        prefix_n        = 0
        repeatvals      = []
        while True:
            vals = self.f.map_form_to_entity_repeated_items(formvals, prefix_template%prefix_n)
            if vals is None:
                break
            repeatvals.append(vals)
            prefix_n += 1
        return {self.e: repeatvals}

# End.