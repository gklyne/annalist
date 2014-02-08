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
#       <collection-id>/
#         _annalist_collection/
#             coll_meta.jsonld
#             coll_prov.jsonld
#           types/
#             <type-id>/
#               type_meta.jsonld
#               type_prov.jsonld
#              :
#           views/
#               view_meta.jsonld
#               view_prov.jsonld
#              :
#           lists/
#               list_meta.jsonld
#               list_prov.jsonld
#              :
#           bridges/
#             (bridge-description (incl path mapping in collection) - @@TBD)
#              :
#           user-groups/  @@TBD
#             group-description
#              :
#           access/  @@TBD
#             default-access
#             (more details to work through - keep it simple for starters)
#         <type-id>/
#           <entity-id>/
#             entity-data.jsonld
#             entity-prov.jsonld
#            :
#          :
#        :

SITE_DIR        = "annalist_site"

# Path values in the following are relative to the base directory of the site (.../$SITE_DIR)

SITE_META_FILE  = "_annalist_site/site_meta.jsonld"
SITE_META_PATH  = SITE_META_FILE
SITE_PROV_FILE  = "_annalist_site/site_prov.jsonld"

SITE_COLL_DIR   = "%(coll_id)s"
COLL_META_FILE  = "_annalist_collection/coll_meta.jsonld"
COLL_META_PATH  = SITE_COLL_DIR + "/" + COLL_META_FILE
COLL_PROV_FILE  = "_annalist_collection/coll_prov.jsonld"

COLL_TYPE_DIR   = "types"
TYPE_INFO_DIR   = "%(type_id)s"
TYPE_META_FILE  = "type_meta.lsonld"
TYPE_META_PATH  = SITE_COLL_DIR + "/" + COLL_TYPE_DIR + "/" + TYPE_INFO_DIR + "/" + TYPE_META_FILE
TYPE_PROV_FILE  = "type_prov.lsonld"

COLL_VIEW_DIR   = "views"
VIEW_INFO_DIR   = "%(view_id)s"
VIEW_META_FILE  = "view_meta.lsonld"
VIEW_META_PATH  = SITE_COLL_DIR + "/" + COLL_VIEW_DIR + "/" + VIEW_INFO_DIR + "/" + VIEW_META_FILE
VIEW_PROV_FILE  = "view_prov.lsonld"

COLL_LIST_DIR   = "lists"
LIST_INFO_DIR   = "%(list_id)s"
LIST_META_FILE  = "list_meta.lsonld"
LIST_META_PATH  = SITE_COLL_DIR + "/" + COLL_LIST_DIR + "/" + LIST_INFO_DIR + "/" + LIST_META_FILE
LIST_PROV_FILE  = "list_prov.lsonld"

COLL_ENTITY_DIR  = "%(type_id)s/%(entity_id)s"
ENTITY_DATA_FILE = "entity-data.jsonld"
ENTITY_DATA_PATH = SITE_COLL_DIR + "/" + COLL_ENTITY_DIR + "/" + ENTITY_DATA_FILE
ENTITY_PROV_FILE = "entity-prov.jsonld"

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
        self.BASE_DIR  = base_data_dir
        self.SITE_DIR  = SITE_DIR
        self.SITE_PATH = os.path.join(base_data_dir, SITE_DIR)
        return

# End.
