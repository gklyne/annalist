"""
Annalist vocabulary record
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import urlparse
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL, RDFS, OWL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordVocab(EntityData):

    _entitytype     = ANNAL.CURIE.Vocabulary
    _entitytypeid   = layout.VOCAB_TYPEID
    _entityview     = layout.COLL_VOCAB_VIEW
    _entitypath     = layout.COLL_VOCAB_PATH
    _entityfile     = layout.VOCAB_META_FILE

    def __init__(self, parent, vocab_id):
        """
        Initialize a new RecordVocab object, without metadata (yet).

        parent      is the parent entity from which the view is descended.
        vocab_id    the local identifier for the vocabulary; also used as namespace prefix.
        """
        super(RecordVocab, self).__init__(parent, vocab_id)
        self._parent = parent
        # log.debug("RecordVocab %s: dir %s"%(vocab_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _migrate_values(self, entitydata):
        """
        Vocabulary namespace definition entity format migration method.

        The specification for this method is that it returns an entitydata value
        which is a copy of the supplied entitydata with format migrations applied.

        NOTE:  implementations are free to apply migrations in-place.  The resulting 
        entitydata should be exctly as the supplied data *should* appear in storage
        to conform to the current format of the data.  The migration function should 
        be idempotent; i.e.
            x._migrate_values(x._migrate_values(e)) == x._migrate_values(e)
        """
        # Migrate
        #   rdfs:seeAlso [ { 'owl:sameAs': <foo> }, ... ]
        # to:
        #   rdfs:seeAlso [ { '@id': <foo> }, ... ]
        seeAlso = entitydata.get(RDFS.CURIE.seeAlso, [])
        for i in range(len(seeAlso)):
            if OWL.CURIE.sameAs in seeAlso[i]:
                seeAlso[i]['@id'] = seeAlso[i].pop(OWL.CURIE.sameAs)
        # Return result
        return entitydata

    def _post_update_processing(self, entitydata, post_update_flags):
        """
        Default post-update processing.

        This method is called when a RecordVocab entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the entity belongs.
        """
        self._parent.generate_coll_jsonld_context(flags=post_update_flags)
        return entitydata

# End.
