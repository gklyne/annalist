"""
WSGI config for annalist_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "annalist_site.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# End.