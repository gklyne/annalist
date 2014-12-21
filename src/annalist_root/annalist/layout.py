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
#       _annalist-site/
#           site_meta.json_ld
#           site_prov.json_ld
#       c/
#         <collection-id>/
#           _annalist_collection/
#               coll_meta.jsonld
#               coll_prov.jsonld
#             types/
#               <type-id>/
#                 type_meta.jsonld
#                 type_prov.jsonld
#                :
#             views/
#                 view_meta.jsonld
#                 view_prov.jsonld
#                :
#             lists/
#                 list_meta.jsonld
#                 list_prov.jsonld
#                :
#             fields/
#                 field_meta.jsonld
#                 field_prov.jsonld
#                :
#             users/  @@TBD
#               user-description
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

SITE_META_FILE          = "_annalist_site/site_meta.jsonld"
SITE_PROV_FILE          = "_annalist_site/site_prov.jsonld"
META_SITE_REF           = "../"

SITEDATA_DIR            = "_annalist_site"
SITEDATA_VIEW           = "%(id)s/"
SITEDATA_PATH           = "%(id)s"
SITEDATA_META_FILE      = "sitedata_meta.jsonld"
META_SITEDATA_REF       = "./"

SITE_COLL_VIEW          = "c/%(id)s/"
SITE_COLL_PATH          = "c/%(id)s"
COLL_META_FILE          = "_annalist_collection/coll_meta.jsonld"
COLL_PROV_FILE          = "_annalist_collection/coll_prov.jsonld"
META_COLL_REF           = "../"

COLL_TYPE_VIEW          = "d/_type/%(id)s/"
COLL_TYPE_PATH          = "_annalist_collection/types/%(id)s"
SITE_TYPE_PATH          = "_annalist_site/types/%(id)s"
TYPE_META_FILE          = "type_meta.jsonld"
TYPE_PROV_FILE          = "type_prov.jsonld"
META_TYPE_REF           = "./"

COLL_LIST_VIEW          = "d/_list/%(id)s/"
COLL_LIST_PATH          = "_annalist_collection/lists/%(id)s"
SITE_LIST_PATH          = "_annalist_site/lists/%(id)s"
LIST_META_FILE          = "list_meta.jsonld"
LIST_PROV_FILE          = "list_prov.jsonld"
META_LIST_REF           = "./"

COLL_VIEW_VIEW          = "d/_view/%(id)s/"
COLL_VIEW_PATH          = "_annalist_collection/views/%(id)s"
SITE_VIEW_PATH          = "_annalist_site/views/%(id)s"
VIEW_META_FILE          = "view_meta.jsonld"
VIEW_PROV_FILE          = "view_prov.jsonld"
META_VIEW_REF           = "./"

COLL_GROUP_VIEW         = "d/_group/%(id)s/"
COLL_GROUP_PATH         = "_annalist_collection/groups/%(id)s"
SITE_GROUP_PATH         = "_annalist_site/groups/%(id)s"
GROUP_META_FILE         = "group_meta.jsonld"
GROUP_PROV_FILE         = "group_prov.jsonld"
META_GROUP_REF          = "./"

COLL_FIELD_VIEW         = "d/_field/%(id)s/"
COLL_FIELD_PATH         = "_annalist_collection/fields/%(id)s"
SITE_FIELD_PATH         = "_annalist_site/fields/%(id)s"
FIELD_META_FILE         = "field_meta.jsonld"
FIELD_PROV_FILE         = "field_prov.jsonld"
META_FIELD_REF          = "./"

COLL_USER_VIEW         = "d/_user/%(id)s/"
COLL_USER_PATH         = "_annalist_collection/users/%(id)s"
SITE_USER_PATH         = "_annalist_site/users/%(id)s"
USER_META_FILE         = "user_meta.jsonld"
USER_PROV_FILE         = "user_prov.jsonld"
META_USER_REF          = "./"

COLL_ENUM_VIEW          = "d/%(type_id)s/%(id)s/"
COLL_ENUM_PATH          = "_annalist_collection/enums/%(type_id)s/%(id)s"
SITE_ENUM_PATH          = "_annalist_site/enums/%(type_id)s/%(id)s"
ENUM_META_FILE          = "enum_meta.jsonld"
ENUM_PROV_FILE          = "enum_prov.jsonld"
META_ENUM_REF           = "./"

COLL_TYPEDATA_VIEW      = "d/%(id)s/"
COLL_TYPEDATA_PATH      = "d/%(id)s"
TYPEDATA_META_FILE      = "type_data_meta.jsonld"
META_TYPEDATA_REF       = "./"

TYPEDATA_ENTITY_VIEW    = "%(id)s/"
TYPEDATA_ENTITY_PATH    = "%(id)s"
ENTITY_DATA_FILE        = "entity-data.jsonld"
ENTITY_PROV_FILE        = "entity-prov.jsonld"
DATA_ENTITY_REF         = "./"

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
        self.BASE_DIR       = base_data_dir
        self.SITE_DIR       = SITE_DIR
        self.SITEDATA_DIR   = SITEDATA_DIR
        self.SITE_PATH      = os.path.join(base_data_dir, SITE_DIR)
        return

# End.
