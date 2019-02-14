from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Annalist action confirmation view definition
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import os
import logging

from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.template                import loader

from django.conf                    import settings

from utils.ContentNegotiationView   import ContentNegotiationView

from annalist.models.annalistuser   import AnnalistUser

from annalist.views.generic         import AnnalistGenericView

# Helper function to get last N lines of log file, rather than loading
# entire file into memory (was getting MemoryError falures.)
#
# Adapted from: https://stackoverflow.com/a/13790289/324122

def tail(f, lines=1, _buffer=4098):
    """
    Tail a file and get X lines from the end
    """
    lines_found = []
    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1
    # loop until we find more than X lines
    # (Looking for `>lines` because the first line may be truncated)
    while len(lines_found) <= lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break
        lines_found = f.readlines()
        block_counter -= 1
    return lines_found[-lines:]


class ServerLogView(AnnalistGenericView):
    """
    View class to handle requests to the Annalist user profile URI
    """
    def __init__(self):
        super(ServerLogView, self).__init__()
        return

    # GET

    def get(self, request):
        def resultdata():
            serverlogname = settings.ANNALIST_LOG_PATH
            log.info("ServerLogView: serverlogname %s"%(serverlogname,))
            with open(serverlogname, "r") as serverlogfile:
                # serverlog     = list(serverlogfile) # Generates MemoryError with large logs
                serverlog = tail(serverlogfile, 2000)
                return (
                    { 'title':              self.site_data()["title"]
                    , 'serverlogname':      serverlogname
                    , 'serverlog':          "".join(serverlog)
                    , 'continuation_url':   continuation_url
                    })

        continuation_url  = self.continuation_next(
            request.GET, self.view_uri("AnnalistHomeView")
            )
        return (
            # self.authenticate(continuation_url) or 
            self.authorize("ADMIN", None) or
            self.render_html(resultdata(), 'annalist_serverlog.html') or 
            self.error(self.error406values())
            )

    def post(self, request):
        continuation_url  = request.POST.get("continuation_url", "../")
        return HttpResponseRedirect(continuation_url)

# End.
