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
    - [ ] Use user id to locate, but also check email address when granting permissions.
    - [ ] create collection also creates initial user record for creator with all permissions
    - [ ] view description for user
    - [ ] field descriptions for user
    - [ ] list description for user
    - [ ] certain views and/or types need admin/config permission to edit or list or view
    - [ ] update authorization checks
    - [ ] annalist-manager updates to initialize users directory
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
