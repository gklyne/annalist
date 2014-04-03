# Introduction to Annalist

Linked data notebook software


## Background

This project is inspired in part by working with small research groups, and also my own experiences and requirements for data management in running a small business.

**Data - The First Mile**:  while there are many tools for archiving, publishing and processing data, it seems there is a gap in provision for non-developers to create new datasets.  Maybe the most widely used tools are spreadsheets, but these are not so good for sharing and remixing data.

For example, in work on Research Objects, a common question for which there was often not a satisfactory answer was: "How do I create a Research Object?"


## Goals

A software tool for data management that is:

* Easy - can be used out-of-the box without prior configuration

* Flexible - can add struycture to data as needs are recognized.  No force-fitting of datra into a pre-defined schema.

* Sharable - data is created in an easy-to-read plain text format.  The data is sharable with and accessible by those who don't have Annalist software.

* Remixable - data can be mixed with other sources.  This is achieved mainly by using Linbked Data principles and technologies.  Also, provide suppoirt for augmenting existing spreadsheet data and make it available as linked data.


## Status (as of April 2014)

Annalist has been in part-time development since January 2014.  Currently, it exists as an early demonstrator, which shows the intended direction of development, but is still well short of being a usable system.  I estimate it is about 50% along the way to being a minimum releasable product.


## Tour of early demonstrator features

(Links here assume a local copy of the Annalist web server application running on Django's default port 8000.)

### Front page

[http://localhost:8000/annalist/site/](http://localhost:8000/annalist/site/)

* Login via OAuth2/Open ID Connect, currently using Google+ as identity provider

* Web pages build using responsive web page layout framework (Zurb Foundation), will hopefully be mobile-friendly.

* Presents a list of _collections_.  A collection is the administrative unit of data (e.g. for access control), and is also a candidate for presentation as a Research Object.

### View collection

[http://localhost:8000/annalist/c/coll1/d/](http://localhost:8000/annalist/c/coll1/d/)

A default list of records/entities is displayed.  Alternative list views are (will be) possible, but the default list view is configured per collection.  "Find", "View", "Default" are not yet implemented.

### Customize collection

[http://localhost:8000/annalist/c/coll1/!edit](http://localhost:8000/annalist/c/coll1/!edit)

A collection is configured with:

* Record (entity) types - high level classification of collection contents, _not_ structural.

* List views - provide an overview of some or all entities in a collection.  This will in future include grid views as well as simple list views (e.g. for thumbnail image indexes).

* Record (entity) views - provide detail view and editing of entity contents.  

### View/edit record type

[http://localhost:8000/annalist/c/coll1/_annalist_collection/types/type1/!edit](http://localhost:8000/annalist/c/coll1/_annalist_collection/types/type1/!edit)

Note that minimal; information associated with a record type - presentational rather than structural.

### Back to collection view

[http://localhost:8000/annalist/c/coll1/d/](http://localhost:8000/annalist/c/coll1/d/)

### Select entity edit view

[http://localhost:8000/annalist/c/coll1/d/type1/entity1/!edit](http://localhost:8000/annalist/c/coll1/d/type1/entity1/!edit)

This form is entitely data driven.  Cf. `src/annalist_site/annalist/sitedata/views/Default_view/view_meta.jsonld`.

See also (Manualm URI; this navigation is not yet implemented):

[http://localhost:8000/annalist/c/coll1/v/BibEntry_view/type1/entity1/!edit](http://localhost:8000/annalist/c/coll1/v/BibEntry_view/type1/entity1/!edit)

and its view definition `src/annalist_site/annalist/sitedata/views/BibEntry_view/view_meta.jsonld`.

The underlying stored data is JSON-LD (or will be) - cf. `src/annalist_site/devel/annalist_site/c/coll1/d/type1/entity1/entity-data.jsonld`.

Views (not types) define structure in data.  Different views may expose different structure in the same data.  The BibJSON example is incomplete: I still need to add alternative- and repeat subgroup displays to capture the full richness of BibJSON.

The record/entity type can be changed arbitrarily while editing, without losing or invalidating any data that is present.

New fields can be added to a view as-required ("New field" not yet implemented)

## Summary of approach

**Data first, structure and configuration second**

("Just-in-time schema"?)

This is supported by the inherent flexibility of the underlying Linked Data RDF model.

**Frame- or entity-oriented**

Uses linked data and RDF technology and ideas, but with focus on a frame-level rather than graph-level interface.

Imagine one is using a card index for recording data: the goaol is that each record/entity corresponds to the unit of information one might write on a card.

Each entity (or record) has a defined URI, and can be accessed as a first class web resource.

**Flat file storage format**

It's RDF, but there is no triple store (yet).

This is partly a consequence of the framke orientation, and also the goal of easy sharing.

Later developments may inytroduce a triple store (or other index) as an auxiliary to accelerate access to data, but the flat files are always the definitive data.  Any indexes will be regenerated as needed, and are for internal use and service provision, not part of the externally accessible form of data.

Also:
* version control freindly (git, etc.)
* "view source" for data
* hand-editable
* can be presented by vanilla HTTP server

## Futures

* Data bridges, especially spreadsheet
* Research Object creation
* Data on separate HTTP server (e.g. WebDAV instead of file access)
* Multiple identity providers
* More field types (links, images, etc.)
* Grid display (e.g. image thumbnail gallery with selected metadata; cf. FlyTED)
* provenance data capture (e.g. - look at creating additional resource in entity._save)
* git integration for data versioning
  ? dat integration for versioning? (https://github.com/maxogden/dat)
* Memento integration for old data recovery
* ResourceSync integration for data sync
* Shuffl integration?

