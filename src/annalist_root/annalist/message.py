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
DATA_ERROR                  = "Problem with data"
UNEXPECTED_FORM_DATA        = "Unexpected form data: %r"
MISSING_COLLECTION_ID       = "Missing identifier for new collection"
INVALID_COLLECTION_ID       = "Invalid identifier for new collection: '%(coll_id)s'"
CREATED_COLLECTION_ID       = "Created new collection: '%(coll_id)s'"
NO_COLLECTION_METADATA      = "Metadata not found for collection '%(id)s'"
CONFIRM_REQUESTED_ACTION    = """Confirm requested action"""
ARE_YOU_SURE                = """Are you sure?"""
CONFIRM_OR_CANCEL           = """Click "Confirm" to continue, or "Cancel" to abort operation"""
ACTION_COMPLETED            = """Action completed"""
TURTLE_SERIALIZE_ERROR      = """Problem generating Turtle serialization from data"""
TURTLE_SERIALIZE_REASON     = """Internal description of error"""

INVALID_OPERATION_ATTEMPTED = "Attempt to peform invalid operation"
INVALID_TYPE_CHANGE         = "Change of entity type to or from '_type' is not supported"
INVALID_TYPE_RENAME         = "Renaming of Annalist built-in types is not supported"
CREATE_ENTITY_FAILED        = "Problem creating/updating entity %s/%s (see log for more info)"
RENAME_ENTITY_FAILED        = "Problem renaming entity %s/%s to %s/%s (see log for more info)"
COPY_ENTITY_FAILED          = "Problem copying entity %s/%s to %s/%s (see log for more info)"
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

NO_COLLECTION_VIEW          = "No collection selected for viewing"
MANY_COLLECTIONS_VIEW       = "Too many collections selected for viewing:  %(ids)s"
NO_COLLECTION_EDIT          = "No collection selected for editing"
MANY_COLLECTIONS_EDIT       = "Too many collections selected for viewing:  %(ids)s"
NO_COLLECTIONS_REMOVE       = "No collections selected for removal"
REMOVE_COLLECTIONS          = "Remove collection(s): %(ids)s"
MIGRATE_COLLECTION_ERROR    = "Error(s) occurred while migrating collection data for %(id)s"
MIGRATED_COLLECTION_DATA    = "Migrated data for collection %(id)s"

TOO_MANY_ENTITIES_SEL       = "Too many items selected"
NO_ENTITY_FOR_COPY          = "No entity selected to copy"
NO_ENTITY_FOR_EDIT          = "No entity selected to edit"
NO_ENTITY_FOR_DELETE        = "No entity selected to delete"
CANNOT_DELETE_ENTITY        = "Entity %(id)s of type %(type_id)s not found or cannot be deleted"
SITE_ENTITY_FOR_DELETE      = "Cannot remove site built-in entity %(id)s of type %(type_id)s, or entity not found"
TYPE_VALUES_FOR_DELETE      = "Cannot remove type %(id)s with existing values"
REMOVE_ENTITY_DATA          = "Remove entity %(id)s of type %(type_id)s in collection %(coll_id)s"

NO_TYPE_FOR_COPY            = "No entity type selected to copy"
NO_TYPE_FOR_EDIT            = "No entity type selected to edit"
NO_TYPE_FOR_DELETE          = "No entity type selected to delete"

NO_VIEW_FOR_COPY            = "No entity view selected to copy"
NO_VIEW_FOR_EDIT            = "No entity view selected to edit"
NO_VIEW_FOR_DELETE          = "No entity view selected to delete"

NO_LIST_FOR_COPY            = "No list view selected to copy"
NO_LIST_FOR_EDIT            = "No list view selected to edit"
NO_LIST_FOR_DELETE          = "No list view selected to delete"

ENTITY_MESSAGE_LABEL        = "%(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DEFAULT_LABEL        = ""    # "Entity %(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DEFAULT_COMMENT      = ""    # "Entity %(type_id)s/%(entity_id)s in collection %(coll_id)s"
ENTITY_DOES_NOT_EXIST       = "Entity %(type_id)s/%(id)s (%(label)s) does not exist"
ENTITY_COPY_FILE_ERROR      = "Failed to copy file %(file)s while copying entity %(id)% to %(src_id)s"

RESOURCE_DOES_NOT_EXIST     = "Resource %(ref)s for entity %(id)s does not exist"
RESOURCE_NOT_DEFINED        = "Resource %(ref)s is not present for entity %(id)s"
REMOVE_RECORD_TYPE          = "Remove entity type %(id)s in collection %(coll_id)s"
REMOVE_RECORD_VIEW          = "Remove entity view %(id)s in collection %(coll_id)s"
REMOVE_RECORD_LIST          = "Remove list %(id)s in collection %(coll_id)s"
LIST_NOT_DEFINED            = "List %(list_id)s/%(list_ref)s is not present for entity type %(type_id)s"
LIST_NOT_ACCESSED           = "List %(list_id)s/%(list_ref)s not accessed for entity type %(type_id)s"

SITE_RESOURCE_NOT_DEFINED   = "Resource %(ref)s is not recogized for site"
SITE_RESOURCE_NOT_EXIST     = "Site resource %(ref)s does not exist"

COLLECTION_ID               = "Problem with collection identifier"
COLLECTION_ID_INVALID       = "The collection identifier is missing or not a valid identifier"
COLLECTION_LABEL            = "Collection %(id)s"
COLLECTION_EXISTS           = "Collection %(id)s already exists"
COLLECTION_NOT_EXISTS       = "Collection %(id)s does not exist"
COLLECTION_REMOVED          = "The following collections were removed: %(ids)s"

COLLECTION_NEWER_VERSION    = ("Cannot access collection %(id)s, "+
                               "which was created by software version %(ver)s. "+
                               "(Update Annalist server software to use this collection)")
COLL_PARENT_NOT_EXIST       = "Collection %(id)s references non-existent parent %(parent_id)s"
COLL_RESOURCE_NOT_DEFINED   = "Resource %(ref)s is not recogized for collection %(id)s"
COLL_RESOURCE_NOT_EXIST     = "Resource %(ref)s for collection %(id)s does not exist"
COLL_MIGRATE_DIR_FAILED     = "Collection %(id)s migration %(old_path)s -> %(new_path)s failed. (%(exc)s)"

ANNALIST_USER_ID            = "Problem with user identifier"
ANNALIST_USER_ID_INVALID    = "The user identifier is missing or not a valid identifier"
ANNALIST_USER_LABEL         = "User %(id)s in collection %(coll_id)s"
ANNALIST_USER_EXISTS        = "User %(save_id)s in collection %(save_coll)s already exists"
ANNALIST_USER_NOT_EXISTS    = "User %(id)s in collection %(coll_id)s does not exist"
ANNALIST_USER_REMOVED       = "User %(id)s in collection %(coll_id)s was removed"

RECORD_TYPE_ID              = "Problem with entity type identifier"
RECORD_TYPE_ID_INVALID      = "The entity type identifier is missing or not a valid identifier"
RECORD_TYPE_LABEL           = "Entity type %(id)s in collection %(coll_id)s"
RECORD_TYPE_EXISTS          = "Entity type %(save_id)s in collection %(save_coll)s already exists"
RECORD_TYPE_NOT_EXISTS      = "Entity type %(id)s in collection %(coll_id)s does not exist"
RECORD_TYPE_REMOVED         = "Entity type %(id)s in collection %(coll_id)s was removed"

RECORD_VIEW_ID              = "Problem with entity view identifier"
RECORD_VIEW_ID_INVALID      = "The entity view identifier is missing or not a valid identifier"
RECORD_VIEW_LABEL           = "Entity view %(id)s in collection %(coll_id)s"
RECORD_VIEW_EXISTS          = "Entity view %(save_id)s in collection %(save_coll)s already exists"
RECORD_VIEW_NOT_EXISTS      = "Entity view %(id)s in collection %(coll_id)s does not exist"
RECORD_VIEW_REMOVED         = "Entity view %(id)s in collection %(coll_id)s was removed"
RECORD_VIEW_LOAD_ERROR      = "Error loading view '%(id)s', file %(file)s: %(message)s"
DISPLAY_ALTERNATIVE_VIEW    = "Displaying alternative view '%(id)s'"

RECORD_LIST_ID              = "Problem with list identifier"
RECORD_LIST_ID_INVALID      = "The list identifier is missing or not a valid identifier"
RECORD_LIST_LABEL           = "List %(id)s in collection %(coll_id)s"
RECORD_LIST_EXISTS          = "List %(save_id)s in collection %(save_coll)s already exists"
RECORD_LIST_NOT_EXISTS      = "List %(id)s in collection %(coll_id)s does not exist"
RECORD_LIST_REMOVED         = "List %(id)s in collection %(coll_id)s was removed"
RECORD_LIST_LOAD_ERROR      = "Error loading list '%(id)s', file %(file)s: %(message)s"
DISPLAY_ALTERNATIVE_LIST    = "Displaying alternative list '%(id)s'"

RECORD_GROUP_ID             = "Problem with field group identifier"
RECORD_GROUP_ID_INVALID     = "The field group identifier is missing or not a valid identifier"
RECORD_GROUP_LABEL          = "Field group %(id)s in collection %(coll_id)s"
RECORD_GROUP_EXISTS         = "Field group %(save_id)s in collection %(save_coll)s already exists"
RECORD_GROUP_NOT_EXISTS     = "Field group %(id)s in collection %(coll_id)s does not exist"
RECORD_GROUP_REMOVED        = "Field group %(id)s in collection %(coll_id)s was removed"

RECORD_FIELD_ID             = "Problem with view field identifier"
RECORD_FIELD_ID_INVALID     = "The view field identifier is missing or not a valid identifier"
RECORD_FIELD_LABEL          = "View field %(id)s in collection %(coll_id)s"
RECORD_FIELD_EXISTS         = "View field %(save_id)s in collection %(save_coll)s already exists"
RECORD_FIELD_NOT_EXISTS     = "View field %(id)s in collection %(coll_id)s does not exist"
RECORD_FIELD_REMOVED        = "View field %(id)s in collection %(coll_id)s was removed"

RECORD_VOCAB_ID             = "Problem with vocabulary identifier"
RECORD_VOCAB_ID_INVALID     = "The vocabulary namespace identifier is missing or not a valid identifier"
RECORD_VOCAB_LABEL          = "Vocabulary %(id)s in collection %(coll_id)s"
RECORD_VOCAB_EXISTS         = "Vocabulary %(save_id)s in collection %(save_coll)s already exists"
RECORD_VOCAB_NOT_EXISTS     = "Vocabulary %(id)s in collection %(coll_id)s does not exist"
RECORD_VOCAB_REMOVED        = "Vocabulary %(id)s in collection %(coll_id)s was removed"

RECORD_ENUM_ID              = "Problem with enumeration type identifier"
RECORD_ENUM_ID_INVALID      = "The enumeration type identifier is missing or not a valid identifier"
RECORD_ENUM_LABEL           = "Enumeration type %(id)s in collection %(coll_id)s"
RECORD_ENUM_EXISTS          = "Enumeration type %(save_id)s in collection %(save_coll)s already exists"
RECORD_ENUM_NOT_EXISTS      = "Enumeration type %(id)s in collection %(coll_id)s does not exist"
RECORD_ENUM_REMOVED         = "Enumeration type %(id)s in collection %(coll_id)s was removed"

ENTITY_DATA_ID              = "Problem with entity identifier"
ENTITY_DATA_ID_INVALID      = "The entity identifier is missing, too long, or not a valid identifier"
ENTITY_DATA_LABEL           = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s"
ENTITY_DATA_EXISTS          = "Entity %(save_id)s of type %(save_type)s in collection %(save_coll)s already exists"
ENTITY_DATA_NOT_EXISTS      = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s does not exist"
ENTITY_DATA_REMOVED         = "Entity %(id)s of type %(type_id)s in collection %(coll_id)s was removed"
ENTITY_TYPE_ID              = "Problem with entity type identifier"
ENTITY_TYPE_ID_INVALID      = "The entity type identifier is missing, too long, or not a valid identifier (%(type_id)s)"
ENTITY_LOAD_ERROR           = "Error loading '%(id)s', file %(file)s: %(message)s"

DEFAULT_LIST_UPDATED        = "Default list view for collection %(coll_id)s changed to %(list_id)s"
DEFAULT_VIEW_UPDATED        = "Default view for collection %(coll_id)s changed to %(view_id)s/%(type_id)s/%(entity_id)s"
REMOVE_FIELD_ERROR          = "Problem with remove field(s) request"
MOVE_FIELD_ERROR            = "Problem with move field up/down request"
NO_FIELD_SELECTED           = "No field(s) selected"

CREATE_FIELD_ENTITY_ERROR   = "Create new entity error"
NO_REFER_TO_TYPE			      = "Field '%(field_label)s' does not specify a valid 'Refer to type'"
MISSING_FIELD_LABEL         = "(field missing: '%(id)s')"

VIEW_DESCRIPTION_HEADING    = "Problem with view description"
VIEW_PROPERTY_DUPLICATE     = "Field %(field_id)s repeats use of property %(property_uri)s in view"

UNKNOWN_TASK_ID             	= "Unknown task Id in form response: %(task_id)s"
NO_VIEW_OR_LIST_SELECTED		  = "Please select an exiting view and/or list as a basis for creating new ones"
TASK_CREATE_VIEW_LIST       	= "Created new view and/or list for type %(id)s (%(label)s)"
TASK_CREATE_SUBTYPE         	= "Created subtype %(id)s (%(label)s)"
TASK_CREATE_SUBFIELD          = "Created field %(id)s (%(label)s) using subproperty of %(base_uri)s."
TASK_CREATE_MANY_VALUE_FIELD 	= "Created repeating value field '%(field_id)s' for '%(label)s' (check subfield 'Entity type' is blank, or matches repeat field 'Value type')"
TASK_CREATE_LIST_VALUE_FIELD 	= "Created sequence of values field '%(field_id)s' for '%(label)s' (check subfield 'Entity type' is blank, or matches repeat field 'Value type')"
TASK_CREATE_REFERENCE_FIELD 	= "Created reference to field '%(field_id)s'. (Select value for 'Refer to type' on current display, and re-save. Also check subfield 'Entity type' is blank, or matches referring field 'Value type')"

# Strings for data generated by task buttons

# TYPE_COMMENT                = (
#     "# %(type_label)s\n\n"+
#     "Entity type [%(type_label)s]($BASE:_type/%(type_id)s)."
#     )

SUBTYPE_COMMENT             = (
    "# %(type_label)s\n\n"+
    "Entity type [%(type_label)s]($BASE:_type/%(type_id)s), "+
    "subtype of [%(base_type_label)s]($BASE:_type/%(base_type_id)s)."
    )

SUBFIELD_LABEL               = (
    "@@ Subfield of %(base_field_label)s (%(base_field_id)s)@@"
    )
SUBFIELD_COMMENT             = (
    "# %(field_label)s\n\n"+
    "Field [%(field_label)s]($BASE:_field/%(field_id)s), "+
    "using property uri %(field_prop_uri)s, "+
    "subproperty of [%(base_field_label)s]($BASE:_field/%(base_field_id)s)."
    )

TYPE_VIEW_LABEL             = "%(type_label)s view"
TYPE_VIEW_COMMENT           = (
    "# %(type_label)s view\n\n"+
    "View entity of type [%(type_label)s]($BASE:_type/%(type_id)s)."
    )

TYPE_LIST_LABEL             = "%(type_label)s list"
TYPE_LIST_COMMENT           = (
    "# %(type_label)s list\n\n"+
    "List entities of type [%(type_label)s]($BASE:_type/%(type_id)s)."
    )

MANY_FIELD_LABEL            = "%(field_label)s (repeating)"
MANY_FIELD_COMMENT          = (
    "# %(field_label)s (repeating)\n\n"+
    "Zero, one or more instances of [%(field_label)s]($BASE:_field/%(field_id)s)."
    )
MANY_FIELD_PLACEHOLDER      = "(Zero, one or more %(field_label)s fields)"
MANY_FIELD_ADD              = "Add %(field_label)s"
MANY_FIELD_DELETE           = "Remove %(field_label)s"

LIST_FIELD_LABEL            = "%(field_label)s (sequence)"
LIST_FIELD_COMMENT          = (
    "# %(field_label)s (sequence)\n\n"+
    "List of [%(field_label)s]($BASE:_field/%(field_id)s) fields."
    )
LIST_FIELD_PLACEHOLDER      = "(Sequence of %(field_label)s fields)"
LIST_FIELD_ADD              = "Add %(field_label)s"
LIST_FIELD_DELETE           = "Remove %(field_label)s"

FIELD_REF_LABEL             = "%(field_label)s (ref)"
FIELD_REF_COMMENT           = "%(field_label)s (ref)"
FIELD_REF_PLACEHOLDER       = "(Reference to %(field_label)s field)"

# Other strings

COLL_README_HEAD            = (
    "# %(label)s\n\r"+
    "\n\r"+
    ""
    )

COLL_README                 = (
    "# Annalist collection `%(id)s`\n\r"+
    "\n\r"+
    "This directory contains an [Annalist](http://annalist.net) data collection.\n\r"+
    "\n\r"+
    "%(heading)s"+
    "%(comment)s"+
    "\n\r"+
    # "\n\r"+
    "")

# End.
