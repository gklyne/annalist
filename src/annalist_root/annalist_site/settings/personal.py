# Personal deployment (same host) settings
#
# Data is kept in personal directory area
# Service configuration is kept under personal home directory
#

from common import *

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = os.path.expanduser("~")
CONFIG_BASE     = os.path.join(os.path.expanduser("~"), ".annalist/")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG           = False
TEMPLATE_DEBUG  = False
ALLOWED_HOSTS   = ['*']     # Insecure: use e.g. ['.annalist.net']

import logging
log = logging.getLogger(__name__)
log.info("Annalist version %s (personal configuration)"%(ANNALIST_VERSION))
log.info("SETTINGS_MODULE: "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:   "+BASE_DATA_DIR)
log.info("CONFIG_BASE:     "+CONFIG_BASE)
log.info("DJANGO_ROOT:     "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR: "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:   "+SITE_SRC_ROOT)
log.info("DB PATH:         "+DATABASES['default']['NAME'])

# End.
