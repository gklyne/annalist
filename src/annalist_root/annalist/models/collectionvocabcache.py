from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

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

from annalist.models.collectionentitycache  import (
    Cache_Error, CollectionEntityCacheObject, CollectionEntityCache
    )
from annalist.models.recordvocab            import RecordVocab

#   ---------------------------------------------------------------------------
# 
#   Collection namespace vocabulary cache class
# 
#   ---------------------------------------------------------------------------

class CollectionVocabCache(CollectionEntityCache):
    """
    This class manages and accesses namespace vocabulary cache objects for
    multiple collections.

    Per-collection cacheing is implemented by CollectionEntityCacheObject.
    """
    def __init__(self):
        """
        Initialize.

        Initializes a namespace vocabulary cache cache with no per-collection data.
        """
        super(CollectionVocabCache, self).__init__(CollectionEntityCacheObject, RecordVocab)
        return

    # Collection vocabulary namespace cache alllocation and access methods

    def set_vocab(self, coll, vocab_entity):
        """
        Save a new or updated vocabulary namespace definition
        """
        return self.set_entity(coll, vocab_entity)

    def remove_vocab(self, coll, vocab_id):
        """
        Remove vocabulary namespace from collection cache.

        Returns the vocabulary namespace entity removed if found, or None if not defined.
        """
        return self.remove_entity(coll, vocab_id)

    def get_vocab(self, coll, vocab_id):
        """
        Retrieve a vocabulary namespace description for a given Id.

        Returns a vocabulary namespace object for the specified collecion and Id.
        """
        return self.get_entity(coll, vocab_id)

    def get_vocab_from_uri(self, coll, vocab_uri):
        """
        Retrieve a vocabulary namespace description for a given URI.

        Returns a vocabulary namespace object for the specified collecion and URI.
        """
        return self.get_entity_from_uri(coll, vocab_uri)

    def get_all_vocab_ids(self, coll, altscope=None):
        """
        Returns all vocabulary namespaces currently available for a collection in the 
        indicated scope.  Default scope is vocabularies defined directly in the collection.
        """
        return self.get_all_entity_ids(coll, altscope=altscope)

    def get_all_vocabs(self, coll, altscope=None):
        """
        Returns all vocabulary namespace currently available for a collection in the 
        indicated scope.  Default scope is vocabularies defined directly in the collection.
        """
        return self.get_all_entities(coll, altscope=altscope)

# End.
