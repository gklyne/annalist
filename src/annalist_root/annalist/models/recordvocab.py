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
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

class RecordVocab(EntityData):

    _entitytype     = ANNAL.CURIE.Vocabulary
    _entitytypeid   = "_vocab"
    _entityview     = layout.COLL_VOCAB_VIEW
    _entitypath     = layout.COLL_VOCAB_PATH
    _entityfile     = layout.VOCAB_META_FILE
    _entityref      = layout.META_VOCAB_REF

    def __init__(self, parent, vocab_id):
        """
        Initialize a new RecordVocab object, without metadata (yet).

        parent      is the parent entity from which the view is descended.
        vocab_id    the local identifier for the vocabulary; also used as namespace prefix.
        """
        super(RecordVocab, self).__init__(parent, vocab_id)
        self._parent = parent
        log.debug("RecordVocab %s: dir %s"%(vocab_id, self._entitydir))
        return

    def _migrate_filenames(self):
        """
        Override EntityData method
        """
        return None

    def _post_update_processing(self, entitydata):
        """
        Default post-update processing.

        This method is called when a RecordVocab entity has been updated.  

        It invokes the containing collection method to regenerate the JSON LD context 
        for the collection to which the entity belongs.
        """
        self._parent.generate_coll_jsonld_context()
        return entitydata

# End.
