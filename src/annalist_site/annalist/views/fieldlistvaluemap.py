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

from annalist.fields.render_utils       import bound_field

from annalist.views.fielddescription    import FieldDescription
from annalist.views.fieldvaluemap       import FieldValueMap


class FieldListValueMap(object):
    """
    Define an entry to be added to an entity view value mapping table,
    corresponding to a list of field descriptions.

    NOTE: select fields are handled by having a special field 'options' passed
    in the default value supplied, which is picked out and handled specially
    in the bound_field class.

    coll    is the collection object holding the field definitions
    fields  list of FieldDescription values.
    c       key in context which receives a list of field values

    NOTE: The form rendering template iterates over the context field values to be 
    added to the form display.  The constructor for this object appends the current
    field to a list of field value mappings at the indcated context field.
    """

    def __init__(self, coll, fields, c=None):
        self.c  = c
        self.fs = []
        for f in fields:
            log.debug("FieldListValueMap: field %r"%(f))
            if 'annal:field_id' in f:
                field_context = FieldDescription(coll, f)
                log.debug("FieldListValueMap: field_id %s, field_name %s"%
                    (field_context['field_id'], field_context['field_name'])
                    )
                self.fs.append(
                    FieldValueMap(c=self.c, f=field_context)
                    )
            elif 'annal:repeat_id' in f:
                repeat_context = RepeatDescription(f)
                repeatmap = []
                self.get_fields_entityvaluemap(repeatmap, f['annal:repeat'])
                # @@TODO: use repeat_id value for context identifier?  
                #         (Need to ensure it can be recovered later when rendering.)
                self.fs.append(
                    RepeatValueMap(c='repeat', e="annal:view_fields", r=repeatmap, f=repeat_context)
                    )
            else:
                assert False, "Unknown/unsupportred field values:"+repr(f)
        return

    def map_entity_to_context(self, entityvals, extras=None):
        listcontext = {}
        if self.c:
            listcontext[self.c] = []
            for f in self.fs:
                fv = f.map_entity_to_context(entityvals, extras=extras)
                listcontext[self.c].append(fv[self.c])
        return listcontext

    def map_form_to_context(self, formvals, extras=None):
        listcontext = {}
        if self.c:
            listcontext[self.c] = []
            for f in self.fs:
                fv = f.map_form_to_context(formvals, extras=extras)
                listcontext[self.c].append(fv[self.c])
        return listcontext

    def map_form_to_entity(self, formvals):
        vals = {}
        for f in self.fs:
            vals.update(f.map_form_to_entity(formvals))
        return vals

# End.