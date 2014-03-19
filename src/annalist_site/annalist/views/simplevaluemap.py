"""
Annalist class for processing a SimpleValueMap in an annalist view value mapping table.

A SimpleValueMap maps values directly from a supplied entity value to the indicated field
in the context, and also from the form values returned to an entity value, or another context
for re-rendering.  The entity and form fields used are build directly into the mapping table.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import collections

from annalist.fields.render_utils   import bound_field

# Named tuple is base class for SimpleValueMap:

_SimpleValueMap_tuple = collections.namedtuple("SimpleValueMap", ("c", "e", "f"))

class SimpleValueMap(_SimpleValueMap_tuple):
    """
    Define an entry in an entity value mapping table corresponding to a
    simple value that can be mapped from an incoming entity to a request
    context, and from form response data to a request context or to a
    resulting entity value.

    c       request context field name (also keys default values)
    e       entity value field name (property URI)
    f       HTML input form field name (used as key in POST results)
    """

    def _map_to_context(self, context, vals, valkey, defaults=None):
        if self.c:
            context[self.c] = vals.get(valkey, 
                defaults and defaults.get(self.c, None)
                )
        return

    def map_entity_to_context(self, context, entityvals, defaults=None):
        self._map_to_context(context, entityvals, self.e, defaults)
        return

    def map_form_to_context(self, context, formvals, defaults=None):
        self._map_to_context(context, formvals, self.f, defaults)
        return

    def map_form_to_entity(self, entityvals, formvals):
        if self.e and self.f:
            log.debug("SimpleValueMap.map_form_to_entity %s, %s, %r"%(self.e, self.f, formvals))
            v = formvals.get(self.f, None)
            if v:
                entityvals[self.e] = v
            # entityvals[self.e] = formvals.get(self.f, None)
        return


class StableValueMap(SimpleValueMap):
    """
    Like SimpleValueMap, except that no value is returned from the 
    form to the entity.  (Some fields are handled specially.)
    """

    def map_form_to_entity(self, entityvals, formvals):
        return

# End.