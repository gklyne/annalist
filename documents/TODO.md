# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# V0.1.7, towards V0.1.8

- [x] Add button to annalist.net page: https://github.com/BetaNYC/getDataButton
- [x] Extend form-generator capabilities [issue #2](https://github.com/gklyne/annalist/issues/2)
    - [x] Revise representation of repeat field structures in view description: repeat description to be part of root of repeat structure, not an ad ho0c field at the end.  This should remove some special cases from the code.
    - [x] Refactor handling of repeat field groups
    - [x] Define type for field group (_group?  Or use _view?)
    - [x] Use _list rather than _view? (NO: list has much more bound-in semantics)
    - [x] Rename 'View_field' to (say) 'View_field_view' (cf. previous use _list)
    - [x] Define view for field group (list of fields)
    - [x] Define list for field groups (not needed as views used for field-groups)
    - [x] Redefine view with list of fields?  Not if that impacts usability.
    - [x] Define e-v-map for defined list of fields
    - [x] Repeat to reference list of fields 
- [x] Eliminate duplication with list view - rework list to use same repeating mechanism as view
- [x] Provide clean(er) mechanism to propagate extra context to bound fields in repeat group rendering
- [x] Try eliminating `view_context` parameter from `FieldListValueMap` constructor - turns out that it's needed for generating enumerated type lists based on target type of view, but code has been rationalized and slightly simplified and relevant comments added.
- [x] Use distinguished names for internally-generated context keys (e.g. '_fields')
- [x] Simplify list template now that repeat fields are handled by a field renderer
- [x] Try to make mapping classes more consistent in their return types for sub-context values
- [x] Raise error if required view_context information is missing for EntityFinder
- [x] Add field for `annal:field_entity_type` property in field view
- [x] Revisit definitions for BibJSON view; confirm that repeat field groups can be created
    - [x] Bib_type field should be enumeration
    - [x] Month, year on same line
    - [x] Restrict view choices field to views that are not subsidiary field groups
- [x] Improve list column layout, avoid values overflowing column and overlapping next (e.g. with long identifiers - cf. http://localhost:8000/annalist/c/coll1/l/Default_list_all/_view/) (PART FIX - made id column wider)
- [x] Improve display of view fields: put field names in header of repeat-group
    - [x] Reworked field rendering to support more options
    - [x] List display remove header rendering from template, handle in repeat
        1. [x] Put header column logic in repeat group item renderer
        2. [x] Update list template
    - [x] Introduce new render type Repeat*Row, sharing code with RepeatGroup
    - [x] Move row selection from template (uses .item) to editlist (uses RepeatGroup)
    - [x] Work through field rendering options for Repeat*Row:
    - [x] Rework field description used by view view to use new field rendering options
- [x] merge rework-form-manager to develop branch
- [x] Bugfix: e.g. 'Bib_person_field_view' does not show appropriate field options
- [x] Bug: create field group does not show up on field group list
- [x] Need test coverage for FieldDescription with a field group
- [ ] Tests for sitedata: using Beautifiul soup (maybe), create table-driven tests for checking field contents for various rendered pages (lists and views), abstracted away from details of rendering and layout.  For example, test that correct field options are displayed for different views.
    - [x] Move site data functions from entity_testentitydata to entity_testsitedata
    - [x] Add functions for groups
    - [ ] Define new test_sitedata module with functions for testing values in view rendering via BeautifulSoup
    - [ ] Create test cases for each of the main views on site data
    - [ ] Remove tests from other test sites that duplicate these tests (esp test_record* tests)
- [ ] Test software installaton from merged branch
- [ ] Test new capabilities to define view with repeating fields - make sure it is doable
- [ ] Test adding more data to cruising log
- [ ] Test upgrade of existing deployment
- [ ] Deploy updates to annalist.net
- [ ] New sub-release

(later)

- [ ] Think about mechanism for a common field (e.g. rdfs:label) to return a specified field value (e.g. bib:title).  Associate aliases with record type, used when constructing view/list context.
- [ ] Generalize collection/site hierarchy to use a "search path" of imported collections
- [ ] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  (defer?)
- [ ] Enumerated values are hard-wired into entitytypeinfo - move them to regular type/data files in site data?  Hmmm... currently, it seems all _annalist_site values need to be hard-wired in entitytypeinfo; maybe look to use collection "search path" logic instead (see above)

- [ ] Review options for creating user accounts in development software version (currently have 'admin'/admin@localhost in sitedata as holding option).  Put something explicit in makedevelsite.sh? Document site 'admin' user and development setup?
- [ ] Think about fields that return subgraph (defer?)
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication

(sub-release?)

- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] Shared deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
- [ ] `annalist-manager` help to provide list of permission tokens
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]
- [ ] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] 'Add field' can't be followed by 'New field' because of duplicate property used
- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to view log
- [ ] Usability issues arising from creating cruising log
    - [ ] Want option to create linked record directly from other record entry field (issue #??).
    - [ ] Fields should default to previous value entered.  How to save these?

(sub-release?)

- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Review concurrent access issues; document assumptions
- [ ] Use site/collection data to populate help panes on displays; use Markdown.
- [ ] review use of template files vs. use of inline template text in class
    - [x] Need to support edit/view/item/head (NOT: probably via class inheritance structure)
    - [x] Inline template text should be more efficient as it avoids repeated reading of template files
    - [x] Inline template text keeps value mapping logic with template logic
    - [ ] Inline templates may be harder to style effectively; maybe read HTML from file on first use?
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Provide content for the links in the page footer

Notes for Future TODOs:

- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s). 
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions
- [ ] Make default values smarter; e.g. field renderer logic to scan collection data for candidates?
- [ ] Option to rearrange fields on view form (after restructuring?)
- [ ] When creating type, default URI to be based on id entered
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection? 
- [ ] Provide a way to edit collection metadata (e.g. link from Customize page)
- [ ] Provide a way to edit site metadata (e.g. via link from site front page)
- [ ] Provide a way to view/edit site user permissions (e.g. via link from site front page)
- [ ] Provide a way to view/edit site type/view/list/etc descriptions (e.g. via link from site front page)
- [ ] Undefined list error display (any error?) - include link to collection in top bar
- [ ] Help display for view: use commentary text from view descrtiption; thus can tailore help for each view.
- [ ] Introduce markdown rendering type
- [ ] Use markdown directly for help text
- [ ] Consider associating property URI with view rather than/as well as field, so fields can be re-used
- [ ] Option to auto-generate unique property URI for field in view, maybe using field definition as base
- [ ] Need easier way to make new entries for fields that are referenced from a record; e.g. a `New value` button as part of an enum field.
- [ ] Instead of separate link on the login page, have "Local" as a login service option.
- [ ] Entity edit view: "New field" -> "New field type"


<!-- 
.........1.........2.........3.........4.........5.........6.........7.........8
-->
