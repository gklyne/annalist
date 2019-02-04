"""
Root settings module for Annalist.

Default submodule is selected by manage.py or am_runserver.py

To specify an alternative:
  python manage.py rundevserver --settings=annalist_site.settings.personal
  python manage.py runserver --settings=annalist_site.settings.personal
or
  export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal

See also:
  http://www.rdegges.com/the-perfect-django-settings-file/

"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

import sys

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.debug("Python path:    "+repr(sys.path))

# End.
