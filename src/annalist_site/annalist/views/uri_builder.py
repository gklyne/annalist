"""
This module contains functions to assist in the construction of URIs for views.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import urllib

def uri_params(*param_dicts):
    """
    Consruct a URI parameter string from the supplied dictionary values 
    (or values which are convertible to a dictionary using `dict()`).
    """
    uri_param_dict = {}
    for d in param_dicts:
        uri_param_dict.update(d)
    uri_param_str = ""
    next_sep      = "?"        
    for pnam in uri_param_dict:
        uri_param_str += next_sep + pnam + "=" + urllib.quote(uri_param_dict[pnam], "':,!=/")
        next_sep = "&"
    return uri_param_str

def uri_with_params(base_uri, *param_dicts):
    """
    Construct a URI from the supplied base URI (with any parameters and/or fragment removed)
    and URI paramneters created using the supplied dictionary values.
    """
    bare_uri = base_uri.split("#", 1)[0]
    bare_uri = bare_uri.split("?", 1)[0]
    return bare_uri + uri_params(*param_dicts)

# End.
