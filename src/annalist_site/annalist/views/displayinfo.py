"""
This module defines a class that is used to gather information about an entity
list or view display that is needed to process various kinds of HTTP request.

The intent of this module is to collect and isolate various housekeeping functions
into a common module to avoid repetition of logic and reduce code clutter in
the various Annalist view processing handlers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

#   -------------------------------------------------------------------------------------------
#
#   Display information class
#
#   -------------------------------------------------------------------------------------------

class DisplayInfo(object):
    """
    This class collects and organizes common information needed to process various
    kinds of view requests.

    A number of methods are provided that collect different kinds of information,
    allowing the calling method flexibility over what information is actually 
    gathered.  All methods follow a common pattern loosely modeled on an error
    monad, which uses a Django HttpResponse object to record the first problem
    found in the information gathering chain.  Once an error has been detected, 
    subsequent methods do not update the display information, but simply return
    the error response object.

    The information gathering methods do have some dependencies and must be
    invoked in a sequence that ensures the dependencies are satisfied.
    """

    def __init__(self, view):
        self.view           = view
        self.reqhost        = None
        self.site           = None
        self.collection     = None
        self.type_id        = None
        self.entitytypeinfo = None
        self.list_id        = None
        self.recordlist     = None
        self.view_id        = None
        self.recordview     = None
        self.http_response  = None
        return

    def get_site_info(self, reqhost):
        if not self.http_response:
            self.reqhost        = reqhost
            self.site           = self.view.site(host=reqhost)
        return self.http_response

    def get_coll_info(self, coll_id):
        """
        Check collection identifier, and get reference to collection object.
        """
        assert (self.site is not None)
        if not self.http_response:
            if not Collection.exists(self.site, coll_id):
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.COLLECTION_NOT_EXISTS%{'id': coll_id}
                        )
                    )
            else:
                self.collection = Collection.load(self.site, coll_id)
        return self.http_response

    def get_type_info(self, type_id):
        """
        Check type identifier, and get reference to type information object.
        """
        assert ((self.site and self.collection) is not None)
        if not self.http_response:
            if type_id:
                self.type_id        = type_id
                self.entitytypeinfo = EntityTypeInfo(self.site, self.collection, type_id)
                if not self.entitytypeinfo.entityparent:
                    # log.warning("DisplayInfo.get_type_data: RecordType %s not found"%type_id)
                    self.http_response = self.view.error(
                        dict(self.view.error404values(),
                            message=message.RECORD_TYPE_NOT_EXISTS%(
                                {'id': type_id, 'coll_id': self.collection.get_id()})
                            )
                        )
        return self.http_response

    def get_list_info(self, list_id):
        """
        Retrieve list definition to use for display
        """
        if not self.http_response:
            if not RecordList.exists(self.collection, list_id, self.site):
                log.info("DisplayInfo.get_list_info: RecordList %s not found"%list_id)
                coll_id = self.collection.get_id()
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.RECORD_LIST_NOT_EXISTS%(
                            {'id': list_id, 'coll_id': self.collection.get_id()})
                        )
                    )
            else:
                self.recordlist = RecordList.load(self.collection, list_id, self.site())
                log.debug("DisplayInfo.get_list_info: %r"%(self.recordlist.get_values()))
        return self.http_response

    def get_view_info(self, view_id):
        """
        Retrieve view definition to use for display
        """
        if not self.http_response:
            if not RecordView.exists(self.collection, view_id, self.site:
                log.warning("DisplayInfo.get_view_info: RecordView %s not found"%view_id)
                coll_id = self.collection.get_id()
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.RECORD_VIEW_NOT_EXISTS%(
                            {'id': view_id, 'coll_id': self.collection.get_id()})
                        )
                    )
            else:
                self.recordview = RecordView.load(self.collection, view_id, self.site())
                log.debug("DisplayInfo.get_view_info: %r"%(self.recordview.get_values()))
        return self.http_response

# End.
