## I've got an account, how do I create a new collection?

Create a new collection as described at https://github.com/gklyne/annalist/blob/develop/documents/tutorial/annalist-tutorial.adoc#creating-a-new-collection  (Note that the collection Id must consist of letters, digits and '\_' characters, without spaces or other punctuation.)

### Use existing definitions in new collection

An Annalist collection may be linked to a "parent" collection, from which it inherits any existing type, view and other definitions.  To use existing definititions in a new colection:

1. Create a neew collecton as noted above.

2. Edit metadata for your new collection as described at https://github.com/gklyne/annalist/blob/develop/documents/tutorial/annalist-tutorial.adoc#change-collection-metadata

3. On the form displayed, select the collection containing existiong definitions in the "Parent" field, and click "Save".

4. When listing collection contents, select the "Scop[e all" checkbox option, and then the "List" button, to see definitions imported from the parent collection(s).


### Collections that ship with Annalist

Annalist ships with a number collections definitions for some commonly-used or example data collections.  If you have command line access to the host system where the Annalist server is running, these collections can be installed into the Annalist site data using the `annalist_manager` utility using the command:

    annalist_manager installcollection <collection_id>

(See Annalist installation instructions for more information about the `annaliust_manager` command line utility.)

Available collection defimnitions include:

* `Resource_defs`: contains some common definitions for uploaded, imported and linked media files audio, image, etc.)

* `RDF_schema_defs`:  contains definitions for defining RDF schema data.  These definitions are used by the `Annalist_schema` collection.

* `Concept_defs`: contains definitions for defining and/or including SKOS concepts and relations in a collection's data.

* `Journal_defs`: contains definitions for a journal-style collection, which contains a series of journal entries recording some activity or series of activities.  We have found that this sometimes forms a useful starting point for recording new data whose useful structure is not initially known.  The journal entries can later be referenced for backgrund context for more structured data entries.

* `Namespace_defs`: contains some definitions for common vocabulary namespaces that are not core to Annalist.  (Annalist core namespaces include `rdf`, `rdfs`, `owl`, `xsd` and `annal`.)

* `Annalist_schema`: contains definitions for terms in the `annal` namespace, which are used in the RDF information structures used to drive Annalist's internalop[eration (such as type, view and list definitions).


### Example: how do I start my own 'journal'?

Annalist ships with a collection called `Journal_defs`, which contains definitions for a Journal-style collection, and which in turn inherits from `Resource_defs` and more.  Assuming these collections have been installed (see above), the definitions may be used as the starting point for a new journal-style collection:

1. Create a new collecton as noted above.

2. Edit metadata for your new collection as described at https://github.com/gklyne/annalist/blob/develop/documents/tutorial/annalist-tutorial.adoc#change-collection-metadata

3. On the form displayed, select "Journal and Resource definitions" in the "Parent" field, and click "Save".  (This imports journal entry definitions from collection "Journal_defs".)

4. Back on the front page, click on the link for the new collection you just created.  

5. In the "List" field, select "Journal entries" from the dropdown list, then click the "List" button.  An empty list of journal entries is displayed.  Click on "New" to create a new entry.

By default, new entries are created with a numeric Id (e.g. 00000001), which can be overridden with something more meaningful, or left as-is.  Ids used must consist of letters, digits and/or '_' characters, without spaces or other punctuation.

