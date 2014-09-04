# Field rendering templates

This directory contains templates for rendering different types of field value in different contexts.

The template namne format is:

    annalist_<context>_<value-type>

where `<context>` is one of:

* `edit` - a template used to render an element that can be used to display and edit a field value
* `view` - a template used for an element to display a value without options to change it
* `head` - used to render an element to display a list heading for a field
* `item` - used to render an element to display a field value in a list
* `grid` - used to render an element to display a field value in a grid

and `<value-type>` is a value used in a field definition `annal:field_value_type` vcalue (see `sitedata/fields` for field definitions by field id).
