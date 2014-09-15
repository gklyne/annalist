
Annalist directory layout
-------------------------

See layout.py


Annalist URI/directoty structure
----------------------

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
            * fields/
                * field-type
                *  :
        * record-type/
            * record-id
            *  :
        *  :
    *    : (repeat for each collection)
