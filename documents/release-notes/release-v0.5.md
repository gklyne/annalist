# Annalist v0.5 release notes

Annalist release 0.5.x is a candidate feature-complete minimal viable product for an eventual version 1 release.

A summary of issues intended to be resolved for product release can be seen in the [issues list for the first alpha release milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).  See also the file [documents/TODO.md](https://github.com/gklyne/annalist/blob/develop/documents/TODO.md) on the "develop" branch.


## Current release: 0.5.0

This release contains the first candidate feature-complete functionality for an Annalist V1 software release.  The aim has been to complete features that are likely to affect the stored data structures used by Annalist, to minimize future data migration requirements.  The intent is to use this release in several projects to test if it offers minimal viable product functionality for its intended use.  Meanwhile, planned developments up to a version 1.0 release will focus on documentation, stability, security and performance concerns.

The main change in this release from earlier (v0.1) releases is simplification the user interface for defining entity views (specifically, fields that contain repeating groups of values) by eliminating the use of separate field group entities.  This in turn has led to changes in the underlying view and field definition structures used by Annalist.

Other changes include:

- popup help for view fields (tooltip text) is defined seperately from for general help text in a field definition.
- the installable collection `Journal_defs` has been split into `Resource_defs` and `Journal_defs`.
- An `annalist-manager` subcommand has been aded to migrate data for all collections in a site.
- A small number of bug fixes

See the "History" selection below, and the notes for verion 0.1.37 in the [Release 0.1.x](./release-v0.1) notes for more details .

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

- [Release 0.1.x](./release-v0.1)

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


