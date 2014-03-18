"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import collections

from annalist.fields.render_utils   import bound_field


# Named tuple is base class for SimpleValueMap:

_FieldValueMap_tuple = collections.namedtuple("FieldValueMap", ("c", "f"))

class FieldValueMap(_FieldValueMap_tuple):
    """
    Define an entry in an entity value mapping table corresponding to a
    field value and descriuption, which is added to a list of such fields
    in the indicated context variable.

    c       request context field name for a list of fields
    fd      field description structure (cf. `get_field_context` below)
    """

    def __new__(cls, *args, **kwargs):
        self = super(FieldValueMap, cls).__new__(cls, *args, **kwargs)
        self.e = self.f['field_property_uri']
        self.i = self.f['field_id']
        return self

    def _map_to_context(self, context, vals, valkey, defaults=None):
        if self.c:
            if self.c not in context:
                context[self.c] = []
            boundfield = bound_field(
                field_description=self.f, 
                entity=vals, key=valkey
                )
            context[self.c].append(boundfield)
        return

    def map_entity_to_context(self, context, entityvals, defaults=None):
        self._map_to_context(context, entityvals, self.e, defaults)
        return

    def map_form_to_context(self, context, formvals, defaults=None):
        self._map_to_context(context, formvals, self.i, defaults)

    def map_form_to_entity(self, entityvals, formvals):
        if self.e:
            log.debug("FieldValueMap.map_form_to_entity %s, %r"%(self.e, formvals))
            v = formvals.get(self.i, None)
            if v:
                entityvals[self.e] = v
        return

# End.