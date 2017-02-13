/Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/

This directory contains Annalist site data for http://test.example.com/testsite/.

Directory layout:

    /Users/graham/workspace/github/gklyne/annalist/src/annalist_root/sampledata/data/annalist_site/
      c/
        _annalist_site/                 (site-wide definitions)
          d/
            coll_meta.jsonld            (site metadata)
            coll_context.jsonld         (JSON-LD context for site definitions)
            _enum_field_placement/
              (field-placement-value)/
                enum_meta.jsonld
               :
            _enum_list_type/
              (list-type-id)/
                enum_meta.jsonld
               :
            _enum_render_type/
              (render-type-id)/
                enum_meta.jsonld
               :
            _enum_value_type/
              (value-type-id)/
                enum_meta.jsonld
               :
            _enum_value_mode/
              (value-mode-id)/
                enum_meta.jsonld
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
          d/
            coll_meta.jsonld            (collection metadata)
            coll_context.jsonld         (JSON-LD context for collection data)
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
            (type-id)/                  (contains all entity data for identified type)
              (entity-id)/              (contains data for identified type/entity)
                entity_data.jsonld      (entity data)
                entity_prov.jsonld      (entity provenance @@TODO)
                (attachment files)      (uploaded/imported attachments)

               :                        (repeat for entities of this type)

             :                          (repeat for types in collection)

         :                              (repeat for collections in site)

Created by annalist.models.site.py
for Annalist 0.1.36 at 2017-02-08 16:18:45


