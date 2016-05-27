/Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/

This directory contains Annalist site data for http://test.example.com/testsite/.

Directory layout:

    /Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/
      c/
        _annalist_site/
          _annalist_collection/         (site-wide definitions)
            coll_meta.jsonld            (site metadata)
            coll_context.jsonld         (JSON-LD context for site definitions)
            _enum/
              (enumerated type values)
               :
            _field/
              (view-field definitions)
               :
            _group/
              (field group definitions)
               :
            _list/
              (entity list definitions)
               :
            _type/
              (type definitions)
               :
            _user/
              (user permissions)
               :
            _view/
              (entity view definitions)
               :
            _vocab/
              (vocabulary namespace definitions)
               :
        (collection-id)/                (user-created data collection)
          _annalist_collection/         (collection definitions)
            coll_meta.jsonld            (collection metadata)
            coll_context.jsonld         (JSON-LD context for collection definitions)
            _type/                      (collection type definitions)
              (type-id)/
                type_meta.jsonld
               :
            _list/                      (collection list definitions)
              (list-id)/
                list_meta.jsonld
               :
            _view/                      (collection view definitions)
              (view-id)/
                view_meta.jsonld
               :
            _field/                     (collection field definitions)
              (field-id)/
                field_meta.jsonld
               :
            _group/                     (collection field group definitions)
              (group-id)/
                group_meta.jsonld
               :
            _user/                      (collection user permissions)
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
for Annalist 0.1.32 at 2016-05-26 10:55:40


