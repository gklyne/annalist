# Note of assumptions made in code (partial)


## util.py

read_entity, write_entity: volume of data associated with a single entity can be kept in memory.
The idea that individual entities contain modest amount of data is fairly pervasive in
the overall design of anallist; e.g. that entity data can be searched in memory, so
don't need to worry about complex indexing structures within an entity.  Also, the entity
is the funamental referenceable unit of information presented by Annalist.


## site.py

Site.collections_dict: number of collections in a site is small 
enough that metadata for all collections can be handled in memory.
Collection metadata is small dictionary, <10 items.
Expected number of collections in a site is less than 100.





