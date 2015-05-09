# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] HOWTOs for common tasks; task-oriented documentation
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.


# Version 0.1.13, towards 0.1.14

- [x] BUG: invalid entity id in field data causes 500 ServerError
- [x] BUG: If field group refers back to orinal field, python blows its stack, reports 500 ServerError
- [x] Improve reporting of 500 serverError
- [x] BUG: edit from view, change id, results in NOT FOUND error displayed when returning to previous view.  This occurs because the continuation URI is refers to the old entity when the id is changed.
    - treat id/type change as special case and update all matching URIs in the continuation chain.  This involves dismantling and reassembling the continuation URI, and the continuation URL handling logic has been refactored to facilitate this.
- [x] Support for complex entity field values (e.g. supporting details for resource imports)
    - [x] Refactor entityedit Save_Entity handling
    - [x] Refactor entityedit to carry more context in viewinfo (simplify function calls)
    - [x] Refactor value decoding so it can access other form fields (to build complex values)?  (see next)
- [x] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [x] Blob and file upload support: images, spreadsheets, ...
        - [x] Choose render type name: URIImport
        - [x] Define renderer test cases as a new module in `annalist/tests/`, e.g.:
            - [x] Copy `test_render_bool_checkbox.py` to new module name
            - [x] Update descriptive comment at top of module
            - [x] Update `import` statement to refer to new module to be defined
            - [x] Update class name
            - [x] Rename and update the test case method for value rendering: this should cover value view and edit cases as appropriate.
            - [x] Rename and update the test case method for decoding input values suitable for storage in a JSON structure.
        - [x] Define a new renderer module in `annalist/views/fields/`; e.g.:
            - [x] Copy `render_bool_checkbox.py` to new module name
            - [x] Update descrptive comment at top of module
            - [x] Update class name for value mapper
            - [x] Implement value mapping as required.  If the values do not require mapping between the JSON object and form data, the class `render_text.RenderText`, which contains identity mapping functions, can be used instead.  If the renderer updates the JSON representation of existing data, consider handling legacy representations in the `encode` method to facilitate data migration.
            - [x] Rename and update the view renderer and edit renderer functions to generate appropriate HTML.
            - [x] Rename and update the get renderer function.  Note that this function must returned a `RenderFieldValue` object, as this provides the interfaces required by the rest of Annalist to render values in different contexts.
        - [x] Update entityedit.py to recognize new action to import resource
        - [x] Add tests for file import (needs to be a "full stack" test - see `test_field_alias` or `test_linked_records` for simple form of structure to follow)
        - [x] Edit module `annalist/views/fields/render_utils.py` to import the get renderer function, and add it to the dictionary `_field_get_renderer_functions`.
        - [x] Add the renderer type name to the enumeration defined in `annalist/sitedata/enums/Enum_render_type`
        - [x] Update the test modules to accommodate the new render type, and retest:
            - [x] `annalist/tests/test_entitygenericlist.py` about line 244 (bump counter)
            - [x] `annalist/tests/entity_testsitedata.py`, about line 306 (add new render type name in sorted list)
        - [x] Check the affected web views and augment the site CSS file (`annalist/static/css/annalist.css`)
    - [x] Field definition enhancements to link to uploaded file
        - [x] Design revised field definition structure to separate rendering from value reference
            - [x] Value reference direct
            - [x] Value reference as upload to current entity
            - [x] Value reference as URI
            - [x] Value reference as field of another Annalist entity
        - [x] Review existing render type definitions in light of new design
        - [x] Work out migration strategy for collections to use new field structure
        - [x] Revise field render selection logic to allow separate edit renderer selection from view renderer selection
            - Updated logic in maily in render_utils, but some interfaces are revised affecting fielddescription, etc.
        - [x] Revise field value handling to take account of multiple sources
        - [x] Figure out how to resolve relative references: based on entity URL?
        - [x] Test, test cases
        - [x] Refactor: change field names in field description. 
            - [x] s/field_options_typeref/field_ref_type/
            - [x] s/field_restrict_values/field_ref_restriction/
            - [x] s/field_target_key/field_ref_field/
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Apply updates to site data as needed
        - [x] Add logic to migrate collection data
            - [x] Add migration hook to Entity.load() method - call self._migrate_values()
            - [x] Default _migrate_values method in EntityRoot just returns with no change
            - [x] Attach migration data/method to EntityData subclasses as required.  May include common logic in EntityData method.
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Add field ref to field view form
- [x] Add 'view' button to edit form
- [ ] Add file-upload option (with resulting value like URI-import)
    - Cf. https://docs.djangoproject.com/en/1.7/topics/http/file-uploads/
        - class UploadedFile
            - .read
            - .multiple_chunks -> bool
            - .chunks -> generator of chunk data
            - .name
            - .size
            - .content_type
            - .charset
            - .content_type_extra
- [ ] Serve reference to uploaded or imported resource
    - [ ] How to determine content-type? Save parallel metadata, read entity, use extension?
        - read entity is probably the right way, then locate field from resource name.  
        - 404 if not found there, or resource does not exist
        - initially, for GET only
- [ ] Add software version to coll_meta.
    - [ ] Check this when accessing collection.
    - [ ] Update when updating collection
    - cf. http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
        from distutils.version import LooseVersion, StrictVersion
        LooseVersion("2.3.1") < LooseVersion("10.1.2")
- [x] Is it really appropriate to save the annal:url value in a stored entity?
    - [x] in sitedata/users/admin/user_meta.jsonld, not a usable locator
    - [x] entityroot._load_values() supply value for URL
    - [x] entityroot.set_values only supplies value of not already present
    - [x] entityroot.save() discards value before saving
    - [x] views/entityedit.py makes referebnce in 'baseentityvaluemap'.  Removed; tests updated.

(new release?)

- [ ] Usability: 3 key tasks need to be easier (at the level of a single form fill-out):
    - [ ] Create a new type+view+list, suitably interconnected
    - [ ] Define a new field type and add to a view
    - [ ] Create repeating fields in a view.  (a) Define a repeating field type and add to view, or (b) define a repeating group containing an existing field type, and add to a view. (a) could a checkbox choice on the previous task.  See also: [#41](https://github.com/gklyne/annalist/issues/41)
    - Currently it gets tedious creating view forms with repeated fields; need to figure a way to streamline this.
    - See also discussion below of introducing "tasks" - this would be an early candidate for that.
    - Need to think how the interface would work.  Option to add "task" button to any form?
- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to download log, if admin permissions
    - [ ] rotate log files (max 5Mb?) (cf. [RotatingFileHandler](https://docs.python.org/2/library/logging.handlers.html#logging.handlers.RotatingFileHandler))
- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support (e.g. content negotiation)
- [ ] Use site/collection data to populate help panes on displays; use Markdown.
- [ ] Login window: implement "Local" as a provider, authenticated against the local Django user base.
- [ ] Login: support continuation URI
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]

(feature freeze for V0.9alpha?)

- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Loom into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] Eliminate redundant render types
- [ ] Provide content for the links in the page footer
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] Shared deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
    - Seems to be working, but needs explicit testing to make sure.
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.)
- [ ] Review length restriction on entity/type ids: does it serve any purpose?
- [ ] Form field layout: introduce padding so the fields lay out as indicated by the position value
- [x] Improve formatting of README sent to PyPI
    - renamed src/RAEDME.md to README.rst


Usability notes:

- [x] Need easier way to make new entries for fields that are referenced from a record; e.g. a `New value` button as part of an enum field.
- [x] Clearer linkage between related records - hyperlinks on non-editing views
- [ ] Introduce notion of "Task", based on form, but linked to "script" action.
    - [ ] Create a "wizard-like" (or one-form) interface for creating type+list+view set.
        - test by creating contacts/supplies listy for CruisingLog
    - [ ] Create a "wizard-like" (or one-form) interface for creating field+field-group set.
        - needs to create (a) individual fields in group, (b) field group and (c) field referring to group.
    - [ ] Procedure for creating type + view definition + list definition + field definitions from a simple overview description
    - [ ] Procedure for creating enumeration type from simple description of options
    - [ ] Procedure to migrate textual type annotations to enumeration types
    - [ ] Simplify repetitive data entry; e.g.
        - Use-case: create bibliographic author details from just full name entered
        - [ ] derived field (possibly hidden) with a rule to guide its creation from other fields in a view
        - [ ] default value from other field (possibly from a derived field)
        - [ ] initial value/identifier templates (e.g. create ID from current date)
            - NOTE: default and initial values behave differently
        - [ ] "view source" record editing (of JSON), with post-entry syntax checking.
- [ ] Getting type URI/CURIE to match across type/list is too fragile.  Avoid using selector for this unless it's really needed?
- [ ] Use pop-up text based on field comment to tell user how a field value is used
- [ ] Option to re-order fields on view form
- [ ] When creating type, default URI to be based on id entered
- [ ] Instead of separate link on the login page, have "Local" as a login service option.
- [ ] List display paging
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Improve reporting of errors due to invalid view/field definitions, etc.
- [ ] add 404 handling logic to generate message and return to next continuation up the chain.
    - [ ] reinstate get_entity_data in displayinfo, and include 404 response logic.
    - [ ] update entityedit c.line_116 to use new displayinfo function.  This will mean that all 404 response logic is concentrated in the displayinfo module. (Apart from statichack.)
    - [ ] update displayinfo so that it receives a copy of the continuation data when initialized.
    - [ ] pass continuation data into view_setup, list_setup, collection_view_setup for ^^.  For site, just use default/empty continuation.
    - [ ] Calling sites to collect continuation are: EntityGenericListView.get, EntityGenericListView.post, EntityDeleteConfirmedBaseView.complete_remove_entity, GenericEntityEditView.get, GenericEntityEditView.post.
- [ ] ORCID authentication - apparently OAuth2 based (cf. contact at JISC RDS workshop)
- [ ] Create image-viewing page to avoid download options, and link to that. (cf. UriImage renderer)
- [ ] Vary layout for editing and viewing?  Sounds hard.
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
- [ ] When creating (e.g.) bibliographic information, it would be useful if an author id could be linked to another record type (enumeration-style) and use the linked value to populate fields in the referring record.
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?  But note that general philosophy is to avoid unnecessary validity checks that might impede data entry.
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions
- [ ] Make default values smarter; e.g. field renderer logic to scan collection data for candidates?
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection? 
- [ ] Provide a way to edit collection metadata (e.g. link from Customize page)
- [ ] Provide a way to edit site metadata (e.g. via link from site front page)
- [ ] Provide a way to view/edit site user permissions (e.g. via link from site front page)
- [ ] Provide a way to view/edit site type/view/list/etc descriptions (e.g. via link from site front page)
- [ ] Undefined list error display, or any error - include link to collection in top bar
- [ ] Help display for view: use commentary text from view descrtiption; thus can tailor help for each view.
- [x] Introduce markdown rendering type
- [ ] Use markdown directly for help text
- [x] Consider associating property URI with view rather than/as well as field, so fields can be re-used
- [x] Option to auto-generate unique property URI for field in view, maybe using field definition as base
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an image from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - check out JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo
- [ ] Think aboutr selective updates to complex field values (e.g. import_field logic).
    - Currently, the save_entity logic in `views.entityedit` assumes that fields are completely replaced at the top-level of keys in `entityvals`.  There is no support for partial replacement of a field from a form input: either the entire field is replaced or the original field value is kept in its entirety.  The import_field logic generates additional values when the `Import` button is activated, but not when the URL field is updates. Possible approaches:
        - re-work the whole entity form data mapping logic so that fields can be partially updated.  This will involve accessing the original entity data before `save_entity` is called, and arranging that original field values are available while form data valuesare being mapped.  This is a fairly comploex re-work is desired.
        - separate complex field values into separate fields that can be updated all-or-nothing
        - save original field data in a hidden form field (similar to `views.confirm`)
- [ ] Consider refactoring form generator around Idiom/Formlet work; cf.
    - http://groups.inf.ed.ac.uk/links/papers/formlets-essence.pdf
    - http://homepages.inf.ed.ac.uk/wadler/papers/formlets/formlets.pdf
    - http://homepages.inf.ed.ac.uk/slindley/papers/dbwiki-sigmod2011.pdf


# Feedback

* https://github.com/gklyne/annalist/issues/40


----
