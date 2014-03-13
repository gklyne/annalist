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
#             bridges/
#               (bridge-description (incl path mapping in collection) - @@TBD)
#                :
#             user-groups/  @@TBD
#               group-description
#                :
#             access/  @@TBD
#               default-access
#               (more details to work through - keep it simple for starters)
#           <type-id>/
#             <entity-id>/
#               entity-data.jsonld
#               entity-prov.jsonld
#              :
#            :
#          :

SITE_DIR                = "annalist_site"

SITE_META_FILE          = "_annalist_site/site_meta.jsonld"
SITE_PROV_FILE          = "_annalist_site/site_prov.jsonld"
META_SITE_REF           = "../"

SITEDATA_DIR            = "sitedata"
SITEDATA_PATH           = "%(id)s"
SITEDATA_META_FILE      = "sitedata_meta.jsonld"
META_SITEDATA_REF       = "./"

SITE_COLL_PATH          = "c/%(id)s"
COLL_META_FILE          = "_annalist_collection/coll_meta.jsonld"
COLL_PROV_FILE          = "_annalist_collection/coll_prov.jsonld"
META_COLL_REF           = "../"

COLL_TYPE_PATH          = "types/%(id)s"
TYPE_META_FILE          = "type_meta.jsonld"
TYPE_PROV_FILE          = "type_prov.jsonld"
META_TYPE_REF           = "./"

COLL_VIEW_PATH          = "views/%(id)s"
VIEW_META_FILE          = "view_meta.jsonld"
VIEW_PROV_FILE          = "view_prov.jsonld"
META_VIEW_REF           = "./"

COLL_LIST_PATH          = "lists/%(id)s"
LIST_META_FILE          = "list_meta.jsonld"
LIST_PROV_FILE          = "list_prov.jsonld"
META_LIST_REF           = "./"

COLL_FIELD_PATH         = "fields/%(id)s"
FIELD_META_FILE         = "field_meta.jsonld"
FIELD_PROV_FILE         = "field_prov.jsonld"
META_FIELD_REF          = "./"

COLL_TYPEDATA_PATH      = "d/%(id)s"
TYPEDATA_META_FILE      = "type_data_meta.jsonld"
META_TYPEDATA_REF       = "./"

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
