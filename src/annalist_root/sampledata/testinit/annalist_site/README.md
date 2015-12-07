src/annalist_root/annalist/sampledata/data/site/

This directory contains sample Annalist site data used for testing

Directory layout:

  $BASE_DATA_DIR
    annalist-site/
      _annalist-site/
        site_meta.json_ld
      <collection-id>/
        _annalist_collection/
          coll_meta.jsonld
          types/
            <type-id>/
              type_meta.jsonld
             :
          views/
            <view-id>/
              view_meta.jsonld
             :
          lists/
            <list-id>/
              list_meta.jsonld
             :
          bridges/
            (bridge-description (incl path mapping in collection) - @@TBD)
             :
          user-groups/  @@TBD
            group-description
             :
          access/  @@TBD
            default-access
            (more details to work through - keep it simple for starters)
        <type-id>/
          <entity-id>/
            entity-data.jsonld
            entity-prov.jsonld
           :
         :
       :
