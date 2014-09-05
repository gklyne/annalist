# Rendering of entity type on form; rationalize rendering logic

(Changes made as described below)

## Form field rendering for GET

  get:

        entity = self.get_entity(viewinfo.entity_id, typeinfo, action, entity_initial_values)

        return self.form_render(viewinfo, entity, add_field, continuation_uri)

  form_render(self, viewinfo, entity, add_field, continuation_uri):

        viewcontext = entityvaluemap.map_value_to_context(entity, ...)

So, in this case, values are provided as a genuine entity with proper entity_type, etc.

## Form re-rendering for POST

  post:
        return self.form_response(
            viewinfo,
            entity_id, orig_entity_id, 
            entity_type, orig_entity_type,
            messages, context_extra_values
            )

  form_response(self, viewinfo, 
                entity_id, orig_entity_id, entity_type, orig_entity_type, 
                messages, context_extra_values):

        return self.form_re_render(entityvaluemap, form_data, context_extra_values, ...)

        form_context = entityvaluemap.map_form_data_to_context(form_data, ...)

  map_form_data_to_context(self, form_data, **kwargs):

        entityvals = self.map_form_data_to_values(form_data)

        context = self.map_value_to_context(entityvals, **kwargs)

In this case, values are provided as a dictionary without proper entity_type, etc.

## Solution

Simplify bound_field so that it works with entity values supplied as a dictionary only.

Vaues may be 1:1 with stored entity values keyed by CURIE or URI, or may be special keys
that access entity parameters unrelated to the field being rendered, or field parameters
unrelated to the entity being processed.

A special case is 'field_value' which uses a field definition to select a value from
the entity data.  Special cases of field_value are 'entity_id', 'entity_type[_id?]' and 'annal:type'.  The first two are clearly bound to the entity access logic.  The third works as a synonym for 'entity_type', so that when an entity is rendered its type drop-down is initialized to the stored 'annal:type' value.

In code paths that supply values from an entity, the special fields should be added to the
entity values dictionary so they can be referenced directly.  All code paths should add 
special values to the entity values dictionary as needed.

(later) Options should be re-worked as a more generic entity reference that enumerates 
the target entity ids on the fly as required, using type information in the field definition.

