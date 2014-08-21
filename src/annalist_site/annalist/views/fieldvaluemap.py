"""
Annalist class for processing a FieldValueMap in an annalist view value mapping table.

A FieldValueMap accepts a context field identifier and a field description structure,
and generates context values to drive rendering of that field in a form.
The template used is expected to iterate over the fields and render each one, e.g.:

    {% for field in fields %}
    {% include field.field_render_edit %}
    {% endfor %}

The iterated values of `field` provide additional values for the field rendering template,
including the value of the entity field to be presented.  Field descriptions are bound 
to entity values as the context elements are generated by this class. 

Entity and form field names used for this value are obtained from the field definition;
i.e. they are defined indirectly to support data-driven form generation.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings

from annalist.views.fields.render_utils import bound_field

class FieldValueMap(object):
    """
    Define an entry in an entity value mapping table corresponding to a
    field value and description, which is added to a list of such fields
    in the indicated context variable.

    NOTE: select fields are handled by having a special field 'options' passed
    in the default value supplied, which is picked out and handled specially
    in the bound_field class.

    f       field description structure (cf. `FieldDescription`)

    NOTE: The form rendering template iterates over the context field values to be 
    added to the form display.  The constructor for this object appends the current
    field to a list of field value mappings at the indcated context field.
    """

    def __init__(self, f=None):
        self.f = f
        self.e = f['field_property_uri']    # entity data key
        self.i = f['field_name']            # field data key
        return

    def map_entity_to_context(self, entityvals, extras=None):
        """
        Returns a dictionary of values to be added to the display context under construction
        """
        options = ["(no options)"]
        options_choices = self.f.get('field_choices', None)
        options_key     = self.f.get('field_options_valkey', None)
        if options_choices:
            options = options_choices
        elif options_key:
            if extras and options_key in extras:
                options = extras[options_key]
            else:
                options = ['(missing options)']
        # log.info("map entity %s to context %s, vals %r"%(self.e, self.i, entityvals))
        # log.info("map_entity_to_context: bound_field: extras %r"%(extras,))
        boundfield = bound_field(
            field_description=self.f, 
            entityvals=entityvals, key=self.f['field_property_uri'],
            options=options,
            extras=extras
            )
        return boundfield

    def map_form_to_entity(self, formvals):
        entityvals = {}
        if self.e:
            log.debug("FieldValueMap.map_form_to_entity %s, %r"%(self.e, formvals))
            v = formvals.get(self.i, None)
            if v:
                entityvals[self.e] = v
        return entityvals

    def map_form_to_entity_repeated_item(self, formvals, prefix):
        """
        Extra helper method used when mapping repeated field items to repeated entity values.
        The field name extracted is constructed using the supplied prefix string.

        Returns None if the prefixed value does not exist, which may be used as a loop
        termination condition.
        """
        # log.info("Form->entity: prefix %s, fieldname %s"%(prefix, self.i))
        v = formvals.get(prefix+self.i, None)
        if v:
            return {self.e: v}
        return None

    def get_structure_description(self):
        return (
            { 'field_type':     'FieldValueMap'
            , 'field_descr':    self.f
            , 'entity_field':   self.e
            , 'form_field':     self.i
            })

# End.