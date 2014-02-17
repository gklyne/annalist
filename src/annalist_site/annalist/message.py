"""
Define various message strings generated in the code
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

SITE_NAME_DEFAULT       = "Annalist linked data journal"
ACTION_COMPLETED        = "Action completed"
NO_ACTION_PERFORMED     = "No action performed"
INPUT_ERROR             = "Problem with input"
MISSING_COLLECTION_ID   = "Missing identifier for new collection"
INVALID_COLLECTION_ID   = "Invalid identifier for new collection: '%s'"
CREATED_COLLECTION_ID   = "Created new collection: '%s'"
REMOVE_COLLECTIONS      = "Remove collection(s): %s"
NO_COLLECTIONS_SELECTED = "No collections selected for removal"
COLLECTIONS_REMOVED     = "The following collections were removed: %s"
NO_TYPE_FOR_COPY        = "No record type selected to copy"
NO_TYPE_FOR_EDIT        = "No record type selected to edit"
NO_TYPE_FOR_DELETE      = "No record type selected to delete"

# End.
