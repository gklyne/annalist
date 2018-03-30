"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import traceback
import re

from urlparse               import urljoin  # py3: from urllib.parse ...
from collections            import OrderedDict, namedtuple

from django.conf            import settings
from django.utils.html      import escape

from annalist.exceptions    import TargetIdNotFound_Error, TargetEntityNotFound_Error
from annalist.identifiers   import RDFS, ANNAL
from annalist.util          import split_type_entity_id

from annalist.models.entitytypeinfo         import EntityTypeInfo
from annalist.models.entity                 import EntityRoot

from annalist.views.uri_builder             import (
    uri_params, uri_with_params, continuation_params
    )
from annalist.views.form_utils.fieldchoice  import FieldChoice

# -----------------------------------------------------------------------------
# Field description for doctests (avoids circular imports via FieldDescription)
# -----------------------------------------------------------------------------

class MockFieldDescription(object):
    """
    Simplified field description for local testing.
    (Somehow, can't get it working with real FieldDescription...)
    (I think it may be a problem with import cycles...)
    """

    def __init__(self, coll, recordfield):
        self._field_desc = recordfield
        return

    def __copy__(self):
        """
        Shallow copy of self.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result._field_desc = self._field_desc
        return result

    def __repr__(self):
        return repr(self._field_desc)

    def __getitem__(self, k):
        """
        Allow direct indexing to access field description fields
        """
        return self._field_desc[k]

    def get(self, name, default):
        return self._field_desc.get(name, default)

    def get_field_id(self):
        """
        Returns the field identifier
        """
        return self._field_desc['field_id']

    def get_field_name(self):
        """
        Returns form field name to be used for the described field
        """
        return self.get('field_name', self.get_field_id())

    def get_field_property_uri(self):
        """
        Returns form field property URI to be used for the described field
        """
        return self._field_desc['field_property_uri']

    def get_field_subproperty_uris(self):
        """
        Returns list of possible subproperty URIs for the described field
        """
        return self._field_desc.get('field_subproperty_uris', [])

    def get_field_value_key(self, entityvals):
        """
        Returns field value key for use in supplied entity values instance
        """
        return self.get_field_property_uri()

# -----------------------------------------------------------------------------
# Bound field
# -----------------------------------------------------------------------------

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

    --- from annalist.views.fields.field_description import FieldDescription

    >>> coll = None
    >>> entity = EntityRoot("entityuri", "entityuri", "entitydir", "entitydir")
    >>> entity.set_id("testentity")
    >>> vals = entity.set_values({"foo": "foo_val", "bar": "bar_val"})
    >>> field_foo_desc = MockFieldDescription(coll, {"field_id": "foo_id", "field_property_uri": "foo", "field_type": "foo_type"})
    >>> field_foo = bound_field(field_foo_desc, entity)
    >>> field_foo._key
    'foo'
    >>> field_foo.description['field_type']
    'foo_type'
    >>> field_foo.field_value
    'foo_val'
    >>> field_bar_desc = MockFieldDescription(coll, {"field_id": "bar_id", "field_property_uri": "bar", "field_type": "bar_type"})
    >>> field_bar = bound_field(field_bar_desc, entity)
    >>> field_bar.description['field_type']
    'bar_type'
    >>> field_bar.field_value
    'bar_val'
    >>> field_def_desc = MockFieldDescription(coll, {"field_id": "def_id", "field_property_uri": "def", "field_type": "def_type"})
    >>> entityvals = entity.get_values()
    >>> entityvals['entity_id']      = entity.get_id()
    >>> entityvals['entity_type_id'] = entity.get_type_id()
    >>> entityvals['entity_link']    = entity.get_url()
    >>> field_def = bound_field(field_def_desc, entity)
    >>> field_def.description['field_type']
    'def_type'
    >>> field_def.field_value == ""
    True
    >>> field_def = bound_field(field_def_desc, entity, context_extra_values={"def": "default"})
    >>> field_def.description['field_type']
    'def_type'
    >>> field_def.field_value
    'default'
    >>> field_def.entity_link
    'entityuri/'
    >>> field_def.htmlrepr()
    "<ul><li>key: def</li><li>val: default</li><li>field_description: {'field_property_uri': 'def', 'field_id': 'def_id', 'field_type': 'def_type'}</li></ul>"
    """

    __slots__ = ("_field_description", "_entityvals", "_targetvals", "_key", "_extras")

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
        self._targetvals        = None
        self._key               = field_description.get_field_property_uri()
        self._extras            = context_extra_values
        return

    def __copy__(self):
        """
        Shallow(-ish) copy of self.

        (Tried code from http://stackoverflow.com/a/15774013, but hits recursion limit)
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result._field_description = self._field_description.copy()
        result._entityvals        = self._entityvals
        result._targetvals        = self._targetvals
        result._key               = self._key
        result._extras            = self._extras
        return result

    def __getattr__(self, name):
        """
        Get a bound field description attribute.  Broadly, if the attribute name is 
        "field_value" then the value corresponding to the field description is 
        retrieved from the entity, otherwise the named attribute is retrieved from 
        the field description.

        There are also a number of other special cases handled here as needed to 
        support internally-generated hyperlinks and internal system logic.
        """
        # log.info("self._key %s, __getattr__ %s"%(self._key, name))
        # log.info("self._key %s"%self._key)
        # log.info("self._entity %r"%self._entity)
        if name in ["entity_id", "entity_link", "entity_type_id", "entity_type_link"]:
            return self._entityvals.get(name, "")

        elif name == "entity_value":
            return self._entityvals
        elif name in ["field_value", "field_edit_value"]:
            return self.get_field_value()
        elif name == "field_value_key":
            return self.get_field_value_key()
        elif name == "field_value_link":
            return self.get_field_selection_link()
        elif name in ["target_value", "field_view_value"]:
            return self.get_target_value()
        elif name == "target_value_link":
            return self.get_target_link()
        elif name == "continuation_url":
            return self.get_continuation_url()
        elif name == "continuation_param":
            return self.get_continuation_param()

        elif name == "field_id":
            return self._field_description.get_field_id()
        elif name == "field_name":
            return self._field_description.get_field_name()
        elif name == "field_label":
            return self._field_description["field_label"]
        elif name == "field_help":
            return self.get_field_help_esc()
        elif name == "field_tooltip":
            return self.get_field_tooltip()
        elif name == "field_tooltip_attr":
            return self.get_field_tooltip_attr()
        elif name == "render":
            return self._field_description["field_renderer"]
        elif name == "value_mapper":
            return self._field_description["field_value_mapper"]
        elif name == "description":
            return self._field_description

        elif name == "field_value_key":
            return self._key
        elif name == "context_extra_values":
            return self._extras
        elif name == "options":
            return self.get_field_options()
        elif name == "copy":
            return self.__copy__

        # elif name == "row_field_descs":
        elif True:      # For diagnosing failed accesses...
            msg = "@@@@ Accessing bound_field.%s"%(name,)
            log.error(msg)
            log.debug("".join(traceback.format_stack()))
            assert False, msg
        return "@@bound_field.%s@@"%(name)

    def get_field_value(self):
        """
        Return field value corresponding to key from field description.
        """
        field_key = self.get_field_value_key()
        field_val = self._entityvals.get(field_key, None)
        # Allow field value to be provided via `context_extra_values` if not in entity.
        # (Currently used for 'get_view_choices_field' and 'get_list_choices_field'
        # to insert current display selection.)
        if field_val is None and self._extras and self._key in self._extras:
            field_val = self._extras[self._key]
        # If no value present, use default from field definition, or blank value
        if field_val is None:
            field_val = self._field_description.get('field_default_value', None)
            if field_val is None:
                field_val = ""
        return field_val

    def get_field_value_key(self):
        """
        Return field value key used in current entity.

        This takes account of possible use of subproperties of the property URI
        specified in the field description.  If the declared property URI is not 
        present in the entity, and a subproperty URI is present, then that 
        subproperty URI is returned.  Otherwise the declared property URI is returned.
        """
        return self._field_description.get_field_value_key(self._entityvals)

    def get_field_selection_link(self):
        """
        Return a link corresponding to a field value that is a selection from 
        an enumeration of entities (or some other value with an associated link),
        or None
        """
        choices = self._field_description['field_choices']  # OrderedDict
        v       = self.field_value
        if choices and v in choices:
            return choices[v].link
        return None

    def get_field_help_esc(self):
        """
        Return help text from field description, for use as tooltip
        """
        return escape(
            self._field_description['field_help'] or 
            "@@field help for %(field_label)s@@"%self._field_description
            )

    def get_field_tooltip(self):
        """
        Return tooltip text for displaying field popup
        """
        tooltip_text_esc = escape(
            self._field_description['field_tooltip'] or 
            (self._field_description['field_help']) or
            "@@tooltip for %(field_label)s@@"%self._field_description
            )
        return tooltip_text_esc

    def get_field_tooltip_attr(self):
        """
        Return tooltip attribute for displaying field help, or blank
        """
        tooltip_text_esc = self.get_field_tooltip()
        return ''' title="%s"'''%tooltip_text_esc if tooltip_text_esc else ''

    def get_target_value(self):
        """
        Get target value of field for view display.

        This may be different from field_value if it references another entity field
        """
        targetvals = self.get_targetvals()
        # log.debug("bound_field.get_target_value: targetvals %r"%(targetvals,))
        target_key = self._field_description.get('field_ref_field', None)
        target_key = target_key and target_key.strip()
        if targetvals is not None:
            if target_key:
                log.debug("bound_field.get_target_value: target_key %s"%(target_key,))
                target_value = targetvals.get(target_key, "(@%s)"%(target_key))
            else:
                target_value = targetvals
        elif target_key:
            target_value = self._entityvals.get(target_key, "(@%s)"%(target_key))
        else:
            target_value = self.field_value
        # log.debug("bound_field.get_target_value result: %r"%(target_value,))
        return target_value

    def get_target_link(self):
        """
        Return link corresponding to target value, or None.

        The target value is treated as a relative reference relative to 
        the field_link value.  If the target value is itself an absolute URI, 
        it will be used as-is.

        If the target value is a dictionary structure created by a URIImport or 
        FileUpload field, the resulting value links to the imported data object.

        If the field is a reference to values of another type (i.e. a selection 
        field), then the field field value is used to determine the selected entity, 
        and the entity link is used as the base URI against which the target value 
        is resolved (the entity URI referencing a directory or container).
        """
        target_base  = self.get_field_selection_link() or self.entity_link
        target_value = self.get_target_value()
        # log.debug("get_target_link: base %r, value %r"%(target_base, target_value))
        if target_base and target_value:
            if isinstance(target_value, dict) and 'resource_name' in target_value:
                target_ref = target_value['resource_name']
            elif isinstance(target_value, (str, unicode)):
                target_ref = target_value
            else:
                log.warning(
                    "bound_field.get_target_link: "+
                    "target_value must be URI string or URIImport structure; got %r"%
                      (target_value,)
                    )
                target_ref = None
            return urljoin(target_base, target_ref)
        return target_value

    def get_targetvals(self):
        """
        If field description is a reference to a target type entity or field, 
        return a copy of the referenced target entity, otherwise None.
        """
        log.debug("bound_field.get_targetvals: field_description %r"%(self._field_description,))
        target_type = self._field_description.get('field_ref_type',  None)
        target_key  = self._field_description.get('field_ref_field', None)
        log.debug("bound_field.get_targetvals: target_type %s, target_key %s"%(target_type, target_key))
        if self._targetvals is None:
            if target_type:
                # Extract entity_id and type_id; default to type id from field descr
                field_val = self.get_field_value()
                log.debug("field_val: %s"%(field_val,))
                type_id, entity_id = split_type_entity_id(self.get_field_value(), target_type)
                log.debug("bound_field.get_targetvals: type_id %s, entity_id %s"%(type_id, entity_id))
                # Get entity type info
                coll     = self._field_description._collection
                typeinfo = EntityTypeInfo(coll, type_id)
                # Check access permission, assuming user has "VIEW" permission in collection
                # This is primarily to prevent a loophole for accessing user account details
                #@@TODO: pass actual user permissions in to bound_field or field description 
                #        or extra params
                user_permissions    = ["VIEW"]
                req_permissions_map = typeinfo.get_entity_permissions_map(entity_id)
                req_permissions     = list(set( req_permissions_map[a] for a in ["view", "list"] ))
                if all([ p in user_permissions for p in req_permissions]):
                    if entity_id is None or entity_id == "":
                        raise TargetIdNotFound_Error(value=(typeinfo.type_id, self._field_description["field_name"]))
                    targetentity = typeinfo.get_entity(entity_id)
                    if targetentity is None:
                        raise TargetEntityNotFound_Error(value=(target_type, entity_id))
                    targetentity = typeinfo.get_entity_implied_values(targetentity)
                    self._targetvals = get_entity_values(typeinfo, targetentity)
                    log.debug("bound_field.get_targetvals: %r"%(self._targetvals,))
                else:
                    log.warning(
                        "bound_field.get_targetvals: target value type %s requires %r permissions"%
                        (target_type, req_permissions)
                        )
        log.debug("bound_field.get_targetvals: targetvals %r"%(self._targetvals,))
        return self._targetvals

    def get_link_continuation(self, link):
        """
        Return supplied base link with continuation parameter appended
        (if the link value is defined - i.e. not None or empty).
        """
        if link:
            link += self.get_continuation_param()
        return link

    def get_continuation_param(self):
        """
        Generate continuation parameter string for return back to the current request page
        """
        cparam = ""
        chere  = self.get_continuation_url()
        if chere:
            cparam = uri_params({'continuation_url': chere})
        return cparam

    def get_continuation_url(self):
        """
        Generate continuation URL for return back to the current request page
        """
        chere = ""
        if self._extras is None:
            log.warning("bound_field.get_continuation_url() - no extra context provided")
        else:
            requrl = self._extras.get("request_url", "")
            if requrl:
                chere  = uri_with_params(requrl, continuation_params(self._extras))
        # log.debug('bound_field.get_continuation_url %s'%(chere,))
        return chere

    def get_field_options(self):
        options = self._field_description['field_choices']      # OrderedDict
        options = ( options.values() if options is not None else 
                    [ FieldChoice('', label="(no options)") ]
                  )
        return options

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __iter__(self):
        """
        Implement iterator protocol, returning accessible value keys.
        """
        yield "entity_id"
        yield "entity_type_id"
        yield "entity_link"
        yield "entity_type_link"
        yield "field_edit_value"
        yield "field_view_value"
        yield "field_value"
        yield "field_value_key"
        yield "field_value_link"
        yield "target_value"
        yield "target_value_link"
        yield "continuation_url"
        yield "continuation_param"
        yield "description"
        yield "options"
        # Direct access to selected field descrption attributes 
        yield "field_id"
        yield "field_name"
        yield "field_label"
        yield "field_help"
        yield "field_tooltip"
        yield "field_tooltip_attr"
        return

    def as_dict(self):
        return dict( # self._field_description.items(), 
            entity=dict(self._entityvals.items()), 
            field_value=self.field_value, 
            context_extra_values=self._extras, 
            key=self._key
            )

    def __repr__(self):
        return self.fullrepr()

    def __str__(self):
        return self.shortrepr()

    def __unicode__(self):
        return self.shortrepr()

    def shortrepr(self):
        return (
            "bound_field(\n"+
            "  { 'key': %r\n"%(self._key,)+
            "  , 'val': %r\n"%(self.field_value,)+
            "  , 'field_description': %r\n"%(self._field_description,)+
            "  })")

    def fullrepr(self):
        try:
            field_view_value = self.field_view_value
        except Exception as e:
            field_view_value = str(e)
        return (
            ( "bound_field(\n"+
              "  { 'key': %r\n"+
              "  , 'field_edit_value': %r\n"+
              "  , 'field_view_value': %r\n"+
              "  , 'description': %r\n"+
              "  , 'entity_vals': %r\n"+
              "  })\n"
            )%( self._key
              , self.field_edit_value
              , field_view_value 
              , self._field_description
              , dict(self._entityvals.items())
              )
            )

    def htmlrepr(self):
        return (
            "<ul>"+
            "<li>key: %s</li>"%(self._key,)+
            "<li>val: %s</li>"%(self.field_value,)+
            "<li>field_description: %r</li>"%(self._field_description,)+
            "</ul>"
            )

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def get_entity_values(typeinfo=None, entity=None, entity_id=None, action="view"):
    """
    Returns an entity values dictionary for a supplied entity, suitable for
    use with a bound_field object.
    """
    if not entity_id:
        entity_id = entity.get_id()
    type_id    = entity.get_type_id()
    entityvals = entity.get_values().copy()
    entityvals['entity_id']        = entity_id
    entityvals['entity_link']      = entity.get_view_url_path()
    # log.info("type_id %s"%(type_id))
    entityvals['entity_type_id']   = type_id
    if action == "copy":
        # Allocate new entity Id and lose values based on original Id 
        # when performing a copy operation.
        # entity_id = typeinfo.entityclass.allocate_new_id(typeinfo.entityparent)
        # log.info("@@ copy new entity_id %s"%entity_id)
        # entityvals['entity_id'] = entity_id
        entityvals.pop('entity_link', None)
        entityvals[ANNAL.CURIE.id] = entity_id
        entityvals.pop(ANNAL.CURIE.uri, None)
    if typeinfo and typeinfo.recordtype:
        entityvals['entity_type_link'] = typeinfo.recordtype.get_view_url_path()
    # else:
    #     log.error("get_entity_values: No recordtype: typeinfo %r"%(typeinfo,))
    #     log.error("get_entity_values: No recordtype: entity id %s/%s"%(type_id,entity_id))
    #     log.error("get_entity_values: No recordtype: entity %r"%(entity,))
    #     traceback.print_stack()
    return entityvals

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
