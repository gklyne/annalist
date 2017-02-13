# Values of annal:field_value_type property

Obtained by:

    grep -rh annal:field_value_type ./annalist | awk '{print $3}' | sort | uniq

Results (reorganized and "attic" values removed)

    annal:EntityRef
    annal:Placement
    annal:Identifier
    annal:Enum
    
    annal:Type
    annal:View
    annal:List
    annal:Field
    annal:List_type

@@TODO: flesh this out when required.