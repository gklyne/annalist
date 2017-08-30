## How can I define a subtype of an existing type?

Annalist does not maintain subtype/supertype relationships directly between its internal types, but it does provide facilities for recording such relationships between type URIs.

There is a field in the Annalist type definition form for specifying supertype URIs for a type; zero, one or more supertype URIs may be specified.  When generating JSON-LD, all of these type identifiers are applied when creating or updating an instance of the type.  When enumerating values of a type for list displays and drop-down lists in reference fields, instances of types that include the target type as a supertype (i.e. subtypes of the target type) are included.  When adding a supertype to an existing type, it may be necessary to perform a data migration on the collection (see "Customize > Migrate data") for existing instances to be recognized as subtypes.

In practice, there is often more to declaring a supertype/subtype relationship between types:  subtypes often have different associated views with additional fields.  Annalist can help with creating these.

### To define a new type that is a subtype of an existing type:

1. Navigate to a view of the supertype definition for which a subtype is to be defined. (e.g. view a list of "Entity types", if necessary with "Scope all" selected, then click on the entry for the desired supertype).

2. Click on the "Define subtype" button.  A new form is displayed with initial details of the new subtype.  The "Type Id", "Label", "Comment" and "Type URI" fields will probably need to be updated with details for the new type.  The "Supertype URIs" field is filled in with the URI of the supertype, and its supertypes if any.  The "Default view" and "Default list" fields are copied from the supertype.

3. To define a new view and list for the new subtype, click on the "Define view+list" button.  The new view and list definitions are created with the same Ids as the subtype itself and with fields copied from the supertype definitions. The subtype edit form is redisplayed with the new view and list selected.

4. The new view and/or list may now be edited by clicking on the edit button ("✍", or writing hand) by the corresponding field.  Typically, the view may be edited to include fields for properties of the new, more specialized type.


