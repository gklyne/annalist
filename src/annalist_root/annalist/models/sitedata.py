"""
Annalist site data

Site data is an alternative location for generic Annalist metatadata 
(e.g. type and view definitions, etc.) that are common across all 
collections (and even installations).  It is implemeted as a specially-
named Collection object.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist                   import layout
from annalist.identifiers       import ANNAL
from annalist                   import util

from annalist.models.collection import Collection

class SiteData(Collection):

    _entitytype     = ANNAL.CURIE.SiteData
    _entitytypeid   = "_sitedata"

    def __init__(self, parentsite, entityid=layout.SITEDATA_ID):
        """
        Initialize a new SiteData object, without metadta (yet).

        parentsite  is the parent site from which the new collection is descended.
        """
        if entityid != layout.SITEDATA_ID:
            raise ValueError("Site data initialized with incorrect entity id (%s)"%entityid)
        super(SiteData, self).__init__(parentsite, entityid)
        return

    @classmethod
    def create_sitedata(cls, parent, sitedata):
        """
        Method loads a site data entity

        cls         is a class value used to construct the new entity value
        parent      is the parent site from which the new SiteData entity is descended.
        sitedata    is a dictionary of values that are stored for the created site data.

        Returns the site data collection as an instance of the supplied SiteData class.
        """
        log.debug("SiteData.create: entityid %s"%(layout.SITEDATA_ID))
        return cls.create(parent, layout.SITEDATA_ID, sitedata)

    @classmethod
    def load_sitedata(cls, parent):
        """
        Method loads a site data entity

        cls         is a class value used to construct the new entity value
        parent      is the parent site from which the new SiteData entity is descended.

        Returns the site data collection as an instance of the supplied SiteData class,
        with data oaded from the corresponding Annalist storage, or None if there is no
        such collection data.
        """
        log.debug("SiteData.create: entityid %s"%(layout.SITEDATA_ID))
        return cls.load(parent, layout.SITEDATA_ID)

# End.
