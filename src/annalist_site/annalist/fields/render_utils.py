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

# from annalist.fields.render_text    import RenderText
from render_text    import RenderText

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

    >>> entity = {"foo": "foo_val", "bar": "bar_val" }
    >>> field_foo_desc = {"field_property_uri": "foo", "field_type": "foo_type"}
    >>> field_foo = bound_field(field_foo_desc, entity)
    >>> field_foo.field_type
    'foo_type'
    >>> field_foo.field_value
    'foo_val'
    >>> field_bar_desc = {"field_property_uri": "bar", "field_type": "bar_type"}
    >>> field_bar = bound_field(field_bar_desc, entity)
    >>> field_bar.field_type
    'bar_type'
    >>> field_bar.field_value
    'bar_val'
    >>> field_def_desc = {"field_property_uri": "def", "field_type": "def_type"}
    >>> field_def = bound_field(field_def_desc, entity)
    >>> field_def.field_type
    'def_type'
    >>> field_def.field_value == None
    True
    >>> field_def = bound_field(field_def_desc, entity, default="default")
    >>> field_def.field_type
    'def_type'
    >>> field_def.field_value
    'default'
    """

    __slots__ = ("_field_description", "_entity", "_key", "_default")

    def __init__(self, field_description=None, entity=None, key=None, default=None):
        """
        Initialize a bound_field object.

        field_description   is a dictionary-like object describing a display
                            field.  See assignment of `field_context` in 
                            `views.entityeditbase` for more details of this.
        entity              is an entity from which a value to be rendered is
                            obtained.  The specific field value used is defined
                            by the combination with `field_description`
        key                 a key used to extract a field from the supplied entity.
                            If not specified, the value of the `field_property_uri`
                            field of the field description is used: this assumes the
                            supplied entity is an actual entity rather than a field 
                            value dictionary .
        default             is a default value to be used if the entity does 
                            not define the required value.
        """
        self._field_description = field_description
        self._entity            = entity
        self._key               = key or self._field_description['field_property_uri']
        self._default           = default
        return

    def __getattr__(self, name):
        """
        Get a bound field description attribute.  If the attribute name is "field_value"
        then the value corresponding to the field description is retrieved from the entity,
        otherwise the named attribute is retrieved from thge field description.
        """
        # log.info("__getattr__ %s"%name)
        # log.info("self._key %s"%self._key)
        # log.info("self._entity %r"%self._entity)
        if name == "field_value":
            # Note: .keys() is required here as iterator on EntityData returns files in directory
            if self._key in self._entity.keys():
                return self._entity[self._key]
            else:
                return self._default
        else:
            return self._field_description[name]

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __iter__(self):
        """
        Implement iterator protocol, returning accessible value keys.
        """
        yield "field_value"
        for k in self._field_description:
            yield k
        return

    def as_dict(self):
        return dict(self._field_description.items(), 
            entity=dict(self._entity.items()), 
            field_value=self.field_value, 
            default=self._default, 
            key=self._key
            )

    def __repr__(self):
        return repr(self.as_dict())


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
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_edit_textarea.html"
    log.warning("get_edit_renderer: %s not found"%renderid)
    return None

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
    if renderid == "annal:field_render/Textarea":
        return "field/annalist_view_textarea.html"
    log.warning("get_edit_renderer: %s not found"%renderid)
    return None

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
    log.debug("get_item_renderer: %s not found"%renderid)
    return "field/annalist_item_none.html"

Placement = namedtuple("Placement", ['field', 'label', 'value'])

def get_placement_classes(placement):
    """
    Returns placement classes corresponding to placement string provided.

    >>> get_placement_classes("small:0,12").field
    'small-12 columns'
    >>> get_placement_classes("small:0,12").label
    'small-12 medium-2 columns'
    >>> get_placement_classes("small:0,12").value
    'small-12 medium-10 columns'
    >>> get_placement_classes("medium:0,12")
    Placement(field='small-12 columns', label='small-12 medium-2 columns', value='small-12 medium-10 columns')
    >>> get_placement_classes("large:0,12")
    Placement(field='small-12 columns', label='small-12 medium-2 columns', value='small-12 medium-10 columns')
    >>> get_placement_classes("small:0,12;medium:0,4")
    Placement(field='small-12 medium-4 columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    >>> get_placement_classes("small:0,12;medium:0,6;large:0,4")
    Placement(field='small-12 medium-6 large-4 columns', label='small-12 medium-4 large-6 columns', value='small-12 medium-8 large-6 columns')
    >>> get_placement_classes("small:0,6;medium:0,4")
    Placement(field='small-6 medium-4 columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    """
    def format_class(cd):
        prev = cd.get("small", None)
        for test in ("medium", "large"):
            if (test in cd):
                if cd[test] == prev:
                    del cd[test]
                else:
                    prev = cd[test]
        return " ".join([k+"-"+str(v) for k,v in cd.items()]) + " columns"
    ppr = re.compile(r"^(small|medium|large):(\d+),(\d+)$")
    ps = placement.split(';')
    labelw      = {'small': 12, 'medium': 2, 'large': 2}
    field_width = OrderedDict([ ('small', 12) ])
    label_width = OrderedDict([ ('small', 12), ('medium',  2) ])
    value_width = OrderedDict([ ('small', 12), ('medium', 10) ])
    for p in ps:
        pm = ppr.match(p)
        if not pm:
            break
        pmmode   = pm.group(1)    # "small", "medium" or "large"
        pmoffset = int(pm.group(2))
        pmwidth  = int(pm.group(3))
        field_width[pmmode] = pmwidth
        label_width[pmmode] = labelw[pmmode]*(12 // pmwidth)
        value_width[pmmode] = 12 - label_width[pmmode]
        if label_width[pmmode] >= 12:
            label_width[pmmode] = 12
            value_width[pmmode] = 12
    c = Placement(
            field=format_class(field_width),
            label=format_class(label_width),
            value=format_class(value_width)
            )
    log.debug("get_placement_class %s, returns %s"%(placement,c))
    return c

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
