# Values of annal:value_type property

Obtained by:

    grep -rh annal:value_type * | awk '{print $3}' | sort | uniq

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
    annal:Value_type
    annal:List_type


    "annal:Text"
    "annal:Longtext"
    "annal:Slug"
    "annal:Identifier"

    "annal:Type"
    "annal:View"
    "annal:List"

    "annal:Field_type"
    "annal:List_type"
    "annal:Placement"
