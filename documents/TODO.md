# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] HOWTOs for common tasks; task-oriented documentation
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.


# Version 0.1.11, towards 0.1.12

- [x] Minor bug: in DMO_experiment, add new performer field, click "+" to define new performer, on return to previous page new field is not there.  Suspect it is because all fields are blank when "+" is clicked, so new field not saved.  Modified `views.form_utils.fieldvaluemap` to treat only `None` as non-existend field value.
- [x] Configuration change so that shell session in new Docker container can see server logs.  Save logs in root of annalist_site data.  
- [x] Non-editing entity view: [#3](https://github.com/gklyne/annalist/issues/3)
    - [x] Create new test suite for non-editing view (add copy options)
    - [x] Update authorization tests (add copy options)
    - [x] Create new template
    - [x] Add new response dispatch options to entityedit
    - [x] Update application urls
    - [x] Check/update view-field renderers
    - [x] Get rid of <p> elements in repeat group listings; update CSS as needed
- [x] New render type: Boolean (checkbox) [#2](https://github.com/gklyne/annalist/issues/2)
    - [x] Boolean/checkbox test cases
    - [x] Boolean/checkbox renderer; allow for migrating old representations
    - [x] Add renderer to render_utils tables
    - [x] Add render type name to enumerated value; update tests
    - [x] Update site data (view?) to use new renderer
    - [x] Check web page(s) (again) and tweak CSS definitions as needed
- [x] Document process for creating and integrating a new renderer
- [x] New render type: Link (hyperlink) [#2](https://github.com/gklyne/annalist/issues/2)
    - [x] Link test cases
    - [x] Link renderer (think about data migration in design)
    - [x] Add renderer to render_utils tables
    - [x] Add render type name to enumerated value; update tests (test_entitygenericlist:244, entity_testsitedata:306)
    - [x] Update site data to use new renderer
    - [x] etc.
- [x] New render type: image, [#2](https://github.com/gklyne/annalist/issues/2)
    - [x] Image test cases
    - [x] Image renderer
    - [x] Add renderer to render_utils tables
    - [x] Add render type name to enumerated value; update tests (test_entitygenericlist:244, entity_testsitedata:306)
    - [x] Update site data to use new renderer
    - [x] etc.
- [x] Extend CruisingLog example data with image galleries for place and daily log entries
    - [x] Generate thumbnails that link to larger images
    - [x] Create new field group "AnnotatedPicture" with textarea and image fields
    - [x] Create Annotation (Textarea) and Picture (UriImage) fields for above
    - [x] Create RepeatGroupRow field AnnotatedPictures
    - [x] Add RepeatGroupRow field to Place view with field group AnnotatedPicture
    - [x] Add RepeatGroupRow field to Place view with field group AnnotatedPicture
    - [x] Test
- [x] New render type: Markdown, [#2](https://github.com/gklyne/annalist/issues/2)
    - following same outline steps as checkbox
    - cf. http://pythonhosted.org//Markdown/reference.html
    - [x] Markdown test cases
    - [x] Markdown renderer
    - [x] Add renderer to render_utils tables
    - [x] Add render type name to enumerated value; update tests (test_entitygenericlist:244, entity_testsitedata:306)
    - [x] Run tests
    - [x] Update test data to use new renderer
    - [x] Fix up CSS for Markdown formatting; e.g.
        - div.columns.view-value > span.markdown p
        - div.columns.view-value > span.markdown li
        - div.columns.view-value > span.markdown h1
        - div.columns.view-value > span.markdown h2
        - div.columns.view-value > span.markdown h3
        - div.columns.view-value > span.markdown h4
    - [x] Update Annalist dependencies to include markdown package
    - [x] Update site data to use Markdown where appropriate 
- [x] Fix styling (row spacing) for site front page - it looks a bit spaced-out following changes to view/list styling.  probably just needs appropriate new CSS classes to be included.
- [x] Beside the "Add field" button, include "Edit view" button on entity editing page.
- [x] BUG: RepeatGroupRow field without Group Ref specified gives 500 error when view is displayed
- [x] BUG: no substitute if add/remove labels not supplied
- [x] Field placement lacks 0/9, 3/9, 0/8, 4/8, 3/6 options
- [x] Provide image click-through to larger version.
- [x] Replace the "Add field" button with an "Edit view" button
    - [x] Also change "Add field?" option in view form to "Editable view?"
    - [x] Update field names and tests
- [x] View display: suppress headings for empty repeatgrouprow value
- [ ] Entity drop-down selectors: add current value to list if not already present
    - (avoids hiding information if type URI changed and field type is no longer offered)
- [x] Add "Edit view" option to view as well as edit form
    - View description doesn't carry the entity Id to the contrinuation URI (None instead)

(sub-release?)

- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to view log
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
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Eliminate type-specific render types
- [ ] Review length restriction on entity/type ids: does it serve any purpose?
- [ ] Form field layout: introduce padding so the fields lay out as indicated by the position value


Usability notes:

- [x] Need easier way to make new entries for fields that are referenced from a record; e.g. a `New value` button as part of an enum field.
- [ ] Clearer linkage between related records - hyperlinks on non-editing views
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


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Create image-viewing page to avoid download options, and link to that. (cf. UriImage renderer)
- [ ] Vary layout for editing and viewing?  Sounds hard.
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
- [ ] When creating (e.g.) bibliographic information, it would be useful if an author id could be linked to another record type (enumeration-style) and use the linked value to populate fields in the referring record.
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?
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
- [ ] Introduce markdown rendering type
- [ ] Use markdown directly for help text
- [x] Consider associating property URI with view rather than/as well as field, so fields can be re-used
- [x] Option to auto-generate unique property URI for field in view, maybe using field definition as base
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an mage from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - checkmout JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo


----
