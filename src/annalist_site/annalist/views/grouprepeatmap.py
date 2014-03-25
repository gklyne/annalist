"""
Annalist class for processing a GroupRepeatMap in an annalist view value mapping table.

A GroupRepeatMap is used to render repeated groups of fields (e.g. a list or grid) for 
each one of a list of entities.  When the mapping function `map_entity_to_context` is called,
the supplied `entityvals` is expected to be an iterator (list, tuple, etc.) of entities or
dictionry values.

The present implementation does not support mapping from form data (for re-rendering) or
returning values from a form to update entities.  As yet, no mechanism is adopted for
representing repeated groups of fields in a form.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import collections

from annalist.fields.render_utils   import bound_field

# Named tuple is base class for GroupRepeatMap:

_GroupRepeatMap_tuple = collections.namedtuple("GroupRepeatMap", ("c", "e", "g"))

class GroupRepeatMap(_GroupRepeatMap_tuple):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple entities.  

    c       request context field name for the repeated groups.
    e       name of entity value field containig list of entities  
    g       a group of field descriptions to be repeated for each provided entity.
            The value supplied is in the form of an entity value map, and the named
            context field is populated with a list of "sub-context" values, each of
            which corresponds to a supplied entity or repeated value.
    """

    # def __new__(cls, *args, **kwargs):
    #     self = super(GroupRepeatMap, cls).__new__(cls, *args, **kwargs)
    #     return self

    def map_entity_to_context(self, context, entityval, extras=None):
        if self.c:
            if self.c not in context:
                context[self.c] = []
            for entity in entityval[self.e]:
                grp_context = { 'entity_id': entity.get_id() }
                for kmap in self.g:
                    kmap.map_entity_to_context(grp_context, entity, extras=extras)
                context[self.c].append(grp_context)
        return

    def map_form_to_context(self, context, formvals, extras=None):
        log.warn("GroupRepeatMap.map_form_to_context not supported")
        return

    def map_form_to_entity(self, entityvals, formvals):
        log.warn("GroupRepeatMap.map_form_to_entity not supported")
        return

# End.