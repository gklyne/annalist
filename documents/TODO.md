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
- [x] BUG: edit from view, change id, results in NOT FOUND error displayed when returning to previous view.  This occurs because the continuation URI is changed when the id is changed.
    - treat id/type change as special case and update all matching URIs in the continuation chain.  This involves dismantling and reassembling the continuation URI, and the continuation URL handling logic has been refactored to facilitate this.
- [ ] Add 'view' button to edit form
- [ ] Create facility to built repeat field and group structure for existing simple field
    - Currently it gets tedious creating view forms with repeated fields; need to figure a way to streamline this.
    - See also discussion below of introducing "tasks" - this would be an early candidate for that.
    - Need to think how the interface would work.  Option to add "task" button to any form?
- [x] Is it really appropriate to save the annal:url value in a stored entity?
    - [x] in sitedata/users/admin/user_meta.jsonld, not a usable locator
    - [x] entityroot._load_values() supply value for URL
    - [x] entityroot.set_values only supplies value of not already present
    - [x] entityroot.save() discards value before saving
    - [x] views/entityedit.py makes referebnce in 'baseentityvaluemap'.  Removed; tests updated.
- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
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
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of fielod to random value - can no longer browse to field description from view/group description)


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

# Feedback to be sorted

## Backend storage options

From Kingsley Idehen: [https://lists.w3.org/Archives/Public/public-lod/2015Feb/0116.html]()
kidehen@openlinksw.com

Kingsley requests at least one of:

1. LDP
2. WebDAV
3. SPARQL Graph Protocol
4. SPARQL 1.1 Insert, Update, Delete.

My comment:  WebDAV(ish) was on the original roadmap - see https://github.com/gklyne/annalist/issues/32 The intent has been to use vanilla HTTP as far as possible (GET, PUT, POST, etc.) and then use WebDAV PROPFIND(?) to enumerate directory contents.  The more complex stuff isn't needed.

Kingsley also mentions not to worry about access control, but leave that to the backend.  But it woud be the Annalist server, not the browser, that acesses the backend data so there would need to be some way to convey whatever authentication/authosization tokens are needed.  My rough plan was to use an OAUTH2/OIDC enabled backend that should be a small extension from the current OIDC authentication logic already used by Annalist, but the details still need to be worked out.

----
