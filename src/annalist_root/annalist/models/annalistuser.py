from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Annalist user record

A user is represented in a collectionm by:
- an ID (slug)
- a URI (currently a mailto: URI)
- a label (full name)
- a description
- a list of permissions applicable to the collection
- ...

The ID and URI must be matched by the authenticated issuer of an HTTP request for the
permissionms to be applied.  Other fields are cosmetic.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import os.path
import shutil

import logging
log = logging.getLogger(__name__)

from django.conf import settings

from annalist                   import layout
from annalist.exceptions        import Annalist_Error
from annalist.identifiers       import ANNAL
from annalist                   import util
from annalist.models.entity     import Entity
from annalist.models.entitydata import EntityData

site_default_user_id  = "_site_default_user_perms"
site_default_user_uri = "annal:User/_default_user_perms"

default_user_id  = "_default_user_perms"
default_user_uri = "annal:User/_default_user_perms"

unknown_user_id  = "_unknown_user_perms"
unknown_user_uri = "annal:User/_unknown_user_perms"

class AnnalistUser(EntityData):

    _entitytype     = ANNAL.CURIE.User
    _entitytypeid   = layout.USER_TYPEID
    _entityroot     = layout.COLL_USER_PATH
    _entityview     = layout.COLL_USER_VIEW
    _entityfile     = layout.USER_META_FILE

    def __init__(self, parent, user_id):
        """
        Initialize a new AnnalistUser object, without metadata (yet).

        parent      is the parent entity from which the type is descended.
        user_id     the local identifier for the user
        altparent   is a site object to search for this new entity,
                    allowing site-wide AnnalistUser values to be found.
        """
        super(AnnalistUser, self).__init__(parent, user_id)
        # log.debug("AnnalistUser %s: dir %s"%(user_id, self._entitydir))
        # log.debug("AnnalistUser %s: url %s, viewurl %s"%(user_id, self._entityurl, self._entityviewurl))
        return

    def _migrate_values(self, userpermissions):
        """
        User permission data format migration method.
        """
        migration_map = (
            [ (ANNAL.CURIE.user_permissions, ANNAL.CURIE.user_permission)
            ])
        userpermissions = self._migrate_values_map_field_names(migration_map, userpermissions)
        return userpermissions

# End.
