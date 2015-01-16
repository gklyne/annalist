# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] HOWTOs for common tasks; task-oriented documentation
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.


# V0.1.9, towards V0.1.10

- [x] Bug: https://github.com/gklyne/annalist/issues/39 (hotfix 0.1.8a)
- [x] Add mechanism to alias a common field (e.g. rdfs:label) to return some other specified field value (e.g. bib:title).  Associate aliases with record type, used when constructing view/list context.
- [x] Option to create linked record directly from other record entry field (issue #23). Propose enum type renderer should include a "New" button that launches new view to enter new value of appropriate type.
    - [x] Add new logic in views.entityedit
    - [x] Create enumeration renderer: update template or replace with renderer class to add extra "New" button to enumerated value fields
    - [x] Create test case for new option (should be able to adapt, e.g., "New view" test case?)
    - [x] Create test case for new button on field selector in _view edit
- [x] BUG: View property-override in field list is not working, or is not recognized by by the duplicate property check.  See also issue (below) about 'Add field' followed by 'New field'.
- [x] BUG: '+' button on repeated field value creates entity of wrong type: e.g. _type not Place.  Was bug in enumeration scanning logic.
- [x] BUG: Add segment in CruisingLog gives 500 server error.
- [x] BUG: annalist-manager updatesitedata not clearing out old enumeration types.  Not there.  See next.
- [x] BUG: pip uninstall not clearing out old sample data, causing test failures.  Looks like a problem with the build process, not clearing out old files.  How to fix?
    - python setup.py clean --all
- [x] BUG: ID too long is ccepted but then can't access (404 response).  Need to id validity check before saving.
- [x] Usability issues arising from creating cruising log
    - [x] 'Add field' can't be followed by 'New field' because of duplicate property used
        - consider using Enum_optional logic so the field selector id isn't automatically filled in;  ignore blank field ids when processing;  ensure field with blank id is still saved with view/group.
        - chosen fix is to auto-generate a property URI in the view description based on the field property URI but with a _2, _3, etc suffix.  If there is an existing view-defined property URI that clashes, reject the update as now.
        - what to do if the render type is changed?  Ideally, remove any auto-generated property URI, but preserve manually entered values.
    - [x] Entity edit view: "New field" -> "New field type"
- [x] Refactor button locating logic in edit form response handler
- [ ] Review field description is_enumeration (?) - use `has_new_button` for fields with `new` button
- [ ] review field description and detection of repeated field-group references. 
- [ ] Use `annalist_edit_choice.html` instead of annalist_edit_view_sel.html - update view template.  Cf. View_sel vs List_sel render types.
- [ ] Consider removing "New type", "New view" and "New field type" buttons, and corresponding test cases.
- [ ] RepeatGroup renderer - use placeholder beside label as way to explain content?
- [ ] Select new list view: drop type_id from URI? (e.g. when changing to view of different type)
- [ ] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  The current mechanism of using an explciit type to display site-wide values is probably confusing.
- [ ] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] Review options for creating user accounts in development software version (currently have 'admin'/admin@localhost in sitedata as holding option).  Put something explicit in makedevelsite.sh? Document site 'admin' user and development setup?
- [ ] `annalist-manager` help to provide list of permission tokens
 
(sub-release?)

- [ ] New render types: Markdown, Boolean (checkbox), Link (hyperlink)
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
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
- [ ] Provide content for the links in the page footer
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]

(feature freeze for V0.9alpha?)

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
- [ ] review use of template files vs. use of inline template text in class
    - [x] Need to support edit/view/item/head (NOT: probably via class inheritance structure)
    - [x] Inline template text should be more efficient as it avoids repeated reading of template files
    - [x] Inline template text keeps value mapping logic with template logic
    - [ ] Inline templates may be harder to style effectively; maybe read HTML from file on first use?
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Eliminate type-specific render types
- [ ] Review length restriction on entity/type ids: does it serve any purpose?


Usability notes:

- [ ] Need easier way to make new entries for fields that are referenced from a record; e.g. a `New value` button as part of an enum field.
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

- [ ] When creating (e.g.) bibliographic information, it would be useful if an author id could be linked to another record type (enumeration-style) and use the linked value to populate fields in the referring record.
- [ ] Review site/collection data organization
    - [ ] Generalize collection/site hierarchy to use a "search path" of imported collections.  See also next item.
    - [ ] Enumerated values are hard-wired into models.entitytypeinfo - move them to regular type/data files in site data?  Hmmm... currently, it seems all _annalist_site values need to be hard-wired in entitytypeinfo; maybe look to use collection "search path" logic instead (see above).
    - [ ] Think about implementing site data as a distinguished collection, thereby exploiting the access control framework for site metadata updates.
    - [ ] _annalist_core for software-defined values, and _annalist_site for local overrides?
    - [ ] Refer collection management permissions (create/update/etc) to _annalist_site collection - this will make it easier to define top-level permnissions through Annalist itself, rather than relying on annalist-manager.
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s). 
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
- [ ] Option to auto-generate unique property URI for field in view, maybe using field definition as base
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an mage from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - checkmout JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.


----
