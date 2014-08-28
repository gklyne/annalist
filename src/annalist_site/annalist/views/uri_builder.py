"""
This module contains functions to assist in the construction of URIs for views.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import urllib
import re

# From RFC 3986:
gen_delims  = ":/?#[]@"
sub_delims  = "!$&'()*+,;="
unreserved  = "-._~"
# subset of above safe in query string (no "?", "&" or #")
query_safe  = re.sub('[?&#]', '', gen_delims + sub_delims + unreserved)

def build_dict(*param_dicts, **param_dict):
    merged_param_dict = param_dict.copy()
    for d in param_dicts:
        # log.info("param_dicts %r"%(d,))
        merged_param_dict.update(d)
    return merged_param_dict

def uri_params(*param_dicts, **param_dict):
    """
    Construct a URI parameter string from the supplied dictionary values 
    (or values which are convertible to a dictionary using `dict()`).
    """
    uri_param_dict = build_dict(*param_dicts, **param_dict)
    uri_param_str = ""
    next_sep      = "?"        
    for pnam in uri_param_dict:
        pval = uri_param_dict[pnam]
        if pval is not None:
            uri_param_str += next_sep + pnam + "=" + urllib.quote(pval, query_safe)
            next_sep = "&"
    return uri_param_str

def uri_base(uri):
    """
    Construct a base URI from the supplied base URI by removing any parameters and/or fragments.
    """
    base_uri = uri.split("#", 1)[0]
    base_uri = base_uri.split("?", 1)[0]
    return base_uri

def uri_with_params(base_uri, *param_dicts, **param_dict):
    """
    Construct a URI from the supplied base URI (with any parameters and/or fragment removed)
    and URI paramneters created using the supplied dictionary values.
    """
    return uri_base(base_uri) + uri_params(*param_dicts, **param_dict)

def continuation_params(*param_dicts, **param_dict):
    """
    Return URI parameters from the supplied dictionary specifically needed for a continuation 
    URI, ignoring all others.  These are the parameters which, in conjunction with a base URI, 
    represent application state.  Parameters not included here are transient in their effect.
    """
    uri_param_dict = build_dict(*param_dicts, **param_dict)
    return (
        { 'continuation_url': uri_param_dict.get('continuation_url') or None
        , 'search':           uri_param_dict.get('search_for')       or 
                              uri_param_dict.get('search')           or None
        })

# End.
