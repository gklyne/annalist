"""
This module is used to cache per-collection vocabulary namespace information.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                       import layout
from annalist.exceptions            import Annalist_Error
from annalist.identifiers           import ANNAL, RDFS

from annalist.models.recordvocab    import RecordVocab

#   ---------------------------------------------------------------------------
# 
#   Local helper functions
# 
#   ---------------------------------------------------------------------------


#   ---------------------------------------------------------------------------
# 
#   Error class
# 
#   ---------------------------------------------------------------------------

class Vocab_Cache_Error(Annalist_Error):
    """
    Class for errors raised by closure calculations.
    """
    def __init__(self, value=None, msg="Vocab_Cache_error"):
        super(Vocab_Cache_Error, self).__init__(value, msg)
        return

#   ---------------------------------------------------------------------------
# 
#   Type-cache object class
# 
#   ---------------------------------------------------------------------------

class CollectionVocabCacheObject(object):
    """
    This class is a vocabulary namespace URI cache for a specified collection.

    NOTE: Type entities are instantiated with respect to a specified collection,
    but the collection objects are transient (regenerated for each request), so
    the cache stores the vocabulary namespace values but not the instantiated entity.

    Two kinds of information are cached:

    1.  vocab cache: details of all vocabulary namespaces that are visible to
        this class, indexed by vocab id and vocab URI
    2.  scope cache: lists of vocab Ids that are visible in different scopes: used 
        when returning vocabulary namespace enumerations.

    Scope values currently include "user", "all", "site"; None => "coll".
    Apart from treating None as collection local scope, the logic in this class
    treats scope names as opaque identifiers.  The scope logic is embedded mainly
    in the Entity and EntityRoot class methods "_children".
    """
    def __init__(self, coll_id):
        """
        Initialize a cache object for a specified collection.

        coll_id         Collection id with which the vocab cache is associated.
        """
        super(CollectionVocabCacheObject, self).__init__()
        self._coll_id            = coll_id
        self._vocabs_by_id       = {}
        self._vocab_ids_by_uri   = {}
        self._vocab_ids_by_scope = {}
        return

    def _make_vocab(self, coll, vocab_id, vocab_values):
        """
        Internal helper method to construct a vocabulary namespace entity given its Id and values.

        Returns None if either Id or values evaluate as Boolean False (i.e. are None or empty).
        """
        vocab_entity = None
        if vocab_id and vocab_values:
            parent_id = vocab_values["parent_id"]
            parent    = coll
            if coll.get_id() != parent_id:
                for parent in coll.get_alt_entities(altscope="all"):
                    if parent.get_id() == parent_id:
                        break
                else:
                    msg = (
                        "Saved parent id %s not found for vocab %s in collection %s"%
                        (parent_id, vocab_id, coll.get_id())
                        )
                    log.error(msg)
                    raise ValueError(msg)
            vocab_entity = RecordVocab._child_init(parent, vocab_id)
            vocab_entity.set_values(vocab_values["data"])
        return vocab_entity

    def _load_vocab(self, coll, vocab_entity):
        """
        Internal helper method loads vocabulary namespace data to cache.

        Returns True if new vocabulary namespace was added.
        """
        vocab_id     = vocab_entity.get_id()
        vocab_uri    = vocab_entity.get_uri()
        vocab_parent = vocab_entity.get_parent().get_id()
        vocab_data   = vocab_entity.get_save_values()
        add_vocab    = False
        if vocab_id not in self._vocabs_by_id:
            self._vocabs_by_id[vocab_id]      = {"parent_id": vocab_parent, "data": vocab_data}
            self._vocab_ids_by_uri[vocab_uri] = vocab_id
            # Finish up, flush scope cache
            add_vocab = True
            self._vocab_ids_by_scope = {}
        return add_vocab

    def _load_vocabs(self, coll):
        """
        Initialize cache of RecordVocab entities, if not already done
        """
        if self._vocabs_by_id == {}:
            for vocab_id in coll._children(RecordVocab, altscope="all"):
                t = RecordVocab.load(coll, vocab_id, altscope="all")
                self._load_vocab(coll, t)
        return

    def get_coll_id(self):
        return self._coll_id

    def set_vocab(self, coll, vocab_entity):
        """
        Save a new or updated vocabulary namespace definition.
        """
        self._load_vocabs(coll)
        return self._load_vocab(coll, vocab_entity)

    def remove_vocab(self, coll, vocab_id):
        """
        Remove vocabulary namespace from collection cache.

        Returns the vocab entity removed, or None if not found.
        """
        self._load_vocabs(coll)
        vocab_values = self._vocabs_by_id.get(vocab_id, None)
        vocab_entity = self._make_vocab(coll, vocab_id, vocab_values)
        if vocab_entity:
            vocab_uri = vocab_entity.get_uri()
            self._vocabs_by_id.pop(vocab_id, None)
            self._vocab_ids_by_uri.pop(vocab_uri, None)
            self._vocab_ids_by_scope = {}
        return vocab_entity

    def get_vocab(self, coll, vocab_id):
        """
        Retrieve vocabulary namespace description entity for a given Id.

        Returns a vocabulary namespace entity for the supplied Id, or None 
        if not defined in the current cache object.
        """
        self._load_vocabs(coll)
        vocab_values = self._vocabs_by_id.get(vocab_id, None)
        return self._make_vocab(coll, vocab_id, vocab_values)

    def get_vocab_from_uri(self, coll, vocab_uri):
        """
        Retrieve a vocabulary namespace description for a given URI.

        Returns a vocabulary namespace object for the specified collecion and URI,
        or None if the URI does not exist
        """
        self._load_vocabs(coll)
        vocab_id     = self._vocab_ids_by_uri.get(vocab_uri, None)
        vocab_entity = self.get_vocab(coll, vocab_id)
        return vocab_entity

    def get_all_vocab_ids(self, coll, altscope=None):
        """
        Returns a generator of all vocabulary namespace Ids currently defined 
        for a collection, which may be qualified by a specified scope.

        NOTE: this method returns only those Ids for which a record has
        been saved to the collection data storage.
        """
        self._load_vocabs(coll)
        scope_name = altscope or "coll"     # 'None' designates collection-local scope
        if scope_name in self._vocab_ids_by_scope:
            scope_vocab_ids = self._vocab_ids_by_scope[scope_name]
        else:
            # Generate scope cache for named scope
            scope_vocab_ids = []
            for vocab_id in coll._children(RecordVocab, altscope=altscope):
                if vocab_id != layout.INITIAL_VALUES_ID:
                    scope_vocab_ids.append(vocab_id)
            self._vocab_ids_by_scope[scope_name] = scope_vocab_ids
        return scope_vocab_ids

    def get_all_vocabs(self, coll, altscope=None):
        """
        Returns a generator of all vocabulary namespace currently defined 
        for a collection, which may be qualified by a specified scope.

        NOTE: this method returns only those records that have actually been saved to
        the collection data storage.
        """
        scope_vocab_ids = self.get_all_vocab_ids(coll, altscope=altscope)
        for vocab_id in scope_vocab_ids:
            t = self.get_vocab(coll, vocab_id)
            if t:
                yield t
        return

#   ---------------------------------------------------------------------------
# 
#   Collection vocabulary-cache class
# 
#   ---------------------------------------------------------------------------

class CollectionVocabCache(object):
    """
    This class manages multiple-collection cache objects
    """
    def __init__(self):
        """
        Initialize.

        Initializes a value cache cache with no per-collection data.
        """
        super(CollectionVocabCache, self).__init__()
        self._caches = {}
        return

    # @@TODO: these are candidates for a common base class
    # Generic collection cache alllocation and access methods

    def _get_cache(self, coll, cache_cls):
        """
        Local helper returns a cache object for a specified collection.

        Creates a new cache object if needed.

        coll        is a collection object for which a cache object is obtained
        cache_cls   is a class object for the cache object to be returned.  The class 
                    constructor is called with the collection id as parameter.
        """
        coll_id = coll.get_id()
        if coll_id not in self._caches.keys():
            # Create and save new cache object
            self._caches[coll_id] = cache_cls(coll_id)
        return self._caches[coll_id]

    def flush_cache(self, coll):
        """
        Remove all cached data for a specified collection.

        Returns True if the cache object was defined, otherwise False.

        coll        is a collection object for which a cache is removed.
        """
        coll_id = coll.get_id()
        cache   = self._caches.pop(coll_id, None)
        log.info("CollectionVocabCache: flushed vocab cache for collection %s"%(coll_id,))
        return (cache is not None)

    def flush_all(self):
        """
        Remove all cached data for all collections.
        """
        self._caches = {}
        log.info("CollectionVocabCache: flushed vocab cache for all collections")
        return

    # Collection vocabulary namespace cache alllocation and access methods

    def set_vocab(self, coll, vocab_entity):
        """
        Save a new or updated vocabulary namespace definition
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.set_vocab(coll, vocab_entity)

    def remove_vocab(self, coll, vocab_id):
        """
        Remove vocabulary namespace from collection cache.

        Returns the vocabulary namespace entity removed if found, or None if not defined.
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.remove_vocab(coll, vocab_id)

    def get_vocab(self, coll, vocab_id):
        """
        Retrieve a vocabulary namespace description for a given Id.

        Returns a vocabulary namespace object for the specified collecion and Id.
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.get_vocab(coll, vocab_id)

    def get_vocab_from_uri(self, coll, vocab_uri):
        """
        Retrieve a vocabulary namespace description for a given URI.

        Returns a vocabulary namespace object for the specified collecion and URI.
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.get_vocab_from_uri(coll, vocab_uri)

    def get_all_vocab_ids(self, coll, altscope=None):
        """
        Returns all vocabulary namespaces currently available for a collection in the 
        indicated scope.  Default scope is vocabularies defined directly in the collection.
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.get_all_vocab_ids(coll, altscope=altscope)

    def get_all_vocabs(self, coll, altscope=None):
        """
        Returns all vocabulary namespace currently available for a collection in the 
        indicated scope.  Default scope is vocabularies defined directly in the collection.
        """
        vocab_cache = self._get_cache(coll, CollectionVocabCacheObject)
        return vocab_cache.get_all_vocabs(coll, altscope=altscope)

# End.
