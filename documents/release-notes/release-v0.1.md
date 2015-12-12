# Annalist v0.1 release notes

Release 0.1 is the first public prototype of Annalist.  It contains what I hope is sufficient tested functionality for the purposes of early evaluation, but there are significant intended capabilities not yet implemented, and many refinements to be applied.

A summary of issues to be resolved for product release can be seen in the [issues list for the first alpha release milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).  See also the file [documents/TODO.md](https://github.com/gklyne/annalist/blob/develop/documents/TODO.md) on the "develop" branch.

## Current release: 0.1.24b

(See "History" below for information about previous releases)

This patch release fixes a data migration bug in the 0.1.24 release.  This bug meant that data from older releases was not being recognized when accessed by the original 0.1.24 release.


## Status

The primary goals of Annalist are:

* Easy data: out-of-box data acquisition, modification and organization of small data records.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

Of these, the first three are substantially implemented (though there are lots of details to be added), and the fourth is at best only partiallly implemented.

Key features implemented:

* Simple installation and setup procedure to quickly get a working installation
* Highly configurable form interface for entering, presenting and modifying data records, built using self-maintained configuration data.  The core presentation engine is substantially complete, but additional field renderers are still required to support a wider range of basic data types.
* Grid-based responsive layout engine (currently using Zurb Foundation)
* File based, versioning-friendly, textual data storage model;  data design is RDF-based, and uses JSON-LD elements, but contexts not yet defined so it's just JSON with RDF potential.
* Ability to create new entity record types, views and listing formats on-the-fly as data is being prepared
* Authentication with 3rd party IDP authentication (current implementation uses OAuth2/OpenID Connect, tested with Google, but should be usable with other OpenID Connect identity providers).  (Note access control is separate - see "Authorization" below.)
* Authorization framework for access control, applied mainly per-collection but with site-wide defaults.
* Support for linking to and annotating binary objects such as images.
* Image rendering
* Audio clip rendering (via HTML5 capabilities)

Intended core features not yet fully implemented but which are intended for the first full release:

* Support for a range of field and data types to work with commonly used data: numbers, dates, etc.
* Support for JSON-LD contexts.
* Full linked data support, recognizing a range of linked data formats and facilitating the creation of links in and out.  (Links can be created, but it's currently a mostly manual process.)
* Serve and access data through a standard HTTP server (current implementation uses direct file access).
* Grid view (e.g. for photo+metadata galleries).

An intended core feature that will probably not make the first release is data bridges to other data sources, in particular to allow Annalist to work with existing spreadhseet data.

There are also a number of rough edges to rounded off.  Through use of the software with real data, a number of areas have been identified where usability could be significantly improved.

See the [list of outstanding issues for initial release](https://github.com/gklyne/annalist/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22V0.x+alpha%22) for more details on planned features still to be implemented.

There are many other features noted on the project roadmap that are not yet planned for inclusion as core features in the initial release.  As far as possible, future development will be guided by actual requirements from applications that use the Annalist platform.


## Feedback

The main purpose of this release is to be a viable platform for getting feedback from potential users of the software.  In particular, I'd like to hear:

* If installation and getting a running service on a computer meeting the indicated prerequisites takes longer than 10 minutes.  What were the stumbling points?
* Any problems that occur whle trying to use the software.
* Ways in which the software does not meet preferred workflows for collecting data.
* Any must-have features for the software to be useful.
* Any other thoughts, ideas, or difficulties you care to report.

If you have a github account, feedback can be provided through the [github issue tracker](https://github.com/gklyne/annalist/issues).  Otherwise, by message to the [annalist-discuss forum](https://groups.google.com/forum/#!forum/annalist-discuss) at Google Groups.


## Development

Active development takes place on the [`develop` branch](https://github.com/gklyne/annalist/tree/develop) of the GitHub repository.  The `master` branch is intended for stable releases, and is not used for active development.  It would be appreciated if any pull requests submitted can against the `develop` branch.


# Further information

(Many of these documents are still work-in-progress)

* [Annalist overview](../introduction.md)
* [Installing and setting up Annalist](../installing-annalist.md)
* [Getting started with Annalist](../getting-started.md)
* [Guide to using Annalist](../using-annalist.adoc)
* [Simple demonstration sequence](../demo-script.md)
* [Frequently asked questions](../faq.md)
* [Developer information](../developer-info.md)
* [Development roadmap](../roadmap.md)


# History


## Version 0.1.24b

This patch release fixes a data migration bug in the 0.1.24 release.  This bug meant that data from older releases was not being recvognized when accessed by the original 0.1.24 release.


## Version 0.1.24a

This patch release fixes a minor bug in the 0.1.24 release which sometimes caused on of the test cases to fail.  The faullt was in the test suite setup rather than the Annalist software, but in the spirit of "no broken windows" is being fixed here.


## Version 0.1.24

This release adds sharing of collection structure descriptions, which is a first step towards supporting modularization of data structure descriptions.

An Annalist collection can be defined to inherit record type, view, list and other definitions from an existing collection.  This means a new collection can be created based on the structure of an existing collection, and then evolved as before.  Any changes that are made to the collection configuration are recorded in the new collection, and do not affect the original.  It will requiure some experimentation to work out how to best use this capability, but the current thinking is that the collection structure may be defined separately from the data, to be inherited by any collections that use the structure as a starting point.  (The structure descriptions can be extracted from an existing collection by copying the directory `c/_annalist_site` into a new collection.)

A number of bugs have been fixed, and there has been some extensive internal code refactoring, in part to prepare the codebase for separation of the record storage from the Annalist web service (e.g. to allow collections to be stored in separate Linked Data Platform servers).  For more details, see the change notes for release 0.1.23.


# Version 0.1.23, towards 0.1.24

- [x] BUG: resolve model dependency on view module introduced by context-generation logic
    - (caused Django configuration settings to be invoked too early, and spurious log output)
    - cf. TODOs in model.site and model.collection
- [x] BUG: `render_utils.get_mode_renderer`, handling of repeat fields? (cf. comment from Cerys.)
    - Added logic so that repeat fields also support current-mode rendering (but rendering as a normal view; i.e. with label)
- [x] BUG: enumerated values listed as types (when using "View all")
- [x] BUG: default view setting is not applied.
- [x] BUG (from 0.1.22 release): creating admin user in new site fails
- [x] Suppress display of _initial_values when listing entities (is this the right choice?)
- [x] moved 'child_entity_ids' method to root so it can be used with `Site` objects
- [x] moved site scoping enumeration logic from `Site` to `EntityRoot`
- [x] Re-work site/collection structure to allow cascaded inheritance between collections.  Eliminate site data as separate thing, but instead use a standard, read-only, built-in collection. This will    allow an empty collection to be used as a template for a new collection.  As with site data, edits are always added to the current collection.
    - [x] move annalist sitedata to special collection location
    - [x] re-implement SiteData as instance of collection; use this as collection parent; test
    - [x] re-work alternative-directory logic to be controlled by the parent rather than the child.
    - [x] add 'altscope' parameter to calls that may access the alternative search path (replacing `altparent` parameter)
    - [x] when creating a collection, allow to specify alternate parent(s); ensure no loops: must end up at sitedata; test
    - [x] ensure that _annalist_site collection cannot be removed
    - [x] implement search logic in Entity._exists_path, Entity._chidren, Entity._child_dirs, overriding methods from EntityRoot.
    - [x] remove all alt path/parent logic from EntityRoot
    - [x] change altparent parameter for altscope flag (None, "all", ...)
        - altparent is still used with Collection constructor to indicate alternative search path
    - [x] require Collection `altparent` to itself be a Collection.  Support later alteration of the `altparent`.
     - [x] Isolate all file access or file-dependent logic to EntityRoot (to simplify alternate storage later)
        - considered moving all remove file/path logic to EntityRoot and eliminating os.path inclusion in Entity, but still have directory path setup in Entity constructor.  The allocation of directory names is somewhat bound up with parent/child reklationships, so this limited file name handling logic remains in Entity.
- [x] Ensure that _annalist_site collection data cannot be updated
    - [x] Add new site permission map in model.entitytypeinfo that forbids modifications except users
- [x] Site data migration
    - [x] `annalist_manager updatesite` updated to create data in new location.
    - [x] `annalist_manager updatesite` copies previous users and vocabs to new location.
- [x] Updates to annalist-manager (createsite, updatesite): don't rely on sample data
    - [x] refactor site initializaton logic in models.site.py
    - [x] re-work am_createsite to use just models.site functions.
- [x] Provision for editing collection data (label, comment, parents, etc.); test
- [x] Re-think protections for viewing/editing collection metadata: really want the authorization to be based on permissions in the collection being accessed.
- [x] Create altscope="user" that skips alt parents and checks just local and site permissions
- [x] Provision for specifying and using inherited collections
    - [x] When loading a collection, add logic to set alternate parent based on specified parent in collection metadata.  Uses Collection.set_alt_ancestry
- [x] The bibiographic definitions currently part of site data moved to a "built-in" collection and inherited only when required (e.g., for certain tests).
    - [x] revise layout of site data in source tree to facilitate separate subsets (e.g. Bibliographic data)
    - [x] use new layout for site data to separate Bibliographic data from "core" site data
    - [x] copy bibliographic data collection into test data fixture
    - [x] update tests to work with biblio data in separate collection
- [x] Update JSON-LD spike code, and test with latest rdflib-jsonld
    - See: https://github.com/RDFLib/rdflib-jsonld/issues/33
    - [x] Add comment (generated by, date) to generated context files


## Version 0.1.22

This release puts "linked data" in the Annalist linked data notebook.  Up to this point, Annalist data has been stored and indirectly accessible as JSON, with Compact URI strings (CURIEs) used as key values for attributes.  This release augments the JSON data with auto-generated JSON-LD context files so that the JSON data can be read and processed as [JSON-LD](http://json-ld.org/#), hence loaded and processed with other data presented as RDF.

Also, the web pages for Annalist records now return links to the underlying JSON-LD data:

1. as "get the data" clickable links in the web pages,
2. as HTML `<link>` elements (with `rel=alternate` and content type attribute) in the web page header, and
3. as HTTP `Link:` headers (also with `rel=alternate` and content type attributes).

(Not implemented in this release, but intended for a future release, is HTTP content negotiation available on the primary URI for each entity record.)

Some bugs have been fixed, as noted in the version 0.1.21 summary.


## Version 0.1.21, towards 0.1.22

- [x] BUG: add a supertype while editing (copying) a new type loses any type URI entered.
- [x] BUG: create instance of type with defined type URI saves with `annal:type` value of `annal:EntityData`
- [x] BUG: renaming a group used by a view results in confusing Server Error messages (missing field)
- [x] BUG: (confusing interface) when local type/list/view overrides site definition, appears twice in dropdown lists.
    - include type/entity ids in drop-down lists; may want to review this choice later
- [x] Fix naming inconsistency: entity-data.jsonld should be entity_data.jsonld.
- [x] Content migration logic for entity-data.jsonld -> entity_data.jsonld
- [x] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [x] Add `_vocab` built-in type that can be defined at site-level for built-in namespaces like `rdf`, `rdfs`, `annal`, etc., and at collection level for user-introduced namespaces.
    - [x] Define built-in vocabularies: RDF, RDFS, XSD, OWL, ANNAL
    - [x] Generate JSON-LD context descriptions incorporating the available prefix information.
        - site context data is created during installation as part of `annalist-manager updatesite`
        - collection context is created when collection is created
    - [x] Arrange to regenerate collection context when view/group/field/vocab are updated
        - [x] Implement post-update processing hook in EntityRoot
        - [x] Move context generation functions to collection class
        - [x] Define post-update hook for vocab, etc to regenerate context
    - [x] Arrange for context to be web-accessible via Annalist server
    - [x] When generating entity data, incoporate context information
    - [x] Add context references to site data
    - [x] JSON-LD context data test case (read as RDF using Python rdflib-jsonld)
- [x] Generate site JSON-LD context data as part of 'updatesite' installation step
- [x] Ensure that raw entity JSON is HTTP-accessible directly from the Annalist server, subject to permissions (e.g. <entity>/entity_data.jsonld.  Also for types, views, fields, etc.)
    - [x] coll entity data
    - [x] coll type data
    - [x] coll list data
    - [x] coll view data
    - [x] coll field data
    - [x] coll group data
    - [x] coll vocab data
    - [x] coll user data
    - [x] site type
    - [x] site list data
    - [x] site view data
    - [x] site field data
    - [x] site group data
    - [x] site vocab data
    - [x] site user data
- [x] Test cases to ensure JSONLD contexts can be accessed by HTTP.  
    - Collection and site, with correct relative location to entity data:
    - [x] entity -> collection context
    - [x] type -> collection context
    - [x] site-defined type -> site context
- [x] Add HTTP and HTML links to data to responses.  Also, link to data on view form.
- [x] Save 'annal:type' URI value in entity that matches corresponding type data.
- [x] Closed https://github.com/gklyne/annalist/issues/19


## Version 0.1.20

This release has tackled a number of usability issues, and in particular introduces a notion of "task buttons" that provide short cuts for some commonly performed collection configuration activities:
- creating view and list definitions for a new record type
- creating field and group definitions for a repeated field group
- creating field and group definitions for displaying fields from a linked record

Other changes include:
- Simple links no longer include continuation URIs.  This means that the link URLs are more consistently usable as identifiers.
- Missing entity links are rendered in a more distinctive style.
- Closing top-level list displays no longer return to the site home page, but rather redisplay the collection default view.  This has the effect of making collections more "sticky" in the sense that a user is less likely to find they are unexpectedly looking at some completely different data collection.

It also fixes a number of bugs, including several introduced by the new logic to allow lists to include subtypes in release 0.1.18.  (This change meant that the way entity references is handled is fundamentally changed, and a few required updates were overlooked and missed by the test suite.)  See the version 0.1.19 task summary for more details.

An [Annalist tutorial](http://annalist.net/documents/tutorial/annalist-tutorial.html) document has been created.  It is still in a very drafty form, but it provides a more task-oriented desription of Annalist capabilities.  There is a generated HTML document and associated resources in directory `documents/tutorial/annalist-tutorial` of the distribution kit.  A copy has been placed online at [http://annalist.net/documents/tutorial/annalist-tutorial.html]().  A [rough rendering](https://github.com/gklyne/annalist/blob/develop/documents/tutorial/annalist-tutorial.adoc) of the latest working draft can be viewed directly from the Annalist Github repository.


## Version 0.1.19, towards 0.1.20

Usability: key tasks need to be easier (at the level of a single form fill-out):
- Create a new type+view+list, suitably interconnected
- Create repeating fields in a view
- Create multifield reference in a view/group
- See also: [#41](https://github.com/gklyne/annalist/issues/41)
- See also discussion below of introducing generic "tasks" - this would be an early pathfinder for that.

- [x] BUG: view types > view type > task button > (error) > Cancel.  Returns to type list rather than view of edited type.  Fixed up some probvlems with continuation URI generation.
- [x] BUG: extend render placement to handle list columns defined for small only
- [x] BUG: unclosed <div> in RepeatGroupRow renderer was causing formatting errors.  (Ugly but not fatal.)
- [x] BUG: `<form action="" ...>` fails HTML validation.  Use `action="#"` instead.
- [x] BUG: attempting to create new referenced entity while current entity Id is invalid gives a very obscure server error message (message with Save is sort-of OK).
- [x] BUG: Edit referenced field button in edit view doesn't work if entity type has been changed to subtype.
- [x] BUG: image with placement (0/8) displays incorrect label size.   Remove field placement options x/8 or x/9 (not sub-multiple of 12).  These widths are still allowed for columns.
- [x] BUG: "Define view+list" error when defining a new type; remember when entity has been saved and skip existence check when performing a subsequent save. Added `DisplayInfo.saved()` method.
- [x] When rendering missing entity reference in view mode, use alternative style/colour
- [x] Don't include continuation URI with entity links in list, view, etc.?
- [x] Create a new type+view+list, suitably interconnected
    - [x] Add task-button description to view description for type; use structure for repeat values: for each: Button Id, button label
    - [x] Render task buttons on view (generic logic)
    - [x] Add logic to catch and dispatch view+list task-button click
    - [x] Add logic to create/update view+list from type form data - hand-coded for now, but subsequent implementation may be data-driven.
    - [x] Create test case(s)
- [x] Create repeating fields in a view.
    - [x] Add task button to field definition form: define repeat field
    - [x] Add logic to catch and dispatch define-repeat click
    - [x] Add logic to create repeat group that references current field
    - [x] Add logic to create repeat field that references group
    - [x] Create test case(s)
- [x] Create multifield reference fields in a view or group.
    - [x] Add task button to field definition form: define field reference
    - [x] Add logic to catch and dispatch define-multifield click
    - [x] Add logic to create multifield group that references current field
    - [x] Add logic to create multifield reference field that references group
    - [x] Fix up formatting for reference field not in a repeated group
    - [x] Create test case(s)
- [x] On closing top-level list display: return to collection default view, not Home.  This has teh effect of keepinbg the user within a single collection unless they explicitly select `Home` from the menu bar.
- [x] Change "List users" heading to "List user permissions"
- [x] Initial tutorial/task-oriented documentation. Uses personal photo library example.


## Version 0.1.18

This release introduces several interface changes to address usability problems, 
bug-fixes (many associated with resource import/file upload logic), and embodies 
some fairly extensive changes to the internal code structure.

New features include:
* an option to reorder repeated field entries in a view (via move up/down buttons)
* ability to declare simple type hierarchies with different presentation of subtypes.  
Lists of a given type also include any subtypes.  
Consistent with the Annalist philosophy, type hierarchies can be adjusted 
dynamically and are not baked in to the data storage structure.
* option to edit existing referenced values from entity edit view, 
in addition to creating new values.
* in entity edit view, entity-reference dropdown lists display labels rather
than internal entity Ids, which it is hoped will lead to more user-friendly 
presentation when creating and editing entity data records.

(More details are given in the release notes change summary for version 0.1.17)


## Version 0.1.17, towards 0.1.18

- [x] Option to re-order fields on view form: add move-up/move-down buttons
- [x] Multiple URIs for type, and instances of type - add "supertypes" field
      to type description, and propagate these to the @types field of created 
      instances.
- [x] List of type also includes subtypes
- [x] Dropdowns to select value of type also presents subtypes
- [x] When using "+" to add an enum entry, also provide quick route to edit entry.
    - [x] when existing item is selected, change button label "+" to "writing hand" (&#x270D;)
    - [x] when button is clicked, edit existing value if selected.
- [x] Enumerated selection - include labels rather than Ids in dropdown

- [x] Introduce separate data-compatibility version (may lag current version).  
This means that older software may continue to work with newer data when 
no compatibility-breaking changes are introduced.
- [x] _group annal:record_type fields updated to treat grouped field 
description data as separate record type.
- [x] Confirmation message when resource is imported/uploaded
- [x] Missing enumerated value reference: provide better diagnostic
- [x] Missing enumerated value field: display diagnostic instead of blank
- [x] Remove redundant field render types (Type, List, View, Field, etc.)
    - keep entries in render_utils for backwards compatibility

- [x] BUG: if alternative field is defined for "Entity_id" (e.g. for different label), 
can't save entity, because internal expected form of field name was not used.  
When RenderType is "EntityId, force use of standard field name.  
Similar for "EntityTypeId".
- [x] BUG: if Value_entity field does not include "refer to type" value, 
barfs with 500 error.
- [x] BUG: Multifield ref inside a repeat field not occupying the entire 
width of the field generates messed up layout of labels vs content.  
Added an additional layer of row/cols for the headers of the 
multifield reference.
- [x] BUG: import resource in new entity raises internal error
- [x] BUG: import image when new or changed changed record ID gives error
- [x] BUG: import image when changing record ID causes error on save
- [x] BUG: if multiple repeated field groups are selected for deletion, 
only the last is deleted
- [x] BUG: follow links to edit view, then save, does not return to entity view.

- [x] Internal refactoring of error handling and reporting via "responsinfo" structure
- [x] Built-in `Entity_id` and `Entity_label` fields position/size values updated
- [x] Revise add field buttons to use save+redirect rather than re-render
- [x] Use responseinfo values for status reporting to user
    - changes made for save and import.
    - other changes to be applied as the need arises.
- [x] When testing site data, additional consistency check that entity type of 
repeated field matches with value type of referencing field and group
- [x] Add test cases for references to type with subtypes defined: 
check that subtype instances are also presented.
- [x] Add/update test cases for selecting entity type
- [x] Add/update test cases for selecting entity view
- [x] Add/update test cases for selecting entity list
- [x] Update site data to ensure new enumerated-value logic is tested
- [x] Small improvement of performance for collection type access
- [x] Small improvement of performance for test suite setup


## Version 0.1.16

The main advances in this release are improvement of the file upload and resource import logic, and improvements to the form rendering to make it easier to use media attachments.  One strategy adopted is to use an entity type as a "media library" to which resources can be attached, and to provide new field rendering options to reference the attached resources and associated metadata.  These new capabilities have been used to enhance the picture displays in the "CruisingLog" demo collection at http://demo.annalistr.net/ (see definitions for `DailyLog`, `Place` and `Picture`).

Other changes include:

* Support for audio clips
* General rationalization of some aspects of the form rendering logic
* More test cases
* Documentation updates


## Version 0.1.15, towards 0.1.16

- [x] create picture gallery demonstration collection to test file uploads
- [x] BUG: file upload when creating entity appears to not work; need to create first then upload.
- [x] ensure attachments are moved when entity is renamed.
- [x] test cases for upload image displayed in same entity, rename with attachments, edit entity with attachment
- [x] file upload view/edit: display uploaded filename as well as link
- [x] rename render type URIImage as RefImage; update documentation
- [x] allow multiple fields displayed from referenced entity (e.g. image for file upload).
- [x] add render type RefAudio (use embedded HTML player); update documentation
- [x] rationalize field description form to make handling of upload/import and references to fields in other entities more obvious
    - [x] Add `field_value_mode` to field description
    - [x] Add migration logic to set `field_value_mode` appropriately in field definitions
    - [x] Change some field labels
    - [x] Rename FieldDescription method `has_import_button` to `is_import_field`
    - [x] Use `field_value_mode` to determine `is_import_field` and `is_upload_field`
    - [x] Find all references to `field_value_type` and change logic to use `field_value_mode`
    - [x] Remove references to `field_ref_type` when selecting renderer (`get_edit_type`, others?)
    - [x] Remove 'field_value_type' from `FieldDescription`.  Update all tests to use 'field_target_type'
    - [x] Add 'field_value_mode' to all field descriptions in site data and some example data
    - [x] Remove `annal:Import` and `annal:Upload` as instances of `field_value_type` in site and demo data
    - [x] Update all references in code to 'annal:...' value types to use ANNAL.CURIE.... values instead
- [x] Update documentation (including README.md status summary)


## Version 0.1.14

The big change in this release is inital support for imported web resources and uploaded files within an Annalist collection.  These are captured as "attachments" to an entity via field render types `URIImport` or `FileUpload`.  The attachments can then be referenced via the entity to which they are attached, also specifiying the field property URI: see `documents/view-field-types.md` for more details.

The new facilities for presenting uploaded and imported files still need some work, and some code refactoring will be needed to make handling of such references more consistent.

A number of bugs have been fixed, and other features added or improved:

* Add logic to serve content of entity attachment in orginally submitted form.
* Add "View" button to entity edit form.  This makes it possible to show hyperlinks that can be used to access referenced entities.
* Fix some situations causing "500 Server error" messages.
* Update continuation URI if necessary when an entity is renamed.
* Added software version to collection, and refuse access if collection version is higher than current software version.
* Don't save `annal:url` value in stored entities; rather depend on its value being determined when an entity is accessed.  This potentially improves portability of data collections.
* Add documentation of view field descriptions, particularly to cover fields that are used to create entity attachments.
* Added internal support for complex field values that can be partially updated (used to support attachment metadata).
* Quite extensive code refactoring to support attachments.
* Added hooks for file format migration.


# Version 0.1.13, towards 0.1.14

- [x] BUG: invalid entity id in field data causes 500 ServerError
- [x] BUG: if field group refers back to orinal field, python blows its stack, reports 500 ServerError
- [x] Improve reporting of 500 serverError
- [x] BUG: edit from view, change id, results in NOT FOUND error displayed when returning to previous view.  This occurs because the continuation URI is refers to the old entity when the id is changed.
    - treat id/type change as special case and update all matching URIs in the continuation chain.  This involves dismantling and reassembling the continuation URI, and the continuation URL handling logic has been refactored to facilitate this.
- [x] Support for complex entity field values (e.g. supporting details for resource imports)
    - [x] Refactor entityedit Save_Entity handling
    - [x] Refactor entityedit to carry more context in viewinfo (simplify function calls)
    - [x] Refactor value decoding so it can access other form fields (to build complex values)?  (see next)
- [x] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [x] Blob and file upload support: images, spreadsheets, ...
        - [x] Choose render type name: URIImport
        - [x] Define renderer test cases as a new module in `annalist/tests/`, e.g.:
            - [x] Copy `test_render_bool_checkbox.py` to new module name
            - [x] Update descriptive comment at top of module
            - [x] Update `import` statement to refer to new module to be defined
            - [x] Update class name
            - [x] Rename and update the test case method for value rendering: this should cover value view and edit cases as appropriate.
            - [x] Rename and update the test case method for decoding input values suitable for storage in a JSON structure.
        - [x] Define a new renderer module in `annalist/views/fields/`; e.g.:
            - [x] Copy `render_bool_checkbox.py` to new module name
            - [x] Update descrptive comment at top of module
            - [x] Update class name for value mapper
            - [x] Implement value mapping as required.  If the values do not require mapping between the JSON object and form data, the class `render_text.RenderText`, which contains identity mapping functions, can be used instead.  If the renderer updates the JSON representation of existing data, consider handling legacy representations in the `encode` method to facilitate data migration.
            - [x] Rename and update the view renderer and edit renderer functions to generate appropriate HTML.
            - [x] Rename and update the get renderer function.  Note that this function must returned a `RenderFieldValue` object, as this provides the interfaces required by the rest of Annalist to render values in different contexts.
        - [x] Update entityedit.py to recognize new action to import resource
        - [x] Add tests for file import (needs to be a "full stack" test - see `test_field_alias` or `test_linked_records` for simple form of structure to follow)
        - [x] Edit module `annalist/views/fields/render_utils.py` to import the get renderer function, and add it to the dictionary `_field_get_renderer_functions`.
        - [x] Add the renderer type name to the enumeration defined in `annalist/sitedata/enums/Enum_render_type`
        - [x] Update the test modules to accommodate the new render type, and retest:
            - [x] `annalist/tests/test_entitygenericlist.py` about line 244 (bump counter)
            - [x] `annalist/tests/entity_testsitedata.py`, about line 306 (add new render type name in sorted list)
        - [x] Check the affected web views and augment the site CSS file (`annalist/static/css/annalist.css`)
    - [x] Field definition enhancements to link to uploaded file
        - [x] Design revised field definition structure to separate rendering from value reference
            - [x] Value reference direct
            - [x] Value reference as upload to current entity
            - [x] Value reference as URI
            - [x] Value reference as field of another Annalist entity
        - [x] Review existing render type definitions in light of new design
        - [x] Work out migration strategy for collections to use new field structure
        - [x] Revise field render selection logic to allow separate edit renderer selection from view renderer selection
            - Updated logic in maily in render_utils, but some interfaces are revised affecting fielddescription, etc.
        - [x] Revise field value handling to take account of multiple sources
        - [x] Figure out how to resolve relative references: based on entity URL?
        - [x] Test, test cases
        - [x] Refactor: change field names in field description. 
            - [x] s/field_options_typeref/field_ref_type/
            - [x] s/field_restrict_values/field_ref_restriction/
            - [x] s/field_target_key/field_ref_field/
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Apply updates to site data as needed
        - [x] Add logic to migrate collection data
            - [x] Add migration hook to Entity.load() method - call self._migrate_values()
            - [x] Default _migrate_values method in EntityRoot just returns with no change
            - [x] Attach migration data/method to EntityData subclasses as required.  May include common logic in EntityData method.
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Add field ref to field view form
- [x] Add 'view' button to edit form
- [x] Add file-upload option (with resulting value like URI-import)
    - Cf. https://docs.djangoproject.com/en/1.7/topics/http/file-uploads/
- [x] Serve reference to uploaded or imported resource.  Content-type and other infiormation is saved in a URIImport or FileUpload field value that is a dictionary.
- [x] Test cases for file upload
    - [x] test_render_file_upload (adapt from test_render_uri_import)
    - [x] test_upload_file (adapt from test_import_resource)
- [x] Create field definition for referencing uploaded image file - use URIlink render type
- [x] Test case for referencing uploaded file
    - [x] Similar to Import test
    - [x] View rendering test with reference to uploaded file 
        - (Use URIImage for manual test, then create test case)
        - need to extract resource_name from target field value for link...
- [x] Sort out file upload view rendering
- [x] Add test case for simple image URL reference rendering (no target link)
- [x] Add software version to coll_meta.
    - [x] Add when creating collection
    - [x] Check this when accessing collection.
        - cf. http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
            from distutils.version import LooseVersion, StrictVersion
            LooseVersion("2.3.1") < LooseVersion("10.1.2")
        - accessing collection:
            - Check version in DisplayInfo.get_coll_info()
    - [x] Update when updating collection
            - tie in to entity save logic.
- [x] Is it really appropriate to save the annal:url value in a stored entity?
    - [x] in sitedata/users/admin/user_meta.jsonld, not a usable locator
    - [x] entityroot._load_values() supply value for URL
    - [x] entityroot.set_values only supplies value of not already present
    - [x] entityroot.save() discards value before saving
    - [x] views/entityedit.py makes reference in 'baseentityvaluemap'.  Removed; tests updated.
- [x] Update documentation to cover import/upload and references.


## Version 0.1.12

The substantial change in this release is the introduction of non-editing entity views, with rendering of links to other referenced entities.  This makes it very much easier to navigate the network of entities that make up a collection.  A number of new render types have been introduced, many to support more useful data display in the non-editing view (links, Markdown formatting, etc - more details below.).  This non-editing view is now the default display for all entities.

This release also contains a number of usability enhancements and bug fixes, including:

* Save logs in root of annalist_site data, for Docker visibility.  When Annalist is running in a Docker conainer, another container can attach to the same data data volume in order to view the server logs (see the [installation instructions](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) for more information about how to do this).
* New render type: Boolean as checkbox
* New render type: URI as Hyperlink
* New render type: URI as embedded image
* New render type: long text with Markdown formatting; and new CSS to style Markdown-formatted text.
* Page layout/styling changes; rationalize some CSS usage to achieve greater consistency between the editing, non-edit and list views.
* Change 'Add field' button to 'Edit view' - this switches to the view editing page where field definitions can be changed, added or removed.
* Add 'View description' button on non-editing entity views - this switches to a display of the view description.  Subject to permissions, an 'Edit' button allows the view definition to be edited.
* View display: suppress headings for empty repeatgrouprow value.
* Preserve current value in form if not present in drop-down options.  This change ws introduced mainly to prevent some surprising effects when editing field descriptions; the change is partially effective, but there remain some link navigation issues when a field value of not one of those available in a drop-down selector.
* Various bug fixes (see below)


# Version 0.1.11, towards 0.1.12

- [x] Minor bug: in DMO_experiment, add new performer field, click "+" to define new performer, on return to previous page new field is not there.  Suspect it is because all fields are blank when "+" is clicked, so new field not saved.  Modified `views.form_utils.fieldvaluemap` to treat only `None` as non-existent field value.
- [x] Configuration change so that shell session in new Docker container can see server logs.  Save logs in root of annalist_site data.  
- [x] Non-editing entity view: [#3](https://github.com/gklyne/annalist/issues/3)
- [x] New render type: Boolean (checkbox) [#2](https://github.com/gklyne/annalist/issues/2)
- [x] Document process for creating and integrating a new renderer
- [x] New render type: Link (hyperlink) [#2](https://github.com/gklyne/annalist/issues/2)
- [x] New render type: Image, [#2](https://github.com/gklyne/annalist/issues/2)
- [x] Extend CruisingLog example data with image galleries for place and daily log entries
- [x] New render type: Markdown, [#2](https://github.com/gklyne/annalist/issues/2)
    - [x] Markdown test cases
    - [x] Markdown renderer
    - [x] Fix up CSS for Markdown formatting; e.g.
        - div.columns.view-value > span.markdown p
        - div.columns.view-value > span.markdown li
        - div.columns.view-value > span.markdown h1
        - div.columns.view-value > span.markdown h2
        - div.columns.view-value > span.markdown h3
        - div.columns.view-value > span.markdown h4
    - [x] Update Annalist dependencies to include markdown package
    - [x] Update site data to use Markdown where appropriate 
- [x] Fix styling (row spacing) for site front page - it looks a bit spaced-out following changes to view/list styling.  probably just needs appropriate new CSS classes to be included.
- [x] Beside the "Add field" button, include "Edit view" button on entity editing page.
- [x] BUG: RepeatGroupRow field without Group Ref specified gives 500 error when view is displayed
- [x] BUG: no substitute if add/remove labels not supplied
- [x] Field placement lacks 0/9, 3/9, 0/8, 4/8, 3/6 options
- [x] Provide image click-through to larger version.
- [x] Replace the "Add field" button with an "Edit view" button
- [x] Add "Edit view" option to view as well as edit form
    - View description doesn't carry the entity Id to the continuation URI (None instead)
- [x] View display: suppress headings for empty repeatgrouprow value
- [x] Entity drop-down selectors: add current value to list if not already present
    - (avoids hiding information if type URI changed and field type is no longer offered)
    - Done, but when a field is not available for a view, there is no link provided to edit it.


## Version 0.1.10

This release contains a number of usability enhancements and bug fixes, including:

* Option to create new linked record from referring record view.  This means, for example, when creating a view description that the field selector drop-downs have an additional "+" button that can be used to create a new field type definition.  This feature is provided for all enumerated value fields that refer to some other entity type.
* Add field alias option.  This allows record-specific fields to be returned as the value for some other property URI;  e.g. in bibliographic records (`BibEntry_type`), the `bib:title` field can be used for `rdfs:label` values, and hence appear in views that expect `rdfs:label` to be defined.
* When changing a list view, don't filter by entity type.  Previously, when listinging (say) all `_type` entities, and changing the list type to `View_list`, no entries would be displayed because of conflicting entity selection criteria.
* Use more obvious interface for displaying collection only vs collection+site entity listings.  Previously used an explicit type id in the URI to display collection+site data; now uses `View` vs `View all` buttons to display collection-only or collection+site data respectively.
* Use placholder as descriptive label for repeated group form display.
* Implement special renderer for field placement (position/size)
* Rework handling of repeated use of same field.  In previous releases, having the same field type appear more than once in a view description could lead to unexpected happenings when editing an entity.  This is now fixed by ensuring that a unique property URI is used for each one.
* `annalist-manager` enhancements; permissions help, new information subcommands
* Document default admin user permissions created with new site
* Various bug fixes
* Form display and response code refactored to make code easier to undertsand, and ease future maintenance and exhancement of the code base.
* Refactor field rendering logic for better support of more complex field rendering options (cf. field placement).
* Added build scripts for Docker containers, and add Docker-based installation instructions.


## Version 0.1.9, towards 0.1.10

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
- [x] BUG: ID too long is accepted but then can't access (404 response).  Need to id validity check before saving.
- [x] Refactor button locating logic in edit form response handler
- [x] Refactor and clean up entity save code in edit form response handler
- [x] Review field description is_enum_field - use `has_new_button` for fields with `new` button
- [x] review field description and detection of repeated field-group references. 
- [x] Select new list view: drop type_id from URI? (e.g. when changing to view of different type)
- [x] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  The current mechanism of using an explciit type to display site-wide values is probably confusing.
    - Implmentation adds 'scope' flag to list URIs (!all), and adds "View all" button to list views to select the wider scope.
- [x] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] Consider removing "New type", "New view" and "New field type" buttons, but keep corresponding test cases so they can be reinstated).  Tie logic in to new enumerated-value handling.
    - [x] refactor logic for new-entity from entity edit view
    - [x] rename 'View_repeat_fields' back to just 'View_fields'
    - [x] hide new type, view, field type buttons in edit template
- [x] Usability issues arising from creating cruising log (see next item)
    - [x] 'Add field' can't be followed by 'New field' because of duplicate property used
        - consider using Enum_optional logic so the field selector id isn't automatically filled in;  ignore blank field ids when processing;  ensure field with blank id is still saved with view/group.
        - chosen fix is to auto-generate a property URI in the view description based on the field property URI but with a _2, _3, etc suffix.  If there is an existing view-defined property URI that clashes, reject the update as now.
        - what to do if the render type is changed?  Ideally, remove any auto-generated property URI, but preserve manually entered values.
    - [x] Entity edit view: "New field" -> "New field type"
- [x] BUG: save entity where view has same field id with different properties is not working properly.  Second value is saved to both fields.  It turns out the field property URI in view description is only a partial fix to the duplicated fields problem, and the approach needs to be re-thought.
    - [x] Verify problem in test case - TestEntityEditDupFieldTest
        - [x] Create a view with duplicate field id
        - [x] Create entity with values for duplicate field id - the exact representation will be up for grabs.  For now use suffix for those after the first - later may consider using a list of values.
        - [x] Render entity in view, check context used to generate form.
        - [x] Submit form with values for duplicate fields.  Again, the exact representation will be up for grabs, but for now use a suffix for fields after the first.
        - [x] Will need function to create test entity data with dup field vals; this will isolate representation of dup fields in an entity
        - [x] Will need function to create test form data with dup field vals; this will isolate representation of dup fields in a form
    - [x] Fix problem.
        - [x] Introduce suffix into FieldDescription when building EntityValueMap.
        - [x] Update field_name and field_property_uri values to include suffix.  Also add acvcess functions.
        - [x] No error if field definition is repeated in view (or group).  (Good - that code was pig ugly!)
        - [x] FieldListValueMap invoke conflict resolution logic in FieldDescription.
        - [x] Where possible, replace direct access to field name and property URI to use new access methods.  (bound_field still uses direct indexing because test code uses faked FieldDescription structure.)
- [x] RepeatGroup renderer - use placeholder beside label as way to explain content?
- [x] Implement renderer for field placement field
- [x] Revise tokenset renderer to follow field placement pattern; get rid of encode/decode methods?
- [x] Rationalize storage of repeat_prefix in context: top level or under 'repeat'?
- [x] Review options for creating user accounts in development software version (currently have 'admin'/'mailto:admin@localhost' in sitedata as holding option).  Put something explicit in makedevelsite.sh?  Document site 'admin' user and development setup?
    - For now, sticking with admin user entry in initial site data.  Updated install document.
- [x] Remove `/annalist_root/sampledata/data/` from distribution kit data so that test suite can run in Docker container.  (Otherwise, can't rename old data directory due to "Invalid cross-device link" error)
- [x] `annalist-manager` help to provide list of permission tokens
- [x] `annalist-manager` createsitedata should also create collections directory
- [x] `annalist-manager` option to write version string to stdout
- [x] docker installation files and scripts, and docker container available from dockerhub
- [ ] Installation instructions need to be clear (and tested) about ordering of create, initialize, defaultadmin
    - final check when creating new release.


## Version 0.1.8a

This is a patch release for bug https://github.com/gklyne/annalist/issues/39.  This bug causes a server error to be reported if a user logs in with an ill-formed user_id.

## Version 0.1.8

The main new feature in this release is full support for views containing repeated fields (e.g. a bibliographic entry containing multiple authors).  These can be displayed as a repeating group of fields formatted similarly to non-repeating fields (`RepeatGroup` render type) or as a repeating row of values with column headings (`RepeatGroupRow` render type).  With this enhancement, the core web presentation engine is substantially complete, with further capablities to be provided by adding new field renderers.

Other changes are a substantial reworking of the form-generating and handling engine used for data display and entry, numerous small bug-fixes and enlargement of test coverage.

Summary of other improvements and bug-fixes:

* Added field groups as part of support for repeating fields in a data view.
* Updated sample descriptions of bibliographic data to use repeatinbg field groups, to fully support BibTeX/BibJSON-like structures.
* Update annalist.net demo site front page (see `documents/pages`).
* New test suite to check completeness and consistency of site-wide data.
* Fixed some bugs in field type selection when editing view descriptions.
* View generating code regorganization and rationalization.  Most of the HTML form-generating code is now in a separate code directory.
* Unification logic used to generate entity list displays and repeating fields in an entity view/edit form.
* Formatting, generated HTML and CSS changes; eliminate use of HTML `<table>`.
* Fix server error when copying view without URI field (also hotfix 0.1.6a).


# V0.1.7, towards V0.1.8

TODOs completed:

- [x] Add "get the data" button to annalist.net page: https://github.com/BetaNYC/getDataButton
- [x] Extend form-generator capabilities [issue #2](https://github.com/gklyne/annalist/issues/2)
    - [x] Revise representation of repeat field structures in view description: repeat description to be part of root of repeat structure, not an ad hoc field at the end.  This should remove some special cases from the code.
    - [x] Refactor handling of repeat field groups
    - [x] Define type for field group (_group?  Or use _view?)
    - [x] Use _list rather than _view? (NO: list has much more bound-in semantics)
        - NOTE: in debugging, a new built-in type has been introduced to provide better control over UI elements.
    - [x] Rename 'View_field' to (say) 'View_field_view' (cf. previous use _list)
    - [x] Define view for field group (list of fields)
    - [x] Define list for field groups (not needed as views used for field-groups)
    - [x] Redefine view with list of fields?  Not if that impacts usability.
    - [x] Define e-v-map for defined list of fields
    - [x] Repeat to reference list of fields 
- [x] Eliminate duplication with list view - rework list to use same repeating mechanism as view
- [x] Provide clean(er) mechanism to propagate extra context to bound fields in repeat group rendering
- [x] Try eliminating `view_context` parameter from `FieldListValueMap` constructor
    - it turns out that it's needed for generating enumerated type lists based on target type of view, but code has been rationalized and slightly simplified and relevant comments added.
- [x] Use distinguished names for internally-generated context keys (e.g. '_fields')
- [x] Simplify list template now that repeat fields are handled by a field renderer
- [x] Make mapping classes more consistent in their return types for sub-context values
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
    - [x] Introduce new render type RepeatGroupRow, sharing code with RepeatGroup
    - [x] Move row selection from template (uses .item) to editlist (uses RepeatGroup)
    - [x] Work through field rendering options for RepeatGroupRow:
    - [x] Rework field description used by view view to use new field rendering options
- [x] merge rework-form-manager to develop branch
- [x] Bugfix: e.g. 'Bib_person_field_view' does not show appropriate field options
- [x] Bug: create field group does not show up on field group list
- [x] Need test coverage for FieldDescription with a field group
- [x] Tests for sitedata: using Beautifiul soup (maybe), create table-driven tests for checking field contents for various rendered pages (lists and views), abstracted away from finer details of rendering and layout.  For example, test that correct field options are displayed for different views.
    - [x] Move site data functions from entity_testentitydata to entity_testsitedata
    - [x] Add functions for groups
    - [x] Define new test_sitedata module with functions for testing values in view rendering via BeautifulSoup
    - [x] Create test cases for each of the main views on site data
    - [x] Remove tests from other test sites that duplicate these tests (esp test_record* tests) (do this later, progressively)
- [x] Test software installation from merged branch
- [x] Hand-test new capabilities to define view with repeating fields - make sure it is doable
- [x] Test adding more data to cruising log sample data
- [x] Rename: Field_sel Group_field_sel (option for Field_group_view only)
- [x] Copy: Field_property, Field_placement -> Group_field_* (options for Field_group_view)
- [x] Test upgrade of existing deployment
- [x] Deploy updates to annalist.net


## Version 0.1.6

The main new feature in this release is an authorization (access control) framework;
There are also numerous small improvements and bug-fixes:

* Implemented authorization framework
* Updated `annalist-manager` to set up initial/default perissions needed to start working with Annalist
* More new commands in `annalist-manager`
* List view option to hide columns on smaller screens (cf. permissions)
* Extend test suite covereage
* When adding field to view: check property URI is unique
* Documentation updates and new screencasts
* When renaming type, rename insrances to new type
* Prevent deleting type with instances present
* If specified default list not found, revert to built-in default
* Fix bug in entity reference field links (was linking to self, not target record)
* Add optional enumeration to available field render types
* Use separate Django database for each configuration
* Improve log file handling; include timestamps
* Some small usability improvements
* Address some areas of technical debt

## Version 0.1.5

TODOs completed:

- [x] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
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
- [x] Default button on view edit form (and others) should be "Save".
    - See http://stackoverflow.com/questions/1963245/.
    - I found adding a duplicate hidden save button at the top of the <form> element did the trick.
- [x] List view: option to hide columns on smaller screens (cf. permissions)
- [x] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
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
- [x] Flesh out the user documentation
- [x] record new demo screencasts
- [x] Seems to be a problem renaming a type for which there are defined values: need to rename the typedata directory too.  See Issue [#34](https://github.com/gklyne/annalist/issues/34)
- [x] Create new type: leave type URI field blank.
- [x] BUG: if default list description is deleted, collection cannot display.  Should revert to default default? [#36](https://github.com/gklyne/annalist/issues/36)
- [x] BUG: deleting type with existing records causes Server Error 500.  [#34](https://github.com/gklyne/annalist/issues/34)
- [x] Clean out old code, especially check @@TODOs in `entityedit.save_entity`
- [x] Test creation of cruising log (again) using real log data
    - [x] BUG: place name links to daily log record, not place record [#37](https://github.com/gklyne/annalist/issues/37)
    - [x] Provide option for optional enumerated value in field definitions (Enum_optional per render_utils)
- [x] Use separate Django database for each configuration
- [x] Think about how to handle change of email address (option to remove user from Django database?)
    - annalist_manager now has deleteuser option
- [x] Include date+time in log entries


## Version 0.1.4

Cleaning up some simple bugs and presentation problems.

From here on, use convention of even numbers for stable sub-releases and odd numbers for working versions.

* Post-release documentation updates
* Update annalist_manager with updatesitedata command and to create auth providers directory
* Updated field view definition to include extra fields used for enumerated type displays, etc.
* Updated view editing form description.
* Update field and view description of fields to restrict presentation of field choices
* Fix problem of ignoring blank value in submitted form (issue #30)
* Use collection and list labels for headings on entity list page (issue #26)
* Clean up page and section headings in record editing view
* Change confusing 'Select' label of field id (Field_sel) dropdown in view description
* Initialize entity label and comment to blank (issue #24)
* Fixed problem with rename locally created Default_view (issue #22)
* Fix that changing type of entity was not deleting old record (issue #29)

### TODOs completed for 0.1.4

- [x] annalist-manager option to update site data, leaving the rest untouched
- [x] annalist-manager initialize: needs to create `.annalist/providers` directory [#27](https://github.com/gklyne/annalist/issues/27).
- [x] Update view and field descriptions [#16](https://github.com/gklyne/annalist/issues/16)
    - [x] extend field edit form to include additional fields used.
    - [x] extend view edit form to include additional fields used in sitedata (i.e. record_type)
    - [x] add more 'annal:field_entity_type' constraints for fields that are intended to be used only with specific entity types (e.g. fields, views, etc.)
    - [x] List view also needs 'annal:field_entity_type' to control selection
        - [x] Add field manually to internal list descriptions
        - [x] Add field to List_view
    - [x] Remove "Default_field"
- [x] Blank value in submitted form is ignored [#30](https://github.com/gklyne/annalist/issues/30)
- [x] List headings are clutter [#26](https://github.com/gklyne/annalist/issues/26)
- [x] Clean up page and section headings in record editing view
- [x] 'Select' label for field type is un-obvious [#25](https://github.com/gklyne/annalist/issues/25)
- [x] New entities are initially populated with useless junk [#24](https://github.com/gklyne/annalist/issues/24)
    - initialization logic is in models.entitytypeinfo.get_initial_entity_values
- [x] Change type of entry doesn't delete old record [#29](https://github.com/gklyne/annalist/issues/29)
    - [x] Fix bug in entityedit (not usinjg new type info to check existence of renamed entity)
    - [x] Fixed gaps and bug in test code
- [x] Can't rename locally created Default_view [#22](https://github.com/gklyne/annalist/issues/22)
    - [x] Fix up default action resulting from click on link may need to change later when read only views introduced
    - [x] Additional authorization check if Save called with unexpected action
    - [x] Update authorization reporting to say what access (scope) was requested, rather than HTTP method

## Version 0.1.3

* First public prototype release

## Version 0.1.2

* Test with Django 1.7
* Initial installation kit
* Apply sorting to entity lists to make test cases more robust across systems
* Setup scripts to initialize installation and site data
* Fix problem with local logins
* Various minor page presentation changes
* Access root URI path ('/') redirects to site display
* Add some online help text for site, collection front pages, and login page
* Resolve virtualenv problem on Ubuntu 14.04
* util.removetree hack to allow test suite to run on Windows
* Initial documentation
* Demonstration screencast

## Version 0.1.1

* Feature freeze
* See below for summary of history to this point

## Initial public prototype outline plan

Initially guided by mockups per https://github.com/gklyne/annalist/blob/master/documents/mockup/Annalist.pdf?raw=true

1.  Front page/initial display
    * [x] form elements to create new collection
    * [x] form elements to delete collection
    * [x] include supporting logic in Collection module
    * [x] rework authentication/authorization to allow unauthenticated access for public data 
    * [x] test cases for site, site views; refactor tests to separate directory, modules
    * [x] adopt responsive CSS framework (Foundation)
2.  Collection display
    * [x] refactor metadata field access to common superclass
    * [x] types
        * [x] implement skeleton RecordType module
        * [x] create test cases for types in collection
        * [x] implement type methods
    * [x] views
        * [x] implement skeleton RecordView module
        * [x] create test cases for views in collection
        * [x] implement view methods
    * [x] lists
        * [x] implement skeleton RecordList module
        * [x] create test cases for lists in collection
        * [x] implement list methods
    * [x] UI test cases
    * [x] form elements to add/delete types/views/lists/...
    * [x] Add CollectionActionView test cases (handled with entity managed)
3. Record type display
    * [x] template
    * [x] view: edit form display
    * [x] view test cases
    * [x] refactor redirect_info, redirect_error in generic view to takle URI rather than view name parameter, and add new method to handle URI generation from view name + params.
    * [x] model
    * [x] model test cases
    * [x] view edit form response handling
    * [x] refactor code locally
    * [x] more refactoring; try to abstract common logic for RecordList, RecordView
    * [x] review generic view base functions - should some be inlined now?
    * [x] Move types/views/lists data into _annalist_collection directory
4. Default record view/edit display (code to be refactored later)
    * [x] form generation
    * [x] form display test cases
    * [x] provision for data access fallback to site data (for types, views, fields, etc.)
    * [x] form response handler
    * [x] test cases
    * [x] refactor URI and test data support for test cases to separate module; use reverse for URI generation; 
    * [x] refactor DefaultEdit form display
    - [x] WONTDO: isolate directory generation for tests.
    * [x] change <site>/collections/ to <site>/c/ or <site>/coll/ throughout.
    - [x] WONTDO: Similar for /d/ and /data/?
    * [x] include path values in entities.
    - [x] WONTDO: include base and reference values in entities. (later: requires use of @context)
    * [x] create data view display based on generic render logic
    * [x] editing recordtype: returns "already exists" error; display operation (new, copy, edit, etc) in edit form
    * [x] function to create initial development site data (based on test code)
    - [x] WONTDO: entity should carry its own RecordType id (where it's kept within a collection).  Have implemented alternative mechanism through bound_field that allows the entity to be less self-aware, hence more easily ported.
    * [x] menu dropdown on small display not working: need JS from Zurb site? (fixed by update to 5.2.1)
5. Default record list display
    * [x] form generation
    * [x] form display test cases (initial for default and all)
    * [x] include sitedata lists in drop-down
    * [x] form response handler (delete and others todo)
    * [x] entity list view: add selection fields (and classes)
    * [x] form response test cases
    * [x] customize response handler
    * [x] new entity from list-all display; changing type of entity
        * [x] Create default type in site data
        * [x] Create field render type for drop-down (render_utils and field template)
        * [x] Add field to default display
        * [x] Add type list data to display context
        * [x] Add original type as hidden field in edit form
        * [x] Add logic to form submission handler
        * [x] add test cases for changing type id (new and edit)
        - [x] WONTDO: remove recordtypedata access from entityeditbase.get_coll_type_data to POST handler (for recordtype, etc., the collection object is supplied as parent, so this is not so simple.)
        * [x] remove return_value from field definitions - this is now handled differently
        * [x] new record from list all: use default type, not random selection
        * [x] new record, change type, error doesn't redisplay types
        * [x] error loses continuation URI in edit form
        * [x] remove message header that appears on return from form edit (appears to be resolved?)
        * [x] review skipped tests - can any be enabled now?
        * [x] delete entity continues to wrong page
    * [x] add entity links to list views
        * [x] Update bound_field to provide access to entity URI
        * [x] Create field render type for entity ref
        * [x] Update field in default list displays
    * [x] connect site display to default display of entities, not customize
    * [x] connect list display to record view display
    * [x] build entity selector logic into list view
6. Generic entity edit view
    * [x] extract/generalize relevant logic from `defaultedit.py`
    * [x] parameterize view-id on extra URI field
    * [x] create new URI mapping entries
    * [x] create new test suite for generic edit view
    * [x] refactor defaultedit.py as special case (subclass?)
    * [x] fix urls.py error and re-test
7. Generic record list display and editing
    * [x] extract/generalize relevant logic from `defaultlist.py`
    * [x] refactor defaultlist.py as special case (subclass?)
    * [x] parameterize view-id on extra URI field
    * [x] create new URI mapping entries
    * [x] create new test suite for generic list view
        * [x] choose test scenario: Field definitions: http://localhost:8000/annalist/c/coll1/d/_field/ 
        * [x] list field descriptions?  Need to create list description (4 fields?).  http://localhost:8000/annalist/c/coll1/l/Fields_list/_field/
        * [x] also choose / define default view for list (Create field view?)
        * [x] need to rationalize entity display structure to encompass data, collection level metadata and site-level metadata.
        * [x] check list display in dev app
        * [x] define test suite test_genericentitylist based loosely on test_entitydefaultlist
        * [x] create test case for creating/editing site metadata entities (currently fail in dev system) e.g. create test_entitymetadataedit based on entitygenericedit.
        * [x] create edit view tests for all the main entity classes (type, view, list, data), along the lines of test_entityfieldedit, moving support code out of entity_testutils.
            * [x] copy/refactor test_recordtype to use same pattern as test_entityfieldedit
            * [x] see if old record type view class can be deleted
            * [x] incorporate model tests in test_entityfieldedit (cf. test_recordtype)
            * [x] rename test_entityfieldedit -> test_recordfield? (cf. test_recordtype)
        * [x] resolve overloading of "entity_uri" in context.
    * [x] entity_uri appears in entity view context as name (same as annal:uri) but also in bound field as locator.  Change name used in bound field to `entity_ref`.
    * [x] refactor delete confirm code to generic module, with type-specific messages.  Note that type, view and list deletes are triggered from the collection edit view, with different form variables, and also have specific remove functions in the collection class, so need separate implementations (for now?).
    * [x] update render template/logic for RecordView_view
    * [x] update template to include delete field options; finalize form response data
    * [x] implement tests for add/delete fields
    * [x] implement handlers for add/delete fields
    * [x] edit form response should update, not replace, any data from the original (so data from multiple views is not discarded).
    * [x] implement delete confirm view for views and lists.
    * [x] review missing tests: implement or delete?
    * [x] fix up view links from list display
    * [x] define View-list and List-list
    * [x] view button handler from list display + test
    * [x] continuation handling: replace by more generic parameter handling based on dictionary; move handling of escape logic, etc.
    * [x] search button handler from list display
    * [x] consider that 'Find' and 'View' buttons could be combined
    * [x] don't include continuation-uri param when URI is blank
    * [x] implement some version of entity selection logic
    * [x] decide how to handle presentation of field types (where?): (a) use simple text string, not CURIE; (b) use CURIE, but use render type to extract ID; but will need to map back when form is submitted?
        * [x] it all rather depends on the anticipated extensibility model for field types.  Option (a) is simplest for now.
    * [x] default_view response handler (needs generic view to make sense)
    * [x] implement view- and list- edit from collection customization page
    * [x] implement per-type default list and view
        * [x] already works for list view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/
        * [x] but not yet for entity view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/type1/
        * [x] return list_info structure rather than saving values in object. 
    * [x] consider replicating list_seup logic for view_setup.
    * [x] find and eliminate other references to get_coll_data, etc.
    * [x] don't return placeholder text in a form as field value; use HTML5 placeholder attribute
    * [x] refactor fields package as subpackage of views
    * [x] fix entity links to use default view URI (/d/...)
    * [x] List type + "View" selection uses // for type field - select based on list or suppress
    * [x] customize > edit record view > add field > cancel -- returns to wrong place.
    * [x] need test case for remove field with no field selected
    * [x] factor out add-field logic used by current add-field code
    * [x] test case for POST with 'add_view_field'
    * [x] provide option to invoke add-field logic during initial form rendering
    * [x] add_field button on entity edit displays; need way to control its inclusion
    * [x] new entity initialization vector through typeinfo, AND/OR provide mechanism to associate initial values for each entity type.
    * [x] "Add field" when creating new entity results in multiple entities created (use !edit for continuation URI?)  Add test case.
    * [x] tests
        * [x] skipped '@@TODO defaultlist default-view button handler'
        * [x] skipped '@@TODO defaultlist search button handler'
        * [x] skipped '@@TODO genericlist default-view button handler'
        * [x] skipped '@@TODO genericlist search button handler'
            * [x] annalist.tests.test_entitygenericlist.EntityGenericListViewTest
        * [x] skipped '@@TODO genericlist default list button'
            * [x] annalist.tests.test_entitygenericlist.EntityGenericListViewTest
8. initial application testing
    * [x] review and simplify bound_field logic for accessing field_value
    * [x] Create new type - appears twice in default_list_all display.  Delete one deletes both appearances, so this looks like display problem.  I thought this had been fixed.  Confirmed to be knock-on from incorrect creation of _type data (see next).
    * [x] New entry save as _type does not create new type in collection
    * [x] field view has size/position field; use as default when adding to view.
    * [x] viewing new entity with custom type generates "keyerror annal:value_type" @ fielddescription.py line 55.
    * [x] update field view description to display all relevant fields; ???
    * [x] when defining a field, the render type selected also implies a field value type; handle this in "FieldDescription constructor?"  Later, maybe.  For now, add value type field.
    * [x] make FieldDescription constructor more resilient to missing data.
    * [x] Changing type to built-in type in entity edit display does not save to correct location
    * [x] List editing view formatting is messed up (small-6?)
    * [x] Click on local type in default_list, then cancel, returns to Type_list display.  No continuation_uri in links.
    * [x] Click on local record in Default_list, cancel, returns to default data display (/d/ rather than /l/).  In default display, types don't appear.
    * [x] grey out set_default button on collection default display (/d/, /l/)
    * [x] When creating new collection, there's no obvious way to create a new record type (or view).
    * [x] Handle bare /l/ URI and redirect to default view for collection
    * [x] Remove precalculated list_ids and view_ids from view context
    * [x] Script to refresh sitedata in devel site
    * [x] In view editing, provide field id drodown
    * [x] In list displays, hyperlink entity type to view/edit form
    * [x] No easy way to create field description while editing view details; include new-field button
        * [x] update form template
        * [x] implement handler for 'new_field' response
        * [x] implement test case for 'new_field' response
        * [x] list description view not showing types or views in dropdowns
        * [x] introduce Default_field type
    * [x] When defining field, missing placement is silently ignored; field is not saved; (still)
    * [x] Authorization of field editing is not handled consistently:  allows config when no delete authz (no login)
    * [x] Display of remove-field checkbox based on "delete" permission. 
    * [x] Save entity edit is not requiring login - should check from POST?
    * [x] Entityedit add test cases for unauthorized config requests (and more?)
    * [x] From type display, want easy retreat to default display for collection
    * [x] View_type display should suppress add-field option.  Similar for View_list and View_field?
    * [x] suppress _initial_values as option when selecting type/view/list
    - [x] WONTDO: Add field allows new view type to be created, but how to make this default for displayed type?
    * [x] Generic field renderer for entityref as selection among available entity ids.  Use for field selection.  Options should be reworked using this form of enumeration, handled on the fly as required, using type information from the field definition.
    * [x] Type view should have dropdowns for default view and list
    * [x] List view selector syntax isn't working: need to nail down how type selection can work.  In saved data, I'm seeing '"annal:type": "annal:EntityData"', which isn't realy helpful.
        * [x] change all references to annal:type to @type, in sitedata and code (i.e. URIs/CURIE values).  E.g. annal:Type, annal:View, annal:EntityData, etc.
        * [x] for annal:type, assign local type_id value.  Consider renaming as annal:type_id.
        * [x] annal:type is retained for URI/CURIE of entity class (is this helpful?)
        * [x] list type selectors then use local type_id values.
    - [x] WONTDO: @type list selector - allow selection by type substring - e.g. coll/type
    * [x] When not logged in, should still have option to select a different view
    * [x] From list view, continuation URI for new, copy, etc should exclude message parameters.  In particular, links in rendered fields have the extra stuff.  (But do include ?search param)
    * [x] Customize > delete record > confirm : returns to wrong place
    * [x] Generalized enumeration types
        * [x] Define new RecordEnum class with type_id parameter on constructor; dynamically created directory paths; dynamic class creation?
        * [x] Test cases for RecordEnum
        - [x] WONTDO: Add optional type_id to all entity constructors (ignore on existing)
        * [x] Update entitytypeinfo to support enum types
        * [x] More test cases?
        * [x] Review, rationalize type naming and type ids.  Update sitedata.
        * [x] Update list type field definition
        * [x] Update tests using list type field definition
        * [x] Create type records for enumeration types, used for:
            - locating the default view and/or list id for records of that type
            - getting entity @type URI/CURIE values while editing
            - getting a view/edit link to type record
            - See notes in models.typeinfo
    * [x] Enumeration type for list types (list/grid: default list)
        * [x] Update field definition
        * [x] Create type record
        * [x] Update/add tests cases
    * [x] Enumeration type for field render types (text, testarea, etc...); use in fields display
        * [x] Create enumeration data
        * [x] Update field definition
        * [x] Create type records
        * [x] Update/add tests cases
        * [x] development test site is broken - why?  Isolate problem in test before fixing.
    * [x] allow '//' comments in JSON files - strip out before parsing JSON (but leave blank lines)
    * [x] Don't show Bib_* fields for non-biblio record types 
        - [x] WONTDO: Move Bib_* fields to separate "built-in" collection
        - [x] WONTDO: Can enumeration-like logic be used to support sub-areas in site data?
        * Long term is to move Bib_ field types out of site data, and provide easy way to incorporate library fragments into new collections, but for now they are part of the test environment.  See below.
        * Alternative might be value-scoped enumerations
        * [x] Update EntityFinder logic to support tests comparing with enclosing view fields
        * [x] Update entity selector call site (just one)
        * [x] Update selector syntax and sitedata
        * [x] Use EntityFinder logic in enumeration selection (FieldDescription.py)
        * [x] Add view context to FieldDescription
        * [x] Introduce biblio record type
        * [x] Introduce biblio record list
        * [x] Update test cases
        * [x] Field name updates (field_render, value_type)
        * [x] Update test cases
        * [x] Add fields to restrict bib_* fields to BibEntry views
            - [x] WONTDO: Declare additional/multiple types for entity?
        * [x] Update field selector view
        * [x] Use field selector in FieldDescription
        * [x] Update test cases
9. Prepare for release 0.1
    * [x] feature freeze
    * [x] version identifier in system
    * [x] remove dead code
    * [x] test with Django 1.7
    * [x] installation package
    * [x] test installation on non-development system
        * [x] sorting of enumeration lists
        * [x] sorting of entity lists (by typeid then entityid)
        * [x] sorting of entity lists enumerated in tests
        * There could be more test cases that need hardening, but so far all pass on a Linux deployment
    * [x] check python version in setup
    * [x] __init__.py in annalist_root dir causes test failure on Ubuntu 14.04; cf. https://code.djangoproject.com/ticket/22280.   Removing it solves the test case problem, but it was included originally to get the setup.py script to work as intended.  Try removing it and see if we can get kit builder to work.
    * [x] Login page - link to local Django login & admin pages
    * [x] Fix profile display with local credentials
    * [x] Logged-in username should appear in top menu; e.g. xxxx profile or xxxx: profile logout
    * [x] root URI - redirect to /annalist/site/
    * [x] utility/script for running tests
    * [x] utility/script for site creation
    * [x] utility/script for running server
    * [x] online help text (initial)
    - [x] WONTDO: Test installation on Windows (De-prioritized for now. Tests pass, but having problems accessing the settings when running the server. Change directory?)
    * [x] Documentation
        * [x] release notes/introduction;  link from README (about this release); key missing features/issues
        * [x] installation - link from README
        * [x] getting started - reference installation then walk through demo sequence; link from README (getting started);
        - [>] demo script (needs cleaning up)
        * [x] using Annalist - flesh out; link from README
        * [x] flesh out introduction/overview
        * [x] how to setup OpenIDConnect providers - move to separate document; link from installation doc
        * [x] tidy up README
        * [x] Move remaining TODOs to Roadmap and issues
        * [x] Flesh out roadmap
    * [x] Create mailing list -- see https://groups.google.com/forum/#!forum/annalist-discuss
    - [>] Demo deployment
    * [x] Demo screencast -- see http://annalist.net
    - [x] Add TODO list to release notes, and reset
    - [x] Bump version and update history
    - [x] Update version number in scripts, documents, etc.
    - [x] Post updated kit download
    - [x] Update front page link at annalist.net
    - [x] Upload to PyPI
    - [x] Final updates to master
    - [x] Post announcement to Google Group, and elsewhere

