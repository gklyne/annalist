"""
This module defines a class that performs mapping of entity data between 
whoile entities, (Django) view contexts and form data.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy

class EntityValueMap(object):
    """
    This class represents a mapping between some specific entity data
    and view context data and HTML form data.
    """

    def __init__(self, basemap):
        """
        Initialize and entity-map value.

        basemap is a static list of the initial (base) fields that are covered
                by this EntityValueMap.  Each entry in this list provides at 
                least these three methods:
                map_entity_to_context:
                    accepts a dictionary-like value containing entity values,
                    and extra/default value keyword parameters, and returns a 
                    partial context dictionary corresponding for item(s) covered
                    by the described entry.
                map_form_to_entity:
                    accepts a dictionary-like value containing form data values, 
                    and returns a partial dictionary of corressponding entity 
                    value fields.
                get_structure_description:
                    returns a simple directory describing the field structure.
                    Common to all is member 'field_type', which indicates the type
                    if field map entry.  Other fields are dependent onthe type.

        See classes SimpleValueMap, FieldValue, FieldListValueMap, 
        RepeatedValuesMap, etc., for possible entries in an entity/value map.

        NOTE: mapping from context to form data is handled by templates 
        and/or field renderers.
        """
        super(EntityValueMap, self).__init__()
        self._map = copy.copy(basemap)
        return

    def __iter__(self):
        """
        Return entity value map entries
        """
        for map_entry in self._map:
            yield map_entry
        return

    def add_map_entry(self, map_entry):
        """
        Adds a single mapping entry to an entity/value map.
        """
        self._map.append(map_entry)
        return

    def map_value_to_context(self, entity_values, **kwargs):
        """
        Map data from entity values to view context for rendering.

        Values defined in the supplied entity take priority, and the keyword 
        arguments provide values when the entity does not.
        """
        # log.debug("EntityValueMap.map_value_to_context, context_extra_values: %r"%(kwargs,))
        context = {}
        for kmap in self._map:
            # log.debug("EntityValueMap.map_value_to_context, kmap: %r"%(kmap,))
            kval = kmap.map_entity_to_context(entity_values, context_extra_values=kwargs)
            # log.debug("EntityValueMap.map_value_to_context, kval: %r"%(kval,))
            context.update(kval)
        return context

    def map_form_data_to_values(self, form_data, entityvals, **kwargs):
        """
        Map data from form response to entity data.  

        Returns a deep copy of the supplied `entityvals` updated with values from
        then form.  Values not mentioned in the form data are not updated.
        """
        log.debug("map_form_data_to_values: form_data %r, entityvals %r"%(form_data, entityvals))
        values = copy.deepcopy(entityvals) or {}
        for kmap in self._map:
            kmap.map_form_to_entity(form_data, values)
        return values

# End.
