"""
Test settings

A copy of initial data is created within the project.
Service configuration is kept under personal home directory to 
protect secret keys, etc.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

import os
import sys

from .common import *

import logging
log = logging.getLogger(__name__)

ANNALIST_VERSION_MSG = "Annalist version %s (test configuration)"%(ANNALIST_VERSION)

SETTINGS_MODULE   = __name__
SITE_DIR_NAME     = "annalist_test"
BASE_DATA_DIR     = SITE_SRC_ROOT+"/sampledata/data"
BASE_SITE_DIR     = os.path.join(BASE_DATA_DIR, SITE_DIR_NAME)
CONFIG_BASE       = os.path.join(os.path.expanduser("~"), ".annalist/")
STATIC_ROOT       = os.path.join(BASE_SITE_DIR, 'static')

BASE_LOG_DIR      = SITE_SRC_ROOT+"/"
ANNALIST_LOG_PATH = BASE_LOG_DIR+ANNALIST_LOG_FILE
ACCESS_LOG_PATH   = BASE_LOG_DIR+ACCESS_LOG_FILE
ERROR_LOG_PATH    = BASE_LOG_DIR+ERROR_LOG_FILE

DATABASE_PATH     = os.path.join(BASE_SITE_DIR, 'db.sqlite3')
DATABASES         = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   DATABASE_PATH,
    }
}

# URI parts used for testing
TEST_HOST           = "test.example.com"
TEST_HOST_URI       = "http://"+TEST_HOST
TEST_BASE_PATH      = "testsite"
TEST_BASE_URI       = TEST_HOST_URI+"/"+TEST_BASE_PATH

# Changing the current working directory affects test discovery..
# TEST_DISCOVER_TOP_LEVEL = os.path.join(SITE_SRC_ROOT, "annalist")
# os.chdir(TEST_DISCOVER_TOP_LEVEL)

# Logging level used by selected log statements whose output may be useful
# for tracing field values displayed in Annalist edit/view forms.
# Suggested use is to raise level to logging.INFO when running a single named
# test, when trying to understand how values end up in a form.
TRACE_FIELD_VALUE   = logging.DEBUG

# Override root URI configuration for tests
ROOT_URLCONF    = 'annalist_site.runtests_urls'

ALLOWED_HOSTS     = ["test.example.com"]

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
        'timed': {
            'format': '%(levelname)s %(asctime)s %(message)s'
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
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': ANNALIST_LOG_PATH,
            'formatter': 'timed'
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
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django': {
            'handlers': ['console', 'logfile'],
        },
        'django.request': {
            'level':    'ERROR'
        },
        'py.warnings': {
            'handlers': ['console', 'logfile'],
        },
    }
}

# LOGGING['loggers']['django.request'] = {'level': 'ERROR'}

# log.info("@@@@ settings: "+__name__)
# log.info("@@@@ settings globals: "+repr(globals()))
log.info(ANNALIST_VERSION_MSG)
# log.info("Annalist version %s (test configuration)"%(ANNALIST_VERSION))
log.info("SETTINGS_MODULE:   "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:     "+BASE_DATA_DIR)
log.info("CONFIG_BASE:       "+CONFIG_BASE)
log.info("DJANGO_ROOT:       "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR:   "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:     "+SITE_SRC_ROOT)
log.info("TEST_BASE_URI:     "+TEST_BASE_URI)
log.info("DEFAULT_DB_PATH:   "+DATABASES['default']['NAME'])
log.info("DATABASE_PATH:     "+DATABASE_PATH)

# log.info("TEST_RUNNER:             "+TEST_RUNNER)
# log.info("TEST_DISCOVER_TOP_LEVEL: "+TEST_DISCOVER_TOP_LEVEL)
log.info("STATICFILES_DIRS:  "+repr(STATICFILES_DIRS))
log.info("ANNALIST_LOG_PATH: "+ANNALIST_LOG_PATH)
# log.info("TEMPLATES:\n%r\n"%TEMPLATES)

# testsettings =  sys.modules["annalist_site.settings.runtests"]
# log.info("@@@@ testsettings "+repr(hash(testsettings)))
# log.info("@@@@defaultname: "+testsettings.DATABASES['default']['NAME'])

# See also: annalist/apps.py

log.debug("Test debug log")

# End.
