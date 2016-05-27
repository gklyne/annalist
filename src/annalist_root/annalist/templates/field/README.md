# Field rendering templates

This directory contains templates for rendering different types of field value in different contexts.

The template name format is:

    annalist_<context>_<value-type>

where `<context>` is one of:

* `edit` - a template used to render an element that can be used to display and edit a field value
* `view` - a template used for an element to display a value without options to change it
* [`grid` - used to render an element to display a field value in a grid NOT YET IMPLEMENTED]

and `<value-type>` is indicative of the type of value rendered by the template.

The selection of field templates for rendering is handled by module views.fields.find_renderers.

## Notes

* http://stackoverflow.com/questions/1480588/input-size-vs-width
