# Shared deployment (separate server host) settings
#
# Data is kept under /var directory
# Configuration is kept under /etc directory
#

from common import *

ANNALIST_VERSION_MSG = "Annalist version %s (shared service configuration)"%(ANNALIST_VERSION)

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = "/var"
BASE_SITE_DIR   = os.path.join(BASE_DATA_DIR, layout.SITE_DIR)
CONFIG_BASE     = "/etc/annalist/"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG           = False
TEMPLATE_DEBUG  = False
ALLOWED_HOSTS   = ['.annalist.net']     # @@FIXME

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DATA_DIR, 'annalist_site/_annalist_site/db.sqlite3'),
    }
}

LOGGING_FILE    = '/var/log/annalist/annalist.log'
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
            'filename': LOGGING_FILE
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
        'oauth2': {
            'handlers': ['logfile'],
            'level': 'INFO', # Or maybe INFO or DEBUG
            'propagate': False
        },
    },
}


import logging
log = logging.getLogger(__name__)
log.info(ANNALIST_VERSION_MSG)
# log.info("Annalist version %s (shared service configuration)"%(ANNALIST_VERSION))
log.info("SETTINGS_MODULE: "+SETTINGS_MODULE)
log.info("BASE_DATA_DIR:   "+BASE_DATA_DIR)
log.info("CONFIG_BASE:     "+CONFIG_BASE)
log.info("DJANGO_ROOT:     "+DJANGO_ROOT)
log.info("SITE_CONFIG_DIR: "+SITE_CONFIG_DIR)
log.info("SITE_SRC_ROOT:   "+SITE_SRC_ROOT)
log.info("DB PATH:         "+DATABASES['default']['NAME'])

# End.
