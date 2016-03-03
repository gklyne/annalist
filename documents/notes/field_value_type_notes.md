# Notes for field value types.

The field value type (`annal:field_value_type`) that is part of a field definition is not really used at present (except possibly by enumerated value restriction expressions), and consequently the values assigned have been a bit erratic.  These notes are intended to provide a basis for some consistency of use, and in due course may be used to assist with field validation and RDF typed literal generation.

The value type for a field is determined by a combination of the render type and the value mode.

When the field contains a literal, the field value type provides more information about the value of the literal (which may also be related its internal storage format - e.g. `CheckBox` treated internally as `Boolean`).  When the field contains a URI reference, the field value type refelects the intended type of the referenced resource.

Render type      | Value mode   | Field value type (default)
-----------------|--------------|---------------------------
                 |              |
*                | Value_direct | (see below)
*                | Value_entity | annal:EntityRef
*                | Value_field  | annal:EntityRef
*                | Value_import | (see below)
*                | Value_upload | (see below)
                 |              |
CheckBox         | *            | annal:Boolean
Codearea         | *            | annal:Longtext
EntityId         | *            | annal:Slug
EntityTypeId     | *            | annal:Slug
Enum             | *            | (type of referenced entity - same as `annal:field_ref_type`)
Enum_choice      | *            | (type of referenced entity - same as `annal:field_ref_type`)
Enum_choice_opt  | *            | (type of referenced entity - same as `annal:field_ref_type`)
Enum_optional    | *            | (type of referenced entity - same as `annal:field_ref_type`)
FileUpload       | *            | rdfs:Resource
Identifier       | *            | annal:Identifier
Markdown         | *            | annal:Richtext
Placement        | *            | annal:Placement
RefAudio         | *            | annal:Audio
RefImage         | *            | annal:Image
RefMultifield    | *            | annal:EntityRef
RepeatGroup      | *            | rdf:List
RepeatGroupRow   | *            | rdf:List
ShowMarkdown     | *            | annal:Richtext
Showtext         | *            | annal:Text
Slug             | *            | annal:Slug (annal:EntityRef)
Text             | *            | annal:Text
Textarea         | *            | annal:Longtext
TokenSet         | *            | rdfs:Resource
URIImport        | *            | rdfs:Resource
URILink          | *            | rdfs:Resource

Fields that contain a reference to some other entity are typed as `annal:EntityRef`, which means the immediate field value is expected to contain an `entity_id` or `type_id/entity_id`.

