# Test settings
#
# A copy of initial data is created within the project
# Service configuration is kept under personal home directory to protect secret keys, etc
#

from common import *

import logging
log = logging.getLogger(__name__)

# Override authentication backend to use local database only
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )

# Override logging setings for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'null': {
            'class': 'logging.NullHandler',
        }
    },
    'loggers': {
        # '': {
        #      'handlers': ['console'],
        #      'level': 'INFO',
        #  },
        'annalist': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'django': {
            'handlers': ['console'],
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}

# URI parts used for testing
TEST_HOST           = "test.example.com"
TEST_HOST_URI       = "http://"+TEST_HOST
TEST_BASE_PATH      = "testsite"
TEST_BASE_URI       = TEST_HOST_URI+"/"+TEST_BASE_PATH

# Logging level used by selected log statements whose output may be useful
# for tracing field values displayed in Annalist edit/view forms.
# Suggested use is to raise level to logging.INFO when running a single named
# test, when trying to understand how values end up in a form.
TRACE_FIELD_VALUE   = logging.DEBUG

# Override root URI configuration for tests
ROOT_URLCONF        = 'annalist_site.runtests_urls'

SETTINGS_MODULE     = __name__
BASE_DATA_DIR       = SITE_SRC_ROOT+"/sampledata/data"
CONFIG_BASE         = os.path.join(os.path.expanduser("~"), ".annalist/")

log.info("Annalist version %s (test configuration)"%(ANNALIST_VERSION))
log.info("SETTINGS_MODULE: "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:   "+BASE_DATA_DIR)
log.info("CONFIG_BASE:     "+CONFIG_BASE)
log.info("DJANGO_ROOT:     "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR: "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:   "+SITE_SRC_ROOT)
log.info("DB PATH:         "+DATABASES['default']['NAME'])
log.debug("Test debug log")

# End.
