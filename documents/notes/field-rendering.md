# Annalist field rendering

## Notes for using object renderers rather than templates

Use of template files vs. use of inline template text in renderer class

- Need to support edit/view/item/head uses of field, probably via class inheritance structure
- Inline template text should be more efficient as it avoids repeated reading of template files
- Inline template text keeps value mapping logioc with template logic
- Inline templates may be harder to style effectively; maybe read HTML from file on first use?


## Notes for documentation

Annalist remndering of fields on a form goes through several pieces.  (At some stage, the logic should be brought into a less dispersed state.)

* `annalist/templates/`:  main template maps from main context to form
* `annalist/templates/field/`:  sub template maps from field context to form
* `views/`: view function sets up main template;  central to the view logic for data driven views is a "mapping table" that maps values between entities, form data and contexts.  Some of the logic for this is in `entityeditbase.py`.  Modules `defaultedit.py` and `defaultlist.py` contain much of the core logoic for re cord editing forms and list displays respectively. (@@these should be be reorganized to group the logic more sanely)
    * Mapping table entries are objects with methods for performing the various mappings that may be required. (@@move these to fields?)
        * `annalist/views/simplevaluemap.py`: mapping table entry for simple entiry values:  provides direct mapping between a set of entity values, a form data dictionary and top-level entries in a view context.  Static forms can be generated using just this type of mapping entry
        * `annalist/views/fieldvaluemap.py`: mapping table entries for a data-defined form field.  See also: `views.entityeditbase.get_field_context`, `fields.render_utils.bound_field`, `fields.render_utils.get_view_renderer`, `fields.render_utils.get_edit_renderer`, etc.
        * `annalist/views/grouprepeatmap`: mapping repeated fields for list and grid views.  Provides for repetition of a specified mapping table for each of a list of entities.
    * `views.entityeditbase.get_form_entityvaluemap` returns the entity/value map corresponding to a record view (e.g. see `sitedata/views/Default_view`).
    * `views.entityeditbase.get_list_entityvaluemap` returns the entity/value map corresponding to a list view (e.g. see `sitedata/lists/Default_list`).
* `fields/`: the intent is that modukles in this directory can be used in place of sub-templates to render field values.  (@@make sub-dir of `views/`?)  This reflects a capability to be introduced with a forthcoming Django release:
    > Changed in Django Development version: The variable may also be any object with a render() method that accepts a context. This allows you to reference a compiled Template in your context. 
    - https://docs.djangoproject.com/en/dev/ref/templates/builtins/#include
* `fields/render_utils.py`: this module contains a hodge-podge of functions to support form rendering:
    * `fields/render_utils.bound_field`: binds a field context description (see `views.entityeditbase.get_field_context`) to an entity value and returns various values that can be referenced in a field rendering template.  (This could be replaced by more specialized field rendering classes.)
    * `fields/render_utils.get_view_renderer`: returns field renderer (currently a template name string) for a value display-only field.  Supply the `annal:field_render` value from a field definition (see `sitedata/` and user-defined forms data)
    * `fields/render_utils.get_edit_renderer`: returns field renderer for an editable value field.
    * `fields/render_utils.get_head_renderer`: returns field renderer for list heading field.
    * `fields/render_utils.get_edit_renderer`: returns field renderer for a list item field.
* `sitedata/`: contains data for built-in data-defined forms.
    * `sitedata/types/`: built-in RecordType descriptions (currently None)
    * `sitedata/views/`: built-in record edit/display view form descriptions.
    * `sitedata/lists/`: built-in record list/grid view form descriptions.
    * `sitedata/fields/`: fields used by built-in view descriptions, and maybe others.
    * `sitedata/enumertions/`: define enumerated values that can be referenced by form fields (e.g. for drop-down selections) (@@not yet used)

