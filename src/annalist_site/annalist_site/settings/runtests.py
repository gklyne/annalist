# Test settings
#
# A copy of initial data is created within the project
# Service configuration is kept under personal home directory to protect secret keys, etc
#

from common import *

# Override authentication backend to use local datrabase only
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = SITE_SRC_ROOT+"/test/data"
CONFIG_BASE     = os.path.join(os.path.expanduser("~"), ".annalist/")

import logging
log = logging.getLogger(__name__)
log.info("SETTINGS_MODULE: "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:   "+BASE_DATA_DIR)
log.info("CONFIG_BASE:     "+CONFIG_BASE)
log.info("DJANGO_ROOT:     "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR: "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:   "+SITE_SRC_ROOT)
log.info("DB PATH:         "+DATABASES['default']['NAME'])

# End.
