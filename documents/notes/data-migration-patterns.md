# Data migration patterns to consider

## Change property URI

Add alias to type definition

## Change type URI

Edit type definition

## Add new  type URI

Add supertype to type definition

## Type refinement (introduce subtypes)

1. Define subtype with new type URI and existing type URI(s) as supertype URI(s)
2. CHECK: update list type to use supertype test so that subtypes are included
3. Define view and list for new type if needed to add new fields
4. Edit entities that are subtype instances: 
    - may need to usedefault entity form to change type
    - then use new view to add additional fields as required

## List simplification; e.g.

        "entity:seeAlso_r": [
            {
              "rdfs:seeAlso": "https://jena.apache.org/documentation/serving_data/"
            }
          ]
    =>
        "rdfs:seeAlso": [
            {
               "@id": https://jena.apache.org/documentation/serving_data/"
            }
          ]

## Remove unused fields

@@TBD - currently, hand-edit JSON-LD



