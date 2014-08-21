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

from annalist.models.entity         import EntityRoot, Entity

from annalist.views.uri_builder     import uri_params

from render_text                    import RenderText

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
    >>> field_def.field_placeholder == "..."
    True
    >>> field_def.field_value == ""
    True
    >>> field_def = bound_field(field_def_desc, entity, extras={"def": "default"})
    >>> field_def.field_type
    'def_type'
    >>> field_def.field_value
    'default'
    >>> field_def.entity_link
    'entityuri/'
    >>> field_def.htmlrepr()
    "<ul><li>key: def</li><li>val: default</li><li>field_description: {'field_property_uri': 'def', 'field_id': 'def_id', 'field_type': 'def_type'}</li></ul>"
    """

    __slots__ = ("_field_description", "_entityvals", "_key", "_options", "_extras")

    def __init__(self, field_description, entityvals, key=None, options=None, extras=None):
        """
        Initialize a bound_field object.

        field_description   is a dictionary-like object describing a display
                            field.  See `FieldDescription` class for more details.
        entityvals          is an entity values dictionary from which a value to be 
                            rendered is obtained.  The specific field value used is 
                            defined by the combination with `field_description`.  
        key                 a key used to extract a field from the supplied entity.
                            If not specified, the value of the `field_property_uri`
                            field of the field description is used: this assumes the
                            supplied entity is an actual entity rather than a field 
                            value dictionary.
        options             for enumeration/select type fields, a list of allowable values
        extras              if supplied, a supplementary value dictionary that may be probed
                            for values that are not provided by the entity itself.  
                            Can be used to specify default values for an entity.
        """
        self._field_description = field_description
        self._entityvals        = entityvals
        self._key               = key or self._field_description['field_property_uri']
        self._options           = options
        self._extras            = extras
        # if isinstance(entity, EntityRoot):
        #     eid = entity.get_id()
        # else:
        #     eid = "(dict)"
        eid = entityvals.get('entity_id', "@@@render_utils.__init__@@@")
        log.log(settings.TRACE_FIELD_VALUE,
            "bound_field: field_id %s, entity_id %s, value_key %s, value %s"%
            (field_description['field_id'], eid, self._key, self['field_value'])
            )
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
        if name in ["entity_id", "entity_type_id", "entity_link"]:
            return self._entityvals.get(name, "")
        elif name == "field_value_key":
            return self._key
        elif name == "field_placeholder":
            return self._field_description.get('field_placeholder', "...")
        elif name == "continuation_url":
            return self._extras.get("request_url", "")
        elif name == "entity_link_continuation":
            return self.entity_link+self.get_continuation_param()
        elif name == "field_value":
            if self._key == "annal:type":
                # @@TODO: remove annal:Type hack when proper selection from enumerated entities
                #         has been implemented.
                #
                # The handling of annal:Type is something of a hack to return the internal
                # type-id for an entity rarther than its type URI/CURIE, which is used in 
                # turn by the form renderer to determine the type_id selection on the rendered
                # form.  This hack shoukd be rendered unnecessary when the entity reference
                # selection is properly generalized.
                return self.entity_type_id
            elif self._key in self._entityvals:
                return self._entityvals[self._key]
            elif self._extras and self._key in self._extras:
                return self._extras[self._key]
            else:
                # Return default value, or empty string.
                # Used to populate form field value when no value supplied
                return self._field_description.get('field_default_value', None) or ""
        elif name == "options":
            return self.get_field_options()
        else:
            # log.info("bound_field[%s] -> %r"%(name, self._field_description[name]))
            return self._field_description[name]

    def get_field_options(self):
        # log.info("get_field_options: %r"(self._options,))
        return self._options

    def get_continuation_param(self):
        cparam = self.continuation_url
        if cparam:
            cparam = uri_params({'continuation_url': cparam})
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
        yield "continuation_url"
        yield "entity_link_continuation"
        yield "field_value"
        yield "options"
        for k in self._field_description:
            yield k
        return

    def as_dict(self):
        return dict(self._field_description.items(), 
            entity=dict(self._entityvals.items()), 
            field_value=self.field_value, 
            extras=self._extras, 
            key=self._key
            )

    def __repr__(self):
        return self.shortrepr()

    def shortrepr(self):
        return (
            "bound_field(\n"+
            "  { 'key': %r\n"%(self._key,)+
            "  , 'val': %r\n"%(self.field_value,)+
            "  , 'field_description': %r\n"%(self._field_description,)+
            "  })")

    def fullrepr(self):
        return (
            "bound_field({'field':%r, 'vals':%r, 'key':%r, 'field_value':%r, 'extras':%r})"%
            (self._field_description, dict(self._entityvals.items()), 
                self._key, self.field_value, self._extras) 
            )

    def htmlrepr(self):
        return (
            "<ul>"+
            "<li>key: %s</li>"%(self._key,)+
            "<li>val: %s</li>"%(self.field_value,)+
            "<li>field_description: %r</li>"%(self._field_description,)+
            "</ul>")

def get_edit_renderer(renderid):
    """
    Returns an field edit renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    # @@TODO: currently just a minimal placeholder
    if renderid == "annal:field_render/Text":
        return "field/annalist_edit_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "field/annalist_edit_text.html"
    if renderid == "annal:field_render/Placement":
        return "field/annalist_edit_text.html"
    if renderid == "annal:field_render/EntityRef":
        return "field/annalist_edit_text.html"    
    if renderid == "annal:field_render/Identifier":
        return "field/annalist_edit_text.html"    
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_edit_textarea.html"
    if renderid == "annal:field_render/Type":
        return "field/annalist_edit_select.html"
    if renderid == "annal:field_render/View_fields":
        return "field/annalist_todo.html"
    log.warning("get_edit_renderer: %s not found"%renderid)
    # raise ValueError("get_edit_renderer: %s not found"%renderid)
    # Default to simple text for unknown renderer type
    return "field/annalist_edit_text.html"

def get_view_renderer(renderid):
    """
    Returns a field view renderer object that can be referenced in a 
    Django template "{% include ... %}" element.

    This version returns the name of a template to render the form.
    With future versions of Django (>=1.7), and alternative is to return an
    object with a `.render(context)` method that returns a string to be
    included in the resulting page:
        The variable may also be any object with a render() method that accepts 
        a context. This allows you to reference a compiled Template in your context.
        - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
    """
    # @@TODO: currently just a minimal placeholder
    if renderid == "annal:field_render/Text":
        return "field/annalist_view_text.html"
        # return RenderText()
    if renderid == "annal:field_render/Slug":
        return "field/annalist_view_text.html"
    if renderid == "annal:field_render/Placement":
        return "field/annalist_view_text.html"
    if renderid == "annal:field_render/EntityRef":
        return "field/annalist_view_entityref.html"    
    if renderid == "annal:field_render/Identifier":
        return "field/annalist_view_entityref.html"    
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_view_textarea.html"
    if renderid == "annal:field_render/Type":
        return "field/annalist_view_select.html"
    if renderid == "annal:field_render/View_fields":
        return "field/annalist_todo.html"
    log.warning("get_view_renderer: %s not found"%renderid)
    # raise ValueError("get_view_renderer: %s not found"%renderid)
    # Default to simple text for unknown renderer type
    return "field/annalist_view_text.html"

def get_head_renderer(renderid):
    """
    Returns a field list heading renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    return "field/annalist_head_any.html"

def get_item_renderer(renderid):
    """
    Returns a field list row-item renderer object that can be referenced in a 
    Django template "{% include ... %}" element.
    """
    if renderid == "annal:field_render/Text":
        return "field/annalist_item_text.html"
    if renderid == "annal:field_render/Slug":
        return "field/annalist_item_text.html"
    if renderid == "annal:field_render/EntityRef":
        return "field/annalist_item_entityref.html"    
    if renderid == "annal:field_render/Type":
        return "field/annalist_item_type.html"
    if renderid == "annal:field_render/Identifier":
        # @@TODO: use identifier lookup to display label
        return "field/annalist_item_text.html"
    log.debug("get_item_renderer: %s not found"%renderid)
    return "field/annalist_item_none.html"

def get_entity_values(entity, entity_id=None):
    """
    Returns an entity values dictionary for a supplied entity, suitable for
    use with a bound_field object (see above).
    """
    if not entity_id:
        entity_id = entity.get_id()
    entityvals = entity.get_values().copy()
    entityvals['entity_id']      = entity_id
    entityvals['entity_type_id'] = entity.get_type_id()
    entityvals['entity_link']    = entity.get_view_url_path()
    return entityvals

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
