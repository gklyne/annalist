# Values of annal:field_value_type property

Obtained by:

    grep -rh annal:field_value_type ./annalist | awk '{print $3}' | sort | uniq

Results (reorganized and "attic" values removed)

    annal:Slug
    annal:Placement
    annal:Identifier
    annal:Enum
    
    annal:Type
    annal:View
    annal:List
    annal:Field
    annal:Field_type
    annal:List_type
    (annal:Value_type)

