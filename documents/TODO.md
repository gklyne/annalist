# Annalist TODO

   - [ ] proposed activity
   - [>] in progress
   * [x] completed
   * [x] WONTDO: ...
   * additional note

NOTE: information in this document is being migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Towards V0.1.4

- [x] annalist-manager option to update site data, leaving the rest untouched
- [x] annalist-manager initialize: needs to create `.annalist/providers` directory [#27](https://github.com/gklyne/annalist/issues/27).
- [x] Update view and field descriptions [#16](https://github.com/gklyne/annalist/issues/16)
    - [x] extend field edit form to include additional fields used.
    - [x] extend view edit form to include additional fields used in sitedata (i.e. record_type)
    - [x] add more 'annal:field_entity_type' constraints for fields that are intended to be used only with specific entity types (e.g. fields, views, etc.)
    - [x] List view also needs 'annal:field_entity_type' to control selection
        - [x] Add field manually to internal list descrptions
        - [x] Add field to List_view
    - [x] Remove "Default_field"
- [ ] Blank value in submitted form is ignored [#30](https://github.com/gklyne/annalist/issues/30)
- [ ] List headings are clutter [#26](https://github.com/gklyne/annalist/issues/26)
- [ ] 'Select' label for field type is un-obvious [#25](https://github.com/gklyne/annalist/issues/25)
- [ ] New entities are initially populated with useless junk [#24](https://github.com/gklyne/annalist/issues/24)
- [ ] Change type of entry doesn't delete old record [#29](https://github.com/gklyne/annalist/issues/29)
- [ ] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
- [ ] Extend form-generator capabilities [#2](https://github.com/gklyne/annalist/issues/2)
- [ ] Grid view [#7](https://github.com/gklyne/annalist/issues/7)
- [ ] Can't rename locally created Default_view [#22](https://github.com/gklyne/annalist/issues/22)
- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] Link browsing?
    - [ ] Easy access to entity links?
    - [ ] URI to URL lookup?
- [ ] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)

