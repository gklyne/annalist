# Root settings module
#
# Default submodule is selected by manage.py
#
# To specify an alternative:
#   python manage.py runserver --settings=annalist_site.settings.personal
# or
#   export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal
#
# See also:
#   http://www.rdegges.com/the-perfect-django-settings-file/
#

import sys

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.debug("Python path:    "+repr(sys.path))

# End.
