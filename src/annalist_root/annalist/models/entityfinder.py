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

from annalist.util                  import valid_id, extract_entity_id

from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitytypeinfo import EntityTypeInfo

#   -------------------------------------------------------------------
#   Auxilliary functions
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
    return key

#   -------------------------------------------------------------------
#   EntityFinder
#   -------------------------------------------------------------------

class EntityFinder(object):
    """
    Logic for enumerating entities matching a supplied type, selector and/or search string.
    """

    def __init__(self, coll, selector=None):
        """
        Initialize entity finder for collection and selector.
        """
        super(EntityFinder, self).__init__()
        self._coll     = coll
        self._site     = coll.get_site()
        self._selector = EntitySelector(selector, FieldComparison(coll))
        # self._subtypes = None
        return

    def get_collection_type_ids(self, altscope):
        """
        Returns iterator over possible type ids in current collection.

        Each type is returned as a candidate type identifier string
        """
        for t in self._coll._children(RecordType, altscope=altscope):
            yield t
        return

    def get_collection_subtypes(self, type_id, altscope):
        """
        Returns a iterator of `entitytypeinfo` objects for all subtypes
        of the supplied type in the current collection, including the 
        identified type itself.
        """
        if not valid_id(type_id):
            log.warning("EntityFinder.get_collection_uri_subtypes: invalid type_id %s"%(type_id,))
            return []
        supertypeinfo = EntityTypeInfo(self._coll, type_id)
        supertypeuri  = supertypeinfo.get_type_uri()
        if supertypeuri is None:
            log.warning("EntityFinder.get_collection_uri_subtypes: no type_uri for %s"%(type_id,))
        return self.get_collection_uri_subtypes(supertypeuri, altscope)

    def get_collection_uri_subtypes(self, type_uri, altscope=None):
        """
        Returns a iterator of `entitytypeinfo` objects for all subtypes
        of the supplied type in the current collection, including the 
        identified type itself.
        """
        # log.info(
        #     "@@ EntityFinder.get_collection_uri_subtypes: type_uri %s, altscope=%s"%
        #     (type_uri, altscope)
        #     )
        if type_uri is not None:
            for tid in self.get_collection_type_ids(altscope):
                tinfo = EntityTypeInfo(self._coll, tid)
                if tinfo and (type_uri in tinfo.get_all_type_uris()):
                    yield tinfo
        return 

    def get_type_entities(self, type_id, user_permissions, altscope):
        """
        Iterate over entities from collection matching the supplied type.

        'altscope' is used to determine the extent of data to be included in the listing:
        a value of 'all' means that site-wide entyities are icnluded in the listing.
        Otherwise only collection entities are included.        
        """
        #@@
        # log.info("get_type_entities: type_id %s"%type_id)
        #@@
        entitytypeinfo = EntityTypeInfo(self._coll, type_id)
        for e in entitytypeinfo.enum_entities_with_implied_values(
                user_permissions, altscope=altscope
                ):
            if e.get_id() != "_initial_values":
                yield e
        return

    def get_subtype_entities(self, type_id, user_permissions, altscope):
        """
        Iterate over entities from collection that are of the indicated type
        or any of its subtypes.

        'altscope' is used to determine the extent of data to be included in the listing:
        a value of 'all' means that site-wide entities are included in the listing.
        Otherwise only collection entities are included.        
        """
        # NOTE: consider types from all scopes, then entities from specified scope
        for entitytypeinfo in self.get_collection_subtypes(type_id, "all"):
            es = entitytypeinfo.enum_entities_with_implied_values(
                    user_permissions, altscope=altscope
                    )
            es = list(es) #@@ Force strict eval
            for e in es:
                if e.get_id() != "_initial_values":
                    yield e
        return

    def get_all_types_entities(self, types, user_permissions, altscope):
        """
        Iterate over all entities of all type ids from a supplied type iterator
        """
        for t in types:
            for e in self.get_type_entities(t, user_permissions, altscope):
                yield e
        return

    def get_base_entities(self, type_id=None, user_permissions=None, altscope=None):
        """
        Iterate over base entities from collection, matching the supplied type id if supplied.

        If a type_id is supplied, site data values are included.
        """
        if type_id:
            #@@
            # log.info("get_base_entities: type_id %s"%type_id)
            #@@
            return self.get_subtype_entities(type_id, user_permissions, altscope)
            # return self.get_type_entities(type_id, user_permissions, scope)
        else:
            #@@
            # log.info("get_base_entities: all types")
            #@@
            return self.get_all_types_entities(
                self.get_collection_type_ids(altscope="all"), user_permissions, altscope
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
        user_permissions=None, type_id=None, altscope=None, context=None, search=None
        ):
        """
        Iterates over entities of the specified type, matching search term and visible to 
        supplied user permissions.
        """
        entities = self._selector.filter(
            self.get_base_entities(type_id, user_permissions, altscope), context=context
            )
        if search:
            entities = self.search_entities(entities, search)
        return entities

    def get_entities_sorted(self, 
        user_permissions=None, type_id=None, altscope=None, context={}, search=None
        ):
        """
        Get sorted list of entities of the specified type, matching search term and 
        visible to supplied user permissions.
        """
        entities = self.get_entities(
            user_permissions, type_id=type_id, altscope=altscope, 
            context=context, search=search
            )
        return sorted(entities, key=order_entity_key)

    @classmethod
    def entity_contains(cls, e, search):
        """
        Returns True if entity contains/matches search term, else False.
        Search term None (or blank) matches all entities.

        >>> e1  = { 'p:a': '1', 'p:b': '2', 'p:c': '3', 'annal:property_uri': 'annal:member' }
        >>> EntityFinder.entity_contains(e1, "1")
        True
        >>> EntityFinder.entity_contains(e1, "3")
        True
        >>> EntityFinder.entity_contains(e1, "nothere")
        False
        >>> EntityFinder.entity_contains(e1, "annal:member")
        True
        >>> e2 = { 'list': ['l1', 'l2', 'l3'] \
                 , 'dict': {'p:a': 'd1', 'p:b': 'd2', 'p:c': 'd3'} \
                 }
        >>> EntityFinder.entity_contains(e2, "l1")
        True
        >>> EntityFinder.entity_contains(e2, "d3")
        True
        >>> EntityFinder.entity_contains(e2, "nothere")
        False
        """
        if search:
            # Entity is not a dict, so scan entity keys for search
            for key in e:
                val = e[key]
                if cls.value_contains(val, search):
                    return True
                # if isinstance(val, (str, unicode)):
                #     if search in val:
                #         return True
            return False
        return True

    @classmethod
    def value_contains(cls, val, search):
        """
        Helper function tests for search term in dictionary, list or string values.
        Other values are not searched.
        """
        if isinstance(val, dict):
            for k in val:
                if cls.value_contains(val[k], search):
                    return True
        elif isinstance(val, list):
            for e in val:
                if cls.value_contains(e, search):
                    return True
        elif isinstance(val, (str, unicode)):
            return search in val
        return False

#   -------------------------------------------------------------------
#   EntitySelector
#   -------------------------------------------------------------------

class EntitySelector(object):
    """
    This class implements a selector filter.  It is initialized with a selector
    expression, and may be invoked as a filter applied to an entity generator,
    or as a predicate applied to a single entity.

    >>> e  = { 'p:a': '1', 'p:b': '2', 'p:c': '3', '@type': ["http://example.com/type", "foo:bar"] }
    >>> c  = { 'view': { 'v:a': '1', 'v:b': ['2', '3'] } }
    >>> f1 = "'1' == [p:a]"
    >>> f2 = "[p:a]=='2'"
    >>> f3 = ""
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
    def __init__(self, selector, fieldcomp=None):
        self._fieldcomp = fieldcomp
        # Returns None if no filter is applied, otherwise a predcicate function
        self._selector  = self.compile_selector_filter(selector)
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
            <val1> <name> <val2>        invoke comparison method from supplied 
                                        FieldComparison object

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

        Parser uses pyparsing combinators (cf. http://pyparsing.wikispaces.com).
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
        p_comp     = ( Literal("==") | Literal("in") | p_name )
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

    def compile_selector_filter(self, selector):
        """
        Return filter for for testing entities matching a supplied selector.

        Returns None if no selection is performed; i.e. all possible entities are selected.

        Selector formats: see `parse_selector` above.

        This function returns a filter function compiled from the supplied selector.
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
        def match_subtype(v1f, v2f):
            def match_subtype_f(e, c):
                return self._fieldcomp.subtype(v1f(e, c), v2f(e, c))
            return match_subtype_f
        #
        if selector in {None, "", "ALL"}:
            return None
        sel = self.parse_selector(selector)
        if not sel:
            raise ValueError("Unrecognized selector syntax (%s)"%selector)
        v1f = get_val_f(sel['val1'])
        v2f = get_val_f(sel['val2'])
        if sel['comp'] == "==":
            return match_eq(v1f, v2f)
        if sel['comp'] == "in":
            return match_in(v1f, v2f)
        if sel['comp'] == "subtype":
            return match_subtype(v1f, v2f)
        # Drop through: raise error
        raise ValueError("Unrecognized entity selector (%s)"%selector)

#   -------------------------------------------------------------------
#   FieldComparison
#   -------------------------------------------------------------------

class FieldComparison(object):
    """
    Logic for comparing fields using additional context information not available
    directly to 'EntitySelector'
    """

    def __init__(self, coll):
        super(FieldComparison, self).__init__()
        self._coll     = coll
        self._site     = coll.get_site()
        return

    def get_uri_type_info(self, type_uri):
        """
        Return typeinfo corresponding to the supplied type URI
        """
        t     = self._coll.get_uri_type(type_uri)
        return t and EntityTypeInfo(self._coll, t.get_id())

    def subtype(self, type1_uri, type2_uri):
        """
        Returns True if the first type is a subtype of the second type, where both
        types are supplied as type URIs.  Returns True if both URIs are the same.

        If type1_uri is not specified, assume no restriction.

        If type2_uri is not specified, assume it does not satisfy the restriction.
        """
        # log.info("FieldComparison.subtype(%s, %s)"%(type1_uri, type2_uri))
        if not type2_uri or (type1_uri == type2_uri):
            return True
        if not type1_uri:
            return False
        type1_info = self.get_uri_type_info(type1_uri)
        type1_supertype_uris = (type1_info and type1_info.get_all_type_uris()) or []
        # log.info("FieldComparison.subtype: type1_uris (supertypes) %r"%(type1_uris,))
        return type2_uri in type1_supertype_uris

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
