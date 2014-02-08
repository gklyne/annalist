# Test settings
#
# A copy of initial data is created within the project
# Service configuration is kept under personal home directory to protect secret keys, etc
#

from common import *

import logging
log = logging.getLogger(__name__)

# Override authentication backend to use local datrabase only
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )

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

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = SITE_SRC_ROOT+"/test/data"
CONFIG_BASE     = os.path.join(os.path.expanduser("~"), ".annalist/")

log.info("SETTINGS_MODULE: "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:   "+BASE_DATA_DIR)
log.info("CONFIG_BASE:     "+CONFIG_BASE)
log.info("DJANGO_ROOT:     "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR: "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:   "+SITE_SRC_ROOT)
log.info("DB PATH:         "+DATABASES['default']['NAME'])
log.debug("Test debug log")

# End.
