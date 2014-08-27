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
from annalist.models.entitytypeinfo import EntityTypeInfo, get_built_in_type_ids

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
            for e in entitytypeinfo.enum_entities(usealtparent=True):
                yield e
        else:
            # Return all entitities in collection (not including site built-ins)
            for t in self.get_collection_type_ids():
                entitytypeinfo = EntityTypeInfo(self._site, self._coll, t)
                for e in entitytypeinfo.enum_entities(usealtparent=False):
                    yield e
        return

    def get_collection_type_ids(self):
        """
        Returns iterator over possible type ids in current collection.

        Each type is returned as an EntityTypeInfo object.
        """
        for t in get_built_in_type_ids():
            yield t
        for t in self._coll._children(RecordTypeData):
            yield t
        return

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
            ALL (or blank)              match any entity
            @type>=<uri>/<curie>        entity has indicated type
            [annal:type]==annal:Field   entity type is indicated value
            [<field>]==<value>          entity named field is indicated value

        >>> e  = { 'p:a': '1', 'p:b': '2', 'p:c': '3', '@type': ["http://example.com/type", "foo:bar"] }
        >>> f1 = "[p:a]==1"
        >>> f2 = "[p:a]==2"
        >>> f3 = ''
        >>> f4 = "@type>=http://example.com/type"
        >>> f5 = "@type>=foo:bar"
        >>> f6 = "@type>=bar:foo"
        >>> EntityFinder.compile_selector_filter(f1)(e)
        True
        >>> EntityFinder.compile_selector_filter(f2)(e)
        False
        >>> EntityFinder.compile_selector_filter(f3)(e)
        True
        >>> EntityFinder.compile_selector_filter(f4)(e)
        True
        >>> EntityFinder.compile_selector_filter(f5)(e)
        True
        >>> EntityFinder.compile_selector_filter(f6)(e)
        False
        """
        def match_any(e):
            return True
        def match_type(type_val):
            def match_type_f(e):
                return type_val in e.get('@type',[])
            return match_type_f
        def match_field(field_name, field_val):
            def match_field_f(e):
                return e[field_name] == field_val
            return match_field_f
        if selector in {"", "ALL"}:
            return match_any
        #
        # RFC3986:
        #    unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
        #    reserved      = gen-delims / sub-delims
        #    gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
        #    sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
        #                  / "*" / "+" / "," / ";" / "="
        #
        # Not matching [ ] ' for now
        #
        tm = re.match(r'@type>=((\w|[-.~:/?#@!$&()*+,;=])+)$', selector)
        if tm:
            return match_type(tm.group(1))
        sm = re.match(r'\[((\w|:)+)\]==((\w|:)+)$', selector)
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
