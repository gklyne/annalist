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
#         site_meta.json_ld
#       <collection-id>/
#         _annalist_collection/
#           coll_meta.jsonld
#           types/
#             <type-id>/
#               type_meta.jsonld
#              :
#           views/
#             <view-id>/
#               view_meta.jsonld
#              :
#           lists/
#             <list-id>/
#               list_meta.jsonld
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

SITE_META_DIR   = "_annalist_site"
SITE_META_PATH  = SITE_META_DIR
SITE_META_FILE  = "site_meta.jsonld"

SITE_COLL_DIR   = "%(coll_id)s"
SITE_COLL_PATH  = SITE_COLL_DIR

COLL_META_DIR   = "_annalist_collection"
COLL_META_PATH  = SITE_COLL_PATH + "/" + COLL_META_DIR
COLL_META_FILE  = "coll_meta.jsonld"

COLL_TYPE_DIR   = "types"
TYPE_META_DIR   = "%(type_id)s"
TYPE_META_PATH  = SITE_COLL_PATH + "/" + COLL_TYPE_DIR + "/" + TYPE_META_DIR
TYPE_META_FILE  = "type_meta.lsonld"

VIEW_META_DIR   = COLL_META_DIR + "/views"
VIEW_META_FILE  = VIEW_META_DIR + "%(view_id)s/view_meta.lsonld"

LIST_META_DIR   = COLL_META_DIR + "/lists"
LIST_META_FILE  = LIST_META_DIR + "%(list_id)s/list_meta.lsonld"

# and more...

class Layout(object):
    """
    A dynamically created layout value with paths that are dynamnically constructed 
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
