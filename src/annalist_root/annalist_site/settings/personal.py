# Personal deployment (same host) settings
#
# Data is kept in personal directory area
# Service configuration is kept under personal home directory
#

from common import *

ANNALIST_VERSION_MSG = "Annalist version %s (personal configuration)"%(ANNALIST_VERSION)

SETTINGS_MODULE = __name__
BASE_DATA_DIR   = os.path.expanduser("~")
BASE_SITE_DIR   = os.path.join(BASE_DATA_DIR, layout.SITE_DIR)
CONFIG_BASE     = os.path.join(os.path.expanduser("~"), ".annalist/")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG           = False
TEMPLATE_DEBUG  = False
ALLOWED_HOSTS   = ['*']     # Insecure: use e.g. ['.annalist.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DATA_DIR, 'annalist_site/_annalist_site/db.sqlite3'),
    }
}

# LOGGING_FILE = SITE_SRC_ROOT+'/annalist.log'
LOGGING_FILE = BASE_SITE_DIR+'/annalist.log'
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
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
             # But the emails are plain text by default - HTML is nicer
            'include_html': True,
            'formatter': 'verbose'
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'level': 'INFO',
            'filename': LOGGING_FILE,
            'formatter': 'timed'
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': True,
        # },
        'django.request': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'annalist_site': {
            'handlers': ['logfile'],
            'level': 'INFO', # Or maybe INFO or DEBUG
            'propagate': False
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
# log.info("Annalist version %s (personal configuration)"%(ANNALIST_VERSION))
log.info(ANNALIST_VERSION_MSG)
log.debug("SETTINGS_MODULE:  "+SETTINGS_MODULE)
log.debug("BASE_DATA_DIR:    "+BASE_DATA_DIR)
log.debug("CONFIG_BASE:      "+CONFIG_BASE)
log.debug("DJANGO_ROOT:      "+DJANGO_ROOT)
log.debug("SITE_CONFIG_DIR:  "+SITE_CONFIG_DIR)
log.debug("SITE_SRC_ROOT:    "+SITE_SRC_ROOT)
log.debug("STATICFILES_DIRS: "+STATICFILES_DIRS[1])
log.debug("DB PATH:          "+DATABASES['default']['NAME'])
log.debug("ALLOWED_HOSTS:    "+",".join(ALLOWED_HOSTS))
log.debug("LOGGING_FILE:     "+LOGGING_FILE)
# End.
