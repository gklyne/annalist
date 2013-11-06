Annalist directory layout
-------------------------

$ANNALIST_ROOT/
  collection/
    _annalist_config/
      records/
        record-type
         :
      views/
        view-type
         :
      lists/
        list-type
         :
      user-groups/
        group-description
         :
      access/
        default-access
        (more details to work through - keep it simple for starters)
      bridge/
        bridge-description (incl path mapping in collection)
         :
    record-type/
      record-id
       :
     :
   :


Questions:

* Primary type or multiple types?
* How to represent groups within a collection?  Just use multiple associations in a record?
