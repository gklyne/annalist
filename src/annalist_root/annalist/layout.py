"""
Annalist directory/site layout
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path

import logging
log = logging.getLogger(__name__)

# Annalist configuration and metadata files
#
# Directory layout:
#
#   $BASE_DATA_DIR
#     annalist-site/
#       c/
#         _annalist-site/
#           _annalist_collection/
#             coll_meta.json_ld
#             coll_prov.json_ld
#             coll_context.json_ld
#             types/
#              :
#         <collection-id>/
#           _annalist_collection/
#             coll_meta.jsonld
#             coll_prov.jsonld
#             types/
#               <type-id>/
#                 type_meta.jsonld
#                 type_prov.jsonld
#                :
#             views/
#               <view-id>/
#                 view_meta.jsonld
#                 view_prov.jsonld
#                :
#             lists/
#               <list-id>/
#                 list_meta.jsonld
#                 list_prov.jsonld
#                :
#             fields/
#               <field-id>/
#                 field_meta.jsonld
#                 field_prov.jsonld
#                :
#             groups/
#               <group-id>/
#                 group_meta.jsonld
#                 group_prov.jsonld
#                :
#             users/
#               <user-id>/
#                 user_meta.jsonld
#                 user_prov.jsonld
#                :
#             vocabs/
#               <vocab-id>/
#                 vocab_meta.jsonld
#                 vocab_prov.jsonld
#                :
#           d/
#             <type-id>/
#               <entity-id>/
#                 entity-data.jsonld
#                 entity-prov.jsonld
#                :
#              :
#         <collection-id>/
#          :

SITE_DIR                = "annalist_site"
SITEDATA_ID             = "_annalist_site"
BIBDATA_ID              = "bib_definitions"
SITEDATA_DIR            = "c/%(id)s"%{'id': SITEDATA_ID}
SITEDATA_OLD_DIR        = "_annalist_site"
SITE_META_PATH          = ""
SITE_META_FILE          = "@@unused@@site_meta.jsonld"
META_SITE_REF           = "@@unused@@./"
SITE_COLL_VIEW          = "c/%(id)s/"
SITE_COLL_PATH          = "c/%(id)s"
SITE_COLL_CONTEXT_PATH  = "c/%(id)s/d/"    # Used for testing

COLL_META_DIR           = "_annalist_collection"
COLL_META_FILE          = "coll_meta.jsonld"
COLL_PROV_FILE          = "coll_prov.jsonld"
COLL_META_REF           = COLL_META_DIR + "/" + COLL_META_FILE
META_COLL_REF           = "../"
COLL_PROV_REF           = COLL_META_DIR + "/" + COLL_PROV_FILE
COLL_CONTEXT_PATH       = "d/"
COLL_META_CONTEXT_PATH  = META_COLL_REF+COLL_CONTEXT_PATH           # used in models
COLL_CONTEXT_FILE       = "coll_context.jsonld"

SITEDATA_META_DIR       = SITEDATA_DIR + "/" + COLL_META_DIR        # used in tests
SITEDATA_META_FILE      = COLL_META_FILE                            # used in views
SITEDATA_PROV_FILE      = COLL_PROV_FILE                            # used in views
#@@ SITEDATA_META_REF       = SITEDATA_META_DIR + "/" + SITEDATA_META_FILE
#@@ META_SITEDATA_REF       = META_COLL_REF
SITEDATA_CONTEXT_PATH   = "./"                                      # used in models
SITEDATA_ENUM_PATH      = "enums/"
# SITEDATA_PROV_REF       = SITEDATA_META_DIR + "/coll_prov.jsonld"
# SITEDATA_META_SITE_REF  = "../../../"

COLL_COLLDATA_VIEW      = "d/_coll/%(id)s/"

COLL_TYPE_VIEW          = "d/_type/%(id)s/"
COLL_TYPE_PATH          = COLL_META_DIR + "/types/%(id)s"
SITE_TYPE_PATH          = COLL_TYPE_PATH
TYPE_META_FILE          = "type_meta.jsonld"
TYPE_PROV_FILE          = "type_prov.jsonld"
META_TYPE_REF           = "./"

COLL_LIST_VIEW          = "d/_list/%(id)s/"
COLL_LIST_PATH          = COLL_META_DIR + "/lists/%(id)s"
SITE_LIST_PATH          = COLL_LIST_PATH
LIST_META_FILE          = "list_meta.jsonld"
LIST_PROV_FILE          = "list_prov.jsonld"
META_LIST_REF           = "./"

COLL_VIEW_VIEW          = "d/_view/%(id)s/"
COLL_VIEW_PATH          = COLL_META_DIR + "/views/%(id)s"
SITE_VIEW_PATH          = COLL_VIEW_PATH
VIEW_META_FILE          = "view_meta.jsonld"
VIEW_PROV_FILE          = "view_prov.jsonld"
META_VIEW_REF           = "./"

COLL_GROUP_VIEW         = "d/_group/%(id)s/"
COLL_GROUP_PATH         = COLL_META_DIR + "/groups/%(id)s"
SITE_GROUP_PATH         = COLL_GROUP_PATH
GROUP_META_FILE         = "group_meta.jsonld"
GROUP_PROV_FILE         = "group_prov.jsonld"
META_GROUP_REF          = "./"

COLL_FIELD_VIEW         = "d/_field/%(id)s/"
COLL_FIELD_PATH         = COLL_META_DIR + "/fields/%(id)s"
SITE_FIELD_PATH         = COLL_FIELD_PATH
FIELD_META_FILE         = "field_meta.jsonld"
FIELD_PROV_FILE         = "field_prov.jsonld"
META_FIELD_REF          = "./"

COLL_USER_VIEW          = "d/_user/%(id)s/"
COLL_USER_PATH          = COLL_META_DIR + "/users/%(id)s"
SITE_USER_PATH          = COLL_USER_PATH
USER_META_FILE          = "user_meta.jsonld"
USER_PROV_FILE          = "user_prov.jsonld"
META_USER_REF           = "./"
USER_CONTEXT_REF        = "../.."
USER_CONTEXT_FILE       = USER_CONTEXT_REF + "/" + COLL_CONTEXT_FILE

COLL_VOCAB_VIEW         = "d/_vocab/%(id)s/"
COLL_VOCAB_PATH         = COLL_META_DIR + "/vocabs/%(id)s"
SITE_VOCAB_PATH         = COLL_VOCAB_PATH
VOCAB_META_FILE         = "vocab_meta.jsonld"
VOCAB_PROV_FILE         = "vocab_prov.jsonld"
META_VOCAB_REF          = "./"

COLL_ENUM_VIEW          = "d/%(type_id)s/%(id)s/"
COLL_ENUM_PATH          = COLL_META_DIR + "/enums/%(type_id)s/%(id)s"
SITE_ENUM_PATH          = COLL_ENUM_PATH
ENUM_META_FILE          = "enum_meta.jsonld"
ENUM_PROV_FILE          = "enum_prov.jsonld"
META_ENUM_REF           = "./"

COLL_TYPEDATA_VIEW      = "d/%(id)s/"
COLL_TYPEDATA_PATH      = "d/%(id)s"
TYPEDATA_META_FILE      = "type_data_meta.jsonld"
META_TYPEDATA_REF       = "./"

TYPEDATA_ENTITY_VIEW    = "%(id)s/"
TYPEDATA_ENTITY_PATH    = "%(id)s"
COLL_ENTITY_VIEW        = "d/%(type_id)s/%(id)s/"
COLL_ENTITY_PATH        = "d/%(type_id)s/%(id)s"
SITE_ENTITY_VIEW        = "c/%(coll_id)s/d/%(type_id)s/%(id)s/"
SITE_ENTITY_PATH        = "c/%(coll_id)s/d/%(type_id)s/%(id)s"
ENTITY_DATA_FILE        = "entity_data.jsonld"
ENTITY_PROV_FILE        = "entity_prov.jsonld"
DATA_ENTITY_REF         = "./"
CONTEXT_ENTITY_REF      = "%(type_id)s/%(id)s/"
ENTITY_CONTEXT_REF      = "../.."
ENTITY_CONTEXT_FILE     = ENTITY_CONTEXT_REF + "/" + COLL_CONTEXT_FILE
ENTITY_OLD_DATA_FILE    = "entity-data.jsonld"

# and more...

class Layout(object):
    """
    A dynamically created layout value with paths that are dynamically constructed 
    using a supplied base directory.
    """

    def __init__(self, base_data_dir):
        """
        Dynamically initialize a layout value
        """
        self.BASE_DIR           = base_data_dir
        self.SITE_DIR           = SITE_DIR
        self.SITEDATA_ID        = SITEDATA_ID
        self.SITEDATA_DIR       = SITEDATA_DIR
        self.SITEDATA_OLD_DIR   = SITEDATA_OLD_DIR
        self.SITEDATA_META_DIR  = SITEDATA_META_DIR                         # e.g. c/_annalist_site/_annalist_collection
        self.SITE_PATH          = os.path.join(base_data_dir, SITE_DIR)     # e.g. /data/annalist_site
        self.SITEDATA_CONTEXT_DIR = os.path.join(                          # e.g. /data/annalist_site/c/_annalist_site/_annalist_collection/site_context.jsonld
            base_data_dir, SITE_DIR, SITEDATA_META_DIR, COLL_CONTEXT_FILE
            ) 
        return

# End.
