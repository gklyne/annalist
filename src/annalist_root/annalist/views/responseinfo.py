"""
This module defines a class that is used to gather information about a response
to a form submission.

The intent of this module is to collect and isolate various response-handling 
housekeeping functions into a common module to reduce code clutter in
the Annalist form response processing handler.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# from distutils.version              import LooseVersion

# from django.conf                    import settings
# from django.http                    import HttpResponse
# from django.http                    import HttpResponseRedirect
# from django.core.urlresolvers       import resolve, reverse

# import annalist
# from annalist                       import message
# from annalist.identifiers           import RDF, RDFS, ANNAL

from annalist.views.uri_builder     import uri_param_dict

class ResponseInfo(object):
    """
    This class collects and organizes information generated while processing
    a form response.
    """

    def __init__(self):
        """
        Initialize a ResponseInfo object
        """
        self._http_response = None      # Set when an HTTP response is determined (typically an error)
        self._response_conf = None      # Operation confirmation message
        self._response_err  = None      # Error message/flag (string)
        self._response_info = None      # String reporting details of confirmation or error
        self._templates     = None      # Message templates dictionary
        self._updated       = False     # Set True if entity values need to be updated
        return

    def __str__(self):
        str = (
            "{\n"+
            "_http_response: %s\n"%(self._http_response)+
            "_response_conf: %s\n"%(self._response_conf)+
            "_response_err:  %s\n"%(self._response_err)+
            "_response_info: %s\n"%(self._response_info)+
            "_updated:       %s\n"%(self._updated)+
            "}\n")
        return str

    def __repr__(self):
        return str(self)

    def set_http_response(self, http_response):
        if self._http_response is None:
            self._http_response = http_response
        return self     # Result can be 'responseinfo' return value

    def get_http_response(self):
        return self._http_response

    def has_http_response(self):
        return self._http_response is not None

    def set_response_confirmation(self, response_conf, response_info):
        if not self.is_response_error():
            self._response_conf = response_conf
            self._response_info = response_info
        return

    def set_response_error(self, response_err, response_info):
        if not self.is_response_error():
            self._response_err  = response_err
            self._response_info = response_info
        return

    def is_response_confirmation(self):
        return self._response_conf is not None

    def is_response_error(self):
        return self._response_err is not None

    def get_response_conf(self):
        return self._response_conf

    def get_response_err(self):
        return self._response_err

    def get_response_info(self):
        return self._response_info

    def set_updated(self):
        self._updated = True
        return

    def is_updated(self):
        return self._updated

    def set_message_templates(self, templates):
        if self._templates is None:
            self._templates = templates
        else:
            self._templates.update(templates)
        return self._templates

    def get_message_templates():
        return self._templates

    def get_message(self, key):
        return self._templates.get(key, "ResponseInfo.get_message: unknown key %r"%key)

    def get_formatted(self, key, values):
        t = self._templates.get(
            key, "ResponseInfo.get_formatted: unknown key %r (values %%r)"%key
            )
        return t%values

    def http_redirect(self, base_view, next_uri):
        """
        Generate an HTTP redirect response that incorporates any confirmation messages
        set up for the current responseinfo.  The responseinfo object is updated with
        the generated response, which is also returned as the result of thismethod.
        """
        # NOTE: supplied URI is presumed to ioncl;ude continuation and other parameters.
        # These need to be extracted and passed separately to the underlying
        # `redirect_error` or `redirect_info` method so that they can be reassembled 
        # along with the status messages.
        param_dict = uri_param_dict(next_uri)
        if self._http_response is None:
            if self.is_response_error():
                resp = base_view.redirect_error(next_uri,
                    view_params=param_dict, 
                    error_head=self._response_err, 
                    error_message=self._response_info
                    )
            else:
                resp = base_view.redirect_info(next_uri, 
                    view_params=param_dict, 
                    info_head=self._response_conf, 
                    info_message=self._response_info
                    )
            self.set_http_response(resp)
        return self._http_response

# End.
