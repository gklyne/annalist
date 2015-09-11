"""
This module contains functions to assist in the construction of URIs for views.
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
        if pval:
            # log.info("pnam %s, pval %s, uri_param_dict %r"%(pnam, pval, uri_param_dict))
            uri_param_str += next_sep + pnam + "=" + urllib.quote(pval, query_safe)
            next_sep = "&"
    return uri_param_str

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

def continuation_url_chain(continuation_url):
    """
    Disects a supplied continuation URL into its components going back up the return chain.

    Thus, if:
    >>> hop1  = uri_with_params("base:hop1", search="s1")
    >>> hop2  = uri_with_params("base:hop2", search="s2")
    >>> hop3  = uri_with_params("base:hop3", search="s3")
    >>> hop4  = uri_with_params("base:hop4", search="s4")
    >>> hop1p = (uri_base(hop1), uri_param_dict(hop1))
    >>> hop2p = (uri_base(hop2), uri_param_dict(hop2))
    >>> hop3p = (uri_base(hop3), uri_param_dict(hop3))
    >>> hop4p = (uri_base(hop4), uri_param_dict(hop4))
    >>> hop1p
    ('base:hop1', {'search': 's1'})
    >>> hop2p
    ('base:hop2', {'search': 's2'})
    >>> hop3p
    ('base:hop3', {'search': 's3'})
    >>> hop4p
    ('base:hop4', {'search': 's4'})
    >>> hop1c = hop1
    >>> hop2c = uri_with_params("base:hop2", search="s2", continuation_url=hop1)
    >>> hop3c = uri_with_params("base:hop3", search="s3", continuation_url=hop2c)
    >>> hop4c = uri_with_params("base:hop4", search="s4", continuation_url=hop3c)
    >>> hop1c
    'base:hop1?search=s1'
    >>> hop2c
    'base:hop2?search=s2&continuation_url=base:hop1%3Fsearch=s1'
    >>> hop3c
    'base:hop3?search=s3&continuation_url=base:hop2%3Fsearch=s2%26continuation_url=base:hop1%253Fsearch=s1'
    >>> hop4c
    'base:hop4?search=s4&continuation_url=base:hop3%3Fsearch=s3%26continuation_url=base:hop2%253Fsearch=s2%2526continuation_url=base:hop1%25253Fsearch=s1'
    >>> continuation_url_chain(hop1c) == [hop1p]
    True
    >>> continuation_url_chain(hop2c) == [hop2p, hop1p]
    True
    >>> continuation_url_chain(hop3c) == [hop3p, hop2p, hop1p]
    True
    >>> continuation_url_chain(hop4c) == [hop4p, hop3p, hop2p, hop1p]
    True
    """
    c_base   = uri_base(continuation_url)
    c_params = uri_param_dict(continuation_url)
    if "continuation_url" in c_params:
        c_cont = c_params.pop("continuation_url")
        c_list = continuation_url_chain(c_cont)
        c_list.insert(0, (c_base, c_params))
        return c_list
    return [(c_base, c_params)]

def continuation_chain_url(continuation_chain):
    """
    Assembles a list of continuation components into a single continuation URL

    >>> hop1  = uri_with_params("base:hop1", search="s1")
    >>> hop2  = uri_with_params("base:hop2", search="s2")
    >>> hop3  = uri_with_params("base:hop3", search="s3")
    >>> hop4  = uri_with_params("base:hop4", search="s4")
    >>> hop1p = (uri_base(hop1), uri_param_dict(hop1))
    >>> hop2p = (uri_base(hop2), uri_param_dict(hop2))
    >>> hop3p = (uri_base(hop3), uri_param_dict(hop3))
    >>> hop4p = (uri_base(hop4), uri_param_dict(hop4))
    >>> hop1c = hop1
    >>> hop2c = uri_with_params("base:hop2", search="s2", continuation_url=hop1)
    >>> hop3c = uri_with_params("base:hop3", search="s3", continuation_url=hop2c)
    >>> hop4c = uri_with_params("base:hop4", search="s4", continuation_url=hop3c)
    >>> continuation_chain_url([hop1p]) == hop1c
    True
    >>> continuation_chain_url([hop2p, hop1p]) == hop2c
    True
    >>> continuation_chain_url([hop3p, hop2p, hop1p]) == hop3c
    True
    >>> continuation_chain_url([hop4p, hop3p, hop2p, hop1p]) == hop4c
    True
    """
    u_base, u_params = continuation_chain[0]
    c_tail           = continuation_chain[1:]
    if c_tail:
        u_params.update(continuation_url=continuation_chain_url(c_tail))
    return uri_with_params(u_base, u_params)

def url_update_type_entity_id(url_base, 
    old_type_id=None, new_type_id=None, 
    old_entity_id=None, new_entity_id=None
    ):
    """
    Isolates type and entity identifiers in the supplied URL, and replaces 
    them with values supplied.

    Entity ids are updated only if the type id is also supplied and matches.

    URL path forms recognized (see also urls.py):
        .../c/<coll-id>/d/<type-id>/
        .../c/<coll-id>/d/<type-id>/!<scope>
        .../c/<coll-id>/d/<type-id>/<entity-id>/
        .../c/<coll-id>/l/<list-id>/<type-id>/
        .../c/<coll-id>/l/<list-id>/<type-id>/!<scope>
        .../c/<coll-id>/v/<view-id>/<type-id>/
        .../c/<coll-id>/v/<view-id>/<type-id>/!action
        .../c/<coll-id>/v/<view-id>/<type-id>/<entity-id>/
        .../c/<coll-id>/v/<view-id>/<type-id>/<entity-id>/!action

    Thus, the key patterns used for rewriting are:
        ^.*/d/<type-id>/(!.*])?$
        ^.*/d/<type-id>/<entity-id>/$
        ^.*/l/<list-id>/<type-id>/(!.*])?$
        ^.*/v/<view-id>/<type-id>/(!.*])?$
        ^.*/v/<view-id>/<type-id>/<entity-id>/(!.*])?$

    >>> url_update_type_entity_id("http://example.com/base/c/coll/d/t1/",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/d/t2/'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/d/t1/!all",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/d/t2/!all'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/l/list/t1/",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/l/list/t2/'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/l/list/t1/!all",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/l/list/t2/!all'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/v/view/t1/",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/v/view/t2/'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/v/view/t1/!new",
    ...     old_type_id="t1", new_type_id="t2")
    'http://example.com/base/c/coll/v/view/t2/!new'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/d/t1/e1/",
    ...     old_type_id="t1", new_type_id="t2",
    ...     old_entity_id="e1", new_entity_id="e2")
    'http://example.com/base/c/coll/d/t2/e2/'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/v/view/t1/e1/",
    ...     old_type_id="t1", new_type_id="t2",
    ...     old_entity_id="e1", new_entity_id="e2")
    'http://example.com/base/c/coll/v/view/t2/e2/'
    >>> url_update_type_entity_id("http://example.com/base/c/coll/v/view/t1/e1/",
    ...     old_type_id="t1", new_type_id="t2",
    ...     old_entity_id="e1", new_entity_id="e2")
    'http://example.com/base/c/coll/v/view/t2/e2/'
    """
    rewrite_type_id_patterns = (
        # (<prefix>)/(<type_id>)/<suffix>)
        [ re.compile(r"(^.*/d)/(?P<type_id>\w{0,32})/(!.*)?$")
        , re.compile(r"(^.*/l/\w{0,32})/(?P<type_id>\w{0,32})/(!.*)?$")
        , re.compile(r"(^.*/v/\w{0,32})/(?P<type_id>\w{0,32})/(!.*)?$")
        ])
    rewrite_entity_id_patterns = (
        # (<prefix>)/(<type_id>)/(<entity_id>)/<suffix>)
        [ re.compile(r"(^.*/d)/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/(!.*)?$")
        , re.compile(r"(^.*/v/\w{0,32})/(?P<type_id>\w{0,32})/(?P<entity_id>\w{0,32})/(!.*)?$")
        ])
    us, ua, up, uq, uf = urlparse.urlsplit(url_base)
    if new_type_id:
        for rexp in rewrite_type_id_patterns:
            match = rexp.match(up)
            if match:
                prefix, type_id, suffix = match.group(1, 2, 3)
                if not new_entity_id:
                    # Rename all instances of type
                    if type_id == old_type_id:
                        up = "%s/%s/%s"%(prefix, new_type_id, suffix or "")
                        break
        for rexp in rewrite_entity_id_patterns:
            match = rexp.match(up)
            if match:
                prefix, type_id, entity_id, suffix = match.group(1, 2, 3, 4)
                if new_entity_id:
                    # Rename matching type+entities only
                    if ( (type_id == old_type_id) and (entity_id == old_entity_id) ):
                        up = "%s/%s/%s/%s"%(prefix, new_type_id, new_entity_id, suffix or "")
                        break
                else:
                    # Rename all instances of type
                    if type_id == old_type_id:
                        up = "%s/%s/%s/%s"%(prefix, new_type_id, entity_id, suffix or "")
                        break
    return urlparse.urlunsplit((us, ua, up, uq, uf))

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
