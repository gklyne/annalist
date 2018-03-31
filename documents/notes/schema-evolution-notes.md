# Notes for handling schema evolution

The notion of evolution originally evisaged by Annalist was addition and 
refinement of structure through the addition of new types and properties.

A related but different issue is schema evolution that resulkts in changes to
type- and property- URIs already in use.  A problem with this latter type is 
that it is often not possible to determine the intent of a change, so fully
automated data migration is not a practical option.

These notes are thoughts about Annalist features that might be introduced
to support evolution of properties used in existing Annalist data.


# Plan for schema evolution support

Assume that evolution is initially handled by creating a new collection 
that is a copy or inherits from the original.  Also assume that internal 
identifiers used by Annalist remain constant in their overall intent, and 
are not subject to arbitrary renaming.

The general plan is to start by providing reports of changes between 
collections, and possible knock-on effects in their definitions.  
From here, identify mechanisms that can be used to apply data 
migrations that adapt old data for use with updated schemas.

1. Provide report of references to type URIs that have been changed.

2. Provide reporting for references to property URIs that have been changed.

3. Provide reporting of references to types for which subtypes have been defined.

4. Provide reporting of references to property URIs for which superproperties have been defined.

5. Introduce type- and property-URI migration options that cause data to be 
updated when read and written.  All migrations are defined and applied per type,
so that they can be easily performed on-access.

    - property migrations are (currently) handled through alias fields.
    - some type migrations can be handled as supertypes, others may need updates.

7. Provide collection migration option in annalist-mananager that reads and 
writes every entity data record, thereby applying all migrations.

8. Think about more complex migrations (as they arise?)


# Patterns of schema evolution

## Subdivide type into more detailed options

Create a new Annalist type for each subtype.

Declare the orignal type URI as supertype of each refined type.
These are picked up by entity selectors that refer to the original type URI.

The main type URI and all supertype URIs are included when 
entities are created or updated, according to their Annalist type.


## Renaming a type

(a) need to find all references and update them

(b) On some systems (e.g, MacOS), renames that only change the case of characters in the type name fail because the file system naming is case-insensitive.  These renames need to be done in two stages.


## Rename type, view and list

@@TODO


## Change type URI

Update URI in Annalist type declaration.

Update references to original URI in View, List, Field and Group definitions.

Old URI coud be declared as supertype.

The main type URI and all supertype URIs are included when 
entities are created or updated, according to their Annalist type.


## Change property URI

Primary URI definition comes from a Field definition, but this can be
overridden by Views and Lists, which should be updated as appropriate.

Property URIs may be referenced by selectors (value restrictions) in 
Field and List definitions.

Property aliases, defined on a recordtype, can be used to let the old URI be 
recognized in place of the new one.  When editing a form that uses the new 
property URIs, the new URIs are added when the form is saved, and the old ones 
remain as they were.


## Remove property URI no longer used

Can occur when using property aliases to make value accessible at new property URI


## Extend graph path

("Shape changing" pattern? - see below)

Add indirection through an additional resource.  E.g,. replacing the domain and range URIs for `Property` entities in `RDF_schema_defs` with references to `Class` entities.  (Similar has been done for `subclassOf` and `subprpertyOf` using a change of URI.)


## Local entity references and permanent entity URIs

These should be interchageable, with the permanent URI stored for referencing local entities where available.  This will mean that enumerated value displays must be able to reference entities using permanent URIs (annal:uri) as well as local references.


## Change property URI used for both list/collection values and list/collection members

("Shape changing" pattern? - see below)

Example:

    "annal:member": [
        {
          "annal:member": "Journal/00000001"
        }
      ]

to be converted to:

    "coll:list_property": [
        {
          "coll:member_property": "Journal/00000001"
        }
      ]

or:

    "coll:list_property": [
        {
          "@id": "Journal/00000001"
        }
      ]


## "Shape changing" patterns

Some of the preceding examples (where noted) may be particular cases of a more general "shape-changing" pattern, in which a query might be used to locate and match properties that need to be re-written.  (But how easily are differing-length lists handled by querying?)

Pattern matching could be limited to subtrees from an entity node, which could simplify the descriptions required.

See also:
- https://ci.mines-stetienne.fr/sparql-generate/
- https://lists.w3.org/Archives/Public/semantic-web/2018Mar/0136.html


## Change namespace prefix

This change applied to Performance_defs and Parformances required a lot of effort: class URIs and propery URIs had to be changed in inherited definitions, local definitions and local data.  Changing the namespace URI without changing the prefix is relatively easier: just edit the corresponding namespace definition.

The prefix migration may most easily be invoked by directives added to the namespace definition - that way, the migration could be applied for any collection that references and uses the namespace.


