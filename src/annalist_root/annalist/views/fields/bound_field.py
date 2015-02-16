"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections    import OrderedDict, namedtuple

from django.conf                    import settings

from annalist.identifiers           import RDFS, ANNAL

from annalist.models.entitytypeinfo import EntityTypeInfo
from annalist.models.entity         import EntityRoot

from annalist.views.uri_builder     import uri_params, uri_with_params, continuation_params

class bound_field(object):
    """
    Class representing an entity bound to a field description, 
    which can be used as input for data driven rendering of a form field.

    The field description contains information used to extract the field
    value from the entity.

    This class, and in particular its `__getattr__` method, is provided to 
    allow indirected access to an entity value fields to be performed using a 
    Django template using, e.g., "{{ field.field_value }}" (thus satisfying the 
    Django design goal that computation is handled in the python code rather 
    than the template, though in this case the computation us handled while
    rather than before the page is rendered).

    See also: http://docs.python.org/2/reference/datamodel.html#slots

    >>> entity = EntityRoot("entityuri", "entitydir")
    >>> entity.set_id("testentity")
    >>> vals = entity.set_values({"foo": "foo_val", "bar": "bar_val"})
    >>> field_foo_desc = {"field_id": "foo_id", "field_property_uri": "foo", "field_type": "foo_type"}
    >>> field_foo = bound_field(field_foo_desc, entity)
    >>> field_foo.field_type
    'foo_type'
    >>> field_foo.field_value
    'foo_val'
    >>> field_bar_desc = {"field_id": "bar_id", "field_property_uri": "bar", "field_type": "bar_type"}
    >>> field_bar = bound_field(field_bar_desc, entity)
    >>> field_bar.field_type
    'bar_type'
    >>> field_bar.field_value
    'bar_val'
    >>> field_def_desc = {"field_id": "def_id", "field_property_uri": "def", "field_type": "def_type"}
    >>> entityvals = entity.get_values()
    >>> entityvals['entity_id']      = entity.get_id()
    >>> entityvals['entity_type_id'] = entity.get_type_id()
    >>> entityvals['entity_link']    = entity.get_url()
    >>> field_def = bound_field(field_def_desc, entity)
    >>> field_def.field_type
    'def_type'
    >>> field_def.field_placeholder in ["...","@@bound_field.field_placeholder@@"]
    True
    >>> field_def.field_value == ""
    True
    >>> field_def = bound_field(field_def_desc, entity, context_extra_values={"def": "default"})
    >>> field_def.field_type
    'def_type'
    >>> field_def.field_value
    'default'
    >>> field_def.entity_link
    'entityuri/'
    >>> field_def.htmlrepr()
    "<ul><li>key: def</li><li>val: default</li><li>field_description: {'field_property_uri': 'def', 'field_id': 'def_id', 'field_type': 'def_type'}</li></ul>"
    """

    __slots__ = ("_field_description", "_entityvals", "_key", "_extras")

    def __init__(self, field_description, entityvals, context_extra_values=None):
        """
        Initialize a bound_field object.

        field_description       is a dictionary-like object describing a display
                                field.  See `FieldDescription` class for more details.
        entityvals              is an entity values dictionary from which a value to be 
                                rendered is obtained.  The specific field value used is 
                                defined by the combination with `field_description`.  
        context_extra_values    if supplied, a supplementary value dictionary that may be
                                probed for values that are not provided by the entity itself.  
                                Can be used to specify default values for an entity.
        """
        self._field_description = field_description
        self._entityvals        = entityvals
        self._key               = self._field_description['field_property_uri']
        self._extras            = context_extra_values
        eid = entityvals.get('entity_id', "@@@render_utils.__init__@@@")
        # log.log(settings.TRACE_FIELD_VALUE,
        #     "bound_field: field_id %s, entity_id %s, value_key %s, value %s"%
        #     (field_description['field_id'], eid, self._key, self['field_value'])
        #     )
        return

    def __getattr__(self, name):
        """
        Get a bound field description attribute.  If the attribute name is "field_value"
        then the value corresponding to the field description is retrieved from the entity,
        otherwise the named attribute is retrieved from thge field description.
        """
        # log.info("self._key %s, __getattr__ %s"%(self._key, name))
        # log.info("self._key %s"%self._key)
        # log.info("self._entity %r"%self._entity)
        if name in ["entity_id", "entity_link", "entity_type_id", "entity_type_link"]:
            return self._entityvals.get(name, "")
        elif name == "field_value_key":
            return self._key
        elif name == "context_extra_values":
            return self._extras
        elif name == "field_placeholder":
            return self._field_description.get('field_placeholder', "@@bound_field.field_placeholder@@")
        elif name == "continuation_url":
            if self._extras is None:
                log.warning("bound_field.continuation_url - no extra context provided")
                return ""
            cont = self._extras.get("request_url", "")
            if cont:
                cont = uri_with_params(cont, continuation_params(self._extras))
            return cont
        elif name == "entity_link_continuation":
            return self.entity_link+self.get_continuation_param()
        elif name == "entity_type_link_continuation":
            return self.entity_type_link+self.get_continuation_param()
        elif name == "field_value":
            field_val = None
            if self._key in self._entityvals:
                field_val = self._entityvals[self._key]
            elif self._extras and self._key in self._extras:
                field_val = self._extras[self._key]
            if field_val is None:
                # Return default value, or empty string.
                # Used to populate form field value when no value supplied, or provide per-field default
                field_val = self._field_description.get('field_default_value', None)
                if field_val is None:
                    field_val = ""
            return field_val
        elif name == "field_value_link":
            # Used to get link corresponding to a value, if such exists
            return self.get_field_link()
        elif name == "field_value_link_continuation":
            # Used to get link corresponding to a value, if such exists
            link = self.get_field_link()
            if link:
                link += self.get_continuation_param()
            return link
        elif name == "field_description":
            # Used to get link corresponding to a value, if such exists
            return self._field_description
        elif name == "options":
            return self.get_field_options()
        else:
            # log.info("bound_field[%s] -> %r"%(name, self._field_description[name]))
            return self._field_description[name]

    def get_field_link(self):
        # Return link corresponding to field value, or None
        links = self._field_description['field_choice_links']
        v     = self.field_value
        if links and v in links:
            return links[v]
        return None

    def get_field_options(self):
        options = self._field_description['field_choice_labels']
        options = options.values() if options is not None else ["(no options)"]
        return options

    def get_continuation_param(self):
        cparam = self.continuation_url
        if cparam:
            cparam = uri_params({'continuation_url': cparam})
        log.debug('bound_field.get_continuation_param %s'%(cparam,))  #@@
        return cparam

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __iter__(self):
        """
        Implement iterator protocol, returning accessible value keys.
        """
        yield "entity_id"
        yield "entity_type_id"
        yield "entity_link"
        yield "entity_link_continuation"
        yield "entity_type_link"
        yield "entity_type_link_continuation"
        yield "continuation_url"
        yield "field_value"
        yield "field_value_link"
        yield "options"
        for k in self._field_description:
            yield k
        return

    def as_dict(self):
        return dict(self._field_description.items(), 
            entity=dict(self._entityvals.items()), 
            field_value=self.field_value, 
            context_extra_values=self._extras, 
            key=self._key
            )

    def __repr__(self):
        return self.fullrepr()

    def shortrepr(self):
        return (
            "bound_field(\n"+
            "  { 'key': %r\n"%(self._key,)+
            "  , 'val': %r\n"%(self.field_value,)+
            "  , 'field_description': %r\n"%(self._field_description,)+
            "  })")

    def fullrepr(self):
        return (
            "bound_field({'field':%r, 'vals':%r, 'field_value':%r, 'extras':%r})"%
            (self._field_description, dict(self._entityvals.items()), 
                self.field_value, self._extras) 
            )

    def htmlrepr(self):
        return (
            "<ul>"+
            "<li>key: %s</li>"%(self._key,)+
            "<li>val: %s</li>"%(self.field_value,)+
            "<li>field_description: %r</li>"%(self._field_description,)+
            "</ul>"
            )

def get_entity_values(displayinfo, entity, entity_id=None):
    """
    Returns an entity values dictionary for a supplied entity, suitable for
    use with a bound_field object.
    """
    if not entity_id:
        entity_id = entity.get_id()
    type_id    = entity.get_type_id()
    entityvals = entity.get_values().copy()
    entityvals['entity_id']      = entity_id
    entityvals['entity_link']    = entity.get_view_url_path()
    # log.info("type_id %s"%(type_id))
    entityvals['entity_type_id'] = type_id
    typeinfo   = EntityTypeInfo(displayinfo.site, displayinfo.collection, type_id)
    if typeinfo.recordtype:
        entityvals['entity_type_link'] = typeinfo.recordtype.get_view_url_path()
        # @@other type-related info; e.g., aliases - populate 
    return entityvals

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
