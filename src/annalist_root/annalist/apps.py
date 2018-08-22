"""
Annalist application hooks
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf import settings
from django.apps import AppConfig

class AnnalistConfig(AppConfig):
    """
    Annalist config class that logs settings when ready is called.
    (cf. https://docs.djangoproject.com/en/dev/ref/applications/)

    The main purpose of this is to log settings values to the log file, 
    after the log file configuration has been applied.
    """

    name = 'annalist'

    def ready(self):
        log.info("== AnalistConfig.ready ==")
        log.info(settings.ANNALIST_VERSION_MSG)
        log.info("SETTINGS_MODULE:  "+settings.SETTINGS_MODULE)
        log.info("DATABASES:        "+repr(settings.DATABASES))
        log.info("BASE_DATA_DIR:    "+settings.BASE_DATA_DIR)
        log.info("CONFIG_BASE:      "+settings.CONFIG_BASE)
        log.info("DJANGO_ROOT:      "+settings.DJANGO_ROOT)
        log.info("SITE_CONFIG_DIR:  "+settings.SITE_CONFIG_DIR)
        log.info("SITE_SRC_ROOT:    "+settings.SITE_SRC_ROOT)
        log.info("STATICFILES_DIRS: "+repr(settings.STATICFILES_DIRS))
        log.info("DB PATH:          "+settings.DATABASES['default']['NAME'])
        log.info("ALLOWED_HOSTS:    "+",".join(settings.ALLOWED_HOSTS))
        log.info("LOGGING_FILE:     "+settings.LOGGING_FILE)
        log.info("==")
        return

# End.
