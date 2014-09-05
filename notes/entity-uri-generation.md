# Handling of entity URI (cf. for Type records)

When creating new type, URI should be based on ID entered, but possible to override by user.  Set URI when saving rather than when creating? (Partially works).

(Changes made as described below)

## Current processing and thoughts

Uses annal:uri property, which is overloaded as an arbitrary entity locator, which in turn gets some special treatment.  This means the type identifier is bound to its Annalist location, which is OK as a default but not always what is required.

Could use a different property URI, and think about generic way to default value on save based on other fields?

Type URI processing involves the following methods:

- entityvaluemap.map_form_data_to_values
- kmap.map_form_to_entity(form_data)
- Fieldvaluemap.map_form_to_entity looks like the place to intervene; self.f is a field description.
- FieldDescription contains information extracted from _field entity on disk.  Could use special form of 'field_default_value', which is currently used by bound_field in views.fields.render_utils?

## Proposed solution

This proposal generalizes the handling of entity location and identifiers to entities other than type descriptions.

    1. Rename annal:uri to annal:url with current special-case processing logic (to emphasize its role as locator).
    2. Remove any saved 'annal:uri' values in sitedata if they are also locators.
    3. Introduce a new 'annal:uri' field which defaults to annal:url when retrieved, but which may be overridden by user input (if the form used allows this).  On saving, if 'annal:uri' is the same as 'annal:url', don't save it (so that if the entity itself is renamed, its 'annal:uri' value will update accordingly)

For copy operations, the annal:uri field should be reset as the form is rendered.
