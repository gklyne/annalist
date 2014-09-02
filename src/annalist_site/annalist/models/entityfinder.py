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

    def __init__(self, coll, selector=None):
        """
        Initialize entity finder for collection and selector.
        """
        super(EntityFinder, self).__init__()
        self._coll     = coll
        self._site     = coll.get_site()
        self._selector = self.compile_selector_filter(selector)  #@@ change to separate class?
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

    def get_type_entities(self, type_id, include_sitedata=False):
        """
        Iterate over entities from collection matching the supplied type.

        If `include_sitedata` is True, include instances of supplied type_id
        that are defined in site-wide data as well as those in the collection.
        """
        entitytypeinfo = EntityTypeInfo(self._site, self._coll, type_id)
        for e in entitytypeinfo.enum_entities(usealtparent=include_sitedata):
            yield e
        return

    def get_all_types_entities(self, types, include_sitedata=False):
        """
        Iterate mover all entities of all types from a supplied type iterator
        """
        for t in types:
            for e in self.get_type_entities(t, include_sitedata=include_sitedata):
                yield e
        return

    def get_base_entities(self, type_id=None):
        """
        Iterate over base entities from collection, matching the supplied type id if supplied.

        If a type_id is supplied, site data values are included.
        """
        if type_id:
            return self.get_type_entities(type_id, include_sitedata=True)
        else:
            return self.get_all_types_entities(self.get_collection_type_ids(), include_sitedata=False)
        return

    def select_entities(self, entities, context={}):
        """
        Iterate over selection of entities from supplied iterator, using the
        selection specification supplied to the constructor of the current object.

        entities    is an iteratyor over entities from which selection is made
        context     is a dictionary of context values that may be referenced by 
                    the selector in choosing entities to be returned.
        """
        for e in entities:
            if self._selector(e, context=context):
                yield e
        return

    def search_entities(self, entities, search):
        """
        Iterate over entities from supplied iterator containing supplied search term.
        """
        for e in entities:
            if self.entity_contains(e, search):
                yield e
        return

    def get_entities(self, type_id=None, context={}, search=None):
        entities = self.select_entities(self.get_base_entities(type_id), context=context)
        if search:
            entities = self.search_entities(entities, search)
        #@@
        #
        # for e in self.get_selected_entities(type_id=type_id, selector=selector):
        #     if self.entity_contains(e, search):
        #         yield e
        #@@
        return entities


    #@@
    # def get_selected_entities(self, type_id=None, selector=None):
    #     if selector:
    #         s = self.compile_selector(type_id, selector)
    #         if s:
    #             for e in s:
    #                 yield e
    #     else:
    #         for e in self.get_base_entities(type_id):
    #             yield e
    #     return
    #@@

    #@@
    # def compile_selector(self, type_id, selector):
    #     """
    #     Return iterator for entities matching supplied selector.
    #     """
    #     ff = self.compile_selector_filter(selector)
    #     # Test all entitities in collection (not including built-in types)
    #     for e in self.get_base_entities(type_id):
    #         if ff(e): yield e
    #     return
    #@@

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
        >>> c  = {}
        >>> f1 = "[p:a]==1"
        >>> f2 = "[p:a]==2"
        >>> f3 = ''
        >>> f4 = "@type>=http://example.com/type"
        >>> f5 = "@type>=foo:bar"
        >>> f6 = "@type>=bar:foo"
        >>> EntityFinder.compile_selector_filter(f1)(e, c)
        True
        >>> EntityFinder.compile_selector_filter(f2)(e, c)
        False
        >>> EntityFinder.compile_selector_filter(f3)(e, c)
        True
        >>> EntityFinder.compile_selector_filter(f4)(e, c)
        True
        >>> EntityFinder.compile_selector_filter(f5)(e, c)
        True
        >>> EntityFinder.compile_selector_filter(f6)(e, c)
        False
        """
        def match_any(e, context):
            return True
        def match_type(type_val):
            def match_type_f(e, context):
                return type_val in e.get('@type',[])
            return match_type_f
        def match_field(field_name, field_val):
            def match_field_f(e, context):
                return e[field_name] == field_val
            return match_field_f
        if selector in {None, "", "ALL"}:
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
