/usr/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/

This directory contains Annalist site data for http://test.example.com/testsite/.

Directory layout:

    /usr/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/
      c/
        _annalist_site/
          _annalist_collection/         (site-wide definitions)
            coll_meta.jsonld            (site metadata)
            coll_context.jsonld         (JSON-LD context for site definitions)
            enums/
              (enumerated type values)
               :
            fields/
              (view-field definitions)
               :
            groups/
              (field group definitions)
               :
            lists/
              (entity list definitions)
               :
            types/
              (type definitions)
               :
            users/
              (user permissions)
               :
            views/
              (entity view definitions)
               :
            vocabs/
              (vocabulary namespace definitions)
               :
        (collection-id)/                (user-created data collection)
          _annalist_collection/         (collection definitions)
            coll_meta.jsonld            (collection metadata)
            coll_context.jsonld         (JSON-LD context for collection definitions)
            types/                      (collection type definitions
              (type-id)/
                type_meta.jsonld
               :
            lists/                      (collection list definitions
              (list-id)/
                list_meta.jsonld
               :
            views/                      (collection view definitions
              (view-id)/
                view_meta.jsonld
               :
            fields/                     (collection field definitions
              (field-id)/
                field_meta.jsonld
               :
            groups/                     (collection field group definitions
              (group-id)/
                group_meta.jsonld
               :
            users/                      (collection user permissions
              (user-id)/
                user_meta.jsonld
               :
          d/
            (type-id)/                  (contains all entity data for identified type)
              (entity-id)/              (contains data for identified type/entity)
                entity_data.jsonld      (entity data)
                entity_prov.jsonld      (entity provenance @@TODO)
                (attachment files)      (uploaded/imported attachments)

               :                        (repeat for entities of this type)

             :                          (repeat for types in collection)

         :                              (repeat for collections in site)

Created by annalist.models.site.py
for Annalist 0.1.24 at 2015-12-07 11:28:47


