"""
Login views and authentication supporting utilities
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import copy
import urllib

import logging
log = logging.getLogger(__name__)

# from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

def HttpResponseRedirectWithQuery(redirect_uri, query_params):
    """
    Returns an HTTP response object that redirects to the supplied URL with
    the supplied query parameters applied.
    """
    nq = "?"
    for pname in query_params.keys():
        if query_params[pname]:
            redirect_uri += nq + pname + "=" + urllib.quote(query_params[pname])
            nq = "&"
    return HttpResponseRedirect(redirect_uri)

def HttpResponseRedirectLogin(request, message=None):
    """
    Returns an HTTP response object that is used at the end of an 
    authentication flow.

    It redirects to the user_profile_url stored in the current session, 
    with continuation to the supplied continuation_url, with the userid
    for the (attempted) authentication as a further query parameter.
    """
    user_profile_url = request.session['user_profile_url']
    query_params = {}
    if 'continuation_url' in request.session:
        query_params['continuation_url'] = request.session['continuation_url']
    if 'recent_userid' in request.session:
        query_params['recent_userid'] = request.session['recent_userid']
    if message:
        query_params.update(
            { "error_head":       "Login failed"
            , "error_message":    message
            })
    return HttpResponseRedirectWithQuery(user_profile_url, query_params)

def object_to_dict(obj, strip):
    """
    Utility function that creates dictionary representation of an object.

    Args:
        strip: an array of names of members to not include in the dict.

    Returns:
        dictionary, with non-excluded values that can be used to reconstruct an instance
        of the object via its constructor (assuming an appropriate constructor form, as
        used below for oauth2_dict_to_flow, etc.)
    """
    t = type(obj)
    d = copy.copy(obj.__dict__)
    for member in strip:
      if member in d:
        del d[member]
    d['_class']  = t.__name__
    d['_module'] = t.__module__
    return d

# End.
