"""
Define class to represent a field description when processing an entity view.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.models.recordfield        import RecordField
from annalist.models.entitytypeinfo     import EntityTypeInfo

from annalist.views.fields.render_utils import get_edit_renderer, get_view_renderer
from annalist.views.fields.render_utils import get_head_renderer, get_item_renderer
from annalist.views.fields.render_placement import (
    get_placement_classes
    )

class FieldDescription(object):
    """
    Describes an entity view field used with entity-value maps, and methods to perform 
    manipulations involving the field description.
    """

    def __init__(self, collection, field):
        """
        Creates a field description value to use in a context value when
        rendering a form.  Values defined here are mentioned in field
        rendering templates.

        The FieldDescription object behaves as a dictionary containing the various field attributes.

        collection  is a collection object to which the field is considered to belong.
        field       is a dictionary with the field description from a view or list description,
                    containing a field id and placement values.
        """
        field_id    = field['annal:field_id']                   # Field ID slug in URI
        recordfield = RecordField.load(collection, field_id, collection._parentsite)
        if recordfield is None:
            raise ValueError("Can't retrieve definition for field %s"%(field_id))
        field_name      = recordfield.get("annal:field_name", field_id)   # Field name in form
        field_placement = get_placement_classes(
            field['annal:field_placement'] or recordfield.get('annal:field_placement', "")
            )
        log.debug("recordfield   %r"%(recordfield and recordfield.get_values()))
        # log.info("FieldDescription: field['annal:field_placement'] %s"%(field['annal:field_placement']))
        # log.info("FieldDescription: field_placement %r"%(get_placement_classes(field['annal:field_placement']),))
        self._field_context = (
            { 'field_id':               field_id
            , 'field_name':             field_name
            , 'field_placement':        field_placement
            , 'field_render_head':      get_head_renderer(recordfield.get('annal:field_render', ""))
            , 'field_render_item':      get_item_renderer(recordfield.get('annal:field_render', ""))
            , 'field_render_view':      get_view_renderer(recordfield.get('annal:field_render', ""))
            , 'field_render_edit':      get_edit_renderer(recordfield.get('annal:field_render', ""))
            , 'field_label':            recordfield.get('rdfs:label', "")
            , 'field_help':             recordfield.get('rdfs:comment', "")
            , 'field_value_type':       recordfield.get('annal:value_type', "")
            , 'field_placeholder':      recordfield.get('annal:placeholder', "")
            , 'field_default_value':    recordfield.get('annal:default_value', None)
            , 'field_property_uri':     recordfield.get('annal:property_uri', "")
            , 'field_options_valkey':   recordfield.get('annal:options_valkey', None)
            , 'field_options_typeref':  recordfield.get('annal:options_typeref', None)
            , 'field_choices':          None
            })
        if self._field_context['field_options_typeref']:
            typeinfo = EntityTypeInfo(collection._parentsite, collection, self._field_context['field_options_typeref'])
            self._field_context['field_choices'] = typeinfo.enum_entity_ids(usealtparent=True)
            # log.info(list(self._field_context['field_choices']))
        # log.info("FieldDescription: %s"%field_id)
        # log.info("FieldDescription.field %r"%field)
        # log.info("FieldDescription.field_context %r"%(self._field_context,))
        # log.info("FieldDescription.field_placement %r"%(self._field_context['field_placement'],))
        return

    def get_structure_description(self):
        """
        Helper function returns field description information
        (field selector and placement).
        """
        return (
            { 'field_id':           self._field_context['field_id']
            , 'field_placement':    self._field_context['field_placement']
            , 'field_property_uri': self._field_context['field_property_uri']
            })

    def __repr__(self):
        return (
            "FieldDescription("+
            "  { 'field_id': %r\n"%(self._field_context["field_id"])+
            "  , 'field_name': %r\n"%(self._field_context["field_name"])+
            "  , 'field_property_uri': %r\n"%(self._field_context["field_property_uri"])+
            "  })"
            )
        # return repr(self._field_context)

    # Define methods to facilitate access to values using dictionary operations
    # on the FieldDescription object

    def keys(self):
        """
        Return collection metadata value keys
        """
        return self._field_context.keys()

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._field_context.items()

    def get(self, key, default):
        """
        Equivalent to dict.get() function
        """
        return self[key] if self._field_context and key in self._field_context else default

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._field_context[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._field_context[k] = v
        return

    def __iter__(self):
        """
        Iterator over dictionary keys
        """
        for k in self._field_context:
            yield k
        return

# End.
