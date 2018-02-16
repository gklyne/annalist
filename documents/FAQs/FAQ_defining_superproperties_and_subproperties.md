## How can I define a subproperty of an existing property URI?

Annalist associates property URIs with field defintions, along with details of the entity type (domain), value type (range) and how the property value is rendered for presentation.  But there is no directly manages subfield/superfield relation.

However, there is a field in the Annalist field definition form (`Superproperty URIs`) for specifying superproperty URIs; zero, one or more values may be specified.  The superproperty/subproperty relationships are not recorded directly in the generated entity data, but are used to locate (inferrable) instances of a property recorded using a subproperty of the specified field property URI when viewing and/or editing entity data.

The intent is that specialized views of some entity type may be created for particular usage (e.g., associated with a subtype), but still be visible in views using fields associuated with the more generic superproperty URIs.  This is intended to allow some forms of progressive refinement of data models without requiring changes to existing data.

For example, when using CIDOC CRM, an object creation activity (`E65_Creation`) may be a specialization of a general event (`E5_Event`), where the creator property (`P135_was_created_by`), which relates the created object to the creation activity, would be a specialization of the more general presence property (`P12_was_present_at`).  With `P12_was_present_at` recorded as a superproperty URI of `P135_was_created_by`, fields defined with the P12 property URI would also show values defined in data using the P135 property.

### To define a new field using a subproperty of an existing property URI

1. Navigate to a view of the field definition for which a subproperty URI is to be defined. (e.g. view a list of "Field definitions", if necessary with "Scope all" selected, then click on the entry to display the original field).

2. Click on the "Define subproperty  field" button.  A new form is displayed with initial details of a new field, and with the original property URI recorded as a superproperty URI.

3. The "Field Id", "Field label", "Help" and "Property URI" fields will need to be updated with details for the new field.  Other fields are copied from the original field definition, and may be left as-is or updated as appropriate to the relationship expressed by the new field.

4. When done with adding details for the new field, click on "Save".

5. The new field may now be used in view definitions that are appropriate to the more specialized field.  Existing view definitions that use the superproeprty URI will also show values defined using the property URI in the new field.  (Unless the new data uses both new and old property URIs, in which case the existing views will show uses of the more general property in preference to the more specialized version.)

