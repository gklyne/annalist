"""
Annalist directory/site layout

These started out as static values in the settings module, but have
been made late-bound because the static definitions created awkward 
dependencies between configuration specific and generic settings 
modules, and also to allow the same definitions to be used for site 
directories, site URIs and possibly multiple sites.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

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

class Layout(object):

    def __init__(self, base):

        self.BASE_DATA_DIR  = base

        self.SITE_DIR       = "annalist_site"
        self.SITE_PATH      = self.BASE_DATA_DIR + "/" + self.SITE_DIR
        self.SITE_META_DIR  = "_annalist_site"
        self.SITE_META_PATH = self.SITE_PATH + "/" + self.SITE_META_DIR
        self.SITE_META_FILE = "site_meta.jsonld"

        self.SITE_COLL_DIR  = "%(coll_id)s"
        self.SITE_COLL_PATH = self.SITE_PATH + "/" + self.SITE_COLL_DIR

        self.COLL_META_DIR  = "_annalist_collection"
        self.COLL_META_PATH = self.SITE_COLL_PATH + "/" + self.COLL_META_DIR
        self.COLL_META_FILE = "coll_meta.jsonld"

        self.COLL_TYPE_DIR  = "types"
        self.TYPE_META_DIR  = "%(type_id)s"
        self.TYPE_META_PATH = self.SITE_COLL_PATH + "/" + self.COLL_TYPE_DIR + "/" + self.TYPE_META_DIR
        self.TYPE_META_FILE = "type_meta.lsonld"

        self.VIEW_META_DIR  = self.COLL_META_DIR + "/views"
        self.VIEW_META_FILE = self.VIEW_META_DIR + "%(view_id)s/view_meta.lsonld"

        self.LIST_META_DIR  = self.COLL_META_DIR + "/lists"
        self.LIST_META_FILE = self.LIST_META_DIR + "%(list_id)s/list_meta.lsonld"

        # and more...

        return

# End.
