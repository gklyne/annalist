# Adding a new field type to Annalist

Annalist field types determine the kinds of data that can be stored in an entity field, and how that data is prersented for display and editing.  The User interface for display and editing uses dynamically generated HTML.

Files referred to below are in subdirectories of `src/annalist-root/` of the source code tree as stored in GitHub.

HTML for view fields is generated through the following steps:

1. A view references a number of fields, which are defined in `annalist/sitedata/fields/`.  Each field is associated with a named directory containing a file `field_meta.jsonld`, which defines properties of the field (the presentation of which is defined in `annalist/sitedata/views/Field_view/view_meta.jsonld`).  The property named `annal:field_render_type` defines a render type for the field.

2. When generating HTML for a view, the field render type is translated by module `annalist/views/fields/render_utils.py` into a Django renderer object suitable for the context in which the field appears (view. edit, list, etc.).  This renderer object can be referenced by a Django template `%include` template tag (cf. [Django "include" documentation](https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#include) - the capability to include an object with a render method was introduced in Django 1.7).

3. The master template (`annalist/templates/annalist_entity_list.html`, `annalist/templates/annalist_entity_view.html` or `annalist/templates/annalist_entity_edit.html`), or the `RepeatGroup` renderer (`annalist/views/fields/render_repeatgroup.py` invoke the field renderer at the apropriate point on the page).

New field types can be defined in one of the following ways:

* as a set of Django templates.  Simple data types, like text fields, can be handled directly by Django templates and no new rendering logic needs to be created.  For example, see `annalist/templates/field/annalist_view_text.html` and `annalist/templates/field/annalist_edit_text.html`.

* as a new rendering module implemented in Python.  For example, see `annalist/views/fields/render_tokenset.py`.


## Defining a template-based render type

1.  Choose a short name string for the render type that does not clash with any values already defined in `annalist/views/fields/render_utils`.  Most of the defined render types appear in the tables at the start of the module (`_field_view_files`, `_field_edit_files` and `_field_get_renderer_functions`), but others may be mentioned directly in the functions that follow (e.g. `RepeatGroup`, `RepeatGroupRow` and `RepeatListRow` are mapped directly in function `get_view_renderer`)

2.  Define two new template files to generate HTML for viewing and editing values of the new field render type in directory `annalist/templates/field/`.  These are conventionally named `annalist_<type>_view.html` and `annalist_<type>_edit.html` respectively.

3.  Edit module `annalist/views/fields/render_utils.py` and add the template filenames to the dictionaries `_field_view_files` and `_field_view_files`.

When the template is rendered, Annalist provides a context value with various values that can be used by the renderer, the most important of which are:

* `{{field.field_value}}` is the field value to be displayed

* `{{field.field_name}}` and `{{repeat_prefix}}`: when inputting/editing values these define the name used to identify the HTML form input field.  They should always be used together so that if a fielkd is repeated on a form each instance gets a different form value name.

* `{{field.field_placeholder}}` is a string that is used as a placeholder in an unspecified input field.  The exact way this is used will depend on the HTML used, but for a simple text input field it is displayed in the field as a prompt to the user until some actual value is entered.

The available field values are drawn from the field definition and from the entity whose value is displayed, and are defined by the module `annalist/views/fields/bound_field.py`, method `bound_field.__getattr__`.  The `repeat_prefix` value is defined by `annalist/views/fields/render_repeatgroup.py`, in the `render` method.

For example, the following template renders a simple text input field:

    <input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}" 
           placeholder="{{field.field_placeholder}}"
           value="{{field.field_value}}"/>

This example displays an entity identifier as a hyperlink:

    <a href="{{field.entity_type_link_continuation}}">{{field.field_value}}</a>

NOTE: future developments may implement a separate directory for installation- or collection-dependent value rendering templates, to facilitate software updates without trashing local adaptations.


## Defining a class-based render type

For rendering fields that cannot be handled by Django templates, new rendering code can be added to Annalist.  Two new modukles should be created:  a module containing the renderer itself, and a test suite to confirm intended behaviour.

1.  Choose a short name string for the render type that does not clash with any values already defined in `annalist/views/fields/render_utils`.  Most of the defined render types appear in the tables at the start of the module (`_field_view_files`, `_field_edit_files` and `_field_get_renderer_functions`), but others may be mentioned directly in the functions that follow (e.g. `RepeatGroup`, `RepeatGroupRow` and `RepeatListRow` are mapped directly in function `get_view_renderer`)


2.  Define test cases as a new module in `annalist/tests/`.  The existing test module `test_render_bool_checkbox.py` can be used as a starting point for defining a new module.  This module uses another module, `field_rendering_support.py`, to handle common aspects of renderer testing.  I suggest giving the new module a name that starts with `test_render_`.  Steps to consider when creating this module:

    * [ ] Copy `test_render_bool_checkbox.py` to new module name
    * [ ] Update descrptive comment at top of module
    * [ ] Update `import` statement to refer to new module to be defined
    * [ ] Update class name
    * [ ] Rename and update the test case method for value rendering: this should cover value view and edit cases as appropriate.
    * [ ] Rename and update the test case method for decoding input values suitable for storage in a JSON structure.

    Once defined, the Annalist test runner should automatically detect and run the new tests (though the new tests will, of course, initially fail).

3. Define a new renderer module in `annalist/views/fields/`.  The existing module `render_bool_checkbox.py` can be used as a starting point for this.  I suggest giving the new module a name that starts with `render_`.  Steps to consider when creating this module:

    * [ ] Copy `render_bool_checkbox.py` to new module name
    * [ ] Update descrptive comment at top of module
    * [ ] Update class name for value mapper
    * [ ] Implement value mapping as required.  If the values do not require mapping between the JSON object and form data, the class `render_text.RenderText`, which contains identity mapping functions, can be used instead.  If the renderer is updates the JSON representation of existing data, consider handling legacy representations in the `encode` method to facilitate data migration.
    * [ ] Rename and update the view renderer and edit renderer functions to generate appropriate HTML.
    * [ ] Rename and update the get renderer function.  Note that this function must returned a `RenderFieldValue` object, as this provides the interfaces required by the rest of Annalist to render values in different contexts.

4.  Edit module `annalist/views/fields/render_utils.py` to import the get renderer function, and add it to the dictionary `_field_get_renderer_functions`.


## Using a new renderer

1.  Add the renderer type name to the enumeration defined in `annalist/sitedata/enums/Enum_render_type`; this allows the render type to appear on the field type drop-down that is presented when defining a new view or field group in Annalist.  This is easily achieved by duplicating one of the existing directories (e.g. `Text`) to use the new render type name (previously selected at step 1) and editing the file `enum_meta.jsonld` (fields `annal:id`, `rdfs:label`, `rdfs:comment` and `annal:uri`).  The new directory name created must match the dictionary key name used when uopdating `annalist/views/fields/render_utils.py`.

2. Update site or collection data field definitions to use the new renderer as appropiate.

3. Check the affected web views and augment the site CSS file (`annalist/static/css/annalist.css` as needed to get the desired display.  Be very cautious about changing formatting for existing classes;  if a new renderer has special CSS formatting requirements, add new CSS class values for these cases.

NOTE: future developments may implement a separate CSS files for installation- or collection-dependent value rendering templates, to facilitate software updates without trashing local adaptations.

