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

import collections

from annalist.fields.render_utils   import bound_field

# Named tuple is base class for RepeatValuesMap:

_RepeatValuesMap_tuple = collections.namedtuple("RepeatValuesMap", ("c", "e", "r", "f"))

class RepeatValuesMap(_RepeatValuesMap_tuple):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple values in an entity.  

    c       request context field name for the repeated groups.
    e       is the name of the entity field containing a list values for which the
            field group is iterated.
    r       a group of field descriptions to be repeated for each provided set of values.
            The value supplied is in the form of an entity value map, and the named
            context field is populated with a list of "sub-context" values, each of
            which corresponds to a supplied entity or repeated value.
    f       is a dictionary of additional values that are used in generating form values
            related to te repeated fields.
    """

    def map_entity_to_context(self, context, entityvals, extras=None):
        if self.c:
            if self.c not in context:
                context[self.c] = []
            for entity in entityvals:
                grp_context = { 'entity_id': entity.get_id(), 'type_id': entity.get_type_id() }
                for kmap in self.g:
                    kmap.map_entity_to_context(grp_context, entity, extras=extras)
                context[self.c].append(grp_context)
        return

    def map_form_to_context(self, context, formvals, extras=None):
        log.warn("RepeatValuesMap.map_form_to_context not supported")
        return

    def map_form_to_entity(self, entityvals, formvals):
        log.warn("RepeatValuesMap.map_form_to_entity not supported")
        return

# End.