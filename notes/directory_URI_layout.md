Annalist directory layout
-------------------------

See also:

- [URI_structure.md](./notes/URI_structure.md)

$ANNALIST_ROOT/
  collection/
    _annalist_collection.jsonld
    _annalist_collection/
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
    record-type-id/
      record-id
       :
     :
   :


Questions:

* Primary type or multiple types?
* How to represent groups within a collection?  Just use multiple associations in a record?


Annalist URI structure
----------------------

See also:

- [directory_layout.md](./notes/directory_layout.md)

*   $ANNALIST_ROOT/
 
    Presents list of collections and option to create new.  Formats: HTML (form) or JSON-LD.  POST form-data (or JSON-LD?) to create new collection.

    *   $COLLECTION_ID/

        Presents default view for collection, based on defaults)  Formats HTML (form) or JSON-LD.  POST form-data (or JSON-LD?) to change defaults.

        *   _annalist_config/
            * (collection config)
            * records/
                * record-type
                *  :
            * views/
                * view-type
                *  :
            * lists/
                * list-type
                *  :
        * record-type/
            * record-id
            *  :
        *  :
    *    : (repeat for each collection)
