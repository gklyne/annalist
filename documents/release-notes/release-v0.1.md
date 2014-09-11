# Annalist v0.1 release notes

Release 0.1 is the first public prototype of Annalist.  It contains what I hope is sufficient tested functionality for the purposes of early evaluation, but there are significant intended capabilities not yet implemented.


## Status

The primary goals of Annalist are:

* Easy data: out-of-box data acquisition, modification and organization of small data records.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

Of these, the first three are substantially implemented (though there are lots of details to be added), and the fourth is at best only partiallly implemented.

Key features implemented:

* simple installation and setup procedure to quickly get a working installation
* highly configurable form display for entering, presenting and modifying data records
* disk-based data storage structures based on JSON-LD
* ability to create new entity record types, views and listing formats onm-the-fly
* OAuth2/OpenID Connect authentication, tested with Google+ but should be usable with other OpenID Connect identity providers.

Intended core features not yet fully implemented:

* Support for a range of field and data types to work with commonly used data: numbers, dates, etc.
* Data bridges, in particular for integation with spreadsheet data and other common tabular formats.
* Support for JSON-LD contexts.
* Full linked data support, recognizing a range of linked data formats and facilitating the creation of links in and out.  (Links can be created, but it's currently a mostly manual process.)
* Support for linking to and annotating binary objects such as images.
* Authorization framework for access control: currently authenticated users have full access, and unauthenticated users have read-only access.
* Use of HTTP back-end data store.
* Image rendering and other media.
* Grid view (e.g. for photo+metadata galleries).

There are many other features noted on the project roadmap that are not yet planned forinclusion as core features.  As far as possible, future development will be guided by actual requirements from applications that use the Annalist platform.


## Feedback

The main purpose of this release is to be a viable platform for getting feedback from potential users of the software.  In particular, I'd like to hear:

* If installation and getting a running service on a computeer meeting the indicated prerequisites takes longer than 10 minutes.  What were the stumbling points.
* Any problems that occur whle trying to use the software.
* Ways in which the software does not meet preferred workflows for collecting data.
* Any must-have features for the software to be useful.
* Any other thoughts, ideas, or difficulties you care to report.

If you have a github account, feedback can be provided through the [github issue tracker](https://github.com/gklyne/annalist/settings).  Otherwise, by message to the [annalist-discuss forum](https://groups.google.com/forum/#!forum/annalist-discuss) at Google Groups.


## Development

Active development takes place on the [`develop` branch](https://github.com/gklyne/annalist/tree/develop) of the GitHub repository.  The `master` branch is intended for stable releases, and is not used for active development.  It would be appreciated if any pull requests submitted can against the `develop` branch.


## History

First public prototype release @@TODO


## Further information

* [Annalist overview](../introduction.md)
* [Installing and setting up Annalist](../installing-annalist.md)
* [Getting started with Annalist](../getting-started.md)
* [Guide to using Annalist](../using-annalist.md)
* [Simple demonstration sequence](../demo-script.md)
* [Frequently asked questions](../faq.md)
* [Developer information](../developer-info.md)
* [Development roadmap](../roadmap.md)

