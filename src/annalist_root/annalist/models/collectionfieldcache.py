from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
This module is used to cache per-collection field information.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2018, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import layout
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.collectionentitycache  import (
    Cache_Error, CollectionEntityCacheObject, CollectionEntityCache
    )
from annalist.models.closurecache           import ClosureCache
from annalist.models.recordfield            import RecordField

#   ---------------------------------------------------------------------------
# 
#   Field-cache object class
# 
#   ---------------------------------------------------------------------------

class CollectionFieldCacheObject(CollectionEntityCacheObject):
    """
    This class is a field definition cache for a specified collection.

    It extends class CollectionEntityCacheObject with field-specific logic; notably
    overriding method _load_entity with additional logic to maintain a superproperty
    closure cache, and methods to access that cache.
    """
    def __init__(self, coll_id, entity_cls=RecordField):
        """
        Initialize a cache object for a specified collection.

        coll_id         Collection id with which the field cache is associated.
        """
        super(CollectionFieldCacheObject, self).__init__(coll_id, entity_cls)
        self._superproperty_closure = ClosureCache(coll_id, ANNAL.CURIE.superproperty_uri)
        return

    def _load_entity(self, coll, field_entity):
        """
        Internal helper method loads field data to cache.
        Also updates superproperty closure cache.

        Returns True if new field was added.
        """
        field_id     = field_entity.get_id()
        property_uri = field_entity.get_property_uri()
        field_parent = field_entity.get_parent().get_id()
        field_data   = field_entity.get_save_values()
        add_field    = super(CollectionFieldCacheObject, self)._load_entity(
                            coll, field_entity, entity_uri=property_uri
                            )
        if add_field:
            # Add relations for superproperty references from the new property URI
            for superproperty_obj in field_data.get(ANNAL.CURIE.superproperty_uri, []):
                superproperty_uri = superproperty_obj["@id"]
                self._superproperty_closure.add_rel(property_uri, superproperty_uri)
            # Also add relations for references *to* the new property URI
            for try_subproperty_obj in self.get_all_entities(coll):
                sub_superp_objs = try_subproperty_obj.get(ANNAL.CURIE.superproperty_uri, [])
                sub_superp_uris = (
                    [ sub_superp_obj["@id"] for sub_superp_obj in sub_superp_objs ]
                    )
                if property_uri in sub_superp_uris:
                    subproperty_uri = try_subproperty_obj.get(ANNAL.CURIE.property_uri, None)
                    if subproperty_uri:
                        self._superproperty_closure.add_rel(subproperty_uri, property_uri)
        return add_field

    def _drop_entity(self, coll, field_id):
        """
        Override method that drops an entity from the cache, to also remove references
        from the superproperty closure cache.

        Returns the field entity removed, or None if not found.
        """
        field_entity = super(CollectionFieldCacheObject, self)._drop_entity(coll, field_id)
        if field_entity:
            property_uri = field_entity.get_property_uri()
            self._superproperty_closure.remove_val(property_uri)
        return field_entity

    def get_superproperty_uris(self, property_uri):
        """
        Returns all superproperty URIs for a specified property URI.

        Returns all superproperty URIs, even those for which there 
        is no defined field entity.
        """
        return self._superproperty_closure.fwd_closure(property_uri)

    def get_subproperty_uris(self, property_uri):
        """
        Returns all subproperty URIs for a specified property URI.

        Returns all subproperty URIs, even those for which there 
        is no defined field entity.
        """
        return self._superproperty_closure.rev_closure(property_uri)

    def get_superproperty_fields(self, coll, property_uri):
        """
        Returns all superproperties for a specified property URI.

        This method returns only those superproperties that are defined as entities.
        """
        self._load_entities(coll)
        for st_uri in self.get_superproperty_uris(property_uri):
            st = self.get_entity_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def get_subproperty_fields(self, coll, property_uri):
        """
        Returns all subproperties for a specified property URI.

        This method returns only those subproperties that are defined as entities.
        """
        self._load_entities(coll)
        for st_uri in self.get_subproperty_uris(property_uri):
            st = self.get_entity_from_uri(coll, st_uri)
            if st:
                yield st
        return

    def remove_cache(self):
        """
        Close down and release all collection field cache data
        """
        # log.debug("@@@@remove field cache %r"%(self.get_coll_id(),))
        super(CollectionFieldCacheObject, self).remove_cache()
        self._superproperty_closure.remove_cache()
        self._superproperty_closure = None
        return

#   ---------------------------------------------------------------------------
# 
#   Collection field-cache class
# 
#   ---------------------------------------------------------------------------

class CollectionFieldCache(CollectionEntityCache):
    """
    This class manages field cache objects over multiple collections
    """
    def __init__(self):
        """
        Initialize.

        Initializes a value cache cache with no per-collection data.
        """
        super(CollectionFieldCache, self).__init__(CollectionFieldCacheObject, RecordField)
        return

    # Collection field cache allocation and access methods

    def set_field(self, coll, field_entity):
        """
        Save a new or updated field definition
        """
        return self.set_entity(coll, field_entity)

    def remove_field(self, coll, field_id):
        """
        Remove field from collection field cache.

        Returns the field entity removed if found, or None if not defined.
        """
        return self.remove_entity(coll, field_id)

    def get_field(self, coll, field_id):
        """
        Retrieve a field description for a given field Id.

        Returns a field object for the specified collection and field Id.
        """
        return self.get_entity(coll, field_id)

    def get_field_from_uri(self, coll, field_uri):
        """
        Retrieve a field description for a given property URI.

        Returns a field object for the specified collection and property URI.
        """
        return self.get_entity_from_uri(coll, field_uri)

    def get_all_field_ids(self, coll, altscope=None):
        """
        Returns all fields currently available for a collection in the indicated scope.
        Default scope is fields defined directly in the indicated collection.
        """
        return self.get_all_entity_ids(coll, altscope=altscope)

    def get_all_fields(self, coll, altscope=None):
        """
        Returns all fields currently available for a collection in the indicated scope.
        Default scope is fields defined directly in the indicated collection.
        """
        return self.get_all_entities(coll, altscope=altscope)

    def get_superproperty_fields(self, coll, field_uri):
        """
        Returns all superproperties for a specieid property URI.
        """
        field_cache = self._get_cache(coll)
        return field_cache.get_superproperty_fields(coll, field_uri)

    def get_subproperty_fields(self, coll, field_uri):
        """
        Returns all subproperties for a specieid property URI.
        """
        field_cache = self._get_cache(coll)
        return field_cache.get_subproperty_fields(coll, field_uri)

    def get_superproperty_uris(self, coll, field_uri):
        """
        Returns all superproperties for a specieid property URI.
        """
        field_cache = self._get_cache(coll)
        return field_cache.get_superproperty_uris(field_uri)

    def get_subproperty_uris(self, coll, field_uri):
        """
        Returns all subproperties for a specieid property URI.
        """
        field_cache = self._get_cache(coll)
        return field_cache.get_subproperty_uris(field_uri)

# End.
