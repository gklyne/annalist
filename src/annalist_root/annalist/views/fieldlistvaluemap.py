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

from annalist.views.fielddescription    import FieldDescription
from annalist.views.fieldvaluemap       import FieldValueMap
from annalist.views.repeatdescription   import RepeatDescription
from annalist.views.repeatvaluesmap     import RepeatValuesMap
from annalist.views.subgroupvaluemap    import SubgroupValueMap

class FieldListValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.
    """

    def __init__(self, coll, fields, view_context):
        """
        Define an entry to be added to an entity view value mapping table,
        corresponding to a list of field descriptions.

        collection      is a collection from which data is being rendered.
        fields          list of field descriptions from a view definition, each
                        of which is a dictionary with the field description from 
                        a view or list description.
        view_context    is a dictionary of additional values that may ube used in assembling
                        values to be used when rendering the fields.

        NOTE: The form rendering template iterates over the context field values to be 
        added to the form display.  The constructor for this object appends the current
        field to a list of field value mappings in context field 'fields'.
        """
        self.fd = []
        self.fs = []
        for f in fields:
            # log.info("\n********\nFieldListValueMap: field %r\n*********"%(f))
            if ANNAL.CURIE.field_id in f:
                field_context = FieldDescription(coll, f, view_context)
                log.debug("FieldListValueMap: field_id %s, field_name %s"%
                    (field_context['field_id'], field_context['field_name'])
                    )
                self.fd.append(field_context.get_structure_description())
                self.fs.append(FieldValueMap(f=field_context))
            elif ANNAL.CURIE.repeat_id in f:
                repeat_context  = RepeatDescription(f)  # For repeat controls, button labels, etc.
                repeatfieldsmap = FieldListValueMap(coll, f[ANNAL.CURIE.repeat], view_context)
                repeatvaluesmap = RepeatValuesMap(repeat=repeat_context, fields=repeatfieldsmap)
                self.fd.append(repeatvaluesmap.get_structure_description())
                self.fs.append(repeatvaluesmap)
            else:
                assert False, "Unknown/unsupported field values:"+repr(f)
        return

    def __repr__(self):
        return (
            "FieldListValueMap.fs: %r\n"%(self.fs)
            )

    def map_entity_to_context(self, entityvals, extras=None):
        listcontext = []
        for f in self.fs:
            fv = f.map_entity_to_context(entityvals, extras=extras)
            listcontext.append(fv)
        return { 'fields': listcontext }

    def map_form_to_entity(self, formvals):
        vals = {}
        for f in self.fs:
            vals.update(f.map_form_to_entity(formvals))
        return vals

    def map_form_to_entity_repeated_items(self, formvals, prefix):
        """
        Extra helper method used when mapping a repeated list of fields items to 
        repeated entity values.  Returns values corresponding to a single repeated 
        set of fields.  The field names extracted are constructed using the supplied 
        prefix string.

        Returns a dictionary of repeated field values found using the supplied prefix.

        Returns None if no prefixed field value exists, which may be used as a loop
        termination condition.
        """
        vals = {}
        prefix_seen = False
        for f in self.fs:
            v = f.map_form_to_entity_repeated_item(formvals, prefix)
            if v is not None:
                vals.update(v)
                prefix_seen = True
        return vals

    def get_structure_description(self):
        """
        Helper function returns list of field description information
        """
        return (
            { 'field_type':     'FieldListValueMap'
            , 'field_list':     self.fd 
            })

# End.
