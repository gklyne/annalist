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
from pyparsing import Word, QuotedString, Literal, Group, Empty, StringEnd, ParseException
from pyparsing import alphas, alphanums

from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitytypeinfo import EntityTypeInfo, get_built_in_type_ids

#   -------------------------------------------------------------------
#   Auxilliary fiunctions
#   -------------------------------------------------------------------

def order_entity_key(entity):
    """
    Function returns sort key for ordering entities by type and entity id

    Use with `sorted`, thus:

        sorted(entities, order_entity_key)
    """
    type_id   = entity.get_type_id() 
    entity_id = entity.get_id()
    key = ( 0 if type_id.startswith('_')   else 1, type_id, 
            0 if entity_id.startswith('_') else 1, entity_id
          )
    # log.info(key)
    return key

#   -------------------------------------------------------------------
#   EntityFinder
#   -------------------------------------------------------------------

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
        self._selector = EntitySelector(selector)
        return

    def get_collection_type_ids(self):
        """
        Returns iterator over possible type ids in current collection.

        Each type is returned as a candidate type identifier string
        """
        for t in get_built_in_type_ids():
            yield t
        for t in self._coll._children(RecordTypeData):
            yield t
        return

    def get_type_entities(self, type_id, user_permissions, scope):
        """
        Iterate over entities from collection matching the supplied type.

        'scope' is used to determine the extend of data top be included in the listing:
        a value of 'all' means that site-wide entyioties are icnluded in the listing.
        Otherwise only collection entities are included.        
        """
        entitytypeinfo = EntityTypeInfo(self._site, self._coll, type_id)
        include_sitedata = (scope == "all")
        for e in entitytypeinfo.enum_entities(user_permissions, usealtparent=include_sitedata):
            yield e
        return

    def get_all_types_entities(self, types, user_permissions, scope):
        """
        Iterate mover all entities of all types from a supplied type iterator
        """
        assert user_permissions is not None
        for t in types:
            for e in self.get_type_entities(t, user_permissions, scope):
                yield e
        return

    def get_base_entities(self, type_id=None, user_permissions=None, scope=None):
        """
        Iterate over base entities from collection, matching the supplied type id if supplied.

        If a type_id is supplied, site data values are included.
        """
        if type_id:
            return self.get_type_entities(type_id, user_permissions, scope)
        else:
            return self.get_all_types_entities(
                self.get_collection_type_ids(), user_permissions, scope
                )
        return

    def search_entities(self, entities, search):
        """
        Iterate over entities from supplied iterator containing supplied search term.
        """
        for e in entities:
            if self.entity_contains(e, search):
                yield e
        return

    def get_entities(self, 
        user_permissions=None, type_id=None, scope=None, context=None, search=None
        ):
        """
        Get list of entities of the specified type, matching search term and visible to 
        supplied user permissions.
        """
        entities = self._selector.filter(
            self.get_base_entities(type_id, user_permissions, scope), context=context
            )
        if search:
            entities = self.search_entities(entities, search)
        return entities

    def get_entities_sorted(self, 
        user_permissions=None, type_id=None, scope=None, context={}, search=None
        ):
        """
        Get sorted list of entities of the specified type, matching search term and 
        visible to supplied user permissions.
        """
        entities = self.get_entities(
            user_permissions, type_id=type_id, scope=scope, 
            context=context, search=search
            )
        return sorted(entities, key=order_entity_key)

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

#   -------------------------------------------------------------------
#   EntitySelector
#   -------------------------------------------------------------------

class EntitySelector(object):
    """
    This class implements a selector filter.  It is initialized with a selector
    expression, and may be invoked as a filter applied to an entity generator,
    or as a predicater applied to a single entity.

    >>> e  = { 'p:a': '1', 'p:b': '2', 'p:c': '3', '@type': ["http://example.com/type", "foo:bar"] }
    >>> c  = { 'view': { 'v:a': '1', 'v:b': ['2', '3'] } }
    >>> f1 = "'1' == [p:a]"
    >>> f2 = "[p:a]=='2'"
    >>> f3 = ''
    >>> f4 = "'http://example.com/type' in [@type]"
    >>> f5 = "'foo:bar' in [@type]"
    >>> f6 = "'bar:foo' in [@type]"
    >>> f7 = "[p:a] in view[v:a]"
    >>> f8 = "[p:b] in view[v:b]"
    >>> f9 = "[p:a] in view[v:b]"
    >>> f10 = "[annal:field_entity_type] in view[annal:record_type]"
    >>> f11 = "foo:bar in [@type]"
    >>> f12 = "bar:foo in [@type]"
    >>> EntitySelector(f1).select_entity(e, c)
    True
    >>> EntitySelector(f2).select_entity(e, c)
    False
    >>> EntitySelector(f3).select_entity(e, c)
    True
    >>> EntitySelector(f4).select_entity(e, c)
    True
    >>> EntitySelector(f5).select_entity(e, c)
    True
    >>> EntitySelector(f6).select_entity(e, c)
    False
    >>> EntitySelector(f7).select_entity(e, c)
    True
    >>> EntitySelector(f8).select_entity(e, c)
    True
    >>> EntitySelector(f9).select_entity(e, c)
    False
    >>> EntitySelector(f10).select_entity(e, c)
    True
    >>> EntitySelector(f11).select_entity(e, c)
    True
    >>> EntitySelector(f12).select_entity(e, c)
    False
    """
    def __init__(self, selector):
        # Returns None if no filter is applied, otherwise a predcicate function
        self._selector = self.compile_selector_filter(selector)
        return

    def filter(self, entities, context=None):
        """
        Iterate over selection of entities from supplied iterator, using the
        selection specification supplied to the constructor of the current object.

        entities    is an iterator over entities from which selection is made
        context     is a dictionary of context values that may be referenced by 
                    the selector in choosing entities to be returned.

        If no filtering is applied, the supplied iterator is returned as-is.
        """
        if self._selector:
            entities = self._filter(entities, context)
        return entities

    def _filter(self, entities, context):
        """
        Internal helper applies selector to entity iterator, returning a new iterator.
        """
        for e in entities:
            if self._selector(e, context):
                yield e
        return

    def select_entity(self, entity, context={}):
        """
        Apply selector to an entity, and returns True if the entity is selected
        """
        if self._selector:
            return self._selector(entity, context)
        return True

    @classmethod  #@@ @staticmethod, no cls?
    def parse_selector(cls, selector):
        """
        Parse a selector and return list of tokens

        Selector formats:
            ALL (or blank)              match any entity
            <val1> == <val2>            values are same
            <val1> in <val2>            second value is list containing 1st value, 
                                        or values are same, or val1 is None.

            <val1> and <val2> may be:

            [<field-id>]                refers to field in entity under test
            <name>[<field-id>]          refers to field of context value, or None if the
                                        indicated context value or field is not defined.
            "<string>"                  literal string value.  Quotes within are escaped.

        <field_id> values are URIs or CURIEs, using characters defined by RFC3986,
        except "[" and "]"
        
        RFC3986:
           unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
           reserved      = gen-delims / sub-delims
           gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
           sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                         / "*" / "+" / "," / ";" / "="
        """
        def get_value(val_list):
            if len(val_list) == 1:
                return { 'type': 'literal', 'name': None,        'field_id': None,        'value': val_list[0] }
            elif val_list[0] == '[':
                return { 'type': 'entity',  'name': None,        'field_id': val_list[1], 'value': None }
            elif val_list[1] == '[':
                return { 'type': 'context', 'name': val_list[0], 'field_id': val_list[2], 'value': None }
            else:
                return { 'type': 'unknown', 'name': None,        'field_id': None,        'value': None }
        p_name     = Word(alphas+"_", alphanums+"_")
        p_id       = Word(alphas+"_@", alphanums+"_-.~:/?#@!$&'()*+,;=)")
        p_val      = ( Group( Literal("[") + p_id + Literal("]") )
                     | Group( p_name + Literal("[") + p_id + Literal("]") )
                     | Group( QuotedString('"', "\\") )
                     | Group( QuotedString("'", "\\") )
                     | Group( p_id )
                     )
        p_comp     = ( Literal("==") | Literal("in") )
        p_selector = ( p_val + p_comp + p_val + StringEnd() )
        try:
            resultlist = p_selector.parseString(selector).asList()
        except ParseException:
            return None
        resultdict = {}
        if resultlist:
            resultdict['val1'] = get_value(resultlist[0])
            resultdict['comp'] = resultlist[1]
            resultdict['val2'] = get_value(resultlist[2])
        return resultdict

    @classmethod  #@@TODO: @staticmethod, no cls?
    def compile_selector_filter(cls, selector):
        """
        Return filter for for testing entities matching a supplied selector.

        Returns None if no selection is performed; i.e. all possible entities are selected.

        Selector formats:
            ALL (or blank)              match any entity
            <val1> == <val2>            values are same
            <val1> in <val2>            second value is list containing 1st value, 
                                        or values are same, or val1 is None.

            <val1> and <val2> may be:

            [<field-id>]                refers to field in entity under test
            <name>[<field-id>]          refers to field of context value, or None if the
                                        indicated context value or field is not defined.
            "<string>"                  literal string value.  Quotes within are escaped.
        """
        def get_entity(field_id):
            "Get field from entity tested by filter"
            def get_entity_f(e, c):
                return e.get(field_id, None)
            return get_entity_f
        #
        def get_context(name, field_id):
            "Get field from named value in current display context"
            def get_context_f(e, c):
                # Raises error if context value not supplied
                if name in c and c[name]:
                    return c[name].get(field_id, None)
                return None
            return get_context_f
        #
        def get_literal(value):
            "Get literal value specified directly in selector string"
            def get_literal_f(e, c):
                return value
            return get_literal_f
        #
        def get_val_f(selval):
            if selval['type'] == "entity":
                return get_entity(selval['field_id'])
            elif selval['type'] == "context":
                return get_context(selval['name'], selval['field_id'])
            elif selval['type'] == "literal":
                return get_literal(selval['value'])
            else:
                raise ValueError("Unrecognized value type from selector (%s)"%selval['type'])
                assert False, "Unrecognized value type from selector"
        #
        def match_eq(v1f, v2f):
            def match_eq_f(e, c):
                return v1f(e, c) == v2f(e, c)
            return match_eq_f
        #
        def match_in(v1f, v2f):
            def match_in_f(e, c):
                v1 = v1f(e, c)
                if not v1: return True
                v2 = v2f(e, c)
                if isinstance(v2, list):
                    return v1 in v2
                return v1 == v2
            return match_in_f
        #
        if selector in {None, "", "ALL"}:
            return None
        sel = cls.parse_selector(selector)
        if not sel:
            raise ValueError("Unrecognized selector syntax (%s)"%selector)
        v1f = get_val_f(sel['val1'])
        v2f = get_val_f(sel['val2'])
        if sel['comp'] == "==":
            return match_eq(v1f, v2f)
        if sel['comp'] == "in":
            return match_in(v1f, v2f)
        # Drop through: raise error
        raise ValueError("Unrecognized entity selector (%s)"%selector)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
