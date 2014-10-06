# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# V0.1.5, towards V0.1.6

* [x] Default button on view edit form (and others) should be "Save".
    - See http://stackoverflow.com/questions/1963245/.
    - I found adding a duplicate hidden save button at the top of the <form> element did the trick.
- [ ] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
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
    - [ ] field rendering: logic to decode value entered; e.g. for token list
        - [x] new user rendering tests
        - [x] existing user render tests
        - [x] existing user update tests (post edit form) - focus on resulting permissions field
        - [x] move get_entity_values from 'render_utils' to 'bound_field'
        - [ ] update code to use class for simple text rendering
        - [ ] review use of template files vs. use of inline template text in class
    - [x] user view: change stored permissions to list
        - clarify JSON-LD behaviour for treatment as set vs sequence
        - see: http://www.w3.org/TR/json-ld/#sets-and-lists
        - e.g. { '@list': ['a', 'b', ... ] }
        - but note: JSON-LD default is to treat as set, ehich is OK for permissions:
        - [x] Rename TokenList -> TokenSet
    - [ ] new field render option: annal:field_render_type: TokenList (with value_type annal:TokenList) 
    - [ ] add test to render existing built-in user
    - [ ] add tests to check encoding/decoding of user permissions
    - [x] certain views and/or types need admin/config permission to edit or list or view
    - [ ] list description for user
    - [ ] annalist-manager updates to initialize users directory, but don't wipe existing permissions
    - [ ] annalist-manager option to create site user entry and default site permissions
    - [ ] site-wide permissions (e.g. to create collections) need to be site permissions
    - [ ] ...
- [ ] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
- [ ] Scan code for all uses of 'annal:xxx' CURIES, and replace with ANNAL.CURIE.xxx references.  (See issue [#4](https://github.com/gklyne/annalist/issues/4))
- [ ] Add field to view: check property URI is unique
- [ ] Don't store host name in entity URL fields (this is just a start - see issues [#4](https://github.com/gklyne/annalist/issues/4), [#32](https://github.com/gklyne/annalist/issues/32))

(Release here?)

- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
- [ ] Extend form-generator capabilities [#2](https://github.com/gklyne/annalist/issues/2)
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
- [ ] Think about how to handle change of email address (option to remove user from Django database?)
