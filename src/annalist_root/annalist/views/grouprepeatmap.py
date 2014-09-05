"""
Annalist class for processing a GroupRepeatMap in an annalist view value mapping table.

A GroupRepeatMap is used to render repeated groups of fields (e.g. a list or grid) for 
each one of a list of entities.  When the mapping function `map_entity_to_context` is called,
the supplied `entityval` is expected to contain a field, nanmed by the 'e' parameter to the
constructor, that is an iterator (list, tuple, etc.) of entities or dictionary values that 
are to be processed for display.

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

from annalist.views.fields.bound_field  import bound_field

# Named tuple is base class for GroupRepeatMap:

_GroupRepeatMap_tuple = collections.namedtuple("GroupRepeatMap", ("c", "e", "g"))

class GroupRepeatMap(_GroupRepeatMap_tuple):
    """
    Define an entry in an entity value mapping table corresponding to a
    group of fields that is repeated for multiple entities.  

    c       request context field name for the repeated groups.
    e       name of entity value field containing list of entities  
    g       a group of field descriptions to be repeated for each provided entity.
            The value supplied is in the form of an entity value map, and the named
            context field is populated with a list of "sub-context" values, each of
            which corresponds to a supplied entity or repeated value.
    """

    # def __new__(cls, *args, **kwargs):
    #     self = super(GroupRepeatMap, cls).__new__(cls, *args, **kwargs)
    #     return self

    def map_entity_to_context(self, entityval, extras=None):
        subcontext = {}
        if self.c:
            subcontext[self.c] = []
            for v in entityval[self.e]:
                grp_context = { 'entity_id': v['entity_id'], 'type_id': v['entity_type_id'] }
                for kmap in self.g:
                    grp_context.update(kmap.map_entity_to_context(v, extras=extras))
                subcontext[self.c].append(grp_context)
        return subcontext

    def map_form_to_context(self, formvals, extras=None):
        log.warn("GroupRepeatMap.map_form_to_context not supported")
        return {}

    def map_form_to_entity(self, formvals):
        log.warn("GroupRepeatMap.map_form_to_entity not supported")
        return {}

    def get_structure_description(self):
        return (
            { 'field_type':     'GroupRepeatMap'
            , 'entity_field':   self.e
            , 'context_field':  self.c
            , 'group_fields':   self.g.get_structure_description()
            })

# End.