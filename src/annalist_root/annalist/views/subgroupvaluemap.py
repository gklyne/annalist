"""
Annalist class for "lifting" a value mapping to a new mapping that is the same as the
original mapping but which is returned as a named subfield of the returned dictionary
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import collections

from django.conf                        import settings

class SubgroupValueMap(object):
    """
    View value mapping class that returns the values froma  supplied value mapping
    object, but in a specified context sub-field.

    valuemap    is an existing value map used to construct values returned.
    c           is a context sub-field in which mapped values are returned.

    (Sub-fields for entity return values could be defined, but as yet no need has been identified.)
    """

    def __init__(self, valuemap, c=None):
        self.valuemap = valuemap
        self.c        = c
        return

    def __repr__(self):
        return "FieldListValueMap(c=%s, %r)"%(self.c, self.valuemap)

    def map_entity_to_context(self, entityvals, extras=None):
        return { self.c: self.valuemap.map_entity_to_context(entityvals, extras=extras) }

    def map_form_to_entity(self, formvals):
        return self.valuemap.map_form_to_entity(formvals)

    def map_form_to_entity_repeated_items(self, formvals, prefix):
        return self.map_form_to_entity_repeated_items(formvals, prefix)
