## How can I re-use definitions in different collections?

NOTE: example links on this page refer to the Analust demo site at [annalist.net](http://annalist.net/).

Annalist has a capability for a data collection to "inherit" data from another collection on the same server.  This is mainly useful for re-using type, view and list definitions, but can apply to any data.

When I use this facility, I try to keep the definitions separate from the data:  I create a collection that contains type and view definitions, themn another collection that inherits those definitions and contains instances of the defined types.  For example, the `Annalist_schema` collection that is part of an Annalist software installation uses definitions from `RDF_schema_defs`.

Annalist includes a number of installable collections that contain some generally useful definitions:

* [Concept_defs](http://demo.annalist.net/annalist/c/Concept_defs/) contains definitions for SKOS concepts and relationships.
* [Journal_defs](http://demo.annalist.net/annalist/c/Journal_defs/) contains definitions that can be used for building up journal- or log type data that include narrative descriptons and structured data elements.
* [Namespace_defs](http://demo.annalist.net/annalist/c/Namespace_defs/) contains definions of some common namespaces that may be used in property or class URIs in Annalist data, and are used when generating RDF (e.g. JSON-LD) output to ensure that compact URI forms can be resolved to standard URIs.
* [Resource_defs](http://demo.annalist.net/annalist/c/Resource_defs/) contains maimnly field and view definotioons that can be used when incorporating uploaded, imported or linked media in a data collection.  ("uploaded" refers to files uploaded from a user's computer; "imported" refers to resources copied from other web sites, and "linked" refers to references to resources on the web for which no local copy is created.)

These collections must be installed using the `annalist-manager` command line utility before they can be referenced by other collections; e.g.

    annalist-manager installcollection Resource_defs

Installed collections will show up on the Annalist site home page.

A new collection can be created using definitions from any available collection as follows:

1. Log in to Annalist using an account with ADMIN or CREATE_COLLECTION permissions.

2. Create a new data collection.

3. On the home screen, select the checkbox by your new collection and click "Edit metadata"

4. In the Collection metadata form, select the "parent" collection from which the new collection should inherit definitions.

Inherited definitions may be edited in child collections, in which case a copy of any edited definitions is created in the child collection.  This allows existing definitions to be used as a starting point for new collections, modified as required, without affecting the parent collection or any other child collections.

Inherited definitions may be cascaded. E.g. `Journal_defs` inherits definitons from `Resource_defs`, so any collection that inherits from `Journal_defs` also has access to definitions from `Resource_defs`.  When inheritance is cascaded in this way, all collections from which definitions are inherited must be installed.

Core Analist definitions (`_type`, `_view`, etc.) are implicitly inherited by all other collections, and may be viewed (but not edited) as a special collecion [_annalist_site](http://demo.annalist.net/annalist/c/_annalist_site/)

The current implementation (as of 2017-05) does not support multiple inheritance of collections; i.e. a collection may inherit definitions from at most one other collections.


