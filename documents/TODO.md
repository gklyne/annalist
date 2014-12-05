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
- [ ] Revisit definitions for BibJSON view; confirm that repeat field groups can be created
    - [ ] Bib_type field should be enumeration
    - [x] Month, year on same line
    - [ ] Restrict viewref field to views that are not subsidiary field groups
- [ ] Improve display of view fields: put field names in header of repeat-group
    - view, edit, colhead, colview, coledit render options; template gets to choose
    - think how this plays with responsive content

(merge rework-form-manager to develop branch)

- [ ] Review options for creating user accounts in development software version (currently have 'admin'/admin@localhost in sitedata as holding option).  Put something explicit in makedevelsite.sh? Document site 'admin' user and development setup?

- [ ] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  (defer?)
- [ ] Think about fields that return subgraph (defer?)
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] Generalize collection/site hierarchy to use a "search path" of imported collections (defer)
- [ ] Review field placement and layout grid density (16col instead of 12col?)

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


# BibJSON structures

(later:  copy to documentation/notes directory)

cf. http://okfnlabs.org/bibjson/

## Simple string fields

address: Publisher's address (usually just the city, but can be the full address for lesser-known publishers)

[annote: An annotation for annotated bibliography styles (not typical) @@ use rdfs:comment?

booktitle: The title of the book, if only part of it is being cited

chapter: The chapter number

edition: The edition of a book, long form (such as "First" or "Second")

editor: (see Bib_person_field_view below)

eprint: A specification of an electronic publication, often a preprint or a technical report @@handle as identifier/link?

howpublished: How it was published, if the publishing method is nonstandard

institution: The institution that was involved in the publishing, but not necessarily the publisher

journal: (see Bib_journal_field_view below)

[key: A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing).]

month: The month of publication (or, if unpublished, the month of creation)

[note: Miscellaneous extra information @@ use rdfs:comment?]

number: The "(issue) number" of a journal, magazine, or tech-report, if applicable. (Most 
publications have a "volume", but no "number" field.)

organization: The conference sponsor

pages: Page numbers, separated either by commas or double-hyphens.

publisher: The publisher's name

school: The school where the thesis was written

series: The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science") @@ field missing

title: The title of the work

type: The field overriding the default type of publication (e.g. "Research Note" for techreport, "{PhD} dissertation" for phdthesis, "Section" for inbook/incollection)

volume: The volume of a journal or multi-volume book

year: The year of publication (or, if unpublished, the year of creation)


## Object fields

### Bib_person_field_view

author: [list] The name(s) of the author(s)
editor: [list] The name(s) of the editor(s)

    id:
    name:
    alternate:
    firstname:
    lastname:


### Bib_journal_field_view

journal: [object] The journal or magazine the work was published in
    id:
    name:
    shortcode:


### Bib_license_field_view

license is a list of objects
license:
    type:
    url:
    description:
    jurisdiction:


### Bib_identifier_field_view

identifier is a list of objects
identifier:
    id:
    type: (e.g. DOI, crossref,)
    url:
    anchor:

