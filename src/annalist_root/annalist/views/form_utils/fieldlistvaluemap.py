"""
Annalist class for processing a list of field mappings for conversion between
entity values context values and form data.

A FieldListValueMap is an object that can be inserted into an entity view value
mapping table to process the corresponding list of fields.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# import collections

from django.conf                        import settings

from annalist.identifiers               import RDFS, ANNAL

from annalist.views.form_utils.fielddescription import FieldDescription, field_description_from_view_field
from annalist.views.form_utils.fieldvaluemap    import FieldValueMap
from annalist.views.form_utils.repeatvaluesmap  import RepeatValuesMap

class FieldListValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.
    """

    def __init__(self, c, coll, fields, view_context):
        """
        Define an entry to be added to an entity view value mapping table,
        corresponding to a list of field descriptions.

        c               name of field used for this value in display context
        collection      is a collection from which data is being rendered.
        fields          list of field descriptions from a view definition, each
                        of which is a dictionary with the field description from 
                        a view or list description.
        view_context    is a dictionary of additional values that may be used in
                        assembling values to be used when rendering the fields.
                        Specifically, this are currently used in calls of
                        `EntityFinder` for building filtered lists of entities
                        used to populate enumerated field values.  Fields in
                        the supplied context currently used are `entity` for the
                        entity value being rendered, and `view` for the view record
                        used to render that value
                        (cf. GenericEntityEditView.get_view_entityvaluemap)

        The form rendering template iterates over the field descriptions to be
        added to the form display.  The constructor for this object appends the 
        current field to a list of field value mappings, with a `map_entity_to_context`
        method that assigns a list of values from the supplied entity to a context 
        field named by parameter `c`.
        """
        self.c      = c         # Context field name for values mapped from entity
        self.fd     = []        # List of field descriptions
        self.fm     = []        # List of field value maps
        properties  = None      # Used to detect and disambiguate duplicate properties
        for f in fields:
            log.debug("FieldListValueMap: field %r"%(f,))
            # @@TODO: check for common logic here and FieldDescription field_group_ref processing
            field_desc = field_description_from_view_field(coll, f, view_context)
            properties = field_desc.resolve_duplicates(properties)
            self.fd.append(field_desc)
            # @@TODO: generate padding if needed
            if field_desc.is_repeat_group():
                repeatfieldsmap = FieldListValueMap('_unused_fieldlistvaluemap_', 
                    coll, field_desc.group_view_fields(), view_context
                    )
                repeatvaluesmap = RepeatValuesMap(c='_fieldlistvaluemap_',
                    f=field_desc, fieldlist=repeatfieldsmap
                    )
                self.fm.append(repeatvaluesmap)
            else:
                self.fm.append(FieldValueMap(c='_fieldlistvaluemap_', f=field_desc))
        return

    def __repr__(self):
        return (
            "FieldListValueMap.fm: %r\n"%(self.fm)
            )

    def map_entity_to_context(self, entityvals, context_extra_values=None):
        listcontext = []
        for f in self.fm:
            fv = f.map_entity_to_context(entityvals, context_extra_values=context_extra_values)
            listcontext.append(fv['_fieldlistvaluemap_'])
        return { self.c: listcontext }

    def map_form_to_entity(self, formvals, entityvals):
        """
        Use form data to update supplied entity values
        """
        for f in self.fm:
            f.map_form_to_entity(formvals, entityvals)
        return entityvals

    def map_form_to_entity_repeated_items(self, formvals, entityvals, prefix):
        """
        Extra helper method used when mapping a repeated list of fields items to 
        repeated entity values.  Returns values corresponding to a single repeated 
        set of fields.  The field names extracted are constructed using the supplied 
        prefix string.

        Returns a dictionary of repeated field values found using the supplied prefix.
        """
        for f in self.fm:
            f.map_form_to_entity_repeated_item(formvals, entityvals, prefix)
        return entityvals

    def get_structure_description(self):
        """
        Helper function returns list of field description information
        """
        return (
            { 'field_type':     'FieldListValueMap'
            , 'field_list':     self.fd 
            })

    def get_field_description(self):
        return None

# End.
