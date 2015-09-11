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

from annalist.exceptions    import TargetIdNotFound_Error, TargetEntityNotFound_Error
from annalist.identifiers   import RDFS, ANNAL
from annalist.util          import split_type_entity_id

from annalist.models.entitytypeinfo         import EntityTypeInfo
from annalist.models.entity                 import EntityRoot

from annalist.views.uri_builder             import (
    uri_params, uri_with_params, continuation_params
    )
from annalist.views.form_utils.fieldchoice  import FieldChoice


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

        elif name in ["field_value", "field_edit_value"]:
            return self.get_field_value()
        elif name == "field_value_link":
            return self.get_field_link()
        elif name == "field_value_link_continuation":
            return self.get_link_continuation(self.get_field_link())

        elif name in ["target_value", "field_view_value"]:
            return self.get_target_value()
        elif name == "target_value_link":
            return self.get_target_link()
        elif name == "target_value_link_continuation":
            return self.get_link_continuation(self.get_target_link())

        elif name == "entity_link_continuation":
            return self.entity_link+self.get_continuation_param()
        elif name == "entity_type_link_continuation":
            return self.entity_type_link+self.get_continuation_param()
        elif name == "continuation_url":
            return self.get_continuation_url()
        elif name == "continuation_param":
            return self.get_continuation_param()
        elif name == "field_description":
            return self._field_description
        elif name == "field_value_key":
            return self._key
        elif name == "context_extra_values":
            return self._extras
        elif name == "options":
            return self.get_field_options()
        #@@
        # elif name == "field_placeholder":
        #     return self._field_description.get('field_placeholder', "@@bound_field.field_placeholder@@")
        #@@
        else:
            # log.info("bound_field[%s] -> %r"%(name, self._field_description[name]))
            return self._field_description.get(name, "@@bound_field.%s@@"%(name))

    def get_field_value(self):
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

    def get_field_link(self):
        # Return link corresponding to field value that is a selection from an enumeration of entities
        # (or some other value with an associated link), or None
        #@@
        # links = self._field_description['field_choice_links']
        # v     = self.field_value
        # if links and v in links:
        #     return links[v]
        #@@
        choices = self._field_description['field_choices']  # OrderedDict
        v       = self.field_value
        if choices and v in choices:
            return choices[v].link
        return None

    def get_target_value(self):
        """
        Get target value of field for view display.

        This may be different from field_value if it references another entity field
        """
        targetvals = self.get_targetvals()
        log.debug("bound_field.get_target_value: targetvals %r"%(targetvals,))
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
        log.debug("bound_field.get_target_value result: %r"%(target_value,))
        return target_value

    def get_target_link(self):
        """
        Return link corresponding to target value, or None.

        The target value is treated as a relative reference relative to the field_link value.
        If the target value is itself an absolute URI, it will be used as-is.

        If the target value is a dictionary structure created by a URIImport or FileUpload field, 
        the resulting value links to the imported data object.
        """
        target_base  = self.get_field_link() or self.entity_link
        target_value = self.get_target_value()
        log.debug("get_target_link: base %r, value %r"%(target_base, target_value))
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
                type_id, entity_id = split_type_entity_id(self.get_field_value(), target_type)
                # Get entity type info
                #@@TODO: eliminate site param...
                coll     = self._field_description._collection
                typeinfo = EntityTypeInfo(coll.get_site(), coll, type_id)
                # Check access permission, assuming user has "VIEW" permission in current collection
                # This is primarily to prevent a loophole for accessing user account details
                #@@TODO: pass actual user permissions in to bound_field or field description or extra params
                user_permissions = ["VIEW"]
                req_permissions  = list(set( typeinfo.permissions_map[a] for a in ["view", "list"] ))
                if all([ p in user_permissions for p in req_permissions]):
                    if entity_id is None or entity_id == "":
                        raise TargetIdNotFound_Error(value=(typeinfo.type_id, self.field_name))
                    targetentity = typeinfo.get_entity(entity_id)
                    if targetentity is None:
                        raise TargetEntityNotFound_Error(value=(target_type, entity_id))
                    self._targetvals = get_entity_values(typeinfo, targetentity)
                    log.debug("bound_field.get_targetvals: %r"%(self._targetvals,))
                else:
                    log.warning(
                        "bound_field.get_targetvals: target value type %s requires %r permissions"%
                        (target_type, req_permissions)
                        )
                # # Get entity type info
                # #@@TODO: eliminate site param...
                # coll           = self._field_description._collection
                # targettypeinfo = EntityTypeInfo(coll.get_site(), coll, target_type)
                # # Check access permission, assuming user has "VIEW" permission in current collection
                # # This is primarily to prevent a loophole for accessing user account details
                # #@@TODO: pass actual user permissions in to bound_field or field description or extra params
                # user_permissions = ["VIEW"]
                # req_permissions  = list(set( targettypeinfo.permissions_map[a] for a in ["view", "list"] ))
                # if all([ p in user_permissions for p in req_permissions]):
                #     target_id    = self.get_field_value()
                #     if target_id is None or target_id == "":
                #         raise TargetIdNotFound_Error(value=(targettypeinfo.type_id, self.field_name))
                #     targetentity = targettypeinfo.get_entity(target_id)
                #     if targetentity is None:
                #         raise TargetEntityNotFound_Error(value=(targettypeinfo.type_id, target_id))
                #     self._targetvals = get_entity_values(targettypeinfo, targetentity)
                #     log.debug("bound_field.get_targetvals: %r"%(self._targetvals,))
                # else:
                #     log.warning(
                #         "bound_field.get_targetvals: target value type %s requires %r permissions"%
                #         (target_type, req_permissions)
                #         )
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
        log.debug('bound_field.get_continuation_url %s'%(chere,))
        return chere

    def get_field_options(self):
        #@@
        # options = self._field_description['field_choice_labels']  # OrderedDict
        # options = options.values() if options is not None else ["(no options)"]
        #@@
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
        yield "entity_link_continuation"
        yield "entity_type_link"
        yield "entity_type_link_continuation"
        yield "field_edit_value"
        yield "field_view_value"
        yield "field_value"
        yield "field_value_link"
        yield "field_value_link_continuation"
        yield "target_value"
        yield "target_value_link"
        yield "target_value_link_continuation"
        yield "continuation_url"
        yield "continuation_param"
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
            ( "bound_field(\n"+
              "  { 'key': %r\n"+
              "  , 'field_edit_value': %r\n"+
              "  , 'field_view_value': %r\n"+
              "  , 'field_descr': %r\n"+
              "  , 'entity_vals': %r\n"+
              "  })\n"
            )%( self._key
              , self.field_edit_value
              , self.field_view_value 
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

def get_entity_values(typeinfo=None, entity=None, entity_id=None):
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
    #@@ typeinfo   = EntityTypeInfo(displayinfo.site, displayinfo.collection, type_id)
    if typeinfo and typeinfo.recordtype:
        entityvals['entity_type_link'] = typeinfo.recordtype.get_view_url_path()
    # This is red herring:  working version also has this
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
