"""
Define various message strings generated in the code.
As far as possible, user display strings referenced directly by 
source code are isolated here to facilitate editing and translation.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

SITE_NAME_DEFAULT           = "Annalist linked data notebook"
ACTION_COMPLETED            = "Action completed"
NO_ACTION_PERFORMED         = "No action performed"
NO_SELECTION                = "(No '%(id)s' selected)"
INPUT_ERROR                 = "Problem with input"
SYSTEM_ERROR                = "System error"
UNEXPECTED_FORM_DATA        = "Unexpected form data: %r"
MISSING_COLLECTION_ID       = "Missing identifier for new collection"
INVALID_COLLECTION_ID       = "Invalid identifier for new collection: '%(coll_id)s'"
CREATED_COLLECTION_ID       = "Created new collection: '%(coll_id)s'"

INVALID_OPERATION_ATTEMPTED = "Attempt to peform invalid operation"
INVALID_TYPE_CHANGE         = "Change of record type to or from '_type' is not supported"
INVALID_TYPE_RENAME         = "Renaming of Annalist built-in types is not supported"
CREATE_ENTITY_FAILED        = "Problem creating/updating entity %s/%s (see log for more info)"
RENAME_ENTITY_FAILED        = "Problem renaming entity %s/%s to %s/%s (see log for more info)"
RENAME_TYPE_FAILED          = "Problem renaming type %s to %s (see log for more info)"

IMPORT_ERROR                = "Resource import error"
IMPORT_ERROR_REASON         = ("Failed to import resource %(import_url)s as %(import_name)s"+
                               " for %(type_id)s/%(id)s: %(import_exc)s")
IMPORT_DONE                 = "Resource imported"
IMPORT_DONE_DETAIL          = ("Imported <%(resource_url)s>"+
                               " as %(import_name)s"+
                               " for entity %(type_id)s/%(id)s")

UPLOAD_ERROR                = "File upload error"
UPLOAD_ERROR_REASON         = ("Failed to upload file %(uploaded_file)s as %(upload_name)s"+
                               " for %(type_id)s/%(id)s: %(import_exc)s")
UPLOAD_DONE                 = "File uploaded"
UPLOAD_DONE_DETAIL          = ("Uploaded <%(uploaded_file)s>"+
                               " as %(upload_name)s"+
                               " for entity %(type_id)s/%(id)s")

REMOVE_COLLECTIONS          = "Remove collection(s): %(ids)s"
NO_COLLECTIONS_SELECTED     = "No collections selected for removal"
COLLECTIONS_REMOVED         = "The following collections were removed: %(ids)s"

TOO_MANY_ENTITIES_SEL       = "Too many items selected"
NO_ENTITY_FOR_COPY          = "No data record selected to copy"
NO_ENTITY_FOR_EDIT          = "No data record selected to edit"
NO_ENTITY_FOR_DELETE        = "No data record selected to delete"
SITE_ENTITY_FOR_DELETE      = "Cannot remove site built-in entity %(id)s, or entity not found"
TYPE_VALUES_FOR_DELETE      = "Cannot remove type %(type_id)s with existing values"
REMOVE_ENTITY_DATA          = "Remove record %(id)s of type %(type_id)s in collection %(coll_id)s"

NO_TYPE_FOR_COPY            = "No record type selected to copy"
NO_TYPE_FOR_EDIT            = "No record type selected to edit"
NO_TYPE_FOR_DELETE          = "No record type selected to delete"

NO_VIEW_FOR_COPY            = "No record view selected to copy"
NO_VIEW_FOR_EDIT            = "No record view selected to edit"
NO_VIEW_FOR_DELETE          = "No record view selected to delete"

NO_LIST_FOR_COPY            = "No list view selected to copy"
NO_LIST_FOR_EDIT            = "No list view selected to edit"
NO_LIST_FOR_DELETE          = "No list view selected to delete"

ENTITY_MESSAGE_LABEL        = "%(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DEFAULT_LABEL        = ""    # "Entity %(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DEFAULT_COMMENT      = ""    # "Entity %(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DOES_NOT_EXIST       = "Entity %(id)s does not exist"

RESOURCE_DOES_NOT_EXIST     = "Resource %(ref)s for entity %(id)s does not exist"
RESOURCE_NOT_DEFINED        = "Resource %(ref)s is not present for entity %(id)s"
REMOVE_RECORD_TYPE          = "Remove record type %(id)s in collection %(coll_id)s"
REMOVE_RECORD_LIST          = "Remove record list %(id)s in collection %(coll_id)s"
REMOVE_RECORD_VIEW          = "Remove record view %(id)s in collection %(coll_id)s"

COLLECTION_ID               = "Problem with collection identifier"
COLLECTION_ID_INVALID       = "The collection identifier is missing or not a valid identifier"
COLLECTION_LABEL            = "Collection %(id)s"
COLLECTION_EXISTS           = "Collection %(id)s already exists"
COLLECTION_NOT_EXISTS       = "Collection %(id)s does not exist"
COLLECTION_NEWER_VERSION    = ("Cannot access collection %(id)s, "+
                               "which was created by software version %(ver)s. "+
                               "(Update Annalist server software to use this collection)")

ANNALIST_USER_ID            = "Problem with user identifier"
ANNALIST_USER_ID_INVALID    = "The user identifier is missing or not a valid identifier"
ANNALIST_USER_LABEL         = "User %(id)s in collection %(coll_id)s"
ANNALIST_USER_EXISTS        = "User %(id)s in collection %(coll_id)s already exists"
ANNALIST_USER_NOT_EXISTS    = "User %(id)s in collection %(coll_id)s does not exist"
ANNALIST_USER_REMOVED       = "User %(id)s in collection %(coll_id)s was removed"

RECORD_TYPE_ID              = "Problem with record type identifier"
RECORD_TYPE_ID_INVALID      = "The record type identifier is missing or not a valid identifier"
RECORD_TYPE_LABEL           = "Record type %(id)s in collection %(coll_id)s"
RECORD_TYPE_EXISTS          = "Record type %(id)s in collection %(coll_id)s already exists"
RECORD_TYPE_NOT_EXISTS      = "Record type %(id)s in collection %(coll_id)s does not exist"
RECORD_TYPE_REMOVED         = "Record type %(id)s in collection %(coll_id)s was removed"

RECORD_LIST_ID              = "Problem with record list identifier"
RECORD_LIST_ID_INVALID      = "The record list identifier is missing or not a valid identifier"
RECORD_LIST_LABEL           = "Record list %(id)s in collection %(coll_id)s"
RECORD_LIST_EXISTS          = "Record list %(id)s in collection %(coll_id)s already exists"
RECORD_LIST_NOT_EXISTS      = "Record list %(id)s in collection %(coll_id)s does not exist"
RECORD_LIST_REMOVED         = "Record list %(id)s in collection %(coll_id)s was removed"

RECORD_VIEW_ID              = "Problem with record view identifier"
RECORD_VIEW_ID_INVALID      = "The record view identifier is missing or not a valid identifier"
RECORD_VIEW_LABEL           = "Record view %(id)s in collection %(coll_id)s"
RECORD_VIEW_EXISTS          = "Record view %(id)s in collection %(coll_id)s already exists"
RECORD_VIEW_NOT_EXISTS      = "Record view %(id)s in collection %(coll_id)s does not exist"
RECORD_VIEW_REMOVED         = "Record view %(id)s in collection %(coll_id)s was removed"

RECORD_GROUP_ID             = "Problem with field group identifier"
RECORD_GROUP_ID_INVALID     = "The field group identifier is missing or not a valid identifier"
RECORD_GROUP_LABEL          = "Field group %(id)s in collection %(coll_id)s"
RECORD_GROUP_EXISTS         = "Field group %(id)s in collection %(coll_id)s already exists"
RECORD_GROUP_NOT_EXISTS     = "Field group %(id)s in collection %(coll_id)s does not exist"
RECORD_GROUP_REMOVED        = "Field group %(id)s in collection %(coll_id)s was removed"

RECORD_FIELD_ID             = "Problem with record field identifier"
RECORD_FIELD_ID_INVALID     = "The record field identifier is missing or not a valid identifier"
RECORD_FIELD_LABEL          = "Record field %(id)s in collection %(coll_id)s"
RECORD_FIELD_EXISTS         = "Record field %(id)s in collection %(coll_id)s already exists"
RECORD_FIELD_NOT_EXISTS     = "Record field %(id)s in collection %(coll_id)s does not exist"
RECORD_FIELD_REMOVED        = "Record field %(id)s in collection %(coll_id)s was removed"

RECORD_ENUM_ID              = "Problem with enumeration type identifier"
RECORD_ENUM_ID_INVALID      = "The enumeration type identifier is missing or not a valid identifier"
RECORD_ENUM_LABEL           = "Enumeration type %(id)s in collection %(coll_id)s"
RECORD_ENUM_EXISTS          = "Enumeration type %(id)s in collection %(coll_id)s already exists"
RECORD_ENUM_NOT_EXISTS      = "Enumeration type %(id)s in collection %(coll_id)s does not exist"
RECORD_ENUM_REMOVED         = "Enumeration type %(id)s in collection %(coll_id)s was removed"

ENTITY_DATA_ID              = "Problem with entity identifier"
ENTITY_DATA_ID_INVALID      = "The entity identifier is missing, too long, or not a valid identifier"
ENTITY_DATA_LABEL           = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s"
ENTITY_DATA_EXISTS          = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s already exists"
ENTITY_DATA_NOT_EXISTS      = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s does not exist"
ENTITY_DATA_REMOVED         = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s was removed"
ENTITY_TYPE_ID              = "Problem with entity type identifier"
ENTITY_TYPE_ID_INVALID      = "The entity type identifier is missing, too long, or not a valid identifier (%(type_id)s)"

DEFAULT_VIEW_UPDATED        = "Default list view for collection %(coll_id)s changed to %(list_id)s"
REMOVE_FIELD_ERROR          = "Problem with remove field(s) request"
MOVE_FIELD_ERROR            = "Problem with move field up/down request"
NO_FIELD_SELECTED           = "No field(s) selected"

VIEW_DESCRIPTION_HEADING    = "Problem with view description"
VIEW_PROPERTY_DUPLICATE     = "Field %(field_id)s repeats use of property %(property_uri)s in view"

UNKNOWN_TASK_ID             = "Unknown task Id in form response: %(task_id)s"
TASK_CREATE_VIEW_LIST       = "Created view and list for %(label)s"
TASK_CREATE_REPEAT_FIELD    = "Created repeating-value field and group %(field_id)s for %(label)s"
TASK_CREATE_REFERENCE_FIELD = "Created reference to field %(field_id)s: select 'Refer to type' value and re-save"
# End.
