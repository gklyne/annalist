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
SYSTEM_ERROR            = "System error"
UNEXPECTED_FORM_DATA    = "Unexpected form data: %r"
MISSING_COLLECTION_ID   = "Missing identifier for new collection"
INVALID_COLLECTION_ID   = "Invalid identifier for new collection: '%s'"
CREATED_COLLECTION_ID   = "Created new collection: '%s'"
REMOVE_COLLECTIONS      = "Remove collection(s): %s"
NO_COLLECTIONS_SELECTED = "No collections selected for removal"
COLLECTIONS_REMOVED     = "The following collections were removed: %s"
NO_TYPE_FOR_COPY        = "No record type selected to copy"
NO_TYPE_FOR_EDIT        = "No record type selected to edit"
NO_TYPE_FOR_DELETE      = "No record type selected to delete"
DOES_NOT_EXIST          = "%s does not exist"
REMOVE_RECORD_TYPE      = "Remove record type %s in collection %s"
COLLECTION_ID           = "Problem with collection identifier"
COLLECTION_ID_INVALID   = "The collection identifier is missing or not a valid identifier"
COLLECTION_LABEL        = "Collection %s"
COLLECTION_EXISTS       = "Collection %s already exists"
COLLECTION_NOT_EXISTS   = "Collection %s does not exist"
RECORD_TYPE_ID          = "Problem with record type identifier"
RECORD_TYPE_ID_INVALID  = "The record type identifier is missing or not a valid identifier"
RECORD_TYPE_LABEL       = "Record type %s in collection %s"
RECORD_TYPE_EXISTS      = "Record type %s in collection %s already exists"
RECORD_TYPE_NOT_EXISTS  = "Record type %s in collection %s does not exist"
RECORD_TYPE_REMOVED     = "Record type %s in collection %s was removed"
ENTITY_DATA_ID          = "Problem with entity identifier"
ENTITY_DATA_ID_INVALID  = "The entity identifier is missing or not a valid identifier"
ENTITY_DATA_LABEL       = "Entity %s of type %s in collection %s"
ENTITY_DATA_EXISTS      = "Entity %s of type %s in collection %s already exists"
ENTITY_DATA_NOT_EXISTS  = "Entity %s of type %s in collection %s does not exist"
ENTITY_DATA_REMOVED     = "Entity %s of type %s in collection %s was removed"



# End.
