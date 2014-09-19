# Annalist TODO

   - [ ] proposed activity
   - [>] in progress
   * [x] completed
   * [x] WONTDO: ...
   * additional note

NOTE: information in this document is being migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# V0.1.5, towards V0.1.6

- [x] Default button on view edit form (and others) should be "Save".
    - See http://stackoverflow.com/questions/1963245/.
    - I found adding a duplicate hidden save button at the top of the <form> element did the trick.
- [ ] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
- [ ] Extend form-generator capabilities [#2](https://github.com/gklyne/annalist/issues/2)
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)

