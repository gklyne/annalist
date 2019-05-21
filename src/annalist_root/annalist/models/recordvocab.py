"""
Annalist vocabulary record
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import os.path
import shutil

from django.conf import settings

from annalist                   import message
from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL, RDFS, OWL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordVocab(EntityData):

    _entitytype     = ANNAL.CURIE.Vocabulary
    _entitytypeid   = layout.VOCAB_TYPEID
    _entityroot     = layout.COLL_VOCAB_PATH
    _entityview     = layout.COLL_VOCAB_VIEW
    _entityfile     = layout.VOCAB_META_FILE

    def __init__(self, parent, vocab_id):
        """
        Initialize a new RecordVocab object, without metadata (yet).

        parent      is the parent collection in which the namespace is defined.
        vocab_id    the local identifier for the vocabulary; also used as namespace prefix.
        """
        super(RecordVocab, self).__init__(parent, vocab_id)
        self._parent = parent
        # log.debug("RecordVocab %s: dir %s"%(vocab_id, self._entitydir))
        return

    @classmethod
    def _pre_save_validation(cls, type_id, entity_id, entitydata):
        """
        Pre-save value validation.

        Override EntityRoot method

        Returns a list of strings describing any errors detected, or an empty list 
        if no problems are found.
        """
        errs = super(RecordVocab, cls)._pre_save_validation(type_id, entity_id, entitydata)
        if ANNAL.CURIE.uri in entitydata:
            vuri = entitydata[ANNAL.CURIE.uri]
            if vuri[-1] not in {":", "/", "?", "#"}:
                msg = message.RECORD_VOCAB_URI_TERM%({"id": entity_id, "uri": vuri})
                log.info(msg)
                errs.append(msg)
        return errs

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
        Post-update processing.

        This method is called when a RecordVocab entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the entity belongs.
        """
        self._parent.flush_collection_caches()
        self._parent.generate_coll_jsonld_context(flags=post_update_flags)
        return entitydata

    def _post_remove_processing(self, post_update_flags):
        """
        Post-remove processing.

        This method is called when an entity has been removed.  
        """
        self._parent.flush_collection_caches()
        return

# End.
