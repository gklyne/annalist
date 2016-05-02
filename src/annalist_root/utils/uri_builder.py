"""
This module contains functions to assist in the manipulation and construction of URIs.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import urllib
import urlparse
import re

# From RFC 3986:
gen_delims  = ":/?#[]@"
sub_delims  = "!$&'()*+,;="
unreserved  = "-._~"
# subset of above safe in query string (no "?", "&" or #")
query_safe  = re.sub('[?&#]', '', gen_delims + sub_delims + unreserved)

def uri_base(uri):
    """
    Get the base URI from the supplied URI by removing any parameters and/or fragments.
    """
    base_uri = uri.split("#", 1)[0]
    base_uri = base_uri.split("?", 1)[0]
    return base_uri

def uri_query_key_val(p):
    """
    Returns a key-value pair for a supplied query parameter string.

    The value part returned has %-escaping unapplied.

    If no '=' is present, the value part returned is an empty string.
    """
    kv = p.split("=", 1) + [""]
    return (kv[0], urllib.unquote(kv[1]))

def uri_param_dict(uri):
    """
    Extract parameter dictionary from the supplied URI

    >>> uri_param_dict("base:path?q1=p1&q2=p2#frag") == { 'q1': "p1", 'q2': "p2"}
    True
    >>> uri_param_dict("base:path?q1=p1=p1&q2=p2%26p2&q3") == { 'q1': "p1=p1", 'q2': "p2&p2", 'q3': "" }
    True
    """
    base_uri = uri.split("#", 1)[0]
    query    = (base_uri.split("?", 1)+[""])[1]
    return { k: v for k, v in [ uri_query_key_val(qp) for qp in query.split("&") ] }

def build_dict(*param_dicts, **param_dict):
    """
    Create a merged dictionary from the supplied dictionaries and keyword parameters.
    """
    merged_param_dict = param_dict.copy()
    for d in param_dicts:
        if d is not None:
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
        if pval:
            # log.info("pnam %s, pval %s, uri_param_dict %r"%(pnam, pval, uri_param_dict))
            uri_param_str += next_sep + pnam + "=" + urllib.quote(pval, query_safe)
            next_sep = "&"
    return uri_param_str

def uri_with_params(base_uri, *param_dicts, **param_dict):
    """
    Construct a URI from the supplied base URI (with any parameters and/or fragment removed)
    and URI parameters created using the supplied dictionary values.
    """
    return uri_base(base_uri) + uri_params(*param_dicts, **param_dict)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
