"""
This module contains (and isolates) logic used to find entities based on entity type,
list selection criteria and search terms.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re

from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitytypeinfo import EntityTypeInfo

class EntityFinder(object):
    """
    Logic for enumerting entities matching a supplied type, selector and/or search string.
    """

    def __init__(self, coll):
        super(EntityFinder, self).__init__()
        self._coll = coll
        self._site = coll.get_site()
        return

    def get_entities(self, type_id=None, selector=None, search=None):
        for e in self.get_selected_entities(type_id=type_id, selector=selector):
            if self.entity_contains(e, search):
                yield e
        return

    def get_selected_entities(self, type_id=None, selector=None):
        if selector:
            s = self.compile_selector(type_id, selector)
            if s:
                for e in s:
                    yield e
        else:
            for e in self.get_base_entities(type_id):
                yield e
        return

    def get_base_entities(self, type_id=None):
        if type_id:
            # return all entities in collection of a specific type (includes built-ins)
            entitytypeinfo = EntityTypeInfo(self._site, self._coll, type_id)
            for e in entitytypeinfo.entityparent.child_entities(
                    entitytypeinfo.entityclass, 
                    altparent=entitytypeinfo.entityaltparent):
                yield e
        else:
            # Return all entitities in collection (not including built-in types)
            for f in self._coll._children(RecordTypeData):
                t = RecordTypeData.load(self._coll, f)
                if t:
                    for e in t.entities():
                        yield e

    def compile_selector(self, type_id, selector):
        """
        Return iterator for entities matching supplied selector.
        """
        ff = self.compile_selector_filter(selector)
        # Test all entitities in collection (not including built-in types)
        for e in self.get_base_entities(type_id):
            if ff(e): yield e
        return

    @classmethod
    def compile_selector_filter(cls, selector):
        """
        Return filter for for testing entities matching a supplied selector.

        Selector formats:
            (blank)                     match any entity
            @annal:type==annal:Field    entity type is indicated value
            @<field>==<value>           entity named field is indicated value

        >>> e  = { 'p:a': '1', 'p:b': '2', 'p:c': '3' }
        >>> f1 = "@p:a==1"
        >>> f2 = "@p:a==2"
        >>> f3 = ''
        >>> EntityFinder.compile_selector_filter(f1)(e)
        True
        >>> EntityFinder.compile_selector_filter(f2)(e)
        False
        >>> EntityFinder.compile_selector_filter(f3)(e)
        True
        """
        def match_any(e):
            return True
        def match_field(field_name, field_val):
            def match_field_f(e):
                return e[field_name] == field_val
            return match_field_f
        if selector == "":
            return match_any
        sm = re.match(r'@((\w|:)+)==((\w|:)+)$', selector)
        if sm:
            return match_field(sm.group(1), sm.group(3))
        # Drop through: raise error
        raise ValueError("Unrecognized entity selector (%s)"%selector)

    @classmethod
    def entity_contains(cls, e, search):
        """
        Returns True if entity contains/matches search term, else False.
        Search term None (or blank) matches all entities.

        >>> e  = { 'p:a': '1', 'p:b': '2', 'p:c': '3' }
        >>> EntityFinder.entity_contains(e, "1")
        True
        >>> EntityFinder.entity_contains(e, "3")
        True
        >>> EntityFinder.entity_contains(e, "nothere")
        False
        """
        if search:
            for key in e:
                val = e[key]
                if isinstance(val, (str, unicode)):
                    if search in val:
                        return True
            return False
        return True

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
