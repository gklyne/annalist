# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).

# Documentation

1. Diagrams to support demos

2. Illustrated tour of the user interface

3. HOWTOs for certain tasks


# V0.1.9, towards V0.1.10

- [ ] Bug: https://github.com/gklyne/annalist/issues/39
- [ ] Think about mechanism for a common field (e.g. rdfs:label) to return a specified field value (e.g. bib:title).  Associate aliases with record type, used when constructing view/list context.  This will allow BibEntry title to show in defaul list.
- [ ] Review options for creating user accounts in development software version (currently have 'admin'/admin@localhost in sitedata as holding option).  Put something explicit in makedevelsite.sh? Document site 'admin' user and development setup?
- [ ] When creating (e.g.) bibliographic information, it would be useful if an author id could be linked to another record type (enumeration-style) and use the linked value to populate fields in the referring record.
- [ ] RepeatGroup renderer - use placeholder beside label as way to explain content?
- [ ] Select new list view: drop type from URI? (e.g. when changing to view of different type)
- [ ] Generalize collection/site hierarchy to use a "search path" of imported collections.  See also next item.
- [ ] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  The currenmt mechanism of using an explciit type to display site-wide values is probably confusing.
- [ ] Enumerated values are hard-wired into entitytypeinfo - move them to regular type/data files in site data?  Hmmm... currently, it seems all _annalist_site values need to be hard-wired in entitytypeinfo; maybe look to use collection "search path" logic instead (see above).

(next sub-release?)

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
- [ ] Think about fields that return subgraph (defer?)
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
- [ ] Create a "wizard-like" (or one-form) interface for creating type+list+view set.
- [ ] Create a "wizard-like" (or one-form) interface for creating field+field-group set.
- [ ] Simplify repetitive data entry; e.g.
    - Use-case: create bibliographic author details from just full name entered
    - [ ] derived field (possibly hidden) with a rule to guide its creation from other fields in a view
    - [ ] default value from other field (possibly from a derived field)
    - [ ] initial value/identifier templates (e.g. create ID from current date)
        - NOTE: default and initial values behave differently
    - [ ] "view source" record editing (of JSON), with post-entry syntax checking.


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
