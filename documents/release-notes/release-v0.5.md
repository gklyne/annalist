# Annalist v0.5 release notes

Annalist release 0.5.x is a candidate feature-complete minimal viable product for an eventual version 1 release.

A summary of issues intended to be resolved for product release can be seen in the [issues list for the first alpha release milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).  See also the file [documents/TODO.md](https://github.com/gklyne/annalist/blob/develop/documents/TODO.md) on the "develop" branch.


## Current release: 0.5.4

This release contains some significant changes to simplify workflows used when creating definitons that use structured ontology terms, based on some experiences using Annalist to create CIDOC CRM data.  It also provides options for generating Turtle data output.  There are numerous bug fixes, which are described in the notes below for release 0.5.3.

Specific visible changes include:

* Turtle data output for entities and entity lists, to make it easier to share Annalist data with other linked data applications.
* New facility to create a subtype with key values inherited or derived from the parent type.
* Revised creation of view and list definitions for a type, to work more easily for subtypes.  Fields from existing type view and list definitions, or from the default view and list definitions, are copied into the new definitions created.
* Changes to help text, diagnostics and other messages.

There is some extensive internal refactoring in the view logic used to generate data outputs, and the links used to access data outputs.


## Status

The Annalist software is now believed to offer a level of functionality that will be incorporated in an initial full software release.  The primary goals of Annalist are to make it easy for people to create and share linked data on the web, without programming:

* Easy data: out-of-box data acquisition, modification and organization of small data records.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data on the web, with links in and links out.

Key features implemented:

* Simple installation and setup procedure to quickly get a working installation
* Highly configurable form interface for entering, presenting and modifying data records, built using self-maintained configuration data.  The core presentation engine is substantially complete, but additional field renderers are still required to support a wider range of basic data types.
* Grid-based responsive layout engine (currently using Zurb Foundation)
* File based, versioning-friendly, textual data storage model;  data design is RDF-based, and uses JSON-LD elements.  JSON-LD contextx are automatically generated as needed for each collection to allow ingest as RDF.
* Ability to create new entity record types, views and listing formats on-the-fly as data is being prepared
* Authentication with 3rd party IDP authentication (current implementation uses OAuth2/OpenID Connect, tested with Google, but should be usable with other OpenID Connect identity providers).  (Note access control is separate.)
* Authorization framework for access control, applied mainly per-collection but with site-wide defaults.
* Support for uploading, importing and linking to, and annotating, binary objects such as images.
* Image rendering
* Audio clip rendering (via HTML5 capabilities)

Intended core features not yet fully implemented but which are under consideration for future releases:

* Full linked data support, recognizing a range of linked data formats and facilitating the creation of links in and out.  (Links can be created, but it's currently a mostly manual process.)
* Serve and access underlying data through a standard HTTP server using LDP and/or SoLiD protocols (the current implementation uses direct file access).
* Grid view (e.g. for photo+metadata galleries).
* Data bridges to other data sources, in particular to allow Annalist to work with existing spreadhseet and other data.

See the [list of outstanding issues for initial release](https://github.com/gklyne/annalist/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22V0.x+alpha%22) for more details on planned features still to be implemented.

There are many other features noted on the project roadmap that are not yet planned for inclusion as core features.  As far as possible, future development will be guided by actual requirements from applications that use the Annalist platform.


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

See also previous release notes:

- [Release 0.1.x](./release-v0.1.md)


## Release: 0.5.4

This release contains some significant changes to simplify workflows used when creating definitons that use structured ontology terms, based on some experiences using Annalist to create CIDOC CRM data.  It also provides options for generating Turtle data output.  There are numerous bug fixes, which are described in the notes below for release 0.5.3.

Specific visible changes include:

* Turtle data output for entities and entity lists, to make it easier to share Annalist data with other linked data applications.
* New facility to create a subtype with key values inherited or derived from the parent type.
* Revised creation of view and list definitions for a type, to work more easily for subtypes.  Fields from existing type view and list definitions, or from the default view and list definitions, are copied into the new definitions created.
* Changes to help text, diagnostics and other messages.

There is some extensive internal refactoring in the view logic used to generate data outputs, and the links used to access data outputs.


# Version 0.5.3, towards 0.5.4

- [x] BUG: copy entity and Id change (or copy and something) causes errors on save.
- [x] BUG: When accessing JSON-LD from `.../v/<view-id>/...` form of URL (e.g. `.../c/EMLO_in_CRM_samples/v/Linked_image/Linked_image/image_00000026/`), the relative reference to retrieve the JSON-LD does not work.
- [x] BUG: software update zaps default user permissions (e.g. CREATE_COLLECTION)
    - introduced _site_default_user_perms which are consulted in preference to _default_user_perms, but not overridden on update
- [x] BUG: when default view references non-accessible entity: 
    - if default view/list unavailable, revert to default list
- [x] BUG: create subtype without login generates unhelpful error response
- [x] BUG: display list with no fields generates error
- [x] BUG: define view+list with none selected generates invalid list (and unhelpful view?)
- [x] BUG: field pos/size dropdown doesn't display properly on Chinese language Chrome
    - Changed characters used, but haven't yet been able to retest with Chinese language browser
- [x] BUG: data links for collection metadata are broken (since changes to entity_data_ref?)
- [x] Is there a way to allow multiple literal fields with the same property (cf. crm:P3_has_note)?  YES: use field URI "@value" inthe repeat field definition.
- [x] Make it easier to create subtype + view + list...
    - Provide "Create subtype" button and copy view information, supertypes, etc from supertype
    - Enhance create view+list logic to copy previous view+list definitions as defaults
- [x] Separate buttons for create list- and multiple-value fields (seq vs set)
- [x] When creating a repeat field, be more helpful in creating the help and tooltip text
- [x] Default type list/view and subtype comments: include link to type
- [x] Create FAQ for defining subtypes
- [x] For missing field definition, improve text and try to include field name referenced
- [x] Identifier values (URI/CURIE) should have leading/trailing spaces stripped on entry.
- [x] When inheriting definitions, also use parent collection default view if none defined locally.
- [x] Turtle rendering
    - Turtle output generated by parsing JSON-LD and outputing as Turtle using rdflib
    - Implement Turtle output for entity data views
    - Implement Turtle output for entity list views
    - Extensive refactoring of data view logic:
        - common logic to handle different return types (JSON-LD and Turtle)
        - common logic for entity and list data.
        - updated logic for adding "Link" headers to HTTP response
    - Add Turtle redirect calls alongside JSON-LD redirects
        - entityedit.py, form_render
        - entitylist.py, get
    - Create test cases for Turtle output (based on JSON-LD test cases)


# Version 0.5.2

This is mainly a maintenance release to fix some bugs that were introduced (or first noticed) in version 0.5.0.  It also contains some minor presentation, help text and documentation enhncements (including an initial set of FAQs).

The other technical change is some internal code refactoring to move towards possible per-entity access control (currently implemented on an ad hoc basis for default and unknown user permissions).


# Version 0.5.1, towards 0.5.2

- [x] BUG: edit collection metadata fails on save with
    - Original form is not providing correct original collection id
    - Added logic to entitytypeinfo to handle special case of collection ancestor id
    - Modified entityedit GET handler to use entitytypeinfo to access ancestor id
    - Added new test case that detects the original problem
- [x] BUG: failed to migrate linked data tools cleanly 
    - Returns error when trying to view tool:
    - Field See_also_r is missing 'group_field_list' value
    - Caused by earlier migration failure; possible from an attempt to hand-edit data
    - Fixed by removing old collection configuration data; no software change
- [x] BUG: migrating data doesn't update software version in data
    - also: editing collection metadata doesn't update collection s/w version
    - currently save logic of edit form handler calls viewinfo.update_coll_version()
    - [x] Redefine software compatibility version update as Collection method
    - [x] DisplayInfo updated to use new method
    - [x] Collection data migration updated to call new method
    - [-] Special case of editing collection metadata.  This would need a new set of logic (possibly in entitytypeinfo.py) to distinguish between a containing collection and ancestor for any entity (in almost all cases these would be the same), for very little practical benefit. So, for the time being, this is not being fixed.
- [x] BUG: Exception in RenderMultiFields_value.renderAttributeError
    - ("'NoneType' object has no attribute 'get'",)
    - this is caused by a reference to a non-existent field within a repeated field group: the error is in the data, due to old (erroneous) definitions not being removed, but the software reporting of this is unhelpful.
    - it turns out some earlier tests to provide improved reporting had been skipped; these tests have been reactivated and reports are somewhat more helpful.
- [x] BUG: OIDC login sequence returns wrong message if there is email address mismatch (e.g., logged in to wrong Google account)
    - instead of "email address mismatch", reports "was not authenticated".
    - but if different user id is selected, login propceeds OK
    - email address check in OIDC handler removed - this is handled and reported by the calling code
- [x] "Type definition" help text is a little confusing (cf 'Entity types ...').
- [x] Lay groundwork in EntityTypeInfo for access control possibly defined per-entity.
    - Currently used with ad-hoc logic for allowing view of default and unknown users
    - Replaces similar ad-hoc logic previously in DisplayInfo
    - Re-worked other direct references to EntityTypeInfo.permissions_map
- [x] See_also_r field duplicated in field options list
        - [x] Definitions in Resource_defs have been removed.
        - NOTE: See_also_r defined and referenced by:
            - Carolan_Guitar -> this will be a migration case study
            - Performance_defs -> (ditto?)
- [x] Tweak rendering of empty repeat-group


# Version 0.5.0

This release contains candidate feature-complete functionality for an Annalist V1 software release.  The aim has beemn to complete features that are seen as likely to affect the stored data structures used by Annalist, to minimize future data migration requirements.  The intent is that this release will be used in actual projects to test if it offers minimal viable product functionality for its imntended use.  Meanwhile, planned developments will focus more on documentation, stability, security and performance concerns.

### Revised view definition interface

Extensive changes that aim to simplify the user interface for defining entity views (specifically, fields that contain repeating groups of values) by eliminating the use of separate field group entities.  This in turn has led to changes in the underlying view and field definition structures used by Annalist.

Also added are data migration capabilities for existing data collections that use record groups. These have been used to migrate installable collection data.

The `Annalist_schema` instalable collection data (which provides RDF-schema based definitions for the Annalist-specific vocabulary terms) has been updated to reflect the field group changes.

### Other features

- popup help for view fields (tooltip text) is defined seperately from for general help text in a field definition.  (HTML5 tooltips don't support rich text formatting, so thios was limiting what could be included in the field definition help descriptions.)

- the installable collection `Journal_defs` has been split into two, with the aim of improving ease of sharing common definitions:
    - `Resource_defs` provides field and view definitions for uploaded, imported and linked media resources (currently image and audio), and annoted references to arbitrary web resources.  It also provides a number of commionly used namespace definitions (dc, foaf, and a namespace for local names without global URIs).
    - `Journal_defs` (which uses media definitions imported from `Resource_defs`) now provides just the (mainly) narrative journal structure that has been found useful for capturing some kinds of activity description.

- An `annalist-manager` subcommand (`migrateallcollections`) has been aded to migrate data for all collections in a site.

### Bug fixes

- Editing an entity inherited from another collection (which is supposed to create a new copy of that entity in the current collection) was generating an error when saving the edted entity.  The fix to this involved extensive refactoring of the entity editing and save logic to keep better track of the collection from which the original entity data was obtained.

- Fixed site data and installable collection data so that entity selection for inclusion in fields presenting drop-down selection lists would operate more consistently.


