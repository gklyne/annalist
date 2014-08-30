# Values of annal:field_render property

Obtained by:

    grep -rh annal:field_render ./annalist | awk '{print $3}' | sort | uniq

Results (reorganized and "attic" values removed)

    "annal:field_render/EntityId"
    "annal:field_render/EntityTypeId"
    "annal:field_render/Text"
    "annal:field_render/Textarea"
    "annal:field_render/Slug"
    "annal:field_render/Identifier"

    "annal:field_render/Enum"
    "annal:field_render/Field"
    "annal:field_render/List"
    "annal:field_render/Type"
    "annal:field_render/View"
    "annal:field_render/Placement"

    "annal:field_render/View_sel"
