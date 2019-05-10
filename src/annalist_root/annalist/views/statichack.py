from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Static hack view to allow Django serving of static files using Django's 
internal static file server.

This approach is explicitly NOT recommended by Django for production 
web servers, but has been created to allow a Django application to be 
deployed locally without requiring a separate web server to be deployed.

It is claimed to be very inefficient, and may be insecure, and as such 
should not be used for an open Internet deployment.

The logic has been copied and adapted from django.contrib.staticfiles.views

For deployment, add the following to the site-level urls.py file:

    if not settings.DEBUG:
        urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', serve_static),
            )

@@TODO: use separate settings flag to enable this, which can be set for
"personal" deployments only (i.e. not for shared deployments)

@@TODO: replace static file finder logic with direct serving logic assuming
prior use of collectfiles utility - this should allow greater control over 
the location of the served static files, rather than having them mixed with 
the server code.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import posixpath

import logging
log = logging.getLogger(__name__)

from django.conf                            import settings

from django.http                            import Http404
from django.utils.six.moves.urllib.parse    import unquote
from django.views                           import static
from django.contrib.staticfiles             import finders

def serve_static(request, path, insecure=False, **kwargs):
    """
    Serve static files below a given point in the directory structure or
    from locations inferred from the staticfiles finders.

    To use, put a URL pattern such as:

        (r'^static/(?P<path>.*)$', 'annalist.views.statichack.serve_static')

    in your `annalist_root/urls.py` URL configuration file.

    It uses the django.views.static.serve() view to serve the found files.
    """
    # log.info("serve_static %s"%(path))
    try:
        normalized_path = posixpath.normpath(unquote(path)).lstrip('/')
        absolute_path = finders.find(normalized_path)
        if not absolute_path:
            if path.endswith('/') or path == '':
                raise Http404("Directory indexes are not allowed here.")
            raise Http404("'%s' could not be found" % path)
        document_root, path = os.path.split(absolute_path)
        # log.info("document_root %s, path %s"%(document_root, path))
    except Exception as e:
        log.info(str(e))
        raise
    return static.serve(request, path, document_root=document_root, **kwargs)

def serve_pages(request, coll_id, page_ref, insecure=False, **kwargs):
    """
    Serve static files below a given point in the directory structure or
    from locations inferred from the staticfiles finders.

    To use, put a URL pattern such as:

        url(r'^c/(?P<coll_id>\w{1,128})/p/(?P<page_ref>[\w/.-]{1,250})$',
                                'annalist.views.statichack.serve_pages`),

    in your `annalist_root/annalist/urls.py` URL configuration file.

    It uses the django.views.static.serve() view to serve the found files.
    """
    # log.info("serve_pages %s"%(path))
    try:
        page_path = settings.BASE_SITE_DIR+"/c/"+coll_id+"/p/"+page_ref
        log.info("statichack.serve_pages %s"%(page_path,))
        normalized_path = posixpath.normpath(unquote(page_path))
        if not os.path.exists(normalized_path):
            if page_path.endswith('/') or page_path == '':
                raise Http404("Directory indexes are not allowed here.")
            raise Http404("'%s' could not be found" % page_path)
        document_root, path = os.path.split(normalized_path)
        # log.info("document_root %s, path %s"%(document_root, path))
    except Exception as e:
        log.info(str(e))
        raise
    return static.serve(request, path, document_root=document_root, **kwargs)

# End.
