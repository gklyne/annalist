"""
Shared deployment (separate server host) settings

Data is kept under /var directory.
Configuration is kept under /etc directory.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

from .common import *

ANNALIST_VERSION_MSG = "Annalist version %s (shared service configuration)"%(ANNALIST_VERSION)

SETTINGS_MODULE   = __name__
SITE_DIR_NAME     = "annalist_site"
BASE_DATA_DIR     = "/var"
BASE_SITE_DIR     = os.path.join(BASE_DATA_DIR, SITE_DIR_NAME)
CONFIG_BASE       = "/etc/annalist/"
STATIC_ROOT       = os.path.join(BASE_SITE_DIR, 'static')

BASE_LOG_DIR      = "/var/log/annalist/"
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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG           = False
ALLOWED_HOSTS   = ['.annalist.net']     # @@FIXME

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
             # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': ANNALIST_LOG_PATH
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        'annalist': {
            'handlers': ['logfile'],
            'level': 'INFO', # Or maybe INFO or DEBUG
            'propagate': False
        },
        'login': {
            'handlers': ['logfile'],
            'level': 'INFO', # Or maybe INFO or DEBUG
            'propagate': False
        },
    },
}

import logging
log = logging.getLogger(__name__)
log.info(ANNALIST_VERSION_MSG)
log.debug("SETTINGS_MODULE:   "+SETTINGS_MODULE)
log.debug("BASE_DATA_DIR:     "+BASE_DATA_DIR)
log.debug("CONFIG_BASE:       "+CONFIG_BASE)
log.debug("DJANGO_ROOT:       "+DJANGO_ROOT)
log.debug("SITE_CONFIG_DIR:   "+SITE_CONFIG_DIR)
log.debug("SITE_SRC_ROOT:     "+SITE_SRC_ROOT)
log.debug("STATICFILES_DIRS:  "+repr(STATICFILES_DIRS))
log.debug("DB PATH:           "+DATABASES['default']['NAME'])
log.debug("ALLOWED_HOSTS:     "+",".join(ALLOWED_HOSTS))
log.debug("ANNALIST_LOG_PATH: "+ANNALIST_LOG_PATH)
log.debug("TRACE_FIELD_VALUE: "+str(TRACE_FIELD_VALUE))

# End.
