"""
Development settings

Data is kept within the project directory
(initialize as required, e.g. by copying initial testdata).
Service configuration is kept under personal home directory to 
protect secret keys, etc.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

from .common import *

ANNALIST_VERSION_MSG = "Annalist version %s (development configuration)"%(ANNALIST_VERSION)

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = SITE_SRC_ROOT+"/devel"
BASE_SITE_DIR   = os.path.join(BASE_DATA_DIR, layout.SITE_DIR)
CONFIG_BASE     = os.path.join(os.path.expanduser("~"), ".annalist/")

DATABASE_PATH   = os.path.join(BASE_DATA_DIR, 'annalist_site/db.sqlite3')
DATABASES       = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH,
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# INSTALLED_APPS += (
#     'django.contrib.staticfiles',
#     )

LOGGING_FILE = "None (output to console)"

# import logging
# log = logging.getLogger(__name__)
# log.info("Annalist version %s (development configuration)"%(ANNALIST_VERSION))
# log.info(ANNALIST_VERSION_MSG)
# log.info("SETTINGS_MODULE:  "+SETTINGS_MODULE)
# log.info("BASE_DATA_DIR:    "+BASE_DATA_DIR)
# log.info("CONFIG_BASE:      "+CONFIG_BASE)
# log.info("DJANGO_ROOT:      "+DJANGO_ROOT)
# log.info("SITE_CONFIG_DIR:  "+SITE_CONFIG_DIR)
# log.info("SITE_SRC_ROOT:    "+SITE_SRC_ROOT)
# log.info("STATICFILES_DIRS: "+repr(STATICFILES_DIRS))
# log.info("DB PATH:          "+DATABASES['default']['NAME'])

# End.
