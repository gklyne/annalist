# Values of annal:field_render_type property

Obtained by:

    grep -rh annal:field_render_type ./annalist | awk '{print $3}' | sort | uniq

Results (reorganized and "attic" values removed)

    "annal:field_render_type/EntityId"
    "annal:field_render_type/EntityTypeId"
    "annal:field_render_type/Text"
    "annal:field_render_type/Textarea"
    "annal:field_render_type/Slug"
    "annal:field_render_type/Identifier"

    "annal:field_render_type/Enum"
    "annal:field_render_type/Field"
    "annal:field_render_type/List"
    "annal:field_render_type/Type"
    "annal:field_render_type/View"
    "annal:field_render_type/Placement"

    "annal:field_render_type/View_sel"
