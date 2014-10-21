# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# V0.1.5, towards V0.1.6

* [x] Default button on view edit form (and others) should be "Save".
    - See http://stackoverflow.com/questions/1963245/.
    - I found adding a duplicate hidden save button at the top of the <form> element did the trick.
* [x] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
    - [x] layout.py: add _user defs
    - [x] message.py
    - [x] entitytypeinfo.py
    - [x] annalistuser.py (new)
    - [x] AnnalistUser test suite
    - [x] create _user type
    - [x] collection.py - just get_user_perms method for now.
    - [x] get_user_perms test case in test_collection
    - [x] add method for getting details of current authenticated user (GenericView).
    - [x] update authorization method calls to include target collection
    - [x] Use user id to locate, but also check email address when granting permissions.
    - [x] Create generic view method for accessing user permissions (may supersede collection method)
    - [x] Provision for site-wide default permissions
    - [x] Authorization test suite
    - [x] update authorization logic to use permissions data
    - [x] create collection also creates initial user record for creator with all permissions
    - [x] annalist-manager create admin user also needs to create site admin permissions for that user
        - Note: required change to create Django user programmatically rather than by django-admin utility
    - [x] view description for user
    - [x] field descriptions for user
    - [x] field rendering: logic to decode value entered; e.g. for token list
        - [x] new user rendering tests
        - [x] existing user render tests
        - [x] existing user update tests (post edit form) - focus on resulting permissions field
        - [x] move get_entity_values from 'render_utils' to 'bound_field'
        - [x] WONTDO update code to use class for simple text rendering
            - NOT YET: current structure doesn't distinguish between edit, view, etc.
            - Resolve that before updating existing use of separate template files
    - [x] user view: change stored permissions to list
        - clarify JSON-LD behaviour for treatment as set vs sequence
        - see: http://www.w3.org/TR/json-ld/#sets-and-lists
        - e.g. { '@list': ['a', 'b', ... ] }
        - but note: JSON-LD default is to treat as set, which is OK for permissions:
        - [x] Rename TokenList -> TokenSet
    - [x] new field render option: annal:field_render_type: TokenSet (with value_type annal:TokenSet) 
    - [x] add test to render existing built-in user
    - [x] add tests to check encoding/decoding of user permissions
    - [x] certain views and/or types need admin/config permission to edit or list or view
    - [x] list description for user
    - [x] annalist-manager updates to initialize site-users directory, but don't wipe existing user permissions
    - [x] annalist-manager option to update existing Django user to admin status
    - [x] annalist-manager option to create site user entry and default site permissions
    - [x] what site-level permission is required to create new collection?
        - Site-level CREATE/DELETE.  
        - Add test cases
    - [x] annalist-manager option to delete existing user
    - [x] site-wide permissions (e.g. to create collections) need to be site permissions
    - [x] implement delete user handler and tests - WONTDO: handled by generic entity delete
* [x] List view: option to hide columns on smaller screens (cf. permissions)
* [x] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
    - [x] Missing resource error reporting in:
        - [x] annalist/views/collection.py (missing collection)
        - [x] annalist/views/recordtype.py (missing type)
        - [x] annalist/views/genericlist.py (missing collection, type, list description)
        - [x] annalist/views/genericedit.py (missing collection, type, view description, entity)
- [x] Scan code for all uses of 'annal:xxx' CURIES, and replace with ANNAL.CURIE.xxx references.  (See issue [#4](https://github.com/gklyne/annalist/issues/4))
- [x] Add field to view: check property URI is unique
- [x] Don't store host name in entity URL fields (this is just a start - see issues [#4](https://github.com/gklyne/annalist/issues/4), [#32](https://github.com/gklyne/annalist/issues/32))
- [x] Investigate use of path-only references for copntinuation URIs
    - [x] would need to resolve when generating Location: header field ...
    - It turns out that instances of continuation URI with hostname are all used for testing Location: header responses, hence there's nothing to do (except add a few comments).
- [x] set base directory for running tests so that annalist_root doesn't appear in test names
    - tried, but doesn't seem to be an easy way to do this (apart, maybe, from creating a new test runner)
- [x] Initial documentation of authorization controls
- [x] Review getting started documentation in light of new authz controls
- [ ] Test creation of cruising log (again) using real log data
- [x] Flesh out the user documentation
- [ ] record new demo screencast
- [ ] Seems to be a problem renaming a type for which there are defined values: need to rename the typedata directory too

(Release here?)

- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Extend form-generator capabilities [#2](https://github.com/gklyne/annalist/issues/2)
    - [ ] Refactor handling of repeat field groups
    - [ ] Define type for field group (_group)
    - [ ] Define view for field group (list of fields)
    - [ ] Define list for field group
    - [ ] Refdefine view with list of fields?  Not if that impacts usability.
    - [ ] Define e-v-map for defined list of fields
    - [ ] Repeat to reference list of fields 
    - [ ] Eliminate dupliction with list view
    - [ ] Add option to add repeated field group
    - [ ] Revisit 
- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] Shared deployment should generate a new secret key in settings
- [ ] Use separate Django database for each configuration
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
- [x] Think about how to handle change of email address (option to remove user from Django database?)
    - annalist_manager now has deleteuser option
- [ ] review use of template files vs. use of inline template text in class
    - [x] Need to support edit/view/item/head (NOT: probably via class inheritance structure)
    - [x] Inline template text should be more efficient as it avoids repeated reading of template files
    - [x] Inline template text keeps value mapping logic with template logic
    - [ ] Inline templates may be harder to style effectively; maybe read HTML from file on first use?
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s). 
- [ ] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] Provide content for the links in the page footer
- [ ] 'Add field' can't be followed by 'New field' because of duplicate property used
- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
- [ ] Include date+time in log entries


Notes for Future TODOs:

- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions
- [ ] Make default values smarter; e.g. field renderer logioc to scan collection data for candidates?
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
